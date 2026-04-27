# 各 Skill 固定默认路由表（已落地）

说明：以下为 `自动智能（省成本）` 下的固定默认顺序。  
系统按顺序选择第一个“当前可用”的通道与模型。

## 高质量优先（财务 / 法务 / 尽调）
- `uk_hk_financial_contract_counsel`
  1. `chatgpt / gpt-5.4`（或 `gpt-5.4-mini`）
  2. `google-gemini-cli / gemini-3.1-pro-preview`（或 `gemini-3.1-flash-lite-preview`）
  3. `nvidia / minimax-m2.7`
- `financial-analysis`
  1. `chatgpt / gpt-5.4-mini`（或 `gpt-5.4`）
  2. `google-gemini-cli / gemini-3.1-pro-preview`（或 `gemini-3.1-flash-lite-preview`）
  3. `nvidia / minimax-m2.7`
- `financial-report-summary`
  1. `chatgpt / gpt-5.4-mini`（或 `gpt-5.4`）
  2. `google-gemini-cli / gemini-3.1-pro-preview`（或 `gemini-3.1-flash-lite-preview`）
  3. `nvidia / minimax-m2.7`
- `due-diligence-web-research`
  1. `chatgpt / gpt-5.4-mini`（或 `gpt-5.4`）
  2. `google-gemini-cli / gemini-3.1-pro-preview`（或 `gemini-3.1-flash-lite-preview`）
  3. `nvidia / minimax-m2.7`
- `document-review`
  1. `chatgpt / gpt-5.4-mini`（或 `gpt-5.4`）
  2. `google-gemini-cli / gemini-3.1-pro-preview`（或 `gemini-3.1-flash-lite-preview`）
  3. `nvidia / minimax-m2.7`
- `pdf-excel-analysis`
  1. `chatgpt / gpt-5.4-mini`（或 `gpt-5.4`）
  2. `google-gemini-cli / gemini-3.1-pro-preview`（或 `gemini-3.1-flash-lite-preview`）
  3. `nvidia / minimax-m2.7`
- `banking-sblc`, `banking-dlc`, `mckinsey-thinking`
  1. `chatgpt / gpt-5.4-mini`（或 `gpt-5.4`）
  2. `google-gemini-cli / gemini-*`
  3. `nvidia / minimax-m2.7`

## 低成本优先（协作 / 周报 / 文稿）
- `google-workspace`
- `composio-workspace`
- `obsidian-notion`
- `client-follow-up-weekly-update`
- `slack-collaboration`
- `humanizer`
  1. `nvidia / minimax-m2.7`
  2. `lmstudio / (本地首可用模型)`
  3. `chatgpt / gpt-5.4-mini`

## 图像场景
- `free-image-draft`
  1. `chatgpt / gpt-5.4`（或 `gpt-5.4-mini`）
  2. `nvidia / minimax-m2.7`

## 手动路由优先
- 用户在 Route Settings 明确手动选择通道/模型后，系统不覆盖。
- 用户切回 `自动智能（省成本）` 后，重新应用本固定路由表。
