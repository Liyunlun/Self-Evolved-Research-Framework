"""LLM engines for the TD-NL TextGrad backend.

The engines here implement a minimal callable protocol:

    class Engine:
        def __call__(self, prompt: str, system_prompt: Optional[str] = None) -> str: ...

That protocol is satisfied by real `textgrad.engine.EngineLM` subclasses as
well, so engines produced here can be plugged into real textgrad via
`textgrad.set_backward_engine(engine)` when the full library is installed.

Factory behavior: `make_default_engine()` returns the first working engine
in preference order, or `None` if none is available (so the caller can
cleanly fall back to the deterministic shim behavior).

Preference order:
  1. ClaudeCodeCLIEngine  — if `claude` is on $PATH
  2. (future: AnthropicAPIEngine, OpenAIEngine)
  3. None
"""
from __future__ import annotations

import os
import shutil
from typing import Optional

from .claude_code import ClaudeCodeCLIEngine


def make_default_engine(**kwargs) -> Optional[ClaudeCodeCLIEngine]:
    """Return the preferred available engine, or None.

    Disable entirely by setting env var SER_TDNL_DISABLE_ENGINE=1 (useful
    for CI / fixture-regen runs that must stay deterministic).
    """
    if os.environ.get("SER_TDNL_DISABLE_ENGINE") == "1":
        return None
    if shutil.which("claude") is not None:
        try:
            return ClaudeCodeCLIEngine(**kwargs)
        except Exception:
            return None
    return None


__all__ = ["ClaudeCodeCLIEngine", "make_default_engine"]
