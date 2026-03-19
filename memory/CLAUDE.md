# Memory System

Persistent memory across sessions using a three-tier file system.

## Structure

```
MEMORY.md        -> Always-loaded index (200-line hard limit)
episodes/        -> Episodic memories (recent, max 20 files, 7-day retention)
topics/          -> Consolidated topics (max 50 files, 90-day retention)
procedures/      -> Procedures + permanent decisions (max 100 files)
```

## Tier Capacity Limits

| Tier | Max Files | Max Lines/File | Retention |
|------|-----------|----------------|-----------|
| episodes | 20 | 200 | 7 days |
| topics | 50 | 500 | 90 days |
| procedures | 100 | unlimited | permanent |

## Memory Type Emergence

Types emerge naturally from usage:
- **Episodes** -> created by `memory.write` after any insight-producing skill
- **Topics** -> emerge via `memory.consolidate` when 3+ episodes cluster
- **Procedures** -> emerge when 2+ episodes describe same multi-step process

See `skills/micro/memory.md` for the full write/retrieve/consolidate/forget specs.
