#!/usr/bin/env python3
"""Provider-chain coverage guard (L6).

Static guarantee that every CORE provider call goes through the single
deterministic entry point `run_provider_chain`. Any direct cliproxy /
known_good_chat_path / raw stream call in a core path is a coverage leak.

PASS only when direct_calls == 0 and coverage == 1.0.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER_V2 = ROOT / "server_v2"

# providers.py legitimately implements the chain internals (cliproxy transport,
# stream parser). Everything else is a consumer and must use run_provider_chain.
CHAIN_IMPL_FILE = SERVER_V2 / "providers.py"

CORE_GLOBS = [
    SERVER_V2 / "workflow.py",
    SERVER_V2 / "routers" / "orchestrate.py",
    SERVER_V2 / "routers" / "war_room.py",
    SERVER_V2 / "routers" / "runtime.py",
]

# Direct-call markers that bypass the chain when found in a core file.
DIRECT_MARKERS = (
    r"\bknown_good_chat_path\s*\(",
    r"\b_stream_chat_completion\s*\(",
    r"CLIPROXY_API\s*\}?/?chat",
    r"127\.0\.0\.1:8317/v1",
    r"127\.0\.0\.1:8642/v1",
    r"\bsafe_provider_call\s*\(",
    r"\bsmart_provider_call\s*\(",
    r"\brun_auth_pool\s*\(",
)
CHAIN_MARKER = re.compile(r"\brun_provider_chain\s*\(")


def scan() -> dict:
    scan_result: list[dict] = []
    direct_calls = 0
    chain_calls = 0

    for path in CORE_GLOBS:
        if not path.exists():
            continue
        rel = str(path.relative_to(ROOT))
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for marker in DIRECT_MARKERS:
                if re.search(marker, line):
                    direct_calls += 1
                    scan_result.append({"file": rel, "line": i, "call_type": "direct_bypass",
                                         "marker": marker, "code": stripped[:120]})
            if CHAIN_MARKER.search(line):
                chain_calls += 1
                scan_result.append({"file": rel, "line": i, "call_type": "chain_entry",
                                    "code": stripped[:120]})

    total = direct_calls + chain_calls
    coverage = 1.0 if direct_calls == 0 and chain_calls > 0 else (
        round(chain_calls / total, 4) if total else 0.0
    )
    return {
        "PASS": direct_calls == 0 and chain_calls >= 1,
        "total_provider_calls": total,
        "chain_calls": chain_calls,
        "direct_calls": direct_calls,
        "coverage": coverage,
        "scan": scan_result,
        "chain_impl_file": str(CHAIN_IMPL_FILE.relative_to(ROOT)),
    }


def main() -> int:
    result = scan()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["PASS"] and result["coverage"] == 1.0 else 1


if __name__ == "__main__":
    sys.exit(main())
