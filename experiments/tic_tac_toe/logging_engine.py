"""Engine wrapper that records every (prompt, response) pair to a JSONL file.

Transparent to callers: it has the same __call__/.generate surface as the
inner engine. Useful for debugging and post-hoc auditing of every LLM
interaction during a cycle.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Optional


class LoggingEngine:
    def __init__(self, inner, log_path: Path, label: str = "engine"):
        self.inner = inner
        self.log_path = log_path
        self.label = label
        self._lock = threading.Lock()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        # truncate on construction - one cycle per file
        log_path.write_text("", encoding="utf-8")
        self.call_idx = 0

    def _write(self, entry: dict) -> None:
        with self._lock:
            with self.log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def __call__(self, prompt: str, system_prompt: Optional[str] = None, **kw) -> str:
        t0 = time.time()
        self.call_idx += 1
        idx = self.call_idx
        err = None
        resp = None
        try:
            resp = self.inner(prompt, system_prompt=system_prompt, **kw)
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:300]}"
            raise
        finally:
            self._write(
                {
                    "idx": idx,
                    "label": self.label,
                    "t_start": t0,
                    "t_end": time.time(),
                    "dt_sec": round(time.time() - t0, 2),
                    "system_prompt": (system_prompt or "")[:2000],
                    "prompt": prompt[:2000],
                    "response": (resp or "")[:2000] if not err else None,
                    "error": err,
                }
            )
        return resp

    def generate(self, content: str, system_prompt: Optional[str] = None, **kw) -> str:
        return self.__call__(content, system_prompt=system_prompt, **kw)
