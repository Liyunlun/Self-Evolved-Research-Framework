# Synthetic fixture — `efficiency_vs_claim`

Everything below is invented.

## Excerpt from the method section

> AggrGrad maintains K = 8 auxiliary policies per update. Each auxiliary policy runs J = 4
> inner-loop gradient steps. The base policy is then updated by backpropagating through
> the inner loops via a chain-rule Jacobian product. An additional trust-region solve is
> applied to the final aggregated gradient.

## Excerpt from the "computational cost" appendix

> Table A7 reports wall-clock time for AggrGrad and baselines on CartPole-v1 (state dim
> 4) and Acrobot-v1 (state dim 6). AggrGrad is 1.8× slower than PPO on CartPole-v1 and
> 2.1× slower on Acrobot-v1. Wall-clock on larger benchmarks is omitted to save space.

## Excerpt from the main-claim section

> AggrGrad is especially effective on high-dimensional tasks such as Humanoid-v4 (state
> dim 376) and Ant-v4 (state dim 111), where its sample efficiency advantage is most
> pronounced.

## What a taste-calibrated reviewer should notice

The paper explicitly claims the method shines on high-dimensional tasks, but the only
wall-clock numbers come from the lowest-dimensional ones. A back-of-envelope account
(K=8 auxiliary policies × J=4 inner steps × per-batch cost, plus a trust-region solve)
scales roughly with state-dim × K × J. The cost could dominate the sample-efficiency
gain on Humanoid-v4, but the paper does not let the reader verify this.

## Expected finding

Probe: `efficiency_vs_claim`.
Severity: `major`.
Resolution: add Humanoid-v4 and Ant-v4 wall-clock rows to Table A7 with identical
hardware and (ideally) a cost-per-sample breakdown split into "forward pass", "inner
loop", "trust-region solve".
