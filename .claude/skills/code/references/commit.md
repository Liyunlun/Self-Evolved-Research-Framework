# code.commit

**Trigger**: Code reviewed and verified, ready to persist.

## Process

1. **Stage explicitly** — name files, never `git add -A` or `git add .`.
2. **Prefix message** — use convention from `config.yaml git.commit_prefixes`:
   - `feat:` new feature
   - `fix:` bug fix
   - `exp:` experiment code
   - `refactor:` restructuring
   - `docs:` documentation
   - `chore:` maintenance
3. **Never commit**: secrets (.env, credentials), `.claude/`, `logs/`, `memory/episodes/`.
4. **Verify**: run `git status` after commit to confirm clean state.
5. **Clear dirty flag**: `observe.sh` auto-clears `.claude/.ser-dirty` on commit detection.

## Suggested Next
- `experiment.run` (if experiment code) or next task
