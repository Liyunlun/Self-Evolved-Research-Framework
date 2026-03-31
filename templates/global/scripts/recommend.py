#!/usr/bin/env python3
"""SER v6 — Thompson Sampling Recommendation Generator

Reads weights.yaml, generates N independent samples per weight,
writes sample queues to .claude/.ser-recommendations.json.

Called by session.open: python3 ~/.claude/ser/scripts/recommend.py --samples 10

Stateless — reads weights, writes recommendations, exits.
Stdlib only — no numpy dependency.
"""

import json
import math
import random
import sys
import yaml
from os.path import expanduser, exists

# Parse args
N = int(sys.argv[sys.argv.index('--samples') + 1]) if '--samples' in sys.argv else 10

# Read weights
weights_path = expanduser('~/.claude/ser/weights.yaml')
if not exists(weights_path):
    print("[SER recommend.py] weights.yaml not found — using uniform priors", file=sys.stderr)
    json.dump({}, open('.claude/.ser-recommendations.json', 'w'), indent=2)
    sys.exit(0)

try:
    weights = yaml.safe_load(open(weights_path))
except Exception as e:
    print(f"[SER recommend.py] Failed to parse weights.yaml: {e}", file=sys.stderr)
    json.dump({}, open('.claude/.ser-recommendations.json', 'w'), indent=2)
    sys.exit(0)

# Read learning config for ambiguity threshold
config_path = expanduser('~/.claude/ser/config.yaml')
config = {}
if exists(config_path):
    try:
        config = yaml.safe_load(open(config_path)) or {}
    except Exception:
        pass

total_obs = weights.get('meta', {}).get('total_observations', 0)
burn_in_min = config.get('learning', {}).get('burn_in_min_observations', 30)
if total_obs < burn_in_min:
    AMBIGUITY_THRESHOLD = config.get('learning', {}).get('ambiguity_threshold_burnin', 0.3)
else:
    AMBIGUITY_THRESHOLD = config.get('learning', {}).get('ambiguity_threshold_normal', 0.1)

recommendations = {}

# Beta-distributed weights: generate N samples each
for category in ['transitions', 'chain_selection', 'checkpoints', 'step_skip']:
    recommendations[category] = {}
    for key, params in weights.get(category, {}).items():
        a, b = params.get('alpha', 1), params.get('beta', 1)
        recommendations[category][key] = [random.betavariate(a, b) for _ in range(N)]

# Poisson-Gamma repeat rounds: sample λ from Gamma, then k from Poisson(λ)
recommendations['repeat_rounds'] = {}
for key, params in weights.get('repeat_rounds', {}).items():
    a, b = params.get('alpha', 2), params.get('beta', 1)
    samples = []
    for _ in range(N):
        lam = random.gammavariate(a, 1.0 / b)  # Gamma(α, β) → rate λ
        # Poisson sampling via inverse transform (stdlib only, no numpy)
        L, k, p = math.exp(-lam), 0, 1.0
        while p > L:
            k += 1
            p *= random.random()
        samples.append(max(1, k - 1))  # at least 1 round
    recommendations['repeat_rounds'][key] = samples

# Ambiguity flags for chain_selection
recommendations['ambiguity'] = {}
chain_sel = recommendations.get('chain_selection', {})
if len(chain_sel) > 1:
    keys = list(chain_sel.keys())
    for i in range(N):
        scores = {k: chain_sel[k][i] for k in keys}
        sorted_keys = sorted(scores, key=scores.get, reverse=True)
        top1 = scores[sorted_keys[0]]
        top2 = scores[sorted_keys[1]] if len(sorted_keys) > 1 else 0
        for k in keys:
            if k not in recommendations['ambiguity']:
                recommendations['ambiguity'][k] = []
            recommendations['ambiguity'][k].append((top1 - top2) < AMBIGUITY_THRESHOLD)

# Write output
output_path = '.claude/.ser-recommendations.json'
try:
    json.dump(recommendations, open(output_path, 'w'), indent=2)
except Exception as e:
    print(f"[SER recommend.py] Failed to write recommendations: {e}", file=sys.stderr)
    sys.exit(1)
