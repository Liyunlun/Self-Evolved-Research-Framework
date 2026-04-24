# Taste Priors — What to Notice Across All Stages

This file defines seven reusable probes that a rigorous reviewer applies implicitly. Each
stage reads this file and fires the probes that apply. A probe is *tasteful* when it
tests whether the paper's stated mechanism is actually what produced the reported numbers
— not whether the paper exists, is formatted well, or claims to be novel.

**How to use**: at the start of each stage, scan the probes below. If a probe applies to
what you just read, emit a finding that names the probe. The probe names are stable tags
the orchestrator uses for downstream aggregation; do NOT rename them.

Use only this catalog. Do not invent new probes.

---

## Probe 1 — `mechanism_attribution`

**Principle**: The paper's performance gain must be traceable to its *claimed* mechanism, not to confounding architectural or training changes.

**Fires when** any of the following holds:
- The paper claims mechanism M causes gain G, but no ablation isolates M.
- The paper itself reports a setting where M does not hold (e.g., M was not observed) yet G still appears — so G cannot be *because* of M.
- The experimental regime cannot produce behavior that would distinguish M-works from M-does-not-work.

**Finding shape** (synthetic illustration — do NOT copy a real paper):
> *The paper attributes the improvement on task T to mechanism M, but Table X reports the same improvement in a regime where Section Y states M does not activate. Either M is not the operative mechanism or the attribution is under-specified. Propose: add an ablation that removes M while keeping the rest of the architecture constant, and report G on the same benchmarks.*

**Severity rule**: if the paper's headline claim depends on the attribution → `major` (poster) or `critical` (oral/best_paper). If the attribution is secondary → `minor`.

---

## Probe 2 — `hidden_assumption_audit`

**Principle**: Every derivation invokes assumptions. An assumption is a contribution only if it holds in the regime the method operates; otherwise it is a hidden failure mode.

**Fires when** any of the following holds:
- A derivation uses an equality/inequality that silently drops a term (the dropped term may be where the claimed phenomenon actually lives).
- An assumption is stated but is trivially false for the actual deployment distribution (e.g., "assume uniform policy" for a well-trained policy).
- A bound holds "for any π" or "for any x" but must necessarily include a degenerate case the authors did not intend.

**Finding shape** (synthetic illustration — do NOT copy a real paper):
> *Equation K states H ≥ H' via a step that drops a non-negative term T. The paper's claimed benefit (multi-modality / diversity / stability) resides in T. Maximizing H' alone is therefore insufficient to drive the claimed benefit. Either bound T from below or demonstrate empirically that T is small at convergence.*

**Severity rule**: if the dropped/violated assumption is load-bearing for the main claim → `major` or higher; if it only affects a secondary claim → `minor`.

---

## Probe 3 — `benchmark_claim_match`

**Principle**: For every primary claim, at least one experiment must run in a regime that could *fail* if the claim were wrong.

**Fires when** any of the following holds:
- The claim is about property P (e.g., exploration, generality, long-horizon behavior), but every benchmark either does not exercise P or is dominated by a different bottleneck.
- The benchmarks are structurally similar to each other (same family, same observation modality, same horizon scale), so together they test one regime — not a range.
- The paper generalizes to a broad category (e.g., "language models", "continuous control") but exercises ≤2 narrow instances of that category.

**Finding shape** (synthetic illustration):
> *Section Z claims property P as the central motivation. All reported benchmarks fall in regime R, where property P is not the bottleneck. Either rescope the claim to regime R, or add at least one benchmark in a regime where P-absent methods are known to fail.*

**Severity rule**: `major` when the claim is headline; `minor` when the claim is secondary and the paper admits the limitation explicitly.

---

## Probe 4 — `efficiency_vs_claim`

**Principle**: When a method adds forward passes, backward passes, memory, or search, its computational cost must be reported *at the setting where the claimed advantage is strongest* — not at the cheapest setting.

**Fires when** any of the following holds:
- Wall-clock is reported only on the simpler/smaller environment, while the claim is about scaling to a larger one.
- The method introduces K-way replication, J inner steps, or tree search, but the cost breakdown does not vary K / J / depth.
- Back-of-envelope compute accounting (passes × batch × steps) produces a number that contradicts the reported wall-clock.

**Finding shape** (synthetic illustration):
> *The method adds K auxiliary networks and one inner-loop solve per update. Wall-clock is reported only on the smallest benchmark. Because the claim is strongest on the largest benchmark, add a cost breakdown there. For orientation: reporting passes-per-update × K would already let readers check the trade-off.*

