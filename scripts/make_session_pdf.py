#!/usr/bin/env python3
"""Generate PDF report documenting the TextGrad-backed TD-NL mechanism
with two worked examples (paper-read TextGrad, session summarize task).
Uses fpdf2 and an available CJK TTF font."""
from __future__ import annotations
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

LATIN_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
LATIN_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
CJK_FONT = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
OUT = Path("outputs/session-artifacts/2026-04-20-textgrad-td-nl-walkthrough.pdf")


class PDF(FPDF):
    def header(self):
        pass
    def footer(self):
        self.set_y(-14)
        self.set_font("CJK", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"TextGrad x TD-NL walkthrough  -  Page {self.page_no()}",
                  align="C")


def mc(pdf, h, txt):
    pdf.multi_cell(0, h, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def h1(pdf, txt):
    pdf.set_font("CJK", "", 18); pdf.set_text_color(10, 20, 60)
    pdf.ln(2); mc(pdf, 9, txt); pdf.ln(1)


def h2(pdf, txt):
    pdf.set_font("CJK", "", 14); pdf.set_text_color(30, 60, 110)
    pdf.ln(3); mc(pdf, 8, txt); pdf.ln(0.5)


def h3(pdf, txt):
    pdf.set_font("CJK", "", 12); pdf.set_text_color(50, 90, 140)
    pdf.ln(2); mc(pdf, 7, txt)


def body(pdf, txt):
    pdf.set_font("CJK", "", 10.5); pdf.set_text_color(30, 30, 30)
    mc(pdf, 5.5, txt); pdf.ln(0.5)


def code(pdf, txt):
    pdf.set_font("CJKMono", "", 8.5)
    pdf.set_fill_color(244, 244, 247); pdf.set_text_color(20, 20, 60)
    for line in txt.rstrip("\n").split("\n"):
        pdf.set_x(pdf.l_margin)
        pdf.cell(0, 4.6, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
    pdf.ln(1)


def bullet(pdf, items):
    pdf.set_font("CJK", "", 10.5); pdf.set_text_color(30, 30, 30)
    for b in items:
        pdf.set_x(pdf.l_margin + 4)
        pdf.multi_cell(0, 5.5, f"\u2022 {b}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(0.5)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(left=14, top=14, right=14)
    pdf.set_auto_page_break(auto=True, margin=16)
    # Primary: Latin (DejaVu), fallback: CJK (Droid)
    pdf.add_font("CJK", "", LATIN_FONT)
    pdf.add_font("CJKMono", "", LATIN_MONO)
    pdf.add_font("ZH", "", CJK_FONT)
    pdf.set_fallback_fonts(["ZH"])
    pdf.add_page()

    # ---------- cover ----------
    pdf.set_font("CJK", "", 22); pdf.set_text_color(10, 20, 60)
    pdf.ln(18)
    mc(pdf, 11, "TextGrad x TD-NL 机制说明")
    pdf.set_font("CJK", "", 14); pdf.set_text_color(60, 60, 90)
    mc(pdf, 8, "SER 框架 skill 进化层的端到端走查 + 两个实例")
    pdf.ln(4)
    pdf.set_font("CJK", "", 10.5); pdf.set_text_color(90, 90, 90)
    mc(pdf, 6,
        "Session:  2026-04-20\n"
        "Branch:   skills-to-standard-claude-format\n"
        "Commit:   ae4b157  \"Add TextGrad backend for TD-NL skill evolution\"\n"
        "Examples: (1) paper-read of TextGrad   (2) this session's summarize-project task")
    pdf.ln(6)

    h2(pdf, "一、本次 session 的交付")
    bullet(pdf, [
        "新增 skills/td-nl/textgrad_backend/ 包 (7 个文件)：variables / trace / td_layer / backward / propose / test_smoke / __init__",
        "新增 CLI：scripts/evolve_textgrad.py (--dry-run / --apply-proposal / --gamma / --json)",
        "G2 schema 升级到 v3 (5-phase inline TD)；v2 / v1 依旧兼容",
        "evolve-cycle.md、evolve-suggest/SKILL.md、feedback-log.md 全部同步更新",
        "4/4 smoke tests 通过，包括新增的 v3 解析与置信度覆盖用例",
    ])

    h2(pdf, "二、整体数据流")
    code(pdf,
        "G2 text block (v3, 5-phase)\n"
        "      |  trace.py  regex + comment-strip\n"
        "      v\n"
        "SessionGraph (DAG, Kahn topo order)\n"
        "      |  aggregate()\n"
        "      v\n"
        "{skill -> SkillAggregate(predicted_Vs, inline_tds, conf_votes,...)}\n"
        "      |  TDLayer.score():  r + gamma*V(s') - V(s)  blended 50/50 with inline_td\n"
        "      v\n"
        "{skill -> td_error, strength, new_overall}\n"
        "      |  backward.py: spec_var + firing_var DAG  ->  TextLoss(head, critique)\n"
        "      v\n"
        "TextualGradientDescent.step()  (only strength == hard)\n"
        "      |  propose.py: pick max|td| hard skill\n"
        "      v\n"
        "PROPOSAL entry -> feedback-log.md S Pending Proposals\n"
        "      |  user 审批\n"
        "      v\n"
        "evolve-apply -> 真正改 SKILL.md + history 快照")

    # ---------- Example 1 ----------
    pdf.add_page()
    h1(pdf, "示例 1：paper-read TextGrad")
    body(pdf,
        "场景：用户把《TextGrad》arXiv 论文扔给 SER，Claude 触发 paper-read，后续自动链式触发 "
        "memory-write、memory-consolidate，session-close 时 evolve-suggest 做 G1 聚合。"
        "整个 session 共有 4 个 firing，形成一条线性 DAG。")

    h2(pdf, "1.1  Session 内的 G2 写入 (v3 5-phase)")
    code(pdf,
        "- [2026-04-20] session:s7 node:n1 upstream:- skill:paper-read\n"
        "    P1_analysis: \"arXiv paper TextGrad, 公式密集方法节\"\n"
        "    P2_predict:  V=7, conf=high, reason=\"paper-read 在 arXiv 类稳定\"\n"
        "    P4_strategy: keep\n"
        "    P5_result:   outcome=as_expected, reward=0, ev=\"提取到 3 个核心贡献\"\n"
        "\n"
        "- [2026-04-20] session:s7 node:n2 upstream:n1 skill:memory-write\n"
        "    P1_analysis: \"写 1 条 episodic, TextGrad 方法梗概\"\n"
        "    P2_predict:  V=6, conf=medium, reason=\"对公式内容偶有截断\"\n"
        "    P3_td:       delta=-0.9, interp=\"轻微下修\"\n"
        "    P4_strategy: keep\n"
        "    P5_result:   outcome=as_expected, reward=0, ev=\"写入成功, 含 3 个标签\"\n"
        "\n"
        "- [2026-04-20] session:s7 node:n3 upstream:n2 skill:memory-consolidate\n"
        "    P1_analysis: \"归并 2 条 textgrad episodic 到 topics/textgrad.md\"\n"
        "    P2_predict:  V=5, conf=high, reason=\"首次 merge 新主题常漏字段\"\n"
        "    P3_td:       delta=-1.5, interp=\"确认 prior 失败模式复现\"\n"
        "    P4_strategy: refine, note=\"保留 method 小节\"\n"
        "    P5_result:   outcome=worse, reward=-1, ev=\"丢了 backward pass 公式\"\n"
        "\n"
        "- [2026-04-20] session:s7 node:n4 upstream:n3 skill:evolve-suggest\n"
        "    P1_analysis: \"本 session 有 1 处下游感知的 upstream 失败\"\n"
        "    P2_predict:  V=6, conf=high\n"
        "    P3_td:       delta=-0.4, interp=\"小偏差\"\n"
        "    P4_strategy: keep\n"
        "    P5_result:   outcome=as_expected, reward=0, ev=\"backend 跑通, 1 proposal\"")

    h2(pdf, "1.2  Parser -> SessionGraph")
    body(pdf,
        "trace.py 先用 _iter_pending_lines 跨行剥离 <!-- ... --> 注释（防止 schema 示例被误吃），"
        "再按 _V3_HEAD_RE 识别 v3 块头，状态机收集 P1-P5 字段。Kahn 拓扑给出执行序 [n1,n2,n3,n4]。")
    code(pdf,
        "SessionGraph(session='s7',\n"
        "  nodes={\n"
        "    'n1': TraceNode(skill='paper-read',       predicted_V=7, conf='high',\n"
        "                    inline_td=None, reward=0,  is_v3=True),\n"
        "    'n2': TraceNode(skill='memory-write',     predicted_V=6, conf='medium',\n"
        "                    inline_td=-0.9, reward=0,  is_v3=True),\n"
        "    'n3': TraceNode(skill='memory-consolidate', predicted_V=5, conf='high',\n"
        "                    inline_td=-1.5, reward=-1, outcome='worse'),\n"
        "    'n4': TraceNode(skill='evolve-suggest',   predicted_V=6, conf='high',\n"
        "                    inline_td=-0.4, reward=0)\n"
        "  })")

    h2(pdf, "1.3  TD(0) 打分 (memory-consolidate 细节)")
    code(pdf,
        "V(s)  = current_values['memory-consolidate'] = 6.0\n"
        "V(s') = mean(predicted_Vs) = 5.0                 # v3 优先 over bootstrap\n"
        "r     = net_delta / max(1, count) = -1.0\n"
        "gamma = 0.9\n"
        "\n"
        "td_batch   = r + gamma*V(s') - V(s) = -1 + 0.9*5 - 6 = -2.5\n"
        "td_inline  = mean(inline_tds) = -1.5\n"
        "td_final   = 0.5*td_batch + 0.5*td_inline = -2.0\n"
        "\n"
        "confidence = argmax(conf_votes) = 'high'   ->   lr = 1.0\n"
        "|td_final| = 2.0  >=  1.0   ->   strength = 'hard'\n"
        "new_overall = clamp(6.0 + 1.0 * -2.0, 1, 10) = 4.0")
    body(pdf,
        "其余 skill 全部落到 soft / drop，因此最终只有 memory-consolidate 带 hard 标签。")

    h2(pdf, "1.4  TextGrad 反向图 + TGD.step")
    code(pdf,
        "spec_vars[memory-consolidate]  (requires_grad=True, SKILL.md 全文)\n"
        "    v\n"
        "firing_vars[n3] (preds = [spec_vars[memory-consolidate], firing_vars[n2]])\n"
        "    v\n"
        "firing_vars[n4] (preds = [spec_vars[evolve-suggest],     firing_vars[n3]])\n"
        "    v\n"
        "head (preds = [firing_vars[n4]])\n"
        "    v\n"
        "TextLoss(head, critique=\"SESSION s7 TD REPORT ... memory-consolidate td=-2.0 hard ...\")\n"
        "    v\n"
        "loss.backward()  -> 每个 requires_grad Variable 得到 textual gradient\n"
        "TextualGradientDescent.step() 仅覆盖 strength==hard 的 spec_var")
    body(pdf,
        "离线环境下，shim 在 SKILL.md 前面贴 <<EVOLVE NOTE (shim)>> 作为占位。")

    h2(pdf, "1.5  Propose + 日志搬移")
    code(pdf,
        "# 写入 feedback-log.md S Pending Proposals:\n"
        "- [2026-04-20] PROPOSAL target:memory-consolidate (Q^L: 6.0 -> 4.0, delta:-2.00)\n"
        "    problem: 归并时丢失方法节公式\n"
        "    gradient: <textgrad 返回的自然语言梯度>\n"
        "    diff: |\n"
        "      - Merge episodic memories by topic.\n"
        "      + Merge episodic memories by topic, preserving any method-section\n"
        "      +   equations or pseudocode blocks verbatim.\n"
        "    evidence: 丢了 backward pass 的公式小节\n"
        "    risk: 可能使 topic 文件膨胀; 回滚路径 skills/td-nl/history/\n"
        "\n"
        "# 4 个 G2 块移入 Processed Feedback，写 cycle summary:\n"
        "- Cycle 2026-04-20 [session:s7]: 4 entries across 4 skills (V^L 6.0 -> 5.5)\n"
        "  - memory-consolidate: net_delta=-1, td_error=-2.00, strength=hard\n"
        "  - paper-read:         net_delta=0,  td_error=-0.70, strength=soft\n"
        "  - memory-write:       net_delta=0,  td_error=-0.25, strength=soft\n"
        "  - evolve-suggest:     net_delta=0,  td_error=-0.50, strength=soft\n"
        "  - Spec proposal: yes (target: memory-consolidate)")

    # ---------- Example 2 ----------
    pdf.add_page()
    h1(pdf, "示例 2：总结描述当前项目 (本 session 本身)")
    body(pdf,
        "这是一个 meta 实例：把用户这一整个 session（让 Claude 研究 textgrad、"
        "实现 trace 化、讲解机制、生成 PDF）按 G2 规范回溯记录，"
        "看 evolve-suggest 会得出什么结论。session 内有 6 个 firing，形成双链分叉。")

    h2(pdf, "2.1  触发链 (逻辑时序)")
    code(pdf,
        "session:s8 (legacy chain from compaction resumed)\n"
        "\n"
        "  n1  general-research      (search textgrad literature)\n"
        "   |\n"
        "  n2  design-converge       (choose option C: trace化)\n"
        "   |\n"
        "  n3  writing-draft         (implement textgrad_backend/ package)\n"
        "   |\n"
        "  n4  writing-draft         (mechanism explanation - Round 1)\n"
        "   |\n"
        "  n5  writing-draft         (mechanism explanation - Round 2, example-driven)\n"
        "   |\n"
        "  n6  session-close         (this node: memory + PDF + digest)")

    h2(pdf, "2.2  G2 (v3) 记录")
    code(pdf,
        "- [2026-04-20] session:s8 node:n1 upstream:- skill:general-research\n"
        "    P1_analysis: \"查 TextGrad 与 TDRL 结合的相关工作\"\n"
        "    P2_predict:  V=7, conf=high, reason=\"open web + 目标明确\"\n"
        "    P4_strategy: keep\n"
        "    P5_result:   outcome=better, reward=+1, ev=\"定位到 ProTeGi/Trace/REVOLVE 等\"\n"
        "\n"
        "- [2026-04-20] session:s8 node:n2 upstream:n1 skill:design-converge\n"
        "    P1_analysis: \"选方案 C (DAG trace 化)\"\n"
        "    P2_predict:  V=7, conf=high\n"
        "    P3_td:       delta=+0.3, interp=\"方案收敛, 走向清晰\"\n"
        "    P4_strategy: keep\n"
        "    P5_result:   outcome=better, reward=+1, ev=\"确定 spec_var + firing_var 双层 DAG\"\n"
        "\n"
        "- [2026-04-20] session:s8 node:n3 upstream:n2 skill:writing-draft\n"
        "    P1_analysis: \"实现 backend 代码 7 文件\"\n"
        "    P2_predict:  V=7, conf=high\n"
        "    P3_td:       delta=+0.5, interp=\"smoke test 全绿\"\n"
        "    P4_strategy: keep\n"
        "    P5_result:   outcome=better, reward=+1, ev=\"4/4 tests pass, td=-2.925 符合预期\"\n"
        "\n"
        "- [2026-04-20] session:s8 node:n4 upstream:n3 skill:writing-draft\n"
        "    P1_analysis: \"为用户产出第一版机制讲解\"\n"
        "    P2_predict:  V=7, conf=high\n"
        "    P3_td:       delta=0.0, interp=\"稳定输出\"\n"
        "    P4_strategy: keep\n"
        "    P5_result:   outcome=as_expected, reward=0, ev=\"用户继续追问具体例子\"\n"
        "\n"
        "- [2026-04-20] session:s8 node:n5 upstream:n4 skill:writing-draft\n"
        "    P1_analysis: \"写具体例子驱动的完整讲解\"\n"
        "    P2_predict:  V=8, conf=high, reason=\"用 numeric walkthrough 提清晰度\"\n"
        "    P3_td:       delta=+0.8, interp=\"用户称'非常有用'\"\n"
        "    P4_strategy: keep, note=\"下次可直接默认写示例驱动版本\"\n"
        "    P5_result:   outcome=better, reward=+1, ev=\"用户进一步请求 PDF 固化\"\n"
        "\n"
        "- [2026-04-20] session:s8 node:n6 upstream:n5 skill:session-close\n"
        "    P1_analysis: \"执行 memory + PDF + digest 三件套\"\n"
        "    P2_predict:  V=7, conf=high\n"
        "    P3_td:       delta=0.0, interp=\"流程性工作\"\n"
        "    P4_strategy: keep\n"
        "    P5_result:   outcome=as_expected, reward=0, ev=\"生成本 PDF 成功\"")

    h2(pdf, "2.3  TD(0) 计算 (writing-draft 合并 3 次 firing)")
    body(pdf,
        "writing-draft 在 session 中触发 3 次 (n3, n4, n5)，聚合时被合并到一个 SkillAggregate：")
    code(pdf,
        "predicted_Vs = [7, 7, 8]             mean = 7.33    -> V(s')\n"
        "inline_tds   = [+0.5, 0.0, +0.8]     mean = +0.43   -> td_inline\n"
        "conf_votes   = {'high': 3}           confidence = 'high',  lr = 1.0\n"
        "strategy     = {'keep': 3}           action = keep\n"
        "\n"
        "assume V(s) = current_values['writing-draft'] = 6.5\n"
        "r = (+1 + 0 + +1) / 3 = +0.67\n"
        "td_batch = 0.67 + 0.9*7.33 - 6.5 = +0.77\n"
        "td_final = 0.5*0.77 + 0.5*0.43   = +0.60\n"
        "\n"
        "|td| = 0.60  ->   strength = 'soft'   (>=0.25 但 <1.0)\n"
        "new_overall = clamp(6.5 + 1.0*0.60, 1, 10) = 7.10")

    h2(pdf, "2.4  结论 (evolve-suggest 给出的 session 报告)")
    code(pdf,
        "Cycle 2026-04-20 [session:s8]: 6 entries across 4 skills (V^L 6.0 -> 6.4)\n"
        "  - general-research : net_delta=+1, td=+0.40, strength=soft\n"
        "  - design-converge  : net_delta=+1, td=+0.40, strength=soft\n"
        "  - writing-draft    : net_delta=+2, td=+0.60, strength=soft\n"
        "  - session-close    : net_delta=0,  td=+0.00, strength=drop\n"
        "  Spec proposal: none (no skill reached |td|>=1.0)\n"
        "  Observation: writing-draft 连续正向 (第 1 次同向), 若再 2 次可触发非 hard 提案")
    body(pdf,
        "这正是 TD-NL 的设计意图：好的 session 也能驱动缓慢的 Q^L 上修 (soft 更新)，"
        "但不会产出 proposal，避免'状态好时盲目改规格'。")

    # ---------- invariants ----------
    pdf.add_page()
    h1(pdf, "三、核心不变量 + 风险收敛")
    bullet(pdf, [
        "一次 session 最多一个 SKILL.md 被改 (propose 阶段只取 max|td| 的 hard skill)",
        "spec 改动永远可回滚 (history/ 快照 + 单点修改 + user 审批)",
        "v1/v2/v3 schema 混合文件依然能解析 (三套正则 + dispatcher)",
        "shim 保证离线可测 (variables.py 占位 Variable / TextLoss / TGD)",
        "v3 的 conf 和 V 自估可以覆盖统计兜底 (小样本高置信也能驱动 hard update)",
        "G2 与 evolve-suggest 解耦：G2 仅写 pending, 聚合/反向/提案全部在 CLI 内完成",
    ])

    h2(pdf, "四、与相关工作的接口")
    code(pdf,
        "TextGrad    :  Variable, TextLoss, TextualGradientDescent (LLM 文本梯度)\n"
        "TD(0)       :  delta = r + gamma*V(s') - V(s)  on top of textual gradients\n"
        "Trace-OptoPrime: 本工作的 spec_var + firing_var 双层 DAG 受其启发\n"
        "ProTeGi     :  单 skill 的 prompt 优化 (本工作用 TGD 替代)\n"
        "REVOLVE     :  revision layer, 启发了 propose 的 diff 生成\n"
        "Reflexion   :  P1/P4 反思段落的灵感来源")

    h2(pdf, "五、文件清单")
    code(pdf,
        "scripts/evolve_textgrad.py                                  # CLI 入口\n"
        "scripts/make_session_pdf.py                                 # 本 PDF 生成器\n"
        "skills/td-nl/textgrad_backend/__init__.py                   # 包入口\n"
        "skills/td-nl/textgrad_backend/variables.py                  # Variable / shim\n"
        "skills/td-nl/textgrad_backend/trace.py                      # v1/v2/v3 parser + DAG\n"
        "skills/td-nl/textgrad_backend/td_layer.py                   # TD(0) 聚合打分\n"
        "skills/td-nl/textgrad_backend/backward.py                   # 反向图构造\n"
        "skills/td-nl/textgrad_backend/propose.py                    # 提案 + 日志搬移\n"
        "skills/td-nl/textgrad_backend/test_smoke.py                 # 4 个离线用例\n"
        "skills/_shared/evolve-cycle.md                              # G2/G1 文档 (v3)\n"
        "skills/evolve-suggest/SKILL.md                              # 调用 CLI 的首选路径\n"
        "skills/td-nl/feedback-log.md                                # schema v3 头注释")

    pdf.output(str(OUT))
    print(f"wrote {OUT}  ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
