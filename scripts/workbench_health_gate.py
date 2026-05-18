#!/usr/bin/env python3
"""Workbench health baseline, release gate, and daily patrol.

This script is intentionally dependency-light and safe for live runtime checks.
It does not modify production data beyond creating and revoking short-lived
login sessions used for smoke tests.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = os.getenv("HERMES_HEALTH_BASE_URL", "http://127.0.0.1:8765").rstrip("/")
TARGET_MODELS = {
    "chatgpt": "gpt-5.5",
    "gemini-auth": "gemini-3.1-pro",
    "gemini-api": "gemini-3.1-pro",
}

HEALTH_SCORE_WEIGHTS = {
    "auth_success_rate": 20,
    "logout_success_rate": 15,
    "ai_route_correct_rate": 15,
    "provider_error_rate": 10,
    "scheduler_success_rate": 10,
    "config_cache_correct_rate": 10,
    "file_center_availability": 10,
    "observability_rate": 10,
}

CHANGE_TIERS = {
    "1": {
        "name": "tier_1_low_risk",
        "required_modes": ["preflight"],
        "description": "Docs, tests, read-only scripts, copy changes, or isolated non-runtime governance updates.",
    },
    "2": {
        "name": "tier_2_runtime_safe",
        "required_modes": ["preflight", "live"],
        "description": "Small runtime changes touching UI, observability, AI routing, config reads, or non-destructive APIs.",
    },
    "3": {
        "name": "tier_3_production_critical",
        "required_modes": ["preflight", "live", "daily"],
        "description": "Auth, permission, config mutation, file center, scheduler, rollback, database, or production-asset-adjacent changes.",
    },
}


class _CaseInsensitiveHeaders(dict):
    """RFC 7230 §3.2: HTTP header field names are case-insensitive.

    Plain ``dict(resp.headers)`` loses the case-insensitivity of
    ``http.client.HTTPMessage``. Behind uvicorn (which always lowercases
    response header names on the wire) a case-sensitive ``.get("Set-Cookie")``
    would miss the genuinely-present ``set-cookie`` header. This preserves the
    dict interface while making lookups case-insensitive.
    """

    def __init__(self, headers: object) -> None:
        super().__init__()
        self._lower: dict[str, str] = {}
        for key, value in (headers.items() if hasattr(headers, "items") else []):
            self[key] = value
            self._lower[key.lower()] = value

    def get(self, key: str, default: object = None) -> object:  # type: ignore[override]
        if key in self:
            return self[key]
        return self._lower.get(key.lower(), default)


class Gate:
    def __init__(self, base_url: str, *, verbose: bool = False, change_tier: str = "2", change_id: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.verbose = verbose
        self.change_tier = change_tier if change_tier in CHANGE_TIERS else "2"
        self.change_id = change_id or f"change-{time.strftime('%Y%m%d-%H%M%S')}"
        self.results: list[dict] = []

    def check(self, name: str, ok: bool, detail: object = None, *, critical: bool = True) -> None:
        item = {
            "name": name,
            "status": "PASS" if ok else "FAIL",
            "critical": bool(critical),
            "detail": detail if detail is not None else {},
        }
        self.results.append(item)
        if self.verbose or not ok:
            print(json.dumps(item, ensure_ascii=False))

    def result_ok(self, name: str) -> bool:
        return any(item["name"] == name and item["status"] == "PASS" for item in self.results)

    def run_command(self, name: str, command: list[str], *, critical: bool = True) -> None:
        started = time.time()
        try:
            proc = subprocess.run(
                command,
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=120,
            )
            self.check(
                name,
                proc.returncode == 0,
                {
                    "command": command,
                    "duration_ms": int((time.time() - started) * 1000),
                    "output_tail": proc.stdout[-1200:],
                },
                critical=critical,
            )
        except Exception as exc:
            self.check(name, False, {"command": command, "error": str(exc)}, critical=critical)

    def request(
        self,
        opener: urllib.request.OpenerDirector,
        path: str,
        *,
        method: str = "GET",
        data: dict | None = None,
        headers: dict | None = None,
        timeout: int = 12,
    ) -> tuple[int, dict, dict]:
        body = None
        next_headers = {"Accept": "application/json", **(headers or {})}
        if data is not None:
            body = json.dumps(data).encode("utf-8")
            next_headers["Content-Type"] = "application/json"
        req = urllib.request.Request(
            self.base_url + path,
            data=body,
            method=method,
            headers=next_headers,
        )
        try:
            with opener.open(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
                return resp.status, _CaseInsensitiveHeaders(resp.headers), self._json(raw)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", "replace")
            return exc.code, _CaseInsensitiveHeaders(exc.headers), self._json(raw)

    @staticmethod
    def _json(raw: str) -> dict:
        try:
            payload = json.loads(raw or "{}")
            return payload if isinstance(payload, dict) else {"raw": payload}
        except Exception:
            return {"raw": raw[:500]}

    @staticmethod
    def opener() -> urllib.request.OpenerDirector:
        jar = http.cookiejar.CookieJar()
        return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    def preflight(self) -> None:
        self.run_command("python_syntax_app_server", ["python3", "-m", "py_compile", "app_server.py"])
        self.run_command("frontend_js_syntax", ["node", "--check", "assets/app.js"])
        self.run_command("api_js_syntax", ["node", "--check", "assets/api.js"])
        self.run_command("auth_js_syntax", ["node", "--check", "assets/auth.js"])
        self.run_command("skill_registry_audit", ["python3", "scripts/skill_registry_audit.py"])
        self.run_command("skill_guide_audit", ["python3", "scripts/skill_guide_audit.py"])
        self.run_command("ai_quality_eval", ["python3", "scripts/workbench_ai_eval.py"])
        self.run_command("contract_tests", ["python3", "tests/test_intelligence_refresh_contract.py"])

    def live(self, *, daily: bool = False) -> None:
        email = os.getenv("HERMES_HEALTH_EMAIL") or os.getenv("FASTONE_TEST_EMAIL") or ""
        password = os.getenv("HERMES_HEALTH_PASSWORD") or os.getenv("FASTONE_TEST_PASSWORD") or ""

        public = self.opener()
        status, _, health = self.request(public, "/api/health")
        self.check("health_endpoint", status == 200 and health.get("ok") is True, {"status": status, "payload": health})

        status, _, unauth_admin = self.request(public, "/api/admin/platform-settings")
        self.check(
            "unauth_admin_api_blocked",
            status in {401, 403},
            {"status": status, "error": unauth_admin.get("error")},
        )

        if not email or not password:
            self.check(
                "credentials_available_for_auth_smoke",
                False,
                "Set HERMES_HEALTH_EMAIL and HERMES_HEALTH_PASSWORD for auth smoke checks.",
            )
            return

        status, _, missing = self.request(
            public,
            "/api/auth/login",
            method="POST",
            data={"identifier": email, "password": password},
        )
        self.check(
            "login_requires_browser_session_header",
            status == 400 and missing.get("error") == "browser_session_required",
            {"status": status, "error": missing.get("error")},
        )

        opener = self.opener()
        browser_session = f"bs-gate-{int(time.time())}"
        auth_headers = {"X-Hermes-Browser-Session": browser_session}
        status, login_headers, login = self.request(
            opener,
            "/api/auth/login",
            method="POST",
            data={"identifier": email, "password": password},
            headers=auth_headers,
        )
        set_cookie = str(login_headers.get("Set-Cookie") or "")
        self.check(
            "login_cookie_is_session_scoped",
            status == 200
            and login.get("authenticated") is True
            and "Max-Age" not in set_cookie
            and "Expires=" not in set_cookie,
            {"status": status, "authenticated": login.get("authenticated")},
        )

        status, _, me = self.request(opener, "/api/me", headers=auth_headers)
        self.check("same_browser_session_stays_authenticated", status == 200 and me.get("authenticated") is True, {"status": status})

        status, _, reopened = self.request(opener, "/api/me", headers={"X-Hermes-Browser-Session": browser_session + "-reopened"})
        self.check("browser_reopen_simulation_requires_login", status == 401 and not reopened.get("authenticated"), {"status": status})

        # Re-login because the browser-reopen mismatch intentionally revokes the previous session.
        opener = self.opener()
        browser_session = f"bs-gate-2-{int(time.time())}"
        auth_headers = {"X-Hermes-Browser-Session": browser_session}
        status, _, login = self.request(
            opener,
            "/api/auth/login",
            method="POST",
            data={"identifier": email, "password": password},
            headers=auth_headers,
        )
        self.check("second_login_for_protected_smoke", status == 200 and login.get("authenticated") is True, {"status": status})

        status, _, agents = self.request(opener, "/api/ai-agents", headers=auth_headers)
        agent_models = {
            str(item.get("id") or ""): str(item.get("model") or "")
            for item in agents.get("agents", [])
            if isinstance(item, dict)
        }
        self.check(
            "ai_agent_actual_models",
            status == 200 and all(agent_models.get(key) == value for key, value in TARGET_MODELS.items()),
            {"status": status, "models": {key: agent_models.get(key) for key in TARGET_MODELS}},
        )

        status, settings_headers, settings = self.request(opener, "/api/admin/platform-settings", headers=auth_headers)
        cache_control = str(settings_headers.get("Cache-Control") or "")
        self.check(
            "platform_settings_no_store",
            status == 200 and settings.get("ok") is True and "no-store" in cache_control,
            {"status": status, "cache_control": cache_control},
        )

        status, _, files = self.request(opener, "/api/v2/file-center/files", headers=auth_headers)
        self.check("file_center_list_available", status == 200 and files.get("ok") is True, {"status": status, "count": files.get("count")})

        status, _, cron = self.request(opener, "/api/cron-status", headers=auth_headers)
        self.check("cron_status_readable", status == 200 and cron.get("ok") is True, {"status": status})

        status, _, release = self.request(opener, "/api/release-observability?window=24h", headers=auth_headers)
        self.check("release_observability_readable", status == 200 and release.get("ok") is True, {"status": status})
        self.release_observability = release if isinstance(release, dict) else {}

        status, logout_headers, logout = self.request(opener, "/api/auth/logout", method="POST", data={}, headers=auth_headers)
        clear_cookie = str(logout_headers.get("Set-Cookie") or "")
        self.check(
            "logout_revokes_session_and_cookie",
            status == 200 and logout.get("authenticated") is False and "Max-Age=0" in clear_cookie,
            {"status": status},
        )

        status, _, after_logout = self.request(opener, "/api/me", headers=auth_headers)
        self.check("after_logout_api_rejected", status == 401 and not after_logout.get("authenticated"), {"status": status})

        if daily:
            self.log_patrol()

    def log_patrol(self) -> None:
        log_path = ROOT / "app_server.log"
        if not log_path.exists():
            self.check("structured_log_file_exists", False, {"path": str(log_path)}, critical=False)
            return
        tail = log_path.read_text(encoding="utf-8", errors="replace")[-1_000_000:]
        for marker in (
            '"event_type": "api_request"',
            '"event_type": "auth_event"',
            '"event_type": "scheduler"',
            '"event_type": "ai_event"',
            '"event_type": "task_event"',
        ):
            self.check(f"log_marker_{marker}", marker in tail, {"marker": marker}, critical=False)

    def compute_health_score(self) -> dict:
        if not any(item["name"] == "health_endpoint" for item in self.results):
            preflight_ok = all(item["status"] == "PASS" for item in self.results if item.get("critical"))
            return {
                "score": 100.0 if preflight_ok else 0.0,
                "grade": "green" if preflight_ok else "red",
                "mode": "preflight",
                "components": {"preflight_gate": 1.0 if preflight_ok else 0.0},
                "weights": {"preflight_gate": 100},
                "providerErrors24hTotal": 0,
            }
        release_data = {}
        if isinstance(getattr(self, "release_observability", None), dict):
            release_data = self.release_observability.get("data") or self.release_observability.get("snapshot") or {}
        provider_errors = release_data.get("providerErrors24h") or {}
        provider_error_total = int(provider_errors.get("total", 0) or 0) if isinstance(provider_errors, dict) else 0
        provider_error_rate = max(0.0, 1.0 - min(provider_error_total, 50) / 50.0)
        components = {
            "auth_success_rate": 1.0 if self.result_ok("login_cookie_is_session_scoped") and self.result_ok("same_browser_session_stays_authenticated") else 0.0,
            "logout_success_rate": 1.0 if self.result_ok("logout_revokes_session_and_cookie") and self.result_ok("after_logout_api_rejected") else 0.0,
            "ai_route_correct_rate": 1.0 if self.result_ok("ai_agent_actual_models") else 0.0,
            "provider_error_rate": provider_error_rate,
            "scheduler_success_rate": 1.0 if self.result_ok("cron_status_readable") else 0.0,
            "config_cache_correct_rate": 1.0 if self.result_ok("platform_settings_no_store") else 0.0,
            "file_center_availability": 1.0 if self.result_ok("file_center_list_available") else 0.0,
            "observability_rate": 1.0 if self.result_ok("release_observability_readable") else 0.0,
        }
        score = round(sum(components[key] * weight for key, weight in HEALTH_SCORE_WEIGHTS.items()), 1)
        return {
            "score": score,
            "grade": "green" if score >= 90 else "yellow" if score >= 75 else "red",
            "components": components,
            "weights": HEALTH_SCORE_WEIGHTS,
            "providerErrors24hTotal": provider_error_total,
        }

    def rollback_plan(self, summary: dict) -> dict:
        critical_failed = [item for item in summary.get("results", []) if item.get("critical") and item.get("status") != "PASS"]
        score = float((summary.get("health_score") or {}).get("score", 100) or 0)
        score_block = score < 75
        rollback_required = bool(critical_failed)
        if score_block:
            rollback_required = True
        plan = {
            "rollback_required": rollback_required,
            "recommended_action": "STOP_RELEASE_AND_ROLLBACK_TO_LAST_STABLE" if rollback_required else "CONTINUE",
            "rollback_reasons": [item.get("name") for item in critical_failed] + (["health_score_below_75"] if score_block else []),
            "rollback_executed": False,
            "audit_standard": {
                "must_record": ["change_id", "change_tier", "failed_checks", "health_score", "recommended_action", "operator", "timestamp"],
                "auto_execute_guard": "Requires HERMES_HEALTH_ALLOW_ROLLBACK=1 and HERMES_HEALTH_ROLLBACK_COMMAND.",
            },
        }
        command = os.getenv("HERMES_HEALTH_ROLLBACK_COMMAND", "").strip()
        if rollback_required and command and os.getenv("HERMES_HEALTH_ALLOW_ROLLBACK") == "1":
            proc = subprocess.run(
                shlex.split(command),
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=180,
            )
            plan["rollback_executed"] = proc.returncode == 0
            plan["rollback_command"] = command
            plan["rollback_output_tail"] = proc.stdout[-1200:]
        return plan

    def summary(self) -> dict:
        failed = [item for item in self.results if item["status"] != "PASS"]
        critical_failed = [item for item in failed if item.get("critical")]
        payload = {
            "ok": not critical_failed,
            "base_url": self.base_url,
            "generated_at": int(time.time()),
            "change_id": self.change_id,
            "change_tier": self.change_tier,
            "change_tier_policy": CHANGE_TIERS[self.change_tier],
            "failed_count": len(failed),
            "critical_failed_count": len(critical_failed),
            "results": self.results,
        }
        payload["health_score"] = self.compute_health_score()
        payload["rollback"] = self.rollback_plan(payload)
        return payload


def write_report(payload: dict) -> Path:
    out_dir = ROOT / "output" / "health-gate"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"workbench-health-{time.strftime('%Y%m%d-%H%M%S')}.json"
    payload["report_path"] = str(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    latest = out_dir / "latest.json"
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path = path.with_suffix(".md")
    md_path.write_text(render_markdown_report(payload), encoding="utf-8")
    latest_md = out_dir / "latest.md"
    latest_md.write_text(render_markdown_report(payload), encoding="utf-8")
    payload["markdown_report_path"] = str(md_path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def render_markdown_report(payload: dict) -> str:
    health = payload.get("health_score") or {}
    rollback = payload.get("rollback") or {}
    failed = [item for item in payload.get("results", []) if item.get("status") != "PASS"]
    lines = [
        "# Workbench Health Gate Report",
        "",
        f"- change_id: `{payload.get('change_id', '')}`",
        f"- change_tier: `{payload.get('change_tier', '')}`",
        f"- ok: `{payload.get('ok')}`",
        f"- health_score: `{health.get('score')}` / `{health.get('grade')}`",
        f"- rollback_required: `{rollback.get('rollback_required')}`",
        f"- recommended_action: `{rollback.get('recommended_action')}`",
        f"- critical_failed_count: `{payload.get('critical_failed_count')}`",
        "",
        "## Rollback Audit",
        "",
        f"- rollback_reasons: `{', '.join(str(x) for x in rollback.get('rollback_reasons', []) or []) or 'NONE'}`",
        f"- rollback_executed: `{rollback.get('rollback_executed')}`",
        "- audit_required_fields: `change_id, change_tier, failed_checks, health_score, recommended_action, operator, timestamp`",
        "",
        "## Failed Checks",
        "",
    ]
    if failed:
        for item in failed:
            lines.append(f"- `{item.get('name')}`: `{item.get('status')}` critical=`{item.get('critical')}`")
    else:
        lines.append("- NONE")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes Finance Workbench health gate")
    parser.add_argument("--mode", choices=["preflight", "live", "daily", "all"], default="all")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--change-tier", choices=sorted(CHANGE_TIERS), default=os.getenv("HERMES_CHANGE_TIER", "2"))
    parser.add_argument("--change-id", default=os.getenv("HERMES_CHANGE_ID", ""))
    args = parser.parse_args()

    gate = Gate(args.base_url, verbose=args.verbose, change_tier=args.change_tier, change_id=args.change_id)
    if args.mode in {"preflight", "all"}:
        gate.preflight()
    if args.mode in {"live", "daily", "all"}:
        gate.live(daily=args.mode == "daily")

    payload = gate.summary()
    if args.write_report or args.mode == "daily":
        write_report(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
