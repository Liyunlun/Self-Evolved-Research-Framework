# SER v5.0 → dev 变更详解

> 本文档详细对比 SER v5.0（原版）与 SER dev（当前开发版）的所有差异。
> 基线 commit: `9f77010`（v5.0 最后一个版本）
> 当前 commit: `761d6a7`（dev 最新版本）

---

## 一、总览

| 维度 | v5.0 | dev | 变化 |
|------|------|-----|------|
| Micro-skill 数量 | 41 | 50 | **+9 新技能** |
| Spec 文件数 | 13 | 16（含 3 个 experiment 源文件） | +3 |
| Intent Router 条目 | 25 | 47 | **+22** |
| CLAUDE.md 章节 | 8 | 10 | +2（Dual Review, Memory Parameters） |
| config.template.yaml 行数 | 75 | 130 | +55 |
| setup.sh 步骤 | 6 | 10 | +4 |
| setup.sh 行数 | 166 | 362 | +196 |
| 数据文件变化 | — | -7 删除预置文件 | setup.sh 动态生成 |

---

## 二、新增技能（+9）

| 新技能 | Spec 文件 | 功能 | 来源 |
|--------|-----------|------|------|
| `idea.refine` | idea.md | 将粗略想法精炼为结构化研究提案 | ARIS fusion |
| `lit.search` | paper.md | 文献检索（arXiv/DBLP 自动搜索） | ARIS fusion |
| `math.dse` | experiment.base.md | 设计空间探索（参数扫描） | ARIS fusion |
| `paper.compile` | writing.md | LaTeX 编译为 PDF | ARIS fusion |
| `paper.figure` | writing.md | 从数据生成论文图表 | ARIS fusion |
| `paper.illustrate` | visual.md | 论文架构/流程示意图（TikZ/SVG） | ARIS fusion |
| `pixel.create` | visual.md | 像素画 / 装饰性 SVG | ARIS fusion |
| `proof.write` | proof.md | 从零写证明（区别于 formalize 的格式化） | ARIS fusion |
| `experiment.plan` | experiment.base.md | 实验设计与规划 | ARIS fusion |

---

## 三、增强技能（v5.0 已有，dev 中改进）

| 技能 | 变更内容 |
|------|----------|
| `idea.discover` | 候选数量从硬编码 8-12 改为 `config.yaml § workflows.idea_discovery.candidate_count`，可被 TD-NL 优化 |
| `idea.verify` | 新增 Agent subagent 跨模型验证流程，替代纯内部评估 |
| `writing.outline` | 从 writing.draft 的子流程独立为完整技能，新增大纲结构模板 |
| `writing.draft` | 新增 dual review 集成（config.yaml 控制） |
| `checklist.create` | 支持 `category` 参数（paper-audit, paper-writing, research-pipeline 等 7 类） |
| `checklist.status` | 从 planning.md 迁移到 checklist.md，增加 per-category 完成度统计 |
| `memory.write` | 增加 `importance_threshold` 参数化，参数存于 config.yaml |
| `memory.retrieve` | 增加权重参数化（tag_overlap, keyword_match, recency, importance） |
| `memory.consolidate` | 增加 `episode_threshold`, `cluster_min`, `memory_md_pressure_line` 参数 |
| `memory.forget` | 增加 `stale_episode_days`, `stale_topic_days`, `protected_types` 参数 |
| `session.open` | 新增首次 session 容错（无历史日志时的 fallback） |
| `session.close` | 新增明确要求记录所有用户文本输入 |
| `theory.formalize` | 输出路径标准化：`methodology/{topic}.md`（工作）/ `outputs/{topic}/theory/`（交付），定义了 `{topic}` 占位符 |
| `proof.write` | 输出路径添加决策标准：检查 Checklist.md 判断是论文绑定还是探索性 |
| `experiment.analyze` | 保留在 planning.md（权威定义），experiment.base.md 中改为 redirect |

---

## 四、新增 Spec 文件

