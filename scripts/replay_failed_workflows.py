#!/usr/bin/env python3
"""L8 Failure Replay Engine.

Read-only analysis of failed workflows + execution memory. Does NOT mutate
production state and does NOT re-run real provider calls (no provider storm).
It reconstructs the recovery path each failed task would take through the
deterministic chain and reports provider comparison. PASS when analysis
completes coherently (an empty failure set is a valid PASS).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

QUEUE = ROOT / "data" / "task_queue.json"


def main() -> int:
    try:
        from server_v2 import provider_intelligence as pi
        from server_v2.providers import PROVIDER_CHAIN
        pi.ensure_data_files()

        tasks = []
        if QUEUE.exists():
            try:
                tasks = json.loads(QUEUE.read_text(encoding="utf-8") or "[]")
            except Exception:
                tasks = []
        failed = [t for t in tasks if isinstance(t, dict) and t.get("status") == "failed"]

        replays = []
        for t in failed[-50:]:
            res = t.get("result") if isinstance(t.get("result"), dict) else {}
            tr = res.get("trace") if isinstance(res.get("trace"), dict) else {}
            attempts = tr.get("provider_attempts") if isinstance(tr.get("provider_attempts"), list) else []
            tried = [a.get("provider") for a in attempts if isinstance(a, dict)]
            # Recovery path = remaining deterministic chain after the tried set.
            recovery = [s["provider"] for s in PROVIDER_CHAIN if s["provider"] not in tried]
            replays.append({
                "task_id": t.get("id"),
                "error": (t.get("error") or res.get("error") or "")[:120],
                "providers_tried": tried,
                "recovery_path": recovery,
                "recoverable": bool(recovery),
            })

        mem = pi.read_execution_memory(limit=500)
        learning = pi.build_learning_report()

        recoverable = sum(1 for r in replays if r["recoverable"])
        report = {
            "PASS": True,  # analysis completed; empty failure set is valid
            "failed_workflows": len(failed),
            "replayed": len(replays),
            "recoverable": recoverable,
            "execution_memory_records": len(mem),
            "most_stable_provider": learning.get("most_stable_provider"),
            "sample": replays[:5],
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"PASS": False, "error": str(exc)[:200]}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
