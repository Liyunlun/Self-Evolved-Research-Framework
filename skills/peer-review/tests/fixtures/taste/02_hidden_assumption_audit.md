# Synthetic fixture — `hidden_assumption_audit`

Everything below is invented.

## Excerpt from a hypothetical derivation

> To compute the policy entropy, we use the decomposition
>
>   H(π) = H(π | z) + I(π ; z).
>
> Applying H(π) ≥ H(π | z), we optimize the lower bound
>
>   L(θ) = E_z [ Σ_i log σ_i(z) ].
>
> Maximizing L(θ) over θ therefore promotes a high-entropy, diverse policy.

## What a taste-calibrated reviewer should notice

The inequality H(π) ≥ H(π|z) silently drops I(π;z) — the *mutual-information* term.
If the paper's headline claim is that its method produces a *multi-modal* or *diverse*
policy, that diversity comes from variation in z, which is exactly what I(π;z) captures.
Maximizing only H(π|z) is satisfied by *per-z Gaussian spread* (large σ_i), which is
unimodal — the opposite of what the paper claims to deliver.

## Expected finding

Probe: `hidden_assumption_audit`.
Severity: `major` (the dropped term is load-bearing for the multi-modality claim).
Resolution: either (i) bound I(π;z) from below and include it in the objective, or (ii)
provide an empirical verification that I(π;z) remains bounded away from zero at
convergence (e.g., measure action distribution conditional on z vs unconditional).
