# Scripts - Helper Scripts

This directory contains Python scripts that support the SER framework, mainly to **reduce token usage**.

## Script List

### `skill_analyzer.py` - Skill Usage Statistics Analyzer

**Purpose**: Incrementally scan Skill invocation logs and generate a structured statistics report

**Usage**:
```bash
python scripts/skill_analyzer.py
```

**Output**:
- `logs/analysis/skills_stats.json` - statistics report (read by `/skill-evolve`)
- `logs/analysis/last_processed.txt` - last processed position (incremental marker)

**Token Savings**:
- Traditional approach: `/skill-evolve` needs 20-30K tokens to read and analyze logs
- Script-based approach: only 3-5K tokens to read the JSON report
- **Roughly 80% savings**

---

## Install Dependencies

```bash
pip install -r scripts/requirements.txt
```

---

## Integrating with /skill-evolve

`/skill-evolve` execution flow:

```
1. [Bash] Run `python scripts/skill_analyzer.py`
    ↓
2. [Read] Read `logs/analysis/skills_stats.json` (cost <1K tokens)
    ↓
3. [Claude] Present the report + user interaction (cost 8-15K tokens)
    ↓
4. [Claude] Generate improvement actions + update files (cost 5-10K tokens)
```

**Total cost**: 13-25K tokens (about 25-40% less than the original 20-30K)

---

## Data Model

### Skill ID Mapping

Each Skill has a unique ID:

```python
SKILL_IDS = {
    # Meta layer
    "research-init": "meta_001",
    "background-builder": "meta_002",
    ...

    # Object layer
    "problem-decompose": "research_001",
    "proof-refine": "research_004",
    ...
}
```

### Log Format Requirements

Each Skill log file should include the following fields (used for analytics):

```yaml
# logs/research-skills/{skill_name}/YYYY-MM-DD_NNN.yaml

metadata:
  skill_id: "research_004"  # unique identifier
  timestamp: "2026-02-15 14:30"

token_consumption:
  actual: 25000

user_satisfaction: 5  # 1-5

variant_used: "deep"  # if a variant was used
variant_winner: "deep"  # if that variant won
```

---

## Future Extensions

- [ ] Support extracting Skill calls from Claude conversation logs (via pattern matching)
- [ ] Time-series analysis (token usage trends, satisfaction changes)
- [ ] Automatically generate variant suggestions (based on failure patterns)

---

*Version: 1.0*
