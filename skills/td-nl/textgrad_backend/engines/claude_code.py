"""Claude Code CLI as a TextGrad-compatible LLM engine.

Shells out to `claude -p --output-format text` per call, using the user's
existing Claude Code authentication. No separate ANTHROPIC_API_KEY
required — OAuth/keychain auth works because we do NOT pass --bare.

Isolation flags used to keep engine calls from recursing into SER:
  --disable-slash-commands  : skills don't fire inside the engine call
  --output-format text      : plain-text response on stdout

The engine runs from a neutral cwd (default: /tmp) so that project-level
CLAUDE.md files are not auto-loaded. User-level ~/.claude/CLAUDE.md
still loads; callers that need full isolation should pass their own cwd.

Protocol:
    engine(prompt)                         -> str
    engine(prompt, system_prompt="...")    -> str
    engine.generate(content, system_prompt=...)  # alias for textgrad compat
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Optional


class ClaudeCodeCLIEngine:
    """LLM engine that invokes the Claude Code CLI in non-interactive mode."""

    def __init__(
        self,
        model: str = "haiku",
        timeout: float = 120.0,
        cwd: Optional[str] = "/tmp",
        extra_args: Optional[Iterable[str]] = None,
        cli_path: Optional[str] = None,
    ):
        self.model = model
        self.timeout = timeout
        self.cwd = cwd
        self.extra_args = list(extra_args) if extra_args else []
        resolved = cli_path or shutil.which("claude")
        if not resolved:
            raise RuntimeError(
                "claude CLI not found on PATH — install Claude Code or pass cli_path="
            )
        self.cli_path = resolved

    # textgrad's EngineLM surface expects both __call__ and .generate
    def __call__(self, prompt: str, system_prompt: Optional[str] = None, **_) -> str:
        return self.generate(prompt, system_prompt=system_prompt)

    def generate(
        self,
        content: str,
        system_prompt: Optional[str] = None,
        **_,
    ) -> str:
        if not isinstance(content, str):
            content = str(content)
        argv = [
            self.cli_path,
            "-p",
            "--model",
            self.model,
            "--output-format",
            "text",
            "--disable-slash-commands",
        ]
        if system_prompt:
            argv += ["--system-prompt", system_prompt]
        argv += self.extra_args
        proc = subprocess.run(
            argv,
            input=content,
            capture_output=True,
            text=True,
            timeout=self.timeout,
            cwd=self.cwd,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"claude CLI exited {proc.returncode}: "
                f"{proc.stderr.strip()[:500] or '(no stderr)'}"
            )
        return proc.stdout.strip()

    def __repr__(self) -> str:  # pragma: no cover
        return f"ClaudeCodeCLIEngine(model={self.model!r}, cwd={self.cwd!r})"
