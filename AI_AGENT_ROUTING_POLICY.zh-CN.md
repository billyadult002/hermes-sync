# FASTONE Hermes AI Agent 使用策略（复杂度 + Skill 驱动）

## 1. 目标
- 在不牺牲输出质量的前提下，默认选择最省 token 的可用 AI Agent。
- 对高风险任务自动提升模型能力，避免“便宜但不够用”。
- 保留人工可控：用户可在 `Route Settings` 手动指定通道与模型。

## 2. 默认路由原则（Auto Smart）
- 默认进入 `自动智能（省成本）` 模式。
- 系统根据三类信号自动选路：
  - 任务复杂度：输入长度、结构、附件数量、是否含图片。
  - 激活 Skill：按业务风险分层（高风险/中风险/低风险）。
  - 可用通道健康度：只在可用 provider 中选择。

## 3. 复杂度分级
- `simple`：短请求、单一动作、无或少量上下文。
- `medium`：有分析意图或中等上下文（如摘要、比对、初步判断）。
- `complex`：长文本、多附件、图像任务、深度审阅/推理任务。

## 4. Skill 风险分级（核心）
- 高风险（质量优先）：
  - `uk_hk_financial_contract_counsel`
  - `financial-analysis`
  - `financial-report-summary`
  - `due-diligence-web-research`
  - `document-review`
  - `pdf-excel-analysis`
- 低风险（成本优先）：
  - `humanizer`
  - `client-follow-up-weekly-update`
  - `slack-collaboration`
  - `obsidian-notion`
  - `google-workspace`
  - `composio-workspace`
- 其他默认中风险。

## 5. 自动选路矩阵
- 图像任务：优先图像能力模型（例如 `chatgpt/gpt-5.4`）。
- 高风险或复杂任务：优先高质量模型（如 `chatgpt/gpt-5.4-mini`，必要时升至 `gpt-5.4`）。
- 低风险 + simple：优先低成本通道（本地 `lmstudio` → `nvidia/minimax-m2.7` → 轻量云模型）。
- 中等任务：优先 `nvidia/minimax-m2.7` 或 `gpt-5.4-mini`，兼顾成本与质量。

## 6. 用户手动选择优先级
- 用户在 `Route Settings` 手动应用后，系统尊重人工路由，不再自动覆盖。
- 用户可再次选择 `自动智能（省成本）` 回到系统自动选路。

## 7. 额外省 token 方案（已纳入策略）
- 附件与上下文按需注入，避免无关长上下文进入每轮对话。
- 高频低风险任务优先本地/低成本通道，减少高价模型占用。
- 仅在必要场景（高风险/复杂）自动升级到更强模型。

## 8. 运维建议
- 每周抽样核查：低风险任务质量是否稳定、高风险任务是否仍需更强模型。
- 每月调整 Skill 风险分层与模型优先级，跟随业务场景和模型表现变化。
- 发生链路异常时，优先回退至可用稳定通道，保证连续可用。
