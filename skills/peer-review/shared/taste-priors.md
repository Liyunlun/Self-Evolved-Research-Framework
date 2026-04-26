# Taste Priors — What to Notice Across All Stages

This file defines seven reusable probes that a rigorous reviewer applies implicitly. Each
stage reads this file and fires the probes that apply. A probe is *tasteful* when it
tests whether the paper's stated mechanism is actually what produced the reported numbers
— not whether the paper exists, is formatted well, or claims to be novel.

**How to use**: at the start of each stage, scan the probes below. If a probe applies to
what you just read, emit a finding that names the probe. The probe names are stable tags
the orchestrator uses for downstream aggregation; do NOT rename them.

Use only this catalog. Do not invent new probes.

**Finding-shape rule (all probes)**: every finding emitted by a probe must (a) cite
internal evidence from the paper under review (section / equation / figure / table), (b)
name the probe in the `probe:` tag, (c) state what empirical, theoretical, or
presentational change would resolve or downgrade the finding. Do not write illustrative
text that resembles the prose of any specific prior paper; write the concrete mechanics
observed in *this* paper.

---

## Probe 1 — `mechanism_attribution`

**Principle**: The paper's performance gain must be traceable to its *claimed* mechanism, not to confounding architectural or training changes.

**Fires when** any of the following holds:
- The paper claims mechanism M causes gain G, but no ablation isolates M.
- The paper itself reports a setting where M does not hold yet G still appears — so G cannot be *because* of M.
- The experimental regime cannot produce behavior that would distinguish M-works from M-does-not-work.

**What the finding must contain**:
- The paper's stated attribution (mechanism → gain), cited to the section or figure that makes the claim.
- The specific evidence inside the paper that undercuts the attribution — either a missing ablation or an internal inconsistency.
- A concrete resolution: the ablation, control, or regime change that would isolate the claimed mechanism from confounds.

**Severity rule**: if the paper's headline claim depends on the attribution → `major` (poster) or `critical` (oral/best_paper). If the attribution is secondary → `minor`.

---

## Probe 2 — `hidden_assumption_audit`

**Principle**: Every derivation invokes assumptions. An assumption is a contribution only if it holds in the regime the method operates; otherwise it is a hidden failure mode.

**Fires when** any of the following holds:
- A derivation uses an equality/inequality that silently drops a term (the dropped term may be where the claimed phenomenon actually lives).
- An assumption is stated but is trivially false for the actual deployment distribution.
- A bound holds "for any" quantifier over a set that must necessarily include a degenerate case the authors did not intend.

**What the finding must contain**:
- The exact step or assumption, cited to the equation or lemma number in the paper.
- Why the assumption is load-bearing: name the part of the main claim that depends on it.
- A concrete resolution: either bound the dropped/unjustified term, restrict the claim to the regime where the assumption holds, or supply an empirical check that the assumption is approximately satisfied.

**Severity rule**: if the dropped/violated assumption is load-bearing for the main claim → `major` or higher; if it only affects a secondary claim → `minor`.

---

## Probe 3 — `benchmark_claim_match`

**Principle**: For every primary claim, at least one experiment must run in a regime that could *fail* if the claim were wrong.

**Fires when** any of the following holds:
- The claim is about property P, but every benchmark either does not exercise P or is dominated by a different bottleneck.
- The benchmarks are structurally similar to each other (same family, same observation modality, same horizon scale), so together they test one regime — not a range.
- The paper generalizes to a broad category but exercises only a narrow slice of that category.

**What the finding must contain**:
- The paper's stated property-of-interest, cited to the motivation section.
- The regime the reported benchmarks actually exercise, cited to the experiments section.
- A concrete resolution: either rescope the claim to match the tested regime, or add a benchmark in a regime where property-P-absent methods are known to fail.

**Severity rule**: `major` when the claim is headline; `minor` when the claim is secondary and the paper admits the limitation explicitly.

---

## Probe 4 — `efficiency_vs_claim`

**Principle**: When a method adds forward passes, backward passes, memory, or search, its computational cost must be reported *at the setting where the claimed advantage is strongest* — not at the cheapest setting.

