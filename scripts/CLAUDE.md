# Utility Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `citation_fetch.py` | Fetch BibTeX from DBLP/CrossRef | `python citation_fetch.py "Title" [--authors "Name"] [--batch file.txt]` |
| `notify.py` | Fail-open webhook notifications | `python notify.py "Message" [--level info\|warning\|error\|success]` |
| `skill_analyzer.py` | Parse session logs for usage stats | `python skill_analyzer.py` |
| `pack.sh` | Pack framework as clean template for new projects | `bash scripts/pack.sh [VERSION]` |
| `install-skills.sh` | Install bundled Claude Code skills into `.claude/skills` | `bash scripts/install-skills.sh [--link] [--force] [--user] [--only PATTERNS] [--exclude PATTERNS] [--code-track claude\|codex]` |

## Dependencies

`pip install -r requirements.txt` — mainly PyYAML. No heavy ML dependencies.

## Environment Variables

- `SER_NOTIFY_WEBHOOK_URL` — webhook URL for notify.py (optional, fail-open)
