#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import argparse

HERMES_HOME = Path(os.getenv("HERMES_HOME", Path.home() / ".hermes"))
WORKBENCH = HERMES_HOME / "finance-workbench"
ENV_PATH = HERMES_HOME / ".env"
GOOGLE_API_CLI = Path("/Users/billtin/Documents/New project/google-workspace-fix/google_api.py")
PROFILE = "saerc"
PROFILE_LABEL = "SAERC"

SEARCH_WINDOW_HOURS = 30
MAX_MESSAGES = 8
MAX_DETAIL_MESSAGES = 3
MAX_PUSH_ITEMS = 10

PRIORITY_KEYWORDS = {
    "bank": 9,
    "银行": 9,
    "bmo": 10,
    "tdsb": 10,
    "american express": 10,
    "amex": 10,
    "andre": 8,
    "bonnie": 8,
    "payment": 7,
    "statement": 7,
    "account": 6,
    "credit card": 8,
    "banking": 7,
    "school": 6,
    "tuition": 6,
    "invoice": 7,
    "receipt": 5,
    "verification": 7,
    "security alert": 7,
    "wire": 8,
    "loan": 7,
    "facility": 7,
}

ACTION_KEYWORDS = {
    "reply": 5,
    "respond": 5,
    "action required": 7,
    "due": 6,
    "required": 5,
    "urgent": 7,
    "immediately": 7,
    "payment due": 7,
    "verify": 6,
    "review": 4,
    "schedule": 4,
    "meeting": 3,
}


def env_value(*keys: str) -> str:
    if not ENV_PATH.exists():
        return ""
    values: dict[str, str] = {}
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    for key in keys:
        if values.get(key):
            return values[key]
    return ""


def profile_state_path() -> Path:
    return WORKBENCH / "audit" / f"priority-email-state-{PROFILE}.json"


def load_state() -> dict:
    state_path = profile_state_path()
    if not state_path.exists():
        return {"seen": {}, "last_run": 0}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return {"seen": {}, "last_run": 0}


def save_state(state: dict) -> None:
    state_path = profile_state_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def curl_json(method: str, url: str, *, query: dict | None = None, data: dict | None = None, headers: dict[str, str] | None = None) -> dict:
    if query:
        from urllib.parse import urlencode
        url = f"{url}?{urlencode(query, doseq=True)}"
    cmd = [
        "curl",
        "--http1.1",
        "--silent",
        "--show-error",
        "--location",
        "--retry",
        "3",
        "--retry-all-errors",
        "--retry-delay",
        "1",
        "--max-time",
        "20",
        "--request",
        method,
        "--write-out",
        "\n__HTTP_STATUS__:%{http_code}",
    ]
    for key, value in (headers or {}).items():
        cmd.extend(["--header", f"{key}: {value}"])
    if data is not None:
        from urllib.parse import urlencode
        cmd.extend(["--header", "Content-Type: application/x-www-form-urlencoded", "--data", urlencode(data)])
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"curl failed with exit {result.returncode}")
    body, marker, status = result.stdout.rpartition("\n__HTTP_STATUS__:")
    if marker != "\n__HTTP_STATUS__:":
        raise RuntimeError("Missing HTTP status marker")
    if int(status or "0") >= 400:
        raise RuntimeError(body.strip() or f"HTTP {status}")
    return json.loads(body or "{}")


def google_cli_json(*args: str) -> list[dict] | dict:
    cmd = [sys.executable, str(GOOGLE_API_CLI), "--profile", PROFILE, *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "google_api.py failed")
    stdout = result.stdout.strip()
    if not stdout:
        return []
    return json.loads(stdout)


def header_map(payload: dict) -> dict[str, str]:
    return {h["name"]: h["value"] for h in payload.get("payload", {}).get("headers", []) if isinstance(h, dict)}


def extract_message_body(payload: dict) -> str:
    import base64

    body = ""
    node = payload.get("payload", {})
    if node.get("body", {}).get("data"):
        body = base64.urlsafe_b64decode(node["body"]["data"]).decode("utf-8", errors="replace")
    else:
        for part in node.get("parts", []) or []:
            if part.get("mimeType") in {"text/plain", "text/html"} and part.get("body", {}).get("data"):
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
                break
    return clean_text(body)


