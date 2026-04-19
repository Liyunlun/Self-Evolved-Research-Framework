# Self-Evolved Research (SER) — Dev 分支

> [Self-Evolved Research Framework](https://github.com/Shiien/Self-Evolved-Research-Framework) v5.0 的开发分支。

基于 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 的行为驱动研究协作框架。自然对话即可使用——SER 自动检测意图并路由到对应的微技能。框架通过自然语言 TD 学习不断优化自身技能。

**核心能力**：50 个微技能、层级式 checklist 引擎、TD-NL 自进化、双审机制（跨模型交叉验证）。

## 架构

SER 使用 3 层行为协议：

| 层级 | 范围 | 文件 |
|------|------|------|
| **Layer 0** | 全局默认设置（git 规范、GPU 策略、工具） | `~/.claude/CLAUDE.md` |
| **Layer 1** | SER dev 框架（意图路由、技能、数据契约） | `CLAUDE.md` |
| **Layer 2** | 项目专属配置与记忆 | `config.yaml` + `memory/` |

## 安装

```bash
git clone git@github.com:Liyunlun/Self-Evolved-Research-Framework.git
cd Self-Evolved-Research-Framework
bash scripts/setup.sh
```

安装脚本会创建 `config.yaml`、初始化记忆系统、创建所有必要目录和 TD-NL 基础设施文件。支持 MetaScheduler 模式（用于自动化 agent 工作流）。可安全重复运行（幂等）。

### 安装选项

- **本地模式**（默认）：直接通过 SSH 访问 GPU 节点
- **MetaScheduler 模式**：通过 MetaBot Agent Bus 提交实验到集群

## 微技能（50 个技能，16 个 spec 文件）

| 分类 | Spec 文件 | 技能 |
|------|-----------|------|
| **会话** | `session.md` | `session.open`, `.close` |
| **论文** | `paper.md` | `paper.read`, `.compare`, `.index`, `lit.search` |
| **理论** | `theory.md` | `theory.formalize`, `.decompose`, `.search`, `.counterexample`, `.generalize` |
| **证明** | `proof.md` | `proof.critique`, `.fix`, `.formalize`, `.verify`, `.write` |
| **写作** | `writing.md` | `writing.outline`, `.draft`, `.review`, `.polish`, `paper.figure`, `.compile` |
| **规划** | `planning.md` | `plan.suggest`, `.milestone`, `progress.capture`, `status.report`, `decision.analyze`, `experiment.analyze` |
| **实验** | `experiment.*.md` | `experiment.plan`, `.run`, `.monitor`, `math.dse`（基础 + 本地/MetaScheduler 模式） |
| **记忆** | `memory.md` | `memory.write`, `.retrieve`, `.consolidate`, `.forget` |
| **元技能** | `meta.md` | `evolve.suggest`, `.apply`, `general.research` |
| **想法** | `idea.md` | `idea.discover`, `.verify`, `.refine` |
| **研究** | `research.md` | `research.explore`, `design.converge` |
| **清单** | `checklist.md` | `checklist.create`, `.verify`, `.update`, `.status` |
| **视觉** | `visual.md` | `pixel.create`, `paper.illustrate` |
| **集成** | `integrate.md` | `project.integrate` |

## 意图路由

SER 通过 CLAUDE.md 中的 47 条路由表自动检测用户意图。支持中英文触发：

| 你说的话 | 触发技能 |
|---------|----------|
| "找论文"、"related work" | `lit.search` |
| "prove this"、"写证明" | `proof.write` |
| "refine idea"、"精炼想法" | `idea.refine` |
| "画像素图"、"pixel art" | `pixel.create` |
| "论文插图"、"draw pipeline" | `paper.illustrate` |
| "设计实验"、"plan experiment" | `experiment.plan` |
| "写大纲"、"paper outline" | `writing.outline` |
| "审阅论文"、"review paper" | `writing.review` |
| "project status"、"项目状态" | `status.report` |
| _(更多见 CLAUDE.md § Intent Router)_ | |

路由原则：**自上而下匹配，专用优先于通用**。

## 技能进化（TD-NL）

框架通过自然语言 TD 学习优化自身的微技能 spec：

1. **G2**（内联）：每次技能执行后，追加结果评估到反馈日志
2. **G1**（session.close）：聚合 G2 反馈，更新单技能价值估计，提出 spec 编辑建议
3. **Apply**（用户触发）：编辑技能 spec，支持版本存档和回滚

### TD-NL 基础设施

```
skills/td-nl/
├── value-function.md     # V^L：系统级价值函数（14 类 50 技能）
├── feedback-log.md       # G2 条目 + 待处理提案
├── skill-values/         # 单技能 Q^L（首次触发时创建）
│   └── _template.md      # 新技能价值文件模板
└── history/              # Spec 版本存档（回滚用）
```

## 双审机制（Dual Review）

当 `config.yaml § dual_review.enabled` 为 true 时，指定技能会自动调用外部模型进行交叉验证：

- `writing.review` — 跨模型论文审阅
- `idea.verify` — 外部新颖性评估
- `proof.critique` — 独立证明检查
- `experiment.analyze` — 外部结果解读

通过 MCP 工具（默认 `mcp__codex__codex`）调用，输出共识点和分歧点。

## 项目结构

```
├── CLAUDE.md              # 行为协议（意图路由 + 数据契约）
├── config.template.yaml   # 复制为 config.yaml 并自定义
├── scripts/setup.sh       # 安装脚本（幂等，支持 --update）
├── skills/
│   ├── CLAUDE.md          # 技能索引
│   ├── micro/             # 14 个微技能 spec 文件（优化目标）
│   └── td-nl/             # TD-NL 技能进化基础设施
├── memory/                # 持久化三级记忆
│   ├── episodes/          # 情景记忆（近期）
│   ├── topics/            # 语义记忆（巩固后）
│   └── procedures/        # 程序记忆（永久）
├── checklists/            # 层级任务追踪（L0/L1/L2）
├── methodology/           # 研究方法 + 想法
│   ├── approach.md        # 研究方向（setup.sh 创建桩文件）
│   └── ideas/             # 想法发现产物
├── paper/                 # 论文相关
│   ├── proofs/            # 证明文件
│   ├── theory/            # 定理声明
│   ├── figures/           # 图表
│   ├── papers/            # 论文草稿
│   └── reviews/           # 审稿相关
├── experiments/           # 实验代码 + 结果
├── logs/                  # 会话日志
│   ├── digest/            # 会话摘要（YAML + SUMMARY.md）
│   ├── progress/          # 进度日志
│   └── experiments/       # 实验日志
├── outputs/               # 研究交付物
│   ├── visuals/           # SVG / 像素画
│   └── paper/             # 论文输出
├── resources/             # 参考材料
│   ├── papers/            # 论文阅读笔记
│   └── repos/             # 参考仓库
├── background/            # 研究背景材料
└── docs/                  # 计划、报告
```

## Token 预算

| 操作 | Token 消耗 |
|------|-----------|
| 会话生命周期（open + close） | ~2-4K |
| G2 内联评估（每次技能触发） | ~100-200 |
| 技能进化（evolve.suggest） | 2-4K |
| 论文分析 | 3-8K |
| 理论形式化 | 3-8K |
| 证明精炼 | 3-10K/轮 |
| 写作（草稿/审阅/润色） | 2-15K |
| 实验（执行 + 监控） | 各 2-4K |
| 想法发现 + 新颖性验证 | 4-8K + 3-6K |
| 规划与进度 | 1-5K |
| 清单操作 | 1-3K |
| 视觉创作 | 2-8K |
| 文献检索 | 2-5K |
| 记忆操作 | 1-3K |

## 与 v5.0 的区别

详见 [docs/CHANGELOG-v5-to-dev.md](docs/CHANGELOG-v5-to-dev.md)。

主要变化：+9 新技能、Intent Router 25→47 条、config 参数化、双审机制、MetaScheduler 集成、setup.sh 从 6 步扩展到 10 步。

## 上游

开发分支。上游仓库：[Shiien/Self-Evolved-Research-Framework](https://github.com/Shiien/Self-Evolved-Research-Framework)

## 许可证

MIT — 见 [LICENSE](LICENSE)
