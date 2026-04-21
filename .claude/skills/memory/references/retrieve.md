# memory.retrieve

**Trigger**: Before any knowledge-dependent skill, at `session.open`, or when user asks about prior work/decisions.

## Process

1. Determine query from the calling context (skill name, user question, topic keywords)
2. Read `memory/MEMORY.md` to get the full index
3. Score each entry using weights from `config.yaml` section `memory.retrieve.weights`:
   | Factor | Weight | Description |
   |--------|--------|-------------|
   | `tag_overlap` | 0.4 | How many tags match the query context |
   | `keyword_match` | 0.3 | Keyword similarity between query and entry |
   | `recency` | 0.15 | How recent the entry is |
   | `importance` | 0.15 | The stored importance score |
4. Select top candidates by composite score
5. Read full files for the top 3 candidates
6. Surface retrieved content into the active context for the calling skill

## Suggested Next

- Provides context for whatever skill triggered the retrieval
