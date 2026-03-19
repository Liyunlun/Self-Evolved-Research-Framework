# Micro-Skill: project.integrate

> Merge an existing research project into the SER framework from an unpacked ser-vX.Y distribution.

## Trigger

- User says "integrate SER", "merge into SER framework", "set up SER for this project"
- User has an unpacked `ser-vX.Y/` directory alongside their existing research project

## Prerequisites

- An unpacked SER distribution (e.g., `ser-vX.Y/`) in or near the project root
- An existing research project with code, papers, or data already present

## Process

### Phase 1: Inventory (read-only)

1. **Scan SER pack**: Read `ser-vX.Y/MANIFEST.yaml` to identify all framework files
2. **Scan existing project**: Identify the project's key assets:
   - Source code directories (Python, LaTeX, configs)
   - Paper/document files (.tex, .pdf, .md)
   - Existing `.claude/` configuration (settings.local.json, skills/, hooks/)
   - Existing `CLAUDE.md` with project instructions
   - Git state (branch, uncommitted changes)
3. **Detect conflicts**: Check if any SER directory names already exist in project root:
   - `skills/`, `memory/`, `logs/`, `resources/papers/`, `background/`, `methodology/`, `outputs/`, `resources/`, `scripts/`
   - `.claude/hooks/`, `config.yaml`, `CLAUDE.md`
4. **Report inventory** to user:
   ```
   === SER Integration Inventory ===
   SER version: vX.Y
   Project: {name from existing CLAUDE.md or git remote}

   Existing assets found:
   - {list of code dirs, paper files, configs}

   Conflicts: {none | list of conflicting paths}

   Will copy: {N} framework dirs, {M} config files
   Will merge: CLAUDE.md, .claude/settings.local.json
   Will create: config.yaml, memory/MEMORY.md, logs/digest/SUMMARY.md
   Will preserve: {all existing project files stay in place}
   ```

### Phase 2: Copy Framework (6 sub-steps)

Execute these in order. Each is idempotent (safe to re-run).

#### 2.1: Copy SER directories

```bash
# From project root:
cp -r ser-vX.Y/skills .          # 9 micro-skill specs
cp -r ser-vX.Y/memory .          # Memory system (templates)
cp -r ser-vX.Y/scripts .         # Utility scripts
# Create empty SER directories (only if they don't exist):
for dir in logs/digest background methodology \
           resources/papers; do
  mkdir -p "$dir"
  [ ! -f "$dir/.gitkeep" ] && touch "$dir/.gitkeep"
done
```

**Rule**: Never overwrite existing directories that contain user data. If `resources/papers/` already has files, only add `.gitkeep` if missing.

#### 2.2: Install intent router hook

```bash
mkdir -p .claude/hooks
cp ser-vX.Y/.claude/hooks/ser-intent-router.sh .claude/hooks/
chmod +x .claude/hooks/ser-intent-router.sh
```

#### 2.3: Merge .claude/settings.local.json

Read both the existing settings and SER's settings. Produce a merged version:

- **Permissions**: Union of both permission lists. De-duplicate. Prefer broader patterns (e.g., `Bash(pdflatex:*)` over `Bash(pdflatex -interaction=nonstopmode main.tex)`)
- **Hooks**: Add the `UserPromptSubmit` hook for `ser-intent-router.sh`. If hooks already exist, append (don't replace)

#### 2.4: Merge CLAUDE.md

Create a two-part document:

```markdown
# SER vX.Y — Behavioral Protocol
{entire contents of ser-vX.Y/CLAUDE.md}

# {Project Name} — Domain Knowledge
{entire contents of existing CLAUDE.md}
```

**Rules**:
- SER protocol section comes FIRST (it must be read first for intent routing)
- Remove duplicate headings if the existing CLAUDE.md also has `# CLAUDE.md` as H1
- Update the "Project Architecture" tree in SER section to reflect actual project structure

#### 2.5: Create config.yaml

Fill the template from `ser-vX.Y/config.yaml` with project-specific values. Ask user for:
- Project name and domain/keywords
- Timeline (start date, duration, milestones)
- Current status (what's done, what's next)

If the existing CLAUDE.md contains this information, extract it automatically.

#### 2.6: Initialize memory

**MEMORY.md**: Populate Active Context with:
- Current project focus (from CLAUDE.md or user input)
- Key asset paths (code dirs, paper files)
- Project status (what's done, what's in progress)

**Seed episodes**: Create 1-3 episodes in `memory/episodes/`:
- `YYYY-MM-DD-001.md`: Project overview (assets, architecture, goals)
- `YYYY-MM-DD-002.md`: Key decisions made before SER integration (if any)


**SUMMARY.md**: Create empty session log index:
```markdown
# Session Log Summary

| Date | Type | Summary | Phase | Token Est |
|------|------|---------|-------|-----------|
```

### Phase 3: Verify

1. **Hook test**: `echo '{"user_prompt":"test"}' | bash .claude/hooks/ser-intent-router.sh` — should exit 0
2. **Structure check**: Verify all 9 micro-skill files exist in `skills/micro/`
3. **Memory check**: Verify `memory/MEMORY.md` has Active Context filled
4. **Build check**: If project has a build step (LaTeX compile, test suite), run it to confirm nothing broke
5. **Git check**: `git status` to show all new/modified files before committing

### Phase 4: Commit

Stage and commit with message format:
```
Integrate SER vX.Y framework for structured research workflow

- {N} micro-skill specs (session, paper, theory, proof, writing, planning, meta, research, memory)
- Intent router hook for auto-detecting research intent
- Memory system with Options Framework + TD-NL optimization
- Project config with timeline and milestones
- Merged CLAUDE.md (SER protocol + project domain knowledge)
- Seeded memory with {M} initial episodes
```

## Key Principles

1. **Never move existing files**. Project code, papers, and data stay exactly where they are. SER adds structure around them.
2. **Never overwrite user data**. If a directory/file exists with user content, merge or append — never replace.
3. **Permissions are additive**. Merge settings, never reduce existing permissions.
4. **CLAUDE.md is merged, not replaced**. Both SER protocol and project knowledge must be present.
5. **Memory seeds from existing state**. Don't start cold — extract what's known from CLAUDE.md, git log, and directory structure.

## Output

- Integrated project with SER framework directories
- Merged CLAUDE.md + settings.local.json
- Populated config.yaml + memory/MEMORY.md
- Ready for first `session.open` in next conversation

## Token Cost

~3-5K (mostly file copying + config generation)
