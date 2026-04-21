---
name: proof-write
description: Produce a first-draft mathematical proof from a bare theorem / proposition statement, selecting an appropriate strategy (direct, contradiction, induction, construction, contrapositive) and laying out each step with explicit justification. Saves to `paper/proofs/{name}.tex` or `outputs/{topic}/proofs/{name}.tex`. Triggers on "prove this", "write a proof of", "prove that …", "证明". Upstream of `proof-critique → proof-fix → proof-formalize → proof-verify`; use those skills instead when the user already has a draft.
---

# proof-write

**Trigger**: User gives a theorem / proposition / claim and asks for a proof, with no existing draft. For critiquing a user-provided draft use `proof-critique`; for repairing identified issues use `proof-fix`; for polishing an already-validated proof into LaTeX use `proof-formalize`; for mechanical verification use `proof-verify`.

**Process**:

### 1. Analyze the proposition

- Extract the **precise** statement. Rewrite it in standard form (∀ x ∈ X, P(x) ⇒ Q(x)) and read it back to the user if any ambiguity exists ("you said 'for all sufficiently large n' — is that n ≥ n₀ for some n₀, or n → ∞?"). Do not paper over ambiguity — a proof of the wrong statement wastes both of your iterations.
- Classify the statement type — the type drives strategy selection:
  - **Universal** (∀ x, P(x)): direct / induction / contrapositive
  - **Existential** (∃ x, P(x)): construction (build x) or non-constructive (pigeonhole, cardinality, fixed-point)
  - **Equivalence** (P ⇔ Q): prove both directions separately
  - **Bound / inequality** (|f(x)| ≤ g(x)): usually direct or by induction on the recursive structure of f
  - **Uniqueness** (∃! x, P(x)): prove existence + then assume two and show equal
  - **Negation / non-existence**: contradiction or diagonal argument
- List the **available toolkit**: premises given, prior lemmas the user has cited, theorems from standard references the user has mentioned, and definitions currently in scope. If the user references "Lemma 3.2" without giving it, ask — don't invent.

### 2. Select proof strategy

Choose based on the structure of the claim. State **why** the chosen strategy fits in one sentence so the user can course-correct before you commit to a long derivation.

| Strategy | Fits when |
|---|---|
| **Direct** | Premises give a clear chain of implications to the conclusion |
| **Contradiction** | Negating the conclusion gives a concrete object to manipulate |
| **Contrapositive** | ¬Q is easier to assume than P (common for negated conclusions) |
| **Induction** | Claim is parameterized by ℕ / finite structure / recursive object |
| **Strong induction** | Inductive step needs ≥2 prior cases, not just n−1 |
| **Structural induction** | Claim is over inductively-defined types (trees, terms, proofs) |
| **Construction** | Existence claim where exhibiting a witness is tractable |
| **Extremal / pigeonhole** | Finite + counting argument available |
| **Case analysis** | Hypothesis naturally splits into finite exhaustive cases |

If two strategies look viable, pick the shorter one. If the "obvious" strategy is contradiction but a direct proof exists, prefer direct — contradictions are harder to audit.

### 3. Build the proof step-by-step

Each step must have **one** explicit justification, phrased as one of:

- "by assumption [which one]"
- "by Lemma / Theorem [reference]"
- "by definition of [term]"
- "by [previous step number]"
- "by arithmetic / algebra" (only for trivial manipulations; otherwise cite a rule)
- "by induction hypothesis"

Rules:

- **Introduce variables before using them**: "Let x ∈ X be arbitrary" / "Fix ε > 0" / "Suppose there exists such n". Quantifier scoping errors are the #1 cause of fatal critiques.
- **Handle edge cases up front** — state them and dispatch in ≤1 line each: n = 0, empty set, k = 1, degenerate configurations.
- **Never use the conclusion in a step** (circular reasoning). If tempted, you've confused a lemma with the theorem itself.
- **Keep each step small** — if a step would need its own sub-argument to justify, promote that sub-argument to a **Lemma** and cite it.
- For induction: explicitly state the induction hypothesis, the base case, and the inductive step as three separate blocks. Base case first, hypothesis second, step third — never intermix.
- For case analysis: number the cases, confirm exhaustivity in one line ("cases 1–3 exhaust the possibilities because …"), and handle each case as its own mini-proof.