def search_messages() -> list[dict]:
    day_window = max(1, SEARCH_WINDOW_HOURS // 24 + 1)
    queries = [
        (f"in:inbox is:unread newer_than:{day_window}d", MAX_MESSAGES),
        ('in:inbox newer_than:7d (bank OR bmo OR "american express" OR tdsb OR andre OR bonnie OR 银行 OR payment OR statement OR account)', 4),
    ]
    messages: list[dict] = []
    seen: set[str] = set()
    for query, limit in queries:
        try:
            batch = google_cli_json("gmail", "search", query, "--max", str(limit))
        except Exception:
            batch = []
        if not isinstance(batch, list):
            batch = []
        for item in batch:
            message_id = str(item.get("id") or "")
            if message_id and message_id not in seen:
                seen.add(message_id)
                messages.append(
                    {
                        "id": message_id,
                        "threadId": item.get("threadId", ""),
                        "from": item.get("from", ""),
                        "to": item.get("to", ""),
                        "subject": item.get("subject", ""),
                        "date": item.get("date", ""),
                        "snippet": item.get("snippet", ""),
                        "labels": item.get("labels", []),
                    }
                )
            if len(messages) >= MAX_MESSAGES:
                break
        if len(messages) >= MAX_MESSAGES:
            break
    return messages


def get_message(message_id: str) -> dict:
    try:
        payload = google_cli_json("gmail", "get", message_id)
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    return {
        "id": payload.get("id", message_id),
        "threadId": payload.get("threadId", ""),
        "from": payload.get("from", ""),
        "to": payload.get("to", ""),
        "subject": payload.get("subject", ""),
        "date": payload.get("date", ""),
        "snippet": payload.get("snippet", ""),
        "labels": payload.get("labels", []),
        "body": clean_text(payload.get("body", "")),
    }


def parse_date(value: str) -> datetime:
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def clean_text(value: str) -> str:
    text = re.sub(r"\s+", " ", (value or "")).strip()
    return text[:600]


def score_message(item: dict) -> tuple[int, dict[str, list[str]]]:
    haystack = " ".join(
        [
            str(item.get("from") or ""),
            str(item.get("subject") or ""),
            str(item.get("snippet") or ""),
            str(item.get("body") or ""),
        ]
    ).lower()
    score = 0
    reasons: dict[str, list[str]] = defaultdict(list)

    for keyword, weight in PRIORITY_KEYWORDS.items():
        if keyword in haystack:
            score += weight
            reasons["priority"].append(keyword)

    for keyword, weight in ACTION_KEYWORDS.items():
        if keyword in haystack:
            score += weight
            reasons["action"].append(keyword)

    labels = set(item.get("labels") or [])
    if "UNREAD" in labels:
        score += 4
        reasons["meta"].append("unread")
    if "INBOX" in labels:
        score += 2
        reasons["meta"].append("inbox")
    if "CATEGORY_PERSONAL" in labels:
        score += 1
    if "CATEGORY_PROMOTIONS" in labels:
        score -= 4
        reasons["meta"].append("promotion")
    if "CATEGORY_SOCIAL" in labels:
        score -= 3
    if "CATEGORY_FORUMS" in labels:
        score -= 2

    if any(k in haystack for k in ("american express", "bmo", "bank", "银行", "statement", "payment due", "slack account sign in")):
        score += 4
    if "slack account sign in" in haystack or ("new device" in haystack and "sign in" in haystack):
        score += 8
        reasons["priority"].append("security")
    return score, reasons


def importance_band(score: int) -> str:
    if score >= 18:
        return "最高优先级"
    if score >= 12:
        return "今日需要回复"
    if score >= 8:
        return "值得关注"
    return "一般关注"


def build_digest(items: list[dict]) -> str:
    sections = {
        "highest": [],
        "reply": [],
        "finance": [],
        "school": [],
        "other": [],
    }
    for item in items:
        haystack = " ".join([item.get("from", ""), item.get("subject", ""), item.get("snippet", ""), item.get("body", "")]).lower()
        line = (
            f"- [{importance_band(item['score'])}] {item.get('subject') or '(无主题)'}\n"
            f"  发件人: {item.get('from') or '未知'}\n"
            f"  时间: {item.get('date') or '未知'}\n"
            f"  原因: {item.get('why')}\n"
            f"  建议: {item.get('action')}\n"
        )
        if item["score"] >= 18:
            sections["highest"].append(line)
        elif item["score"] >= 12:
            sections["reply"].append(line)
        elif any(k in haystack for k in ("bank", "银行", "bmo", "american express", "amex", "statement", "payment", "account", "credit card")):
            sections["finance"].append(line)
        elif any(k in haystack for k in ("tdsb", "school", "tuition")):
            sections["school"].append(line)
        else:
            sections["other"].append(line)

    out = [
        f"{PROFILE_LABEL} 每日重要邮件总结",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "1. 最高优先级邮件",
        "\n".join(sections["highest"]) or "- 今日暂无最高优先级邮件",
        "",
        "2. 今日需要回复",
        "\n".join(sections["reply"]) or "- 今日暂无明确需要回复的邮件",
        "",
        "3. 金融 / 银行 / 信用卡相关",
        "\n".join(sections["finance"]) or "- 今日暂无高优先金融类邮件",
        "",
        "4. 学校 / 家庭相关",
        "\n".join(sections["school"]) or "- 今日暂无重点学校/家庭邮件",
        "",
        "5. 其他值得关注",
        "\n".join(sections["other"]) or "- 今日暂无其他重点邮件",
        "",
        "6. 建议下一步",
        "- 先处理最高优先级和安全/账户类邮件。",
        "- 对付款、statement、verification、school 类主题优先确认是否需要当天回复。",
        "- 对 promotional/social 邮件保持低优先级，只保留真正相关的通知。",
    ]
    return "\n".join(out).strip()


def summarize_item(item: dict, reasons: dict[str, list[str]]) -> tuple[str, str]:
    subject = clean_text(item.get("subject") or "")
    snippet = clean_text(item.get("snippet") or "")
    sender = clean_text(item.get("from") or "")
    priority = ", ".join(reasons.get("priority", [])[:3]) or "关键词命中"
    why = f"主题/摘要命中 {priority}"
    if "slack" in subject.lower() and "sign in" in subject.lower():
        why = "检测到账户登录提醒，属于安全相关邮件"
        action = "确认是否为本人登录；若异常，立刻修改密码并检查设备"
    elif any(k in f"{subject} {snippet}".lower() for k in ("statement", "payment", "american express", "bmo", "bank", "银行", "account")):
        action = "检查账单、付款或账户状态，必要时当日处理"
    elif any(k in f"{subject} {snippet}".lower() for k in ("tdsb", "school", "tuition")):
        action = "查看学校/家庭事项是否需要回信、缴费或提交资料"
    elif any(k in f"{subject} {snippet}".lower() for k in ("andre", "bonnie")):
        action = "优先查看是否有明确请求、待确认事项或时间安排"
    elif item["score"] >= 12:
        action = "建议当天阅读并决定是否需要回复"
    else:
        action = "可在处理完高优先级事项后再查看"
    if sender and sender not in why:
        why = f"{why}；发件人 {sender}"
    return why, action


def send_telegram(text: str) -> None:
    token = env_value("TELEGRAM_BOT_TOKEN")
    chat_id = env_value("TELEGRAM_HOME_CHANNEL", "TELEGRAM_ALLOWED_USERS")
    if not token or not chat_id:
        return
    target_chat_id = str(chat_id).split(",")[0].strip()
    parts = []
    current = ""
    for line in text.splitlines(keepends=True):
        if len(current) + len(line) > 3500:
            parts.append(current)
            current = line
        else:
            current += line
    if current:
        parts.append(current)
    for part in parts:
        response = curl_json(
            "POST",
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={
                "chat_id": target_chat_id,
                "text": part,
                "disable_web_page_preview": "true",
            },
        )
        if not response.get("ok", False):
            raise RuntimeError(f"Telegram send failed: {response}")


def main() -> int:
    state = load_state()
    seen = state.setdefault("seen", {})
    messages = search_messages()
    if not messages:
        print("No recent messages found.")
        state["last_run"] = int(time.time())
        save_state(state)
        return 0

    prelim: list[dict] = []
    for item in messages:
        merged = dict(item)
        merged["body"] = ""
        merged["date_dt"] = parse_date(merged.get("date") or "")
        score, reasons = score_message(merged)
        merged["score"] = score
        merged["reasons"] = reasons
        merged["why"], merged["action"] = summarize_item(merged, reasons)
        prelim.append(merged)

    prelim.sort(key=lambda x: (x.get("score", 0), x.get("date_dt")), reverse=True)

    enriched: list[dict] = []
    for item in prelim[:MAX_DETAIL_MESSAGES]:
        message_id = str(item.get("id") or "")
        if not message_id:
            continue
        if seen.get(message_id):
            continue
        try:
            full = get_message(message_id)
        except Exception:
            full = {}
        merged = dict(item)
        merged["body"] = clean_text(full.get("body") or "")
        merged["labels"] = full.get("labels") or item.get("labels") or []
        merged["date_dt"] = parse_date(merged.get("date") or "")
        score, reasons = score_message(merged)
        merged["score"] = score
        merged["reasons"] = reasons
        merged["why"], merged["action"] = summarize_item(merged, reasons)
        enriched.append(merged)

    if not enriched:
        enriched = [item for item in prelim if not seen.get(str(item.get("id") or ""))]

    enriched.sort(key=lambda x: (x.get("score", 0), x.get("date_dt")), reverse=True)
    selected = [item for item in enriched if item.get("score", 0) >= 6][:MAX_PUSH_ITEMS]
    if not selected:
        selected = enriched[:3] or prelim[:3]
        if not selected:
            print("No recent messages found for digest.")
            state["last_run"] = int(time.time())
            save_state(state)
            return 0

    digest = build_digest(selected)
    send_telegram(digest)

    now = int(time.time())
    for item in selected:
        if item.get("id"):
            seen[str(item["id"])] = now
    cutoff = now - 14 * 24 * 60 * 60
    state["seen"] = {k: v for k, v in seen.items() if isinstance(v, int) and v >= cutoff}
    state["last_run"] = now
    save_state(state)

    print(digest)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Priority email digest runner")
    parser.add_argument("--profile", default="saerc")
    parser.add_argument("--label", default="")
    args = parser.parse_args()
    PROFILE = (args.profile or "saerc").strip().lower()
    PROFILE_LABEL = (args.label or PROFILE.upper()).strip()
    raise SystemExit(main())
