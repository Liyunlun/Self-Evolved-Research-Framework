# Synthetic fixture — `decorative_theorem`

Everything below is invented.

## Excerpt from the method section

> OrthoNet is a practical neural architecture that enforces orthogonality in hidden
> representations via a regularizer R(h). At inference time, h is computed by a standard
> forward pass through an MLP; OrthoNet does not materialize, compute, or access the
> theoretical optimum defined in Theorem 1.

## Theorem 1

> *Theorem 1.* Let H be a separable Hilbert space. There exists a function f* : X → H such
> that for every x, f*(x) lies in the orthogonal complement of span({f(y) : y ≠ x}).
>
> *Proof.* Apply the Gram-Schmidt process in H. QED.

## Excerpt from the experimental section

> Table 2 shows OrthoNet outperforms baselines by 2-4% on image classification
> benchmarks. We attribute this to the orthogonality property established in Theorem 1.

## What a taste-calibrated reviewer should notice

Theorem 1 establishes *existence* of a function f* with a desirable property. OrthoNet
does not compute f*, does not approximate it, and the paper's regularizer R(h) is not
shown to drive h toward f*. There is no theoretical or empirical link between Theorem 1's
conclusion and the 2-4% improvement on Table 2. Theorem 1 is decorative: it sounds
related to the method but does nothing to explain why the method works.

## Expected finding

Probe: `decorative_theorem`.
Severity: `major` at oral/best_paper (theory contribution overstated); `minor` at
poster if clearly labeled as motivational.
Resolution: either (i) prove a theorem whose conclusion implies a concrete property of
OrthoNet's regularizer R — e.g., a bound on the distance between OrthoNet's h and f* —
and connect that bound to the experimental metric; OR (ii) move Theorem 1 to a
"Background" section labeled as classical, and remove it from the contribution list.
