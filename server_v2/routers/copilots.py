"""/api/copilots and /api/ai-agents — static registry for the legal page."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

_AGENTS = [
    {
        "id": "auto",
        "name": "Auto",
        "description": "Automatic provider selection",
        "type": "ai_agent",
        "provider": "auto",
        "model": "",
        "enabled": True,
        "available": True,
        "chatEnabled": True,
        "cooldownSeconds": 0,
        "external": False,
    },
    {
        "id": "chatgpt",
        "name": "ChatGPT",
        "description": "OpenAI ChatGPT via cliproxy",
        "type": "ai_agent",
        "provider": "chatgpt",
        "model": "gpt-5.5",
        "enabled": True,
        "available": True,
        "chatEnabled": True,
        "cooldownSeconds": 0,
        "external": False,
    },
    {
        "id": "gemini",
        "name": "Gemini",
        "description": "Google Gemini",
        "type": "ai_agent",
        "provider": "gemini",
        "model": "gemini-3.1-pro",
        "enabled": True,
        "available": True,
        "chatEnabled": True,
        "cooldownSeconds": 0,
        "external": False,
    },
    {
        "id": "gemini-auth",
        "name": "Gemini Auth",
        "description": "Google Gemini via authenticated proxy",
        "type": "ai_agent",
        "provider": "gemini",
        "model": "gemini-3.1-pro",
        "enabled": True,
        "available": True,
        "chatEnabled": True,
        "cooldownSeconds": 0,
        "external": False,
    },
    {
        "id": "gemini-api",
        "name": "Gemini API",
        "description": "Google Gemini via API key",
        "type": "ai_agent",
        "provider": "gemini",
        "model": "gemini-3.1-pro",
        "enabled": True,
        "available": True,
        "chatEnabled": True,
        "cooldownSeconds": 0,
        "external": False,
    },
]


@router.get("/api/copilots")
async def get_copilots() -> dict:
    return {
        "ok": True,
        "defaultAgent": "auto",
        "currentProvider": "",
        "currentModel": "",
        "agents": _AGENTS,
        "copilots": _AGENTS,
    }


@router.get("/api/ai-agents")
async def get_ai_agents() -> dict:
    return {
        "ok": True,
        "defaultAgent": "auto",
        "currentProvider": "",
        "currentModel": "",
        "agents": _AGENTS,
    }
