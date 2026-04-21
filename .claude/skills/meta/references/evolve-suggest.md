## evolve.suggest

**Trigger**: Runs at `session.close`, after memory operations complete (G1 Aggregation).

### Process
**Phase 1 — Read observations**:
Read all observation entries from `logs/observations/` for this session.

**Phase 2 — Per-skill aggregation**:
For each skill that was observed:
- Count `better`, `as_expected`, `worse` outcomes
- Compute `net_delta` = sum of all delta values
- Synthesize a pattern description (e.g., "writing.review consistently underperforms on methodology sections")

**Phase 3 — Per-skill value update**:
Apply learning rate based on confidence level:
| Confidence | Learning Rate | When |
|------------|---------------|------|
| High | 1.0 | 10+ observations, consistent direction |
| Medium | 0.5 | 5-9 observations, mostly consistent |
| Low | 0.25 | <5 observations, or mixed signals |

Update the skill's internal value estimate.

**Phase 4 — System value recomputation**:
Recompute the overall system performance value from all skill values weighted by usage frequency.

**Phase 5 — Spec edit proposal**:
Generate a concrete edit proposal if:
- `|net_delta| >= 3` for any skill, OR
- Same direction (all better or all worse) for 3+ consecutive sessions

The proposal includes: target skill, specific text to change, rationale, and expected impact.

**Phase 6 — Cleanup**:
- Move processed observation entries to archive
- Write cycle summary to `logs/evolution/`

### Suggested Next
- Proposal generated: present to user for approval, then `evolve.apply` on approval