| 文件 | 内容 |
|------|------|
| `skills/micro/visual.md` | 全新文件，包含 `pixel.create` + `paper.illustrate` + Composition Rules + TD-NL Integration |
| `skills/micro/experiment.base.md` | 从原 `experiment.md` 拆分出的公共部分 + `experiment.plan` + `math.dse` |
| `skills/micro/experiment.local.md` | 本地直接 SSH 模式的 `experiment.run` + `experiment.monitor` |
| `skills/micro/experiment.ms.md` | MetaScheduler 模式的实验执行协议（`mb task manager` 交互） |

### Experiment 二进制安装机制

v5.0 只有一个 `experiment.md`，所有模式代码混在一起。dev 拆分为：

```
experiment.base.md   ← 公共技能（plan, analyze, dse）
experiment.local.md  ← 本地模式（SSH + screen）
experiment.ms.md     ← MetaScheduler 模式（mb task）
```

安装时 setup.sh 组装：`base + local` 或 `base + ms` → `experiment.md`，然后删除源文件。用户看到的永远只是一个 `experiment.md`。

---

## 五、CLAUDE.md 变更

### 新增章节

| 章节 | 内容 |
|------|------|
| **Dual Review** | 跨模型双审机制：使用 MCP 工具调用外部模型（GPT-5.4），在 `writing.review`, `idea.verify`, `proof.critique`, `experiment.analyze` 触发 |
| **Memory Parameters** | 记忆系统参数化说明：所有阈值引用 `config.yaml § memory`，可被 TD-NL 优化 |

### Intent Router 变更

| 指标 | v5.0 | dev |
|------|------|-----|
| 总条目 | 25 | 47 |
| 覆盖技能 | ~30/41 | 47/50（剩余 3 个为内部技能：memory.*, evolve.*） |
| 路由原则 | 无明确优先级 | Top-to-bottom, specific-before-generic |
| 中文触发词 | 2 条 | 12 条（找论文、写证明、精炼想法、画像素图、论文插图等） |

### Project Architecture 变更

v5.0 架构图 14 行，dev 扩展到 30 行，新增：
- `paper/theory/` — 定理声明
- `paper/figures/scripts/` — 图表生成脚本
- `methodology/approach.md` — 研究方向桩
- `methodology/ideas/` — 想法发现产物
- `outputs/visuals/` — SVG/pixel art
- `logs/progress/` — 进度捕获日志
- `logs/experiments/` — 实验日志
- `skills/td-nl/skill-values/_template.md` — Q^L 模板

### Token Budget 变更

新增 3 项：

| 操作 | Token 预算 |
|------|-----------|
| Checklist operations | 1-3K |
| Visual creation (pixel/illustrate) | 2-8K |
| Literature search | 2-5K |

---

## 六、config.template.yaml 变更

### 新增配置段

```yaml
# v5.0 不存在，dev 新增：

memory:                              # 记忆参数化（TD-NL 可优化）
  write.importance_threshold: 5
  retrieve.weights: {tag: 0.4, keyword: 0.3, recency: 0.15, importance: 0.15}
  consolidate.episode_threshold: 15
  forget.stale_episode_days: 7

workflows:                           # 工作流参数化
  review_loop.max_rounds: 3
  idea_discovery.candidate_count: 5
  paper_writing.auto_improve_rounds: 2

dual_review:                         # 跨模型双审
  enabled: true
  tool: "mcp__codex__codex"
  model: "gpt-5.4"
  when: [writing.review, idea.verify, proof.critique, experiment.analyze]

# metascheduler:                     # MetaScheduler 集成（安装时选配）
#   bot_name: "manager"
#   default_conda_env: "research"
```

### 修改项

| 配置项 | v5.0 | dev |
|--------|------|-----|
| `skill_architecture` | `"micro-v5.0"` | `"micro-dev"` |
| `autonomy` | 存在 | 保持不变 |
| MetaScheduler | 不存在 | 可选注释块 |

