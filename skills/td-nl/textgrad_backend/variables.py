"""Variable wrapper with a lightweight shim fallback.

If `textgrad` is importable we re-export its Variable/TextLoss/
TextualGradientDescent directly. Otherwise we provide a shim that:
  - stores a string value and a list of accumulated textual gradients
  - supports .backward(...) by appending the critique string
  - supports TextualGradientDescent.step() by prepending a <<EVOLVE NOTE>>
    block to the spec text (non-destructive; suitable for dry-run/CI)

The shim exists so the rest of the pipeline can be exercised without
network access or an API key. For real evolution, install textgrad:
    pip install textgrad
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional

USING_REAL_TEXTGRAD = False
try:  # pragma: no cover - optional dep
    import textgrad as _tg  # type: ignore

    Variable = _tg.Variable  # type: ignore[attr-defined]
    TextLoss = _tg.TextLoss  # type: ignore[attr-defined]
    TextualGradientDescent = _tg.TextualGradientDescent  # type: ignore[attr-defined]
    USING_REAL_TEXTGRAD = True
except Exception:  # fall back to shim

    @dataclass
    class Variable:  # type: ignore[no-redef]
        """Shim Variable. Minimal surface used by the backward/propose code."""

        value: str
        role_description: str = ""
        requires_grad: bool = False
        predecessors: List["Variable"] = field(default_factory=list)
        gradients: List[str] = field(default_factory=list)

        def get_value(self) -> str:
            return self.value

        def set_value(self, v: str) -> None:
            self.value = v

        def backward(self, critique: str = "") -> None:
            """Walks predecessors and appends the critique to each that
            requires_grad. Deterministic; no LLM call."""
            seen = set()
            stack: List[Variable] = [self]
            while stack:
                node = stack.pop()
                if id(node) in seen:
                    continue
                seen.add(id(node))
                for p in node.predecessors:
                    if p.requires_grad and critique:
                        p.gradients.append(critique)
                    stack.append(p)

    @dataclass
    class TextLoss:  # type: ignore[no-redef]
        """Shim loss: carries the critique string and the output variable."""

        evaluation_instruction: str
        engine: Optional[object] = None

        def __call__(self, prediction: Variable) -> Variable:  # type: ignore[override]
            loss_var = Variable(
                value=f"LOSS[{self.evaluation_instruction}] over {prediction.role_description}",
                role_description="textual loss",
                requires_grad=False,
                predecessors=[prediction],
            )
            # attach critique seed so backward has something to propagate
            loss_var._critique_seed = self.evaluation_instruction  # type: ignore[attr-defined]
            # override backward to use the critique seed
            orig_backward = loss_var.backward

            def _backward(critique: str = "") -> None:
                orig_backward(critique or self.evaluation_instruction)

            loss_var.backward = _backward  # type: ignore[assignment]
            return loss_var

    @dataclass
    class TextualGradientDescent:  # type: ignore[no-redef]
        """Shim optimizer: prepends an <<EVOLVE NOTE>> block to each parameter's
        value summarizing accumulated gradients. Non-destructive - the original
        spec text is preserved below the note. Real TGD rewrites the text
        in place using an LLM."""

        parameters: List[Variable]
        engine: Optional[object] = None

        def zero_grad(self) -> None:
            for p in self.parameters:
                p.gradients.clear()

        def step(self) -> None:
            for p in self.parameters:
                if not p.gradients:
                    continue
                header_lines = ["<<EVOLVE NOTE (shim) - accumulated textual gradients>>"]
                for i, g in enumerate(p.gradients, 1):
                    header_lines.append(f"  [g{i}] {g}")
                header_lines.append("<<END EVOLVE NOTE>>\n")
                p.value = "\n".join(header_lines) + p.value
                p.gradients.clear()


def load_skill_variable(path: str, skill_name: str) -> Variable:
    """Load a SKILL.md from disk as a requires_grad Variable."""
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    return Variable(
        value=text,
        role_description=(
            f"skill specification governing when and how '{skill_name}' fires; "
            "edits should preserve YAML frontmatter and keep the public trigger "
            "semantics stable."
        ),
        requires_grad=True,
    )