### 4. Self-audit before handoff

Before emitting the draft, read through it once with each lens:

- **Variable scope**: every symbol is introduced with a quantifier or a "let" before first use.
- **Circularity**: no step cites the conclusion or a not-yet-proved claim.
- **Edge cases**: every special case mentioned in step 3 is dispatched.
- **Final line**: the last sentence literally states the conclusion of the theorem (not an intermediate result). If it doesn't, your proof proves something else — stop and fix before handoff.
- **Justifications**: every step has one from the list in step 3. "Clearly", "obviously", "it follows that" without a citation are critique bait.

This is a self-critique pass, not a replacement for `proof-critique`. Catches 60-70% of mistakes cheaply so the user's critique cycle starts from a cleaner draft.

### 5. Output in LaTeX

Use standard theorem environments:

```latex
\begin{theorem}[Name of theorem, if any]
\label{thm:{slug}}
{precise statement}
\end{theorem}

\begin{proof}
{proof body with \textbf{Case 1}, \textit{Base case}, \textit{Inductive step}, etc. as
inline emphasis — do not nest environments unless the sub-claim is a promoted Lemma.}
\end{proof}
```

Promoted sub-arguments get their own `\begin{lemma}…\end{lemma}` block above the main theorem, with its own proof environment.

### 6. Save the artifact

- If a `paper/proofs/` directory exists (camera-ready project): save to `paper/proofs/{name}.tex` — one file per theorem or tightly-coupled bundle.
- Otherwise: save to `outputs/{topic}/proofs/{name}.tex`.
- File should be `\input`-able from the main paper (no `\documentclass`, no `\begin{document}`).

**Inputs**: Theorem / proposition statement (natural language or LaTeX), premises, available lemmas & definitions
**Outputs**: `paper/proofs/{name}.tex` or `outputs/{topic}/proofs/{name}.tex`
**Token**: ~3-12K (simple propositions: 3-5K; multi-lemma theorems: 8-12K)
**Composition**:
- Draft ready → suggest `proof-critique` to audit (catches the 30-40% the self-audit missed)
- Critique finds fixable issues → `proof-fix`
- Proof validated → `proof-formalize` to polish the LaTeX to publication form
- Proof intended for mechanical check → `proof-verify` (Lean / Coq / Isabelle port)
- Theorem statement itself needs decomposition first → `theory-decompose` before this skill
- Theorem is surprising / non-obvious → `theory-counterexample` to stress-test before committing to a proof

## Common pitfalls

- **Proving a stronger statement by accident** — the writer slips in an implicit premise ("assume f is continuous") not present in the original. Always re-read the exact statement from step 1 before writing the final line.
- **Jumping to contradiction reflexively** — contradiction is seductive but hard to audit. If a direct proof is available, use it.
- **Forgetting non-trivial base cases** — induction on n ≥ 1 is not the same as n ≥ 0. Base case at the wrong index silently omits a case.
- **Re-using a variable name** — using `n` as both the outer quantifier and the inductive index inside a nested claim. Rename nested bound variables.
- **Unstated uniform bounds** — "there exists N such that for all n ≥ N, …" — is N uniform across ε or does it depend on ε? Be explicit.
- **Citing a lemma you haven't proved** — promoted lemmas must either be proved inline (in their own proof environment) or cite a specific external reference with a page/section number. "By a standard result" is not a proof.
- **Missing the "only if" direction of an iff** — equivalences need both halves. If you only proved P ⇒ Q, say so and flag Q ⇒ P as remaining; do not declare the iff established.
- **Case analysis that isn't exhaustive** — "Case 1: x > 0. Case 2: x < 0." omits x = 0. Always state exhaustivity explicitly.
- **Reading the theorem in a forgiving way** — if the statement says "for all sufficiently large n" ask the user to commit to a concrete n₀ before writing. Vague "sufficiently" clauses are where proofs silently break.
- **LaTeX-level issues delaying critique** — unbalanced `\begin{proof}`/`\end{proof}`, stray `$` signs, or undefined command refs make `proof-critique` trip on syntax instead of logic. Compile locally (or at least syntax-check) before saving.
