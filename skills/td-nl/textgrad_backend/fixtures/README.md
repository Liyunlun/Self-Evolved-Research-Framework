# TextGrad backend regression fixtures

Snapshots of expected `run_backward` output for known inputs. Refreshed
intentionally when the scoring algorithm changes; otherwise, a diff
against these files is a regression signal.

## Files

| File | Source input | Backend | Purpose |
|------|--------------|---------|---------|
| `live_feedback_log_2026-04-20.json` | `skills/td-nl/feedback-log.md` as of 2026-04-20 (session `s8`, 6 v3 entries) | shim (offline) | First live-data regression — locks V^L bump, per-skill td errors, and single-proposal target |

## Refreshing

Regenerate a fixture by running:

```bash
python3 scripts/evolve_textgrad.py --dry-run --json > \
  skills/td-nl/textgrad_backend/fixtures/<name>.json
```

Then `git diff` to confirm the change is intentional.