**Fires when** any of the following holds:
- Wall-clock is reported only on a simpler/smaller environment, while the claim is about scaling to a larger one.
- The method introduces a multiplicative factor (replication count, inner-loop depth, search width) but the reported cost does not vary that factor.
- Back-of-envelope compute accounting (passes × batch × steps) contradicts the reported wall-clock.

**What the finding must contain**:
- The method's added computational cost, identified in the algorithm or pseudocode.
- The setting at which cost is reported vs. the setting at which the advantage is strongest.
- A concrete resolution: the specific cost breakdown (e.g., per-update passes, or variation along the expensive axis) that would let the reader judge the trade-off.

**Severity rule**: `major` when the cost could plausibly dominate the reported advantage; `minor` when the added cost is clearly negligible and the paper acknowledges it.

---

## Probe 5 — `terminology_audit`

**Principle**: A loaded term is a contribution only when the paper's mechanism distinctively realizes that concept. Using the term for a standard mechanism oversells the contribution.

**Fires when** any of the following holds:
- The named mechanism is mathematically equivalent (or near-equivalent) to an established operation whose ordinary name does not carry the loaded connotation.
- The paper does not cite or contrast the established version.
- A structural property of the mechanism directly contradicts the semantic load of the term.

**What the finding must contain**:
- The term in question, cited to the title, abstract, or contribution list.
- The equation that shows the mechanism reducing to a standard operation, cited by equation number.
- A concrete resolution: either add a contrast experiment that the standard operation cannot reproduce, or rename the mechanism to reflect its actual operation.

This probe is *structural*, not stylistic: the trigger is "the math equals a standard operation", not "the name sounds fancy."

**Severity rule**: `major` when the loaded term is in the title or contribution list; `minor` when it only appears in section headings.

---

## Probe 6 — `decorative_theorem`

**Principle**: A theorem is a contribution only when it explains the empirical gain. Existence theorems, combinations of two prior bounds, or asymptotic results that do not tighten any practical regime are decorative.

**Fires when** any of the following holds:
- The theorem establishes existence of an object the paper's method does not compute.
- The theorem is the composition of prior results with no new step.
- The theorem's hypotheses rule out the realistic regime while the method operates outside that regime.
- The paper provides no link between the theorem's conclusion and any experimental metric that improved.

**What the finding must contain**:
- The theorem's precise conclusion, cited to its numbered statement.
- The gap between the theorem's conclusion and any experimental metric in the paper.
- A concrete resolution: either restate the theorem to directly imply an improved metric, or move it to an appendix and refocus the main-text claim.

**Severity rule**: `major` at oral/best_paper (theory contribution overstated); `minor` at poster (decorative theorem is tolerated if clearly labeled).

---

## Probe 7 — `vote_moving_weakness`

**Principle**: Every `[major]` or `[critical]` weakness must be phrased so the authors can tell what concrete evidence would resolve it. A weakness the authors cannot act on is a complaint, not a review.

**Fires when**: a weakness lacks a resolution path — no added experiment, no clarification, no proof step, no rewording would change the reviewer's severity.

**What the audited bullet must contain**:
- The weakness statement, severity-tagged.
- A trailing `Resolution:` clause that names the specific evidence or clarification that would reduce the severity or dissolve the weakness.
- If no such resolution exists, the weakness itself is out of scope for this review — drop it.

**Severity rule**: this probe does not produce new findings; it audits existing ones. Applied by `peer-review-critique` during self-critique (Sub-step B).

---

## Cross-probe rules

- **Do not double-count.** A single weakness usually triggers one probe, not several. If it triggers two, pick the more specific one.
- **Cite internal evidence.** Each finding must cite a section, equation, figure, or table from the paper being reviewed, per `base_instruction.md`.
- **Probes are floors, not ceilings.** The must-check lists in each stage SKILL are separate. Probes add to them; they do not replace them.
- **Language register** matches the rest of the review: neutral, evidence-first, constructive. No sarcasm, no rhetorical questions.
- **Do not import prose** from unrelated papers when writing a finding. Describe only what is in the paper under review.

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
