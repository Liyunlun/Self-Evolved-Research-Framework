# Synthetic fixture — `benchmark_claim_match`

Everything below is invented.

## Excerpt from the abstract / introduction

> We propose MetaSparse, a reinforcement learning method for *sparse-reward, long-horizon*
> tasks. MetaSparse is designed to handle environments where the reward signal is
> available only at task completion, and where the episode length regularly exceeds
> 10,000 timesteps.

## Excerpt from the experimental section

> Experiments are conducted on nine navigation environments: FourRooms-5x5,
> FourRooms-9x9, PointMaze-1, PointMaze-2, PointMaze-3, AntMaze-u, AntMaze-medium,
> ObjectRetrieval-small, and ObjectRetrieval-medium. State dimensionalities range from 4
> to 27. Episode lengths range from 100 to 1500 timesteps. Rewards are binary at task
> completion.

## What a taste-calibrated reviewer should notice

The paper's claim covers two properties: sparse rewards AND long horizons (≥10,000 steps).
The benchmarks are sparse-reward but top out at 1500-step horizons. The "long-horizon"
part of the claim is never exercised. Additionally, the nine environments are
structurally similar (low-dimensional navigation), so they jointly test one regime, not a
range.

## Expected finding

Probe: `benchmark_claim_match`.
Severity: `major` (the long-horizon half of the headline claim is untested).
Resolution: either (i) add experiments on at least one benchmark with the targeted
horizon (≥10k steps), OR (ii) scope the claim to the horizon range actually tested
("sparse-reward navigation up to ~1500 steps"). Rescoping does not diminish the
contribution and is explicitly preferable to an unsupported overclaim.
