"""TD-NL runtime built on top of TextGrad.

Module layout:
    variables   - wraps each SKILL.md as a (real or shim) textgrad Variable
    trace       - parses feedback-log.md into a per-session DAG
    td_layer    - TD(0) layer: delta = r + gamma*V(s') - V(s), scales text grads
    backward    - orchestrates loss.backward() + TD scaling + TGD.step()
    propose     - writes the proposed spec diff back to feedback-log.md

The package runs with the real `textgrad` package if installed; otherwise it
falls back to a minimal in-process shim that implements the tiny surface
needed here (Variable, TextLoss, TextualGradientDescent). The shim does NOT
call any LLM - it emits deterministic placeholder gradients so the rest of
the pipeline (TD layer, proposal writer, smoke test) can run end-to-end.
"""
from .variables import Variable, TextLoss, TextualGradientDescent, USING_REAL_TEXTGRAD
from .trace import SessionGraph, TraceNode, parse_feedback_log
from .td_layer import TDLayer, td0_error
from .backward import run_backward
from .propose import write_proposal

__all__ = [
    "Variable",
    "TextLoss",
    "TextualGradientDescent",
    "USING_REAL_TEXTGRAD",
    "SessionGraph",
    "TraceNode",
    "parse_feedback_log",
    "TDLayer",
    "td0_error",
    "run_backward",
    "write_proposal",
]
