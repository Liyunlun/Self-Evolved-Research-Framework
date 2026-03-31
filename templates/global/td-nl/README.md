# SER v6 — Learning System Documentation

## Overview

SER v6 uses Bayesian learning with Thompson Sampling to optimize skill routing,
chain selection, checkpoint placement, and repeat round counts. The system learns
from observable user behavior, not from model self-evaluation or explicit ratings.

## Core Representations

### Beta(α, β) — Binary choices
Used for: transitions, chain selection, checkpoints, step skip probabilities.
- Mean = α / (α + β)
- Update: user takes option → option.α += 1 (no penalty on unchosen)
- Prior: Beta(1, 1) = uniform

### Gamma(α, β) → Poisson — Count data
Used for: repeat round counts.
- Sampling: λ ~ Gamma(α, β), then k ~ Poisson(λ)
- Update: user needed k rounds → α += k, β += 1
- Prior: Gamma(2, 1) → mean 2 rounds

## Thompson Sampling Flow

1. `session.open` runs `recommend.py --samples 10`
2. For each weight, N independent samples are drawn
3. Samples written to `.claude/.ser-recommendations.json`
4. Model pops one sample per decision point
5. If queue exhausted → re-run recommend.py or use posterior mean

## Time Decay

Applied at `session.close` via `update_weights.py`:
- days_elapsed = (now - last_update).days
- factor = 0.95 ^ days_elapsed
- α *= factor, β *= factor
- Floor: min(α, β) >= 1.0

## Reward Signals (Behavioral Only)

| Signal | Weight | Source |
|--------|--------|--------|
| User follows suggested next | 0.35 | G2 actual vs suggested |
| Artifact survival rate | 0.25 | File still referenced later |
| User corrected routing | 0.20 | "No, do X instead" |
| Conversation continuation | 0.20 | Topic shift = satisfied |

## Graceful Degradation

The learning system is an optimization layer, not a functional dependency:
- weights.yaml missing → uniform priors for all decisions
- recommend.py fails → model uses SKILL.md Suggested Next only
- update_weights.py fails → observations lost, next session from last good weights
- observe.sh fails → silent, tool-level data lost
- flock deadlock → timeout after 10s, skip update

## File Layout

```
~/.claude/ser/
├── weights.yaml           # Global Bayesian weights
├── weights.yaml.bak.{1-3} # Auto-backups (last 3)
├── weights.yaml.lock      # flock concurrency
├── config.yaml            # Learning parameters
├── chains.yaml            # Chain templates
├── hooks/
│   ├── session-guard.sh   # First-message session.open enforcement
│   └── observe.sh         # Tool observation (PreToolUse + PostToolUse)
├── scripts/
│   ├── recommend.py       # Thompson Sampling (session.open)
│   └── update_weights.py  # Weight update (session.close)
└── td-nl/
    └── README.md          # This file
```
