## index

**Trigger**: User asks about their reading list, wants an overview of papers read, or asks "what have I read about X?".

### Process
1. Read all files in `resources/papers/` directory
2. Parse YAML frontmatter from each paper file (status, tags, relevance)
3. Output an organized index:
   - Group by topic/tag clusters
   - Within each group, sort by relevance score (descending)
   - Show status indicators: read / skimmed / cited / unread
   - Include one-line summary per paper
4. Identify and report gaps:
   - Topics with few papers
   - Highly relevant papers only skimmed
   - Missing foundational references suggested by citation patterns

### Suggested Next
- For unread or skimmed papers that seem important -> `paper.read`
