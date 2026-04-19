# SER v6 Redesign Plan

> Self-Evolving Research Framework — Architecture Redesign
> Status: Draft v2 (post-review revision)
> Date: 2026-03-30

---

## Table of Contents

1. [Current Problems](#1-current-problems)
2. [Design Principles](#2-design-principles)
3. [Skill System Redesign](#3-skill-system-redesign)
4. [Skill Chain Architecture](#4-skill-chain-architecture)
5. [Bayesian Learning System](#5-bayesian-learning-system)
6. [Autonomy Control](#6-autonomy-control)
7. [CLAUDE.md Restructuring](#7-claudemd-restructuring)
8. [Hook Configuration](#8-hook-configuration)
9. [ECC + TD-NL Global Infrastructure](#9-ecc--td-nl-global-infrastructure)
10. [Weight Management](#10-weight-management)
11. [Migration Plan](#11-migration-plan)
12. [New Project Setup](#12-new-project-setup)
13. [Failure Recovery and Graceful Degradation](#13-failure-recovery-and-graceful-degradation)
14. [Open Questions](#14-open-questions)

---

## 1. Current Problems

SER v5 has three layers of failure:

### 1.1 Skills — Custom format, invisible to Claude Code

Skills live at `skills/micro/*.md` — a custom natural language format. Claude Code's native skill system expects `.claude/skills/<name>/SKILL.md`. Claude Code cannot auto-discover or auto-load SER skills.

### 1.2 Hooks — Entire chain is broken

| Component | Status | Root Cause |
|-----------|--------|------------|
| `.claude/hooks.json` | Ignored | Wrong filename — Claude Code reads `settings.json` |
| `.claude/settings.json` | Missing | Never created by `setup.sh` |
| `ser-intent-router.sh` | Dead | Exists on disk, registered nowhere |
| `observe.sh` (ECC) | Dead | Registered in `hooks.json` which is ignored |

Verification: `observe.sh` creates a `projects/` directory on first run. That directory does not exist — confirming it has never executed.

### 1.3 CLAUDE.md Intent Router — Advisory only

The 47-row intent routing table in CLAUDE.md is the only thing that actually functions. But it depends entirely on LLM compliance — no enforcement, no fallback. In long conversations, the model frequently ignores the routing table.

### 1.4 setup.sh — Skips all Claude Code integration

`setup.sh` (363 lines) creates the data scaffold (directories, configs, TD-NL infrastructure) but does not:
- Create `.claude/` directory
- Install any hooks or `settings.json`
- Set up skills in Claude Code format
- Register `ser-intent-router.sh` or `observe.sh`

`integrate.md` describes a hook installation process that `setup.sh` does not implement.

---

## 2. Design Principles

### 2.1 Model autonomy over mechanical routing

The model's NLU is far superior to regex for intent matching. Skill routing should leverage model understanding, not fight it.

### 2.2 Self-evolution as first-class feature

Skill routing, chain selection, and checkpoint placement are all learnable parameters — not hardcoded config.

### 2.3 Behavioral data over self-assessment

User behavior (what they actually do) is more reliable than model self-evaluation or user ratings. The learning system should be grounded in observable signals.

### 2.4 Bayesian updates for small-data learning

Each skill transition may only be observed a few times per session. Bayesian methods (Beta distributions) handle sparse data naturally and provide uncertainty estimates for free.

### 2.5 Graceful degradation

Any learning component can fail without breaking research workflows. The system must degrade to "no learning but fully functional" mode when components are unavailable or corrupted.

---

## 3. Skill System Redesign

### 3.1 Decision: Grouped SKILL.md (Option B)

Convert ~14 micro-skill spec files into grouped `.claude/skills/*/SKILL.md` files. Each group contains multiple sub-skills.

```
.claude/skills/
├── paper/SKILL.md        → paper.read, paper.compare, paper.index, lit.search
├── theory/SKILL.md       → theory.formalize, decompose, search, counterexample, generalize
├── proof/SKILL.md        → proof.critique, write, fix, formalize, verify
├── writing/SKILL.md      → writing.draft, outline, review, polish, figure, compile
├── planning/SKILL.md     → plan.suggest, milestone, status, progress, decision, experiment.analyze
├── experiment/SKILL.md   → experiment.plan, run, monitor, math.dse
├── idea/SKILL.md         → idea.discover, verify, refine
├── visual/SKILL.md       → pixel.create, paper.illustrate
├── checklist/SKILL.md    → checklist.create, verify, update, status
├── research/SKILL.md     → research.explore, design.converge
├── memory/SKILL.md       → memory.write, retrieve, consolidate, forget
├── review/SKILL.md       → dual_review (external model review)
└── meta/SKILL.md         → session.open, session.close, G2, evolve.suggest, evolve.apply, general.research
```

`session.open` and `session.close` are skills in `meta/SKILL.md`. CLAUDE.md contains a one-line trigger rule (`execute session.open at conversation start`) and the session-guard hook enforces it. The full procedure lives in the skill spec.

`dual_review` is a regular skill in `review/SKILL.md`, not a special annotation on chains.

### 3.2 Why grouped, not 47 individual files

| Concern | 47 files | ~14 grouped files |
|---------|----------|-------------------|
| Context cost at conversation start | 47 skill descriptions loaded | ~14 skill descriptions loaded |
| Shared context (data contracts, formats) | Duplicated across files | Shared within group |
| Fault tolerance | Wrong skill = wrong spec entirely | Wrong sub-skill but right group = model can self-correct |
| Maintenance | 47 directories | ~14 directories |

### 3.3 SKILL.md structure

Each SKILL.md follows this format:

```markdown
# /<group> — Group Description

When to use this skill:
- [natural language trigger descriptions]
- [model reads these to decide whether to use this skill]

## <sub-skill-name>

**Trigger**: [when this sub-skill applies]

### Process
[execution spec — the existing micro-skill content]

### Suggested Next
[transition suggestions with reasons — populated/updated by TD-NL]
[RULE: if a transition is already covered by chains.yaml, do not duplicate here]
```

### 3.4 Routing mechanism

No regex hooks. No intent router. The model reads SKILL.md trigger descriptions and decides autonomously.

Why this is better than regex:
- "帮我比较这两篇论文" → model understands = paper.compare
- "这两篇文章有什么区别" → regex misses, model understands
- "A 和 B 的方法差在哪" → regex misses, model understands

---

## 4. Skill Chain Architecture

### 4.1 Problem: most workflows are cross-group

Real research workflows span multiple skill groups:

```
Literature survey:  lit.search → paper.read → paper.compare → writing.draft
                    (paper)      (paper)      (paper)         (writing)

Idea development:   idea.discover → idea.verify → dual_review → idea.refine
                    (idea)         (idea)        (review)       (idea)

Proof cycle:        theory.formalize → proof.write → proof.critique → dual_review → proof.fix
                    (theory)          (proof)        (proof)          (review)       (proof)

Experiment loop:    experiment.plan → experiment.run → experiment.analyze → decision.analyze
                    (experiment)     (experiment)      (planning)          (planning)
```

Current SER has no chain concept — the CLAUDE.md intent router is flat (pattern → single skill).

### 4.2 Chain storage: centralized `chains.yaml`

Chains are cross-group global knowledge. They don't belong in any single SKILL.md.

**Location**: `~/.claude/ser/chains.yaml` (global — shared across all SER projects)

```yaml
chains:
  literature_survey:
    trigger: "user wants literature survey, related work, or background research"
    steps: [lit.search, paper.read, paper.compare, writing.draft]
    selection_weight: {alpha: 1, beta: 1}
    repeat: {}
    checkpoints:
      after_paper.read:
        weight: {alpha: 1, beta: 1}

  idea_pipeline:
    trigger: "user has an idea to develop or wants brainstorming"
    steps: [idea.discover, idea.verify, dual_review, idea.refine]
    selection_weight: {alpha: 1, beta: 1}
    repeat:
      verify_review_refine:
        rounds_dist: {alpha: 2, beta: 1}
    checkpoints:
      after_discover:
        weight: {alpha: 1, beta: 1}

  proof_cycle:
    trigger: "user needs to write or verify a proof"
    steps: [theory.formalize, proof.write, proof.critique, dual_review, proof.fix]
    selection_weight: {alpha: 1, beta: 1}
    repeat:
      critique_review_fix:
        rounds_dist: {alpha: 3, beta: 1}
    checkpoints: {}

  paper_writing:
    trigger: "user is writing a paper or paper section"
    steps: [writing.outline, writing.draft, writing.review, dual_review, writing.polish]
    selection_weight: {alpha: 1, beta: 1}
    repeat:
      review_polish:
        rounds_dist: {alpha: 2, beta: 1}
    checkpoints:
      after_outline:
        weight: {alpha: 1, beta: 1}
```

Note: all weights initialized to `{alpha: 1, beta: 1}` (uniform prior). The system learns from user behavior, not from model-generated guesses. See §5.5 for cold start strategy.

### 4.3 One skill, multiple chains

A single trigger can match multiple chains. The model selects using pre-computed recommendations from `recommend.py` (see §5.3):

```yaml
# User says "I have an idea"
# Matches:
idea_pipeline:         selection_weight: {alpha: 6, beta: 3}  # thorough, with dual review
idea_quick_check:      selection_weight: {alpha: 3, beta: 5}  # just verify novelty
```

### 4.4 Chain templates are learnable

Every parameter in a chain template can be optimized:

| Parameter | Distribution | Learned from |
|-----------|-------------|-------------|
| `selection_weight` | Beta(α, β) | Which chain users actually follow in this context |
| `checkpoint.weight` | Beta(α, β) | Whether users interrupt at this point |
| `repeat.rounds_dist` | Gamma(α, β) as Poisson prior | How many rounds users need before satisfaction |
| per-step `skip_prob` | Beta(α, β) | Whether users skip this step |

### 4.5 SKILL.md "Suggested Next" vs chains.yaml

Both exist, serving complementary (not competing) purposes:

| | SKILL.md Suggested Next | chains.yaml |
|---|---|---|
| Scope | Single-step transitions not in any chain | Multi-step workflows |
| When used | No chain active, ad-hoc navigation | Structured multi-step execution |
| Learning | Independent — only for transitions NOT covered by chains | Chain-level learning |
| Example | "After paper.read, you might want lit.search" | "Literature survey = lit.search → paper.read → compare → draft" |

**Rule**: if a transition is already part of a chain template, `Suggested Next` does not independently learn that transition's weight. This prevents the two systems from competing.

---

## 5. Bayesian Learning System

### 5.1 Core representation

Two conjugate distribution families:

**Beta(α, β)** — for binary choices (transition taken/not taken, step skipped/not skipped):
```
mean = α / (α + β)
variance = αβ / ((α+β)²(α+β+1))
```

**Gamma(α, β)** — as Poisson rate prior for count data (repeat rounds):
```
mean = α / β
posterior update: observe k rounds → α += k, β += 1
```

### 5.2 Update rule

For binary weights (transitions, chain selection, checkpoints):
```
User takes transition A:
  A.α += 1
  (other alternatives are NOT penalized — Thompson Sampling handles exploration naturally)
```

**No penalty on unchosen alternatives.** Previous design penalized alternatives with `B.β += 1`, which causes winner-take-all convergence and kills exploration. Thompson Sampling already explores low-certainty options via variance — additional punishment is both unnecessary and harmful.

For count weights (repeat rounds):
```
User needed k rounds:
  rounds_dist.α += k
  rounds_dist.β += 1
```

### 5.3 Thompson Sampling — execution model

Thompson Sampling requires actual random number generation. The LLM cannot do this reliably. Therefore, sampling is performed by a **script**.

**Key design: per-decision sampling, not per-session.**

A single sample at session start would fix one random draw for the entire conversation, losing the per-decision explore/exploit tradeoff that makes Thompson Sampling effective. Instead, `recommend.py` generates a **queue of N independent samples** for each weight. The model consumes one sample per decision point.

**Execution flow**:

```
session.open:
  1. Model reads meta/SKILL.md → triggers session.open procedure
  2. Procedure includes: run ~/.claude/ser/scripts/recommend.py --samples 10
  3. recommend.py reads weights.yaml, generates N independent samples per weight,
     writes sample queues to .claude/.ser-recommendations.json
  4. Model reads .ser-recommendations.json into context

During session (each decision point):
  5. Model pops the next sample from the queue for the relevant weight
  6. If queue exhausted → model re-runs recommend.py (or falls back to mean)
```

**`recommend.py`** (stateless, ~60 lines):
```python
import json, math, random, yaml, sys
from os.path import expanduser

N = int(sys.argv[sys.argv.index('--samples') + 1]) if '--samples' in sys.argv else 10
weights = yaml.safe_load(open(expanduser('~/.claude/ser/weights.yaml')))

recommendations = {}

# Beta-distributed weights: generate N samples each
for category in ['transitions', 'chain_selection', 'checkpoints', 'step_skip']:
    recommendations[category] = {}
    for key, params in weights.get(category, {}).items():
        a, b = params['alpha'], params['beta']
        recommendations[category][key] = [random.betavariate(a, b) for _ in range(N)]

# Poisson-Gamma repeat rounds: sample λ from Gamma, then k from Poisson(λ)
recommendations['repeat_rounds'] = {}
for key, params in weights.get('repeat_rounds', {}).items():
    a, b = params['alpha'], params['beta']
    samples = []
    for _ in range(N):
        lam = random.gammavariate(a, 1.0 / b)   # Gamma(α, β) → rate λ
        # Poisson sampling via inverse transform (stdlib only, no numpy)
        L, k, p = math.exp(-lam), 0, 1.0
        while p > L:
            k += 1
            p *= random.random()
        samples.append(max(1, k - 1))             # at least 1 round
    recommendations['repeat_rounds'][key] = samples

json.dump(recommendations, open('.claude/.ser-recommendations.json', 'w'), indent=2)
```

**Why sample queues, not single samples**:
- Single sample: one random draw locks the entire session → no intra-session exploration
- Queue of N: each decision point gets a fresh draw → true per-decision Thompson Sampling
- N=10 covers typical session length; if exhausted, model re-samples or uses posterior mean

This naturally balances exploration and exploitation:
- High α, low β (known good path) → samples consistently high → exploit
- Low α, low β (uncertain) → high variance → sometimes samples high → explore
- No manual ε parameter needed

### 5.4 Time decay

User preferences change. Apply time-proportional decay at each session.close:

```
days_elapsed = (now - last_update_timestamp).days
decay_factor = λ ^ days_elapsed    # λ = 0.95

α *= decay_factor
β *= decay_factor
then add new observations
```

Decay is applied **once per session.close**, proportional to actual elapsed time. Daily sessions apply λ once; a week gap applies λ⁷ ≈ 0.70.

Floor: `min(α, β) >= 1.0` — prevents distributions from collapsing. Beta(0.5, 0.5) is the Jeffreys prior with U-shaped density that produces extreme samples; Beta(1, 1) is the safe uniform baseline.

### 5.5 Cold start strategy

**No model-generated defaults.** All weights start from uniform priors:

- Binary weights: Beta(1, 1) — maximally uncertain, equal probability
- Count weights: Gamma(2, 1) — mean 2 rounds, high variance

**Burn-in period** (first ~10-15 sessions):
- Ambiguity threshold (§5.6) is set higher during burn-in: `AMBIGUITY_THRESHOLD = 0.3` (vs 0.1 normal)
- This causes more frequent user queries, producing high-quality calibration data
- After burn-in, threshold drops to 0.1 and system runs more autonomously
- Burn-in ends when `total_observations > BURN_IN_MIN` (configurable, default 30)

**Group-level priors** still apply: when a new sub-skill is added to an existing group, it inherits the group's aggregated priors (not uniform). This is a Bayesian hierarchical prior, not model guessing.

### 5.6 Ambiguity-driven user intervention

When Thompson Sampling produces ambiguous results, ask the user:

```python
# In recommend.py, for each sample in the queue, flag ambiguities:
for i in range(N):
    scores = {k: samples[k][i] for k in options}
    sorted_keys = sorted(scores, key=scores.get, reverse=True)
    top1, top2 = scores[sorted_keys[0]], scores.get(sorted_keys[1], 0) if len(sorted_keys) > 1 else 0

    ambiguity_flags[i] = (top1 - top2) < AMBIGUITY_THRESHOLD
```

The model reads the per-sample `ambiguous` flag from the recommendations file. When the flag is true at a decision point, the model asks the user. The user is only interrupted when the system genuinely doesn't know.

### 5.7 Reward signals (behavioral only)

Model self-evaluation and explicit ratings are unreliable (CLI has no feedback buttons). Use observable behavioral signals only:

| Signal | Weight | Source | Measurability |
|--------|--------|--------|---------------|
| Did user follow suggested next | 0.35 | G2 actual_next vs suggested | High — directly recorded |
| Artifact survival rate | 0.25 | File still referenced in later sessions | High — observe.sh tracks Read targets |
| User corrected routing | 0.20 | User says "no, do X instead" | Medium — model must recognize correction vs new request |
| Conversation continuation pattern | 0.20 | User continues same topic (unsatisfied) vs moves on (satisfied) | Medium — infer from topic shift |

Signal weights are **fixed initial values**. Future versions may learn these weights via a secondary bandit, but current data volume is insufficient to justify the added complexity.

Principle: **behavior over words**. A user who moves on to the next topic without follow-up questions was likely satisfied.

### 5.8 Chain parameter learning: repeat rounds

Repeat rounds use **Poisson-Gamma** conjugate (two-step sampling):

```yaml
repeat:
  verify_review_refine:
    rounds_dist: {alpha: 2, beta: 1}   # Gamma prior → Poisson rate λ ≈ 2
```

**Sampling** (in recommend.py): first draw rate λ ~ Gamma(α, β), then draw integer k ~ Poisson(λ). This produces a proper integer round count, not a continuous value.

**Update** after each chain execution:
```
User needed k rounds → rounds_dist.α += k, rounds_dist.β += 1
```

Posterior mean of λ = α/β converges to the true average round count. The Poisson layer converts this to an integer recommendation. No need for the model to evaluate "quality >= threshold" — just learn how many rounds users typically need.

### 5.9 Update timing

**At session.close** — batch update after aggregating all G2 entries from the session. Aligns with existing `evolve.suggest` timing. Reduces noise compared to per-transition updates.

Update script (`update_weights.py`) is called by the session.close skill:
1. Read `logs/observations/*.jsonl` for this session
2. Acquire file lock on `weights.yaml` (see §10.4)
3. Apply time decay
4. Apply observation updates
5. Write weights.yaml
6. Auto-backup (see §13)

---

## 6. Autonomy Control

### 6.1 When to auto-chain vs ask user

Based on transition weight (data-driven), not model self-assessed confidence:

```
weight > 0.7    → auto-execute, notify user what was done
weight 0.3–0.7  → suggest, wait for user response
weight < 0.3    → only execute on explicit user request
```

These thresholds themselves can be tuned per-user over time.

### 6.2 Autonomous chains

The model can plan and execute multi-step chains without interrupting the user:

```
idea.discover → idea.verify → dual_review → idea.refine → idea.verify → dual_review → idea.refine → report to user
```

User intervention happens:
- At **chain end** (always — report results)
- At **checkpoints** (when `checkpoint.weight` is high enough)
- At **ambiguity points** (when recommendations flag `ambiguous: true`)

### 6.3 Learning from user interventions

When the user does intervene (by choice or by system request):
1. Record the user's actual choice
2. Update the relevant weights (α += 1 for chosen option)
3. If user chose a path not in the chain template → add it as a new transition

When the user doesn't intervene (chain runs autonomously):
1. Record implicit signals (artifact survival, topic continuation)
2. Update chain selection and round weights
3. Successful autonomous runs increase future autonomy (weights drift toward > 0.7)

### 6.4 User feedback is noisy — mitigations

| Problem | Mitigation |
|---------|-----------|
| User chooses suboptimally | Weight multiple signals, not just choice |
| User preferences change | Time decay (λ = 0.95, time-proportional) |
| Small sample size | Bayesian uncertainty → conservative behavior until data accumulates |
| Weight divergence | Floor at min(α,β) >= 1.0; monitor via `ser doctor` |

---

## 7. CLAUDE.md Restructuring

### 7.1 Current: 296 lines, mixed concerns

### 7.2 What stays in CLAUDE.md

| Section | Lines | Reason to keep |
|---------|-------|----------------|
| **Session trigger rule** | ~3 | `Execute session.open at conversation start` — one-liner, hook enforced |
| **Skill chain protocol** | ~20 | Decision rules for chain selection — model needs this every conversation |
| **Reference docs table** | ~15 | Navigation to detailed specs — model knows where to look |
| **Checklist engine** | ~15 | Cross-skill global format spec |
| **Data contracts** | ~40 | Shared formats (log YAML, paper notes, checklist items, memory structure) |
| **Directory structure** | ~45 | Model needs to know where files go |

**Estimated: ~140 lines**

### 7.3 Skill chain protocol (new section in CLAUDE.md)

```markdown
## Skill Chain Protocol

session.open loads `~/.claude/ser/chains.yaml` and `.claude/.ser-recommendations.json`.

Selecting next action:
1. If active chain → follow chain steps in order
2. If no active chain → match chains.yaml triggers to user intent
3. Multiple chains match → use recommendation scores (if ambiguous, ask user)
4. No chain matches → read SKILL.md "Suggested Next" for single-step transitions

After every skill execution, record G2 (what ran, what was suggested, what user actually did).
At session.close, execute evolve.suggest to update weights.
```

### 7.4 Reference docs table (new section in CLAUDE.md)

```markdown
## Reference Docs

Read these when you need detailed procedures:

| Need to know | Read |
|-------------|------|
| session.open/close full steps | `.claude/skills/meta/SKILL.md` |
| Chain templates and triggers | `~/.claude/ser/chains.yaml` |
| Weight update and learning mechanics | `~/.claude/ser/td-nl/README.md` |
| G2 feedback recording format | `.claude/skills/meta/SKILL.md` → G2 section |
| External model review process | `.claude/skills/review/SKILL.md` |
| Skill evolution (evolve.suggest/apply) | `.claude/skills/meta/SKILL.md` → evolve section |
```

### 7.5 What moves out

| Section | Destination | Reason |
|---------|-------------|--------|
| **Intent router table** (47 rows) | Deleted | Replaced by SKILL.md trigger descriptions + chains.yaml |
| **Session protocol** (full procedure) | `meta/SKILL.md` → session.open, session.close | Now a skill, CLAUDE.md keeps only the trigger rule |
| **TD-NL explanation** | `~/.claude/ser/td-nl/README.md` | System internals, model doesn't need math details |
| **Dual review** | `review/SKILL.md` | Now a regular skill |
| **Token budget** | Deleted | No behavioral impact |

---

## 8. Hook Configuration

### 8.1 Decision: hooks for lifecycle + observation only, not intent routing

| Hook | Event | Script | Purpose |
|------|-------|--------|---------|
| session-guard | `UserPromptSubmit` | `session-guard.sh` | Detect first message → inject "execute session.open" |
| observe (pre) | `PreToolUse` | `observe.sh` | Collect tool usage data |
| observe (post) | `PostToolUse` | `observe.sh` | Collect tool usage data |

**No intent router hook.** Skill routing is handled by model NLU + SKILL.md descriptions.

### 8.2 `.claude/settings.json`

Hook scripts live globally at `~/.claude/ser/hooks/`. Each project's `settings.json` references them using **absolute paths** written at install time by `setup.sh`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "command": "/home/user/.claude/ser/hooks/session-guard.sh",
        "timeout": 3000
      }
    ],
    "PreToolUse": [
      {
        "matcher": "*",
        "command": "CLAUDE_HOOK_PHASE=pre /home/user/.claude/ser/hooks/observe.sh",
        "timeout": 5000
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "command": "CLAUDE_HOOK_PHASE=post /home/user/.claude/ser/hooks/observe.sh",
        "timeout": 5000
      }
    ]
  }
}
```

**Why absolute paths**: JSON has no variable expansion. Neither `~` nor `$HOME` is guaranteed to expand in Claude Code's hook command execution. `setup.sh` resolves `$HOME` at install time and writes the literal absolute path. This eliminates an entire class of "hooks silently don't work" failures — the exact problem that killed SER v5 (§1.2).

### 8.3 session-guard.sh

Minimal script — only fires on first message per conversation:

```bash
#!/usr/bin/env bash
MARKER=".ser/session-active"
if [ ! -f "$MARKER" ]; then
    mkdir -p "$(dirname "$MARKER")" 2>/dev/null
    touch "$MARKER"
    echo "[SER] Execute session.open before responding. Read .claude/skills/meta/SKILL.md."
fi
```

### 8.4 observe.sh — performance contract

**Budget**: each invocation must complete within 50ms. observe.sh appends one JSONL line and exits.

**Failure policy**: silent failure. If write fails (permissions, disk full), observe.sh exits 0 with no output. Observation data loss is acceptable; blocking research workflow is not.

**JSONL rotation**: one file per session (`logs/observations/YYYY-MM-DD-HHMMSS.jsonl`). Prevents single-file growth issues.

---

## 9. ECC + TD-NL Global Infrastructure

### 9.1 Design decision: global scripts + config, per-project data

Scripts, learning parameters, chain templates, and weights are shared across all SER projects. Only raw observation data stays per-project.

### 9.2 Global directory structure

```
~/.claude/ser/
├── hooks/
│   ├── session-guard.sh          # Shared across all projects
│   └── observe.sh                # Shared across all projects
├── scripts/
│   ├── recommend.py              # Thompson Sampling (called by session.open)
│   └── update_weights.py         # Weight update (called by session.close)
├── chains.yaml                   # Global chain templates
├── weights.yaml                  # Global transition weights (single layer)
├── weights.yaml.bak.1            # Auto-backup (last 3 versions)
├── weights.yaml.bak.2
├── weights.yaml.bak.3
├── config.yaml                   # Learning parameters (λ, thresholds, burn-in)
└── td-nl/
    └── README.md                 # System documentation (how learning works)
```

### 9.3 Per-project data

```
<project>/logs/observations/      # JSONL observation data (one file per session)
```

Both ECC (tool-level) and TD-NL (skill-level) write to the same JSONL:

```jsonl
{"type":"tool","tool":"Read","file":"paper/intro.md","duration_ms":120,"ts":"2026-03-30T10:00:01Z"}
{"type":"tool","tool":"Bash","cmd":"python train.py","duration_ms":45000,"ts":"2026-03-30T10:00:02Z"}
{"type":"skill","skill":"paper.read","chain":"literature_survey","step":2,"ts":"2026-03-30T10:01:00Z"}
{"type":"transition","from":"paper.read","to":"paper.compare","suggested":true,"ts":"2026-03-30T10:05:00Z"}
{"type":"checkpoint","chain":"literature_survey","at":"after_paper.read","user_interrupted":false,"ts":"2026-03-30T10:05:01Z"}
```

### 9.4 Why unified storage

Tool-level data enriches skill-level analysis:

- `paper.read` with 3× WebFetch + 5× Read → deep reading session
- `paper.read` with 1× Read → quick skim
- This context informs chain next-step selection (deep read → more likely to need paper.compare)

ECC's `evolve` analyzes tool patterns. TD-NL's `evolve.suggest` analyzes skill patterns. Both read the same JSONL, filtering by `type`.

### 9.5 Why global

- Hook scripts updated once → all projects benefit
- Learning parameters tuned in one place
- Chain templates are research-workflow knowledge, not project-specific
- Weights reflect user habits across all projects
- New projects work immediately — no bootstrapping needed

### 9.6 Migration from v5

- Move ECC observation target from `.ecc-instincts/projects/` to project-local `logs/observations/`
- Convert TD-NL `feedback-log.md` to JSONL format
- Move hook scripts from per-project `.claude/hooks/` to `~/.claude/ser/hooks/`

---

## 10. Weight Management

### 10.1 Single global weights

No three-layer hierarchy. One `~/.claude/ser/weights.yaml` updated by all projects:

```yaml
meta:
  total_observations: 0          # for burn-in tracking
  last_update: "2026-03-30T10:00:00Z"

transitions:
  paper.read → paper.compare: {alpha: 1, beta: 1}
  paper.read → lit.search: {alpha: 1, beta: 1}
  idea.discover → idea.verify: {alpha: 1, beta: 1}

chain_selection:
  literature_survey: {alpha: 1, beta: 1}
  idea_pipeline: {alpha: 1, beta: 1}
  proof_cycle: {alpha: 1, beta: 1}

checkpoints:
  literature_survey.after_paper.read: {alpha: 1, beta: 1}
  idea_pipeline.after_discover: {alpha: 1, beta: 1}

repeat_rounds:
  idea_pipeline.verify_review_refine: {alpha: 2, beta: 1}
  proof_cycle.critique_review_fix: {alpha: 3, beta: 1}

step_skip:
  proof_cycle.dual_review: {alpha: 1, beta: 1}
  paper_writing.dual_review: {alpha: 1, beta: 1}
```

### 10.2 Why not per-project

- Research workflows are similar across projects
- Per-project weights starve for data (few sessions per project)
- User habits are stable across projects
- One layer eliminates all aggregation complexity

### 10.3 New project initialization

1. If `~/.claude/ser/weights.yaml` exists → use it (user already has SER history)
2. If not → create with uniform priors Beta(1,1) and Gamma(2,1)

No per-project copy. All projects read and write the same file.

### 10.4 Update flow (with concurrency safety)

```
session.close (any project):
  1. update_weights.py acquires exclusive file lock:
     flock ~/.claude/ser/weights.yaml.lock

  2. Read weights.yaml

  3. Auto-backup: rotate weights.yaml → .bak.1 → .bak.2 → .bak.3

  4. Apply time-proportional decay:
     days = (now - meta.last_update).days
     factor = 0.95 ^ days
     for all (α, β): α *= factor, β *= factor
     enforce floor: min(α, β) >= 1.0

  5. Apply observation updates from this session's G2 entries

  6. Update meta.total_observations and meta.last_update

  7. Write weights.yaml atomically (write to .tmp, then rename)

  8. Release lock
```

**Concurrency guarantee**: `flock` ensures only one session.close can update weights at a time. Other sessions block briefly (typical update takes <100ms).

---

## 11. Migration Plan

### 11.1 Scope: existing SER projects (SPA, SelfEvolveAgent, etc.)

One-time migration script `scripts/migrate-v6.sh`:

```
Phase A: Prepare (all work in temp directories, no destructive changes)

  A1. Backup global state:
      cp -r ~/.claude/ser/ ~/.claude/ser.backup.$(date +%s)/ (if exists)

  A2. Generate new global files in /tmp/ser-v6-staging/:
      - hooks/session-guard.sh, hooks/observe.sh
      - scripts/recommend.py, scripts/update_weights.py
      - chains.yaml (uniform priors)
      - weights.yaml (uniform priors)
      - config.yaml, td-nl/README.md

  A3. Generate new project files in /tmp/ser-v6-project-staging/:
      - Convert skills/micro/*.md → .claude/skills/*/SKILL.md
      - Generate .claude/settings.json
      - Generate restructured CLAUDE.md

  A4. If skills/td-nl/feedback-log.md has historical G2 data:
      → Parse transitions → pre-populate weights in staging

Phase B: Atomic switch

  B1. git checkout -b backup/pre-v6-migration
      git add -A && git commit -m "backup: pre-v6 migration snapshot"

  B2. mv /tmp/ser-v6-staging/ ~/.claude/ser/
      (atomic directory replacement)

  B3. Apply project changes:
      - Copy staged SKILL.md files to .claude/skills/
      - Copy staged settings.json to .claude/
      - Replace CLAUDE.md with staged version

Phase C: Verify (rollback on any failure)

  C1. Run verification checklist (§12.2)
  C2. If any check fails:
      → git checkout backup/pre-v6-migration
      → mv ~/.claude/ser.backup.*/ ~/.claude/ser/
      → report which check failed
```

### 11.2 Rollback safety

- Project files: `git checkout backup/pre-v6-migration`
- Global files: `~/.claude/ser.backup.<timestamp>/` restored to `~/.claude/ser/`
- Both are covered by Phase C automatic rollback on failure

---

## 12. New Project Setup

### 12.1 Updated setup.sh responsibilities

```
Global (once, if not exists):
  1. Create ~/.claude/ser/ directory structure
  2. Install hook scripts and Python scripts
  3. Generate default chains.yaml and weights.yaml (uniform priors)
  4. Write config.yaml and td-nl/README.md
  5. Resolve $HOME to absolute path for settings.json template

Per project:
  6. Create project directory structure
  7. Generate config.yaml from template
  8. Create observation directory (logs/observations/)
  9. Create memory index and session log
  10. Create checklist system
  11. Convert skills/micro/*.md → .claude/skills/*/SKILL.md
  12. Create .claude/settings.json referencing global hooks
  13. Verify all components (run §12.2 checklist)
```

### 12.2 Verification checklist

```bash
echo "=== SER v6 Installation Verification ==="
# Global
[ -f ~/.claude/ser/chains.yaml ]                && echo "✅ global chains.yaml"
[ -f ~/.claude/ser/weights.yaml ]               && echo "✅ global weights.yaml"
[ -x ~/.claude/ser/hooks/session-guard.sh ]     && echo "✅ global session-guard.sh"
[ -x ~/.claude/ser/hooks/observe.sh ]           && echo "✅ global observe.sh"
[ -x ~/.claude/ser/scripts/recommend.py ]       && echo "✅ recommend.py"
[ -x ~/.claude/ser/scripts/update_weights.py ]  && echo "✅ update_weights.py"
# Project
[ -f .claude/settings.json ]                    && echo "✅ project settings.json"
[ -d .claude/skills/paper ]                     && echo "✅ skills converted"
[ -d .claude/skills/meta ]                      && echo "✅ meta skill (session/G2/evolve)"
[ -d .claude/skills/review ]                    && echo "✅ review skill (dual_review)"
[ -d logs/observations ]                        && echo "✅ observation directory"
# Functional test
bash -c "$(grep 'command' .claude/settings.json | head -1 | sed 's/.*: "//;s/".*//')" \
  && echo "✅ hook command executes" || echo "❌ hook command fails (check path expansion)"
echo "Skills: $(ls -1 .claude/skills/ | wc -l) groups"
```

---

## 13. Failure Recovery and Graceful Degradation

### 13.1 Design principle

The learning system is an **optimization layer**, not a **functional dependency**. All research skills must work without it. If any learning component fails, the system degrades to "no personalization, but fully functional."

### 13.2 Failure scenarios and responses

| Scenario | Detection | Response |
|----------|-----------|----------|
| `weights.yaml` corrupted/missing | `recommend.py` fails to parse | Use uniform priors for all decisions; log warning |
| `recommend.py` fails | session.open gets no recommendations file | Model uses SKILL.md Suggested Next only (no chain optimization) |
| `update_weights.py` fails | session.close logs error | Session's observations are lost but system continues; next session starts from last good weights |
| `observe.sh` fails | Silent (by design) | Tool-level observations lost; skill-level G2 still collected by model |
| `session.close` not executed | User closes terminal | Observations in JSONL are preserved; weights not updated this session; next session picks up from last state |
| `flock` deadlock | Lock held > 10s | `update_weights.py` times out, skips update, logs warning |
| `weights.yaml` drift (α or β explode) | `recommend.py` checks `max(α, β) > 1000` | Auto-normalize: divide both by `max/100`, log warning |

### 13.3 Auto-backup strategy

`update_weights.py` rotates backups before every write:
```
weights.yaml.bak.3 → deleted
weights.yaml.bak.2 → weights.yaml.bak.3
weights.yaml.bak.1 → weights.yaml.bak.2
weights.yaml       → weights.yaml.bak.1
(new data)         → weights.yaml
```

Recovery: `cp ~/.claude/ser/weights.yaml.bak.1 ~/.claude/ser/weights.yaml`

### 13.4 SKILL.md protection

`evolve.apply` modifies SKILL.md files. Safeguards:
- Before any edit, copy current version to `skills/td-nl/history/<skill>-<timestamp>.md`
- After edit, validate SKILL.md structure (must have `# /`, `## `, `### Process`, `### Suggested Next` headers)
- If validation fails, auto-rollback from history

---

## 14. Open Questions

### 14.1 Resolved

| Question | Decision |
|----------|----------|
| Hard hooks for routing? | No — model NLU + SKILL.md descriptions |
| Grouped vs individual SKILL.md? | Grouped (~14 files) |
| Chain storage location? | Global `~/.claude/ser/chains.yaml` |
| Intent router table in CLAUDE.md? | Remove — replaced by SKILL.md + chains |
| Bayesian vs other learning? | Beta + Gamma conjugate families + Thompson Sampling |
| Update frequency? | session.close batch update |
| ECC + TD-NL merge? | Shared JSONL storage, separate analysis |
| Initial weights? | Uniform priors Beta(1,1) / Gamma(2,1) — no model guessing |
| Migration approach? | Staged script with atomic switch + auto-rollback |
| session.open/close location? | Skills in `meta/SKILL.md`, trigger rule in CLAUDE.md |
| dual_review implementation? | Regular skill in `review/SKILL.md`, appears as chain step |
| Per-project vs global weights? | Global only — one `weights.yaml` for all projects |
| TD-NL details in CLAUDE.md? | Protocol only (~20 lines), detail docs in reference table |
| Token budget? | Deleted — no behavioral impact |
| Reward signals? | Behavioral only — no explicit ratings (CLI has no UI for it) |
| Update rule penalizes unchosen? | No — only increment chosen α; TS handles exploration |
| Repeat rounds distribution? | Poisson-Gamma conjugate, not Beta |
| Thompson Sampling executor? | `recommend.py` script, runs at session.open |
| Concurrent weight updates? | `flock` file locking |
| Path expansion in settings.json? | Absolute paths written at install time — no `~` or `$HOME` in JSON |
| Cold start strategy? | Uniform priors + elevated ambiguity threshold during burn-in |
| Suggested Next vs chains conflict? | Mutually exclusive: chain-covered transitions not in Suggested Next |
| Failure recovery? | Graceful degradation to no-learning mode; auto-backup |
| Steps order learning? | Per-step skip probability Beta(α,β) instead of full permutation |

### 14.2 To be validated during implementation

| Question | Plan |
|----------|------|
| Normal ambiguity threshold | Start at 0.1, tune based on user feedback frequency |
| Burn-in ambiguity threshold | Start at 0.3, reduce after 30 observations |
| Time decay λ value | Start at 0.95, monitor weight stability |
| Autonomy thresholds (0.3 / 0.7) | Start with these defaults, make configurable in config.yaml |
| Chain template completeness | Start with ~5 core chains, let the system discover new ones |
| Weight explosion threshold | Start at max(α,β) > 1000, auto-normalize |
| observe.sh actual latency | Profile in real usage, target <50ms |
| Signal weight optimization | Defer to v7 — need sufficient data volume first |
| `ser doctor` diagnostic tool | Build after core system is stable |
