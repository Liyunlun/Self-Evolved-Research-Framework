# Synthetic fixture — `mechanism_attribution`

Everything below is invented. No real paper is referenced.

## Excerpt from a hypothetical method section

> We introduce QFlow, a policy update that blends deterministic and stochastic gradients
> through a learned mixing coefficient. The key insight is that the stochastic branch
> induces *active exploration*: the policy deliberately perturbs actions along directions
> of high uncertainty, leading to faster discovery of high-reward regions.

## Excerpt from the experiments section of the same hypothetical paper

> We evaluate on six continuous-control benchmarks: Hopper-v4, Walker2d-v4, HalfCheetah-v4,
> Ant-v4, Humanoid-v4, and Humanoid-Standup-v4. QFlow achieves SOTA on 5 of 6.
> We do not report results on sparse-reward or hard-exploration benchmarks; all chosen
> environments provide dense per-step rewards throughout training.

## What a taste-calibrated reviewer should notice

The paper's headline *mechanism* is exploration. The reported *evidence* comes only from
dense-reward benchmarks, where an exploration-free policy already reaches near-optimal
performance. Any improvement on these benchmarks is compatible with better exploitation,
optimization, or variance reduction — none of which are the claimed mechanism.

## Expected finding

Probe: `mechanism_attribution`.
Severity: `major` (this is the headline claim).
Resolution: add at least one sparse-reward or hard-exploration benchmark (maze-like or
pixel-based sparse-goal), OR an ablation that removes the stochastic branch while keeping
the rest of QFlow constant, and show the claimed exploration advantage survives.
