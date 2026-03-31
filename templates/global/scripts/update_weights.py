#!/usr/bin/env python3
"""SER v6 — Weight Update Script

Reads session observations from logs/observations/, applies time decay,
updates weights.yaml with new observations.

Called by session.close: python3 ~/.claude/ser/scripts/update_weights.py

Uses flock for concurrent write safety.
"""

import fcntl
import json
import math
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from os.path import expanduser, exists

try:
    import yaml
except ImportError:
    print("[SER update_weights.py] PyYAML not available — skipping weight update", file=sys.stderr)
    sys.exit(0)

SER_DIR = expanduser('~/.claude/ser')
WEIGHTS_PATH = os.path.join(SER_DIR, 'weights.yaml')
LOCK_PATH = os.path.join(SER_DIR, 'weights.yaml.lock')
CONFIG_PATH = os.path.join(SER_DIR, 'config.yaml')
OBS_DIR = 'logs/observations'


def load_config():
    if exists(CONFIG_PATH):
        try:
            return yaml.safe_load(open(CONFIG_PATH)) or {}
        except Exception:
            pass
    return {}


def load_weights():
    if exists(WEIGHTS_PATH):
        try:
            return yaml.safe_load(open(WEIGHTS_PATH)) or {}
        except Exception as e:
            print(f"[SER update_weights.py] Corrupt weights.yaml: {e}", file=sys.stderr)
    return {}


def rotate_backups(config):
    """Rotate weights.yaml → .bak.1 → .bak.2 → .bak.3"""
    backup_count = config.get('update', {}).get('backup_count', 3)
    for i in range(backup_count, 1, -1):
        src = f"{WEIGHTS_PATH}.bak.{i-1}"
        dst = f"{WEIGHTS_PATH}.bak.{i}"
        if exists(src):
            shutil.copy2(src, dst)
    if exists(WEIGHTS_PATH):
        shutil.copy2(WEIGHTS_PATH, f"{WEIGHTS_PATH}.bak.1")


def apply_time_decay(weights, config):
    """Apply time-proportional decay to all weights."""
    learning = config.get('learning', {})
    lam = learning.get('time_decay_lambda', 0.95)
    floor = learning.get('decay_floor', 1.0)

    last_update_str = weights.get('meta', {}).get('last_update', '')
    if not last_update_str:
        return

    try:
        last_update = datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        days = (now - last_update).days
    except Exception:
        days = 0

    if days <= 0:
        return

    factor = lam ** days

    for category in ['transitions', 'chain_selection', 'checkpoints', 'step_skip', 'repeat_rounds']:
        for key, params in weights.get(category, {}).items():
            if 'alpha' in params and 'beta' in params:
                params['alpha'] = max(floor, params['alpha'] * factor)
                params['beta'] = max(floor, params['beta'] * factor)


def check_weight_explosion(weights, config):
    """Auto-normalize if any weight exceeds threshold."""
    learning = config.get('learning', {})
    max_threshold = learning.get('weight_explosion_max', 1000)
    divisor = learning.get('weight_explosion_divisor', 100)

    for category in ['transitions', 'chain_selection', 'checkpoints', 'step_skip', 'repeat_rounds']:
        for key, params in weights.get(category, {}).items():
            if 'alpha' in params and 'beta' in params:
                m = max(params['alpha'], params['beta'])
                if m > max_threshold:
                    params['alpha'] /= (m / divisor)
                    params['beta'] /= (m / divisor)
                    print(f"[SER update_weights.py] Normalized {category}.{key}", file=sys.stderr)


def load_session_observations():
    """Load today's JSONL observations."""
    observations = []
    if not exists(OBS_DIR):
        return observations

    today = datetime.now().strftime('%Y-%m-%d')
    obs_file = os.path.join(OBS_DIR, f"{today}.jsonl")

    if not exists(obs_file):
        return observations

    try:
        with open(obs_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        observations.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass

    return observations


def apply_observations(weights, observations):
    """Apply observation updates to weights."""
    obs_count = 0

    for obs in observations:
        obs_type = obs.get('type', '')

        if obs_type == 'transition':
            from_skill = obs.get('from', '')
            to_skill = obs.get('to', '')
            key = f"{from_skill} → {to_skill}"
            if key in weights.get('transitions', {}):
                weights['transitions'][key]['alpha'] += 1
                obs_count += 1
            else:
                # New transition discovered
                if 'transitions' not in weights:
                    weights['transitions'] = {}
                weights['transitions'][key] = {'alpha': 2, 'beta': 1}
                obs_count += 1

        elif obs_type == 'checkpoint':
            chain = obs.get('chain', '')
            at = obs.get('at', '')
            key = f"{chain}.{at}"
            interrupted = obs.get('user_interrupted', False)
            if key in weights.get('checkpoints', {}):
                if interrupted:
                    weights['checkpoints'][key]['alpha'] += 1
                else:
                    weights['checkpoints'][key]['beta'] += 1
                obs_count += 1

        elif obs_type == 'skill':
            chain = obs.get('chain', '')
            if chain:
                key = chain
                if key in weights.get('chain_selection', {}):
                    weights['chain_selection'][key]['alpha'] += 1
                    obs_count += 1

    return obs_count


def main():
    config = load_config()

    # Acquire lock with timeout
    lock_timeout = config.get('update', {}).get('lock_timeout_seconds', 10)
    lock_fd = None

    try:
        lock_fd = open(LOCK_PATH, 'w')
        start = time.time()
        while True:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.time() - start > lock_timeout:
                    print("[SER update_weights.py] Lock timeout — skipping update", file=sys.stderr)
                    return
                time.sleep(0.1)

        weights = load_weights()
        if not weights:
            print("[SER update_weights.py] No weights to update", file=sys.stderr)
            return

        # Rotate backups
        rotate_backups(config)

        # Apply time decay
        apply_time_decay(weights, config)

        # Apply observations
        observations = load_session_observations()
        obs_count = apply_observations(weights, observations)

        # Update meta
        if 'meta' not in weights:
            weights['meta'] = {}
        weights['meta']['total_observations'] = weights['meta'].get('total_observations', 0) + obs_count
        weights['meta']['last_update'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        # Check for weight explosion
        check_weight_explosion(weights, config)

        # Atomic write: write to tmp, then rename
        tmp_path = WEIGHTS_PATH + '.tmp'
        with open(tmp_path, 'w') as f:
            yaml.dump(weights, f, default_flow_style=False, allow_unicode=True)
        os.rename(tmp_path, WEIGHTS_PATH)

        if obs_count > 0:
            print(f"[SER update_weights.py] Updated {obs_count} observations", file=sys.stderr)

    except Exception as e:
        print(f"[SER update_weights.py] Error: {e}", file=sys.stderr)
    finally:
        if lock_fd:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                lock_fd.close()
            except Exception:
                pass


if __name__ == '__main__':
    main()
