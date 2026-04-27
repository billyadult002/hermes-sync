# Hermes Healthcheck - AI8 Agent Hub

Date: 2026-04-24 Asia/Shanghai

## Scope

- Add a dedicated `AI Agent Hub` page to Hermes.
- Add a separate human-to-AI-agent exchange entry.
- Connect `https://ai8.rcouyi.com/chat` through a controlled, auditable bridge.
- Preserve institutional finance workflow standards: audit, DLP, draft/pending-review status, and memory return.

## Implemented

- Navigation now includes `AI Agent`.
- Hermes Quick Actions now includes `AI Agent`.
- `AI Agent Hub` page supports:
  - AI8 status probe.
  - API-first bridge when `AI8_API_URL` and `AI8_API_KEY` are configured.
  - Task-handoff fallback when no API is configured.
  - Embedded AI8 preview.
  - External open action.
  - Copy-ready AI8 task packet.
  - Save-back to Hermes memory.
- Backend endpoints added:
  - `GET /api/ai-agent/ai8/status`
  - `POST /api/ai-agent/ai8/handoff`
  - `POST /api/ai-agent/memory`
- Audit events added:
  - `ai8_agent_handoff`
  - `ai_agent_memory_save`
- Hermes research memory updated:
  - `memory/home--hermes-research-memory.json`
  - `memory/home--external-ai8-agent.json`

## Acceptance Results

- JavaScript syntax check: passed.
- Python compile check: passed.
- Live service process: running on `127.0.0.1:8765`.
- `GET /console.html`: HTTP 200.
- `GET /api/ai-agent/ai8/status`: HTTP 200, AI8 reachable, title detected as `欧亿AI-8.0 Pro`.
- Unauthenticated handoff POST: HTTP 401, protected as expected.
- Runtime function handoff test: passed, created `handoff_ready` task.
- Runtime memory save test: passed, saved to Hermes memory.

## Current Operational Mode

AI8 API credentials are not configured yet, so Hermes correctly uses:

`task handoff -> AI8 execution -> result paste-back -> Hermes memory/audit`

To enable direct automated API mode later, configure:

- `AI8_API_URL`
- `AI8_API_KEY`

## Design Principle To Preserve

External AI output is not a final institutional conclusion by default. It must enter Hermes as `draft` or `pending_review`, then be adopted, rejected, or routed into project/file/report workflow by a human operator.