---

## 七、setup.sh 变更

### 步骤对比

| # | v5.0 | dev |
|---|------|-----|
| 1 | Config（复制模板） | **Experiment 模式选择**（本地/MetaScheduler） |
| 2 | Required directories | **Experiment 二进制组装**（base+选项 → experiment.md → 删除源文件） |
| 3 | .gitkeep | Config（+ MetaScheduler 配置写入） |
| 4 | Memory index | Required directories（+`paper/theory`, -`memory/td-nl`, -`papers`） |
| 5 | Session log summary | .gitkeep（复用 dirs 数组，消除重复） |
| 6 | Checklist system | **TD-NL 基础设施**（value-function.md, feedback-log.md, _template.md） |
| 7 | — | Memory index（保留模式） |
| 8 | — | Session log summary（保留模式） |
| 9 | — | **Methodology 桩**（approach.md） |
| 10 | — | Checklist system（**7 分类头**） |

### 关键差异

1. **v5.0 无 experiment 模式选择**：所有用户共享同一个 experiment.md
2. **v5.0 无 TD-NL 文件创建**：value-function.md 等需要手动创建
3. **v5.0 无 approach.md**：idea.discover 等技能找不到方法论上下文
4. **v5.0 L1 checklist 无分类头**：只有注释行
5. **v5.0 目录包含 `memory/td-nl`**（错误路径）和 `papers`（与 `resources/papers` 重复）
6. **v5.0 无幂等保护**：`setup.sh` 可能覆盖已有文件

### 幂等性改进

| 场景 | v5.0 行为 | dev 行为 |
|------|-----------|----------|
| 第二次运行 | 可能覆盖 config.yaml | `[=] 已存在, 跳过` |
| --update 模式 | 不存在 | 刷新框架文件，保留项目数据 |
| experiment.md 已存在 | 重新组装 | `[=] 已组装, 跳过` |
| TD-NL 文件已存在 | 不创建 | `[=] 已存在, 跳过` |

---

## 八、文件变更统计

```
27 files changed, 1104 insertions(+), 493 deletions(-)
```

### 新增文件（+4）
- `skills/micro/visual.md` — 视觉创作技能
- `skills/micro/experiment.base.md` — 实验公共部分
- `skills/micro/experiment.local.md` — 本地实验模式
- `skills/micro/experiment.ms.md` — MetaScheduler 实验模式

### 删除文件（-7，改为 setup.sh 动态生成）
- `Checklist.md` — setup.sh 用项目名动态创建
- `checklists/CLAUDE.md` — setup.sh 创建
- `checklists/short-term.md` — setup.sh 创建（含 7 分类头）
- `checklists/mid-term.md` — 同上
- `checklists/long-term.md` — 同上
- `skills/td-nl/value-function.md` — setup.sh 创建（含 14 类 50 技能）
- `skills/td-nl/feedback-log.md` — setup.sh 创建（含 3 个 section）
- `skills/td-nl/skill-values/_template.md` — setup.sh 创建
- `logs/digest/SUMMARY.md` — setup.sh 创建

### 重命名
- `skills/micro/experiment.md` → `skills/micro/experiment.local.md`（原内容成为本地模式专用）

---

## 九、设计理念变化

### v5.0：静态框架
- 所有文件预置在仓库中
- 用户 clone 后直接使用
- 无模式选择
- 技能参数硬编码

### dev：可配置 + 自进化
- **Binary install**：setup.sh 根据用户选择组装最终文件
- **参数化**：记忆阈值、候选数量、审查轮数等可通过 config.yaml 调节
- **TD-NL 可优化**：参数不仅用户可调，框架也能通过使用反馈自动优化
- **Dual Review**：引入外部模型交叉验证，降低单模型偏差
- **MetaScheduler 集成**：支持多节点 GPU 集群实验管理
- **Specific-before-generic routing**：Intent Router 按优先级匹配，专用模式优先于通用
