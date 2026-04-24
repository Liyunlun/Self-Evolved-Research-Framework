# Synthetic fixture — `terminology_audit`

Everything below is invented.

## Excerpt from the method section

> We propose CausalAttn, a *causality-aware* attention mechanism. Given token embeddings
> p_1, …, p_n, we fix a pre-specified graph G (full of zeros and ones) and learn a
> weighting matrix W. The attention re-weighting matrix is
>
>   A = W G Wᵀ.
>
> We interpret A as encoding causal influence between tokens, with A_{ij} quantifying
> the causal effect of token j on token i.

## Excerpt from the appendix

> We choose G to be diagonal with entries in {0, 1}. The learned W has no structural
> constraint and is trained jointly with the base model.

## What a taste-calibrated reviewer should notice

If G is diagonal, then A = W G Wᵀ = Σ_k G_{kk} w_k w_kᵀ, which is a sum of rank-1 outer
products — i.e., *symmetric*. In particular A_{ij} = A_{ji} for every i, j. Causal
effect is by definition asymmetric (j causes i does not imply i causes j), so a symmetric
matrix cannot represent causal influence. The operation here is standard importance
re-weighting: tokens with larger |w_k| get higher weight, and the paper's reported
improvements are fully compatible with importance re-weighting being the operative
effect.

## Expected finding

Probe: `terminology_audit`.
Severity: `major` ("causal" appears in the title and contribution list).
Resolution: either (i) replace G with an asymmetric, learned, or causally-motivated
matrix and demonstrate the reported improvement depends on that asymmetry, OR
(ii) rename the mechanism to reflect its actual operation (e.g.,
"importance-weighted attention" or "relevance-gated attention"). Renaming does not
diminish the empirical contribution.