**Severity rule**: `major` when the cost could plausibly dominate the reported advantage; `minor` when the added cost is clearly negligible and the paper acknowledges it.

---

## Probe 5 — `terminology_audit`

**Principle**: A loaded term (e.g., "causal", "bi-level", "self-supervised", "meta-") is a contribution only when the paper's mechanism distinctively realizes that concept. Using the term for a standard mechanism oversells the contribution.

**Fires when** any of the following holds:
- The named mechanism is mathematically equivalent (or near-equivalent) to a well-known un-flashy operation (importance weighting, alternating updates, reweighted regression, etc.).
- The paper does not cite or contrast the un-flashy version.
- A structural property of the mechanism (e.g., symmetry, commutativity) directly contradicts the semantic load of the term.

**Finding shape** (synthetic illustration):
> *The paper terms its mechanism "<loaded term>". Inspection of Equation K shows the mechanism reduces to <standard operation>. The reported improvements are compatible with <standard operation> being the operative effect. Either provide a contrast experiment that <standard operation> cannot reproduce, or rename the mechanism to reflect its actual operation.*

**Severity rule**: `major` when the loaded term is in the title or contribution list; `minor` when it only appears in section headings.

---

## Probe 6 — `decorative_theorem`

**Principle**: A theorem is a contribution only when it explains the empirical gain. Existence theorems, combinations of two prior bounds, or asymptotic results that do not tighten any practical regime are decorative.

**Fires when** any of the following holds:
- The theorem establishes that "there exists a function F that achieves property Q", but the paper's method does not compute F.
- The theorem is the composition of two well-known results with no new step.
- The theorem's hypotheses rule out the realistic regime (e.g., convexity, infinite samples, continuous-time limit) while the method operates in the discrete / finite / non-convex regime.
- The paper provides no link between the theorem's conclusion and any experimental metric that improved.

**Finding shape** (synthetic illustration):
> *Theorem T concludes <existence / asymptotic property>. Nothing in the proof connects T to the empirical improvement on Table X. Either restate T to directly imply the improved metric, or move T to an appendix and refocus the main-text claim.*

**Severity rule**: `major` at oral/best_paper (theory contribution overstated); `minor` at poster (decorative theorem is tolerated if clearly labeled).

---

## Probe 7 — `vote_moving_weakness`

**Principle**: Every `[major]` or `[critical]` weakness must be phrased so the authors can tell what concrete evidence would resolve it. A weakness the authors cannot act on is a complaint, not a review.

**Fires when**: a weakness lacks a resolution path — no added experiment, no clarification, no proof step, no rewording would change the reviewer's severity.

**Finding shape** (stated in the review's Weaknesses bullet itself, not a separate finding):
> *[major] <weakness statement>. Resolution: <what evidence or clarification would reduce this to minor or dissolve it>.*

**Severity rule**: this probe does not produce new findings; it audits existing ones. Applied by `peer-review-critique` during self-critique (Sub-step B).

---

## Cross-probe rules

- **Do not double-count.** A single weakness usually triggers one probe, not several. If it triggers two, pick the more specific one.
- **Cite internal evidence.** Each finding must cite a section, equation, figure, or table from the paper being reviewed, per `base_instruction.md`.
- **Probes are floors, not ceilings.** The must-check lists in each stage SKILL are separate. Probes add to them; they do not replace them.
- **Language register** matches the rest of the review: neutral, evidence-first, constructive. No sarcasm, no rhetorical questions.

## Probe-to-stage map

| Probe | Primary stage | Secondary stage |
|-------|---------------|-----------------|
| `mechanism_attribution` | `peer-review-story` | `peer-review-evaluations` |
| `hidden_assumption_audit` | `peer-review-correctness` | `peer-review-story` |
| `benchmark_claim_match` | `peer-review-evaluations` | — |
| `efficiency_vs_claim` | `peer-review-evaluations` | — |
| `terminology_audit` | `peer-review-significance` | `peer-review-story` |
| `decorative_theorem` | `peer-review-correctness` | `peer-review-significance` |
| `vote_moving_weakness` | `peer-review-critique` (self-critique pass) | — |

A stage fires a probe only when it is the primary stage for that probe and the probe applies. Secondary-stage mentions exist so a stage can refer to a probe that already fired upstream without re-flagging it.
