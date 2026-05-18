"""Contract tests for server_v2 FastAPI module.

Tests that all modules import cleanly and core business logic is correct,
without requiring a live server.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_imports():
    from server_v2 import config, utils, auth_store, models, deps, providers, workflow
    from server_v2.routers import health, auth, runtime, copilots, orchestrate
    from server_v2.main import app
    print("all imports ok")


def test_config_paths():
    from server_v2.config import ROOT, LOCAL_AUTH_USERS, LOCAL_AUTH_SESSIONS, TASK_QUEUE_PATH
    assert ROOT.exists(), f"ROOT not found: {ROOT}"
    assert LOCAL_AUTH_USERS.exists(), f"users file not found: {LOCAL_AUTH_USERS}"
    print("config paths ok")


def test_utils():
    from server_v2.utils import normalize_email, valid_email, bool_field, safe_slug
    assert normalize_email("  BILL@FastOne.com  ") == "bill@fastone.com"
    assert valid_email("bill@fastonegroup.com")
    assert not valid_email("notanemail")
    assert bool_field({"flag": True}, "flag") is True
    assert bool_field({}, "missing", default=True) is True
    assert safe_slug("hello world!") == "hello_world_"
    print("utils ok")


def test_providers_quality():
    from server_v2.providers import is_low_quality, classify_result, is_provider_failure, compute_quality_score, generate_decision
    assert is_low_quality(None)
    assert is_low_quality("")
    assert is_low_quality("短")
    assert not is_low_quality("This is a substantive legal analysis with multiple paragraphs and real content.")
    assert is_low_quality("工作流启动失败")
    assert is_low_quality("fallback response generated")
    assert classify_result(None) == "empty"
    assert classify_result("fallback response generated") == "fallback"
    assert classify_result("x" * 5) == "low_quality"
    assert classify_result("This is a substantive legal analysis " * 5) == "success"
    assert is_provider_failure("")
    assert is_provider_failure("legal_provider_failed")
    score = compute_quality_score("Executive Analysis " * 200)
    assert score > 50, f"Expected score > 50, got {score}"
    decision = generate_decision({"quality_score": 80})
    assert decision["verdict"] == "approve"
    decision2 = generate_decision({"quality_score": 50})
    assert decision2["verdict"] == "review"
    decision3 = generate_decision({"quality_score": 10})
    assert decision3["verdict"] == "reject"
    print("providers quality checks ok")


def test_workflow_helpers():
    from server_v2.workflow import is_legal_task, build_legal_prompt
    legal_task = {
        "type": "orchestrate",
        "payload": {
            "skill": "trade-finance-instruments#legal",
            "title": "Review SBLC",
            "orchestrate": {"task": "SBLC review", "skill": "contract_review"},
        }
    }
    assert is_legal_task(legal_task), "should detect legal task"
    non_legal = {"type": "workflow", "payload": {"title": "Monthly report"}}
    assert not is_legal_task(non_legal), "should not detect non-legal task"
    prompt = build_legal_prompt(legal_task)
    assert "Executive Legal Conclusion" in prompt
    assert "Enforceability" in prompt
    assert len(prompt) > 200
    print("workflow helpers ok")


def test_auth_store_read_only():
    from server_v2.auth_store import find_local_user, normalize_email
    # Test that we can read the real production users file
    user = find_local_user("bill@fastonegroup.com")
    assert user is not None, "Admin user should exist in production users file"
    assert normalize_email(user.get("email", "")) == "bill@fastonegroup.com"
    assert user.get("role") == "admin"
    print(f"auth_store: found user {user.get('email')}, role={user.get('role')}")


def test_models_pydantic():
    from server_v2.models import LoginRequest, EnqueueTaskRequest, OrchestrateRequest
    req = LoginRequest(email="test@example.com", password="secret")
    assert req.resolved_identifier() == "test@example.com"
    req2 = LoginRequest(identifier="testuser", password="secret")
    assert req2.resolved_identifier() == "testuser"
    enq = EnqueueTaskRequest(type="workflow", title="My task")
    assert enq.type == "workflow"
    orch = OrchestrateRequest(task="Review SBLC", skill="trade-finance-instruments#legal")
    assert orch.task == "Review SBLC"
    print("models ok")


def test_fastapi_app_routes():
    from server_v2.main import app
    routes = {r.path for r in app.routes}
    required = {
        "/api/health",
        "/api/auth/login",
        "/api/auth/logout",
        "/api/auth/session",
        "/api/me",
        "/api/me/permissions",
        "/api/runtime/status",
        "/api/runtime/tasks",
        "/api/runtime/task/{task_id}",
        "/api/runtime/diagnostics",
        "/api/orchestrate",
        "/api/copilots",
        "/api/ai-agents",
    }
    missing = required - routes
    assert not missing, f"Missing routes: {missing}"
    print(f"all {len(required)} required routes present")


if __name__ == "__main__":
    tests = [
        test_imports,
        test_config_paths,
        test_utils,
        test_providers_quality,
        test_workflow_helpers,
        test_auth_store_read_only,
        test_models_pydantic,
        test_fastapi_app_routes,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as exc:
            print(f"FAIL {t.__name__}: {exc}")
            failed += 1
    print(f"\nserver_v2 contract: {passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
