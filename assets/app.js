const LANG_ROUTES = {
  zh: {
    console: "console.html",
    legal: "skill-uk-hk-financial-contract-counsel.html",
    skills: "skills-top20.html",
    index: "index.html",
  },
  en: {
    console: "console-en.html",
    legal: "skill-uk-hk-financial-contract-counsel-en.html",
    skills: "skills-top20-en.html",
    index: "index-en.html",
  },
};

const PAGE_KEYS = new Set(["home", "finance", "skills", "legal", "ai-agent", "work-chat", "doc-flow", "workbench", "my-work", "reports", "file-center", "governance-center", "intel-center"]);
const APPROVAL_PLATFORM_OPTIONS = [
  { id: "financial-analysis", page: "finance", zh: "财务分析", en: "Financial Analysis" },
  { id: "uk_hk_financial_contract_counsel", page: "legal", zh: "法律审阅", en: "Legal Review" },
  { id: "work-chat", page: "work-chat", zh: "协作会话", en: "Collaboration" },
  { id: "doc-flow", page: "doc-flow", zh: "文件审阅审批", en: "Document Flow" },
  { id: "reports", page: "reports", zh: "报告中心", en: "Report Center" },
  { id: "file-center", page: "file-center", zh: "公司文件中心", en: "File Center" },
  { id: "composio-workspace", page: "finance", zh: "Composio", en: "Composio" },
  { id: "pdf-excel-analysis", page: "finance", zh: "PDF to Excel 分析", en: "PDF to Excel" },
  { id: "due-diligence-web-research", page: "finance", zh: "尽职调查", en: "Due Diligence" },
  { id: "financial-report-summary", page: "finance", zh: "财报摘要", en: "Earnings Summary" },
  { id: "client-follow-up-weekly-update", page: "finance", zh: "客户跟进", en: "Client Follow-up" },
  { id: "banking-sblc", page: "finance", zh: "SBLC", en: "SBLC" },
];
const THEME_KEY = "fastone-hermes-theme";
const DENSITY_KEY = "fastone-hermes-density";
const CONVERSATION_KEY = "fastone-hermes-conversations-v1";
const CONVERSATION_RETENTION_MS = 3 * 24 * 60 * 60 * 1000;
const CONVERSATION_VISIBLE_COUNT = 10;
const HERMES_HTTP_ORIGIN = "http://127.0.0.1:8765";
const AUTH_SCHEME_KEY = "fastone:auth:scheme";
const AUTH_TOKEN_KEY = "fastone-hermes-session-token";
try {
  localStorage.removeItem(AUTH_TOKEN_KEY);
} catch {}

function installLocalFileFetchBridge() {
  const nativeFetch = window.fetch.bind(window);
  window.fetch = (input, init = {}) => {
    let target = input;
    let bridged = false;
    if (typeof input === "string") {
      if (input.startsWith("/api/")) {
        target = `${HERMES_HTTP_ORIGIN}${input}`;
        bridged = true;
      } else if (location.protocol === "file:" && input.startsWith("./agents/")) {
        target = `${HERMES_HTTP_ORIGIN}/${input.slice(2)}`;
        bridged = true;
      } else if (location.protocol === "file:" && input.startsWith("agents/")) {
        target = `${HERMES_HTTP_ORIGIN}/${input}`;
        bridged = true;
      }
    }
    if (!bridged) return nativeFetch(target, init);
    const nextInit = { ...init, credentials: "include" };
    const headers = new Headers(init.headers || {});
    const token = sessionStorage.getItem(AUTH_TOKEN_KEY) || "";
    if (token && !headers.has("Authorization")) {
      headers.set("Authorization", `Bearer ${token}`);
    }
    nextInit.headers = headers;
    return nativeFetch(target, nextInit);
  };
}

installLocalFileFetchBridge();

const WEATHER_CODE_META = {
  0: { icon: "☀️", zh: "晴", en: "Clear" },
  1: { icon: "🌤️", zh: "大致晴", en: "Mostly clear" },
  2: { icon: "⛅", zh: "局部多云", en: "Partly cloudy" },
  3: { icon: "☁️", zh: "阴", en: "Overcast" },
  45: { icon: "🌫️", zh: "雾", en: "Fog" },
  48: { icon: "🌫️", zh: "冻雾", en: "Rime fog" },
  51: { icon: "🌦️", zh: "毛毛雨", en: "Light drizzle" },
  53: { icon: "🌦️", zh: "毛毛雨", en: "Drizzle" },
  55: { icon: "🌧️", zh: "浓毛毛雨", en: "Dense drizzle" },
  56: { icon: "🌧️", zh: "冻毛毛雨", en: "Freezing drizzle" },
  57: { icon: "🌧️", zh: "强冻毛毛雨", en: "Heavy freezing drizzle" },
  61: { icon: "🌦️", zh: "小雨", en: "Light rain" },
  63: { icon: "🌧️", zh: "中雨", en: "Rain" },
  65: { icon: "🌧️", zh: "大雨", en: "Heavy rain" },
  66: { icon: "🌧️", zh: "冻雨", en: "Freezing rain" },
  67: { icon: "🌧️", zh: "强冻雨", en: "Heavy freezing rain" },
  71: { icon: "🌨️", zh: "小雪", en: "Light snow" },
  73: { icon: "🌨️", zh: "中雪", en: "Snow" },
  75: { icon: "❄️", zh: "大雪", en: "Heavy snow" },
  77: { icon: "❄️", zh: "雪粒", en: "Snow grains" },
  80: { icon: "🌦️", zh: "阵雨", en: "Rain showers" },
  81: { icon: "🌧️", zh: "强阵雨", en: "Heavy showers" },
  82: { icon: "⛈️", zh: "暴雨阵雨", en: "Violent showers" },
  85: { icon: "🌨️", zh: "阵雪", en: "Snow showers" },
  86: { icon: "❄️", zh: "强阵雪", en: "Heavy snow showers" },
  95: { icon: "⛈️", zh: "雷暴", en: "Thunderstorm" },
  96: { icon: "⛈️", zh: "雷暴冰雹", en: "Thunderstorm hail" },
  99: { icon: "⛈️", zh: "强雷暴冰雹", en: "Severe thunderstorm hail" },
};

const SKILL_ICONS = {
  "uk_hk_financial_contract_counsel": "⚖️",
  "financial-analysis": "📊",
  "banking-dlc": "🌐",
  "banking-sblc": "🛡️",
  "mckinsey-thinking": "🧭",
  "document-review": "📄",
  "google-workspace": "📬",
  "composio-workspace": "🧩",
  "obsidian-notion": "🧠",
  humanizer: "✍️",
  "free-image-draft": "🖼️",
  "pdf-excel-analysis": "📑",
  "due-diligence-web-research": "🔎",
  "financial-report-summary": "📘",
  "client-follow-up-weekly-update": "🤝",
  "slack-collaboration": "💬",
  pe_insight_master: "🏦",
  am_reporting_engine: "📈",
};

const PLATFORM_META = {
  "uk_hk_financial_contract_counsel": {
    section: "legal",
    zh: {
      name: "法律工作平台",
      desc: "聚焦 UK/HK 金融合同、授信文件、担保、保函、SBLC / DLC 和跨境融资条款审阅。",
      tags: ["Legal", "UK / HK"],
      threads: [
        ["Clause Review", "梳理交易结构、事件违约、担保安排与保留事项。"],
        ["Notes", "识别担保范围、责任边界、补足义务与追索路径。"],
      ],
      modes: [
        ["legal-review", "Legal Review", "合同结构、风险和修改建议"],
        ["risk-matrix", "Risk Matrix", "输出分级风险矩阵"],
        ["negotiation", "Negotiation", "形成谈判点与保留意见"],
      ],
      templates: [
        ["完整合同审阅", "交易结构、核心条款、主要风险、修改建议、待确认问题", "请使用 uk_hk_financial_contract_counsel 技能审阅这份合同，输出交易结构、核心条款、主要风险、建议修改和待确认问题。"],
        ["担保条款分析", "审阅 guarantee / security package", "请重点分析保证和担保条款，说明责任范围、限制、执行风险和建议修改。"],
      ],
      promptPlaceholder: "请输入法律审阅、合同风险、授信条款、保函问题或业务视角分析需求。",
      welcome: "这里是法律工作中枢，适合处理金融合同、担保、保函和跨境融资结构审阅。",
    },
    en: {
      name: "Legal Workspace",
      desc: "Focused on UK/HK finance documents, guarantees, facility agreements, SBLC / DLC structures, and cross-border financing clauses.",
      tags: ["Legal", "UK / HK"],
      threads: [
        ["Clause Review", "Review transaction structure, default triggers, guarantees, and reserved items."],
        ["Notes", "Track guarantee scope, liability boundaries, top risks, and follow-up questions."],
      ],
      modes: [
        ["legal-review", "Legal Review", "Clause structure, risk flags, and revisions"],
        ["risk-matrix", "Risk Matrix", "Rank legal issues by severity"],
        ["negotiation", "Negotiation", "Generate negotiation points and fallback asks"],
      ],
      templates: [
        ["Full Agreement Review", "Structure, clauses, risks, edits, open issues", "Please review this agreement and return transaction structure, key clauses, major risks, suggested edits, and open questions."],
        ["Guarantee Review", "Review scope, liability, and enforcement", "Please focus on the guarantee and security provisions, explain liability scope, enforcement risk, and suggested revisions."],
      ],
      promptPlaceholder: "Describe the legal review, contract risk, guarantee issue, or financing clause question.",
      welcome: "This is the legal work center for finance documents, guarantees, SBLC / DLC structures, and cross-border financing clauses.",
    },
  },
  "financial-analysis": {
    section: "finance",
    zh: {
      name: "财务分析工作平台",
      desc: "适合处理财报摘要、经营质量、现金流、杠杆结构和授信意见输出。",
      tags: ["Credit", "Finance"],
      threads: [
        ["Clause Review", "识别交叉违约、提前到期、担保结构与核心谈判点。"],
        ["Notes", "形成管理层摘要、关键风险和下一步动作。"],
      ],
      modes: [
        ["credit-review", "Credit Review", "授信与财务风险判断"],
        ["executive-summary", "Executive Summary", "输出管理层摘要"],
        ["ratio-analysis", "Ratio Analysis", "利润、现金流、杠杆与覆盖"],
      ],
      templates: [
        ["管理层摘要", "输出高管摘要与追问问题", "请基于上传财报输出管理层摘要、关键指标变化、主要风险与后续追问问题。"],
        ["授信意见", "从信用视角输出结论", "请从授信角度分析这家公司，输出经营表现、财务承诺、违约触发、担保结构和建议动作。"],
      ],
      promptPlaceholder: "请输入金融分析、授信判断、合同条款风险、保函风险或财务摘要需求。",
      welcome: "这里是金融工作中枢，适合处理财报、授信、贸易金融、SBLC / DLC 及管理层摘要任务。",
    },
    en: {
      name: "Financial Analysis Workspace",
      desc: "Best for earnings summaries, business quality, cash flow, leverage, and credit recommendation work.",
      tags: ["Credit", "Finance"],
      threads: [
        ["Clause Review", "Review financial covenants, cross-defaults, acceleration, and support structure."],
        ["Notes", "Produce management summaries, key risks, and recommended actions."],
      ],
      modes: [
        ["credit-review", "Credit Review", "Credit and financial risk judgment"],
        ["executive-summary", "Executive Summary", "Management-ready summaries"],
        ["ratio-analysis", "Ratio Analysis", "Cash flow, leverage, and coverage"],
      ],
      templates: [
        ["Management Summary", "Executive summary and follow-up questions", "Please produce a management summary, major changes in key metrics, top risks, and follow-up questions from the uploaded financial statements."],
        ["Credit View", "Return a credit-oriented conclusion", "Please analyze this company from a credit perspective and structure the output around performance, commitments, trigger events, support structure, and recommended actions."],
      ],
      promptPlaceholder: "Describe the finance analysis, credit view, facility issue, or trade-finance question.",
      welcome: "This is the finance work center for financial statements, credit judgment, trade finance, and executive summaries.",
    },
  },
  "banking-dlc": {
    section: "finance",
    zh: {
      name: "DLC 工作平台",
      desc: "聚焦跟单信用证条款、单据不符点、执行路径和银行操作建议。",
      tags: ["Trade Finance", "DLC"],
      threads: [
        ["Clause Review", "识别关键条款、单据不符点和银行确认事项。"],
        ["Notes", "输出 discrepancy 解释、补救路径和沟通要点。"],
      ],
      modes: [
        ["discrepancy-review", "Discrepancy Review", "识别不符点和风险"],
        ["clause-review", "Clause Review", "审阅信用证关键条款"],
        ["bank-actions", "Bank Actions", "给出银行侧动作建议"],
      ],
      templates: [
        ["信用证审阅", "识别关键条款与风险", "请审阅这份 DLC，列出关键条款、单据不符点风险、建议修改和银行应确认事项。"],
        ["单据不符点", "重点解释 discrepancy", "请从银行视角梳理本次单据不符点、严重程度、补救路径和沟通建议。"],
      ],
      promptPlaceholder: "请输入信用证条款、不符点、交单或银行侧动作需求。",
      welcome: "这里适合处理跟单信用证、单据不符点、交单条件和银行执行路径。",
    },
    en: {
      name: "DLC Workspace",
      desc: "Review documentary credit wording, discrepancy points, execution paths, and bank-side actions.",
      tags: ["Trade Finance", "DLC"],
      threads: [
        ["Clause Review", "Review core wording, discrepancy risk, and bank checkpoints."],
        ["Notes", "Summarize discrepancy impact, cure path, and communication points."],
      ],
      modes: [
        ["discrepancy-review", "Discrepancy Review", "Identify discrepancy points and risks"],
        ["clause-review", "Clause Review", "Review documentary credit wording"],
        ["bank-actions", "Bank Actions", "Recommend bank-side actions"],
      ],
      templates: [
        ["DLC Review", "Review wording and risk", "Please review this DLC and list key clauses, discrepancy risks, suggested edits, and bank confirmation items."],
        ["Discrepancy Notes", "Explain the discrepancy set", "Please summarize the discrepancies from the bank perspective, rank severity, and propose cure actions."],
      ],
      promptPlaceholder: "Describe the DLC wording, discrepancy set, bank concern, or document-review request.",
      welcome: "Use this workspace for documentary credit wording, discrepancies, presentation sets, and bank-side execution questions.",
    },
  },
  "banking-sblc": {
    section: "finance",
    zh: {
      name: "SBLC 开证人监督平台",
      desc: "面向开证人/开证方的 SBLC 全流程监督与审核，覆盖尽调、SPA、托管、MT799、MT760、费用释放、原件交付、终止与没收控制。",
      tags: ["Trade Finance", "SBLC", "Issuer Control"],
      threads: [
        ["Issuer Control", "按开证人利益审查条件先决、终止权、没收与托管安排。"],
        ["Institution Map", "理清开证机构、开证银行、接证机构、接证银行、支付银行、收益机构的交叉关系。"],
      ],
      modes: [
        ["issuer-supervision", "Issuer Supervision", "开证人全流程监督"],
        ["contract-escrow-review", "Contract / Escrow Review", "SPA 与托管文件审核"],
        ["swift-gate-control", "SWIFT Gate Control", "MT799 / MT760 条件闸口"],
        ["forfeiture-risk", "Forfeiture Risk", "没收、终止与违约证据"],
      ],
      templates: [
        ["开证人全流程监督", "12 步条件闸口与证据审核", "请按开证人视角审阅这项 SBLC 交易，输出角色关系、12 步条件闸口、每一步责任方/证据/风险、开证人批准点、终止权和下一步动作。"],
        ["SPA / Escrow 审核", "合同、托管、没收与费用释放", "请审核 SPA、SBLC 程序和托管安排，列出必须写入合同的条款、条件先决、托管释放条件、没收触发、争议解决和保护开证人的修改建议。"],
        ["SWIFT 执行核查", "MT799 / MT760 / 原件交付", "请检查 MT799、MT760、接证银行确认、费用支票释放和原件交付流程，列出每个 SWIFT 节点的前置条件、时限、证据、异常处理和开证人停止权。"],
      ],
      promptPlaceholder: "请输入 SBLC 开证人监督、SPA/托管审核、接证银行确认、MT799/MT760、费用释放或违约没收问题。",
      welcome: "这里是 SBLC 开证人监督平台。默认从开证人保护角度审查交易结构、机构交叉关系、合同/托管、SWIFT 闸口、费用释放、原件交付和终止/没收证据。",
    },
    en: {
      name: "SBLC Issuer Control Workspace",
      desc: "Issuer-side end-to-end SBLC supervision covering diligence, SPA, escrow, MT799, MT760, fee release, original delivery, termination, and forfeiture controls.",
      tags: ["Trade Finance", "SBLC", "Issuer Control"],
      threads: [
        ["Issuer Control", "Review conditions precedent, termination rights, forfeiture, and escrow from the issuer’s interest."],
        ["Institution Map", "Map issuer, issuing bank, beneficiary, advising bank, receiving bank, paying bank, and escrow relationships."],
      ],
      modes: [
        ["issuer-supervision", "Issuer Supervision", "End-to-end issuer-side supervision"],
        ["contract-escrow-review", "Contract / Escrow Review", "SPA and escrow review"],
        ["swift-gate-control", "SWIFT Gate Control", "MT799 / MT760 gate control"],
        ["forfeiture-risk", "Forfeiture Risk", "Forfeiture, termination, and default evidence"],
      ],
      templates: [
        ["Issuer Supervision", "12-step gate and evidence review", "Review this SBLC transaction from the issuer perspective. Produce the role map, 12-step condition gates, owner/evidence/risk for each step, issuer approval points, termination rights, and next actions."],
        ["SPA / Escrow Review", "Contract, escrow, forfeiture, and fee release", "Review the SPA, SBLC procedure, and escrow arrangements. List mandatory clauses, conditions precedent, escrow release conditions, forfeiture triggers, dispute resolution, and issuer-protective edits."],
        ["SWIFT Execution Check", "MT799 / MT760 / original delivery", "Check the MT799, MT760, receiving-bank acknowledgment, fee-cheque release, and original delivery process. List prerequisites, timelines, evidence, exception handling, and issuer stop rights for each SWIFT node."],
      ],
      promptPlaceholder: "Describe the SBLC issuer control, SPA/escrow review, receiving-bank acknowledgment, MT799/MT760, fee release, or forfeiture issue.",
      welcome: "This is the SBLC Issuer Control Workspace. It defaults to issuer protection across structure, institutional relationships, contract/escrow, SWIFT gates, fee release, original delivery, and termination/forfeiture evidence.",
    },
  },
  "mckinsey-thinking": {
    section: "finance",
    zh: {
      name: "战略分析工作平台",
      desc: "把复杂问题拆成结构化判断，适合做 issue tree、假设驱动分析和高层简报表达。",
      tags: ["Strategy", "MECE"],
      threads: [
        ["Clause Review", "拆解问题结构、假设路径和关键判断。"],
        ["Notes", "输出 CEO 级摘要、风险与建议动作。"],
      ],
      modes: [
        ["issue-tree", "Issue Tree", "MECE 拆解问题"],
        ["hypothesis", "Hypothesis", "假设驱动分析"],
        ["exec-brief", "Executive Brief", "高层摘要和结论"],
      ],
      templates: [
        ["Issue Tree 拆解", "MECE 结构与优先级", "请把这个问题拆成 MECE issue tree，并给出关键假设、优先顺序和高层摘要。"],
        ["CEO Brief", "面向管理层的精炼输出", "请把这个复杂问题整理成 CEO Brief，包括核心判断、三条证据、主要风险和建议动作。"],
      ],
      promptPlaceholder: "请输入战略问题、拆解逻辑、CEO brief 或假设分析需求。",
      welcome: "这里适合处理战略拆解、管理层判断、issue tree 和高层摘要。",
    },
    en: {
      name: "Strategy Workspace",
      desc: "Break complex questions into issue trees, hypotheses, and executive-ready recommendations.",
      tags: ["Strategy", "MECE"],
      threads: [
        ["Clause Review", "Structure the issue tree, key hypotheses, and decision path."],
        ["Notes", "Return a CEO brief, risk view, and recommended actions."],
      ],
      modes: [
        ["issue-tree", "Issue Tree", "MECE problem breakdown"],
        ["hypothesis", "Hypothesis", "Hypothesis-driven analysis"],
        ["exec-brief", "Executive Brief", "Executive summary and recommendation"],
      ],
      templates: [
        ["Issue Tree", "MECE structure and priority", "Please break this problem into a MECE issue tree and add the main hypotheses, priorities, and an executive summary."],
        ["CEO Brief", "Management-ready output", "Please turn this complex issue into a CEO brief with core judgment, three supporting points, key risks, and recommended actions."],
      ],
      promptPlaceholder: "Describe the strategic question, issue tree, CEO brief, or hypothesis path you need.",
      welcome: "Use this workspace for structured strategy thinking, issue trees, hypotheses, and executive-ready output.",
    },
  },
  "document-review": {
    section: "finance",
    zh: {
      name: "文档审阅工作平台",
      desc: "适合 PDF、PPT、会议纪要和多文档对照整理，强调摘要、交叉比对和交付版本输出。",
      tags: ["Document", "Review"],
      threads: [
        ["Clause Review", "提炼重点、差异与待核查事项。"],
        ["Notes", "形成摘要、比对和交付版结论。"],
      ],
      modes: [
        ["summary", "Summary", "摘要与关键点提取"],
        ["comparison", "Comparison", "多文档交叉比对"],
        ["deliverable", "Deliverable", "形成交付版本"],
      ],
      templates: [
        ["多文档摘要", "提炼重点和差异", "请阅读这些文档，输出统一摘要、主要差异、关键风险和建议下一步。"],
        ["版本比对", "对照不同版本", "请对比这些版本，列出核心差异、风险影响和建议保留意见。"],
      ],
      promptPlaceholder: "请输入 PDF、PPT、纪要、多版本比对或摘要整理需求。",
      welcome: "这里适合处理文档摘要、版本差异、会议纪要和交付版整理。",
    },
    en: {
      name: "Document Review Workspace",
      desc: "Best for PDF, PPT, memo, and multi-document comparison work with delivery-ready outputs.",
      tags: ["Document", "Review"],
      threads: [
        ["Clause Review", "Extract key points, differences, and check items."],
        ["Notes", "Turn multiple documents into one summary and delivery view."],
      ],
      modes: [
        ["summary", "Summary", "Extract key points and structure"],
        ["comparison", "Comparison", "Compare multiple documents"],
        ["deliverable", "Deliverable", "Prepare a delivery-ready result"],
      ],
      templates: [
        ["Multi-Doc Summary", "Extract the main points and differences", "Please read these documents and return one summary, the main differences, key risks, and suggested next steps."],
        ["Version Comparison", "Compare different versions", "Please compare these versions and list the core differences, risk impact, and suggested reservations."],
      ],
      promptPlaceholder: "Describe the PDF, slide deck, memo, summary, or version-comparison task.",
      welcome: "Use this workspace for summaries, comparisons, board packs, meeting notes, and delivery-ready document output.",
    },
  },
  "google-workspace": {
    section: "finance",
    zh: {
      name: "Google Workspace 工作平台",
      desc: "已连接 Google 账号，可直接处理邮件整理、会议纪要、Docs / Sheets 协同和后续行动跟进。",
      tags: ["Ops", "Google"],
      threads: [
        ["Meeting Follow-up", "整理纪要、owner、deadline 和待确认事项。"],
        ["Ops Mail Draft", "形成邮件草稿与协同事项追踪。"],
      ],
      modes: [
        ["meeting-followup", "Meeting Follow-up", "会议后续与责任人"],
        ["mail-draft", "Mail Draft", "邮件草拟与整理"],
        ["ops-sync", "Ops Sync", "Docs/Sheets 协同"],
      ],
      templates: [
        ["会议后续", "纪要、owner、deadline", "请把这次会议内容整理成 follow-up，包括 owner、deadline、待确认事项和邮件草稿。"],
        ["邮件草稿", "整理为专业邮件", "请把这些要点整理成专业英文邮件，语气清晰、简洁、可直接发送。"],
      ],
      promptPlaceholder: "请输入会议纪要、邮件草稿、Docs/Sheets 协同或后续跟进需求。",
      welcome: "Google Workspace 已连接。这里适合直接推进会议跟进、邮件整理、Google Docs / Sheets 协同和运营同步事项。",
    },
    en: {
      name: "Google Workspace",
      desc: "Google account connected for meeting follow-up, mail drafting, Docs and Sheets coordination, and operating sync.",
      tags: ["Ops", "Google"],
      threads: [
        ["Meeting Follow-up", "Organize owners, deadlines, and follow-up items."],
        ["Ops Mail Draft", "Turn rough notes into drafts and sync tasks."],
      ],
      modes: [
        ["meeting-followup", "Meeting Follow-up", "Owners, deadlines, and follow-ups"],
        ["mail-draft", "Mail Draft", "Draft a clear email"],
        ["ops-sync", "Ops Sync", "Docs / Sheets coordination"],
      ],
      templates: [
        ["Meeting Follow-up", "Minutes, owners, deadlines", "Please turn this meeting into a follow-up pack with owners, deadlines, open questions, and a draft email."],
        ["Mail Draft", "Turn notes into a clean message", "Please turn these notes into a concise, professional English email that can be sent directly."],
      ],
      promptPlaceholder: "Describe the meeting follow-up, email draft, Docs / Sheets sync, or ops task.",
      welcome: "Google Workspace is connected. Use this workspace for meetings, email drafts, Docs and Sheets coordination, and operating follow-up work.",
    },
  },
  "composio-workspace": {
    section: "finance",
    zh: {
      name: "Composio 工作平台",
      desc: "沿用 Google Workspace 的双账号工作逻辑，适合统一处理邮件协同、日程编排、文档提纲和工作台自动化动作。",
      tags: ["Ops", "Composio"],
      threads: [
        ["Meeting Follow-up", "按当前账号整理纪要、owner、deadline 和待确认事项。"],
        ["Ops Mail Draft", "按当前账号整理邮件草稿、日程和协同动作。"],
      ],
      modes: [
        ["meeting-followup", "Meeting Follow-up", "会议后续与责任人"],
        ["mail-draft", "Mail Draft", "邮件草拟与整理"],
        ["ops-sync", "Ops Sync", "跨应用协同动作"],
      ],
      templates: [
        ["会议后续", "纪要、owner、deadline", "请按当前 Composio 账号上下文整理这次会议 follow-up，包括 owner、deadline、待确认事项和邮件草稿。"],
        ["工作流草稿", "邮件、日程、Docs、Sheets 联动", "请按当前 Composio 账号上下文输出邮件草稿、会议安排建议、文档提纲和表格跟踪结构。"],
      ],
      promptPlaceholder: "请输入会议后续、邮件整理、日程计划、文档提纲或跨应用协同需求。",
      welcome: "Composio 工作平台已按双账号架构接入。这里适合统一处理会议后续、邮件整理、日程安排、Docs / Sheets 提纲和工作流动作。",
    },
    en: {
      name: "Composio Workspace",
      desc: "Built on the same dual-account logic as Google Workspace for mail coordination, calendar planning, document outlines, and cross-workspace operating actions.",
      tags: ["Ops", "Composio"],
      threads: [
        ["Meeting Follow-up", "Organize owners, deadlines, and open items for the active account."],
        ["Ops Mail Draft", "Draft mail, calendar plans, and operating actions for the active account."],
      ],
      modes: [
        ["meeting-followup", "Meeting Follow-up", "Owners, deadlines, and follow-ups"],
        ["mail-draft", "Mail Draft", "Draft and clean messages"],
        ["ops-sync", "Ops Sync", "Cross-app operating actions"],
      ],
      templates: [
        ["Meeting Follow-up", "Minutes, owners, deadlines", "Please use the active Composio account context to turn this meeting into a follow-up pack with owners, deadlines, open questions, and a draft email."],
        ["Workflow Draft", "Mail, calendar, Docs, and Sheets", "Please use the active Composio account context to produce an email draft, scheduling suggestions, a document outline, and a tracker-table structure."],
      ],
      promptPlaceholder: "Describe the meeting follow-up, email drafting, calendar planning, document outline, or cross-app operating task.",
      welcome: "Composio Workspace is set up with a dual-account structure. Use it for meetings, email cleanup, calendar planning, Docs / Sheets outlines, and operating actions.",
    },
  },
  "obsidian-notion": {
    section: "finance",
    zh: {
      name: "Obsidian / Notion 工作平台",
      desc: "Notion integration 已配置；当前机器到 Notion API 的 TLS 校验仍待打通，现阶段可先作为知识整理工作台使用。",
      tags: ["Knowledge", "Notes"],
      threads: [
        ["Knowledge Map", "重组页面结构、目录和链接关系。"],
        ["Decision Log", "形成 decision log 和知识索引。"],
      ],
      modes: [
        ["knowledge-map", "Knowledge Map", "结构化知识图谱"],
        ["page-rewrite", "Page Rewrite", "页面重写与整理"],
        ["decision-log", "Decision Log", "决策记录与索引"],
      ],
      templates: [
        ["知识库重构", "重组目录和链接关系", "请根据这些笔记和页面，重构知识库结构、关联关系和索引方式。"],
        ["决策记录", "整理为 decision log", "请把这些讨论整理成 decision log，包括背景、选项、结论、原因和待行动项。"],
      ],
      promptPlaceholder: "请输入页面重构、知识库整理、笔记梳理或决策记录需求。",
      welcome: "这里已经可以处理知识库整理、页面重写、笔记关联和决策索引。Notion integration 已配置，但当前机器到 Notion API 的 TLS 链路仍待打通后，才能直接读写页面或数据库。",
    },
    en: {
      name: "Obsidian / Notion Workspace",
      desc: "The Notion integration key is configured, but this machine still needs a working TLS path to the Notion API before direct read/write can be verified.",
      tags: ["Knowledge", "Notes"],
      threads: [
        ["Knowledge Map", "Restructure pages, hierarchies, and links."],
        ["Decision Log", "Turn raw discussion into a decision log and index."],
      ],
      modes: [
        ["knowledge-map", "Knowledge Map", "Map knowledge structure and links"],
        ["page-rewrite", "Page Rewrite", "Rewrite and clean a page"],
        ["decision-log", "Decision Log", "Turn notes into a decision log"],
      ],
      templates: [
        ["Knowledge Base Refactor", "Restructure hierarchy and links", "Please use these notes and pages to restructure the knowledge base, hierarchy, links, and indexing logic."],
        ["Decision Log", "Turn discussion into a record", "Please turn this discussion into a decision log with context, options, conclusion, rationale, and follow-up actions."],
      ],
      promptPlaceholder: "Describe the knowledge-base refactor, page rewrite, note cleanup, or decision-log task.",
      welcome: "Use this workspace for knowledge-base refactoring, page rewrites, linked notes, and decision records. The Notion integration key is configured, but direct page or database access still needs the local TLS path to the Notion API to work.",
    },
  },
  humanizer: {
    section: "finance",
    zh: {
      name: "Humanizer 工作平台",
      desc: "适合自然化改写、语气优化、双语润色和更像真人表达的输出。",
      tags: ["Language", "Tone"],
      threads: [
        ["Tone Upgrade", "识别表达问题、语气偏差和冗余结构。"],
        ["Natural Rewrite", "输出更自然、更稳、更像真人的版本。"],
      ],
      modes: [
        ["tone-upgrade", "Tone Upgrade", "语气升级与自然化"],
        ["bilingual", "Bilingual Polish", "中英文双语润色"],
        ["email-polish", "Email Polish", "邮件口吻优化"],
      ],
      templates: [
        ["自然化改写", "更像真人表达", "请把下面内容改写得更自然、更像真人表达，同时保持原意准确。"],
        ["双语润色", "中英文对应优化", "请对这段中英文内容做双语润色，保持专业、自然、易读。"],
      ],
      promptPlaceholder: "请输入自然化改写、语气优化、双语润色或邮件口吻需求。",
      welcome: "这里适合处理语气优化、自然化改写、双语润色和邮件口吻提升，让成稿更像真人表达。",
    },
    en: {
      name: "Humanizer Workspace",
      desc: "Rewrite drafts into more natural, human, and polished language with bilingual support.",
      tags: ["Language", "Tone"],
      threads: [
        ["Tone Upgrade", "Spot tone issues, awkward phrasing, and overly mechanical language."],
        ["Natural Rewrite", "Return a more natural and human-sounding version."],
      ],
      modes: [
        ["tone-upgrade", "Tone Upgrade", "Upgrade tone and naturalness"],
        ["bilingual", "Bilingual Polish", "Polish Chinese and English together"],
        ["email-polish", "Email Polish", "Improve email tone"],
      ],
      templates: [
        ["Natural Rewrite", "Make it sound more human", "Please rewrite the following content so it sounds more natural and human while preserving the original meaning."],
        ["Bilingual Polish", "Improve both languages together", "Please polish this Chinese and English text together so it remains accurate, professional, natural, and easy to read."],
      ],
      promptPlaceholder: "Describe the rewrite, tone adjustment, bilingual polish, or email-tone task.",
      welcome: "Use this workspace for natural rewrites, tone upgrades, bilingual polishing, and email refinement that feels more human.",
    },
  },
  "free-image-draft": {
    section: "finance",
    zh: {
      name: "Image Draft 工作平台",
      desc: "适合快速生成免费视觉草稿、海报方向图、封面概念和提案配图预览。",
      tags: ["Image", "Draft"],
      threads: [
        ["Visual Draft", "快速出方向图、构图和风格说明。"],
        ["Poster Direction", "整理海报、封面和主视觉草稿。"],
      ],
      modes: [
        ["visual-draft", "Visual Draft", "快速视觉草稿"],
        ["poster", "Poster Direction", "海报和封面方向"],
        ["campaign-visual", "Campaign Visual", "活动主视觉草稿"],
      ],
      templates: [
        ["视觉草稿", "直接生成方向图", "请基于这个主题输出一段适合生成免费视觉草稿的图片提示词，并补充构图、材质、色调和应用场景建议。"],
        ["海报方向", "封面和海报", "请把这个主题整理成适合海报或封面的视觉提示词，并说明版式、色彩和质感建议。"],
      ],
      promptPlaceholder: "请输入海报方向、封面概念、活动视觉或图片草稿需求。",
      welcome: "这里专门用于免费图片草稿生成，适合先快速拿到视觉方向图，再继续打磨提案或主视觉。",
    },
    en: {
      name: "Image Draft Workspace",
      desc: "Generate free visual drafts, poster directions, cover concepts, and pitch-image previews quickly.",
      tags: ["Image", "Draft"],
      threads: [
        ["Visual Draft", "Generate draft visuals, composition ideas, and style notes."],
        ["Poster Direction", "Shape poster, cover, and hero-image concepts."],
      ],
      modes: [
        ["visual-draft", "Visual Draft", "Fast visual drafts"],
        ["poster", "Poster Direction", "Poster and cover concepts"],
        ["campaign-visual", "Campaign Visual", "Campaign key visual drafts"],
      ],
      templates: [
        ["Visual Draft", "Generate a draft image prompt", "Please turn this theme into a free image-draft prompt and add composition, texture, color, and usage guidance."],
        ["Poster Direction", "Poster and cover concept", "Please turn this topic into a poster or cover visual prompt and explain layout, color, and texture suggestions."],
      ],
      promptPlaceholder: "Describe the poster direction, cover concept, campaign visual, or draft image you want.",
      welcome: "This workspace is dedicated to free image drafts so you can get a visual direction quickly before refining a final key visual.",
    },
  },
  "pdf-excel-analysis": {
    section: "finance",
    zh: {
      name: "PDF to Excel 分析工作平台",
      desc: "适合把 PDF 财报、银行资料和扫描表格整理成可直接进入 Excel 的分析底稿。",
      tags: ["PDF", "Excel"],
      threads: [
        ["Table Extract", "提取 PDF 表格、字段和期间结构。"],
        ["Workpaper Build", "形成可直接进入 Excel 的分析底稿。"],
      ],
      modes: [
        ["table-extract", "Table Extract", "提取表格与字段"],
        ["workpaper", "Workpaper", "形成分析底稿"],
        ["qa-flags", "QA Flags", "标记异常和缺口"],
      ],
      templates: [
        ["表格提取", "抽取 PDF 表格", "请从这些 PDF 中提取关键财务表格，按期间、单位和项目名称整理成适合 Excel 分析底稿的结构。"],
        ["分析底稿", "工作底稿与质量标记", "请把这些 PDF 财务资料整理成 Excel 分析底稿格式，保留原始单位、期间标签，并标记数据质量问题或缺口。"],
      ],
      promptPlaceholder: "请输入 PDF 表格提取、Excel 底稿、扫描页整理或数据质量检查需求。",
      welcome: "这里适合把 PDF、扫描页和财务表格整理成 Excel 可用的分析底稿，并清楚保留单位、期间和质量标记。",
    },
    en: {
      name: "PDF to Excel Analysis Workspace",
      desc: "Turn PDF statements, bank materials, and scanned tables into Excel-ready analysis workpapers.",
      tags: ["PDF", "Excel"],
      threads: [
        ["Table Extract", "Extract tables, fields, and reporting periods from PDFs."],
        ["Workpaper Build", "Build an Excel-ready analysis workpaper."],
      ],
      modes: [
        ["table-extract", "Table Extract", "Extract tables and fields"],
        ["workpaper", "Workpaper", "Build an analysis workpaper"],
        ["qa-flags", "QA Flags", "Mark anomalies and gaps"],
      ],
      templates: [
        ["Table Extract", "Extract key tables from PDFs", "Please extract the key financial tables from these PDFs and structure them for an Excel analysis workpaper with periods, units, and line items preserved."],
        ["Analysis Workpaper", "Workpaper with QA flags", "Please turn these PDF financial materials into an Excel-ready analysis workpaper, preserve original units and period labels, and mark any quality issues or gaps."],
      ],
      promptPlaceholder: "Describe the PDF table extraction, Excel workpaper, scanned-page cleanup, or data QA task.",
      welcome: "Use this workspace to turn PDFs, scanned pages, and financial tables into Excel-ready analysis workpapers with clear units, periods, and QA flags.",
    },
  },
  "due-diligence-web-research": {
    section: "finance",
    zh: {
      name: "尽职调查工作平台",
      desc: "适合对公司、个人、项目主体、客户和供应商做公开信息尽调与风险排查。",
      tags: ["DD", "Risk"],
      threads: [
        ["Entity Check", "主体背景、业务结构和公开信息核查。"],
        ["Risk Screen", "红旗事项、监管与诉讼风险排查。"],
      ],
      modes: [
        ["entity-check", "Entity Check", "主体与背景核查"],
        ["risk-screen", "Risk Screen", "风险排查与红旗"],
        ["source-pack", "Source Pack", "来源与结论整理"],
      ],
      templates: [
        ["主体尽调", "背景、业务和风险", "请对这个主体做公开信息尽调，整理基本情况、业务概况、公开风险、潜在红旗和来源链接。"],
        ["交易对手排查", "风险和可信度", "请从交易对手尽调角度，输出主体背景、异常信号、诉讼/监管风险、可信度判断和建议下一步。"],
      ],
      promptPlaceholder: "请输入主体尽调、背景核查、风险排查或来源整理需求。",
      welcome: "这里适合处理公司、个人、客户、供应商和项目主体的公开信息尽调，帮助你更快看到红旗和可信度判断。",
    },
    en: {
      name: "Due Diligence Workspace",
      desc: "Run public-information diligence and risk screens on companies, individuals, counterparties, projects, and suppliers.",
      tags: ["DD", "Risk"],
      threads: [
        ["Entity Check", "Review background, business structure, and public information."],
        ["Risk Screen", "Screen for red flags, regulatory, and litigation risk."],
      ],
      modes: [
        ["entity-check", "Entity Check", "Entity and background review"],
        ["risk-screen", "Risk Screen", "Risk screen and red flags"],
        ["source-pack", "Source Pack", "Organize sources and conclusions"],
      ],
      templates: [
        ["Entity Diligence", "Background, business, and risks", "Please conduct public-information diligence on this entity and summarize the basic profile, business overview, public risks, red flags, and source links."],
        ["Counterparty Screen", "Risk and credibility", "Please assess this counterparty from a diligence perspective and return the background, abnormal signals, litigation or regulatory risk, credibility assessment, and next-step suggestions."],
      ],
      promptPlaceholder: "Describe the entity diligence, background check, risk screen, or source-pack task.",
      welcome: "Use this workspace for public-information diligence on companies, individuals, suppliers, clients, and project entities, with clear sources and risk signals.",
    },
  },
  "financial-report-summary": {
    section: "finance",
    zh: {
      name: "财报摘要工作平台",
      desc: "适合把财报、业绩公告和投资者材料整理成高管摘要、亮点、风险和追问问题。",
      tags: ["Earnings", "Summary"],
      threads: [
        ["Executive Pack", "财报高管摘要、亮点与结论。"],
        ["Risk Highlights", "风险提示、管理层信号和后续追问。"],
      ],
      modes: [
        ["executive-pack", "Executive Pack", "高管摘要与结论"],
        ["risk-highlights", "Risk Highlights", "风险和关注点"],
        ["follow-up", "Follow-up Questions", "追问问题与行动项"],
      ],
      templates: [
        ["高管摘要", "亮点、风险、结论", "请把这份财报整理成高管摘要，包括核心指标、经营亮点、风险提示、管理层信号和一句结论。"],
        ["投资者摘要", "投资者材料精简版", "请把这些业绩材料压缩成投资者可读摘要，突出增长、利润、现金流、指引和关键追问问题。"],
      ],
      promptPlaceholder: "请输入财报摘要、业绩公告、投资者材料或追问问题整理需求。",
      welcome: "这里适合把财报和业绩材料压缩成高管或投资者可读摘要，帮助你快速抓住亮点、风险和后续追问。",
    },
    en: {
      name: "Financial Report Summary Workspace",
      desc: "Turn earnings reports, announcements, and investor materials into executive summaries, highlights, risks, and follow-up questions.",
      tags: ["Earnings", "Summary"],
      threads: [
        ["Executive Pack", "Executive summary, highlights, and conclusion."],
        ["Risk Highlights", "Risk signals, management cues, and follow-up questions."],
      ],
      modes: [
        ["executive-pack", "Executive Pack", "Executive summary and conclusion"],
        ["risk-highlights", "Risk Highlights", "Risks and watchpoints"],
        ["follow-up", "Follow-up Questions", "Questions and action items"],
      ],
      templates: [
        ["Executive Summary", "Highlights, risks, and conclusion", "Please turn this financial report into an executive summary with the key metrics, operating highlights, risk signals, management cues, and a one-line conclusion."],
        ["Investor Summary", "Condensed investor-ready version", "Please compress these earnings materials into an investor-readable summary focused on growth, profitability, cash flow, guidance, and key follow-up questions."],
      ],
      promptPlaceholder: "Describe the earnings summary, announcement review, investor-material digest, or follow-up question task.",
      welcome: "Use this workspace to compress earnings and investor materials into executive or investor-ready summaries with clear highlights, risks, and follow-up questions.",
    },
  },
  "client-follow-up-weekly-update": {
    section: "finance",
    zh: {
      name: "客户跟进工作平台",
      desc: "适合把邮件、会议纪要、聊天记录和行动项整理成客户跟进报告、周报和下一步安排。",
      tags: ["Client", "Follow-up"],
      threads: [
        ["Follow-up Report", "客户进展、风险和下一步整理。"],
        ["Weekly Update", "客户周报、待办和 owner 安排。"],
      ],
      modes: [
        ["follow-up", "Follow-up Report", "客户跟进报告"],
        ["weekly-update", "Weekly Update", "客户周报"],
        ["next-steps", "Next Steps", "下一步动作和 owner"],
      ],
      templates: [
        ["客户跟进", "进展、风险、下一步", "请把这些邮件、纪要和聊天内容整理成客户跟进报告，包括进展、风险、关键信号、下一步和内部责任建议。"],
        ["客户周报", "本周进展与待办", "请把这周与客户相关的事项整理成客户周报，突出重要进展、待确认问题、风险和下周动作。"],
      ],
      promptPlaceholder: "请输入客户跟进、周报、会议纪要整理或下一步安排需求。",
      welcome: "这里适合把散落在邮件、纪要和聊天里的客户事项整理成清楚的跟进报告、周报和 owner 计划。",
    },
    en: {
      name: "Client Follow-up Workspace",
      desc: "Turn emails, meeting notes, chats, and action items into client follow-up reports, weekly updates, and next-step plans.",
      tags: ["Client", "Follow-up"],
      threads: [
        ["Follow-up Report", "Client progress, risks, and next steps."],
        ["Weekly Update", "Client weekly update, open items, and owners."],
      ],
      modes: [
        ["follow-up", "Follow-up Report", "Client follow-up report"],
        ["weekly-update", "Weekly Update", "Client weekly update"],
        ["next-steps", "Next Steps", "Next actions and owners"],
      ],
      templates: [
        ["Client Follow-up", "Progress, risk, next steps", "Please turn these emails, notes, and chats into a client follow-up report with progress, risks, key signals, next steps, and internal ownership suggestions."],
        ["Weekly Update", "This week and next week", "Please turn this week's client-related materials into a weekly update focused on major progress, open questions, risks, and next week's actions."],
      ],
      promptPlaceholder: "Describe the client follow-up, weekly update, meeting-note digest, or next-step planning task.",
      welcome: "Use this workspace to turn scattered emails, notes, and chats into clear client follow-up reports, weekly updates, and owner-aligned next steps.",
    },
  },
  "slack-collaboration": {
    section: "finance",
    zh: {
      name: "Slack 协作工作平台",
      desc: "已连接 Slack workspace，适合整理频道摘要、待回复事项、通知分级和团队协作更新。",
      tags: ["Slack", "Team"],
      threads: [
        ["Channel Summary", "频道重点、待办和责任人整理。"],
        ["Reply Draft", "待回复消息和可直接发送的草稿。"],
      ],
      modes: [
        ["channel-summary", "Channel Summary", "频道摘要"],
        ["reply-draft", "Reply Draft", "待回复整理"],
        ["daily-digest", "Daily Digest", "日更汇总"],
      ],
      templates: [
        ["频道摘要", "重点与待办", "请把这个 Slack 频道的讨论整理成摘要，突出重要信息、待办事项、负责人和截止时间。"],
        ["回复草稿", "需要回复的内容", "请整理这些 Slack 消息里需要回复的内容，并输出简洁、专业的回复草稿。"],
      ],
      promptPlaceholder: "请输入频道摘要、待回复整理、Slack 日报或团队更新需求。",
      welcome: "Slack connector 已连接。这里适合处理频道摘要、待回复事项、协作更新和团队日更，让协同信息更容易落地。",
    },
    en: {
      name: "Slack Collaboration Workspace",
      desc: "Slack workspace connected for channel summaries, reply-needed items, notification triage, and collaboration updates.",
      tags: ["Slack", "Team"],
      threads: [
        ["Channel Summary", "Channel highlights, open items, and owners."],
        ["Reply Draft", "Messages that need a reply and send-ready drafts."],
      ],
      modes: [
        ["channel-summary", "Channel Summary", "Slack channel summary"],
        ["reply-draft", "Reply Draft", "Reply-needed organization"],
        ["daily-digest", "Daily Digest", "Daily digest"],
      ],
      templates: [
        ["Channel Summary", "Highlights and open items", "Please summarize this Slack channel and highlight the important information, open items, owners, and deadlines."],
        ["Reply Draft", "Messages that need replies", "Please identify the Slack messages that need replies and draft concise, professional responses."],
      ],
      promptPlaceholder: "Describe the channel summary, reply draft, Slack digest, or collaboration update you want.",
      welcome: "The Slack connector is now connected. Use this workspace for channel summaries, reply-needed items, collaboration updates, and daily digests that keep the team aligned.",
    },
  },
  pe_insight_master: {
    section: "finance",
    zh: {
      name: "PE 穿透尽调工作平台",
      desc: "聚焦 PE / VC 交易、股权结构、回购条款、tag-along / drag-along 和红队式风险穿透分析。",
      tags: ["PE", "Due Diligence"],
      threads: [
        ["Clause Review", "穿透股权结构、条款边界和触发机制。"],
        ["Notes", "输出三大致命缺陷、回购机制和对赌风险。"],
      ],
      modes: [
        ["deep-dd", "Deep DD", "深度尽调与红旗识别"],
        ["shareholder", "SPA/SHA", "股东协议与回购条款"],
        ["red-team", "Red Team", "输出三大致命缺陷"],
      ],
      templates: [
        ["PE 风险穿透", "三大致命缺陷与结构风险", "请从 PE 尽调视角分析本项目，输出交易结构、关键红旗、回购 / tag-along 风险、三大致命缺陷及建议动作。"],
      ],
      promptPlaceholder: "请输入 PE / VC 尽调、SPA / SHA、回购条款或红队风险分析需求。",
      welcome: "这里适合处理 PE / VC 穿透尽调、股权条款、回购机制与红队式结构风险判断。",
    },
    en: {
      name: "PE Insight Master",
      desc: "Built for PE / VC diligence, shareholding structures, repurchase clauses, tag/drag rights, and red-team risk reviews.",
      tags: ["PE", "Diligence"],
      threads: [
        ["Clause Review", "Break down ownership structure, trigger mechanics, and legal boundaries."],
        ["Notes", "Return the three fatal flaws, repurchase mechanics, and downside exposure."],
      ],
      modes: [
        ["deep-dd", "Deep DD", "Deep diligence and structural red flags"],
        ["shareholder", "SPA/SHA", "Shareholder and repurchase clauses"],
        ["red-team", "Red Team", "Return the three fatal flaws"],
      ],
      templates: [
        ["PE Diligence Review", "Fatal flaws and structural risks", "Please review this opportunity from a PE diligence perspective and return the transaction structure, key red flags, repurchase / tag-along exposure, the three fatal flaws, and recommended actions."],
      ],
      promptPlaceholder: "Describe the PE / VC diligence, SPA / SHA clause, repurchase issue, or red-team review.",
      welcome: "Use this workspace for PE / VC diligence, shareholder clauses, repurchase mechanics, and red-team structural risk analysis.",
    },
  },
  am_reporting_engine: {
    section: "finance",
    zh: {
      name: "资管报告助手",
      desc: "面向资管月报、双语投资者报告、alpha / beta 归因、GIPS 口径和法律免责声明整合。",
      tags: ["AM", "Reporting"],
      threads: [
        ["Clause Review", "抽取净值、归因、风险与合规披露结构。"],
        ["Notes", "形成双语摘要、图表要点和免责声明。"],
      ],
      modes: [
        ["monthly", "Monthly Report", "月报结构与摘要"],
        ["attribution", "Attribution", "alpha / beta 归因"],
        ["bilingual", "Bilingual", "双语投资者报告"],
      ],
      templates: [
        ["资管月报", "生成双语月报骨架", "请根据这些投资资料生成资管月报，包含业绩摘要、alpha / beta 归因、风险提示、图表要点和法律免责声明。"],
      ],
      promptPlaceholder: "请输入资管月报、归因分析、双语报告或免责声明整合需求。",
      welcome: "这里适合处理资管月报、业绩归因、投资者沟通和合规免责声明整合。",
    },
    en: {
      name: "AM Reporting Engine",
      desc: "Built for asset-management monthly reporting, bilingual investor packs, alpha / beta attribution, GIPS framing, and legal disclaimers.",
      tags: ["AM", "Reporting"],
      threads: [
        ["Clause Review", "Extract NAV, attribution, risk framing, and disclosure structure."],
        ["Notes", "Return a bilingual summary, chart cues, and legal disclaimers."],
      ],
      modes: [
        ["monthly", "Monthly Report", "Monthly report structure and summary"],
        ["attribution", "Attribution", "Alpha / beta attribution"],
        ["bilingual", "Bilingual", "Bilingual investor reporting"],
      ],
      templates: [
        ["Monthly Reporting Pack", "Generate a bilingual report frame", "Please turn these investment materials into an asset-management monthly report with performance summary, alpha / beta attribution, risk notes, chart cues, and legal disclaimers."],
      ],
      promptPlaceholder: "Describe the monthly report, attribution view, bilingual investor pack, or disclaimer task.",
      welcome: "Use this workspace for AM monthly reporting, attribution, bilingual investor materials, and compliance-ready disclosure output.",
    },
  },
};

const QUICK_ACTION_GROUPS = {
  legal: {
    zh: [
      ["条款风险矩阵", "按严重性输出红黄绿风险、建议修改和待确认问题。", "请基于当前材料输出条款风险矩阵，按高/中/低严重性列出条款位置、风险原因、业务影响、建议修改和待确认问题。"],
      ["谈判清单", "形成可直接用于谈判的保留点和 fallback。", "请把当前合同或条款整理成谈判清单，包括必须坚持、可让步、可交换条件、fallback wording 和对方可能反驳。"],
      ["担保与追索", "检查 guarantee / security package 和执行路径。", "请重点审阅担保、保证、抵押/质押、追索路径和执行障碍，输出银行或债权人保护建议。"],
      ["先决条件检查", "梳理 CP、交割条件、文件缺口和责任人。", "请整理先决条件清单，包括文件名称、责任方、完成状态、风险缺口和下一步追踪动作。"],
      ["管理层摘要", "压缩成董事/管理层可读结论。", "请把法律审阅结果压缩成管理层摘要，包括交易结构、主要风险、建议动作、谈判优先级和一句结论。"],
    ],
    en: [
      ["Clause Risk Matrix", "Rank clauses by severity with edits and open questions.", "Please produce a clause risk matrix with high/medium/low severity, clause location, risk rationale, business impact, suggested edits, and open questions."],
      ["Negotiation List", "Create negotiation asks, fallbacks, and trade-offs.", "Please turn the current agreement or clause set into a negotiation list with must-haves, concessions, tradeable items, fallback wording, and likely counterarguments."],
      ["Security Package", "Review guarantees, security, and recovery path.", "Please focus on guarantees, security, collateral, recourse path, and enforcement obstacles, then recommend creditor-protection improvements."],
      ["CP Checklist", "Organize conditions precedent and document gaps.", "Please organize a conditions precedent checklist with document name, responsible party, status, risk gap, and next tracking action."],
      ["Executive Summary", "Compress the legal review for management.", "Please compress the legal review into an executive summary with transaction structure, key risks, recommended actions, negotiation priorities, and a one-line conclusion."],
    ],
  },
  finance: {
    zh: [
      ["信用判断", "经营、现金流、杠杆和还款来源。", "请从授信角度分析当前材料，输出经营表现、现金流质量、杠杆结构、还款来源、保护条款和授信结论。"],
      ["财务亮点", "提炼核心指标、趋势和异常。", "请提炼当前财务材料的核心指标、同比/环比趋势、异常变动、驱动因素和需要追问的问题。"],
      ["风险预警", "识别 covenant、流动性和信用风险。", "请识别当前材料中的财务承诺、流动性、盈利质量、债务到期、关联交易和信用风险预警。"],
      ["管理层汇报", "生成高管汇报版摘要。", "请把当前分析整理成高管汇报版，包括核心判断、三条证据、关键风险、建议动作和下一步材料清单。"],
      ["可视化建议", "把表格/指标转为图表方案。", "请把当前数据整理成可视化输出建议，说明适合的折线图、柱状图、饼图或瀑布图，以及每张图的标题和结论。"],
    ],
    en: [
      ["Credit View", "Assess operations, cash flow, leverage, and repayment.", "Please analyze the materials from a credit perspective: operating performance, cash-flow quality, leverage, repayment sources, protection terms, and credit conclusion."],
      ["Financial Highlights", "Extract key metrics, trends, and anomalies.", "Please extract key metrics, YoY/QoQ trends, unusual movements, drivers, and follow-up questions from the financial materials."],
      ["Risk Alerts", "Flag covenants, liquidity, and credit risk.", "Please identify covenant, liquidity, earnings quality, debt maturity, related-party, and credit-risk warning signals in the materials."],
      ["Management Brief", "Create an executive-ready summary.", "Please turn the analysis into a management brief with core judgment, three supporting points, key risks, recommended actions, and next material requests."],
      ["Chart Suggestions", "Convert tables and metrics into chart ideas.", "Please propose visual outputs for the data, including line, bar, pie, or waterfall charts, plus each chart title and takeaway."],
    ],
  },
  trade: {
    zh: [
      ["条款审阅", "检查 DLC/SBLC 关键条款和触发条件。", "请审阅当前贸易金融文件，列出关键条款、触发条件、银行责任、申请人/受益人义务和建议修改。"],
      ["不符点清单", "识别 discrepancy、严重性和补救路径。", "请整理单据不符点清单，包括不符描述、严重性、可补救性、所需文件和沟通建议。"],
      ["提款/付款路径", "拆解 drawing/payment 流程和证明文件。", "请拆解提款或付款路径，说明触发步骤、所需证明、时间节点、争议点和执行风险。"],
      ["银行保护点", "形成银行侧保护条款和操作动作。", "请从银行侧角度提出保护点，包括文本修改、尽调材料、操作控制、保留意见和升级审批建议。"],
      ["客户沟通稿", "生成对客户或交易对手的说明。", "请把当前问题整理成客户沟通稿，语气专业、清楚，包含问题、影响、需补材料和下一步时间安排。"],
    ],
    en: [
      ["Clause Review", "Check DLC/SBLC wording and triggers.", "Please review the trade-finance document and list key clauses, trigger conditions, bank obligations, applicant/beneficiary duties, and suggested revisions."],
      ["Discrepancy List", "Identify discrepancies, severity, and cure path.", "Please organize a discrepancy list with description, severity, curability, required documents, and communication suggestions."],
      ["Drawing / Payment Path", "Map drawing or payment flow and evidence.", "Please map the drawing or payment path with trigger steps, required evidence, timing, dispute points, and execution risk."],
      ["Bank Protection", "Draft bank-side protections and actions.", "Please propose bank-side protections including wording changes, diligence requests, operational controls, reservations, and approval escalation."],
      ["Client Note", "Create a client or counterparty message.", "Please turn the current issue into a professional client note with issue, impact, required materials, and next-step timing."],
    ],
  },
  sblcIssuer: {
    zh: [
      ["开证人总控", "角色关系、12 步闸口、证据与停止权。", "请按开证人视角生成 SBLC 全流程监督表：列出开证机构、开证银行、收益机构、接证/通知银行、支付银行、托管代理、法律顾问的关系；逐步列出 12 个流程闸口、责任方、前置条件、证据、时限、红旗、开证人批准/停止权和下一步。"],
      ["SPA / 托管审核", "把程序写入合同与 escrow。", "请审核 SBLC 程序应如何写入 SPA 和托管协议，输出必须条款、条件先决、支票托管/释放/退回/没收机制、ICC 仲裁、适用法律和保护开证人的修改建议。"],
      ["机构关系图", "澄清各银行与机构的交叉关系。", "请梳理 SBLC 交易中的机构关系：开证人/开证机构、开证银行、收益人/收益机构、接证机构、接证/通知银行、支付银行、托管代理、指定公司/nominee，各自职责、信息流、资金/支票流、SWIFT 流和风险归属。"],
      ["SWIFT 闸口核查", "MT799、MT760、确认与异常处理。", "请检查 MT799 pre-advice、MT799 acknowledgment、MT760 issuance、MT760/MT799 receipt confirmation、原件交付各节点，列明不得进入下一步的条件、银行时限、必须留存证据和开证人终止权。"],
      ["违约与没收矩阵", "延迟、误述、银行不响应、费用异常。", "请生成 SBLC 交易违约/没收矩阵，覆盖受益人延迟超过 5 个银行日、接证银行 3 个银行日不确认、模板未获无条件批准、支付银行位于中国大陆、KYC/AML 不完整、MT760 后发现异常等情形。"],
    ],
    en: [
      ["Issuer Control", "Role map, 12 gates, evidence, stop rights.", "Create an issuer-side SBLC supervision table covering issuer, issuing bank, beneficiary, advising/receiving bank, paying bank, escrow agent, and counsel; for each of the 12 gates list owner, conditions precedent, evidence, timeline, red flags, issuer approval/stop rights, and next action."],
      ["SPA / Escrow Review", "Embed the procedure into SPA and escrow.", "Review how the SBLC procedure should be embedded into the SPA and escrow agreement. Provide mandatory clauses, conditions precedent, cheque escrow/release/return/forfeiture mechanics, ICC arbitration, governing law, and issuer-protective edits."],
      ["Institution Map", "Clarify cross-institution relationships.", "Map the institutional relationships in this SBLC transaction: issuer/issuing party, issuing bank, beneficiary, receiving/advising bank, paying bank, escrow agent, designated company/nominee, their responsibilities, information flow, cheque/fund flow, SWIFT flow, and risk allocation."],
      ["SWIFT Gate Check", "MT799, MT760, acknowledgments, exceptions.", "Check MT799 pre-advice, MT799 acknowledgment, MT760 issuance, MT760/MT799 receipt confirmation, and original delivery nodes. State no-go conditions, bank timelines, evidence to retain, and issuer termination rights."],
      ["Default / Forfeiture Matrix", "Delay, misrepresentation, bank non-response, fee issues.", "Create an SBLC default/forfeiture matrix covering beneficiary delay beyond 5 banking days, receiving bank failing to acknowledge within 3 banking days, template not unconditionally approved, paying bank in Mainland China, incomplete KYC/AML, and post-MT760 irregularities."],
    ],
  },
  strategy: {
    zh: [
      ["Issue Tree", "MECE 拆解问题结构。", "请把这个问题拆成 MECE issue tree，标出一级/二级问题、关键假设、数据需求和优先级。"],
      ["假设验证", "设计验证路径和证据。", "请提出核心假设、验证方法、需要的数据、可观察信号和可能推翻假设的证据。"],
      ["CEO Brief", "压缩为高层决策摘要。", "请整理成 CEO Brief，包括核心判断、三条证据、主要风险、建议动作和决策请求。"],
      ["方案对比", "比较不同策略路径。", "请比较几个可选方案，列出收益、成本、风险、实施难度、时间窗口和推荐排序。"],
      ["行动路线图", "形成 30/60/90 天计划。", "请把建议转成 30/60/90 天行动路线图，包含 owner、里程碑、依赖条件和风险控制。"],
    ],
    en: [
      ["Issue Tree", "Break the problem down MECE.", "Please build a MECE issue tree with first- and second-level questions, key hypotheses, data needs, and priorities."],
      ["Hypothesis Test", "Design evidence and validation path.", "Please define the core hypotheses, validation methods, data needed, observable signals, and disconfirming evidence."],
      ["CEO Brief", "Compress into an executive decision brief.", "Please turn this into a CEO brief with core judgment, three supporting points, key risks, recommended actions, and decision request."],
      ["Options Compare", "Compare strategic paths.", "Please compare the available options by upside, cost, risk, implementation difficulty, timing window, and recommended ranking."],
      ["Action Roadmap", "Create a 30/60/90-day plan.", "Please convert the recommendation into a 30/60/90-day action roadmap with owners, milestones, dependencies, and risk controls."],
    ],
  },
  document: {
    zh: [
      ["一页摘要", "提炼重点、结论和风险。", "请把当前文档整理成一页摘要，包括背景、核心内容、关键结论、风险和下一步。"],
      ["版本差异", "对比多个版本或附件。", "请对比这些文档或版本，列出主要差异、影响、风险等级和建议保留版本。"],
      ["待办提取", "提取 owner、deadline 和未决事项。", "请从材料中提取所有行动项，包括事项、owner、deadline、依赖条件和状态。"],
      ["交付版重写", "改成可直接交付的正式文稿。", "请把当前内容重写为可直接交付的正式版本，结构清晰、语气专业、保留关键事实。"],
      ["质量检查", "检查矛盾、缺失和不一致。", "请检查文档里的矛盾、缺失、数字不一致、定义不清和需要补证的地方。"],
    ],
    en: [
      ["One-page Summary", "Extract key points, conclusion, and risk.", "Please turn the document into a one-page summary with background, core content, key conclusions, risks, and next steps."],
      ["Version Delta", "Compare versions or attachments.", "Please compare these documents or versions and list key differences, impact, risk level, and recommended version."],
      ["Action Items", "Extract owners, deadlines, and open items.", "Please extract all action items with task, owner, deadline, dependencies, and status."],
      ["Delivery Rewrite", "Rewrite into a polished deliverable.", "Please rewrite this into a delivery-ready version with clear structure, professional tone, and preserved facts."],
      ["Quality Check", "Find conflicts, gaps, and inconsistencies.", "Please check for contradictions, missing items, inconsistent figures, unclear definitions, and evidence gaps."],
    ],
  },
  google: {
    zh: [
      ["会议后续", "纪要、owner、deadline 和邮件草稿。", "请整理会议后续，包括纪要摘要、owner、deadline、待确认问题和可发送的 follow-up 邮件草稿。"],
      ["邮件草稿", "生成 Gmail 可发送版本。", "请把这些要点整理成一封清晰、专业、可直接发送的邮件，包含主题、正文和附件提醒。"],
      ["日程安排", "整理 Calendar 安排和准备清单。", "请根据这些事项生成日程安排建议，包括会议标题、参会人、议程、准备材料和时间窗口。"],
      ["Docs 提纲", "形成 Google Docs 文档结构。", "请把当前内容整理成 Google Docs 文档提纲，包括标题层级、正文要点、表格位置和待补材料。"],
      ["Sheets 任务表", "生成 Sheets 跟踪表字段。", "请把事项整理成 Google Sheets 跟踪表结构，包含字段、示例行、状态选项和更新频率。"],
    ],
    en: [
      ["Meeting Follow-up", "Minutes, owners, deadlines, and email draft.", "Please organize meeting follow-up with minutes summary, owners, deadlines, open questions, and a send-ready follow-up email."],
      ["Email Draft", "Create a Gmail-ready message.", "Please turn these notes into a clear, professional email with subject, body, and attachment reminder."],
      ["Calendar Plan", "Build calendar plan and prep checklist.", "Please generate scheduling suggestions with meeting title, attendees, agenda, preparation materials, and timing window."],
      ["Docs Outline", "Create a Google Docs structure.", "Please turn this content into a Google Docs outline with heading levels, body points, table locations, and missing materials."],
      ["Sheets Tracker", "Create a tracking table schema.", "Please organize the items into a Google Sheets tracker with fields, sample rows, status options, and update cadence."],
    ],
  },
  knowledge: {
    zh: [
      ["知识地图", "重组目录、标签和链接关系。", "请把这些笔记整理成知识地图，包括目录层级、标签体系、页面链接和检索入口。"],
      ["Decision Log", "沉淀背景、选项、结论和原因。", "请整理成 decision log，包括背景、选项、讨论要点、最终结论、原因和后续行动。"],
      ["页面重写", "改写为可沉淀的知识库页面。", "请把当前内容重写成知识库页面，包含摘要、背景、正文、行动项和关联页面建议。"],
      ["项目索引", "形成项目 Wiki 和资料入口。", "请为这个项目生成 Wiki 索引，包括资料清单、责任人、关键日期、风险和常用链接。"],
      ["待办同步", "把笔记转成任务和 owner。", "请从这些笔记中提取任务，按 owner、优先级、截止日期、依赖和状态整理。"],
    ],
    en: [
      ["Knowledge Map", "Restructure hierarchy, tags, and links.", "Please organize these notes into a knowledge map with hierarchy, tags, page links, and search entry points."],
      ["Decision Log", "Capture context, options, decision, and rationale.", "Please turn this into a decision log with context, options, discussion points, final decision, rationale, and follow-up actions."],
      ["Page Rewrite", "Rewrite into a durable knowledge-base page.", "Please rewrite this as a knowledge-base page with summary, background, body, action items, and related-page suggestions."],
      ["Project Index", "Create a project wiki and source entry.", "Please generate a project wiki index with source list, owners, key dates, risks, and useful links."],
      ["Task Sync", "Convert notes into tasks and owners.", "Please extract tasks from these notes and organize them by owner, priority, due date, dependency, and status."],
    ],
  },
  language: {
    zh: [
      ["自然化改写", "更像真人，保留原意。", "请把下面内容改写得更自然、更像真人表达，同时保持原意准确、语气稳健。"],
      ["高管语气", "压缩、克制、正式。", "请把这段内容改成高管沟通语气，简洁、克制、专业，避免夸张表达。"],
      ["双语润色", "中英文对应优化。", "请做中英文双语润色，保持事实一致，并让英文自然、中文清楚。"],
      ["邮件优化", "可直接发送的邮件口吻。", "请把内容整理成可直接发送的邮件，包含主题、称呼、正文和收尾。"],
      ["去 AI 味", "减少机械感和套路表达。", "请降低这段文字的 AI 痕迹，减少模板化表达，让语气更自然但仍保持专业。"],
    ],
    en: [
      ["Natural Rewrite", "Make it more human while preserving meaning.", "Please rewrite the text so it sounds more natural and human while preserving the original meaning and steady tone."],
      ["Executive Tone", "Concise, restrained, and formal.", "Please rewrite this in an executive communication style: concise, restrained, professional, and not overstated."],
      ["Bilingual Polish", "Improve Chinese and English together.", "Please polish the Chinese and English together, keep facts aligned, and make the English natural and the Chinese clear."],
      ["Email Polish", "Turn it into a send-ready email.", "Please turn this into a send-ready email with subject, greeting, body, and closing."],
      ["De-AI Rewrite", "Reduce mechanical and template-like phrasing.", "Please reduce the AI-like phrasing and make the text more natural while keeping it professional."],
    ],
  },
  image: {
    zh: [
      ["生成图片草稿", "直接出免费视觉方向图。", "请基于这个主题生成一张视觉草稿，并保留构图、材质、色彩和使用场景说明。", "image"],
      ["海报主视觉", "整理海报/封面提示词。", "请把这个主题整理成海报或封面主视觉提示词，包含主体、背景、镜头、质感、光线和排版建议。"],
      ["提案配图", "生成适合商务提案的配图方向。", "请生成适合商务提案使用的图片提示词，风格高级、干净、可信，避免夸张元素。"],
      ["Logo / Icon 方向", "提出图标化视觉方案。", "请提出 5 个 logo 或 icon 视觉方向，每个包含形状、色彩、象征含义和适用场景。"],
      ["精修提示词", "把粗略想法升级为高质量 prompt。", "请把这个粗略视觉想法升级为高质量图片生成 prompt，补充构图、光线、材质、风格和负面提示。"],
    ],
    en: [
      ["Generate Image Draft", "Create a free visual direction draft.", "Please generate a visual draft for this theme and keep notes on composition, texture, color, and usage scenario.", "image"],
      ["Poster Visual", "Build a poster or cover prompt.", "Please turn this theme into a poster or cover prompt with subject, background, lens, texture, lighting, and layout guidance."],
      ["Pitch Image", "Create a business proposal visual direction.", "Please create an image prompt suitable for a business proposal: premium, clean, credible, and not exaggerated."],
      ["Logo / Icon Direction", "Suggest icon-like visual routes.", "Please propose 5 logo or icon visual directions, each with shape, color, symbolism, and use case."],
      ["Prompt Refine", "Upgrade a rough idea into a strong prompt.", "Please upgrade this rough visual idea into a high-quality image-generation prompt with composition, lighting, material, style, and negative prompt."],
    ],
  },
  pdf: {
    zh: [
      ["表格提取", "提取字段、期间和单位。", "请从 PDF 或扫描页提取关键表格，保留字段、期间、单位、原文标签和数据来源页码。"],
      ["Excel 底稿", "整理成可粘贴 Excel 的结构。", "请把数据整理成 Excel 分析底稿格式，包含表名、字段、期间、单位、数值、公式建议和质量标记。"],
      ["数据 QA", "找异常、缺口和口径不一致。", "请检查数据异常、缺口、口径不一致、单位混用和需要人工复核的位置。"],
      ["指标计算", "生成关键财务比率。", "请基于提取数据计算关键财务指标，并说明公式、解释、趋势和风险信号。"],
      ["导出说明", "给出工作底稿交付说明。", "请生成 Excel 工作底稿交付说明，包括工作表结构、字段定义、数据来源和复核步骤。"],
    ],
    en: [
      ["Table Extract", "Extract fields, periods, and units.", "Please extract key tables from PDFs or scanned pages while preserving fields, periods, units, original labels, and source page numbers."],
      ["Excel Workpaper", "Structure data for Excel use.", "Please organize the data into an Excel-ready workpaper with table name, fields, periods, units, values, formula suggestions, and QA flags."],
      ["Data QA", "Find anomalies, gaps, and definition issues.", "Please check for anomalies, gaps, inconsistent definitions, mixed units, and fields requiring manual review."],
      ["Ratio Build", "Calculate key financial ratios.", "Please calculate key financial ratios from the extracted data and explain formulas, interpretation, trend, and risk signals."],
      ["Export Notes", "Create workpaper delivery notes.", "Please generate Excel workpaper delivery notes with sheet structure, field definitions, data sources, and review steps."],
    ],
  },
  diligence: {
    zh: [
      ["主体概况", "梳理公司/个人背景。", "请对该主体做公开信息尽调，输出主体概况、业务范围、关键人员、关联方和基本可信度判断。"],
      ["红旗扫描", "诉讼、监管、负面新闻和异常信号。", "请扫描该主体的红旗事项，包括诉讼、监管处罚、负面新闻、异常工商信息和交易风险。"],
      ["来源清单", "列出证据和引用链接。", "请整理来源清单，按可信度排序，并说明每个来源支持的结论和仍需核实的问题。"],
      ["交易对手结论", "给出是否推进和条件。", "请从交易对手风险角度给出结论，包括可推进条件、需补材料、风险缓释和审批建议。"],
      ["追问问题", "形成尽调问题清单。", "请生成下一轮尽调问题清单，按财务、法律、经营、合规和声誉风险分类。"],
    ],
    en: [
      ["Entity Profile", "Summarize company or person background.", "Please conduct public-information diligence and return entity profile, business scope, key people, related parties, and credibility view."],
      ["Red Flag Scan", "Litigation, regulatory, media, and anomalies.", "Please scan for red flags including litigation, regulatory penalties, negative media, registry anomalies, and transaction risks."],
      ["Source List", "Organize evidence and citations.", "Please organize sources by credibility and explain which conclusion each source supports and what still needs verification."],
      ["Counterparty View", "Decide whether and how to proceed.", "Please provide a counterparty risk conclusion with proceed conditions, missing materials, mitigants, and approval suggestions."],
      ["Diligence Questions", "Build the next question list.", "Please generate the next diligence question list by finance, legal, operations, compliance, and reputation risk."],
    ],
  },
  client: {
    zh: [
      ["客户周报", "本周进展、风险和下周动作。", "请整理客户周报，包括本周进展、客户信号、风险、待确认问题、下周动作和 owner。"],
      ["待办追踪", "提取任务、负责人和 deadline。", "请从材料中提取客户相关待办，按 owner、deadline、优先级、依赖和状态整理。"],
      ["跟进邮件", "生成客户 follow-up 邮件。", "请生成客户 follow-up 邮件，清楚说明进展、待确认事项、我方需要的信息和建议时间安排。"],
      ["关系信号", "识别客户态度和风险信号。", "请识别客户关系信号，包括积极信号、风险信号、沉默点、关键决策人和建议跟进方式。"],
      ["内部简报", "整理给团队的客户简报。", "请把客户事项整理成内部简报，包括背景、当前状态、风险、机会、下一步和内部责任人。"],
    ],
    en: [
      ["Client Weekly", "Progress, risks, and next-week actions.", "Please prepare a client weekly update with progress, client signals, risks, open questions, next-week actions, and owners."],
      ["Task Tracker", "Extract tasks, owners, and deadlines.", "Please extract client-related tasks by owner, deadline, priority, dependency, and status."],
      ["Follow-up Email", "Draft a client follow-up email.", "Please draft a client follow-up email explaining progress, open items, information needed from them, and proposed timing."],
      ["Relationship Signals", "Identify client attitude and risk signals.", "Please identify client relationship signals including positives, risks, silence points, key decision makers, and follow-up approach."],
      ["Internal Brief", "Create a team-facing client brief.", "Please turn the client matter into an internal brief with background, current status, risks, opportunities, next steps, and internal owners."],
    ],
  },
  slack: {
    zh: [
      ["频道摘要", "读取 Slack 可见频道最近消息。", "自动读取 bot 可见频道，生成重点、待办、owner 和风险。", "summary"],
      ["待回复整理", "找出需要回复或推进的消息。", "自动读取 bot 可见频道，整理待回复事项和回复草稿。", "replies"],
      ["Daily Digest", "生成每日协作摘要。", "自动读取 bot 可见频道，整理今日重点、决策、风险和明日优先级。", "digest"],
      ["通知分级", "按紧急/重要/等待分类。", "请把以下 Slack 消息按紧急、重要、等待、FYI 分类，并说明建议处理顺序。"],
      ["发送草稿", "生成可发到频道的更新。", "请基于以下 Slack 内容生成一段可发送到频道的团队更新，语气简洁、清楚、行动导向。"],
    ],
    en: [
      ["Channel Summary", "Read recent messages from a visible Slack channel.", "Automatically reads a bot-visible channel and prepares highlights, action items, owners, and risks.", "summary"],
      ["Reply Needed", "Find messages that need replies or follow-up.", "Automatically reads a bot-visible channel and organizes reply-needed items and reply drafts.", "replies"],
      ["Daily Digest", "Create a daily collaboration digest.", "Automatically reads a bot-visible channel and prepares highlights, decisions, risks, and tomorrow priorities.", "digest"],
      ["Notification Triage", "Classify urgent, important, waiting, and FYI.", "Please classify the following Slack messages into urgent, important, waiting, and FYI, then recommend handling order."],
      ["Sendable Update", "Draft a post-ready team update.", "Please turn the following Slack context into a concise, clear, action-oriented update that can be posted to the channel."],
    ],
  },
};

const SKILL_ACTION_GROUP = {
  "uk_hk_financial_contract_counsel": "legal",
  "financial-analysis": "finance",
  "banking-dlc": "trade",
  "banking-sblc": "sblcIssuer",
  "mckinsey-thinking": "strategy",
  "document-review": "document",
  "google-workspace": "google",
  "composio-workspace": "google",
  "obsidian-notion": "knowledge",
  humanizer: "language",
  "free-image-draft": "image",
  "pdf-excel-analysis": "pdf",
  "due-diligence-web-research": "diligence",
  "financial-report-summary": "finance",
  "client-follow-up-weekly-update": "client",
  "slack-collaboration": "slack",
  pe_insight_master: "diligence",
  am_reporting_engine: "finance",
};

const appState = {
  lang: document.body.dataset.lang || "zh",
  booted: false,
  auth: {
    authenticated: false,
    user: null,
    idleTimeoutSeconds: 0,
    lastActivityAt: 0,
    lastHeartbeatAt: 0,
  },
  adminUsers: [],
  workMgmt: {
    homeMounted: false,
    refreshTimer: null,
    workbench: null,
    myWork: null,
    reports: [],
    fileCenter: null,
    adminOverview: null,
    selectedReportId: "",
    selectedFileId: "",
  },
  authHeartbeatTimer: null,
  authIdleTimer: null,
  authActivityBound: false,
  adminPending: {
    timer: null,
    users: [],
    directory: [],
    count: 0,
    autoPopupShown: false,
  },
  status: null,
  uiDensity: "comfortable",
  enterprise: {
    selectedProject: "",
  },
  skillsIndex: null,
  skillGuide: null,
  skillConfigs: {},
  currentPage: document.body.dataset.defaultPage || "finance",
  currentSkillId: new URLSearchParams(location.search).get("platform") || "financial-analysis",
  routeState: {
    home: { provider: "", model: "", mode: "general", manual_override: false },
    finance: { provider: "", model: "", mode: "credit-review", manual_override: false },
    legal: { provider: "", model: "", mode: "legal-review", manual_override: false },
    "doc-flow": { provider: "", model: "", mode: "review", manual_override: false },
    workbench: { provider: "", model: "", mode: "project-workbench", manual_override: false },
    "my-work": { provider: "", model: "", mode: "personal-work", manual_override: false },
    reports: { provider: "", model: "", mode: "report-center", manual_override: false },
    "file-center": { provider: "", model: "", mode: "file-governance", manual_override: false },
    "ai-agent": { provider: "", model: "", mode: "external-agent-hub", manual_override: false },
    "intel-center": { provider: "", model: "", mode: "intelligence-center", manual_override: false },
  },
  attachments: {
    home: [],
    finance: [],
    legal: [],
    "doc-flow": [],
  },
  outputs: {
    home: null,
    finance: null,
    legal: null,
    "doc-flow": null,
  },
  ioProgress: {
    home: [],
    finance: [],
    legal: [],
    "doc-flow": [],
  },
  actionSelection: {
    home: 0,
    finance: 0,
    legal: 0,
    "doc-flow": 0,
  },
  submitters: {},
  telegram: {
    enabled: true,
    offset: null,
    polling: false,
    timer: null,
    status: null,
  },
  googleWorkspace: {
    profiles: [],
    currentProfile: "saerc",
  },
  composioWorkspace: {
    profiles: [],
    currentProfile: "fastonegroup",
  },
  weather: {
    loaded: false,
  },
  intel: {
    selectedInstrumentId: "",
    selectedInstrumentSymbol: "",
    lastCandlePayload: null,
    chartPayloads: [],
    lastDailyBrief: null,
    lastMarketsOverview: null,
    lastTopNews: null,
    lastMacroRates: null,
    lastMacroCandlePayload: null,
    selectedMacroSymbol: "",
    selectedNewsId: "",
    savedNewsIds: [],
    newsSearchTimer: null,
    previousFilterState: null,
  },
  hermes: {
    state: "loading",
    syncing: false,
    data: null,
    error: "",
    taskFilter: "all",
  },
  governance: {
    data: null,
    state: "loading",
  },
  aiAgent: {
    status: null,
    state: "loading",
    lastTask: null,
    bridgeMode: "handoff",
  },
  cronStatusTimer: null,
  statusRefreshTimer: null,
  routeStatus: "",
  workChat: {
    users: [],
    conversations: [],
    selectedId: "",
    messages: [],
    messageMeta: {},
    messageDateFilter: "",
    refreshTimer: null,
  },
  documentFlows: {
    users: [],
    buckets: { created: [], pending: [], cc: [], granted: [], all: [] },
    notifications: [],
    selectedId: "",
    detail: null,
    refreshTimer: null,
  },
};

function lang() {
  return appState.lang;
}

function pageTitleLabel(page) {
  const labels = {
    zh: { home: "首页", finance: "财务平台", skills: "技能中心", legal: "法务平台", "ai-agent": "AI Agent 中枢", "work-chat": "协作会话", "doc-flow": "文件流程", workbench: "项目工作台", "my-work": "我的工作", reports: "报告中心", "file-center": "文件中心", "governance-center": "合规审计", "intel-center": "数据中心" },
    en: { home: "Home", finance: "Finance", skills: "Skills Hub", legal: "Legal", "ai-agent": "AI Agent Hub", "work-chat": "Collaboration", "doc-flow": "Document Flow", workbench: "Workbench", "my-work": "My Work", reports: "Reports", "file-center": "File Center", "governance-center": "Compliance", "intel-center": "Data Center" },
  };
  return labels[lang()][page] || page;
}

const DESIGN_TOKENS = {
  color: {
    bg: { page: "var(--work-bg)", card: "var(--work-surface)" },
    border: { default: "var(--work-line)" },
    text: { primary: "var(--work-ink)", secondary: "var(--work-muted)", tertiary: "var(--muted-2)" },
    brand: { primary: "var(--work-accent)" },
    state: { success: "var(--work-ok)", warning: "var(--work-warn)", error: "var(--work-danger)" },
    market: { up: "var(--green)", down: "var(--red)" },
  },
  space: { 8: "8px", 12: "12px", 16: "16px", 24: "24px", 32: "32px" },
  radius: { sm: "8px", md: "12px", lg: "16px" },
};

function hasCjkText(value) {
  return /[\u4e00-\u9fff]/.test(String(value || ""));
}

function firstText(...values) {
  for (const value of values) {
    const text = String(value || "").replace(/\s+/g, " ").trim();
    if (text) return text;
  }
  return "";
}

function getDisplayTitle(item, uiLang = lang()) {
  const titleZh = firstText(item?.titleZh, item?.title_zh);
  const titleEn = firstText(item?.titleEn, item?.title_en);
  const titleFallback = firstText(item?.title);
  if (uiLang === "zh") {
    return firstText(titleZh, titleEn, hasCjkText(titleFallback) ? titleFallback : "", titleFallback)
      || "未命名新闻";
  }
  return firstText(titleEn, titleFallback, titleZh) || "Untitled news";
}

function getDisplaySummary(item, uiLang = lang()) {
  const summaryZh = firstText(item?.summaryZh, item?.summary_zh);
  const translatedSummaryZh = firstText(item?.translatedSummaryZh, item?.translated_summary_zh);
  const generatedSummaryZh = firstText(item?.generatedSummaryZh, item?.generated_summary_zh);
  const primarySummary = firstText(item?.summary, item?.summaryContent, item?.summary_content);
  const summaryEn = firstText(item?.summaryEn, item?.summary_en, item?.originalSummary, item?.rawExcerpt, item?.raw_excerpt);
  const fallbackEn = firstText(summaryEn, primarySummary);
  if (uiLang === "zh") {
    if (summaryZh && hasCjkText(summaryZh)) return { text: summaryZh, status: "translated", label: "中文摘要", source: "summary_zh" };
    if (translatedSummaryZh && hasCjkText(translatedSummaryZh)) return { text: translatedSummaryZh, status: "translated", label: "中文摘要", source: "translated_summary_zh" };
    if (generatedSummaryZh && hasCjkText(generatedSummaryZh)) return { text: generatedSummaryZh, status: "generated", label: "中文摘要", source: "generated_summary_zh" };
    if (primarySummary && hasCjkText(primarySummary)) return { text: primarySummary, status: "translated", label: "中文摘要" };
    if (fallbackEn) return { text: fallbackEn, status: "fallback_en", label: "暂无中文摘要，以下为原文摘要", source: "summary_en" };
    return { text: "暂无摘要。", status: "missing", label: "暂无摘要" };
  }
  return { text: primarySummary || summaryEn || summaryZh || translatedSummaryZh || generatedSummaryZh || "No summary.", status: primarySummary || summaryEn ? "source" : "missing", label: "Summary" };
}

function renderStatusBadge(label, state = "neutral") {
  return `<span class="status-badge status-badge--${escapeHtml(state)}">${escapeHtml(label)}</span>`;
}

function renderTranslationStatusBadge(status) {
  const zh = lang() === "zh";
  const labels = {
    translated: zh ? "中文" : "Translated",
    generated: zh ? "中文生成" : "Generated zh",
    fallback_en: zh ? "原文摘要" : "Source",
    source: zh ? "原文" : "Source",
    missing: zh ? "缺失" : "Missing",
  };
  const tone = status === "translated" ? "success" : status === "generated" ? "success" : status === "fallback_en" ? "warning" : status === "missing" ? "error" : "neutral";
  return `<span class="translation-status translation-status--${tone}">${escapeHtml(labels[status] || labels.source)}</span>`;
}

function renderEmptyState(title, detail = "") {
  return `<div class="state-layer state-layer--empty"><strong>${escapeHtml(title)}</strong>${detail ? `<span>${escapeHtml(detail)}</span>` : ""}</div>`;
}

function renderErrorState(message) {
  return `<div class="state-layer state-layer--error"><strong>${lang() === "zh" ? "加载失败" : "Load failed"}</strong><span>${escapeHtml(message)}</span></div>`;
}

function renderLoadingSkeleton(rows = 3) {
  return `<div class="loading-skeleton">${Array.from({ length: rows }).map(() => `<span></span>`).join("")}</div>`;
}

function renderStateLayer(state, options = {}) {
  const title = options.title || (lang() === "zh" ? "状态更新中" : "Updating state");
  const detail = options.detail || "";
  if (state === "loading") return `<div class="state-layer state-layer--loading">${renderLoadingSkeleton(Number(options.rows || 3))}</div>`;
  if (state === "empty") return renderEmptyState(title, detail);
  if (state === "error") return renderErrorState(detail || title);
  if (state === "no-permission") return `<div class="state-layer state-layer--warning"><strong>${lang() === "zh" ? "权限不足" : "No permission"}</strong><span>${escapeHtml(detail || (lang() === "zh" ? "请联系管理员开通权限。" : "Contact admin to request access."))}</span></div>`;
  if (state === "syncing") return `<div class="state-layer state-layer--syncing"><strong>${lang() === "zh" ? "同步中" : "Syncing"}</strong><span>${escapeHtml(detail || (lang() === "zh" ? "正在刷新最新数据..." : "Refreshing latest data..."))}</span></div>`;
  if (state === "partial") return `<div class="state-layer state-layer--warning"><strong>${lang() === "zh" ? "部分可用" : "Partially available"}</strong><span>${escapeHtml(detail || (lang() === "zh" ? "部分模块暂不可用。" : "Some modules are temporarily unavailable."))}</span></div>`;
  return "";
}

function freshnessMeta(timestamp) {
  const ts = Number(timestamp || 0);
  if (!ts) {
    return {
      state: "warning",
      label: lang() === "zh" ? "待同步" : "Pending sync",
      ageText: lang() === "zh" ? "未知" : "Unknown",
    };
  }
  const age = Math.max(0, Math.floor(Date.now() / 1000) - ts);
  const hours = age / 3600;
  const state = hours <= 6 ? "success" : hours <= 24 ? "warning" : "error";
  const ageText = age < 60
    ? (lang() === "zh" ? "刚刚" : "Just now")
    : age < 3600
      ? (lang() === "zh" ? `${Math.floor(age / 60)}分钟前` : `${Math.floor(age / 60)}m ago`)
      : age < 86400
        ? (lang() === "zh" ? `${Math.floor(age / 3600)}小时前` : `${Math.floor(age / 3600)}h ago`)
        : (lang() === "zh" ? `${Math.floor(age / 86400)}天前` : `${Math.floor(age / 86400)}d ago`);
  return {
    state,
    label: state === "success"
      ? (lang() === "zh" ? "新鲜" : "Fresh")
      : state === "warning"
        ? (lang() === "zh" ? "需关注" : "Watch")
        : (lang() === "zh" ? "过期" : "Stale"),
    ageText,
  };
}

function allIntelMarketRows(markets = appState.intel.lastMarketsOverview) {
  const source = markets?.data || markets || {};
  return (source?.regions || [])
    .flatMap((region) => region.countries || [])
    .flatMap((country) => country.indices || []);
}

function intelQualityMetrics(topNews = appState.intel.lastTopNews, markets = appState.intel.lastMarketsOverview) {
  const newsItems = topNews?.data?.items || topNews?.items || [];
  const marketRows = allIntelMarketRows(markets);
  const zhReady = newsItems.filter((item) => {
    const summary = getDisplaySummary(item, "zh");
    return summary.status === "translated" || summary.status === "generated";
  }).length;
  const fallback = newsItems.filter((item) => getDisplaySummary(item, "zh").status === "fallback_en").length;
  const sourceCount = new Set(newsItems.map((item) => item.sourceName).filter(Boolean)).size;
  const highRisk = newsItems.filter((item) => intelNewsRiskLevel(item) === "high").length;
  const latestMarketTs = Math.max(0, ...marketRows.map((row) => Number(row.lastUpdatedAt || 0)));
  return {
    totalNews: newsItems.length,
    zhReady,
    fallback,
    sourceCount,
    highRisk,
    marketsTracked: marketRows.length,
    marketFreshness: freshnessMeta(latestMarketTs),
  };
}

function renderIntelQualityStrip(topNews, markets) {
  const metrics = intelQualityMetrics(topNews, markets);
  const coverage = metrics.totalNews ? Math.round((metrics.zhReady / metrics.totalNews) * 100) : 0;
  return `
    <div class="quality-strip">
      <div><span>${lang() === "zh" ? "中文覆盖" : "Chinese Coverage"}</span><strong>${coverage}%</strong></div>
      <div><span>${lang() === "zh" ? "英文回退" : "English Fallbacks"}</span><strong>${escapeHtml(String(metrics.fallback))}</strong></div>
      <div><span>${lang() === "zh" ? "来源数" : "Sources"}</span><strong>${escapeHtml(String(metrics.sourceCount))}</strong></div>
      <div><span>${lang() === "zh" ? "高风险" : "High Risk"}</span><strong>${escapeHtml(String(metrics.highRisk))}</strong></div>
      <div><span>${lang() === "zh" ? "市场跟踪" : "Markets"}</span><strong>${escapeHtml(String(metrics.marketsTracked))}</strong></div>
      <div><span>${lang() === "zh" ? "行情新鲜度" : "Market Freshness"}</span><strong>${metrics.marketFreshness.ageText}</strong>${renderStatusBadge(metrics.marketFreshness.label, metrics.marketFreshness.state)}</div>
    </div>
  `;
}

function applyDensity(mode = "comfortable") {
  const next = mode === "compact" ? "compact" : "comfortable";
  appState.uiDensity = next;
  document.body.dataset.density = next;
  try {
    localStorage.setItem(DENSITY_KEY, next);
  } catch {}
  document.querySelectorAll("[data-density-mode]").forEach((button) => {
    button.classList.toggle("is-active", button.getAttribute("data-density-mode") === next);
  });
}

function bindDensityControls() {
  const saved = (() => {
    try {
      return localStorage.getItem(DENSITY_KEY) || "comfortable";
    } catch {
      return "comfortable";
    }
  })();
  document.querySelectorAll("[data-density-mode]").forEach((button) => {
    if (button.dataset.boundDensity === "1") return;
    button.dataset.boundDensity = "1";
    button.addEventListener("click", () => applyDensity(button.getAttribute("data-density-mode") || "comfortable"));
  });
  applyDensity(saved);
}

function ensurePlatformCommandStrip() {
  const app = document.querySelector(".app");
  const dock = document.querySelector(".executive-dock");
  if (!app || !dock) return null;
  let strip = document.querySelector("[data-platform-command-strip]");
  if (!strip) {
    strip = document.createElement("section");
    strip.className = "platform-command-strip";
    strip.setAttribute("data-platform-command-strip", "1");
    dock.insertAdjacentElement("afterend", strip);
  }
  return strip;
}

function renderPlatformCommandStrip() {
  const strip = ensurePlatformCommandStrip();
  if (!strip) return;
  const status = appState.status || {};
  const routeHealth = status.route_health || {};
  const activeRoutes = Object.values(routeHealth).filter((item) => String(item?.status || "").toLowerCase() !== "setup_required");
  const readyRoutes = activeRoutes.filter((item) => String(item?.status || "").toLowerCase() === "ready" || item?.available).length;
  const degradedRoutes = activeRoutes.filter((item) => String(item?.status || "").toLowerCase() && String(item?.status || "").toLowerCase() !== "ready").length;
  const setupRequiredRoutes = Object.values(routeHealth).filter((item) => String(item?.status || "").toLowerCase() === "setup_required").length;
  const hermesState = appState.hermes.state || (status.hermes_online ? "ready" : "partial");
  const intelMetrics = intelQualityMetrics();
  const routeTotal = readyRoutes + degradedRoutes || readyRoutes;
  const coverage = intelMetrics.totalNews ? Math.round((intelMetrics.zhReady / intelMetrics.totalNews) * 100) : 0;
  const hermesTone = hermesState === "ready" ? "success" : hermesState === "error" || hermesState === "offline" ? "error" : "warning";
  const routeTone = degradedRoutes ? "warning" : readyRoutes ? "success" : "error";
  const setupTone = setupRequiredRoutes ? "warning" : "success";
  const coverageTone = !intelMetrics.totalNews ? "warning" : intelMetrics.fallback ? "warning" : "success";
  const routeSummaryTone = routeTone === "error" ? "error" : setupTone === "warning" || routeTone === "warning" ? "warning" : "success";
  const intelSummaryTone = coverageTone === "warning" || intelMetrics.marketFreshness.state !== "success" ? "warning" : "success";
  strip.innerHTML = `
    <div class="platform-command-strip__group">
      <div class="platform-command-item">
        <span>${lang() === "zh" ? "工作上下文" : "Workspace Context"}</span>
        <strong>${escapeHtml(pageTitleLabel(appState.currentPage))}</strong>
        <em>${lang() === "zh" ? "工作上下文已同步" : "Context synchronized"}</em>
      </div>
      <div class="platform-command-item platform-command-item--${escapeHtml(hermesTone)}">
        <span>${lang() === "zh" ? "平台健康" : "Platform Health"}</span>
        <strong>${escapeHtml(hermesState === "ready" ? (lang() === "zh" ? "就绪" : "Ready") : hermesState)}</strong>
        <em>${escapeHtml(status.hermes_online ? (lang() === "zh" ? "网关在线" : "Gateway online") : (lang() === "zh" ? "需复核" : "Needs review"))}</em>
      </div>
      <div class="platform-command-item platform-command-item--${escapeHtml(routeSummaryTone)}">
        <span>${lang() === "zh" ? "AI 路由与配置" : "AI Routing & Setup"}</span>
        <strong>${escapeHtml(String(readyRoutes))}/${escapeHtml(String(routeTotal))}</strong>
        <em>${escapeHtml(setupRequiredRoutes ? `${setupRequiredRoutes} ${lang() === "zh" ? "项非阻塞待配置" : "non-blocking setup"}` : (degradedRoutes ? `${degradedRoutes} ${lang() === "zh" ? "需关注" : "to watch"}` : (lang() === "zh" ? "全部可用" : "All available")))}</em>
      </div>
      <div class="platform-command-item platform-command-item--${escapeHtml(intelSummaryTone)}">
        <span>${lang() === "zh" ? "情报质量" : "Intel Quality"}</span>
        <strong>${coverage}%</strong>
        <em>${escapeHtml(`${intelMetrics.fallback ? `${intelMetrics.fallback} ${lang() === "zh" ? "条英文回退" : "fallback"}` : (lang() === "zh" ? "中文优先" : "CN-first")} · ${intelMetrics.marketFreshness.label}`)}</em>
      </div>
    </div>
    <div class="platform-command-strip__tools">
      <button class="tool-btn" type="button" data-density-mode="comfortable" title="${lang() === "zh" ? "标准密度" : "Comfortable density"}">▦</button>
      <button class="tool-btn" type="button" data-density-mode="compact" title="${lang() === "zh" ? "紧凑密度" : "Compact density"}">▤</button>
    </div>
  `;
  bindDensityControls();
  renderInstitutionalWorkspaceShell();
}

const INSTITUTIONAL_PAGE_META = {
  home: {
    group: "command",
    zh: ["总控台", "任务、路由、风险、动态的统一入口", "先看核心状态，再进入对应工作面"],
    en: ["Command", "Unified entry for tasks, routing, risk, and activity", "Check operating status, then move into the right workspace"],
  },
  finance: {
    group: "advisory",
    zh: ["金融工作台", "财报、授信、交易金融和管理层摘要", "上传材料，选择专用动作，再输出可交付结论"],
    en: ["Finance Desk", "Financial reports, credit, trade finance, and executive summaries", "Attach material, pick a specialized action, then produce a deliverable"],
  },
  legal: {
    group: "advisory",
    zh: ["法律工作台", "金融合同、担保、保函和跨境融资条款", "按结构、风险、修改意见和谈判点推进"],
    en: ["Legal Desk", "Finance contracts, guarantees, instruments, and cross-border clauses", "Work through structure, risk, edits, and negotiation points"],
  },
  "intel-center": {
    group: "markets",
    zh: ["情报中心", "新闻、行情、风险和市场联动", "先筛选主题，再查看 Top30 与相关市场"],
    en: ["Intelligence", "News, markets, risk, and linked movers", "Filter topics, then inspect Top 30 and related markets"],
  },
  workbench: {
    group: "execution",
    zh: ["项目工作台", "项目、任务、风险和全局检索", "从项目状态进入任务执行和问题处理"],
    en: ["Project Workbench", "Projects, tasks, risks, and global search", "Move from project status into execution and issue handling"],
  },
  "my-work": {
    group: "execution",
    zh: ["我的工作", "个人待办、待审文件和报告", "优先处理超期、高优先级和待审批事项"],
    en: ["My Work", "Personal tasks, pending documents, and reports", "Prioritize overdue, high-priority, and approval items"],
  },
  reports: {
    group: "governance",
    zh: ["报告中心", "自动日报、周报和管理评论", "生成报告后补充状态、评论与跟进要求"],
    en: ["Reports", "Automated daily, weekly, and management review reports", "Generate, review, annotate, and track follow-up"],
  },
  "file-center": {
    group: "governance",
    zh: ["文件中心", "文件入库、版本、审批和归档", "先查询/上传，再发起审阅审批签字流程"],
    en: ["File Center", "File intake, versions, approval, and archive", "Search or upload, then start review/approval/signing"],
  },
  "governance-center": {
    group: "governance",
    zh: ["合规与审计中心", "审计留痕、RBAC、DLP、集成健康和知识资产", "先看异常、外发和权限，再进入文件或项目闭环"],
    en: ["Compliance & Audit", "Audit trail, RBAC, DLP, integration health, and knowledge assets", "Check exceptions, outbound data, and permissions before file or project action"],
  },
  "doc-flow": {
    group: "governance",
    zh: ["文件流程", "审阅、审批、签字和抄送通知", "围绕当前文件处理下一步审批动作"],
    en: ["Document Flow", "Review, approval, signing, and CC notifications", "Act on the next approval step for the selected document"],
  },
  "work-chat": {
    group: "collaboration",
    zh: ["协作会话", "项目沟通、成员协作和共享文件", "围绕项目线程沉淀共识、附件与决策"],
    en: ["Collaboration", "Project chat, members, and shared files", "Capture decisions, files, and alignment in project threads"],
  },
  skills: {
    group: "advisory",
    zh: ["Skill 中心", "专业能力入口和任务模板", "按业务问题选择最合适的专业工作台"],
    en: ["Skills Hub", "Specialized capabilities and task templates", "Choose the right professional workspace for the job"],
  },
  "ai-agent": {
    group: "advisory",
    zh: ["AI Agent 中枢", "Hermes 内部 Agent 与外部 AI8 Agent 的统一调用入口", "先选择 Agent，再发起任务、保留审计并回填工作流"],
    en: ["AI Agent Hub", "Unified entry for Hermes agents and the external AI8 agent", "Choose an agent, start a task, retain audit, and return output to workflow"],
  },
};

function institutionalMeta(page = appState.currentPage) {
  const fallback = INSTITUTIONAL_PAGE_META.home;
  const meta = INSTITUTIONAL_PAGE_META[page] || fallback;
  const copy = meta[lang()] || fallback[lang()];
  return {
    group: meta.group || fallback.group,
    title: copy?.[0] || pageTitleLabel(page),
    scope: copy?.[1] || "",
    next: copy?.[2] || "",
  };
}

function institutionalOperatingBrief(page = appState.currentPage) {
  const zh = lang() === "zh";
  const meta = institutionalMeta(page);
  const byGroup = {
    command: zh
      ? ["全局判断", "健康、风险、动态先行", "异常可见，动作可追踪"]
      : ["Global view", "Health, risk, and activity first", "Visible exceptions, traceable actions"],
    advisory: zh
      ? ["专业分析", "材料输入、结构判断、交付输出", "结论 / 依据 / 风险 / 动作"]
      : ["Advisory work", "Ingest, structure, deliver", "Conclusion / evidence / risk / action"],
    markets: zh
      ? ["市场情报", "新闻筛选、Top30、市场联动", "中文优先，英文回退有标识"]
      : ["Market intelligence", "Filter, rank, link markets", "CN-first with explicit fallback"],
    execution: zh
      ? ["执行协同", "项目、待办、沟通闭环", "负责人、期限、状态清楚"]
      : ["Execution", "Projects, tasks, collaboration loop", "Owner, deadline, status clear"],
    governance: zh
      ? ["治理交付", "文件、审批、报告留痕", "版本、权限、归档可审计"]
      : ["Governance", "Documents, approvals, reporting record", "Versioned, permissioned, auditable"],
  };
  const rows = byGroup[meta.group] || byGroup.command;
  return {
    lens: rows[0],
    flow: rows[1],
    standard: rows[2],
  };
}

function institutionalWorkflowBlueprint(page = appState.currentPage) {
  const zh = lang() === "zh";
  const group = institutionalMeta(page).group;
  const labels = zh
    ? ["接收", "分流", "审阅", "决策", "归档"]
    : ["Intake", "Route", "Review", "Decide", "Archive"];
  const detailByGroup = {
    command: zh
      ? ["汇总平台状态", "识别异常入口", "核对风险/待办", "决定处理顺序", "同步审计视图"]
      : ["Collect platform state", "Identify exception entry", "Check risks/actions", "Set operating priority", "Sync audit view"],
    advisory: zh
      ? ["上传/输入任务", "选择专业 Skill / Agent", "输出结构化结论", "形成可执行建议", "沉淀模板与记忆"]
      : ["Upload or enter task", "Pick specialist skill / agent", "Produce structured view", "Create actionable advice", "Save template/memory"],
    markets: zh
      ? ["抓取新闻/行情", "筛选主题风险", "核对中文摘要", "关联市场动作", "生成管理摘要"]
      : ["Ingest news/markets", "Filter topic risk", "Check CN summary", "Link market moves", "Create management brief"],
    execution: zh
      ? ["接收项目事项", "分配负责人", "推进任务/沟通", "处理阻塞审批", "更新项目留痕"]
      : ["Receive project item", "Assign owner", "Advance tasks/threads", "Clear blockers", "Update trace"],
    governance: zh
      ? ["文件/日志入库", "权限与 DLP 分流", "审阅审批签字", "批准/退回/外发", "归档与审计追踪"]
      : ["Capture files/logs", "Route RBAC/DLP", "Review/approve/sign", "Approve/return/export", "Archive and audit"],
  };
  const activeByPage = {
    home: 3,
    finance: 2,
    legal: 2,
    "ai-agent": 1,
    skills: 1,
    "intel-center": 3,
    workbench: 2,
    "my-work": 3,
    "work-chat": 2,
    reports: 4,
    "file-center": 1,
    "governance-center": 4,
    "doc-flow": 3,
  };
  return {
    labels,
    details: detailByGroup[group] || detailByGroup.command,
    active: activeByPage[page] || 1,
  };
}

function institutionalPriorityActions(page = appState.currentPage) {
  const zh = lang() === "zh";
  const common = [
    { action: "command", label: zh ? "命令中心" : "Command" },
    { page: "my-work", label: zh ? "我的待办" : "My Work" },
  ];
  const map = {
    home: [{ page: "governance-center", label: zh ? "看合规异常" : "Compliance" }, { page: "workbench", label: zh ? "看项目" : "Projects" }],
    finance: [{ page: "file-center", label: zh ? "调文件" : "Files" }, { page: "governance-center", label: zh ? "审计/外发" : "Audit" }],
    legal: [{ page: "doc-flow", label: zh ? "走审批" : "Doc Flow" }, { page: "file-center", label: zh ? "合同归档" : "Archive" }],
    "ai-agent": [{ action: "ai8-open", label: zh ? "打开 AI8" : "Open AI8" }, { page: "skills", label: zh ? "Skill 指南" : "Skill Guide" }],
    "intel-center": [{ page: "finance", label: zh ? "转分析" : "Analyze" }, { page: "reports", label: zh ? "生成摘要" : "Report" }],
    workbench: [{ page: "my-work", label: zh ? "个人队列" : "Queue" }, { page: "governance-center", label: zh ? "风险闭环" : "Risk Loop" }],
    "my-work": [{ page: "doc-flow", label: zh ? "文件审批" : "Approvals" }, { page: "workbench", label: zh ? "项目状态" : "Projects" }],
    "work-chat": [{ page: "workbench", label: zh ? "项目闭环" : "Project Loop" }, { page: "file-center", label: zh ? "附件归档" : "Files" }],
    reports: [{ page: "governance-center", label: zh ? "审计追踪" : "Audit Trail" }, { page: "workbench", label: zh ? "跟进行动" : "Follow-up" }],
    "file-center": [{ page: "doc-flow", label: zh ? "发起流程" : "Start Flow" }, { page: "governance-center", label: zh ? "DLP/权限" : "DLP/RBAC" }],
    "governance-center": [{ page: "file-center", label: zh ? "文件中心" : "Files" }, { page: "workbench", label: zh ? "项目 War Room" : "War Room" }],
    "doc-flow": [{ page: "file-center", label: zh ? "文件详情" : "File Detail" }, { page: "reports", label: zh ? "输出报告" : "Report" }],
    skills: [{ page: "finance", label: zh ? "金融 Skill" : "Finance Skills" }, { page: "legal", label: zh ? "法律 Skill" : "Legal Skills" }],
  };
  const actions = [...(map[page] || []), ...common];
  const seen = new Set();
  return actions.filter((item) => {
    const key = item.page || item.action;
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  }).slice(0, 4);
}

function renderPageNextStepAssistant(page = appState.currentPage) {
  const zh = lang() === "zh";
  const meta = institutionalMeta(page);
  const brief = institutionalOperatingBrief(page);
  const actions = institutionalPriorityActions(page).slice(0, 3);
  return `
    <aside class="page-next-step-assistant" data-page-next-step-assistant>
      <div>
        <span>${zh ? "下一步建议" : "Next Best Action"}</span>
        <strong>${escapeHtml(meta.next)}</strong>
        <em>${escapeHtml(brief.standard)}</em>
      </div>
      <div class="page-next-step-assistant__actions">
        ${actions.map((item, index) => item.action
          ? `<button class="btn ${index === 0 ? "btn-primary" : "btn-ghost"}" type="button" data-institutional-floating-action="${escapeHtml(item.action)}">${escapeHtml(item.label)}</button>`
          : `<button class="btn ${index === 0 ? "btn-primary" : "btn-ghost"}" type="button" data-institutional-floating-page="${escapeHtml(item.page)}">${escapeHtml(item.label)}</button>`
        ).join("")}
      </div>
    </aside>
  `;
}

function bindPageNextStepAssistantActions(scope = document) {
  scope.querySelectorAll("[data-page-next-step-assistant] [data-institutional-floating-page]").forEach((button) => {
    if (button.dataset.boundNextStepPage === "1") return;
    button.dataset.boundNextStepPage = "1";
    button.addEventListener("click", () => setActivePage(button.getAttribute("data-institutional-floating-page") || "home", true));
  });
  scope.querySelectorAll("[data-page-next-step-assistant] [data-institutional-floating-action]").forEach((button) => {
    if (button.dataset.boundNextStepAction === "1") return;
    button.dataset.boundNextStepAction = "1";
    button.addEventListener("click", () => {
      const action = button.getAttribute("data-institutional-floating-action");
      if (action === "command") openInstitutionalCommandPalette();
      if (action === "ai8-open") window.open("https://ai8.rcouyi.com/chat", "_blank", "noopener,noreferrer");
    });
  });
}

function ensurePageNextStepAssistant() {
  const rail = document.querySelector("[data-institutional-rail]");
  if (rail) {
    bindPageNextStepAssistantActions(rail);
    return;
  }
  const app = document.querySelector(".app");
  if (!app) return;
  let assistant = document.querySelector("[data-page-next-step-assistant]");
  if (!assistant) {
    assistant = document.createElement("aside");
    assistant.className = "page-next-step-assistant";
    assistant.setAttribute("data-page-next-step-assistant", "1");
    document.body.appendChild(assistant);
  }
  assistant.outerHTML = renderPageNextStepAssistant(appState.currentPage);
  bindPageNextStepAssistantActions(document);
}

function routeHealthSnapshot() {
  const routeHealth = appState.status?.route_health || {};
  const rows = Object.entries(routeHealth);
  const active = rows.filter(([, item]) => String(item?.status || "").toLowerCase() !== "setup_required");
  const ready = active.filter(([, item]) => String(item?.status || "").toLowerCase() === "ready" || item?.available).length;
  const offline = active.filter(([, item]) => String(item?.status || "").toLowerCase() === "offline").length;
  const cooldown = active.filter(([, item]) => String(item?.status || "").toLowerCase() === "cooldown").length;
  const setup = rows.length - active.length;
  return { ready, active: active.length, offline, cooldown, setup };
}

function institutionalNavItems() {
  const zh = lang() === "zh";
  return [
    { id: "home", group: "command", label: zh ? "总控" : "Command", detail: zh ? "10秒决策" : "10-sec brief", glyph: "H" },
    { id: "workbench", group: "execution", label: zh ? "项目" : "Projects", detail: zh ? "War Room" : "War Room", glyph: "P" },
    { id: "file-center", group: "governance", label: zh ? "文件" : "Files", detail: zh ? "Gate Control" : "Gate Control", glyph: "D" },
    { id: "intel-center", group: "command", label: zh ? "情报" : "Intelligence", detail: zh ? "新闻与市场" : "News & markets", glyph: "I" },
    { id: "governance-center", group: "governance", label: zh ? "合规" : "Compliance", detail: zh ? "审计与DLP" : "Audit & DLP", glyph: "G" },
    { id: "ai-agent", group: "advisory", label: zh ? "AI Agent" : "AI Agent", detail: zh ? "AI8 与人机入口" : "AI8 & human bridge", glyph: "X" },
  ];
}

function institutionalNavGroups() {
  const zh = lang() === "zh";
  const labels = {
    command: zh ? "总览" : "Overview",
    advisory: zh ? "专业工作台" : "Advisory",
    execution: zh ? "执行协同" : "Execution",
    governance: zh ? "治理交付" : "Governance",
  };
  return Object.entries(labels).map(([id, label]) => ({
    id,
    label,
    items: institutionalNavItems().filter((item) => item.group === id),
  })).filter((group) => group.items.length);
}

function ensureInstitutionalWorkspaceShell() {
  const app = document.querySelector(".app");
  if (!app) return null;
  document.body.classList.add("financial-institutional-upgrade");
  app.classList.add("institutional-shell");
  let rail = app.querySelector("[data-institutional-rail]");
  if (!rail) {
    rail = document.createElement("aside");
    rail.className = "institutional-rail";
    rail.setAttribute("data-institutional-rail", "1");
    app.insertBefore(rail, app.firstElementChild);
  }
  let context = app.querySelector("[data-institutional-context]");
  if (!context) {
    context = document.createElement("section");
    context.className = "institutional-context";
    context.setAttribute("data-institutional-context", "1");
    const strip = ensurePlatformCommandStrip();
    if (strip) strip.insertAdjacentElement("afterend", context);
    else app.insertBefore(context, document.querySelector(".container.main-chat-container"));
  }
  if (rail.dataset.boundInstitutionalRail !== "1") {
    rail.dataset.boundInstitutionalRail = "1";
    rail.addEventListener("click", (event) => {
      const button = event.target.closest("[data-institutional-page]");
      if (!button) return;
      setActivePage(button.getAttribute("data-institutional-page") || "home", true);
    });
  }
  context.querySelectorAll("[data-institutional-action]").forEach((button) => {
    if (button.dataset.boundInstitutionalAction === "1") return;
    button.dataset.boundInstitutionalAction = "1";
    button.addEventListener("click", () => {
      const action = button.getAttribute("data-institutional-action");
      if (action === "refresh") {
        loadStatus().catch(() => {});
        loadHermesFlagshipData({ syncing: true, showLoading: false }).catch(() => {});
        if (appState.currentPage === "intel-center") loadIntelligenceCenterPage().catch(() => {});
        return;
      }
      if (action === "intel") setActivePage("intel-center", true);
      if (action === "workbench") setActivePage("workbench", true);
      if (action === "ai8-open") window.open("https://ai8.rcouyi.com/chat", "_blank", "noopener,noreferrer");
    });
  });
  return { rail, context };
}

function institutionalCommandItems() {
  const currentLang = lang();
  const zh = currentLang === "zh";
  const visibleNav = new Map(institutionalNavItems().map((item) => [item.id, item]));
  const allPageIds = Object.keys(INSTITUTIONAL_PAGE_META);
  const pageItems = allPageIds.map((id) => {
    const item = visibleNav.get(id) || { id, label: pageTitleLabel(id), detail: "", glyph: String((INSTITUTIONAL_PAGE_META[id]?.group || "p")[0] || "P").toUpperCase() };
    const meta = institutionalMeta(id);
    return {
      id,
      type: "page",
      glyph: item.glyph,
      title: meta.title || item.label,
      detail: meta.scope || item.detail || item.label,
      group: zh ? "核心页面" : "Core pages",
      keywords: [item.id, item.label, meta.title, meta.scope, meta.next],
    };
  });
  const platformItems = Object.entries(PLATFORM_META).map(([id, meta]) => {
    const copy = meta[currentLang] || meta.zh || meta.en || {};
    const sectionLabel = meta.section === "legal" ? (zh ? "法律能力" : "Legal capability") : (zh ? "金融能力" : "Finance capability");
    return {
      id,
      type: "skill",
      glyph: meta.section === "legal" ? "L" : "F",
      title: compactPlatformName(copy.name || id),
      detail: copy.desc || id,
      group: sectionLabel,
      keywords: [id, meta.section, copy.name, copy.desc, ...(copy.tags || [])],
    };
  });
  const actionItems = [
    { id: "account", type: "action", glyph: "U", title: zh ? "账号设置" : "Account settings", detail: zh ? "个人资料、密码与本地会话设置" : "Profile, password, and session settings", group: zh ? "管理入口" : "Management", keywords: ["account", "settings", "账号", "设置"] },
    ...(appState.auth.user?.permissions?.view_team_status ? [{ id: "team-status", type: "action", glyph: "T", title: zh ? "团队状态" : "Team status", detail: zh ? "查看团队在线、会话与工作状态" : "Inspect team presence and work state", group: zh ? "管理入口" : "Management", keywords: ["team", "status", "团队", "状态"] }] : []),
    ...(appState.auth.user?.role === "admin" ? [{ id: "admin", type: "action", glyph: "M", title: zh ? "账号管理" : "Account admin", detail: zh ? "用户、权限与审批管理" : "Users, permissions, and approvals", group: zh ? "管理入口" : "Management", keywords: ["admin", "users", "permissions", "账号", "管理", "权限"] }] : []),
  ];
  return [...pageItems, ...actionItems, ...platformItems];
}

function ensureInstitutionalCommandPalette() {
  let palette = document.querySelector("[data-institutional-command-palette]");
  if (!palette) {
    palette = document.createElement("div");
    palette.className = "institutional-command-palette";
    palette.setAttribute("data-institutional-command-palette", "1");
    palette.hidden = true;
    document.body.appendChild(palette);
  }
  if (palette.dataset.boundInstitutionalCommandPalette !== "1") {
    palette.dataset.boundInstitutionalCommandPalette = "1";
    palette.addEventListener("click", (event) => {
      if (event.target === palette || event.target.closest("[data-command-palette-close]")) {
        closeInstitutionalCommandPalette();
        return;
      }
      const command = event.target.closest("[data-command-type][data-command-id]");
      if (!command) return;
      runInstitutionalCommand(command.getAttribute("data-command-type"), command.getAttribute("data-command-id"));
    });
    palette.addEventListener("input", (event) => {
      if (event.target?.matches("[data-command-palette-search]")) {
        renderInstitutionalCommandPalette(event.target.value || "");
      }
    });
    palette.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        closeInstitutionalCommandPalette();
        return;
      }
      if (event.key !== "Enter") return;
      const activeItem = palette.querySelector("[data-command-type][data-command-id]");
      if (!activeItem) return;
      event.preventDefault();
      runInstitutionalCommand(activeItem.getAttribute("data-command-type"), activeItem.getAttribute("data-command-id"));
    });
  }
  const topActions = document.querySelector(".topbar .top-actions");
  if (topActions) {
    let trigger = topActions.querySelector("[data-command-palette-open]");
    if (!trigger) {
      trigger = document.createElement("button");
      trigger.className = "btn btn-ghost institutional-command-trigger";
      trigger.type = "button";
      trigger.setAttribute("data-command-palette-open", "1");
      trigger.addEventListener("click", openInstitutionalCommandPalette);
      topActions.insertBefore(trigger, topActions.firstChild);
    }
    trigger.innerHTML = `<span>${lang() === "zh" ? "命令中心" : "Command"}</span><strong>⌘K</strong>`;
  }
  return palette;
}

function renderInstitutionalCommandPalette(query = "") {
  const palette = ensureInstitutionalCommandPalette();
  if (!palette) return;
  const normalizedQuery = String(query || "").trim().toLowerCase();
  const items = institutionalCommandItems()
    .filter((item) => {
      if (!normalizedQuery) return true;
      return item.keywords.join(" ").toLowerCase().includes(normalizedQuery);
    })
    .slice(0, 14);
  const zh = lang() === "zh";
  palette.innerHTML = `
    <div class="institutional-command-palette__panel" role="dialog" aria-modal="true" aria-label="${escapeHtml(zh ? "命令中心" : "Command center")}">
      <div class="institutional-command-palette__head">
        <div>
          <span>${zh ? "Global Command" : "Global Command"}</span>
          <strong>${zh ? "调度页面、专业能力与工作流" : "Route pages, capabilities, and workflows"}</strong>
        </div>
        <button class="institutional-command-palette__close" type="button" data-command-palette-close aria-label="${escapeHtml(zh ? "关闭" : "Close")}">×</button>
      </div>
      <label class="institutional-command-palette__search">
        <span>${zh ? "搜索" : "Search"}</span>
        <input type="text" value="${escapeHtml(query)}" data-command-palette-search placeholder="${escapeHtml(zh ? "输入页面、金融、法律、报告、文件或能力名称" : "Search pages, finance, legal, reports, files, or capabilities")}" />
      </label>
      <div class="institutional-command-palette__list">
        ${items.length ? items.map((item) => `
          <button class="institutional-command-palette__item" type="button" data-command-type="${escapeHtml(item.type)}" data-command-id="${escapeHtml(item.id)}">
            <span class="institutional-command-palette__glyph">${escapeHtml(item.glyph)}</span>
            <span class="institutional-command-palette__copy">
              <strong>${escapeHtml(item.title)}</strong>
              <em>${escapeHtml(item.detail)}</em>
            </span>
            <span class="institutional-command-palette__group">${escapeHtml(item.group)}</span>
          </button>
        `).join("") : `
          <div class="institutional-command-palette__empty">
            <strong>${zh ? "没有匹配的命令" : "No matching command"}</strong>
            <span>${zh ? "试试搜索 finance、legal、情报、文件或报告。" : "Try finance, legal, intel, files, or reports."}</span>
          </div>
        `}
      </div>
    </div>
  `;
  const input = palette.querySelector("[data-command-palette-search]");
  input?.focus();
  input?.setSelectionRange(input.value.length, input.value.length);
}

function openInstitutionalCommandPalette() {
  const palette = ensureInstitutionalCommandPalette();
  if (!palette) return;
  palette.hidden = false;
  renderInstitutionalCommandPalette("");
}

function closeInstitutionalCommandPalette() {
  const palette = document.querySelector("[data-institutional-command-palette]");
  if (!palette) return;
  palette.hidden = true;
}

function runInstitutionalCommand(type, id) {
  closeInstitutionalCommandPalette();
  if (!id) return;
  if (type === "action") {
    if (id === "account") openAccountCenter();
    if (id === "team-status") openTeamStatusCenter();
    if (id === "admin") openAdminCenter();
    return;
  }
  if (type === "skill") {
    navigateToWorkspaceSkill(id, true);
    return;
  }
  setActivePage(id, true);
}

function renderInstitutionalWorkspaceShell() {
  const shell = ensureInstitutionalWorkspaceShell();
  if (!shell) return;
  ensureInstitutionalCommandPalette();
  document.querySelectorAll("body > [data-page-next-step-assistant]").forEach((node) => node.remove());
  const { rail, context } = shell;
  const meta = institutionalMeta();
  const brief = institutionalOperatingBrief();
  const route = routeHealthSnapshot();
  const workflow = institutionalWorkflowBlueprint(appState.currentPage);
  const actions = institutionalPriorityActions(appState.currentPage);
  const stateLabel = appState.status?.enterprise_kpis?.health_state || (appState.status?.hermes_online ? "ready" : "partial");
  const routeLabel = `${route.ready}/${route.active || route.ready}`;
  const setupLabel = route.setup ? `${route.setup} ${lang() === "zh" ? "待配置" : "setup"}` : (lang() === "zh" ? "无待配置" : "none");
  const groupedNav = institutionalNavGroups();
  rail.innerHTML = `
    <div class="institutional-rail__brand-block">
      <div class="institutional-rail__brand">
        <img src="${themedFastoneLogo("full")}" alt="FASTONE" />
      </div>
      <div>
        <strong>FASTONE</strong>
        <span>${lang() === "zh" ? "INTERNATIONAL 工作平台" : "INTERNATIONAL WORK PLATFORM"}</span>
      </div>
    </div>
    <nav class="institutional-rail__nav" aria-label="${lang() === "zh" ? "工作平台导航" : "Workspace navigation"}">
      ${groupedNav.map((group) => `
        <div class="institutional-rail__group">
          <div class="institutional-rail__group-title">${escapeHtml(group.label)}</div>
          ${group.items.map((item) => `
            <button class="institutional-rail__item ${appState.currentPage === item.id ? "is-active" : ""}" type="button" data-institutional-page="${escapeHtml(item.id)}">
              <span>${escapeHtml(item.glyph)}</span>
              <strong>${escapeHtml(item.label)}</strong>
              <em>${escapeHtml(item.detail || "")}</em>
            </button>
          `).join("")}
        </div>
      `).join("")}
    </nav>
    ${renderPageNextStepAssistant(appState.currentPage)}
    <div class="institutional-rail__foot">
      <span>${lang() === "zh" ? "Ops" : "Ops"}</span>
      <strong>${escapeHtml(String(appState.status?.enterprise_kpis?.health_score ?? "--"))}</strong>
    </div>
  `;
  bindPageNextStepAssistantActions(rail);
  context.innerHTML = `
    <div class="institutional-context__main">
      <div class="institutional-context__kicker">${escapeHtml(meta.group.toUpperCase())}</div>
      <h2>${escapeHtml(meta.title)}</h2>
      <p>${escapeHtml(meta.scope)}</p>
    </div>
    <div class="institutional-context__signal">
      <div><span>${lang() === "zh" ? "页面定位" : "Page Lens"}</span><strong>${escapeHtml(brief.lens)}</strong></div>
      <div><span>${lang() === "zh" ? "主流程" : "Primary Flow"}</span><strong>${escapeHtml(brief.flow)}</strong></div>
      <div><span>${lang() === "zh" ? "验收标准" : "Acceptance"}</span><strong>${escapeHtml(brief.standard)}</strong></div>
    </div>
    <div class="institutional-context__workflow">
      <div class="institutional-context__workflow-head">
        <span>${lang() === "zh" ? "工作流位置" : "Workflow Position"}</span>
        <strong>${escapeHtml(meta.next)}</strong>
      </div>
      <div class="institutional-context__workflow-steps">
        ${workflow.labels.map((label, index) => {
          const active = index === workflow.active;
          const done = index < workflow.active;
          return `
            <button class="institutional-context__step ${active ? "is-current" : ""} ${done ? "is-done" : ""}" type="button" data-institutional-step="${index + 1}" title="${escapeHtml(workflow.details[index] || label)}">
              <span>${String(index + 1).padStart(2, "0")}</span>
              <strong>${escapeHtml(label)}</strong>
              <em>${escapeHtml(workflow.details[index] || "")}</em>
            </button>
          `;
        }).join("")}
      </div>
    </div>
    <div class="institutional-context__next">
      <span>${lang() === "zh" ? "三步触达" : "Three-step access"}</span>
      <strong>${lang() === "zh" ? "优先进入最可能完成闭环的页面" : "Jump to the most likely closure surface"}</strong>
      <div class="institutional-context__actions">
        ${actions.map((item, index) => item.action
          ? `<button class="btn ${index === 0 ? "btn-primary" : "btn-ghost"}" type="button" data-institutional-action="${escapeHtml(item.action)}">${escapeHtml(item.label)}</button>`
          : `<button class="btn ${index === 0 ? "btn-primary" : "btn-ghost"}" type="button" data-institutional-page-action="${escapeHtml(item.page)}">${escapeHtml(item.label)}</button>`
        ).join("")}
      </div>
    </div>
  `;
  context.querySelectorAll("[data-institutional-action]").forEach((button) => {
    if (button.dataset.boundInstitutionalAction === "1") return;
    button.dataset.boundInstitutionalAction = "1";
    button.addEventListener("click", () => {
      const action = button.getAttribute("data-institutional-action");
      if (action === "refresh") {
        loadStatus().catch(() => {});
        loadHermesFlagshipData({ syncing: true, showLoading: false }).catch(() => {});
        if (appState.currentPage === "intel-center") loadIntelligenceCenterPage().catch(() => {});
      } else if (action === "intel") {
        setActivePage("intel-center", true);
      } else if (action === "workbench") {
        setActivePage("workbench", true);
      } else if (action === "command") {
        openInstitutionalCommandPalette();
      } else if (action === "ai8-open") {
        window.open("https://ai8.rcouyi.com/chat", "_blank", "noopener,noreferrer");
      }
    });
  });
  context.querySelectorAll("[data-institutional-page-action]").forEach((button) => {
    if (button.dataset.boundInstitutionalPageAction === "1") return;
    button.dataset.boundInstitutionalPageAction = "1";
    button.addEventListener("click", () => {
      const page = button.getAttribute("data-institutional-page-action");
      if (page) setActivePage(page, true);
    });
  });
}

function institutionalPageAuditMeta(pageId) {
  const zh = lang() === "zh";
  const map = {
    home: zh ? ["数据来源：路由、自动化、工作台状态", "可信度：系统实时状态优先", "下一步：先看健康、风险和待办"] : ["Source: routing, automation, workspace status", "Trust: live system state first", "Next: health, risks, actions"],
    finance: zh ? ["数据来源：财报、授信、贸易金融材料", "可信度：用户材料 + 工作台输出", "下一步：先确认口径、期间和风险点"] : ["Source: financials, credit, trade-finance materials", "Trust: user materials + workspace output", "Next: scope, period, risks"],
    legal: zh ? ["数据来源：合同、担保、保函、条款文本", "可信度：原文条款优先", "下一步：先看结构、风险和修改点"] : ["Source: contracts, guarantees, instruments, clauses", "Trust: source clauses first", "Next: structure, risks, revisions"],
    "ai-agent": zh ? ["数据来源：Hermes Agent、AI8 外部 Agent、审计记录", "可信度：平台任务记录 + 外部会话回填", "下一步：选择 Agent，提交任务并保存结果"] : ["Source: Hermes Agent, AI8 external agent, audit trail", "Trust: platform task record + external session return", "Next: choose agent, submit task, save result"],
    skills: zh ? ["数据来源：Hermes skill registry", "可信度：已加载技能配置", "下一步：按任务选择专业工作台"] : ["Source: Hermes skill registry", "Trust: loaded skill config", "Next: pick the right desk"],
    "work-chat": zh ? ["数据来源：协作会话与成员动态", "可信度：最近消息优先", "下一步：确认结论、owner 和截止时间"] : ["Source: collaboration threads and activity", "Trust: latest messages first", "Next: decisions, owners, due dates"],
    "doc-flow": zh ? ["数据来源：文件流程与审批记录", "可信度：签字/审批状态优先", "下一步：先处理退回、待批和超期"] : ["Source: document flow and approval records", "Trust: signature/approval status first", "Next: returned, pending, overdue"],
    workbench: zh ? ["数据来源：项目、任务、文档中心", "可信度：系统记录优先", "下一步：先处理超期和高风险项目"] : ["Source: projects, tasks, document center", "Trust: system records first", "Next: overdue and high-risk projects"],
    "my-work": zh ? ["数据来源：我的任务、审批、评论", "可信度：个人待办实时记录", "下一步：先处理待审批与超期项"] : ["Source: my tasks, approvals, comments", "Trust: live personal work queue", "Next: approvals and overdue items"],
    reports: zh ? ["数据来源：日报/周报生成记录", "可信度：系统报告 + 人工评论", "下一步：先筛选 follow_up_needed"] : ["Source: generated reports", "Trust: system report + human comments", "Next: filter follow_up_needed"],
    "file-center": zh ? ["数据来源：文件、版本、审批和归档", "可信度：签字锁定记录优先", "下一步：先看超期、待处理和最新版本"] : ["Source: files, versions, approvals, archive", "Trust: signed/locked records first", "Next: overdue, pending, latest version"],
    "intel-center": zh ? ["数据来源：市场快照、Top30、K线", "可信度：来源数与更新时间双校验", "下一步：先看高风险新闻和市场联动"] : ["Source: market snapshot, Top 30, candles", "Trust: source count and freshness", "Next: high-risk stories and market linkage"],
  };
  return map[pageId] || (zh ? ["数据来源：当前工作台", "可信度：系统状态优先", "下一步：先看异常和待办"] : ["Source: active workspace", "Trust: system state first", "Next: exceptions and actions"]);
}

function renderInstitutionalPageAuditStrips() {
  document.querySelectorAll(".page").forEach((page) => {
    if (!page?.id || page.querySelector("[data-page-audit-strip], .ops-trust-strip")) return;
    const target = page.querySelector(".page-header, .workspace-head, .section-head");
    if (!target) return;
    const strip = document.createElement("div");
    strip.className = "ops-trust-strip ops-trust-strip--auto";
    strip.setAttribute("data-page-audit-strip", page.id);
    strip.innerHTML = institutionalPageAuditMeta(page.id).map((item) => `<span>${escapeHtml(item)}</span>`).join("");
    target.insertAdjacentElement("afterend", strip);
  });
}

function bindInstitutionalShortcuts() {
  if (document.body.dataset.boundInstitutionalShortcuts === "1") return;
  document.body.dataset.boundInstitutionalShortcuts = "1";
  document.addEventListener("keydown", (event) => {
    const target = event.target;
    const isTyping = target && ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName);
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      openInstitutionalCommandPalette();
      return;
    }
    if (event.key === "Escape" && !document.querySelector("[data-institutional-command-palette]")?.hidden) {
      event.preventDefault();
      closeInstitutionalCommandPalette();
      return;
    }
    if (isTyping || !(event.altKey || event.ctrlKey) || event.shiftKey || event.metaKey) return;
    const numeric = Number(event.key);
    if (!Number.isInteger(numeric) || numeric < 1 || numeric > 8) return;
    const item = institutionalNavItems()[numeric - 1];
    if (item?.id) {
      event.preventDefault();
      setActivePage(item.id, true);
    }
  });
}

function effectiveWorkspaceKey(workspaceKey) {
  if (workspaceKey !== "home") return workspaceKey;
  if (appState.currentPage === "legal") return "legal";
  return "finance";
}

function currentMeta(id = appState.currentSkillId) {
  return PLATFORM_META[id] || PLATFORM_META["financial-analysis"];
}

function currentLocaleMeta(id = appState.currentSkillId) {
  return currentMeta(id)[lang()];
}

function currentSkillConfig(id = appState.currentSkillId) {
  return appState.skillConfigs[id] || null;
}

function professionalOutputInstruction(skillId, modeLabel) {
  const mode = modeLabel || "General";
  const antiAiZh = "禁止出现“作为AI”“我只是模型”“以下仅供参考”等明显 AI 痕迹。避免模板腔、机械套话、过度免责声明和空泛连接词，语气必须像该领域资深专业人士直接写给业务负责人、客户或管理层。";
  const antiAiEn = "Do not use AI tell-tale phrasing such as 'as an AI', generic disclaimers, mechanical transitions, or template-heavy wording. The result must read like it was drafted directly by a senior domain professional for a client, operator, or leadership audience.";
  const zhMap = {
    "financial-report-summary": `请直接按专业中文成稿输出，优先形成：【高管摘要】【核心财务数据】【正面信号】【风险提示】【管理层指引与展望】【建议追问】【结论】。${antiAiZh} 当前模式：${mode}。`,
    "financial-analysis": `请按授信/财务分析专业水准输出，优先形成：经营表现、核心指标、风险点、判断结论、建议动作。${antiAiZh} 当前模式：${mode}。`,
    "banking-dlc": `请按银行跟单信用证执行与风险审阅标准输出，优先形成：信用证结构、单据要求、不符点、UCP/ISBP 风险、银行立场、修改建议和下一步。${antiAiZh} 当前模式：${mode}。`,
    "banking-sblc": `请按开证人/开证方 SBLC 全流程监督标准输出，优先形成：机构关系图、12 步流程闸口、条件先决、SPA/托管条款、MT799/MT760 SWIFT 控制、支票/费用释放、原件交付、终止/没收触发、红旗事项和开证人下一步动作。必须区分开证机构/开证人、开证银行、收益人/收益机构、接证机构、接证/通知银行、支付银行、托管代理和法律顾问。${antiAiZh} 当前模式：${mode}。`,
    "pdf-excel-analysis": `请按分析底稿标准输出，清楚标注单位、期间、口径、异常值和待核实项。${antiAiZh} 当前模式：${mode}。`,
    "due-diligence-web-research": `请按尽调报告标准输出，区分事实、信号、判断与来源。${antiAiZh} 当前模式：${mode}。`,
    "client-follow-up-weekly-update": `请按客户跟进/周报标准输出，形成进展、风险、关键信号、下一步和责任建议。${antiAiZh} 当前模式：${mode}。`,
    "uk_hk_financial_contract_counsel": `请按银行与法律双视角输出，结论必须专业、简洁、可执行。${antiAiZh} 当前模式：${mode}。`,
    "humanizer": `请按专业文稿润色标准输出，避免机械语气，保持自然、稳重、准确。${antiAiZh} 当前模式：${mode}。`,
    "mckinsey-thinking": `请按高层策略备忘录标准输出，先结论后论证，保持 MECE 和执行导向。${antiAiZh} 当前模式：${mode}。`,
    "document-review": `请按交付式审阅标准输出，优先摘要、差异、风险和建议修改。${antiAiZh} 当前模式：${mode}。`,
    "google-workspace": `请按商务协同标准输出，形成可直接发送或执行的成稿。${antiAiZh} 当前模式：${mode}。`,
    "composio-workspace": `请按协同动作标准输出，形成可执行清单、邮件草稿、会议后续或提纲。${antiAiZh} 当前模式：${mode}。`,
    "obsidian-notion": `请按知识管理标准输出，结构清晰、层级明确、便于沉淀。${antiAiZh} 当前模式：${mode}。`,
    "slack-collaboration": `请按团队协作摘要标准输出，突出结论、待办、负责人和下一步。${antiAiZh} 当前模式：${mode}。`,
    "free-image-draft": `请按专业金融品牌视觉顾问标准输出，优先形成：视觉目标、构图、色彩材质、生成提示词、负面提示词和迭代方向。${antiAiZh} 当前模式：${mode}。`,
  };
  const enMap = {
    "financial-report-summary": `Write at executive finance quality. Prefer sections for Executive Summary, Core Financial Data, Positive Signals, Risk Signals, Management Outlook, Follow-up Questions, and Conclusion. ${antiAiEn} Current mode: ${mode}.`,
    "financial-analysis": `Write at professional credit-analysis quality with performance, core metrics, risks, conclusion, and recommended actions. ${antiAiEn} Current mode: ${mode}.`,
    "banking-dlc": `Write at bank-grade documentary credit review quality with LC structure, document requirements, discrepancies, UCP/ISBP risk, bank position, amendment suggestions, and next steps. ${antiAiEn} Current mode: ${mode}.`,
    "banking-sblc": `Write at issuer-side SBLC end-to-end supervision quality with institutional role map, 12 procedural gates, conditions precedent, SPA/escrow clauses, MT799/MT760 SWIFT controls, cheque/fee release, original delivery, termination/forfeiture triggers, red flags, and issuer next actions. Distinguish issuing party/issuer, issuing bank, beneficiary, receiving/advising bank, paying bank, escrow agent, and counsel. ${antiAiEn} Current mode: ${mode}.`,
    "pdf-excel-analysis": `Write like a clean analysis workpaper with units, periods, source quality flags, anomalies, and follow-ups. ${antiAiEn} Current mode: ${mode}.`,
    "due-diligence-web-research": `Write like a professional diligence memo with facts, signals, judgment, and sources clearly separated. ${antiAiEn} Current mode: ${mode}.`,
    "client-follow-up-weekly-update": `Write like a client follow-up memo with progress, risks, signals, next steps, and ownership. ${antiAiEn} Current mode: ${mode}.`,
    "uk_hk_financial_contract_counsel": `Write from both legal and bank-risk perspectives with professional, concise, actionable conclusions. ${antiAiEn} Current mode: ${mode}.`,
    "humanizer": `Write at polished editorial quality while sounding natural, human, accurate, and professional. ${antiAiEn} Current mode: ${mode}.`,
    "mckinsey-thinking": `Write like an executive strategy memo: conclusion first, clear logic, MECE structure, practical next steps. ${antiAiEn} Current mode: ${mode}.`,
    "document-review": `Write as a delivery-ready review with summary, differences, risks, and revision suggestions. ${antiAiEn} Current mode: ${mode}.`,
    "google-workspace": `Write in a business-ready collaboration style so the output can be used directly. ${antiAiEn} Current mode: ${mode}.`,
    "composio-workspace": `Write as actionable collaboration output: checklists, drafts, follow-ups, or structured outlines. ${antiAiEn} Current mode: ${mode}.`,
    "obsidian-notion": `Write as high-quality knowledge-management output with clear hierarchy and clean structure. ${antiAiEn} Current mode: ${mode}.`,
    "slack-collaboration": `Write as a team-operations summary with decisions, actions, owners, and next steps. ${antiAiEn} Current mode: ${mode}.`,
    "free-image-draft": `Write like a professional financial-brand visual consultant with creative objective, composition, palette/materials, image prompt, negative prompt, and iteration direction. ${antiAiEn} Current mode: ${mode}.`,
  };
  const map = lang() === "zh" ? zhMap : enMap;
  return map[skillId] || (lang() === "zh" ? `请按当前工作台的专业标准输出，保持结构清晰、结论可执行。${antiAiZh} 当前模式：${mode}。` : `Write to the professional standard of this workspace with clear structure and actionable conclusions. ${antiAiEn} Current mode: ${mode}.`);
}

function professionalQualityChecklist(skillId) {
  const zhMap = {
    "financial-report-summary": "成稿前自检：1. 数字、单位、期间前后一致；2. 先写结论与亮点，再写风险与展望；3. 不虚构财务数据；4. 追问问题必须具体可执行；5. 语言像给管理层的正式摘要。",
    "financial-analysis": "成稿前自检：1. 明确区分事实、判断、建议；2. 关键指标与结论互相支撑；3. 不遗漏流动性、杠杆、现金流和违约信号；4. 建议动作要有优先级；5. 语言像授信或财务分析备忘录。",
    "banking-dlc": "成稿前自检：1. 信用证结构和适用规则清楚；2. 单据要求与不符点逐项对应；3. 不符点严重程度分级；4. 修改建议可落到条款；5. 语言像银行贸易金融操作/风险意见。",
    "banking-sblc": "成稿前自检：1. 必须先画清楚开证人/开证机构、开证银行、收益人、接证/通知银行、支付银行、托管代理和法律顾问的关系；2. 12 个步骤必须逐项列出前置条件、证据、责任方、时限和开证人批准/停止权；3. SPA、托管协议、支票、费用释放、MT799/MT760、原件交付和没收条款必须互相一致；4. 大陆中国支付银行限制必须显式检查；5. 语言像开证人交易控制 memo。",
    "pdf-excel-analysis": "成稿前自检：1. 单位、期间、口径和来源标注清楚；2. 异常值和缺口单独点出；3. 表格或底稿字段命名专业统一；4. 不把待核实数字写成确定事实；5. 语言像分析底稿说明。",
    "due-diligence-web-research": "成稿前自检：1. 事实、信号、判断、来源分开写；2. 风险等级有依据；3. 不把公开传闻写成定论；4. 保留关键来源线索；5. 语言像尽调 memo。",
    "client-follow-up-weekly-update": "成稿前自检：1. 明确写出进展、风险、下一步和责任人；2. 时间节点具体；3. 不写空泛鼓励语；4. 对客户可见版本保持稳重；5. 语言像正式客户跟进周报。",
    "uk_hk_financial_contract_counsel": "成稿前自检：1. 先写交易结构和核心风险；2. 区分法律问题与银行视角问题；3. 修改建议可直接落到条款；4. 不使用模糊法律套话；5. 语言像资深金融律师或银行法律顾问。",
    "humanizer": "成稿前自检：1. 去掉机械连接词和模板套话；2. 保留事实准确性；3. 语气自然但不松散；4. 读起来像真人专业写作；5. 不出现 AI 自我指涉。",
    "mckinsey-thinking": "成稿前自检：1. 结论先行；2. 每段只有一个核心观点；3. 逻辑 MECE；4. 建议动作具体；5. 语言像高层策略备忘录。",
    "document-review": "成稿前自检：1. 优先写摘要和主要问题；2. 风险和修改建议配对出现；3. 不漏关键差异；4. 结论简洁；5. 语言像正式交付审阅意见。",
    "google-workspace": "成稿前自检：1. 输出可直接发送或执行；2. 时间、人名、动作明确；3. 不写空泛寒暄；4. 结构利于协同；5. 语言像商务工作成稿。",
    "composio-workspace": "成稿前自检：1. 每项动作有明确对象和结果；2. 清单顺序合理；3. 草稿可直接发送；4. 不写抽象建议；5. 语言像协同执行指令。",
    "obsidian-notion": "成稿前自检：1. 标题层级清楚；2. 知识点便于沉淀和检索；3. 不堆砌冗余句；4. 结构有复用性；5. 语言像知识库正式条目。",
    "slack-collaboration": "成稿前自检：1. 先写决定和待办；2. 负责人和下一步明确；3. 语句短而清楚；4. 不写长篇背景；5. 语言像团队执行摘要。",
    "free-image-draft": "成稿前自检：1. 视觉方向服务业务目标；2. 构图、色彩、材质和场景具体；3. prompt 可直接用于生成；4. 避免廉价模板感和过度装饰；5. 语言像专业品牌设计说明。",
  };
  const enMap = {
    "financial-report-summary": "Final-pass checklist: keep numbers, units, and periods consistent; lead with conclusion and highlights; never invent metrics; make follow-up questions specific; sound like an executive finance brief.",
    "financial-analysis": "Final-pass checklist: separate facts, judgment, and recommendations; ensure metrics support the conclusion; cover liquidity, leverage, cash flow, and default signals; rank actions; sound like a credit memo.",
    "banking-dlc": "Final-pass checklist: clarify LC structure and applicable rules; map document requirements to discrepancies; grade discrepancy severity; make amendments clause-ready; sound like bank trade-finance operations/risk advice.",
    "banking-sblc": "Final-pass checklist: first clarify the relationship among issuer/issuing party, issuing bank, beneficiary, advising/receiving bank, paying bank, escrow agent, and counsel; list conditions, evidence, owner, timeline, and issuer approval/stop right for all 12 steps; ensure SPA, escrow, cheques, fee release, MT799/MT760, original delivery, and forfeiture clauses align; explicitly test the Mainland China paying-bank restriction; sound like an issuer control memo.",
    "pdf-excel-analysis": "Final-pass checklist: label units, periods, definitions, and sources clearly; flag anomalies and gaps; use professional field naming; do not overstate unverified figures; sound like a workpaper note.",
    "due-diligence-web-research": "Final-pass checklist: keep facts, signals, judgment, and sources distinct; support each risk call; avoid turning rumors into conclusions; preserve source trails; sound like a diligence memo.",
    "client-follow-up-weekly-update": "Final-pass checklist: state progress, risks, next steps, and owners clearly; use specific timing; avoid generic encouragement; keep client-facing wording steady; sound like a formal client update.",
    "uk_hk_financial_contract_counsel": "Final-pass checklist: lead with structure and key risks; separate legal issues from bank-risk issues; make revision suggestions clause-ready; avoid vague legal boilerplate; sound like senior finance counsel.",
    "humanizer": "Final-pass checklist: remove mechanical transitions and template phrasing; keep facts accurate; stay natural without getting loose; sound like polished human writing; never self-reference as AI.",
    "mckinsey-thinking": "Final-pass checklist: lead with the conclusion; one core point per paragraph; keep the logic MECE; make actions concrete; sound like an executive strategy note.",
    "document-review": "Final-pass checklist: lead with summary and major issues; pair each risk with a revision suggestion; do not miss key differences; keep conclusions concise; sound like a delivery-ready review.",
    "google-workspace": "Final-pass checklist: make the output send-ready or execution-ready; keep names, timing, and actions explicit; avoid filler; structure for collaboration; sound like business-ready working copy.",
    "composio-workspace": "Final-pass checklist: each action should have a clear object and expected result; order the list logically; make drafts ready to send; avoid abstract advice; sound like execution guidance.",
    "obsidian-notion": "Final-pass checklist: keep heading hierarchy clear; make the material easy to retain and retrieve; trim redundancy; preserve reuse value; sound like a polished knowledge-base entry.",
    "slack-collaboration": "Final-pass checklist: lead with decisions and actions; keep owners and next steps explicit; keep sentences short; avoid unnecessary background; sound like an operations summary.",
    "free-image-draft": "Final-pass checklist: ensure the visual direction serves the business objective; make composition, palette, materials, and scene concrete; keep the prompt generation-ready; avoid cheap template aesthetics; sound like a professional brand-design note.",
  };
  const map = lang() === "zh" ? zhMap : enMap;
  return map[skillId] || (lang() === "zh"
    ? "成稿前自检：确认结论清楚、结构整齐、信息准确、动作可执行，语言像该领域资深专业人士的正式成稿。"
    : "Final-pass checklist: keep the conclusion clear, structure clean, facts accurate, and actions executable while sounding like a senior domain professional.");
}

function buildWorkspaceSystemPrompt(workspaceKey, meta, modeLabel) {
  const skillId = currentWorkspaceSkillId(workspaceKey);
  const config = currentSkillConfig(skillId);
  if (workspaceKey === "home") {
    return (lang() === "zh"
      ? [
          "这是 FASTONE Hermes AI Agent 的人机交流入口。",
          `当前承接工作流：${meta.name || "当前工作台"}；当前模式：${modeLabel || "General"}。`,
          "直接回答问题，优先给结论和下一步。",
          "语言要像资深专业人士，不要出现 AI 痕迹、套话或冗长免责声明。",
        ]
      : [
          "This is the FASTONE Hermes AI Agent human exchange surface.",
          `Current linked workflow: ${meta.name || "active workspace"}; mode: ${modeLabel || "General"}.`,
          "Answer directly, lead with the conclusion, then give the next step.",
          "Write like a senior professional and avoid AI tell-tale phrasing, boilerplate, or long disclaimers.",
        ]).join("\n");
  }
  const parts = [];
  if (config?.system_prompt) parts.push(config.system_prompt);
  parts.push(meta.welcome);
  parts.push(professionalOutputInstruction(skillId, modeLabel));
  parts.push(professionalQualityChecklist(skillId));
  const sections = config?.output_schema?.sections;
  if (Array.isArray(sections) && sections.length) {
    parts.push((lang() === "zh" ? "输出结构：" : "Output structure: ") + sections.join(", "));
  }
  return parts.filter(Boolean).join("\n");
}

function currentGoogleProfile() {
  const current = appState.googleWorkspace.currentProfile || "saerc";
  return appState.googleWorkspace.profiles.find((item) => item.id === current)
    || appState.googleWorkspace.profiles.find((item) => item.default)
    || { id: current, label: current.toUpperCase(), email: "", authenticated: false };
}

function googleMailboxLabel(profile = currentGoogleProfile()) {
  return profile.email ? `${profile.label} <${profile.email}>` : profile.label;
}

function googleMailboxPromptLine() {
  const profile = currentGoogleProfile();
  return lang() === "zh"
    ? `[Google Workspace 邮箱] ${googleMailboxLabel(profile)}`
    : `[Google Workspace Mailbox] ${googleMailboxLabel(profile)}`;
}

function currentComposioProfile() {
  const current = appState.composioWorkspace.currentProfile || "fastonegroup";
  return appState.composioWorkspace.profiles.find((item) => item.id === current)
    || appState.composioWorkspace.profiles.find((item) => item.default)
    || { id: current, label: current, email: "", authenticated: false };
}

function composioMailboxLabel(profile = currentComposioProfile()) {
  return profile.email ? `${profile.label} <${profile.email}>` : profile.label;
}

function composioMailboxPromptLine() {
  const profile = currentComposioProfile();
  return lang() === "zh"
    ? `[Composio 账号] ${composioMailboxLabel(profile)}`
    : `[Composio Account] ${composioMailboxLabel(profile)}`;
}

function composioTestSummary(profile = currentComposioProfile()) {
  if (profile.last_test_ok === true) {
    return lang() === "zh"
      ? `最近测试通过 · ${formatEpochSeconds(profile.last_test_at)}`
      : `Last test passed · ${formatEpochSeconds(profile.last_test_at)}`;
  }
  if (profile.last_test_ok === false) {
    return lang() === "zh"
      ? `最近测试失败 · ${formatEpochSeconds(profile.last_test_at)}`
      : `Last test failed · ${formatEpochSeconds(profile.last_test_at)}`;
  }
  return lang() === "zh" ? "尚未测试" : "Not tested yet";
}

function quickActionsForSkill(id = appState.currentSkillId) {
  const group = QUICK_ACTION_GROUPS[SKILL_ACTION_GROUP[id] || "finance"] || QUICK_ACTION_GROUPS.finance;
  return group[lang()] || group.zh || [];
}

function routeForFile(kind) {
  return LANG_ROUTES[lang()][kind];
}

function weekdayLabel(dateText) {
  const date = new Date(`${dateText}T00:00:00`);
  return date.toLocaleDateString(lang() === "zh" ? "zh-CN" : "en-US", { weekday: "short" });
}

function weatherClockLabel(dateText, timezone) {
  try {
    const date = dateText ? new Date(dateText) : new Date();
    return new Intl.DateTimeFormat(lang() === "zh" ? "zh-CN" : "en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
      timeZone: timezone || undefined,
    }).format(date);
  } catch {
    return "";
  }
}

function weatherText(code) {
  const meta = WEATHER_CODE_META[Number(code)] || { icon: "🌤️", zh: "天气", en: "Weather" };
  return meta[lang()] || meta.en;
}

function weatherIcon(code) {
  return (WEATHER_CODE_META[Number(code)] || { icon: "🌤️" }).icon;
}

function renderWeatherState(html) {
  document.querySelectorAll("[data-weather-box]").forEach((node) => {
    if (typeof html === "string") {
      node.innerHTML = html;
      return;
    }
    node.innerHTML = node.classList.contains("hero-weather-box")
      ? (html.compact || html.full || "")
      : (html.full || html.compact || "");
  });
}

function renderWeatherLoading() {
  renderWeatherState(`<div class="weather-loading">${lang() === "zh" ? "正在定位并读取本地 7 天天气预报..." : "Locating and loading your 7-day local forecast..."}</div>`);
}

function renderWeatherError(message) {
  renderWeatherState(`<div class="weather-empty">${escapeHtml(message)}</div>`);
}

function renderWeatherForecast(payload, coords) {
  const daily = payload?.daily;
  if (!daily?.time?.length) {
    renderWeatherError(lang() === "zh" ? "天气数据暂时不可用。" : "Weather data is temporarily unavailable.");
    return;
  }
  const current = payload?.current || {};
  const locationLabel = lang() === "zh"
    ? `自动定位 · ${coords.latitude.toFixed(2)}, ${coords.longitude.toFixed(2)}`
    : `Auto-detected · ${coords.latitude.toFixed(2)}, ${coords.longitude.toFixed(2)}`;
  const timezoneLabel = payload.timezone || "Local";
  const currentTemp = Number.isFinite(current.temperature_2m) ? Math.round(current.temperature_2m) : null;
  const apparentTemp = Number.isFinite(current.apparent_temperature) ? Math.round(current.apparent_temperature) : null;
  const currentCode = current.weather_code;
  const clock = weatherClockLabel(current.time, payload.timezone);
  const cards = daily.time.slice(0, 7).map((day, index) => {
    const code = daily.weather_code?.[index];
    const max = Math.round(daily.temperature_2m_max?.[index]);
    const min = Math.round(daily.temperature_2m_min?.[index]);
    const rain = Math.round(daily.precipitation_probability_max?.[index] || 0);
    return `
      <div class="weather-day">
        <strong>${escapeHtml(weekdayLabel(day))}</strong>
        <div class="weather-icon">${weatherIcon(code)}</div>
        <div class="weather-temp">${max}° / ${min}°</div>
        <div class="weather-meta">${escapeHtml(weatherText(code))}</div>
        <div class="weather-meta">${lang() === "zh" ? "降水概率" : "Rain chance"} ${rain}%</div>
      </div>
    `;
  }).join("");
  const compactCards = daily.time.slice(0, 7).map((day, index) => {
    const code = daily.weather_code?.[index];
    const max = Math.round(daily.temperature_2m_max?.[index]);
    const min = Math.round(daily.temperature_2m_min?.[index]);
    return `
      <div class="weather-mini-day">
        <strong>${escapeHtml(weekdayLabel(day))}</strong>
        <span class="weather-mini-icon">${weatherIcon(code)}</span>
        <span>${max}°</span>
        <small>${min}°</small>
      </div>
    `;
  }).join("");
  renderWeatherState({ full: `
    <div class="weather-head">
      <div class="weather-title">
        <strong>${lang() === "zh" ? "本地 7 天天气" : "Local 7-Day Forecast"}</strong>
        <span>${escapeHtml(locationLabel)}</span>
      </div>
      <div class="weather-tag">${escapeHtml(timezoneLabel)}</div>
    </div>
    <div class="weather-current">
      <div class="weather-current-main">
        <div class="weather-current-icon">${weatherIcon(currentCode)}</div>
        <div class="weather-current-copy">
          <strong>${currentTemp === null ? "--" : `${currentTemp}°`}</strong>
          <span>${escapeHtml(weatherText(currentCode))}</span>
        </div>
      </div>
      <div class="weather-current-side">
        <div class="weather-current-chip">${lang() === "zh" ? "本地时间" : "Local time"} ${escapeHtml(clock || "--:--")}</div>
        <div class="weather-current-chip">${lang() === "zh" ? "体感" : "Feels like"} ${apparentTemp === null ? "--" : `${apparentTemp}°`}</div>
      </div>
    </div>
    <div class="weather-grid">${cards}</div>
  `, compact: `
    <div class="weather-head weather-head-compact">
      <div class="weather-title">
        <strong>${lang() === "zh" ? "本地 7 天天气" : "Local 7-Day Forecast"}</strong>
        <span>${escapeHtml(locationLabel)}</span>
      </div>
      <div class="weather-tag">${currentTemp === null ? "--" : `${currentTemp}°`} · ${escapeHtml(weatherText(currentCode))}</div>
    </div>
    <div class="weather-inline-summary">
      <span>${lang() === "zh" ? "体感" : "Feels like"} ${apparentTemp === null ? "--" : `${apparentTemp}°`}</span>
      <span>${lang() === "zh" ? "本地时间" : "Local time"} ${escapeHtml(clock || "--:--")}</span>
      <span>${escapeHtml(timezoneLabel)}</span>
    </div>
    <div class="weather-mini-grid">${compactCards}</div>
  `});
}

async function fetchWeatherForecast(coords) {
  const params = new URLSearchParams({
    latitude: String(coords.latitude),
    longitude: String(coords.longitude),
    current: "temperature_2m,apparent_temperature,weather_code,is_day",
    daily: "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
    timezone: "auto",
    forecast_days: "7",
  });
  const resp = await fetch(`https://api.open-meteo.com/v1/forecast?${params.toString()}`, { cache: "no-store" });
  if (!resp.ok) throw new Error(`weather_http_${resp.status}`);
  return resp.json();
}

function getCurrentPositionAsync() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("geolocation_unavailable"));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => resolve(position.coords),
      (error) => reject(error),
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 1800000 }
    );
  });
}

async function loadWeatherForecast() {
  if (!document.querySelector("[data-weather-box]")) return;
  renderWeatherLoading();
  try {
    const coords = await getCurrentPositionAsync();
    const payload = await fetchWeatherForecast(coords);
    renderWeatherForecast(payload, coords);
    appState.weather.loaded = true;
  } catch (error) {
    if (error?.code === 1) {
      renderWeatherError(lang() === "zh" ? "定位权限未开启。开启浏览器定位后可显示本地 7 天天气。" : "Location permission is blocked. Enable location access to show your local 7-day forecast.");
      return;
    }
    renderWeatherError(lang() === "zh" ? "暂时无法读取本地天气，请稍后刷新重试。" : "Unable to load the local forecast right now. Please refresh and try again later.");
  }
}

function sectionForSkill(id) {
  return currentMeta(id).section || "finance";
}

function setActivePage(pageId, updateHash = false) {
  if (!PAGE_KEYS.has(pageId)) return;
  closeTopNavOverflowMenu();
  appState.currentPage = pageId;
  document.querySelectorAll(".page").forEach((page) => {
    page.classList.toggle("active", page.id === pageId);
  });
  document.querySelectorAll(".tab-btn[data-page]").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.page === pageId);
  });
  if (updateHash) history.replaceState(null, "", `${location.pathname}${location.search}#${pageId}`);
  if (pageId === "home") {
    loadWorkMgmtHomeData().catch(() => {});
    loadHermesFlagshipData({ showLoading: false }).catch(() => {});
  }
  if (pageId === "workbench") loadWorkbenchPage().catch(() => {});
  if (pageId === "my-work") loadMyWorkPage().catch(() => {});
  if (pageId === "reports") loadReportsPage().catch(() => {});
  if (pageId === "file-center") loadFileCenterPage().catch(() => {});
  if (pageId === "governance-center") loadGovernanceCenterPage().catch(() => {});
  if (pageId === "ai-agent") loadAiAgentHubPage().catch(() => {});
  if (pageId === "intel-center") loadIntelligenceCenterPage().catch(() => {});
  if (pageId === "work-chat") loadWorkChat().catch(() => {});
  if (pageId === "doc-flow") loadDocumentFlows().catch(() => {});
  syncDockSkillChipState();
  renderPlatformCommandStrip();
  renderInstitutionalWorkspaceShell();
  renderInstitutionalPageAuditStrips();
  sendAuthHeartbeat();
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (m) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }[m]));
}

function appendMessage(container, text, role = "assistant") {
  if (!container) return null;
  const div = document.createElement("div");
  div.className = role === "user" ? "message user" : "message";
  div.textContent = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function appendHtmlMessage(container, html, role = "assistant") {
  if (!container) return null;
  const div = document.createElement("div");
  div.className = role === "user" ? "message user" : "message";
  div.innerHTML = html;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function pollinationsImageUrl(prompt, aspect = "square") {
  const sizes = {
    square: { width: 1024, height: 1024 },
    landscape: { width: 1280, height: 768 },
    portrait: { width: 768, height: 1280 },
  };
  const choice = sizes[aspect] || sizes.square;
  const encoded = encodeURIComponent(String(prompt || "").trim().slice(0, 420));
  const params = new URLSearchParams({
    width: String(choice.width),
    height: String(choice.height),
    nologo: "true",
    seed: String(Date.now()),
  });
  return `https://image.pollinations.ai/prompt/${encoded}?${params.toString()}`;
}

function inferImageAspect(prompt, mode) {
  const text = `${prompt || ""} ${mode || ""}`.toLowerCase();
  if (/(poster|cover|portrait|封面|海报|竖版)/.test(text)) return "portrait";
  if (/(banner|hero|landscape|wide|横版|长图)/.test(text)) return "landscape";
  return "square";
}

function imageDraftMarkup(prompt, url) {
  const loadingText = lang() === "zh" ? "免费图片草稿已生成，可直接预览或打开原图。" : "Free image draft generated. Preview it here or open the original image.";
  const openText = lang() === "zh" ? "打开原图" : "Open image";
  const retryText = lang() === "zh" ? "再来一张" : "Generate another";
  return `
    <div class="image-result">
      <div class="image-result__hint">${escapeHtml(loadingText)}</div>
      <div class="image-result__preview">
        <img src="${escapeHtml(url)}" alt="${escapeHtml(prompt)}" loading="lazy">
      </div>
      <div class="image-result__actions">
        <a class="btn btn-ghost" href="${escapeHtml(url)}" target="_blank" rel="noreferrer">${escapeHtml(openText)}</a>
        <a class="btn btn-ghost" href="${escapeHtml(url)}" target="_blank" rel="noreferrer">${escapeHtml(retryText)}</a>
      </div>
    </div>
  `;
}

function readConversationStore() {
  try {
    const raw = localStorage.getItem(CONVERSATION_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function writeConversationStore(store) {
  try {
    localStorage.setItem(CONVERSATION_KEY, JSON.stringify(store));
  } catch {}
}

function pruneConversationStore(store = readConversationStore()) {
  const cutoff = Date.now() - CONVERSATION_RETENTION_MS;
  const next = {};
  Object.entries(store || {}).forEach(([workspaceKey, rows]) => {
    const kept = (Array.isArray(rows) ? rows : []).filter((item) => Number(item?.ts || 0) >= cutoff);
    if (kept.length) next[workspaceKey] = kept.slice(-60);
  });
  writeConversationStore(next);
  return next;
}

function conversationLabel(count) {
  return lang() === "zh"
    ? `较早记录 ${count} 条`
    : `${count} earlier message${count > 1 ? "s" : ""}`;
}

function updateConversationArchive(container) {
  if (!container) return;
  let archive = container.querySelector(".conversation-archive");
  if (archive) {
    const body = archive.querySelector(".conversation-archive__body");
    Array.from(body.children).forEach((node) => container.insertBefore(node, archive));
    archive.remove();
    archive = null;
  }
  const items = Array.from(container.querySelectorAll("[data-history-item='1']"));
  if (items.length <= CONVERSATION_VISIBLE_COUNT) return;
  const older = items.slice(0, items.length - CONVERSATION_VISIBLE_COUNT);
  archive = document.createElement("details");
  archive.className = "conversation-archive";
  archive.innerHTML = `
    <summary>${conversationLabel(older.length)}</summary>
    <div class="conversation-archive__body"></div>
  `;
  container.insertBefore(archive, items[items.length - CONVERSATION_VISIBLE_COUNT]);
  const body = archive.querySelector(".conversation-archive__body");
  older.forEach((node) => body.appendChild(node));
}

function recordConversationEntry(workspaceKey, role, content) {
  if (!workspaceKey || !content?.trim()) return;
  const store = pruneConversationStore();
  const scope = conversationScopeKey(workspaceKey);
  const rows = Array.isArray(store[scope]) ? store[scope] : [];
  rows.push({ role, content: content.trim(), ts: Date.now() });
  store[scope] = rows.slice(-60);
  writeConversationStore(store);
}

function renderConversationHistory(workspaceKey, container) {
  if (!container) return;
  const store = pruneConversationStore();
  const rows = Array.isArray(store[conversationScopeKey(workspaceKey)]) ? store[conversationScopeKey(workspaceKey)] : [];
  rows.forEach((item) => {
    const node = appendMessage(container, item.content, item.role === "user" ? "user" : "assistant");
    if (node) {
      node.dataset.historyItem = "1";
      node.dataset.ts = String(item.ts || "");
    }
  });
  updateConversationArchive(container);
}

function refreshConversationHistory(workspaceKey, container) {
  if (!container) return;
  container.querySelectorAll("[data-history-item='1']").forEach((node) => node.remove());
  container.querySelectorAll(".conversation-archive").forEach((node) => node.remove());
  renderConversationHistory(workspaceKey, container);
}

function clearConversationHistory(workspaceKey, container) {
  const store = pruneConversationStore();
  delete store[conversationScopeKey(workspaceKey)];
  writeConversationStore(store);
  if (!container) return;
  container.querySelectorAll(".message").forEach((node) => node.remove());
  container.querySelectorAll("[data-history-item='1']").forEach((node) => node.remove());
  container.querySelectorAll(".conversation-archive").forEach((node) => node.remove());
}

function extractTextContent(content) {
  if (!content) return "";
  if (typeof content === "string") return content;
  if (Array.isArray(content)) return content.map(extractTextContent).join("");
  if (typeof content === "object") {
    if (typeof content.text === "string") return content.text;
    if (typeof content.content === "string") return content.content;
    if (typeof content.output_text === "string") return content.output_text;
  }
  return "";
}

function executiveFrameLabel(type) {
  const labels = {
    zh: {
      conclusion: "结论",
      evidence: "依据",
      risks: "主要风险",
      actions: "下一步动作",
    },
    en: {
      conclusion: "Conclusion",
      evidence: "Evidence",
      risks: "Key Risks",
      actions: "Next Actions",
    },
  };
  return (labels[lang()] || labels.en)[type] || type;
}

function ensureExecutiveDepthFrame(text, workspaceKey = "home") {
  const body = String(text || "").trim();
  if (!body) return body;
  const hasStructuredHeader = /(^|\n)(#+\s|【|Conclusion|结论|Key Risks|主要风险)/i.test(body);
  if (hasStructuredHeader) return body;
  const lines = body.split(/\n+/).map((line) => line.trim()).filter(Boolean);
  const conclusion = lines[0] || body.slice(0, 160);
  const evidence = lines.slice(1, 3).join("；") || (lang() === "zh" ? "结合当前输入与工作流状态形成判断。" : "Derived from current inputs and workflow status.");
  const risk = lines.slice(3, 5).join("；") || (lang() === "zh" ? "关键假设需继续核验，防止执行偏差。" : "Key assumptions should be validated to avoid execution drift.");
  const action = workspaceKey === "legal"
    ? (lang() === "zh" ? "输出可执行条款修改建议并明确谈判优先级。" : "Output executable clause revisions with negotiation priority.")
    : workspaceKey === "finance"
      ? (lang() === "zh" ? "补齐财务证据并给出可执行授信动作清单。" : "Complete financial evidence and return an executable credit action list.")
      : (lang() === "zh" ? "明确负责人、截止时间与交付格式。" : "Specify owner, deadline, and delivery format.");
  return [
    `【${executiveFrameLabel("conclusion")}】`,
    conclusion,
    ``,
    `【${executiveFrameLabel("evidence")}】`,
    evidence,
    ``,
    `【${executiveFrameLabel("risks")}】`,
    risk,
    ``,
    `【${executiveFrameLabel("actions")}】`,
    action,
  ].join("\n");
}

function sanitizeProfessionalText(text, context = {}) {
  let cleaned = String(text || "");
  const patterns = [
    /\bAs an AI(?: language model)?[, ]*/gi,
    /\bI am (?:just |only )?an AI(?: assistant| model)?[, ]*/gi,
    /作为AI(?:语言模型)?[，, ]*/g,
    /我是(?:一个|仅仅是)?AI(?:助手|模型)?[，, ]*/g,
    /以下内容(?:仅供参考|供参考)[：:]?/g,
    /仅供参考[。.]?/g,
    /希望这对你有帮助[。.]?/g,
    /如需进一步帮助.*$/gim,
  ];
  patterns.forEach((pattern) => {
    cleaned = cleaned.replace(pattern, "");
  });
  cleaned = cleaned.replace(/\n{3,}/g, "\n\n");
  return ensureExecutiveDepthFrame(cleaned.trim(), context.workspaceKey || "home");
}

function extractChunkText(parsed) {
  const choice = parsed?.choices?.[0] || {};
  return (
    extractTextContent(choice?.delta?.content) ||
    extractTextContent(choice?.delta?.reasoning_content) ||
    extractTextContent(choice?.message?.content) ||
    extractTextContent(parsed?.content) ||
    extractTextContent(parsed?.output_text) ||
    extractTextContent(parsed?.text) ||
    ""
  );
}

function consumeSseBuffer(buffer, onText) {
  const normalized = buffer.replace(/\r\n/g, "\n");
  const parts = normalized.split("\n\n");
  const remainder = parts.pop() || "";
  for (const block of parts) {
    const lines = block.split("\n").map((line) => line.trimStart()).filter((line) => line.startsWith("data:"));
    for (const line of lines) {
      const payload = line.slice(5).trim();
      if (!payload || payload === "[DONE]") continue;
      try {
        const parsed = JSON.parse(payload);
        const delta = extractChunkText(parsed);
        if (delta) onText(delta);
      } catch {
        onText(payload);
      }
    }
  }
  return remainder;
}

async function extractResponseError(resp) {
  const contentType = resp.headers.get("Content-Type") || "";
  try {
    if (contentType.includes("application/json")) {
      const data = await resp.json();
      return data.error || data.message || `HTTP ${resp.status}`;
    }
  } catch {}
  try {
    const text = await resp.text();
    return text || `HTTP ${resp.status}`;
  } catch {
    return `HTTP ${resp.status}`;
  }
}

async function streamChat(messages, provider, model, workspace, onText, onMeta, options = {}) {
  const resp = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      stream: true,
      fast_mode: Boolean(options.fastMode),
      provider,
      model,
      selected_model: model,
      workspace,
      skill_id: currentWorkspaceSkillId(workspace),
      messages,
    }),
  });
  if (!resp.ok) throw new Error(await extractResponseError(resp));
  if (typeof onMeta === "function") onMeta(resp.headers);
  const reader = resp.body?.getReader();
  if (!reader) {
    onText(await resp.text());
    return;
  }
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    buffer = consumeSseBuffer(buffer, onText);
  }
  if (buffer.trim()) consumeSseBuffer(`${buffer}\n\n`, onText);
}

async function slackRequest(action, payload = {}) {
  const resp = await fetch("/api/slack", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, ...payload }),
  });
  const data = await resp.json();
  if (!resp.ok || !data.ok) throw new Error(data.error || `Slack ${action} failed`);
  return data;
}

function formatSlackMessages(messages) {
  return (messages || [])
    .map((msg, idx) => `${idx + 1}. [${msg.user || "unknown"}] ${msg.text || ""}`)
    .join("\n")
    .slice(0, 8000);
}

async function selectSlackChannel() {
  const data = await slackRequest("channels");
  const channels = (data.channels || []).filter((channel) => channel.id && channel.name);
  if (!channels.length) {
    throw new Error(lang() === "zh" ? "没有可读取的 Slack 频道。请先把 hermes_agent 邀进目标频道。" : "No readable Slack channels. Invite hermes_agent to a target channel first.");
  }
  const preferred = channels.find((channel) => channel.is_member) || channels[0];
  return preferred;
}

async function runSlackWorkspaceAction(kind, input, messages) {
  const labels = {
    summary: {
      zh: "频道摘要",
      en: "Channel Summary",
      prompt: lang() === "zh"
        ? "请把以下 Slack 频道消息整理成频道摘要，突出重要信息、待办事项、负责人、截止时间和风险。"
        : "Please turn the following Slack channel messages into a channel summary with important information, action items, owners, deadlines, and risks.",
    },
    replies: {
      zh: "待回复整理",
      en: "Reply Needed",
      prompt: lang() === "zh"
        ? "请从以下 Slack 消息中找出需要回复、需要确认或需要推进的事项，并输出可直接发送的回复草稿。"
        : "Please identify messages that need replies, confirmation, or follow-up, then draft concise replies that can be sent directly.",
    },
    digest: {
      zh: "Daily Digest",
      en: "Daily Digest",
      prompt: lang() === "zh"
        ? "请把以下 Slack 消息整理成 Daily Digest，包括今日重点、决策、风险、待办和明日优先事项。"
        : "Please turn the following Slack messages into a Daily Digest with highlights, decisions, risks, open items, and tomorrow's priorities.",
    },
  };
  const copy = labels[kind] || labels.summary;
  const status = appendMessage(messages, lang() === "zh" ? `正在读取 Slack 并生成${copy.zh}...` : `Reading Slack and preparing ${copy.en}...`, "assistant");
  try {
    const channel = await selectSlackChannel();
    const history = await slackRequest("history", { channel: channel.id, limit: kind === "digest" ? 40 : 25 });
    const transcript = formatSlackMessages(history.messages || []);
    if (!transcript) {
      status.textContent = lang() === "zh" ? `#${channel.name} 暂无可摘要的消息。` : `#${channel.name} has no messages to summarize.`;
      return;
    }
    input.value = `${copy.prompt}\n\nChannel: #${channel.name}\n\n${transcript}`;
    status.textContent = lang() === "zh"
      ? `已读取 #${channel.name} 最近 ${history.messages.length} 条消息，并填入${copy.zh}任务。点击发送即可生成结果。`
      : `Loaded ${history.messages.length} recent messages from #${channel.name} and prepared the ${copy.en} task. Click Send to generate the result.`;
  } catch (error) {
    status.textContent = `${lang() === "zh" ? "Slack 动作失败：" : "Slack action failed: "}${error.message || error}`;
  }
}

async function telegramRequest(action, payload = {}) {
  const resp = await fetch("/api/telegram", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, ...payload }),
  });
  const data = await resp.json();
  if (!resp.ok || !data.ok) throw new Error(data.description || data.error || `Telegram ${action} failed`);
  return data;
}

async function sendTelegramBridge(text) {
  if (!appState.telegram.enabled || !text?.trim()) return;
  try {
    await telegramRequest("send", { text: text.trim().slice(0, 3900) });
  } catch (error) {
    const status = document.querySelector("[data-role='telegram-status']");
    if (status) status.textContent = `${lang() === "zh" ? "Telegram 发送失败" : "Telegram send failed"}: ${error.message || error}`;
  }
}

async function pollTelegramUpdates({ process = true } = {}) {
  if (appState.telegram.polling) return;
  appState.telegram.polling = true;
  try {
    const data = await telegramRequest("updates", appState.telegram.offset ? { offset: appState.telegram.offset } : {});
    if (data.next_offset) appState.telegram.offset = data.next_offset;
    const updates = data.updates || [];
    const status = document.querySelector("[data-role='telegram-status']");
    if (status) {
      status.textContent = updates.length
        ? (lang() === "zh" ? `Telegram 已读取 ${updates.length} 条新消息` : `Telegram loaded ${updates.length} new message(s)`)
        : (lang() === "zh" ? "Telegram 已连接，等待新消息" : "Telegram connected, waiting for new messages");
    }
    if (!process) return;
    for (const update of updates) {
      if (!update.text || !appState.submitters.home) continue;
      await appState.submitters.home(update.text, { fromTelegram: true, source: update.from || "Telegram" });
    }
  } catch (error) {
    const status = document.querySelector("[data-role='telegram-status']");
    if (status) status.textContent = `${lang() === "zh" ? "Telegram 读取失败" : "Telegram read failed"}: ${error.message || error}`;
  } finally {
    appState.telegram.polling = false;
  }
}

async function ensureTelegramBridge() {
  const composer = document.getElementById("homeInput")?.closest(".composer");
  if (!composer || composer.querySelector(".telegram-bridge-row")) return;
  const row = document.createElement("div");
  row.className = "telegram-bridge-row";
  row.innerHTML = `
    <div class="telegram-bridge-main">
      <strong>${lang() === "zh" ? "Telegram 双向连接" : "Telegram Bridge"}</strong>
      <span data-role="telegram-status">${lang() === "zh" ? "正在连接 Telegram..." : "Connecting Telegram..."}</span>
    </div>
    <div class="telegram-bridge-actions">
      <label class="telegram-toggle">
        <input type="checkbox" data-role="telegram-toggle" checked>
        <span>${lang() === "zh" ? "同步人机交流" : "Sync Human Exchange"}</span>
      </label>
      <button class="btn btn-ghost telegram-pull" type="button" data-role="telegram-pull">${lang() === "zh" ? "读取 Telegram" : "Pull Telegram"}</button>
    </div>
  `;
  composer.insertAdjacentElement("afterbegin", row);
  const toggle = row.querySelector("[data-role='telegram-toggle']");
  const pull = row.querySelector("[data-role='telegram-pull']");
  toggle?.addEventListener("change", () => {
    appState.telegram.enabled = Boolean(toggle.checked);
  });
  pull?.addEventListener("click", () => pollTelegramUpdates({ process: true }));
  try {
    const status = await telegramRequest("status");
    appState.telegram.status = status;
    const label = row.querySelector("[data-role='telegram-status']");
    if (label) {
      label.textContent = lang() === "zh"
        ? `已连接 @${status.bot?.username || "Telegram Bot"}`
        : `Connected @${status.bot?.username || "Telegram Bot"}`;
    }
    await pollTelegramUpdates({ process: false });
    appState.telegram.timer = setInterval(() => {
      if (appState.telegram.enabled && appState.currentPage === "home") pollTelegramUpdates({ process: true });
    }, 15000);
  } catch (error) {
    const label = row.querySelector("[data-role='telegram-status']");
    if (label) label.textContent = `${lang() === "zh" ? "Telegram 连接失败" : "Telegram connection failed"}: ${error.message || error}`;
  }
}

function runQuickWorkspaceAction(action, skillId, input, messages, metaGetter) {
  const [label, detail, prompt, special] = action;
  if (special === "image") {
    const source = input.value.trim() || prompt;
    const meta = metaGetter();
    const mode = appState.routeState.finance?.mode || meta.modes?.[0]?.[0] || "";
    const aspect = inferImageAspect(source, mode);
    const url = pollinationsImageUrl(source, aspect);
    appendHtmlMessage(messages, imageDraftMarkup(source, url), "assistant");
    return;
  }
  if (special) {
    runSlackWorkspaceAction(special, input, messages);
    return;
  }
  const meta = metaGetter();
  const currentText = input.value.trim();
  input.value = currentText
    ? `${prompt}\n\n${currentText}`
    : `${prompt}\n\n${lang() === "zh" ? "请在这里粘贴材料或补充背景。" : "Paste the source material or add context here."}`;
  input.focus();
  appendMessage(
    messages,
    lang() === "zh"
      ? `已载入「${label}」动作：${detail} 你可以直接发送，Hermes 会按 ${meta.name} 处理。`
      : `Loaded "${label}": ${detail} You can send it now and Hermes will process it through ${meta.name}.`,
    "assistant"
  );
}

function progressPercentLabel(percent) {
  return `${Math.max(0, Math.min(100, Math.round(Number(percent) || 0)))}%`;
}

function upsertIoProgress(workspaceKey, record) {
  const list = appState.ioProgress[workspaceKey] || (appState.ioProgress[workspaceKey] = []);
  const idx = list.findIndex((item) => item.id === record.id);
  const next = { ...(idx >= 0 ? list[idx] : {}), ...record, updatedAt: Date.now() };
  if (idx >= 0) {
    list[idx] = next;
  } else {
    list.unshift(next);
  }
  appState.ioProgress[workspaceKey] = list.slice(0, 8);
  renderIoProgress(workspaceKey);
}

function renderIoProgress(workspaceKey) {
  const body = document.querySelector(`#${workspaceKey} [data-role='io-progress-body']`);
  if (!body) return;
  const rows = appState.ioProgress[workspaceKey] || [];
  if (!rows.length) {
    body.innerHTML = `<tr><td colspan="4" class="io-progress__empty">${lang() === "zh" ? "上传、导出和下载进度会显示在这里。" : "Upload, export, and download progress will appear here."}</td></tr>`;
    return;
  }
  body.innerHTML = rows.map((item) => `
    <tr>
      <td>${escapeHtml(item.file || item.label || "-")}</td>
      <td>${escapeHtml(item.status || "-")}</td>
      <td>${escapeHtml(progressPercentLabel(item.progress))}</td>
      <td>${escapeHtml(item.type || "-")}</td>
    </tr>
  `).join("");
}

function ensureSidebarProgressPanel(workspaceKey) {
  if (workspaceKey === "home") return;
  const root = document.getElementById(workspaceKey);
  const side = root?.querySelector(".workspace-side");
  if (!side) return;
  let panel = side.querySelector(".io-progress-panel");
  if (!panel) {
    panel = document.createElement("div");
    panel.className = "io-progress-panel";
    panel.innerHTML = `
      <div class="side-title">${lang() === "zh" ? "处理进度表" : "Processing Progress"}</div>
      <div class="io-progress__table-wrap">
        <table class="io-progress__table">
          <thead>
            <tr>
              <th>${lang() === "zh" ? "文件 / 任务" : "File / Task"}</th>
              <th>${lang() === "zh" ? "状态" : "Status"}</th>
              <th>${lang() === "zh" ? "进度" : "Progress"}</th>
              <th>${lang() === "zh" ? "类型" : "Type"}</th>
            </tr>
          </thead>
          <tbody data-role="io-progress-body"></tbody>
        </table>
      </div>
    `;
    const upload = side.querySelector(".upload");
    if (upload) {
      upload.insertAdjacentElement("beforebegin", panel);
    } else {
      side.appendChild(panel);
    }
  }
  renderIoProgress(workspaceKey);
}

async function readAttachmentSummary(file, onProgress) {
  let preview = "";
  const textLike = file.type.startsWith("text/") || /\.(txt|md|csv|json|xml|yaml|yml)$/i.test(file.name);
  if (textLike) {
    try {
      preview = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onprogress = (event) => {
          if (event.lengthComputable && typeof onProgress === "function") {
            onProgress(Math.round((event.loaded / event.total) * 100));
          }
        };
        reader.onload = () => resolve(String(reader.result || "").slice(0, 2200));
        reader.onerror = () => reject(reader.error || new Error("read_failed"));
        reader.readAsText(file);
      });
    } catch {}
  } else if (typeof onProgress === "function") {
    onProgress(100);
  }
  return {
    name: file.name,
    size: file.size,
    preview,
    textLike,
  };
}

async function imageFileMeta(file, onProgress) {
  const base64 = await fileToBase64(file, onProgress);
  const mime = file.type || "image/png";
  const dataUrl = `data:${mime};base64,${base64}`;
  const dimensions = await new Promise((resolve) => {
    try {
      const img = new Image();
      img.onload = () => resolve({ width: img.naturalWidth || 0, height: img.naturalHeight || 0 });
      img.onerror = () => resolve({ width: 0, height: 0 });
      img.src = dataUrl;
    } catch {
      resolve({ width: 0, height: 0 });
    }
  });
  return { base64, dataUrl, mime, ...dimensions };
}

async function fileToBase64(file, onProgress) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onprogress = (event) => {
      if (event.lengthComputable && typeof onProgress === "function") {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    };
    reader.onload = () => {
      const result = String(reader.result || "");
      const base64 = result.includes(",") ? result.split(",").pop() : result;
      resolve(base64 || "");
    };
    reader.onerror = () => reject(reader.error || new Error("base64_failed"));
    reader.readAsDataURL(file);
  });
}

function attachmentContext(workspaceKey) {
  const items = appState.attachments[workspaceKey] || [];
  if (!items.length) return "";
  return items
    .map((item) => {
      if (item.imageDataUrl) {
        const dim = item.width && item.height ? ` ${item.width}x${item.height}` : "";
        return lang() === "zh"
          ? `[图片附件] ${item.name}${dim}\n请直接阅读图片中的内容、结构、表格、界面或图示，并结合用户问题作答。`
          : `[Image Attachment] ${item.name}${dim}\nPlease read the image content, layout, table, interface, or diagram directly and answer accordingly.`;
      }
      if (item.preview) return `[Attachment Summary] ${item.name}\n${item.preview}`;
      const hint = item.textLike
        ? ""
        : (lang() === "zh" ? "\n[二进制文件已附加，当前仅带文件名与大小，尚未抽取正文]" : "\n[Binary file attached. Only filename and size are attached; body text is not extracted yet.]");
      return `[Attachment] ${item.name}${hint}`;
    })
    .join("\n\n")
    .slice(0, 6000);
}

function attachmentImageParts(workspaceKey) {
  const items = appState.attachments[workspaceKey] || [];
  return items
    .filter((item) => item.imageDataUrl)
    .flatMap((item) => {
      const dim = item.width && item.height ? ` ${item.width}x${item.height}` : "";
      const note = lang() === "zh"
        ? `[图片附件] ${item.name}${dim}`
        : `[Image Attachment] ${item.name}${dim}`;
      return [
        { type: "text", text: note },
        { type: "image_url", image_url: { url: item.imageDataUrl } },
      ];
    });
}

async function attachFileToWorkspace(workspaceKey, file, onUpdate, metadata = {}) {
  const progressId = `${workspaceKey}-upload-${file.name}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  const emit = (patch = {}) => {
    if (typeof onUpdate === "function") onUpdate(patch);
  };
  upsertIoProgress(workspaceKey, {
    id: progressId,
    file: file.name,
    type: lang() === "zh" ? "上传" : "Upload",
    status: lang() === "zh" ? "读取中" : "Reading",
    progress: 0,
  });
  emit({ status: lang() === "zh" ? `正在读取：${file.name}` : `Reading: ${file.name}` });
  const summary = await readAttachmentSummary(file, (percent) => {
    upsertIoProgress(workspaceKey, {
      id: progressId,
      file: file.name,
      type: lang() === "zh" ? "上传" : "Upload",
      status: lang() === "zh" ? "读取中" : "Reading",
      progress: percent,
    });
    emit({ progress: percent });
  });
  if (file.type.startsWith("image/") && file.size <= 12 * 1024 * 1024) {
    upsertIoProgress(workspaceKey, {
      id: progressId,
      file: file.name,
      type: lang() === "zh" ? "上传" : "Upload",
      status: lang() === "zh" ? "处理中" : "Preparing image",
      progress: 82,
    });
    try {
      const imageMeta = await imageFileMeta(file, (percent) => {
        upsertIoProgress(workspaceKey, {
          id: progressId,
          file: file.name,
          type: lang() === "zh" ? "上传" : "Upload",
          status: lang() === "zh" ? "编码图片中" : "Encoding image",
          progress: Math.min(95, Math.max(82, percent)),
        });
      });
      summary.imageDataUrl = imageMeta.dataUrl;
      summary.mime = imageMeta.mime;
      summary.width = imageMeta.width;
      summary.height = imageMeta.height;
      summary.preview = lang() === "zh"
        ? `图片已附加，可直接读取。${imageMeta.width && imageMeta.height ? `尺寸 ${imageMeta.width}x${imageMeta.height}。` : ""}`
        : `Image attached and ready for direct reading.${imageMeta.width && imageMeta.height ? ` Size ${imageMeta.width}x${imageMeta.height}.` : ""}`;
    } catch {}
  }
  if (!summary.preview && /\.(pdf|docx|docm|xlsx|xlsm|pptx|pptm|pages|numbers|key|rtf)$/i.test(file.name) && file.size <= 12 * 1024 * 1024) {
    upsertIoProgress(workspaceKey, {
      id: progressId,
      file: file.name,
      type: lang() === "zh" ? "上传" : "Upload",
      status: lang() === "zh" ? "抽取正文中" : "Extracting text",
      progress: 85,
    });
    emit({ status: lang() === "zh" ? `正在提取：${file.name}` : `Extracting: ${file.name}` });
    try {
      const base64 = await fileToBase64(file, (percent) => {
        upsertIoProgress(workspaceKey, {
          id: progressId,
          file: file.name,
          type: lang() === "zh" ? "上传" : "Upload",
          status: lang() === "zh" ? "编码文件中" : "Encoding file",
          progress: Math.min(95, Math.max(85, percent)),
        });
      });
      const resp = await fetch("/api/attachment/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename: file.name,
          mime: file.type || "",
          base64,
          skill_id: currentWorkspaceSkillId(workspaceKey),
        }),
      });
      const data = await resp.json();
      if (resp.ok && data.ok && data.preview) {
        summary.preview = data.preview;
      }
    } catch {}
  }
  Object.assign(summary, metadata || {});
  appState.attachments[workspaceKey].push(summary);
  upsertIoProgress(workspaceKey, {
    id: progressId,
    file: file.name,
    type: lang() === "zh" ? "上传" : "Upload",
    status: summary.preview
      ? (lang() === "zh" ? "已完成并提取摘要" : "Completed with summary")
      : (lang() === "zh" ? "已附加" : "Attached"),
    progress: 100,
  });
  emit({
    status: summary.preview
      ? (lang() === "zh" ? `已附加并提取：${file.name}` : `Attached with summary: ${file.name}`)
      : (lang() === "zh" ? `已附加：${file.name}` : `Attached: ${file.name}`),
  });
  return summary;
}

function bindWorkspaceFilePicker(workspaceKey, inputId, nameId, statusId) {
  const input = document.getElementById(inputId);
  const nameNode = document.getElementById(nameId);
  const statusNode = document.getElementById(statusId);
  if (!input || input.dataset.bound === "1") return;
  input.dataset.bound = "1";

  const render = () => {
    const items = appState.attachments[workspaceKey] || [];
    if (nameNode) {
      nameNode.textContent = items.length
        ? `${lang() === "zh" ? "最近附件：" : "Latest attachment: "}${items.map((item) => item.name).join(", ")}`
        : (lang() === "zh" ? "最近附件：尚未上传文件。" : "Latest attachment: no file uploaded yet.");
    }
    if (statusNode) {
      statusNode.textContent = items.length
        ? `${items.length} ${lang() === "zh" ? "个文件" : "file(s)"}`
        : "Waiting";
    }
  };

  input.addEventListener("change", async () => {
    const files = Array.from(input.files || []);
    for (const file of files) {
      await attachFileToWorkspace(workspaceKey, file);
    }
    render();
    input.value = "";
  });

  render();
}

function currentWorkspaceSkillId(workspaceKey) {
  const key = effectiveWorkspaceKey(workspaceKey);
  if (key === "finance") return appState.currentSkillId;
  if (key === "legal") return new URLSearchParams(location.search).get("platform") || "uk_hk_financial_contract_counsel";
  if (key === "doc-flow") return "document-review";
  if (key === "ai-agent") return "external-ai8-agent";
  return appState.currentSkillId || "financial-analysis";
}

function conversationScopeKey(workspaceKey) {
  if (workspaceKey === "home") return "home";
  return `${workspaceKey}:${currentWorkspaceSkillId(workspaceKey)}`;
}

function rememberWorkspaceOutput(workspaceKey, prompt, result, meta) {
  appState.outputs[workspaceKey] = {
    workspace: workspaceKey,
    skillId: currentWorkspaceSkillId(workspaceKey),
    title: `${meta.name || pageTitleLabel(workspaceKey)} ${lang() === "zh" ? "输出" : "Output"}`,
    prompt: String(prompt || "").trim(),
    result: String(result || "").trim(),
    attachments: (appState.attachments[workspaceKey] || []).map((item) => ({ ...item })),
    updatedAt: new Date().toISOString(),
    lastExport: appState.outputs[workspaceKey]?.lastExport || null,
  };
}

function preferredExportFormat(workspaceKey) {
  if (workspaceKey === "legal") return "docx";
  const skillId = currentWorkspaceSkillId(workspaceKey);
  if (["financial-report-summary", "pdf-excel-analysis", "am_reporting_engine"].includes(skillId)) return "xlsx";
  if (["document-review", "client-follow-up-weekly-update", "humanizer", "due-diligence-web-research", "financial-analysis", "banking-sblc", "mckinsey-thinking", "obsidian-notion", "google-workspace", "slack-collaboration"].includes(skillId)) return "docx";
  if (["composio-workspace"].includes(skillId)) return "md";
  if (["free-image-draft"].includes(skillId)) return "pptx";
  return "md";
}

function routeProviderModels(providerKey) {
  if (providerKey === "auto") return ["auto-smart"];
  return providerMetaMap()[providerKey]?.models || [];
}

const SKILL_FIXED_DEFAULT_ROUTE_TABLE = {
  "uk_hk_financial_contract_counsel": [
    { provider: "chatgpt", models: ["gpt-5.4", "gpt-5.4-mini"] },
    { provider: "google-gemini-cli", models: ["gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview"] },
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
  ],
  "financial-analysis": [
    { provider: "chatgpt", models: ["gpt-5.4-mini", "gpt-5.4"] },
    { provider: "google-gemini-cli", models: ["gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview"] },
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
  ],
  "financial-report-summary": [
    { provider: "chatgpt", models: ["gpt-5.4-mini", "gpt-5.4"] },
    { provider: "google-gemini-cli", models: ["gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview"] },
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
  ],
  "due-diligence-web-research": [
    { provider: "chatgpt", models: ["gpt-5.4-mini", "gpt-5.4"] },
    { provider: "google-gemini-cli", models: ["gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview"] },
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
  ],
  "document-review": [
    { provider: "chatgpt", models: ["gpt-5.4-mini", "gpt-5.4"] },
    { provider: "google-gemini-cli", models: ["gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview"] },
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
  ],
  "pdf-excel-analysis": [
    { provider: "chatgpt", models: ["gpt-5.4-mini", "gpt-5.4"] },
    { provider: "google-gemini-cli", models: ["gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview"] },
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
  ],
  "banking-sblc": [
    { provider: "chatgpt", models: ["gpt-5.4-mini", "gpt-5.4"] },
    { provider: "google-gemini-cli", models: ["gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview"] },
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
  ],
  "banking-dlc": [
    { provider: "chatgpt", models: ["gpt-5.4-mini", "gpt-5.4"] },
    { provider: "google-gemini-cli", models: ["gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview"] },
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
  ],
  "mckinsey-thinking": [
    { provider: "chatgpt", models: ["gpt-5.4-mini", "gpt-5.4"] },
    { provider: "google-gemini-cli", models: ["gemini-3.1-flash-lite-preview", "gemini-3.1-pro-preview"] },
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
  ],
  "google-workspace": [
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
    { provider: "lmstudio", models: [] },
    { provider: "chatgpt", models: ["gpt-5.4-mini"] },
  ],
  "composio-workspace": [
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
    { provider: "lmstudio", models: [] },
    { provider: "chatgpt", models: ["gpt-5.4-mini"] },
  ],
  "obsidian-notion": [
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
    { provider: "lmstudio", models: [] },
    { provider: "chatgpt", models: ["gpt-5.4-mini"] },
  ],
  "client-follow-up-weekly-update": [
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
    { provider: "lmstudio", models: [] },
    { provider: "chatgpt", models: ["gpt-5.4-mini"] },
  ],
  "slack-collaboration": [
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
    { provider: "lmstudio", models: [] },
    { provider: "chatgpt", models: ["gpt-5.4-mini"] },
  ],
  "humanizer": [
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
    { provider: "lmstudio", models: [] },
    { provider: "chatgpt", models: ["gpt-5.4-mini"] },
  ],
  "free-image-draft": [
    { provider: "chatgpt", models: ["gpt-5.4", "gpt-5.4-mini"] },
    { provider: "nvidia", models: ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"] },
  ],
};

function skillRiskTier(skillId) {
  const highRiskSkills = new Set([
    "uk_hk_financial_contract_counsel",
    "financial-analysis",
    "financial-report-summary",
    "due-diligence-web-research",
    "document-review",
    "pdf-excel-analysis",
    "am_reporting_engine",
    "pe_insight_master",
  ]);
  const lowRiskSkills = new Set([
    "humanizer",
    "client-follow-up-weekly-update",
    "slack-collaboration",
    "obsidian-notion",
    "google-workspace",
    "composio-workspace",
  ]);
  if (highRiskSkills.has(skillId)) return "high";
  if (lowRiskSkills.has(skillId)) return "low";
  return "medium";
}

function estimateTaskComplexity(text, options = {}) {
  const raw = String(text || "").trim();
  const chars = raw.length;
  const lines = raw ? raw.split(/\n+/).length : 0;
  const attachmentsCount = Number(options.attachmentsCount || 0);
  if (options.hasImages) return "complex";
  if (attachmentsCount >= 2) return "complex";
  if (chars > 1200 || lines > 12) return "complex";
  if (chars > 240 || lines > 4) return "medium";
  if (/\b(compare|analyze|review|summarize|forecast|风险|尽调|审阅|合同|财报|报告)\b/i.test(raw)) return "medium";
  return "simple";
}

function selectEnabledRoute(providerMap, provider, preferredModels = [], fallbackModel = "") {
  const meta = providerMap[provider];
  if (!meta?.enabled) return null;
  const models = Array.isArray(meta.models) ? meta.models : [];
  const model = preferredModels.find((item) => models.includes(item)) || models[0] || fallbackModel || "";
  return model ? { provider, model } : null;
}

function skillPreferredRoute(workspaceKey, providerMap) {
  const skillId = currentWorkspaceSkillId(workspaceKey);
  const config = currentSkillConfig(skillId);
  const routing = config?.routing || {};
  const preferredProvider = String(routing.preferred_channel || "").trim();
  const preferredModel = String(routing.preferred_model || "").trim();
  const fallbackProvider = String(routing.fallback_channel || "").trim();
  if (preferredProvider) {
    const hit = selectEnabledRoute(
      providerMap,
      preferredProvider,
      preferredModel ? [preferredModel] : [],
      preferredModel
    );
    if (hit) return hit;
  }
  if (fallbackProvider) {
    const hit = selectEnabledRoute(providerMap, fallbackProvider);
    if (hit) return hit;
  }
  return null;
}

function fixedSkillRoute(skillId, providerMap) {
  const candidates = SKILL_FIXED_DEFAULT_ROUTE_TABLE[skillId] || [];
  for (const candidate of candidates) {
    const route = selectEnabledRoute(providerMap, candidate.provider, candidate.models || []);
    if (route) return route;
  }
  return null;
}

function preferredChatRoute(workspaceKey, route, options = {}) {
  const providerMap = appState.status?.providers || {};
  const skillId = currentWorkspaceSkillId(workspaceKey);
  const riskTier = skillRiskTier(skillId);
  const complexity = estimateTaskComplexity(options.promptText || "", options);
  const manualOverride = Boolean(route?.manual_override && route?.provider && route?.provider !== "auto");
  const stableProvider = providerMap.nvidia?.enabled ? "nvidia" : (appState.status?.current_provider || "chatgpt");
  const stableModel = stableProvider === "nvidia" ? "minimaxai/minimax-m2.7" : (appState.status?.current_model || "");
  const provider = manualOverride ? (route?.provider || stableProvider) : stableProvider;
  const model = manualOverride ? (route?.model || stableModel) : stableModel;
  if (options.hasImages) {
    const imageRoute = selectEnabledRoute(providerMap, "chatgpt", ["gpt-5.4", "gpt-5.4-mini"], "gpt-5.4");
    return imageRoute || { provider, model, fastHomeRoute: workspaceKey === "home" };
  }
  if (manualOverride) {
    return { provider, model, fastHomeRoute: workspaceKey === "home" && provider !== "google-gemini-cli" && provider !== "gemini" };
  }
  const fixedRoute = fixedSkillRoute(skillId, providerMap);
  if (fixedRoute) {
    return { provider: fixedRoute.provider, model: fixedRoute.model, fastHomeRoute: workspaceKey === "home" };
  }
  const skillRoute = skillPreferredRoute(workspaceKey, providerMap);

  const simpleLowCost = [
    skillRoute,
    selectEnabledRoute(providerMap, "lmstudio"),
    selectEnabledRoute(providerMap, "google-gemini-cli", ["gemini-3.1-flash-lite-preview", "gemini-2.5-flash"]),
    selectEnabledRoute(providerMap, "nvidia", ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"]),
    selectEnabledRoute(providerMap, "chatgpt", ["gpt-5.4-mini"]),
  ].filter(Boolean);
  const mediumQuality = [
    skillRoute,
    selectEnabledRoute(providerMap, "chatgpt", ["gpt-5.4-mini"]),
    selectEnabledRoute(providerMap, "google-gemini-cli", ["gemini-3.1-flash-lite-preview", "gemini-3.1-pro-preview"]),
    selectEnabledRoute(providerMap, "nvidia", ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"]),
  ].filter(Boolean);
  const highQuality = [
    selectEnabledRoute(providerMap, "chatgpt", ["gpt-5.4-mini", "gpt-5.4"]),
    selectEnabledRoute(providerMap, "google-gemini-cli", ["gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview"]),
    skillRoute,
    selectEnabledRoute(providerMap, "nvidia", ["minimaxai/minimax-m2.7", "minimax2.7", "minimax-m2.7"]),
  ].filter(Boolean);

  let autoRoute = null;
  if (riskTier === "high" || complexity === "complex") {
    const preferStrong = complexity === "complex"
      ? selectEnabledRoute(providerMap, "chatgpt", ["gpt-5.4", "gpt-5.4-mini"])
      : null;
    autoRoute = preferStrong || highQuality[0] || null;
  } else if (complexity === "simple" && riskTier === "low") {
    autoRoute = simpleLowCost[0] || null;
  } else {
    autoRoute = mediumQuality[0] || null;
  }
  if (!autoRoute) {
    autoRoute = selectEnabledRoute(providerMap, stableProvider, [stableModel], stableModel) || { provider: stableProvider, model: stableModel };
  }

  if (workspaceKey === "home" && ["google-gemini-cli", "gemini", ""].includes(autoRoute.provider)) {
    if (providerMap.chatgpt?.enabled) {
      return { provider: "chatgpt", model: "gpt-5.4-mini", fastHomeRoute: true };
    }
    if (providerMap.nvidia?.enabled) {
      return { provider: "nvidia", model: (providerMap.nvidia.models || [])[0] || "minimaxai/minimax-m2.7", fastHomeRoute: true };
    }
  }
  return { provider: autoRoute.provider, model: autoRoute.model, fastHomeRoute: workspaceKey === "home" };
}

function looksLikeImageBlindReply(text) {
  const value = String(text || "").toLowerCase();
  return [
    "can't see the image",
    "cannot see the image",
    "can't view the image",
    "cannot view the image",
    "i can't access the image",
    "i can’t access the image",
    "i can’t see the image",
    "i can't see the actual content",
    "看不到这张图片",
    "看不到附件图片",
    "无法看到图片",
    "我现在看不到",
  ].some((token) => value.includes(token));
}

function providerMetaMap() {
  return appState.status?.providers || {};
}

function routeProviderOptions() {
  const options = Object.entries(providerMetaMap()).filter(([, value]) => !value?.fallback_only);
  return [["auto", { label: lang() === "zh" ? "自动智能（省成本）" : "Auto Smart (Cost Saver)", models: ["auto-smart"] }], ...options];
}

function routeProviderHint(providerKey) {
  const hints = {
    auto: lang() === "zh" ? "默认按任务复杂度与 Skill 自动选最省成本通道" : "Auto-selects the lowest-cost route by task complexity and skill",
    chatgpt: lang() === "zh" ? "推荐 · 更稳更快" : "Recommended · steadier and faster",
    "google-gemini-cli": lang() === "zh" ? "实验链路 · 可能较慢" : "Experimental · may be slower",
    gemini: lang() === "zh" ? "API 链路 · 需单独配置" : "API route · separate setup",
    lmstudio: lang() === "zh" ? "本地模型" : "Local model",
    nvidia: lang() === "zh" ? "默认链路 · 低成本优先" : "Default route · cost-first",
  };
  return hints[providerKey] || (lang() === "zh" ? "可用通道" : "Available route");
}

function routeModelHint(providerKey, modelKey) {
  if (providerKey === "auto" || modelKey === "auto-smart") {
    return lang() === "zh"
      ? "auto-smart：按任务复杂度与 Skill 自动分配模型"
      : "auto-smart: auto-select model by task complexity and skill";
  }
  if (providerKey === "nvidia") {
    return lang() === "zh" ? "低成本优先模型池" : "Cost-first model pool";
  }
  if (providerKey === "chatgpt") {
    return lang() === "zh" ? "高质量优先模型池" : "Quality-first model pool";
  }
  if (providerKey === "gemini") {
    return lang() === "zh" ? "Gemini 可用模型池" : "Gemini model pool";
  }
  return lang() === "zh" ? "按通道加载模型" : "Models loaded by channel";
}

function routeProviderBadge(providerKey) {
  const labels = {
    auto: lang() === "zh" ? "自动智能" : "Auto Smart",
    chatgpt: lang() === "zh" ? "ChatGPT 推荐" : "ChatGPT Recommended",
    "google-gemini-cli": lang() === "zh" ? "Gemini 实验" : "Gemini Experimental",
    gemini: lang() === "zh" ? "Gemini API" : "Gemini API",
    lmstudio: lang() === "zh" ? "LM Studio 本地" : "LM Studio Local",
    nvidia: lang() === "zh" ? "默认通道" : "Default Route",
  };
  return labels[providerKey] || (lang() === "zh" ? "当前路由" : "Current Route");
}

function routeButtonText(providerKey) {
  return lang() === "zh"
    ? `路由设置 · ${routeProviderBadge(providerKey)}`
    : `Route · ${routeProviderBadge(providerKey)}`;
}

function refreshRouteButtonLabel(workspaceKey) {
  const root = document.getElementById(workspaceKey);
  const button = root?.querySelector(".tool-row .tool-btn[data-menu='route']");
  if (!button) return;
  const effectiveKey = effectiveWorkspaceKey(workspaceKey);
  const route = appState.routeState[effectiveKey] || {};
  const resolved = preferredChatRoute(workspaceKey, route, { hasImages: false });
  button.textContent = routeButtonText(resolved.provider || "chatgpt");
}

function composerRouteLineText(workspaceKey) {
  const effectiveKey = effectiveWorkspaceKey(workspaceKey);
  const route = appState.routeState[effectiveKey] || {};
  const resolved = preferredChatRoute(workspaceKey, route, { hasImages: false });
  const providerLabel = providerMetaMap()[resolved.provider]?.label || resolved.provider || "ChatGPT (Auth)";
  const modelLabel = resolved.model || (resolved.provider === "chatgpt" ? "gpt-5.4-mini" : "");
  const routeLabel = appState.routeStatus || (lang() === "zh" ? "直连" : "Direct");
  return lang() === "zh"
    ? `当前通道：${providerLabel}${modelLabel ? ` · ${modelLabel}` : ""} · ${routeLabel}`
    : `Current: ${providerLabel}${modelLabel ? ` · ${modelLabel}` : ""} · ${routeLabel}`;
}

function refreshComposerRouteLine(workspaceKey) {
  const root = document.getElementById(workspaceKey);
  const node = root?.querySelector("[data-role='composer-route-line']");
  if (!node) return;
  node.textContent = composerRouteLineText(workspaceKey);
}

function refreshAllRouteButtons() {
  ["home", "finance", "legal"].forEach((key) => refreshRouteButtonLabel(key));
}

function refreshAllComposerRouteLines() {
  ["home", "finance", "legal"].forEach((key) => refreshComposerRouteLine(key));
}

function supervisionStateLabel(state) {
  const key = String(state || "").toLowerCase();
  if (lang() === "zh") {
    if (key === "on-track") return "执行正常";
    if (key === "attention") return "重点关注";
    if (key === "risk") return "风险状态";
    return "待更新";
  }
  if (key === "on-track") return "On Track";
  if (key === "attention") return "Attention";
  if (key === "risk") return "At Risk";
  return "Pending";
}

function renderSprintSupervision() {
  const sprint = appState.status?.sprint_supervision || {};
  const projects = Array.isArray(sprint.projects) ? sprint.projects : [];
  const summaries = Array.isArray(sprint.project_summaries) ? sprint.project_summaries : [];
  const select = document.querySelector("[data-role='sprint-project-select']");
  if (projects.length && select) {
    const optionsHtml = projects.map((project) => {
      const key = String(project?.key || "");
      const label = String(project?.label || key || (lang() === "zh" ? "项目" : "Project"));
      return `<option value="${escapeHtml(key)}">${escapeHtml(label)}</option>`;
    }).join("");
    if (select.innerHTML !== optionsHtml) {
      select.innerHTML = optionsHtml;
    }
    const fallbackProject = String(projects[0]?.key || "");
    const selected = appState.enterprise.selectedProject || String(sprint.active_project || fallbackProject);
    appState.enterprise.selectedProject = projects.some((project) => String(project?.key || "") === selected) ? selected : fallbackProject;
    select.value = appState.enterprise.selectedProject;
    if (!select.dataset.bound) {
      select.addEventListener("change", () => {
        appState.enterprise.selectedProject = select.value || fallbackProject;
        renderSprintSupervision();
      });
      select.dataset.bound = "1";
    }
  }
  const activeKey = appState.enterprise.selectedProject || String(sprint.active_project || (projects[0]?.key || ""));
  const activeProject = projects.find((project) => String(project?.key || "") === activeKey) || {};
  const activeSummary = summaries.find((item) => String(item?.key || "") === activeKey) || {};
  const items = Array.isArray(activeProject.items) ? activeProject.items : (Array.isArray(sprint.items) ? sprint.items : []);
  const dayTotal = Math.max(1, Number(activeSummary.day_total || items.length || sprint.day_total || 14));
  const dayCompleted = Math.max(0, Number(activeSummary.day_completed || items.filter((item) => String(item?.status || "").toLowerCase() === "done").length || sprint.day_completed || 0));
  const dayBlocked = Math.max(0, Number(activeSummary.day_blocked || items.filter((item) => String(item?.status || "").toLowerCase() === "blocked").length || 0));
  const progressText = `${dayCompleted}/${dayTotal}`;
  const effectScore = Math.max(0, Math.min(100, Number(activeSummary.implementation_effect_score || sprint.implementation_effect_score || 0)));
  const stateText = supervisionStateLabel(dayBlocked > 0 ? "risk" : (dayCompleted >= dayTotal ? "on-track" : "attention"));
  const acceptanceText = (activeSummary.acceptance_passed ?? sprint.acceptance_passed)
    ? (lang() === "zh" ? "已通过" : "Passed")
    : (lang() === "zh" ? "待收口" : "Pending");
  const closeoutSummary = String(activeProject.closeout_summary || sprint.closeout_summary || "").trim() || (
    lang() === "zh"
      ? "项目收尾摘要待生成。"
      : "Closeout summary is pending."
  );
  const nextImprovement = String(activeProject.next_improvement || sprint.next_improvement || "").trim() || (
    lang() === "zh"
      ? "下一步改进建议待生成。"
      : "Next improvement recommendation is pending."
  );
  document.querySelectorAll("[data-bind='sprint-progress']").forEach((node) => node.textContent = progressText);
  document.querySelectorAll("[data-bind='supervision-state']").forEach((node) => node.textContent = stateText);
  document.querySelectorAll("[data-bind='implementation-effect']").forEach((node) => node.textContent = `${effectScore}%`);
  document.querySelectorAll("[data-bind='acceptance-state']").forEach((node) => node.textContent = acceptanceText);
  document.querySelectorAll("[data-bind='closeout-summary']").forEach((node) => node.textContent = closeoutSummary);
  document.querySelectorAll("[data-bind='next-improvement']").forEach((node) => node.textContent = nextImprovement);
  const timelineNode = document.querySelector("[data-bind='sprint-timeline']");
  if (!timelineNode) return;
  if (!items.length) {
    timelineNode.innerHTML = `<p class="enterprise-monitor__empty">${lang() === "zh" ? "监督进度等待同步。" : "Supervision progress is waiting to sync."}</p>`;
    return;
  }
  timelineNode.innerHTML = items.map((item) => {
    const status = String(item?.status || "pending").toLowerCase();
    const badge = status === "done"
      ? (lang() === "zh" ? "完成" : "Done")
      : status === "blocked"
        ? (lang() === "zh" ? "阻塞" : "Blocked")
        : (lang() === "zh" ? "进行中" : "In Progress");
    const title = String(item?.title || "");
    const day = Number(item?.day || 0);
    return `
      <div class="enterprise-monitor__item" data-status="${escapeHtml(status)}">
        <span class="enterprise-monitor__day">${lang() === "zh" ? `第${day}天` : `Day ${day}`}</span>
        <strong>${escapeHtml(title)}</strong>
        <em>${escapeHtml(badge)}</em>
      </div>
    `;
  }).join("");
}

function updateStatusBindings() {
  const provider = providerMetaMap()[appState.status?.current_provider]?.label || appState.status?.current_provider || "ChatGPT (Auth)";
  const model = appState.status?.current_model || "gpt-5.4-mini";
  const enterpriseKpis = appState.status?.enterprise_kpis || {};
  const fallbackPool = providerMetaMap().chatgpt?.pool_size || 0;
  const fallbackText = fallbackPool
    ? (lang() === "zh" ? `ChatGPT 备用已就绪 · ${fallbackPool}` : `ChatGPT fallback ready · ${fallbackPool}`)
    : (lang() === "zh" ? "备用链路离线" : "Fallback offline");
  const runtime = enterpriseKpis.runtime_label
    ? `${appState.status?.hermes_online ? "Ready" : "Offline"} · ${enterpriseKpis.runtime_label}`
    : (appState.status?.hermes_online ? "Ready" : "Offline");
  const routeStatus = appState.routeStatus || (lang() === "zh" ? "直连" : "Direct");
  const routeHealth = appState.status?.route_health || {};
  const routeStatusLabel = (status) => {
    const normalized = String(status || "").toLowerCase();
    if (normalized === "ready") return lang() === "zh" ? "就绪" : "ready";
    if (normalized === "cooldown") return lang() === "zh" ? "冷却" : "cooldown";
    if (normalized === "setup_required") return lang() === "zh" ? "待配置" : "setup required";
    return lang() === "zh" ? "离线" : "offline";
  };
  const healthBits = Object.entries(routeHealth).map(([key, value]) => {
    const label = providerMetaMap()[key]?.label || key;
    const status = value.status || (value.available ? "ready" : "offline");
    return `${label}: ${routeStatusLabel(status)}`;
  });
  const scoreText = Number.isFinite(Number(enterpriseKpis.health_score)) ? `Score ${enterpriseKpis.health_score}` : "";
  const healthText = healthBits.length
    ? `${healthBits.join(" · ")}${scoreText ? ` · ${scoreText}` : ""}`
    : (lang() === "zh" ? "等待状态数据" : "Waiting for status data");
  document.querySelectorAll("[data-bind='provider']").forEach((node) => node.textContent = provider);
  document.querySelectorAll("[data-bind='model']").forEach((node) => node.textContent = model);
  document.querySelectorAll("[data-bind='fallback']").forEach((node) => node.textContent = fallbackText);
  document.querySelectorAll("[data-bind='runtime']").forEach((node) => node.textContent = runtime);
  document.querySelectorAll("[data-bind='route-status']").forEach((node) => node.textContent = routeStatus);
  document.querySelectorAll("[data-bind='route-health']").forEach((node) => node.textContent = healthText);
  const healthyRoutes = Number.isFinite(Number(enterpriseKpis.ready_routes))
    ? Number(enterpriseKpis.ready_routes)
    : Object.values(routeHealth).filter((item) => item.status === "ready").length;
  const degradedRoutes = Number.isFinite(Number(enterpriseKpis.degraded_routes))
    ? Number(enterpriseKpis.degraded_routes)
    : Object.values(routeHealth).filter((item) => item.status === "cooldown").length;
  const healthScore = Number.isFinite(Number(enterpriseKpis.health_score)) ? Number(enterpriseKpis.health_score) : Math.max(0, 100 - degradedRoutes * 15);
  document.querySelectorAll("[data-bind='health-score']").forEach((node) => node.textContent = String(healthScore));
  document.querySelectorAll("[data-bind='health-ready']").forEach((node) => node.textContent = String(healthyRoutes));
  document.querySelectorAll("[data-bind='health-degraded']").forEach((node) => node.textContent = String(degradedRoutes));
  document.querySelectorAll("[data-bind='health-runtime']").forEach((node) => node.textContent = runtime);
  renderSprintSupervision();
  renderPlatformCommandStrip();
  refreshAllRouteButtons();
  refreshAllComposerRouteLines();
}

function ensureRouteStatusCards() {
  document.querySelectorAll(".compact-status").forEach((status) => {
    if (status.querySelector("[data-bind='route-status']")) return;
    const card = document.createElement("div");
    card.className = "route-status-card";
    card.innerHTML = `<span>${lang() === "zh" ? "路由" : "Route"}</span><strong data-bind="route-status">${lang() === "zh" ? "直连" : "Direct"}</strong>`;
    status.appendChild(card);
  });
}

function setRouteStatus(text) {
  appState.routeStatus = text;
  updateStatusBindings();
}

function routeStatusFromHeaders(headers) {
  const fastPath = headers.get("X-Hermes-Fast-Path");
  const fallback = headers.get("X-Hermes-Fallback") === "1";
  if (fallback && fastPath) return lang() === "zh" ? "已切备用 · 快速链路" : "Fallback · Fast Path";
  if (fallback) return lang() === "zh" ? "已自动切到备用通道" : "Fallback Active";
  if (fastPath) return lang() === "zh" ? "快速链路" : "Fast Path";
  return lang() === "zh" ? "直连" : "Direct";
}

function formatEpochSeconds(seconds) {
  if (!seconds) return lang() === "zh" ? "未运行" : "Not run yet";
  const date = new Date(seconds * 1000);
  return date.toLocaleString(lang() === "zh" ? "zh-CN" : "en-US", { hour12: false });
}

function formatEpochMs(ms) {
  if (!ms) return lang() === "zh" ? "未更新" : "No update";
  const date = new Date(ms);
  return date.toLocaleString(lang() === "zh" ? "zh-CN" : "en-US", { hour12: false });
}

function renderCronStatus(payload) {
  const newsNode = document.querySelector("[data-cron-note='news']");
  const saercNode = document.querySelector("[data-cron-note='saerc']");
  const tianNode = document.querySelector("[data-cron-note='tian']");
  const newsPill = document.querySelector("[data-cron-pill='news']");
  const saercPill = document.querySelector("[data-cron-pill='saerc']");
  const tianPill = document.querySelector("[data-cron-pill='tian']");
  const newsRun = document.querySelector("[data-cron-run='news']");
  const saercRun = document.querySelector("[data-cron-run='saerc']");
  const tianRun = document.querySelector("[data-cron-run='tian']");
  const newsHeadline = document.querySelector("[data-cron-headline='news']");
  const saercHeadline = document.querySelector("[data-cron-headline='saerc']");
  const tianHeadline = document.querySelector("[data-cron-headline='tian']");
  if (newsNode && payload?.news) {
    if (newsPill) {
      newsPill.dataset.state = payload.news.status || "UNKNOWN";
      newsPill.textContent = payload.news.status || "UNKNOWN";
    }
    if (newsRun) {
      newsRun.textContent = lang() === "zh"
        ? `最近配置：${formatEpochMs(payload.news.updated_at)}`
        : `Last config: ${formatEpochMs(payload.news.updated_at)}`;
    }
    if (newsHeadline) {
      newsHeadline.textContent = lang() === "zh"
        ? `09:00 自动生成 · ${payload.news.status}`
        : `Runs at 09:00 · ${payload.news.status}`;
    }
    newsNode.textContent = lang() === "zh"
      ? `状态：${payload.news.status} · 最近配置更新时间：${formatEpochMs(payload.news.updated_at)}`
      : `Status: ${payload.news.status} · Last config update: ${formatEpochMs(payload.news.updated_at)}`;
  }
  if (saercNode && payload?.saerc_digest) {
    if (saercPill) {
      saercPill.dataset.state = payload.saerc_digest.status || "UNKNOWN";
      saercPill.textContent = payload.saerc_digest.status || "UNKNOWN";
    }
    if (saercRun) {
      saercRun.textContent = lang() === "zh"
        ? `最近运行：${formatEpochSeconds(payload.saerc_digest.last_run)}`
        : `Last run: ${formatEpochSeconds(payload.saerc_digest.last_run)}`;
    }
    if (saercHeadline) {
      saercHeadline.textContent = lang() === "zh"
        ? `11:00 / 17:00 自动推送 · ${payload.saerc_digest.status}`
        : `Runs at 11:00 / 17:00 · ${payload.saerc_digest.status}`;
    }
    saercNode.textContent = lang() === "zh"
      ? `状态：${payload.saerc_digest.status} · 最近运行：${formatEpochSeconds(payload.saerc_digest.last_run)} · 已跟踪 ${payload.saerc_digest.seen_count} 封`
      : `Status: ${payload.saerc_digest.status} · Last run: ${formatEpochSeconds(payload.saerc_digest.last_run)} · Tracking ${payload.saerc_digest.seen_count} messages`;
  }
  if (tianNode && payload?.tian_digest) {
    if (tianPill) {
      tianPill.dataset.state = payload.tian_digest.status || "UNKNOWN";
      tianPill.textContent = payload.tian_digest.status || "UNKNOWN";
    }
    if (tianRun) {
      tianRun.textContent = lang() === "zh"
        ? `最近运行：${formatEpochSeconds(payload.tian_digest.last_run)}`
        : `Last run: ${formatEpochSeconds(payload.tian_digest.last_run)}`;
    }
    if (tianHeadline) {
      tianHeadline.textContent = lang() === "zh"
        ? `11:00 / 17:00 自动推送 · ${payload.tian_digest.status}`
        : `Runs at 11:00 / 17:00 · ${payload.tian_digest.status}`;
    }
    tianNode.textContent = lang() === "zh"
      ? `状态：${payload.tian_digest.status} · 最近运行：${formatEpochSeconds(payload.tian_digest.last_run)} · 已跟踪 ${payload.tian_digest.seen_count} 封`
      : `Status: ${payload.tian_digest.status} · Last run: ${formatEpochSeconds(payload.tian_digest.last_run)} · Tracking ${payload.tian_digest.seen_count} messages`;
  }
}

async function loadCronStatus() {
  if (!appState.auth.authenticated) return;
  try {
    const resp = await fetch("/api/cron-status", { cache: "no-store" });
    if (!resp.ok) return;
    const payload = await resp.json();
    renderCronStatus(payload);
  } catch (error) {
    console.warn("Failed to load cron status", error);
  }
}

function startCronStatusRefresh() {
  if (appState.cronStatusTimer) clearInterval(appState.cronStatusTimer);
  appState.cronStatusTimer = setInterval(() => {
    if (appState.auth.authenticated) loadCronStatus();
  }, 120000);
}

function startStatusRefresh() {
  if (appState.statusRefreshTimer) clearInterval(appState.statusRefreshTimer);
  appState.statusRefreshTimer = setInterval(() => {
    if (!appState.auth.authenticated) return;
    loadStatus().catch((error) => console.warn("Failed to refresh status", error));
  }, 45000);
}

async function loadStatus() {
  const resp = await fetch("/api/status", { cache: "no-store" });
  appState.status = await resp.json();
  ["home", "finance", "legal"].forEach((key) => {
    if (typeof appState.routeState[key].manual_override !== "boolean") appState.routeState[key].manual_override = false;
    if (!appState.routeState[key].provider) appState.routeState[key].provider = appState.status.current_provider;
    if (!appState.routeState[key].model) appState.routeState[key].model = appState.status.current_model;
  });
  updateStatusBindings();
}

async function loadGoogleWorkspaceProfiles() {
  try {
    const resp = await fetch("/api/google-workspace/profiles", { cache: "no-store" });
    if (!resp.ok) return;
    const payload = await resp.json();
    appState.googleWorkspace.profiles = payload.profiles || [];
    appState.googleWorkspace.currentProfile = payload.current_profile || appState.googleWorkspace.profiles.find((item) => item.default)?.id || "saerc";
  } catch (error) {
    console.warn("Failed to load Google Workspace profiles", error);
  }
}

async function loadComposioProfiles() {
  try {
    const resp = await fetch("/api/composio/profiles", { cache: "no-store" });
    if (!resp.ok) return;
    const payload = await resp.json();
    appState.composioWorkspace.profiles = payload.profiles || [];
    appState.composioWorkspace.currentProfile = payload.current_profile || appState.composioWorkspace.profiles.find((item) => item.default)?.id || "fastonegroup";
  } catch (error) {
    console.warn("Failed to load Composio profiles", error);
  }
}

async function switchGoogleWorkspaceProfile(profileId, options = {}) {
  if (!profileId) return false;
  const resp = await fetch("/api/google-workspace/profile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile: profileId }),
  });
  if (!resp.ok) return false;
  const payload = await resp.json();
  appState.googleWorkspace.profiles = payload.profiles || appState.googleWorkspace.profiles;
  appState.googleWorkspace.currentProfile = payload.current_profile || profileId;
  renderGoogleWorkspaceProfilePanel();
  applyWorkspaceMeta();
  if (!options.silent) {
    const messages = document.getElementById("financeMessages");
    if (messages && appState.currentSkillId === "google-workspace") {
      const profile = currentGoogleProfile();
      appendMessage(
        messages,
        lang() === "zh"
          ? `已切换邮箱到 ${googleMailboxLabel(profile)}。后续 Meeting Follow-up、Email Draft、Calendar Plan、Docs Outline、Sheets Tracker 都会按这个邮箱上下文继续。`
          : `Mailbox switched to ${googleMailboxLabel(profile)}. Meeting Follow-up, Email Draft, Calendar Plan, Docs Outline, and Sheets Tracker will continue with this mailbox context.`,
        "assistant"
      );
    }
  }
  return true;
}

async function switchComposioProfile(profileId, options = {}) {
  if (!profileId) return false;
  const resp = await fetch("/api/composio/profile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile: profileId }),
  });
  if (!resp.ok) return false;
  const payload = await resp.json();
  appState.composioWorkspace.profiles = payload.profiles || appState.composioWorkspace.profiles;
  appState.composioWorkspace.currentProfile = payload.current_profile || profileId;
  renderComposioProfilePanel();
  applyWorkspaceMeta();
  if (!options.silent) {
    const messages = document.getElementById("financeMessages");
    if (messages && appState.currentSkillId === "composio-workspace") {
      const profile = currentComposioProfile();
      appendMessage(
        messages,
        lang() === "zh"
          ? `已切换账号到 ${composioMailboxLabel(profile)}。后续 Meeting Follow-up、Email Draft、Calendar Plan、Docs Outline、Sheets Tracker 都会按这个账号上下文继续。`
          : `Account switched to ${composioMailboxLabel(profile)}. Meeting Follow-up, Email Draft, Calendar Plan, Docs Outline, and Sheets Tracker will continue with this account context.`,
        "assistant"
      );
    }
  }
  return true;
}

async function saveComposioApiKey(profileId, apiKey) {
  if (!profileId || !apiKey) return false;
  const resp = await fetch("/api/composio/api-key", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile: profileId, api_key: apiKey }),
  });
  if (!resp.ok) return false;
  const payload = await resp.json();
  appState.composioWorkspace.profiles = payload.profiles || appState.composioWorkspace.profiles;
  appState.composioWorkspace.currentProfile = payload.current_profile || profileId;
  renderComposioProfilePanel();
  applyWorkspaceMeta();
  return true;
}

async function testComposioProfile(profileId) {
  if (!profileId) return { ok: false };
  const resp = await fetch("/api/composio/test", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile: profileId }),
  });
  const payload = await resp.json().catch(() => ({ ok: false }));
  appState.composioWorkspace.profiles = payload.profiles || appState.composioWorkspace.profiles;
  appState.composioWorkspace.currentProfile = payload.current_profile || appState.composioWorkspace.currentProfile || profileId;
  renderComposioProfilePanel();
  applyWorkspaceMeta();
  return payload.test || { ok: false, message: payload.error || "Unknown response" };
}

function renderGoogleWorkspaceProfilePanel() {
  const financeRoot = document.getElementById("finance");
  if (!financeRoot) return;
  const infoRow = financeRoot.querySelector(".workspace-info-row");
  if (!infoRow) return;
  let panel = financeRoot.querySelector(".google-mailbox-panel");
  if (appState.currentSkillId !== "google-workspace") {
    if (panel) panel.remove();
    return;
  }
  const profile = currentGoogleProfile();
  const authText = profile.authenticated
    ? (lang() === "zh" ? "已授权" : "Connected")
    : (lang() === "zh" ? "待授权" : "Authorization Needed");
  if (!panel) {
    panel = document.createElement("div");
    panel.className = "welcome google-mailbox-panel";
    infoRow.insertAdjacentElement("afterend", panel);
  }
  panel.innerHTML = `
    <strong>${lang() === "zh" ? "邮箱选择" : "Mailbox Selection"}</strong><br>
    ${escapeHtml(googleMailboxLabel(profile))}
    <div class="tag-row" style="margin-top:12px;">
      <span class="tag">${escapeHtml(authText)}</span>
      <span class="tag">${lang() === "zh" ? "5 个工作动作" : "5 Work Actions"}</span>
      <span class="tag">${lang() === "zh" ? "规则与 SAERC 一致" : "Same Rule Set"}</span>
    </div>
    <div class="workspace-action-buttons account-switch-grid" style="margin-top:14px;">
      ${(appState.googleWorkspace.profiles || []).map((item) => `
        <button
          class="btn ${item.id === profile.id ? "btn-primary" : "btn-ghost"} account-switch-btn google-mailbox-switch"
          type="button"
          data-google-profile="${escapeHtml(item.id)}"
        >
          <strong class="account-switch-name">${escapeHtml(item.label)}</strong>
          <span class="account-switch-email">${escapeHtml(item.email || (lang() === "zh" ? "未填写邮箱" : "No email set"))}</span>
        </button>
      `).join("")}
    </div>
  `;
  panel.querySelectorAll("[data-google-profile]").forEach((button) => {
    button.addEventListener("click", async () => {
      const profileId = button.dataset.googleProfile;
      if (!profileId || profileId === appState.googleWorkspace.currentProfile) return;
      button.disabled = true;
      await switchGoogleWorkspaceProfile(profileId);
      button.disabled = false;
    });
  });
}

function renderComposioProfilePanel() {
  const financeRoot = document.getElementById("finance");
  if (!financeRoot) return;
  const infoRow = financeRoot.querySelector(".workspace-info-row");
  if (!infoRow) return;
  let panel = financeRoot.querySelector(".composio-profile-panel");
  if (appState.currentSkillId !== "composio-workspace") {
    if (panel) panel.remove();
    return;
  }
  const profile = currentComposioProfile();
  const authText = profile.authenticated
    ? (lang() === "zh" ? "已保存 Key" : "Key Saved")
    : (lang() === "zh" ? "待授权" : "Authorization Needed");
  const testText = profile.last_test_ok === true
    ? (lang() === "zh" ? "连接通过" : "Connection OK")
    : profile.last_test_ok === false
      ? (lang() === "zh" ? "连接失败" : "Connection Failed")
      : (lang() === "zh" ? "尚未测试" : "Not Tested");
  if (!panel) {
    panel = document.createElement("div");
    panel.className = "welcome composio-profile-panel";
    infoRow.insertAdjacentElement("afterend", panel);
  }
  panel.innerHTML = `
    <strong>${lang() === "zh" ? "账号选择" : "Account Selection"}</strong><br>
    ${escapeHtml(composioMailboxLabel(profile))}
    <div class="tag-row" style="margin-top:12px;">
      <span class="tag">${escapeHtml(authText)}</span>
      <span class="tag">${escapeHtml(testText)}</span>
      <span class="tag">${lang() === "zh" ? "5 个工作动作" : "5 Work Actions"}</span>
      <span class="tag">${lang() === "zh" ? "双账号隔离" : "Dual Account Isolation"}</span>
    </div>
    <div class="workspace-action-note" style="margin-top:10px;">${escapeHtml(composioTestSummary(profile))}${profile.last_test_message ? ` · ${escapeHtml(profile.last_test_message)}` : ""}</div>
    <div class="workspace-action-buttons account-switch-grid" style="margin-top:14px;">
      ${(appState.composioWorkspace.profiles || []).map((item) => `
        <button
          class="btn ${item.id === profile.id ? "btn-primary" : "btn-ghost"} account-switch-btn composio-profile-switch"
          type="button"
          data-composio-profile="${escapeHtml(item.id)}"
        >
          <strong class="account-switch-name">${escapeHtml(item.label)}</strong>
          <span class="account-switch-email">${escapeHtml(item.email || (lang() === "zh" ? "未填写邮箱" : "No email set"))}</span>
        </button>
      `).join("")}
    </div>
    <div class="workspace-action-buttons account-action-grid" style="margin-top:10px;">
      <button class="btn btn-ghost account-action-btn" type="button" data-composio-api-key="${escapeHtml(profile.id)}">
        <strong>${lang() === "zh" ? "设置 API Key" : "Set API Key"}</strong>
        <span>${lang() === "zh" ? "按账号独立保存" : "Store per account"}</span>
      </button>
      <button class="btn btn-ghost account-action-btn" type="button" data-composio-test="${escapeHtml(profile.id)}">
        <strong>${lang() === "zh" ? "测试连接" : "Test Connection"}</strong>
        <span>${lang() === "zh" ? "验证当前账号" : "Verify current account"}</span>
      </button>
    </div>
  `;
  panel.querySelectorAll("[data-composio-profile]").forEach((button) => {
    button.addEventListener("click", async () => {
      const profileId = button.dataset.composioProfile;
      if (!profileId || profileId === appState.composioWorkspace.currentProfile) return;
      button.disabled = true;
      await switchComposioProfile(profileId);
      button.disabled = false;
    });
  });
  panel.querySelectorAll("[data-composio-api-key]").forEach((button) => {
    button.addEventListener("click", async () => {
      const profileId = button.dataset.composioApiKey;
      const title = lang() === "zh"
        ? `为 ${composioMailboxLabel(profile)} 输入 Composio API Key`
        : `Enter the Composio API key for ${composioMailboxLabel(profile)}`;
      const value = window.prompt(title, "");
      if (!value) return;
      button.disabled = true;
      const ok = await saveComposioApiKey(profileId, value.trim());
      if (ok) {
        const messages = document.getElementById("financeMessages");
        if (messages && appState.currentSkillId === "composio-workspace") {
          appendMessage(
            messages,
            lang() === "zh"
              ? `已为 ${composioMailboxLabel(currentComposioProfile())} 保存 Composio API Key。`
              : `Saved the Composio API key for ${composioMailboxLabel(currentComposioProfile())}.`,
            "assistant"
          );
        }
      }
      button.disabled = false;
    });
  });
  panel.querySelectorAll("[data-composio-test]").forEach((button) => {
    button.addEventListener("click", async () => {
      const profileId = button.dataset.composioTest;
      button.disabled = true;
      const result = await testComposioProfile(profileId);
      const messages = document.getElementById("financeMessages");
      if (messages && appState.currentSkillId === "composio-workspace") {
        appendMessage(
          messages,
          result.ok
            ? (lang() === "zh"
                ? `Composio 连接测试通过：${result.message || composioMailboxLabel(currentComposioProfile())}`
                : `Composio connection check passed: ${result.message || composioMailboxLabel(currentComposioProfile())}`)
            : (lang() === "zh"
                ? `Composio 连接测试失败：${result.message || "请检查 API Key"}`
                : `Composio connection check failed: ${result.message || "Please verify the API key"}`),
          "assistant"
        );
      }
      button.disabled = false;
    });
  });
}

async function waitForRoute(provider, model, timeoutMs = 6000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    await loadStatus();
    if (appState.status?.current_provider === provider && appState.status?.current_model === model) {
      return true;
    }
    await new Promise((resolve) => setTimeout(resolve, 350));
  }
  return false;
}

async function loadSkills() {
  const resp = await fetch("./agents/skills.index.json", { cache: "no-store" });
  appState.skillsIndex = await resp.json();
  const skills = appState.skillsIndex?.skills || [];
  const loaded = await Promise.all(skills.map(async (skill) => {
    try {
      const detail = await fetch(`./agents/${skill.file}`, { cache: "no-store" });
      if (!detail.ok) return [skill.id, null];
      return [skill.id, await detail.json()];
    } catch {
      return [skill.id, null];
    }
  }));
  appState.skillConfigs = Object.fromEntries(loaded.filter(([, value]) => value));
  try {
    const guideResp = await fetch("/api/skills/activation-guide", { cache: "no-store" });
    appState.skillGuide = guideResp.ok ? await guideResp.json() : null;
  } catch {
    appState.skillGuide = null;
  }
}

function renderExecutiveDock() {
  const dock = document.querySelector(".executive-dock");
  if (!dock || !appState.skillsIndex?.skills) return;
  const priority = [
    "uk_hk_financial_contract_counsel",
    "financial-analysis",
    "composio-workspace",
    "pdf-excel-analysis",
    "due-diligence-web-research",
    "financial-report-summary",
    "client-follow-up-weekly-update",
    "banking-sblc",
    "banking-dlc",
    "free-image-draft",
    "slack-collaboration",
  ];
  const ids = [
    ...priority.filter((id) => appState.skillsIndex.skills.some((skill) => skill.id === id) && PLATFORM_META[id]),
    ...appState.skillsIndex.skills.map((skill) => skill.id).filter((id) => !priority.includes(id)),
  ].slice(0, 8);
  dock.innerHTML = ids.map((id) => {
    const meta = PLATFORM_META[id] || PLATFORM_META["financial-analysis"];
    const label = compactPlatformName(meta[lang()].name);
    return `<button class="dock-chip" type="button" data-skill-id="${escapeHtml(id)}">${escapeHtml(label)}</button>`;
  }).join("");
  dock.querySelectorAll("[data-skill-id]").forEach((button) => {
    button.addEventListener("click", () => {
      const skillId = button.dataset.skillId;
      if (!skillId) return;
      navigateToWorkspaceSkill(skillId, true);
    });
  });
}

function normalizeHomeLayout() {
  const homeRoot = document.getElementById("home");
  if (!homeRoot) return;
  homeRoot.querySelector(".twin-home-section")?.remove();
  const cronSection = homeRoot.querySelector(".cron-section");
  const chatSection = Array.from(homeRoot.querySelectorAll(".section")).find((section) => section.querySelector("#homeMessages"));
  if (chatSection && cronSection && chatSection.compareDocumentPosition(cronSection) & Node.DOCUMENT_POSITION_FOLLOWING) {
    homeRoot.insertBefore(chatSection, cronSection);
  }
  const eyebrow = chatSection?.querySelector(".eyebrow");
  const heading = chatSection?.querySelector("h2");
  if (eyebrow) eyebrow.textContent = "Human Exchange";
  if (heading) heading.textContent = lang() === "zh" ? "人机交流" : "Human Exchange";
  const firstMessage = document.querySelector("#homeMessages .message");
  if (firstMessage && !firstMessage.dataset.historyItem) {
    firstMessage.textContent = lang() === "zh"
      ? "你好，这里是 FASTONE Hermes AI Agent 的人机交流入口。你可以直接输入问题，系统将按当前工作链路继续处理。"
      : "Welcome to the FASTONE Hermes AI Agent human exchange surface. Ask directly and the system will continue through the active operating route.";
  }
  const summaryNotes = homeRoot.querySelectorAll(".status-stack .summary-item-wide strong");
  if (summaryNotes[0]) {
    summaryNotes[0].textContent = lang() === "zh"
      ? "人机交流、Cron 中心与协同工作平台均已接入当前工作流。"
      : "Human Exchange, the Cron Center, and the collaboration workspaces are all connected to the current workflow.";
  }
  if (summaryNotes[1]) {
    summaryNotes[1].textContent = lang() === "zh"
      ? "可先从人机交流进入，再按任务切到目标工作平台。"
      : "Start from Human Exchange when needed, then move into the target workspace for focused work.";
  }
}

function ensureEnterpriseCommandCenter() {
  const enterpriseIcon = (name, tone = "core") => {
    const icons = {
      score: '<svg viewBox="0 0 24 24" fill="none"><path d="M4 16.5l4-4 3 3 7-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M20 8v5h-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
      ready: '<svg viewBox="0 0 24 24" fill="none"><path d="M5 12.5l4 4 10-10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
      degraded: '<svg viewBox="0 0 24 24" fill="none"><path d="M12 5v8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><circle cx="12" cy="17" r="1.4" fill="currentColor"/></svg>',
      runtime: '<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="1.8"/><path d="M12 8v5l3 2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
      structure: '<svg viewBox="0 0 24 24" fill="none"><path d="M5 6h14M5 12h14M5 18h8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
      baseline: '<svg viewBox="0 0 24 24" fill="none"><rect x="4" y="5" width="16" height="14" rx="2" stroke="currentColor" stroke-width="1.8"/><path d="M8 10h8M8 14h5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
      sprint: '<svg viewBox="0 0 24 24" fill="none"><path d="M4 18h16M7 18V9m5 9V6m5 12v-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
      supervision: '<svg viewBox="0 0 24 24" fill="none"><path d="M12 4l7 3v5c0 4.2-2.7 7.3-7 8-4.3-.7-7-3.8-7-8V7l7-3z" stroke="currentColor" stroke-width="1.8"/><path d="M9.2 12.3l1.9 1.9 3.8-3.9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
      effect: '<svg viewBox="0 0 24 24" fill="none"><path d="M6 15l3-3 2 2 5-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M16 9h3v3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
      closeout: '<svg viewBox="0 0 24 24" fill="none"><path d="M7 5h10l2 3v10a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V8l2-3z" stroke="currentColor" stroke-width="1.8"/><path d="M9 12h6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
      improvement: '<svg viewBox="0 0 24 24" fill="none"><path d="M12 4l2.2 4.5L19 10l-3.5 3.4.8 4.8L12 16l-4.3 2.2.8-4.8L5 10l4.8-1.5L12 4z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>',
    };
    return `<span class="enterprise-icon enterprise-icon--${name} enterprise-icon--tone-${tone}" aria-hidden="true">${icons[name] || icons.score}</span>`;
  };
  const homeRoot = document.getElementById("home");
  if (!homeRoot) return;
  let section = homeRoot.querySelector("[data-enterprise-center]");
  if (!section) {
    section = document.createElement("section");
    section.className = "section enterprise-center";
    section.dataset.enterpriseCenter = "1";
    section.innerHTML = `
      <div class="section-head">
        <div>
          <div class="eyebrow">Enterprise Command Center</div>
          <h2>${lang() === "zh" ? "企业级决策中枢" : "Enterprise Decision Center"}</h2>
          <p>${lang() === "zh"
            ? "把运行健康、风险与执行动作放在同一视图，确保团队按统一标准推进。"
            : "Keep runtime health, risk, and actions in one view so teams execute against a single standard."}</p>
        </div>
      </div>
      <div class="enterprise-grid">
        <article class="enterprise-card card" data-domain="finance">
          <span class="enterprise-label">${enterpriseIcon("score", "finance")}<em>${lang() === "zh" ? "健康评分" : "Health Score"}</em></span>
          <strong data-bind="health-score">0</strong>
          <p>${lang() === "zh" ? "基于路由就绪率与降级状态的综合评分" : "Composite score from route readiness and degradation state."}</p>
        </article>
        <article class="enterprise-card card" data-domain="collaboration">
          <span class="enterprise-label">${enterpriseIcon("ready", "collaboration")}<em>${lang() === "zh" ? "运行就绪通道" : "Ready Routes"}</em></span>
          <strong data-bind="health-ready">0</strong>
          <p>${lang() === "zh" ? "可直接承载任务的 AI 通道数" : "AI routes currently ready to carry workload."}</p>
        </article>
        <article class="enterprise-card card" data-domain="legal">
          <span class="enterprise-label">${enterpriseIcon("degraded", "legal")}<em>${lang() === "zh" ? "降级通道" : "Degraded Routes"}</em></span>
          <strong data-bind="health-degraded">0</strong>
          <p>${lang() === "zh" ? "处于冷却或备用状态的通道" : "Routes currently in cooldown or degraded mode."}</p>
        </article>
        <article class="enterprise-card card" data-domain="collaboration">
          <span class="enterprise-label">${enterpriseIcon("runtime", "collaboration")}<em>${lang() === "zh" ? "核心运行态" : "Core Runtime"}</em></span>
          <strong data-bind="health-runtime">Ready</strong>
          <p>${lang() === "zh" ? "网关和工作流的即时可用状态" : "Current availability of gateway and workflow core."}</p>
        </article>
      </div>
      <div class="enterprise-rail card">
        <div class="enterprise-rail__col">
          <h3 class="enterprise-headline">${enterpriseIcon("structure", "finance")}<span>${lang() === "zh" ? "标准交付结构" : "Delivery Structure"}</span></h3>
          <p>${lang() === "zh" ? "所有输出统一采用“结论-依据-风险-动作”框架，提升管理层可读性与可执行性。" : "All outputs follow a Conclusion-Evidence-Risk-Action frame for executive readability and execution clarity."}</p>
        </div>
        <div class="enterprise-rail__col">
          <h3 class="enterprise-headline">${enterpriseIcon("baseline", "legal")}<span>${lang() === "zh" ? "企业级验收基线" : "Enterprise Acceptance Baseline"}</span></h3>
          <p>${lang() === "zh" ? "导航一致、路由可观测、权限可控、任务可追溯、异常可恢复。" : "Consistent navigation, observable routing, controlled permissions, traceable tasks, and recoverable failures."}</p>
        </div>
      </div>
      <div class="enterprise-monitor card">
        <div class="enterprise-monitor__head">
          <h3 class="enterprise-headline">${enterpriseIcon("sprint", "collaboration")}<span>${lang() === "zh" ? "14天冲刺监督中枢" : "14-Day Sprint Supervision Hub"}</span></h3>
          <div class="enterprise-monitor__project-switch">
            <label>${lang() === "zh" ? "项目" : "Project"}</label>
            <select data-role="sprint-project-select"></select>
          </div>
          <span data-bind="acceptance-state">${lang() === "zh" ? "待收口" : "Pending"}</span>
        </div>
        <div class="enterprise-monitor__kpis">
          <article>
            <span class="enterprise-label">${enterpriseIcon("sprint", "collaboration")}<em>${lang() === "zh" ? "冲刺进度" : "Sprint Progress"}</em></span>
            <strong data-bind="sprint-progress">0/14</strong>
          </article>
          <article>
            <span class="enterprise-label">${enterpriseIcon("supervision", "legal")}<em>${lang() === "zh" ? "监督状态" : "Supervision Status"}</em></span>
            <strong data-bind="supervision-state">${lang() === "zh" ? "待更新" : "Pending"}</strong>
          </article>
          <article>
            <span class="enterprise-label">${enterpriseIcon("effect", "finance")}<em>${lang() === "zh" ? "实施效果" : "Implementation Effect"}</em></span>
            <strong data-bind="implementation-effect">0%</strong>
          </article>
        </div>
        <div class="enterprise-monitor__notes">
          <div>
            <h4 class="enterprise-headline enterprise-headline--sm">${enterpriseIcon("closeout", "legal")}<span>${lang() === "zh" ? "项目收尾总结" : "Project Closeout Summary"}</span></h4>
            <p data-bind="closeout-summary">${lang() === "zh" ? "项目收尾摘要待生成。" : "Closeout summary is pending."}</p>
          </div>
          <div>
            <h4 class="enterprise-headline enterprise-headline--sm">${enterpriseIcon("improvement", "finance")}<span>${lang() === "zh" ? "下一次改进建议" : "Next Improvement Suggestion"}</span></h4>
            <p data-bind="next-improvement">${lang() === "zh" ? "下一步改进建议待生成。" : "Next improvement recommendation is pending."}</p>
          </div>
        </div>
        <div class="enterprise-monitor__timeline" data-bind="sprint-timeline"></div>
      </div>
    `;
    const anchor = homeRoot.querySelector(".section");
    if (anchor) homeRoot.insertBefore(section, anchor);
    else homeRoot.appendChild(section);
  }
}

function routeForSkill(id) {
  const meta = PLATFORM_META[id] || PLATFORM_META["financial-analysis"];
  if (meta.section === "legal") return `${routeForFile("legal")}?platform=${encodeURIComponent(id)}`;
  return `${routeForFile("console")}?platform=${encodeURIComponent(id)}`;
}

function compactPlatformName(name) {
  return String(name || "")
    .replace(/\s+Workspace\b/gi, "")
    .replace(/工作平台/g, "")
    .replace(/\s{2,}/g, " ")
    .trim();
}

function skillGuideText() {
  return lang() === "zh" ? {
    title: "新人 Skill 使用指南",
    subtitle: "把 Hermes AI Agent 内置工作平台、Hermes 在线已安装 skills、Codex 本地 skills 和插件 skills 放在同一张作战地图里。新人只要看任务类型、复制激活词、补充材料与验收标准，就能正确调用能力。",
    updated: "动态索引",
    search: "搜索 skill、场景、激活词",
    all: "全部",
    hermes: "Hermes AI Agent",
    codex: "Codex Skills",
    plugin: "插件 Skills",
    open: "进入平台",
    copy: "复制激活词",
    copied: "已复制",
    terms: "激活词",
    templates: "推荐开场",
    modes: "工作模式",
    flowA: "1. 先判断任务类型",
    flowB: "2. 用激活词或自然语言点名能力",
    flowC: "3. 补充文件、输出格式、语言和验收标准",
    noData: "Skill 指南正在生成，稍后刷新即可查看。",
  } : {
    title: "New Joiner Skill Guide",
    subtitle: "A single operating map for Hermes AI Agent workspaces, Hermes online installed skills, Codex local skills, and plugin skills. Pick the task type, use the activation term, then add files, format, language, and acceptance criteria.",
    updated: "Live index",
    search: "Search skills, use cases, activation terms",
    all: "All",
    hermes: "Hermes AI Agent",
    codex: "Codex Skills",
    plugin: "Plugin Skills",
    open: "Open Workspace",
    copy: "Copy Activation",
    copied: "Copied",
    terms: "Activation Terms",
    templates: "Starter Prompts",
    modes: "Work Modes",
    flowA: "1. Identify the task type",
    flowB: "2. Name the capability with an activation term",
    flowC: "3. Add files, format, language, and acceptance criteria",
    noData: "The skill guide is being generated. Refresh shortly to view it.",
  };
}

function skillGuideSourceGroup(source) {
  if (source === "hermes-agent" || source === "hermes-online") return "hermes";
  if (source === "plugin") return "plugin";
  return "codex";
}

function skillGuideSourceLabel(item) {
  const source = item?.source;
  if (source === "hermes-agent") return "Hermes AI Agent";
  if (source === "hermes-online") return "Hermes Online";
  if (source === "plugin") return item?.source_label || "Plugin";
  if (source === "codex-system") return "Codex System";
  return item?.source_label || "Codex Local";
}

function skillGuideCategoryLabel(item) {
  const map = {
    finance: lang() === "zh" ? "金融 / 财务" : "Finance",
    legal: lang() === "zh" ? "法律 / 合规" : "Legal",
    research: lang() === "zh" ? "研究 / 尽调" : "Research",
    document: lang() === "zh" ? "文档 / 文件" : "Documents",
    data: lang() === "zh" ? "数据 / 表格" : "Data",
    communication: lang() === "zh" ? "沟通 / 协同" : "Communication",
    design: lang() === "zh" ? "设计 / 视觉" : "Design",
    automation: lang() === "zh" ? "自动化 / 部署" : "Automation",
    developer: lang() === "zh" ? "开发 / 工程" : "Developer",
    knowledge: lang() === "zh" ? "知识管理" : "Knowledge",
    media: lang() === "zh" ? "音视频 / 图片" : "Media",
    operations: lang() === "zh" ? "运营 / 工作流" : "Operations",
    strategy: lang() === "zh" ? "战略 / 管理" : "Strategy",
    analysis: lang() === "zh" ? "分析 / 底稿" : "Analysis",
    creative: lang() === "zh" ? "创意 / 视觉" : "Creative",
    language: lang() === "zh" ? "语言 / 表达" : "Language",
    "trade-finance": lang() === "zh" ? "贸易金融" : "Trade Finance",
    general: lang() === "zh" ? "通用能力" : "General",
  };
  return map[item?.category] || item?.category_label || map.general;
}

function skillGuideSearchText(item) {
  return [
    item?.display_name,
    item?.name,
    item?.description,
    item?.category,
    item?.category_label,
    item?.source_label,
    ...(item?.activation_terms || []),
    ...(item?.tags || []),
    ...(item?.templates || []).flatMap((template) => [template.title, template.description, template.prompt]),
    ...(item?.work_modes || []).flatMap((mode) => [mode.label, mode.description]),
  ].filter(Boolean).join(" ").toLowerCase();
}

function renderSkillGuideItem(item) {
  const copy = skillGuideText();
  const group = skillGuideSourceGroup(item.source);
  const terms = (item.activation_terms || []).slice(0, 6);
  const templates = (item.templates || []).slice(0, 2);
  const modes = (item.work_modes || []).slice(0, 3);
  const route = item.route || (item.skill_id ? routeForSkill(item.skill_id) : "");
  const search = skillGuideSearchText(item);
  return `
    <article class="skill-guide-card skill-guide-card--${escapeHtml(group)}" data-skill-guide-card data-source="${escapeHtml(group)}" data-search="${escapeHtml(search)}">
      <div class="skill-guide-card__top">
        <span class="skill-guide-source">${escapeHtml(skillGuideSourceLabel(item))}</span>
        <span class="skill-guide-category">${escapeHtml(skillGuideCategoryLabel(item))}</span>
      </div>
      <h3>${escapeHtml(item.display_name || item.name || "")}</h3>
      <p>${escapeHtml(item.description || item.when_to_use || "")}</p>
      ${terms.length ? `
        <div class="skill-guide-block">
          <strong>${escapeHtml(copy.terms)}</strong>
          <div class="skill-guide-terms">
            ${terms.map((term) => `<button type="button" class="skill-guide-term" data-copy-term="${escapeHtml(term)}">${escapeHtml(term)}</button>`).join("")}
          </div>
        </div>
      ` : ""}
      ${modes.length ? `
        <div class="skill-guide-block skill-guide-block--compact">
          <strong>${escapeHtml(copy.modes)}</strong>
          <div class="skill-guide-mini-list">
            ${modes.map((mode) => `<span>${escapeHtml(mode.label || mode.id || "")}</span>`).join("")}
          </div>
        </div>
      ` : ""}
      ${templates.length ? `
        <div class="skill-guide-block skill-guide-templates">
          <strong>${escapeHtml(copy.templates)}</strong>
          ${templates.map((template) => `
            <button type="button" data-copy-term="${escapeHtml(template.prompt || template.title || "")}">
              <span>${escapeHtml(template.title || "")}</span>
              <em>${escapeHtml(template.description || template.prompt || "")}</em>
            </button>
          `).join("")}
        </div>
      ` : ""}
      <div class="skill-guide-actions">
        ${item.source === "hermes-agent" && item.skill_id ? `<button class="btn btn-primary skill-guide-open" type="button" data-skill-id="${escapeHtml(item.skill_id)}">${escapeHtml(copy.open)}</button>` : ""}
        ${terms[0] ? `<button class="btn btn-ghost skill-guide-copy" type="button" data-copy-term="${escapeHtml(terms[0])}">${escapeHtml(copy.copy)}</button>` : ""}
      </div>
    </article>
  `;
}

function applySkillGuideFilter() {
  const shell = document.querySelector("[data-skill-guide]");
  if (!shell) return;
  const query = (shell.querySelector("[data-skill-guide-search]")?.value || "").trim().toLowerCase();
  const source = shell.querySelector("[data-skill-guide-source].is-active")?.dataset.skillGuideSource || "all";
  shell.querySelectorAll("[data-skill-guide-card]").forEach((card) => {
    const matchesSource = source === "all" || card.dataset.source === source;
    const matchesQuery = !query || (card.dataset.search || "").includes(query);
    card.hidden = !(matchesSource && matchesQuery);
  });
}

function bindSkillGuide() {
  const shell = document.querySelector("[data-skill-guide]");
  if (!shell || shell.dataset.bound === "1") return;
  shell.dataset.bound = "1";
  shell.querySelector("[data-skill-guide-search]")?.addEventListener("input", applySkillGuideFilter);
  shell.querySelectorAll("[data-skill-guide-source]").forEach((button) => {
    button.addEventListener("click", () => {
      shell.querySelectorAll("[data-skill-guide-source]").forEach((item) => item.classList.remove("is-active"));
      button.classList.add("is-active");
      applySkillGuideFilter();
    });
  });
  shell.querySelectorAll("[data-copy-term]").forEach((button) => {
    button.addEventListener("click", async () => {
      const value = button.dataset.copyTerm || "";
      if (!value) return;
      try {
        await navigator.clipboard.writeText(value);
        const original = button.textContent;
        button.textContent = skillGuideText().copied;
        setTimeout(() => {
          button.textContent = original;
        }, 1100);
      } catch {
        appendMessage("home", `${lang() === "zh" ? "激活词" : "Activation"}: ${value}`, "assistant");
      }
    });
  });
  shell.querySelectorAll(".skill-guide-open").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.skillId;
      if (id) navigateToWorkspaceSkill(id, true);
    });
  });
}

function renderSkillActivationGuide() {
  const grid = document.querySelector(".skill-grid");
  if (!grid) return;
  const copy = skillGuideText();
  let shell = document.querySelector("[data-skill-guide]");
  if (!shell) {
    shell = document.createElement("section");
    shell.className = "skill-guide-shell card";
    shell.dataset.skillGuide = "1";
    grid.closest(".skills-layout")?.querySelector(".skill-grid")?.parentElement?.appendChild(shell);
  }
  const payload = appState.skillGuide;
  const items = payload?.items || [];
  if (!items.length) {
    shell.innerHTML = `<div class="skill-guide-empty">${escapeHtml(copy.noData)}</div>`;
    return;
  }
  const summary = payload.summary || {};
  shell.dataset.bound = "";
  shell.innerHTML = `
    <div class="skill-guide-head">
      <div>
        <div class="eyebrow">${escapeHtml(copy.updated)}</div>
        <h2>${escapeHtml(copy.title)}</h2>
        <p>${escapeHtml(copy.subtitle)}</p>
      </div>
      <div class="skill-guide-stats">
        <span><strong>${Number(summary.total || items.length)}</strong>${lang() === "zh" ? "总能力" : "Total"}</span>
        <span><strong>${Number(summary.hermes || 0)}</strong>Hermes</span>
        <span><strong>${Number(summary.hermes_online || 0)}</strong>${lang() === "zh" ? "在线安装" : "Online Installed"}</span>
        <span><strong>${Number(summary.plugins || 0)}</strong>${lang() === "zh" ? "插件" : "Plugins"}</span>
      </div>
    </div>
    <div class="skill-guide-flow">
      <span>${escapeHtml(copy.flowA)}</span>
      <span>${escapeHtml(copy.flowB)}</span>
      <span>${escapeHtml(copy.flowC)}</span>
    </div>
    <div class="skill-guide-toolbar">
      <input type="search" data-skill-guide-search placeholder="${escapeHtml(copy.search)}" />
      <div class="skill-guide-filters">
        <button type="button" class="is-active" data-skill-guide-source="all">${escapeHtml(copy.all)}</button>
        <button type="button" data-skill-guide-source="hermes">${escapeHtml(copy.hermes)}</button>
        <button type="button" data-skill-guide-source="codex">${escapeHtml(copy.codex)}</button>
        <button type="button" data-skill-guide-source="plugin">${escapeHtml(copy.plugin)}</button>
      </div>
    </div>
    <div class="skill-guide-grid">
      ${items.map(renderSkillGuideItem).join("")}
    </div>
  `;
  bindSkillGuide();
}

function renderSkillsGrid() {
  const grid = document.querySelector(".skill-grid");
  if (!grid || !appState.skillsIndex?.skills) return;
  grid.innerHTML = appState.skillsIndex.skills.map((skill) => {
    const meta = PLATFORM_META[skill.id] || PLATFORM_META["financial-analysis"];
    const locale = meta[lang()];
    return `
      <article class="skill-card card">
        <h3>${escapeHtml(compactPlatformName(locale.name))}</h3>
        <p>${escapeHtml(locale.desc)}</p>
        <div class="tag-row">${locale.tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}</div>
        <button class="btn btn-primary skill-open" data-skill-id="${escapeHtml(skill.id)}" type="button">${lang() === "zh" ? "进入平台" : "Open Workspace"}</button>
      </article>
    `;
  }).join("");
  const count = appState.skillsIndex.skills.length;
  const countNode = document.querySelector("[data-bind='skill-count']");
  if (countNode) countNode.textContent = lang() === "zh" ? `${count} Skills` : `${count} Skills`;
  grid.querySelectorAll(".skill-open").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.skillId;
      const meta = PLATFORM_META[id];
      if (!meta) return;
      navigateToWorkspaceSkill(id, true);
    });
  });
  renderSkillActivationGuide();
}

function navigateToWorkspaceSkill(id, updateHash = true) {
  const meta = PLATFORM_META[id];
  if (!meta) return;
  appState.currentSkillId = id;
  applyWorkspaceMeta();
  syncDockSkillChipState();
  if (meta.section === "legal") {
    setActivePage("legal", updateHash);
    history.replaceState(null, "", `${routeForFile("legal")}?platform=${encodeURIComponent(id)}#legal`);
    return;
  }
  setActivePage("finance", updateHash);
  history.replaceState(null, "", `${routeForFile("console")}?platform=${encodeURIComponent(id)}#finance`);
}

function setThreads(threadList, items) {
  if (!threadList || !items?.length) return;
  threadList.innerHTML = items.map((item, idx) => `
    <div class="thread ${idx === 0 ? "active" : ""}">
      <strong>${escapeHtml(item[0])}</strong>
      <span>${escapeHtml(item[1])}</span>
    </div>
  `).join("");
}

function conversationThreadsForSelection(workspaceKey, skillId, meta) {
  const fallback = meta?.threads?.length ? meta.threads : [
    [lang() === "zh" ? "当前任务" : "Current Task", lang() === "zh" ? "等待载入当前工作动作。" : "Waiting to load the current workspace action."],
    [lang() === "zh" ? "Notes" : "Notes", lang() === "zh" ? "记录补充说明、边界条件和后续事项。" : "Track supporting notes, constraints, and follow-up items."],
  ];
  const actions = quickActionsForSkill(skillId).slice(0, 5);
  const selectedIndex = Number.isInteger(appState.actionSelection[workspaceKey]) ? appState.actionSelection[workspaceKey] : 0;
  const selected = actions[selectedIndex];
  if (!selected) return fallback;
  const noteTitle = lang() === "zh" ? "执行说明" : "Execution Notes";
  const noteBody = lang() === "zh"
    ? `当前已切换到“${selected[0]}”。对话会围绕这项动作继续展开，保留关键判断、待补材料和下一步动作。`
    : `The workspace is now focused on "${selected[0]}". The conversation will continue around this action, keeping track of key judgments, missing materials, and next steps.`;
  return [
    [selected[0], selected[1]],
    [noteTitle, noteBody],
  ];
}

function syncConversationThreads(workspaceKey, skillId, meta) {
  const root = document.getElementById(workspaceKey);
  const threadList = root?.querySelector(".thread-list");
  if (!threadList) return;
  setThreads(threadList, conversationThreadsForSelection(workspaceKey, skillId, meta));
}

function sblcIssuerControlData() {
  const zh = lang() === "zh";
  return {
    title: zh ? "开证人全流程监督台" : "Issuer End-to-End Control Desk",
    subtitle: zh
      ? "以开证人利益为中心，把合约、托管、SWIFT、银行确认、费用释放、原件交付和终止/没收条件放在同一张监督表里。"
      : "Issuer-centered supervision across contract, escrow, SWIFT, bank acknowledgments, fee release, original delivery, and termination/forfeiture conditions.",
    badges: zh
      ? [["规则", "ISP98 / UCP600"], ["核心立场", "开证人满意为先"], ["支付银行限制", "必须在中国大陆以外"]]
      : [["Rules", "ISP98 / UCP600"], ["Position", "Issuer satisfaction first"], ["Paying Bank", "Outside Mainland China"]],
    roles: zh ? [
      ["开证人 / 开证机构", "交易控制方；决定尽调是否满意、模板是否批准、是否继续或终止。"],
      ["开证银行", "按开证人指令发送 MT799、MT760，并通过安全银行渠道交付原件。"],
      ["收益人 / 收益机构", "提供 KYC/AML、信用额度证明、付款能力证明、保证金支票和费用支票。"],
      ["接证机构 / 接证银行", "提供自身模板、接收并认证 MT799/MT760，按 3 个银行日确认 readiness。"],
      ["支付银行", "承载 cheque / cashier order / fee payment；必须位于中国大陆以外并获开证方接受。"],
      ["托管代理 / 指定律师或银行", "持有保证金与费用支票，只在约定条件满足时释放、退回或没收。"],
    ] : [
      ["Issuer / Issuing Party", "Controls diligence satisfaction, template approval, continuation, stop rights, and termination."],
      ["Issuing Bank", "Sends MT799 and MT760 on issuer instruction and delivers originals via secure bank channel."],
      ["Beneficiary", "Provides KYC/AML, credit-line proof, payment-capacity proof, security cheque, and fee cheque."],
      ["Receiving / Advising Bank", "Provides its template, receives and authenticates MT799/MT760, and confirms readiness within 3 banking days."],
      ["Paying Bank", "Supports cheques/cashier orders/fee payment; must be outside Mainland China and acceptable to the issuing party."],
      ["Escrow Agent / Counsel / Bank", "Holds instruments and releases, returns, or forfeits them only under agreed conditions."],
    ],
    gates: zh ? [
      ["01", "尽调与额度确认", "收益人/接证银行", "信用额度确认函、KYC/AML、董事/UBO/授权签字人资料", "资料不完整或无法验证即停止"],
      ["02", "SBLC 模板批准", "收益人/接证银行 → 开证人", "接证银行完整 SBLC wording；开证人书面无条件批准", "未批准模板不得进入下一步"],
      ["03", "付款能力证明", "收益人", "审计报表、bank comfort letter 或开证人认可证明", "付款能力不足或证明不可核验"],
      ["04", "SPA / 主协议签署", "双方 / 法律顾问", "纳入完整 SBLC 程序、适用法律、ICC 仲裁、开证人 indemnity", "程序未写入合同即不签署"],
      ["05", "EUR 350,000 保证金支票托管", "收益人 → 托管代理", "不可撤销银行支票/本票；未达条件不得提示付款", "托管条款未覆盖自动没收"],
      ["06", "MT799 Pre-advice", "开证银行", "确认 1-5 步均令开证人满意后发送 MT799", "任何 CP 未满足不得发送"],
      ["07", "MT799 接收确认", "接证银行", "3 个银行日内正面确认接收、认证和 ready to receive", "逾期/含糊/不确认即触发停止或没收"],
      ["08", "SBLC 费用支票托管", "收益人 → 托管代理", "覆盖发行费、佣金和相关费用的单独不可撤销支票", "金额/收款方/托管条件不一致"],
      ["09", "MT760 正式开出", "开证银行", "仅在 MT799 确认和费用支票托管后，按已批准格式发送", "格式偏离或未经授权不得发送"],
      ["10", "确认与费用支票释放", "接证银行 / 托管代理", "MT760/MT799 receipt authentication；无 discrepancy 后释放/存入费用支票", "发现异常则立即保留或要求退回"],
      ["11", "原件交付", "开证银行", "银行到银行安全快递、tracking、POD，费用由收益人承担", "非安全渠道或无签收证明"],
      ["12", "保证金退回 / 最终结算", "托管代理 / 双方", "SBLC 到期、取消或完全履行后未提示付款退回保证金支票", "收益人侧违约、误述或银行不响应则没收"],
    ] : [
      ["01", "Diligence and credit-line confirmation", "Beneficiary / receiving bank", "Credit-line letter, KYC/AML, director/UBO/signatory materials", "Incomplete or unverifiable materials"],
      ["02", "SBLC template approval", "Beneficiary / receiving bank to issuer", "Full SBLC wording and unconditional written issuer approval", "No next step without approval"],
      ["03", "Proof of payment capacity", "Beneficiary", "Audited financials, bank comfort letter, or issuer-accepted proof", "Insufficient or unverifiable capacity"],
      ["04", "SPA / underlying agreement", "Parties / counsel", "Full procedure, governing law, ICC arbitration, issuer indemnity", "Procedure not embedded in contract"],
      ["05", "EUR 350,000 security cheque escrow", "Beneficiary to escrow", "Irrevocable cheque/cashier order held undeposited", "Escrow lacks automatic forfeiture wording"],
      ["06", "MT799 pre-advice", "Issuing bank", "Only after steps 1-5 are issuer-satisfactory", "Any unmet CP blocks transmission"],
      ["07", "MT799 acknowledgment", "Receiving bank", "Positive acknowledgment within 3 banking days", "Late, unclear, or negative response"],
      ["08", "SBLC fee cheque escrow", "Beneficiary to escrow", "Separate irrevocable fee cheque covering all fees and charges", "Amount/payee/escrow mismatch"],
      ["09", "MT760 issuance", "Issuing bank", "Only after MT799 acknowledgment and fee cheque escrow, using approved wording", "Unauthorized or divergent wording"],
      ["10", "Confirmation and fee release", "Receiving bank / escrow", "MT760/MT799 receipt authentication and no discrepancies", "Irregularity requires hold or return"],
      ["11", "Original delivery", "Issuing bank", "Secure bank courier, tracking, POD, beneficiary cost", "Unsafe channel or no POD"],
      ["12", "Deposit return / final settlement", "Escrow / parties", "Return undeposited after expiry, cancellation, or full performance", "Beneficiary default/misrepresentation triggers forfeiture"],
    ],
    documents: zh ? [
      ["SPA / 主交易协议", "完整纳入本 SBLC 程序、条件先决、适用法律、ICC 仲裁和开证人 indemnity。"],
      ["Escrow Agreement", "保证金支票、费用支票、释放、退回、提示付款、自动没收和争议期间持有规则。"],
      ["SBLC Wording", "必须由开证人书面无条件批准；接证银行版本不得默认采用。"],
      ["SWIFT Evidence Pack", "MT799、MT799 acknowledgment、MT760、MT760/MT799 receipt confirmation、tracking/POD。"],
    ] : [
      ["SPA / Underlying Agreement", "Embed the full procedure, CPs, governing law, ICC arbitration, and issuer indemnity."],
      ["Escrow Agreement", "Security cheque, fee cheque, release, return, presentation, automatic forfeiture, and dispute hold rules."],
      ["SBLC Wording", "Must be unconditionally approved by the issuer in writing; receiving-bank wording is not automatically accepted."],
      ["SWIFT Evidence Pack", "MT799, MT799 acknowledgment, MT760, MT760/MT799 receipt confirmation, tracking/POD."],
    ],
    redFlags: zh ? [
      "接证银行未在 3 个银行日内正面确认 MT799。",
      "收益人或接证银行延迟超过 5 个银行日。",
      "支付银行位于中国大陆或未获开证方接受。",
      "接证银行模板未提供全文或未获开证人无条件批准。",
      "KYC/AML、UBO、授权签字人资料缺失或无法验证。",
      "托管协议未明确费用释放、退回和自动没收条件。",
    ] : [
      "Receiving bank fails to acknowledge MT799 positively within 3 banking days.",
      "Beneficiary-side delay exceeds 5 banking days.",
      "Paying bank is in Mainland China or not acceptable to the issuing party.",
      "Receiving-bank template is not provided in full or not unconditionally approved.",
      "KYC/AML, UBO, or authorized-signatory materials are missing or unverifiable.",
      "Escrow agreement lacks clear release, return, and automatic forfeiture mechanics.",
    ],
  };
}

function sblcDocumentPackageData() {
  const zh = lang() === "zh";
  return [
    ["kyc", zh ? "KYC / AML 资料" : "KYC / AML Pack", zh ? "收益人、董事、UBO、授权签字人、制裁/PEP/AML 文件。" : "Beneficiary, directors, UBOs, authorized signatories, sanctions/PEP/AML files.", true],
    ["credit_line", zh ? "接证银行额度确认" : "Receiving Bank Credit Line", zh ? "接证/通知银行确认足额 credit line / collateral 覆盖 SBLC 金额与费用。" : "Receiving/advising bank confirmation of sufficient credit line/collateral for SBLC value and fees.", true],
    ["payment_capacity", zh ? "付款能力证明" : "Payment Capacity Proof", zh ? "审计报表、bank comfort letter 或其他开证人认可证明。" : "Audited financials, bank comfort letter, or other issuer-accepted proof.", true],
    ["sblc_template", zh ? "SBLC 模板全文" : "Full SBLC Template", zh ? "接证银行拟用完整 wording，必须由开证人书面无条件批准。" : "Full wording proposed by receiving bank; requires unconditional written issuer approval.", true],
    ["spa", zh ? "SPA / 主交易合同" : "SPA / Underlying Agreement", zh ? "完整纳入 SBLC 程序、适用法律、ICC 仲裁和开证人 indemnity。" : "Embeds full SBLC procedure, governing law, ICC arbitration, and issuer indemnity.", true],
    ["escrow", zh ? "托管协议" : "Escrow Agreement", zh ? "保证金支票、费用支票、释放、退回、没收和争议期间持有机制。" : "Security cheque, fee cheque, release, return, forfeiture, and dispute hold mechanics.", true],
    ["security_cheque", zh ? "EUR 350,000 保证金支票" : "EUR 350,000 Security Cheque", zh ? "不可撤销银行支票/本票，托管且未达条件不得提示付款。" : "Irrevocable bank cheque/cashier order held in escrow and not presented unless conditions trigger.", true],
    ["mt799_pre_advice", zh ? "MT799 Pre-advice" : "MT799 Pre-advice", zh ? "开证银行在 1-5 步满足后发送的预通知证据。" : "Evidence of pre-advice sent by issuing bank after steps 1-5 are satisfied.", false],
    ["mt799_ack", zh ? "MT799 接收确认" : "MT799 Acknowledgment", zh ? "接证银行 3 个银行日内确认接收、认证和 ready to receive。" : "Receiving bank confirms receipt, authentication, and readiness within 3 banking days.", false],
    ["fee_cheque", zh ? "SBLC 费用支票" : "SBLC Fee Cheque", zh ? "覆盖发行费、佣金和相关费用的单独不可撤销支票。" : "Separate irrevocable cheque covering issuance fees, commissions, and charges.", false],
    ["mt760", zh ? "MT760 正式开证" : "MT760 Issuance", zh ? "按已批准 SBLC 格式通过 authenticated SWIFT 发送。" : "Authenticated SWIFT MT760 using issuer-approved wording.", false],
    ["mt760_ack", zh ? "MT760 / MT799 收妥确认" : "MT760 / MT799 Receipt Confirmation", zh ? "接证银行确认收到并认证 MT760，且无 discrepancy。" : "Receiving bank confirms receipt/authentication of MT760 with no discrepancy.", false],
    ["original_delivery", zh ? "原件交付与 POD" : "Original Delivery and POD", zh ? "银行到银行安全快递 tracking 与 proof of delivery。" : "Secure bank-to-bank courier tracking and proof of delivery.", false],
    ["final_settlement", zh ? "到期/取消/履行与保证金退回" : "Expiry / Cancellation / Performance and Deposit Return", zh ? "SBLC 到期、取消或履行后保证金支票未提示付款退回证据。" : "Evidence for return of undeposited security cheque after expiry, cancellation, or performance.", false],
  ].map(([id, title, description, required]) => ({ id, title, description, required }));
}

function sblcPackageItems() {
  return (appState.attachments.finance || []).filter((item) => item.sblcCategory);
}

function sblcPackageStatus(categoryId) {
  const items = sblcPackageItems().filter((item) => item.sblcCategory === categoryId);
  if (!items.length) return { state: "missing", label: lang() === "zh" ? "缺失" : "Missing", items: [] };
  const extracted = items.some((item) => item.preview);
  return {
    state: extracted ? "ready" : "attached",
    label: extracted ? (lang() === "zh" ? "已提取" : "Extracted") : (lang() === "zh" ? "已上传" : "Uploaded"),
    items,
  };
}

function sblcCrossCheckWarnings() {
  const zh = lang() === "zh";
  const docs = sblcDocumentPackageData();
  const missingRequired = docs.filter((doc) => doc.required && !sblcPackageStatus(doc.id).items.length);
  const allText = sblcPackageItems().map((item) => `${item.name}\n${item.preview || ""}`).join("\n").toLowerCase();
  const warnings = [];
  if (missingRequired.length) {
    warnings.push([zh ? "资料缺口" : "Missing required package", zh ? `尚缺 ${missingRequired.map((item) => item.title).join("、")}。` : `Missing ${missingRequired.map((item) => item.title).join(", ")}.`]);
  }
  if (/(mainland china|中国大陆|境内银行|内地银行)/i.test(allText)) {
    warnings.push([zh ? "支付银行限制" : "Paying-bank restriction", zh ? "资料中出现中国大陆/境内银行表述，必须核实支付银行是否位于中国大陆以外并获开证方接受。" : "Materials mention Mainland China/onshore banks; verify paying banks are outside Mainland China and acceptable to the issuing party."]);
  }
  if (sblcPackageStatus("sblc_template").items.length && !/(approved|批准|无条件|unconditional)/i.test(allText)) {
    warnings.push([zh ? "模板批准证据不足" : "Template approval evidence gap", zh ? "已上传 SBLC 模板，但未识别到开证人书面无条件批准证据。" : "SBLC template uploaded, but unconditional written issuer approval was not detected."]);
  }
  if (sblcPackageStatus("mt760").items.length && !sblcPackageStatus("mt799_ack").items.length) {
    warnings.push([zh ? "SWIFT 顺序异常" : "SWIFT sequence issue", zh ? "已上传 MT760 相关资料，但尚未上传 MT799 正面接收确认。" : "MT760 material is present, but MT799 positive acknowledgment is missing."]);
  }
  if (sblcPackageStatus("fee_cheque").items.length && !sblcPackageStatus("mt760_ack").items.length) {
    warnings.push([zh ? "费用释放前置条件不足" : "Fee release CP gap", zh ? "已上传费用支票，但尚未上传 MT760/MT799 收妥认证且无 discrepancy 的确认。" : "Fee cheque is present, but MT760/MT799 authenticated receipt with no discrepancy is missing."]);
  }
  if (!warnings.length) warnings.push([zh ? "暂无系统预警" : "No system warning", zh ? "当前自动规则未识别重大矛盾；仍需人工复核主体、日期、金额、银行名称和 SWIFT 真实性。" : "No major contradiction detected by automated rules; still manually verify parties, dates, amounts, bank names, and SWIFT authenticity."]);
  return warnings;
}

function sblcFieldRadarData() {
  const zh = lang() === "zh";
  const allText = sblcPackageItems().map((item) => `${item.name}\n${item.preview || ""}`).join("\n");
  const fields = [
    ["party", zh ? "主体名称" : "Parties", /(beneficiary|issuer|applicant|收益人|开证人|申请人)/i],
    ["amount", zh ? "金额" : "Amount", /(eur|usd|hkd|€|\\$|金额|欧元|美元|港币|350,?000)/i],
    ["currency", zh ? "币种" : "Currency", /(eur|usd|hkd|欧元|美元|港币|币种)/i],
    ["bank", zh ? "银行" : "Bank", /(bank|swift|银行|接证|开证|通知行|paying)/i],
    ["date", zh ? "日期/期限" : "Date / Tenor", /(date|expiry|banking days|日期|到期|银行日|期限)/i],
    ["role", zh ? "角色关系" : "Roles", /(issuer|beneficiary|escrow|counsel|开证|收益|托管|律师)/i],
    ["fee", zh ? "费用/支票" : "Fees / Cheques", /(fee|cheque|cashier|commission|费用|支票|佣金|本票)/i],
    ["validity", zh ? "有效期" : "Validity", /(valid|expiry|cancel|performance|有效|到期|取消|履行)/i],
  ];
  return fields.map(([id, title, regex]) => {
    const matched = regex.test(allText);
    return {
      id,
      title,
      state: matched ? "success" : "warning",
      label: matched ? (zh ? "已识别" : "Found") : (zh ? "待核验" : "Check"),
      detail: matched ? (zh ? "资料中存在对应字段线索" : "Field signal found in package") : (zh ? "建议人工补充或上传对应证明" : "Add evidence or verify manually"),
    };
  });
}

function sblcGateControlStatus(gate) {
  const step = String(gate?.[0] || "");
  const map = {
    "01": ["kyc", "credit_line"],
    "02": ["sblc_template"],
    "03": ["payment_capacity"],
    "04": ["spa"],
    "05": ["escrow", "security_cheque"],
    "06": ["mt799_pre_advice"],
    "07": ["mt799_ack"],
    "08": ["fee_cheque"],
    "09": ["mt760"],
    "10": ["mt760_ack"],
    "11": ["original_delivery"],
    "12": ["final_settlement"],
  };
  const categories = map[step] || [];
  const ready = categories.filter((id) => sblcPackageStatus(id).items.length).length;
  const required = categories.length || 1;
  const complete = ready >= required;
  const zh = lang() === "zh";
  return {
    ready,
    required,
    state: complete ? "success" : "warning",
    label: complete ? (zh ? "可复核" : "Reviewable") : (zh ? "阻塞" : "Blocked"),
    blocker: complete ? (zh ? "证据已上传，等待人工审阅意见。" : "Evidence uploaded; human review required.") : (zh ? "缺少对应 Gate 证据，不能进入下一步。" : "Missing gate evidence; do not proceed."),
    next: complete ? (zh ? "审核一致性并签署 Gate 意见。" : "Review consistency and sign gate opinion.") : (zh ? "补上传材料并完成交叉检查。" : "Upload evidence and complete cross-check."),
  };
}

function sblcReviewOpinionPrompt(kind = "full") {
  const zh = lang() === "zh";
  const packageLines = sblcDocumentPackageData().map((doc) => {
    const status = sblcPackageStatus(doc.id);
    const names = status.items.map((item) => item.name).join(", ") || (zh ? "未上传" : "not uploaded");
    return `${doc.title}: ${status.label} - ${names}`;
  }).join("\n");
  const warnings = sblcCrossCheckWarnings().map((item) => `${item[0]}: ${item[1]}`).join("\n");
  const base = zh
    ? `请基于当前 SBLC 开证人监督平台资料包，生成正式审核意见文件。必须进行所有文件交叉比对，标记主体、银行名称、金额、币种、日期、时限、SBLC 模板版本、SPA/托管/支票/SWIFT 条件不一致，输出可导出的专业审核意见。\n\n[资料包状态]\n${packageLines}\n\n[系统预警]\n${warnings}\n\n`
    : `Based on the current SBLC issuer-control document package, produce a formal review opinion file. Cross-check all files and flag inconsistencies in parties, bank names, amounts, currency, dates, timelines, SBLC wording version, SPA/escrow/cheque/SWIFT conditions, and produce an export-ready professional review opinion.\n\n[Package status]\n${packageLines}\n\n[System warnings]\n${warnings}\n\n`;
  const tails = {
    full: zh ? "输出结构：一页结论、机构关系、资料完整性、12 步流程闸口、文件交叉比对表、不一致/缺口预警、开证人 no-go 条件、合同/托管修改点、下一步责任清单。" : "Output structure: one-page conclusion, institutional role map, package completeness, 12 gates, cross-document comparison table, inconsistency/gap warnings, issuer no-go conditions, SPA/escrow edits, next-action ownership list.",
    inconsistency: zh ? "请重点输出文件交叉比对和不一致预警矩阵，按高/中/低风险列出证据、影响、需补资料和责任方。" : "Focus on cross-document comparison and inconsistency warning matrix, ranked high/medium/low with evidence, impact, missing materials, and owner.",
    conditions: zh ? "请重点输出条件先决与执行闸口 tracking sheet，逐项列出状态、证据、不得进入下一步条件、责任方和截止日期。" : "Focus on conditions precedent and execution gate tracking sheet with status, evidence, no-go conditions, owner, and deadline.",
  };
  return base + (tails[kind] || tails.full);
}

function sblcIssuerPrompt(kind = "control") {
  const zh = lang() === "zh";
  const prompts = {
    control: zh
      ? "请基于当前 SBLC 交易材料，生成开证人全流程监督表。必须覆盖：机构关系图、12 个流程闸口、每步责任方、前置条件、证据、时限、红旗、开证人批准/停止权、终止/没收触发和下一步动作。"
      : "Based on the current SBLC transaction materials, generate an issuer-side end-to-end supervision table covering role map, 12 gates, owner, conditions precedent, evidence, timeline, red flags, issuer approval/stop rights, termination/forfeiture triggers, and next actions.",
    contract: zh
      ? "请从开证人保护角度审核 SPA、SBLC 程序和 escrow agreement，输出必须写入的合同条款、条件先决、托管释放/退回/没收条件、ICC 仲裁、适用法律、indemnity、支付银行限制和建议修改。"
      : "Review the SPA, SBLC procedure, and escrow agreement from the issuer-protection perspective. Provide mandatory clauses, CPs, escrow release/return/forfeiture conditions, ICC arbitration, governing law, indemnity, paying-bank restriction, and edits.",
    swift: zh
      ? "请按 SWIFT 执行闸口检查 MT799 pre-advice、MT799 acknowledgment、MT760 issuance、MT760/MT799 receipt confirmation 和原件交付。逐项列出前置条件、不得进入下一步的 no-go 条件、必须留存证据、异常处理和开证人停止权。"
      : "Check MT799 pre-advice, MT799 acknowledgment, MT760 issuance, MT760/MT799 receipt confirmation, and original delivery as SWIFT execution gates. List prerequisites, no-go conditions, evidence, exception handling, and issuer stop rights.",
  };
  return prompts[kind] || prompts.control;
}

function renderSblcIssuerControlTower() {
  const root = document.getElementById("finance");
  const body = root?.querySelector(".workspace-body");
  const existing = root?.querySelector("[data-sblc-issuer-control]");
  if (!root || !body) return;
  if (appState.currentSkillId !== "banking-sblc") {
    existing?.remove();
    return;
  }
  const data = sblcIssuerControlData();
  const section = existing || document.createElement("section");
  section.className = "sblc-issuer-control";
  section.dataset.sblcIssuerControl = "1";
  section.innerHTML = `
    <div class="sblc-issuer-hero">
      <div>
        <div class="eyebrow">SBLC ISSUER CONTROL</div>
        <h2>${escapeHtml(data.title)}</h2>
        <p>${escapeHtml(data.subtitle)}</p>
      </div>
      <div class="sblc-issuer-badges">
        ${data.badges.map((item) => `<span><em>${escapeHtml(item[0])}</em><strong>${escapeHtml(item[1])}</strong></span>`).join("")}
      </div>
    </div>
    <div class="sblc-issuer-layout">
      <section class="sblc-issuer-panel sblc-issuer-panel--wide">
        <div class="sblc-panel-head">
          <span>${lang() === "zh" ? "机构交叉关系" : "Institutional Relationships"}</span>
          <strong>${lang() === "zh" ? "谁负责什么、谁向谁确认、风险落在哪里" : "Who does what, who confirms to whom, where risk sits"}</strong>
        </div>
        <div class="sblc-role-grid">
          ${data.roles.map((role, index) => `
            <article>
              <span>${String(index + 1).padStart(2, "0")}</span>
              <strong>${escapeHtml(role[0])}</strong>
              <p>${escapeHtml(role[1])}</p>
            </article>
          `).join("")}
        </div>
      </section>
      <aside class="sblc-issuer-panel">
        <div class="sblc-panel-head">
          <span>${lang() === "zh" ? "快捷审核" : "Quick Review"}</span>
          <strong>${lang() === "zh" ? "直接填入对话框" : "Send to composer"}</strong>
        </div>
        <div class="sblc-prompt-stack">
          <button type="button" data-sblc-prompt="control">${lang() === "zh" ? "生成全流程监督表" : "Generate control table"}</button>
          <button type="button" data-sblc-prompt="contract">${lang() === "zh" ? "审核 SPA / 托管条款" : "Review SPA / escrow"}</button>
          <button type="button" data-sblc-prompt="swift">${lang() === "zh" ? "检查 SWIFT 执行闸口" : "Check SWIFT gates"}</button>
        </div>
      </aside>
    </div>
    <section class="sblc-issuer-panel">
      <div class="sblc-panel-head">
        <span>${lang() === "zh" ? "12 步流程闸口" : "12 Procedural Gates"}</span>
        <strong>${lang() === "zh" ? "每步均须有证据、时限、责任方和开证人停止权" : "Each gate needs evidence, timeline, owner, and issuer stop right"}</strong>
      </div>
      <div class="sblc-gate-table">
        ${data.gates.map((gate) => {
          const gateStatus = sblcGateControlStatus(gate);
          return `
          <article>
            <div class="sblc-gate-step">${escapeHtml(gate[0])}</div>
            <div><strong>${escapeHtml(gate[1])}</strong><span>${escapeHtml(gate[2])}</span></div>
            <p>${escapeHtml(gate[3])}</p>
            <div class="sblc-gate-control-cell">
              ${renderStatusBadge(gateStatus.label, gateStatus.state)}
              <em>${escapeHtml(gate[4])}</em>
              <span>${escapeHtml(gateStatus.blocker)}</span>
              <b>${escapeHtml(gateStatus.next)}</b>
            </div>
          </article>
        `;
        }).join("")}
      </div>
    </section>
    <div class="sblc-issuer-layout">
      <section class="sblc-issuer-panel">
        <div class="sblc-panel-head">
          <span>${lang() === "zh" ? "文件与合约控制" : "Contract and Document Control"}</span>
          <strong>${lang() === "zh" ? "起草、审核、签署、执行必须一致" : "Drafting, review, signing, and execution must align"}</strong>
        </div>
        <div class="sblc-doc-stack">
          ${data.documents.map((item) => `<article><strong>${escapeHtml(item[0])}</strong><p>${escapeHtml(item[1])}</p></article>`).join("")}
        </div>
      </section>
      <section class="sblc-issuer-panel">
        <div class="sblc-panel-head">
          <span>${lang() === "zh" ? "红旗与升级事项" : "Red Flags and Escalation"}</span>
          <strong>${lang() === "zh" ? "任一项出现即暂停或升级" : "Any item should pause or escalate"}</strong>
        </div>
        <ul class="sblc-red-flag-list">
          ${data.redFlags.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
        </ul>
      </section>
    </div>
    <section class="sblc-issuer-panel sblc-package-panel">
      <div class="sblc-panel-head">
        <span>${lang() === "zh" ? "资料上传与交叉审核" : "Document Upload and Cross-Review"}</span>
        <strong>${lang() === "zh" ? "全部流程资料在本平台归集、提取、比对和出具意见" : "Collect, extract, compare, and opine inside this workspace"}</strong>
      </div>
      <div class="sblc-package-grid">
        ${sblcDocumentPackageData().map((doc) => {
          const status = sblcPackageStatus(doc.id);
          return `
            <article class="sblc-package-card sblc-package-card--${escapeHtml(status.state)}">
              <div class="sblc-package-card__head">
                <span>${escapeHtml(doc.required ? (lang() === "zh" ? "必需" : "Required") : (lang() === "zh" ? "后续" : "Later"))}</span>
                <strong>${escapeHtml(status.label)}</strong>
              </div>
              <h3>${escapeHtml(doc.title)}</h3>
              <p>${escapeHtml(doc.description)}</p>
              <div class="sblc-package-files">
                ${status.items.length ? status.items.map((item) => `<em>${escapeHtml(item.name)}</em>`).join("") : `<em>${lang() === "zh" ? "尚未上传" : "No file yet"}</em>`}
              </div>
              <label class="btn btn-ghost sblc-package-upload">
                <input type="file" multiple hidden data-sblc-upload="${escapeHtml(doc.id)}">
                ${lang() === "zh" ? "上传资料" : "Upload"}
              </label>
            </article>
          `;
        }).join("")}
      </div>
    </section>
    <div class="sblc-issuer-layout">
      <section class="sblc-issuer-panel">
        <div class="sblc-panel-head">
          <span>${lang() === "zh" ? "自动预警矩阵" : "Automated Warning Matrix"}</span>
          <strong>${lang() === "zh" ? "缺口、不一致、顺序异常和硬性限制" : "Gaps, mismatches, sequence issues, and hard restrictions"}</strong>
        </div>
        <div class="sblc-warning-stack">
          ${sblcCrossCheckWarnings().map((item) => `<article><strong>${escapeHtml(item[0])}</strong><p>${escapeHtml(item[1])}</p></article>`).join("")}
        </div>
      </section>
      <section class="sblc-issuer-panel">
        <div class="sblc-panel-head">
          <span>${lang() === "zh" ? "差异雷达" : "Discrepancy Radar"}</span>
          <strong>${lang() === "zh" ? "主体、金额、币种、银行、日期、角色、费用、有效期" : "Parties, amount, currency, bank, dates, roles, fees, validity"}</strong>
        </div>
        <div class="sblc-radar-grid">
          ${sblcFieldRadarData().map((item) => `
            <article class="sblc-radar-item sblc-radar-item--${escapeHtml(item.state)}">
              ${renderStatusBadge(item.label, item.state)}
              <strong>${escapeHtml(item.title)}</strong>
              <span>${escapeHtml(item.detail)}</span>
            </article>
          `).join("")}
        </div>
      </section>
      <section class="sblc-issuer-panel">
        <div class="sblc-panel-head">
          <span>${lang() === "zh" ? "审核意见文件出口" : "Review Opinion Output"}</span>
          <strong>${lang() === "zh" ? "一键生成后在输出中心导出 Word / PDF" : "Generate, then export from Output Center"}</strong>
        </div>
        <div class="sblc-prompt-stack">
          <button type="button" data-sblc-review-output="full">${lang() === "zh" ? "生成完整审核意见" : "Full review opinion"}</button>
          <button type="button" data-sblc-review-output="inconsistency">${lang() === "zh" ? "生成不一致预警矩阵" : "Inconsistency matrix"}</button>
          <button type="button" data-sblc-review-output="conditions">${lang() === "zh" ? "生成条件闸口追踪表" : "Conditions tracker"}</button>
        </div>
        <p class="sblc-output-note">${lang() === "zh" ? "点击后会把专业审核 prompt 填入输入框；发送给 Hermes 后，可在下方输出中心生成审核意见文件。" : "Click to fill a professional review prompt; send it to Hermes, then generate the review file from the Output Center below."}</p>
      </section>
    </div>
  `;
  if (!existing) {
    const infoRow = body.querySelector(".workspace-info-row");
    if (infoRow?.nextSibling) body.insertBefore(section, infoRow.nextSibling);
    else body.prepend(section);
  }
  section.querySelectorAll("[data-sblc-prompt]").forEach((button) => {
    if (button.dataset.boundSblcPrompt === "1") return;
    button.dataset.boundSblcPrompt = "1";
    button.addEventListener("click", async () => {
      const input = document.getElementById("financeInput");
      const prompt = sblcIssuerPrompt(button.dataset.sblcPrompt);
      if (input) {
        input.value = prompt;
        input.focus();
      }
      try {
        await navigator.clipboard.writeText(prompt);
      } catch {
        // The composer fill is the primary action; clipboard is only a convenience.
      }
    });
  });
  section.querySelectorAll("[data-sblc-review-output]").forEach((button) => {
    if (button.dataset.boundSblcReviewOutput === "1") return;
    button.dataset.boundSblcReviewOutput = "1";
    button.addEventListener("click", async () => {
      const input = document.getElementById("financeInput");
      const prompt = sblcReviewOpinionPrompt(button.dataset.sblcReviewOutput);
      if (input) {
        input.value = prompt;
        input.focus();
      }
      try {
        await navigator.clipboard.writeText(prompt);
      } catch {}
    });
  });
  section.querySelectorAll("[data-sblc-upload]").forEach((input) => {
    if (input.dataset.boundSblcUpload === "1") return;
    input.dataset.boundSblcUpload = "1";
    input.addEventListener("change", async () => {
      const categoryId = input.dataset.sblcUpload;
      const doc = sblcDocumentPackageData().find((item) => item.id === categoryId);
      for (const file of Array.from(input.files || [])) {
        await attachFileToWorkspace("finance", file, undefined, {
          sblcCategory: categoryId,
          sblcLabel: doc?.title || categoryId,
          sblcUploadedAt: new Date().toISOString(),
        });
      }
      input.value = "";
      renderSblcIssuerControlTower();
      ensureOutputCenter("finance", "financeMessages", () => currentLocaleMeta(appState.currentSkillId));
    });
  });
}

function renderWorkspaceDecisionRail(workspaceKey, meta) {
  const root = document.getElementById(workspaceKey);
  const head = root?.querySelector(".workspace-head");
  if (!head || !meta) return;
  let rail = head.querySelector("[data-workspace-decision-rail]");
  if (!rail) {
    rail = document.createElement("div");
    rail.className = "workspace-decision-rail";
    rail.setAttribute("data-workspace-decision-rail", "1");
    head.appendChild(rail);
  }
  const zh = lang() === "zh";
  const skillId = workspaceKey === "legal"
    ? (new URLSearchParams(location.search).get("platform") || "uk_hk_financial_contract_counsel")
    : appState.currentSkillId;
  const route = preferredChatRoute(workspaceKey, appState.routeState[workspaceKey] || {}, { hasImages: false });
  const actions = quickActionsForSkill(skillId).slice(0, 4);
  const selectedIndex = Number.isInteger(appState.actionSelection[workspaceKey]) ? appState.actionSelection[workspaceKey] : 0;
  const stages = [
    [zh ? "收集" : "Intake", zh ? "材料/问题" : "Material"],
    [zh ? "分析" : "Analysis", actions[selectedIndex]?.[0] || meta.modes?.[0]?.[1] || "Review"],
    [zh ? "复核" : "Review", zh ? "风险/缺口" : "Risk / gaps"],
    [zh ? "交付" : "Deliver", preferredExportFormat(workspaceKey).toUpperCase()],
  ];
  rail.innerHTML = `
    <div class="workspace-decision-rail__head">
      <div>
        <span>${zh ? "工作路径" : "Workflow Path"}</span>
        <strong>${escapeHtml(compactPlatformName(meta.name || pageTitleLabel(workspaceKey)))}</strong>
      </div>
      <em>${escapeHtml(route.provider || "--")} / ${escapeHtml(route.model || "--")}</em>
    </div>
    <div class="workspace-decision-rail__steps">
      ${stages.map((stage, index) => `
        <div class="workspace-decision-step ${index === Math.min(selectedIndex, 3) ? "is-current" : ""}">
          <span>${escapeHtml(String(index + 1).padStart(2, "0"))}</span>
          <strong>${escapeHtml(stage[0])}</strong>
          <small>${escapeHtml(stage[1])}</small>
        </div>
      `).join("")}
    </div>
  `;
}

function applyWorkspaceMeta() {
  const financeMeta = currentLocaleMeta(appState.currentSkillId);
  const financeRoot = document.getElementById("finance");
  if (financeRoot) {
    const title = financeRoot.querySelector(".platform-title");
    const desc = financeRoot.querySelector(".platform-desc");
    const statusMode = financeRoot.querySelector(".status-mini-card strong");
    const routeCard = financeRoot.querySelectorAll(".status-mini-card strong")[1];
    const welcome = financeRoot.querySelector(".welcome");
    const input = document.getElementById("financeInput");
    const threadList = financeRoot.querySelector(".thread-list");
    const miniStatus = financeRoot.querySelector(".mini-status");
    if (title) title.textContent = financeMeta.name;
    if (desc) {
      if (appState.currentSkillId === "google-workspace") {
        const profile = currentGoogleProfile();
        desc.textContent = `${financeMeta.desc} ${lang() === "zh" ? "当前邮箱：" : "Current mailbox: "}${googleMailboxLabel(profile)}`;
      } else if (appState.currentSkillId === "composio-workspace") {
        const profile = currentComposioProfile();
        desc.textContent = `${financeMeta.desc} ${lang() === "zh" ? "当前账号：" : "Current account: "}${composioMailboxLabel(profile)}`;
      } else {
        desc.textContent = financeMeta.desc;
      }
    }
    if (statusMode) statusMode.textContent = financeMeta.modes[0][1];
    if (routeCard) {
      routeCard.textContent = appState.currentSkillId === "google-workspace"
        ? currentGoogleProfile().label
        : appState.currentSkillId === "composio-workspace"
          ? currentComposioProfile().label
        : appState.currentSkillId;
    }
    if (welcome) {
      const mailboxLine = appState.currentSkillId === "google-workspace"
        ? `<br>${escapeHtml(lang() === "zh" ? `当前邮箱：${googleMailboxLabel(currentGoogleProfile())}` : `Current mailbox: ${googleMailboxLabel(currentGoogleProfile())}`)}`
        : appState.currentSkillId === "composio-workspace"
          ? `<br>${escapeHtml(lang() === "zh" ? `当前账号：${composioMailboxLabel(currentComposioProfile())}` : `Current account: ${composioMailboxLabel(currentComposioProfile())}`)}`
        : "";
      welcome.innerHTML = `<strong>${lang() === "zh" ? "欢迎说明" : "Workspace Brief"}</strong><br>${escapeHtml(financeMeta.welcome)}${mailboxLine}`;
    }
    if (input) input.placeholder = financeMeta.promptPlaceholder;
    syncConversationThreads("finance", appState.currentSkillId, financeMeta);
    if (miniStatus) {
      let badge = miniStatus.querySelector(".google-mailbox-badge");
      if (appState.currentSkillId === "google-workspace") {
        if (!badge) {
          badge = document.createElement("span");
          badge.className = "mini-pill google-mailbox-badge";
          miniStatus.appendChild(badge);
        }
        badge.textContent = currentGoogleProfile().label;
      } else if (appState.currentSkillId === "composio-workspace") {
        if (!badge) {
          badge = document.createElement("span");
          badge.className = "mini-pill google-mailbox-badge";
          miniStatus.appendChild(badge);
        }
        badge.textContent = currentComposioProfile().label;
      } else if (badge) {
        badge.remove();
      }
    }
    syncWorkspaceActionRow("finance", "financeInput", "financeMessages", () => currentLocaleMeta(appState.currentSkillId));
    ensureOutputCenter("finance", "financeMessages", () => currentLocaleMeta(appState.currentSkillId));
    ensureSidebarProgressPanel("finance");
    renderWorkspaceDecisionRail("finance", financeMeta);
    renderSblcIssuerControlTower();
    refreshConversationHistory("finance", document.getElementById("financeMessages"));
  }

  const legalId = new URLSearchParams(location.search).get("platform") || "uk_hk_financial_contract_counsel";
  const legalMeta = currentLocaleMeta(legalId in PLATFORM_META ? legalId : "uk_hk_financial_contract_counsel");
  const legalRoot = document.getElementById("legal");
  if (legalRoot) {
    const title = legalRoot.querySelector(".platform-title");
    const desc = legalRoot.querySelector(".platform-desc");
    const welcome = legalRoot.querySelector(".welcome");
    const input = document.getElementById("legalInput");
    const skillIdNode = legalRoot.querySelector("[data-bind='legal-skill-id']");
    const displayNameNode = document.querySelector("[data-bind='legal-display-name']");
    const threadList = legalRoot.querySelector(".thread-list");
    if (title) title.textContent = legalMeta.name;
    if (desc) desc.textContent = legalMeta.desc;
    if (welcome) welcome.innerHTML = `<strong>${lang() === "zh" ? "欢迎说明" : "Workspace Brief"}</strong><br>${escapeHtml(legalMeta.welcome)}`;
    if (input) input.placeholder = legalMeta.promptPlaceholder;
    if (skillIdNode) skillIdNode.textContent = legalId;
    if (displayNameNode) displayNameNode.textContent = legalMeta.name;
    syncConversationThreads("legal", legalId, legalMeta);
    syncWorkspaceActionRow("legal", "legalInput", "legalMessages", () => legalMeta);
    ensureOutputCenter("legal", "legalMessages", () => legalMeta);
    ensureSidebarProgressPanel("legal");
    renderWorkspaceDecisionRail("legal", legalMeta);
    refreshConversationHistory("legal", document.getElementById("legalMessages"));
  }
  renderGoogleWorkspaceProfilePanel();
  renderComposioProfilePanel();
}

function ensureAttachmentRow(workspaceKey, inputId) {
  const input = document.getElementById(inputId);
  const host = input?.closest(".chat-card, .composer");
  if (!host || host.querySelector(".attachment-row")) return;
  const storageKey = effectiveWorkspaceKey(workspaceKey);
  const row = document.createElement("div");
  row.className = "attachment-row";
  row.innerHTML = `
    <div class="attachment-toolbar">
      <label class="btn btn-ghost attachment-add">
        <input type="file" data-role="attachment-input" multiple hidden>
        <span>${lang() === "zh" ? "添加附件" : "Add Attachment"}</span>
      </label>
      <div class="file-name" data-role="attachment-status">${lang() === "zh" ? "最近附件：尚未上传文件。" : "Latest attachment: no file uploaded yet."}</div>
    </div>
    <div class="attachment-list" data-role="attachment-list"></div>
  `;
  host.appendChild(row);
  const fileInput = row.querySelector("[data-role='attachment-input']");
  const list = row.querySelector("[data-role='attachment-list']");
  const status = row.querySelector("[data-role='attachment-status']");
  const render = () => {
    const items = appState.attachments[storageKey];
    if (!items.length) {
      list.innerHTML = "";
      status.textContent = lang() === "zh" ? "最近附件：尚未上传文件。" : "Latest attachment: no file uploaded yet.";
      return;
    }
    status.textContent = (lang() === "zh" ? "最近附件：" : "Latest attachment: ") + items.map((item) => item.name).join(", ");
    list.innerHTML = items.map((item, idx) => `
      <div class="tag">
        ${escapeHtml(item.name)}
        <button type="button" class="attachment-remove" data-index="${idx}">×</button>
      </div>
    `).join("");
    list.querySelectorAll(".attachment-remove").forEach((button) => {
      button.addEventListener("click", () => {
        appState.attachments[storageKey].splice(Number(button.dataset.index), 1);
        render();
      });
    });
  };
  fileInput.addEventListener("change", async () => {
    const files = Array.from(fileInput.files || []);
    for (const file of files) {
      await attachFileToWorkspace(storageKey, file, ({ status: nextStatus }) => {
        if (nextStatus) status.textContent = nextStatus;
      });
    }
    render();
    fileInput.value = "";
  });
  render();
}

function syncWorkspaceActionRow(workspaceKey, inputId, messageId, metaGetter) {
  const root = document.getElementById(workspaceKey);
  const composer = root?.querySelector(".composer");
  const composerRow = composer?.querySelector(".composer-row");
  const input = document.getElementById(inputId);
  const messages = document.getElementById(messageId);
  if (!composer || !composerRow || !input || !messages) return;

  let row = composer.querySelector(".workspace-action-row");
  const skillId = workspaceKey === "legal"
    ? (new URLSearchParams(location.search).get("platform") || "uk_hk_financial_contract_counsel")
    : appState.currentSkillId;
  const actions = quickActionsForSkill(skillId).slice(0, 5);
  if (!actions.length) return;
  const selectedIndex = Number.isInteger(appState.actionSelection[workspaceKey]) ? appState.actionSelection[workspaceKey] : 0;

  if (!row) {
    row = document.createElement("div");
    row.className = "workspace-action-row";
    composerRow.insertAdjacentElement("beforebegin", row);
  }

  row.innerHTML = `
    <div class="workspace-action-title">${lang() === "zh" ? "专用动作" : "Specialized Actions"}</div>
    <div class="workspace-action-buttons">
      ${actions.map((action, idx) => `
        <button class="btn ${idx === selectedIndex ? "btn-primary" : "btn-ghost"} workspace-action-btn" type="button" data-action-index="${idx}">
          <strong>${escapeHtml(action[0])}</strong>
          <span>${escapeHtml(action[1])}</span>
        </button>
      `).join("")}
    </div>
    <div class="workspace-action-note">${lang() === "zh" ? "每个按钮会按当前工作平台载入专用任务；Slack 前三项会读取已授权 workspace 的真实消息。" : "Each button loads a task tailored to this workspace. The first three Slack actions read real messages from the connected workspace."}</div>
  `;
  row.querySelectorAll("[data-action-index]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextIndex = Number(button.dataset.actionIndex);
      appState.actionSelection[workspaceKey] = nextIndex;
      row.querySelectorAll("[data-action-index]").forEach((item) => {
        item.classList.toggle("btn-primary", item === button);
        item.classList.toggle("btn-ghost", item !== button);
      });
      syncConversationThreads(workspaceKey, skillId, metaGetter());
      renderWorkspaceDecisionRail(workspaceKey, metaGetter());
      const action = actions[nextIndex];
      if (action) runQuickWorkspaceAction(action, skillId, input, messages, metaGetter);
    });
  });
}

function ensureOutputCenter(workspaceKey, messageId, metaGetter) {
  const root = document.getElementById(workspaceKey);
  const composer = root?.querySelector(".composer");
  const messageBox = document.getElementById(messageId);
  if (!composer || !messageBox) return;
  const exportWorkspaceKey = effectiveWorkspaceKey(workspaceKey);

  let panel = composer.querySelector(".output-center");
  if (!panel) {
    panel = document.createElement("div");
    panel.className = "output-center";
    panel.innerHTML = `
      <div class="output-center__head">
        <div>
          <div class="workspace-action-title">${lang() === "zh" ? "输出中心" : "Output Center"}</div>
          <div class="output-center__hint">${lang() === "zh" ? "处理完成后可导出并下载。文件会保存到 /Users/billtin/Documents/Export Documents。" : "Export and download the result after processing. Files are stored in /Users/billtin/Documents/Export Documents."}</div>
        </div>
        <div class="output-center__controls">
          <select class="output-center__select" data-role="export-format">
            <option value="md">Markdown (.md)</option>
            <option value="txt">Text (.txt)</option>
            <option value="json">JSON (.json)</option>
            <option value="rtf">Apple TextEdit / Pages (.rtf)</option>
            <option value="csv">Apple Numbers CSV (.csv)</option>
            <option value="pages">Apple Pages Compatible (.docx)</option>
            <option value="numbers">Apple Numbers Compatible (.xlsx)</option>
            <option value="key">Apple Keynote Compatible (.pptx)</option>
            <option value="docx">Word (.docx)</option>
            <option value="xlsx">Excel (.xlsx)</option>
            <option value="pptx">PowerPoint (.pptx)</option>
          </select>
          <button class="btn btn-primary" type="button" data-role="export-run">${lang() === "zh" ? "生成文件" : "Generate File"}</button>
        </div>
      </div>
      <div class="output-center__meta">
        <div class="output-meta-card">
          <span>${lang() === "zh" ? "输出位置" : "Storage"}</span>
          <strong data-role="export-storage">${workspaceKey}</strong>
        </div>
        <div class="output-meta-card">
          <span>${lang() === "zh" ? "进度" : "Progress"}</span>
          <strong data-role="export-progress">${lang() === "zh" ? "等待结果" : "Waiting for result"}</strong>
        </div>
        <div class="output-meta-card">
          <span>${lang() === "zh" ? "最新文件" : "Latest File"}</span>
          <strong data-role="export-latest">${lang() === "zh" ? "尚未生成" : "Not generated yet"}</strong>
        </div>
      </div>
      <div class="output-center__actions" data-role="export-actions"></div>
      <div class="dlp-export-note">
        ${lang() === "zh" ? "DLP 提示：导出与下载会进入审计留痕；涉及 KYC、AML、UBO、SWIFT、银行账户或客户敏感资料时，请确认 need-to-know 与外发权限。" : "DLP notice: exports and downloads are audit-tracked. For KYC, AML, UBO, SWIFT, bank account, or sensitive client data, verify need-to-know and sharing permission."}
      </div>
    `;
    composer.appendChild(panel);
  }

  const formatSelect = panel.querySelector("[data-role='export-format']");
  const runButton = panel.querySelector("[data-role='export-run']");
  const storageNode = panel.querySelector("[data-role='export-storage']");
  const progressNode = panel.querySelector("[data-role='export-progress']");
  const latestNode = panel.querySelector("[data-role='export-latest']");
  const actionsNode = panel.querySelector("[data-role='export-actions']");
  const exportState = appState.outputs[workspaceKey];
  const meta = metaGetter();

  formatSelect.value = formatSelect.value || preferredExportFormat(workspaceKey);
  if (!formatSelect.dataset.seeded) {
    formatSelect.value = preferredExportFormat(workspaceKey);
    formatSelect.dataset.seeded = "1";
  }
  storageNode.textContent = exportState?.lastExport?.storage_dir || `/Users/billtin/Documents/Export Documents/${exportWorkspaceKey}`;
  progressNode.textContent = exportState?.lastExport?.progressLabel || (lang() === "zh" ? "等待结果" : "Waiting for result");
  latestNode.textContent = exportState?.lastExport?.filename || (lang() === "zh" ? "尚未生成" : "Not generated yet");
  actionsNode.innerHTML = exportState?.lastExport?.download_url
    ? `<button class="btn btn-ghost" type="button" data-role="export-download">${lang() === "zh" ? "下载文件" : "Download File"}</button>`
    : `<span class="output-center__empty">${lang() === "zh" ? `${meta.name} 生成完内容后，就可以在这里导出 Word / Excel / PowerPoint。` : `Once ${meta.name} produces a result, you can export it here as Word, Excel, or PowerPoint.`}</span>`;
  ensureSidebarProgressPanel(workspaceKey);

  if (runButton.dataset.bound === "1") return;
  runButton.dataset.bound = "1";
  runButton.addEventListener("click", async () => {
    const snapshot = appState.outputs[workspaceKey];
    if (!snapshot?.result?.trim()) {
      progressNode.textContent = lang() === "zh" ? "还没有可导出的 Hermes 输出。" : "There is no Hermes result to export yet.";
      return;
    }
    const selectedFormat = formatSelect.value;
    const exportTitle = `${meta.name} ${lang() === "zh" ? "输出" : "Output"}`;
    const exportProgressId = `${workspaceKey}-export-${Date.now()}`;
    progressNode.textContent = lang() === "zh" ? "准备内容..." : "Preparing content...";
    runButton.disabled = true;
    actionsNode.innerHTML = "";
    upsertIoProgress(workspaceKey, {
      id: exportProgressId,
      file: exportTitle,
      type: lang() === "zh" ? "导出" : "Export",
      status: lang() === "zh" ? "准备中" : "Preparing",
      progress: 10,
    });
    try {
      progressNode.textContent = lang() === "zh" ? "正在生成文件..." : "Generating file...";
      upsertIoProgress(workspaceKey, {
        id: exportProgressId,
        file: exportTitle,
        type: lang() === "zh" ? "导出" : "Export",
        status: lang() === "zh" ? "生成中" : "Generating",
        progress: 65,
      });
      const resp = await fetch("/api/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          workspace: exportWorkspaceKey,
          format: selectedFormat,
          title: exportTitle,
          skill_id: snapshot.skillId,
          prompt: snapshot.prompt,
          assistant_text: snapshot.result,
          attachments: snapshot.attachments || [],
        }),
      });
      const data = await resp.json();
      if (!resp.ok || !data.ok) {
        throw new Error(data.error || `Export ${selectedFormat} failed`);
      }
      appState.outputs[workspaceKey] = {
        ...snapshot,
        lastExport: {
          ...data,
          progressLabel: lang() === "zh" ? "已完成" : "Ready",
        },
      };
      storageNode.textContent = data.storage_dir || storageNode.textContent;
      progressNode.textContent = lang() === "zh" ? "已完成" : "Ready";
      latestNode.textContent = data.filename || latestNode.textContent;
      upsertIoProgress(workspaceKey, {
        id: exportProgressId,
        file: data.filename || exportTitle,
        type: lang() === "zh" ? "导出" : "Export",
        status: lang() === "zh" ? "已完成" : "Completed",
        progress: 100,
      });
      actionsNode.innerHTML = `<button class="btn btn-ghost" type="button" data-role="export-download">${lang() === "zh" ? "下载文件" : "Download File"}</button>`;
      const downloadButton = actionsNode.querySelector("[data-role='export-download']");
      downloadButton?.addEventListener("click", async () => {
        const downloadId = `${workspaceKey}-download-${Date.now()}`;
        const filename = data.filename || "workspace-output";
        upsertIoProgress(workspaceKey, {
          id: downloadId,
          file: filename,
          type: lang() === "zh" ? "下载" : "Download",
          status: lang() === "zh" ? "准备中" : "Preparing",
          progress: 5,
        });
        try {
          const resp = await fetch(data.download_url);
          if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
          const total = Number(resp.headers.get("Content-Length") || 0);
          const reader = resp.body?.getReader();
          if (!reader) {
            const blob = await resp.blob();
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = filename;
            link.click();
            URL.revokeObjectURL(url);
            upsertIoProgress(workspaceKey, {
              id: downloadId,
              file: filename,
              type: lang() === "zh" ? "下载" : "Download",
              status: lang() === "zh" ? "已完成" : "Completed",
              progress: 100,
            });
            return;
          }
          const chunks = [];
          let loaded = 0;
          while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            if (value) {
              chunks.push(value);
              loaded += value.length;
              upsertIoProgress(workspaceKey, {
                id: downloadId,
                file: filename,
                type: lang() === "zh" ? "下载" : "Download",
                status: lang() === "zh" ? "下载中" : "Downloading",
                progress: total ? Math.min(99, Math.round((loaded / total) * 100)) : 70,
              });
            }
          }
          const blob = new Blob(chunks);
          const url = URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = filename;
          link.click();
          URL.revokeObjectURL(url);
          upsertIoProgress(workspaceKey, {
            id: downloadId,
            file: filename,
            type: lang() === "zh" ? "下载" : "Download",
            status: lang() === "zh" ? "已完成" : "Completed",
            progress: 100,
          });
        } catch (error) {
          upsertIoProgress(workspaceKey, {
            id: downloadId,
            file: data.filename || "workspace-output",
            type: lang() === "zh" ? "下载" : "Download",
            status: `${lang() === "zh" ? "失败" : "Failed"}: ${error.message || error}`,
            progress: 0,
          });
        }
      });
    } catch (error) {
      progressNode.textContent = `${lang() === "zh" ? "生成失败：" : "Export failed: "}${error.message || error}`;
      upsertIoProgress(workspaceKey, {
        id: exportProgressId,
        file: exportTitle,
        type: lang() === "zh" ? "导出" : "Export",
        status: `${lang() === "zh" ? "失败" : "Failed"}: ${error.message || error}`,
        progress: 0,
      });
    } finally {
      runButton.disabled = false;
    }
  });
}

function providerOptions() {
  return Object.entries(providerMetaMap()).filter(([, value]) => value?.models?.length);
}

async function ensureRouteMenuReady(workspaceKey) {
  if (!appState.status) await loadStatus();
  const effectiveKey = effectiveWorkspaceKey(workspaceKey);
  if (effectiveKey === "finance" && appState.currentSkillId === "google-workspace" && !(appState.googleWorkspace.profiles || []).length) {
    await loadGoogleWorkspaceProfiles();
  }
  if (effectiveKey === "finance" && appState.currentSkillId === "composio-workspace" && !(appState.composioWorkspace.profiles || []).length) {
    await loadComposioProfiles();
  }
}

function buildToolMenus(workspaceKey, inputId, metaGetter) {
  const root = document.getElementById(workspaceKey);
  const composer = root?.querySelector(".composer");
  const toolRow = composer?.querySelector(".tool-row");
  if (!composer || !toolRow || composer.querySelector(".tool-menu")) return;
  if (!composer.querySelector("[data-role='composer-route-line']")) {
    const routeLine = document.createElement("div");
    routeLine.className = "composer-route-line";
    routeLine.dataset.role = "composer-route-line";
    routeLine.textContent = composerRouteLineText(workspaceKey);
    toolRow.insertAdjacentElement("afterend", routeLine);
  }
  const buttons = Array.from(toolRow.querySelectorAll(".tool-btn"));
  const labels = lang() === "zh"
    ? ["路由设置 ▾", "工作模式 ▾", "快捷模板 ▾"]
    : ["Route Settings ▾", "Work Mode ▾", "Quick Templates ▾"];
  buttons.forEach((button, index) => {
    button.dataset.menu = ["route", "mode", "template"][index];
    button.textContent = index === 0 ? routeButtonText((appState.routeState[effectiveWorkspaceKey(workspaceKey)] || {}).provider || "chatgpt") : (labels[index] || button.textContent);
  });
  const routeMenu = document.createElement("div");
  routeMenu.className = "tool-menu";
  routeMenu.dataset.role = "route";
  routeMenu.innerHTML = `
    <div class="tool-field">
      <label>${lang() === "zh" ? "Channel" : "Channel"}</label>
      <select data-role="provider"></select>
      <div class="tool-note" data-role="provider-hint"></div>
    </div>
    <div class="tool-field">
      <label>${lang() === "zh" ? "Model" : "Model"}</label>
      <select data-role="model"></select>
      <div class="tool-note" data-role="model-hint"></div>
    </div>
    <div class="tool-field google-profile-field" style="display:none;">
      <label>${lang() === "zh" ? "Mailbox" : "Mailbox"}</label>
      <select data-role="google-profile"></select>
    </div>
    <div class="tool-actions">
      <button class="btn btn-primary" type="button" data-role="apply">${lang() === "zh" ? "应用路由" : "Apply Route"}</button>
    </div>
  `;
  const modeMenu = document.createElement("div");
  modeMenu.className = "tool-menu";
  modeMenu.dataset.role = "mode";
  modeMenu.innerHTML = `<div class="template-list" data-role="modes"></div>`;
  const templateMenu = document.createElement("div");
  templateMenu.className = "tool-menu";
  templateMenu.dataset.role = "template";
  templateMenu.innerHTML = `<div class="template-list" data-role="templates"></div>`;
  toolRow.insertAdjacentElement("afterend", routeMenu);
  routeMenu.insertAdjacentElement("afterend", modeMenu);
  modeMenu.insertAdjacentElement("afterend", templateMenu);

  async function fillRouteMenu() {
    await ensureRouteMenuReady(workspaceKey);
    const providerSelect = routeMenu.querySelector("[data-role='provider']");
    const modelSelect = routeMenu.querySelector("[data-role='model']");
    const providerHint = routeMenu.querySelector("[data-role='provider-hint']");
    const modelHint = routeMenu.querySelector("[data-role='model-hint']");
    const profileField = routeMenu.querySelector(".google-profile-field");
    const profileSelect = routeMenu.querySelector("[data-role='google-profile']");
    const state = appState.routeState[effectiveWorkspaceKey(workspaceKey)];
    const providers = routeProviderOptions();
    if (!providers.length && !appState.status) {
      await loadStatus();
    }
    providerSelect.innerHTML = providers.map(([key, value]) => {
      const label = value.label || key;
      return `<option value="${key}">${escapeHtml(label)}</option>`;
    }).join("");
    const manualOverride = Boolean(state.manual_override && state.provider);
    providerSelect.value = manualOverride ? state.provider : "auto";
    const refillModels = () => {
      const models = routeProviderModels(providerSelect.value);
      modelSelect.innerHTML = models.map((model) => `<option value="${model}">${escapeHtml(model)}</option>`).join("");
      if (providerSelect.value === "auto") {
        modelSelect.value = "auto-smart";
      } else {
        modelSelect.value = models.includes(state.model) ? state.model : models[0] || "";
      }
      if (providerHint) {
        providerHint.textContent = routeProviderHint(providerSelect.value);
      }
      if (modelHint) {
        modelHint.textContent = routeModelHint(providerSelect.value, modelSelect.value);
      }
    };
    refillModels();
    providerSelect.onchange = refillModels;
    modelSelect.onchange = () => {
      if (modelHint) {
        modelHint.textContent = routeModelHint(providerSelect.value, modelSelect.value);
      }
    };
    const effectiveKey = effectiveWorkspaceKey(workspaceKey);
    const needsGoogleProfile = effectiveKey === "finance" && appState.currentSkillId === "google-workspace";
    const needsComposioProfile = effectiveKey === "finance" && appState.currentSkillId === "composio-workspace";
    profileField.style.display = needsGoogleProfile || needsComposioProfile ? "block" : "none";
    if (needsGoogleProfile) {
      const profiles = appState.googleWorkspace.profiles || [];
      profileSelect.innerHTML = profiles.map((item) => {
        const suffix = item.email ? ` · ${item.email}` : "";
        const auth = item.authenticated ? "" : (lang() === "zh" ? " · 待授权" : " · Auth Needed");
        return `<option value="${item.id}">${escapeHtml(`${item.label}${suffix}${auth}`)}</option>`;
      }).join("");
      profileSelect.value = appState.googleWorkspace.currentProfile || profiles.find((item) => item.default)?.id || "saerc";
    } else if (needsComposioProfile) {
      const profiles = appState.composioWorkspace.profiles || [];
      profileSelect.innerHTML = profiles.map((item) => {
        const suffix = item.email ? ` · ${item.email}` : "";
        const auth = item.authenticated ? "" : (lang() === "zh" ? " · 待授权" : " · Auth Needed");
        return `<option value="${item.id}">${escapeHtml(`${item.label}${suffix}${auth}`)}</option>`;
      }).join("");
      profileSelect.value = appState.composioWorkspace.currentProfile || profiles.find((item) => item.default)?.id || "fastonegroup";
    }
  }

  function fillModeMenu() {
    const meta = metaGetter();
    const state = appState.routeState[effectiveWorkspaceKey(workspaceKey)];
    const target = modeMenu.querySelector("[data-role='modes']");
    target.innerHTML = meta.modes.map((mode) => `
      <button class="template-item" type="button" data-mode="${escapeHtml(mode[0])}">
        <strong>${escapeHtml(mode[1])}</strong>
        <span>${escapeHtml(mode[2])}</span>
      </button>
    `).join("");
    target.querySelectorAll("[data-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        state.mode = button.dataset.mode;
        modeMenu.classList.remove("open");
      });
    });
  }

  function fillTemplateMenu() {
    const meta = metaGetter();
    const input = document.getElementById(inputId);
    const target = templateMenu.querySelector("[data-role='templates']");
    target.innerHTML = meta.templates.map((tpl, idx) => `
      <button class="template-item" type="button" data-template="${idx}">
        <strong>${escapeHtml(tpl[0])}</strong>
        <span>${escapeHtml(tpl[1])}</span>
      </button>
    `).join("");
    target.querySelectorAll("[data-template]").forEach((button) => {
      button.addEventListener("click", () => {
        const tpl = meta.templates[Number(button.dataset.template)];
        if (input && tpl) input.value = tpl[2];
        templateMenu.classList.remove("open");
      });
    });
  }

  fillRouteMenu();
  fillModeMenu();
  fillTemplateMenu();

  toolRow.addEventListener("click", async (event) => {
    const button = event.target.closest(".tool-btn");
    if (!button) return;
    const key = button.dataset.menu;
    if (!key) return;
    if (key === "route") await fillRouteMenu();
    if (key === "mode") fillModeMenu();
    if (key === "template") fillTemplateMenu();
    const targetMenu = composer.querySelector(`.tool-menu[data-role='${key}']`);
    const shouldOpen = !targetMenu?.classList.contains("open");
    composer.querySelectorAll(".tool-menu").forEach((menu) => {
      menu.classList.toggle("open", menu === targetMenu ? shouldOpen : false);
    });
    if (key === "route" && shouldOpen) {
      requestAnimationFrame(() => {
        targetMenu?.querySelector("[data-role='provider']")?.focus();
      });
    }
  });

  routeMenu.querySelector("[data-role='apply']").addEventListener("click", async () => {
    const provider = routeMenu.querySelector("[data-role='provider']").value;
    const model = routeMenu.querySelector("[data-role='model']").value;
    const profileSelect = routeMenu.querySelector("[data-role='google-profile']");
    const button = routeMenu.querySelector("[data-role='apply']");
    const original = button.textContent;
    button.disabled = true;
    button.textContent = lang() === "zh" ? "应用中..." : "Applying...";
    const effectiveKey = effectiveWorkspaceKey(workspaceKey);
    if (effectiveKey === "finance" && profileSelect?.value) {
      const selectedProfile = profileSelect.value;
      if (appState.currentSkillId === "google-workspace") {
        await switchGoogleWorkspaceProfile(selectedProfile, { silent: true });
      } else if (appState.currentSkillId === "composio-workspace") {
        await switchComposioProfile(selectedProfile, { silent: true });
      }
    }
    if (provider === "auto") {
      appState.routeState[effectiveKey].provider = "";
      appState.routeState[effectiveKey].model = "";
      appState.routeState[effectiveKey].manual_override = false;
      refreshRouteButtonLabel(workspaceKey);
      refreshComposerRouteLine(workspaceKey);
      routeMenu.classList.remove("open");
      button.disabled = false;
      button.textContent = original;
      return;
    }
    const resp = await fetch("/api/provider", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider, model }),
    });
    if (!resp.ok) {
      button.disabled = false;
      button.textContent = original;
      return;
    }
    const payload = await resp.json();
    appState.routeState[effectiveKey].provider = provider;
    appState.routeState[effectiveKey].model = model;
    appState.routeState[effectiveKey].manual_override = true;
    appState.status = payload.status;
    updateStatusBindings();
    refreshRouteButtonLabel(workspaceKey);
    refreshComposerRouteLine(workspaceKey);
    await waitForRoute(provider, model);
    routeMenu.classList.remove("open");
    button.disabled = false;
    button.textContent = original;
  });

  if (!toolRow.querySelector(`[data-role='clear-conversation'][data-workspace='${workspaceKey}']`)) {
    const clearButton = document.createElement("button");
    clearButton.className = "tool-btn tool-btn-clear";
    clearButton.type = "button";
    clearButton.dataset.role = "clear-conversation";
    clearButton.dataset.workspace = workspaceKey;
    clearButton.textContent = lang() === "zh" ? "清空对话" : "Clear Conversation";
    toolRow.appendChild(clearButton);
  }
}

function bindComposer(inputId, sendId, messageId, workspaceKey, metaGetter) {
  const input = document.getElementById(inputId);
  const send = document.getElementById(sendId);
  const messages = document.getElementById(messageId);
  if (!input || !send || !messages) return;
  const fallback = lang() === "zh"
    ? "已收到任务，Hermes 会按当前工作平台继续处理。"
    : "Task received. Hermes will continue in the active workspace.";

  async function submit(externalText = "", options = {}) {
    const text = (externalText || input.value).trim();
    if (!text) return;
    const effectiveKey = effectiveWorkspaceKey(workspaceKey);
    const mailboxContext = workspaceKey === "finance" && appState.currentSkillId === "google-workspace"
      ? `${googleMailboxPromptLine()}\n`
      : workspaceKey === "finance" && appState.currentSkillId === "composio-workspace"
        ? `${composioMailboxPromptLine()}\n`
        : "";
    const userText = options.fromTelegram ? `Telegram: ${text}` : text;
    const userNode = appendMessage(messages, userText, "user");
    if (userNode) userNode.dataset.historyItem = "1";
    recordConversationEntry(workspaceKey, "user", userText);
    updateConversationArchive(messages);
    if (!externalText) input.value = "";
    send.disabled = true;
    const assistant = appendMessage(messages, lang() === "zh" ? "正在调用 Hermes，请稍候..." : "Hermes is responding. Please wait...", "assistant");
    if (assistant) assistant.dataset.historyItem = "1";
    const route = appState.routeState[effectiveKey];
    const meta = metaGetter();
    const mode = meta.modes.find((item) => item[0] === route.mode)?.[1] || meta.modes[0]?.[1] || "General";
    const attachments = attachmentContext(effectiveKey);
    const imageParts = attachmentImageParts(effectiveKey);
    const hasImages = imageParts.length > 0;
    const chatRoute = preferredChatRoute(workspaceKey, route, {
      hasImages,
      promptText: text,
      attachmentsCount: (appState.attachments[effectiveKey] || []).length,
    });
    let result = "";
    rememberWorkspaceOutput(workspaceKey, text, "", meta);
    try {
      if (workspaceKey === "home" && appState.telegram.enabled && !options.fromTelegram) {
        await sendTelegramBridge(`${lang() === "zh" ? "来自 Hermes 人机交流" : "From Hermes Human Exchange"}:\n${text}`);
      }
      setRouteStatus(lang() === "zh" ? "Calling..." : "Calling...");
      const userPayload = imageParts.length
        ? [
            ...(attachments ? [{ type: "text", text: `${lang() === "zh" ? "附件上下文" : "Attached context"}:\n${attachments}` }] : []),
            { type: "text", text: `${mailboxContext}${text}` },
            ...imageParts,
          ]
        : `${mailboxContext}${text}`;
      const buildMessages = () => {
        const userPayload = hasImages
          ? [
              ...(attachments ? [{ type: "text", text: `${lang() === "zh" ? "附件上下文" : "Attached context"}:\n${attachments}` }] : []),
              { type: "text", text: `${mailboxContext}${text}` },
              ...imageParts,
            ]
          : `${mailboxContext}${text}`;
        return [
          { role: "system", content: buildWorkspaceSystemPrompt(workspaceKey, meta, mode) },
          ...(attachments && !hasImages ? [{ role: "user", content: `${lang() === "zh" ? "附件上下文" : "Attached context"}:\n${attachments}` }] : []),
          { role: "user", content: userPayload },
        ];
      };
      await streamChat(
        buildMessages(),
        chatRoute.provider,
        chatRoute.model,
        effectiveKey,
        (token) => {
          result += token;
          assistant.textContent = result || assistant.textContent;
        },
        (headers) => {
          const provider = headers.get("X-Hermes-Provider");
          const model = headers.get("X-Hermes-Model");
          if (provider) route.provider = provider;
          if (model) route.model = model;
          setRouteStatus(routeStatusFromHeaders(headers));
        },
        { fastMode: workspaceKey === "home" }
      );
      if (hasImages && looksLikeImageBlindReply(result)) {
        result = "";
        assistant.textContent = lang() === "zh"
          ? "正在切换看图通道，请稍候..."
          : "Switching to an image-capable route. Please wait...";
        const retryRoute = { provider: "chatgpt", model: "gpt-5.4" };
        await streamChat(
          buildMessages(),
          retryRoute.provider,
          retryRoute.model,
          effectiveKey,
          (token) => {
            result += token;
            assistant.textContent = result || assistant.textContent;
          },
          (headers) => {
            const provider = headers.get("X-Hermes-Provider");
            const model = headers.get("X-Hermes-Model");
            if (provider) route.provider = provider;
            if (model) route.model = model;
            setRouteStatus(routeStatusFromHeaders(headers));
          },
          { fastMode: workspaceKey === "home" }
        );
      }
      const finalText = sanitizeProfessionalText(result.trim() || fallback, { workspaceKey });
      assistant.textContent = finalText;
      recordConversationEntry(workspaceKey, "assistant", finalText);
      rememberWorkspaceOutput(workspaceKey, text, finalText, meta);
      if (workspaceKey === "home" && appState.telegram.enabled) {
        await sendTelegramBridge(`${lang() === "zh" ? "Hermes 回复" : "Hermes Reply"}:\n${finalText}`);
      }
    } catch (error) {
      assistant.textContent = `${lang() === "zh" ? "调用失败：" : "Request failed: "}${error.message || error}`;
      recordConversationEntry(workspaceKey, "assistant", assistant.textContent);
      rememberWorkspaceOutput(workspaceKey, text, "", meta);
    } finally {
      updateConversationArchive(messages);
      messages.scrollTop = messages.scrollHeight;
      send.disabled = false;
    }
  }

  appState.submitters[workspaceKey] = submit;
  const clearButton = document.querySelector(`[data-role='clear-conversation'][data-workspace='${workspaceKey}']`);
  if (clearButton && clearButton.dataset.bound !== "1") {
    clearButton.dataset.bound = "1";
    clearButton.addEventListener("click", () => {
      clearConversationHistory(workspaceKey, messages);
      if (workspaceKey === "home") {
        rememberWorkspaceOutput(workspaceKey, "", "", { name: lang() === "zh" ? "人机交流" : "Human Exchange" });
      }
    });
  }
  send.addEventListener("click", () => submit());
  input.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      submit();
    }
  });
}

function bindNav() {
  document.querySelectorAll(".tab-btn[data-page]").forEach((button) => {
    button.addEventListener("click", () => {
      const page = button.dataset.page;
      setActivePage(page, true);
    });
  });
  document.querySelectorAll(".jump[data-page]").forEach((button) => {
    button.addEventListener("click", () => {
      const page = button.dataset.page;
      setActivePage(page, true);
    });
  });
}

function topNavLabels() {
  if (lang() === "zh") {
    return {
      home: "总控",
      "work-chat": "协作会话",
      skills: "技能中心",
      finance: "财务平台",
      legal: "法务平台",
      "ai-agent": "AI Agent",
      "doc-flow": "文件流程",
      workbench: "项目",
      "my-work": "我的工作",
      reports: "报告中心",
      "file-center": "文件",
      "governance-center": "合规",
      "intel-center": "情报",
      "team-status": "团队态势",
      admin: "管理中心",
      settings: "设置",
    };
  }
  return {
    home: "Command",
    "work-chat": "Collaboration",
    skills: "Skills Hub",
    finance: "Finance",
    legal: "Legal",
    "ai-agent": "AI Agent",
    "doc-flow": "Document Flow",
    workbench: "Projects",
    "my-work": "My Work",
    reports: "Reports",
    "file-center": "Files",
    "governance-center": "Compliance",
    "intel-center": "Intelligence",
    "team-status": "Team Pulse",
    admin: "Admin",
    settings: "Settings",
  };
}

function topNavSkillShortcuts() {
  if (lang() === "zh") {
    return [
      { id: "uk_hk_financial_contract_counsel", label: "法律" },
      { id: "financial-analysis", label: "财务分析" },
      { id: "composio-workspace", label: "Composio" },
      { id: "pdf-excel-analysis", label: "PDF to Excel 分析" },
      { id: "due-diligence-web-research", label: "尽职调查" },
      { id: "financial-report-summary", label: "财报摘要" },
      { id: "client-follow-up-weekly-update", label: "客户跟进" },
      { id: "banking-sblc", label: "SBLC" },
    ];
  }
  return [
    { id: "uk_hk_financial_contract_counsel", label: "Legal" },
    { id: "financial-analysis", label: "Financial Analysis" },
    { id: "composio-workspace", label: "Composio" },
    { id: "pdf-excel-analysis", label: "PDF to Excel" },
    { id: "due-diligence-web-research", label: "Due Diligence" },
    { id: "financial-report-summary", label: "Earnings Summary" },
    { id: "client-follow-up-weekly-update", label: "Client Follow-up" },
    { id: "banking-sblc", label: "SBLC" },
  ];
}

function closeTopNavOverflowMenu() {
  const panel = document.getElementById("topNavOverflowMenu");
  if (panel) panel.remove();
  document.body.dataset.topNavOverflowOpen = "0";
}

function ensureTopNavOverflowGlobalClose() {
  if (document.body.dataset.topNavOverflowBound === "1") return;
  document.body.dataset.topNavOverflowBound = "1";
  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;
    if (target.closest("#topNavOverflowMenu")) return;
    if (target.closest("[data-nav-overflow]")) return;
    closeTopNavOverflowMenu();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeTopNavOverflowMenu();
  });
  window.addEventListener("resize", closeTopNavOverflowMenu);
}

function toggleTopNavOverflowMenu(anchor, labels) {
  const open = document.body.dataset.topNavOverflowOpen === "1";
  if (open) {
    closeTopNavOverflowMenu();
    return;
  }
  closeTopNavOverflowMenu();
  ensureTopNavOverflowGlobalClose();
  const panel = document.createElement("div");
  panel.id = "topNavOverflowMenu";
  panel.className = "top-nav-overflow-menu";
  const headingPage = document.createElement("div");
  headingPage.className = "top-nav-overflow-heading";
  headingPage.textContent = lang() === "zh" ? "页面入口" : "Pages";
  panel.appendChild(headingPage);
  ["doc-flow", "workbench", "my-work", "reports", "file-center", "governance-center", "intel-center"].forEach((page) => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "top-nav-overflow-item";
    if (appState.currentPage === page) item.classList.add("active");
    item.textContent = labels[page] || page;
    item.addEventListener("click", () => {
      closeTopNavOverflowMenu();
      setActivePage(page, true);
    });
    panel.appendChild(item);
  });
  const headingSkill = document.createElement("div");
  headingSkill.className = "top-nav-overflow-heading";
  headingSkill.textContent = lang() === "zh" ? "工作技能" : "Skills";
  panel.appendChild(headingSkill);
  topNavSkillShortcuts().forEach((skill) => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "top-nav-overflow-item";
    if (appState.currentSkillId === skill.id && (appState.currentPage === "finance" || appState.currentPage === "legal")) {
      item.classList.add("active");
    }
    item.textContent = skill.label;
    item.addEventListener("click", () => {
      closeTopNavOverflowMenu();
      navigateToWorkspaceSkill(skill.id, true);
    });
    panel.appendChild(item);
  });
  if (appState.auth.authenticated && appState.auth.user?.permissions?.view_team_status) {
    const headingAdmin = document.createElement("div");
    headingAdmin.className = "top-nav-overflow-heading";
    headingAdmin.textContent = lang() === "zh" ? "管理入口" : "Management";
    panel.appendChild(headingAdmin);
    const teamItem = document.createElement("button");
    teamItem.type = "button";
    teamItem.className = "top-nav-overflow-item";
    teamItem.textContent = labels["team-status"];
    teamItem.addEventListener("click", async () => {
      closeTopNavOverflowMenu();
      await openTeamStatusCenter();
    });
    panel.appendChild(teamItem);
    if (appState.auth.user?.role === "admin") {
      const adminItem = document.createElement("button");
      adminItem.type = "button";
      adminItem.className = "top-nav-overflow-item";
      adminItem.textContent = labels.admin;
      adminItem.addEventListener("click", async () => {
        closeTopNavOverflowMenu();
        await openAdminCenter();
      });
      panel.appendChild(adminItem);
    }
  }
  document.body.appendChild(panel);
  const rect = anchor.getBoundingClientRect();
  const menuWidth = 280;
  const left = Math.max(12, Math.min(window.innerWidth - menuWidth - 12, rect.right - menuWidth));
  const top = Math.max(12, Math.min(window.innerHeight - 160, rect.bottom + 8));
  panel.style.left = `${Math.round(left)}px`;
  panel.style.top = `${Math.round(top)}px`;
  const dynamicMaxHeight = Math.max(180, Math.min(560, window.innerHeight - top - 12));
  panel.style.maxHeight = `${Math.round(dynamicMaxHeight)}px`;
  document.body.dataset.topNavOverflowOpen = "1";
}

function bindTopNavActionTabs() {
  document.querySelectorAll(".tab-btn[data-page-action]").forEach((button) => {
    if (button.dataset.boundPageAction === "1") return;
    button.dataset.boundPageAction = "1";
    button.addEventListener("click", async () => {
      const action = button.dataset.pageAction;
      if (action === "team-status") {
        await openTeamStatusCenter();
      } else if (action === "admin") {
        await openAdminCenter();
      } else if (action === "account") {
        await openAccountCenter();
      }
    });
  });
}

function ensureTopNavLayout() {
  const tabs = document.querySelector(".page-tabs");
  if (!tabs) return;
  const labels = topNavLabels();
  const orderedPages = ["home", "ai-agent", "work-chat", "skills", "finance", "legal", "doc-flow", "workbench", "my-work", "reports", "file-center", "governance-center", "intel-center"];
  const primaryPages = ["home", "workbench", "file-center", "intel-center", "governance-center", "ai-agent"];
  const firstByPage = new Map();
  tabs.querySelectorAll(".tab-btn[data-page]").forEach((button) => {
    const page = String(button.dataset.page || "");
    if (!page) return;
    if (!firstByPage.has(page)) {
      firstByPage.set(page, button);
      return;
    }
    button.remove();
  });
  orderedPages.forEach((page) => {
    let button = firstByPage.get(page);
    if (!button) {
      button = document.createElement("button");
      button.className = "tab-btn";
      button.type = "button";
      button.dataset.page = page;
      tabs.appendChild(button);
      firstByPage.set(page, button);
    }
    button.textContent = labels[page] || page;
  });
  tabs.querySelectorAll(".tab-btn[data-page]").forEach((button) => {
    const page = String(button.dataset.page || "");
    if (!orderedPages.includes(page)) button.remove();
  });
  tabs.querySelectorAll(".tab-btn[data-page], .tab-btn[data-page-action], .tab-btn[data-skill-shortcut], .tab-btn[data-nav-overflow]").forEach((button) => button.remove());
  primaryPages.forEach((page) => {
    const button = firstByPage.get(page);
    if (button) tabs.appendChild(button);
  });
  const settingsButton = document.createElement("button");
  settingsButton.className = "tab-btn tab-btn-settings";
  settingsButton.type = "button";
  settingsButton.dataset.pageAction = "account";
  settingsButton.textContent = labels.settings || (lang() === "zh" ? "设置" : "Settings");
  tabs.appendChild(settingsButton);
  bindTopNavActionTabs();
}

function syncDockSkillChipState() {
  const chips = document.querySelectorAll(".dock .dock-chip[href]");
  chips.forEach((chip) => chip.classList.remove("is-active"));
  chips.forEach((chip) => {
    const href = String(chip.getAttribute("href") || "").trim();
    if (!href) return;
    if (href.includes("#intel-center") && appState.currentPage === "intel-center") {
      chip.classList.add("is-active");
      return;
    }
    if (href.includes("#governance-center") && appState.currentPage === "governance-center") {
      chip.classList.add("is-active");
      return;
    }
    if (href.includes("#ai-agent") && appState.currentPage === "ai-agent") {
      chip.classList.add("is-active");
      return;
    }
    if (href.includes("skill-uk-hk-financial-contract-counsel") && appState.currentPage === "legal") {
      chip.classList.add("is-active");
      return;
    }
    const url = new URL(href, location.href);
    const platform = url.searchParams.get("platform");
    if (platform && platform === appState.currentSkillId && (appState.currentPage === "finance" || appState.currentPage === "legal")) {
      chip.classList.add("is-active");
    }
  });
}

function bindInternalWorkspaceLinks() {
  if (document.body.dataset.internalLinkBound === "1") return;
  document.body.dataset.internalLinkBound = "1";
  document.addEventListener("click", (event) => {
    const link = event.target.closest("a[href]");
    if (!link) return;
    if (link.getAttribute("target") === "_blank") return;
    const href = String(link.getAttribute("href") || "").trim();
    if (!href || href.startsWith("http://") || href.startsWith("https://") || href.startsWith("mailto:") || href.startsWith("tel:")) return;
    const hashPage = (() => {
      try {
        return new URL(href, location.href).hash.replace("#", "");
      } catch {
        return "";
      }
    })();
    if (hashPage && PAGE_KEYS.has(hashPage)) {
      event.preventDefault();
      setActivePage(hashPage, true);
      return;
    }
    if (href.includes("skill-uk-hk-financial-contract-counsel")) {
      event.preventDefault();
      navigateToWorkspaceSkill("uk_hk_financial_contract_counsel", true);
      return;
    }
    if (!href.includes("platform=")) return;
    const isWorkspaceLink = href.startsWith("./console")
      || href.startsWith("./console-en")
      || href.startsWith("./skill-uk-hk-financial-contract-counsel")
      || href.startsWith("./index")
      || href.startsWith("console")
      || href.startsWith("skill-uk-hk-financial-contract-counsel")
      || href.startsWith("index");
    if (!isWorkspaceLink) return;
    const url = new URL(href, location.href);
    const skillId = url.searchParams.get("platform");
    if (!skillId || !PLATFORM_META[skillId]) return;
    event.preventDefault();
    navigateToWorkspaceSkill(skillId, true);
  });
}

function documentFlowCopy() {
  return lang() === "zh" ? {
    tab: "文件审阅审批",
    eyebrow: "Document Review Flow",
    title: "文件审阅与审批流程",
    subtitle: "在同一工作台完成审阅、审批、签字归档、版本追踪与授权协同。",
    progressTitle: "处理进度表",
    create: "发起流程",
    refresh: "刷新",
    listTitle: "流程列表",
    notifications: "通知",
    created: "我发起的",
    pending: "我待处理的",
    cc: "抄送给我",
    granted: "授权查看",
    all: "全部流程",
    emptyList: "当前暂无可见文件流程。",
    emptyDetail: "请选择文件流程，或先发起新的审阅审批流程。",
    adminBadge: "管理员 / 全局查看",
    status: "当前状态",
    workflow: "流程阶段",
    handler: "当前处理人",
    signed: "签字归档",
    unsigned: "未签字",
    encrypted: "加密归档",
    plain: "普通版本",
    currentVersion: "当前版本",
    versionHistory: "历史版本",
    steps: "流程时间线",
    ccRecipients: "抄送人",
    grants: "授权查看",
    note: "流程说明",
    deadline: "截止时间",
    changeReason: "修改说明",
    basedOn: "基于签字版本",
    actionComment: "意见 / 说明",
    download: "下载",
    downloadCurrent: "下载当前版本",
    openCreate: "发起文件流程",
    createTitle: "发起文件审阅审批",
    fileTitle: "文件标题",
    reviewer: "审阅人",
    approver: "审批人",
    ccUser: "抄送人",
    fileUpload: "上传文件",
    textContent: "或直接填写正文",
    flowNote: "流程说明",
    deadlineAt: "截止时间",
    basedDoc: "基于已签字文件（可选）",
    changeSummary: "修改说明 / 版本摘要",
    submitCreate: "提交流程",
    saveDraft: "保存草稿",
    noUsers: "当前没有可选用户。",
    noVersion: "暂无版本记录。",
    noSteps: "暂无流程步骤。",
    noNotifications: "当前没有新通知。",
    noCc: "未设置抄送人。",
    noGrants: "未设置额外授权。",
    grantUser: "授权用户",
    grantAdd: "授权",
    revoke: "撤销",
    createdBy: "发起人",
    updatedAt: "最近更新",
    actionButtons: {
      submit_revision: "提交修订版",
      review_pass: "审阅通过",
      return_for_revision: "退回修改",
      approve: "批准",
      reject: "驳回",
      request_changes: "要求修改",
      sign: "签字归档",
      submit_draft: "提交草稿",
      comment: "添加意见",
      mark_read: "标记已读",
    },
    revisionTitle: "提交修订版",
    revisionNote: "上传修订版后会生成新的版本号，并继续流转审批。",
    revisionFile: "修订文件",
    revisionSummary: "本次修订说明",
    revisionSubmit: "提交修订版",
    commentTitle: "填写意见",
    commentSubmit: "提交",
    grantTitle: "流程授权",
    viewerOnly: "被授权用户默认为只读查看。",
    restartSignedFlow: "从已签字版本发起变更",
    archiveBadge: "FASTONE Signed & Encrypted Archive",
    archiveNote: "已签字归档文件不能直接修改。请基于当前签字版本发起新的变更流程，并填写修改说明。",
    activeStep: "当前节点",
    activeReviewer: "审阅中",
    activeApproval: "待审批",
    activeSign: "待签字",
    activeRevision: "待修改",
    locked: "已锁定",
    unlocked: "可编辑",
    stepStatus: {
      pending: "待处理",
      in_progress: "进行中",
      completed: "已完成",
      returned: "已退回",
      rejected: "已驳回",
    },
  } : {
    tab: "Document Review Flow",
    eyebrow: "Document Review Flow",
    title: "Document Review & Approval",
    subtitle: "Run review, approval, signing, version tracking, and access control in one workspace.",
    progressTitle: "Processing Progress",
    create: "Start Flow",
    refresh: "Refresh",
    listTitle: "Workflow List",
    notifications: "Notifications",
    created: "Created by Me",
    pending: "Pending for Me",
    cc: "CC to Me",
    granted: "Granted View",
    all: "All Flows",
    emptyList: "No visible document workflows.",
    emptyDetail: "Select a workflow, or start a new one.",
    adminBadge: "Admin / Global View",
    status: "Current Status",
    workflow: "Workflow Stage",
    handler: "Current Handler",
    signed: "Signed",
    unsigned: "Unsigned",
    encrypted: "Encrypted Archive",
    plain: "Normal Version",
    currentVersion: "Current Version",
    versionHistory: "Version History",
    steps: "Workflow Timeline",
    ccRecipients: "CC Recipients",
    grants: "Access Grants",
    note: "Workflow Note",
    deadline: "Deadline",
    changeReason: "Change Reason",
    basedOn: "Based on Signed Version",
    actionComment: "Comment / Note",
    download: "Download",
    downloadCurrent: "Download Current Version",
    openCreate: "Start Document Workflow",
    createTitle: "Start a Document Review Flow",
    fileTitle: "Document Title",
    reviewer: "Reviewers",
    approver: "Approvers",
    ccUser: "CC Recipients",
    fileUpload: "Upload File",
    textContent: "Or paste document text",
    flowNote: "Workflow Note",
    deadlineAt: "Deadline",
    basedDoc: "Based on Signed Document (optional)",
    changeSummary: "Change Reason / Version Summary",
    submitCreate: "Submit Workflow",
    saveDraft: "Save Draft",
    noUsers: "No users are currently available.",
    noVersion: "No versions yet.",
    noSteps: "No workflow steps yet.",
    noNotifications: "No new notifications.",
    noCc: "No CC recipients.",
    noGrants: "No extra access grants.",
    grantUser: "Grant User",
    grantAdd: "Grant",
    revoke: "Revoke",
    createdBy: "Created By",
    updatedAt: "Updated",
    actionButtons: {
      submit_revision: "Submit Revision",
      review_pass: "Review Pass",
      return_for_revision: "Return for Revision",
      approve: "Approve",
      reject: "Reject",
      request_changes: "Request Changes",
      sign: "Sign & Archive",
      submit_draft: "Submit Draft",
      comment: "Add Comment",
      mark_read: "Mark Read",
    },
    revisionTitle: "Submit Revision",
    revisionNote: "Uploading a revision will create a new version and keep the workflow moving.",
    revisionFile: "Revision File",
    revisionSummary: "Revision Summary",
    revisionSubmit: "Submit Revision",
    commentTitle: "Add Comment",
    commentSubmit: "Submit",
    grantTitle: "Workflow Access",
    viewerOnly: "Granted users are read-only by default.",
    restartSignedFlow: "Start Change",
    archiveBadge: "FASTONE Signed & Encrypted Archive",
    archiveNote: "Signed archive files cannot be edited directly. Start a new change workflow from the signed version and include a change note.",
    activeStep: "Active Step",
    activeReviewer: "In Review",
    activeApproval: "Pending Approval",
    activeSign: "Pending Signature",
    activeRevision: "Revision Needed",
    locked: "Locked",
    unlocked: "Editable",
    stepStatus: {
      pending: "Pending",
      in_progress: "In Progress",
      completed: "Completed",
      returned: "Returned",
      rejected: "Rejected",
    },
  };
}

function documentStatusLabel(status) {
  const map = lang() === "zh" ? {
    draft: "草稿",
    in_review: "审阅中",
    returned_for_revision: "退回修改",
    pending_approval: "待审批",
    rejected: "已驳回",
    approved: "已批准",
    signed: "已签字",
    archived_locked: "已签字归档",
    superseded: "已被替代",
  } : {
    draft: "Draft",
    in_review: "In Review",
    returned_for_revision: "Returned for Revision",
    pending_approval: "Pending Approval",
    rejected: "Rejected",
    approved: "Approved",
    signed: "Signed",
    archived_locked: "Archived & Locked",
    superseded: "Superseded",
  };
  return map[status] || status || "--";
}

function unifiedStatusLabel(status) {
  const normalized = String(status || "").trim().toLowerCase().replace(/[\s-]+/g, "_");
  if (!normalized) return "--";
  const zh = {
    planning: "规划中",
    active: "进行中",
    on_hold: "暂停",
    blocked: "阻塞",
    completed: "已完成",
    archived: "归档",
    todo: "待办",
    in_progress: "进行中",
    in_review: "审阅中",
    pending_approval: "待审批",
    pending_signature: "待签字",
    done: "完成",
    cancelled: "已取消",
    generated: "已生成",
    draft: "草稿",
    approved: "已批准",
    rejected: "已拒绝",
    signed: "已签字",
    archived_locked: "已签字归档",
    returned_for_revision: "退回修改",
  };
  const en = {
    planning: "Planning",
    active: "Active",
    on_hold: "On Hold",
    blocked: "Blocked",
    completed: "Completed",
    archived: "Archived",
    todo: "To Do",
    in_progress: "In Progress",
    in_review: "In Review",
    pending_approval: "Pending Approval",
    pending_signature: "Pending Signature",
    done: "Done",
    cancelled: "Cancelled",
    generated: "Generated",
    draft: "Draft",
    approved: "Approved",
    rejected: "Rejected",
    signed: "Signed",
    archived_locked: "Archived & Locked",
    returned_for_revision: "Returned for Revision",
  };
  const table = lang() === "zh" ? zh : en;
  if (table[normalized]) return table[normalized];
  const spaced = normalized.replace(/_/g, " ");
  return lang() === "zh" ? spaced : spaced.replace(/\b\w/g, (char) => char.toUpperCase());
}

function documentStepLabel(stepType) {
  const map = lang() === "zh" ? {
    review: "审阅",
    approval: "审批",
    sign: "签字",
    revision: "修改",
    archived_locked: "归档",
  } : {
    review: "Review",
    approval: "Approval",
    sign: "Sign",
    revision: "Revision",
    archived_locked: "Archive",
  };
  return map[stepType] || stepType || "--";
}

function documentActionTakenLabel(action) {
  if (!action) return "--";
  const copy = documentFlowCopy();
  const map = {
    submit_revision: copy.actionButtons.submit_revision,
    review_pass: copy.actionButtons.review_pass,
    return_for_revision: copy.actionButtons.return_for_revision,
    approve: copy.actionButtons.approve,
    reject: copy.actionButtons.reject,
    request_changes: copy.actionButtons.request_changes,
    sign: copy.actionButtons.sign,
    submit_draft: copy.actionButtons.submit_draft,
    comment: copy.actionButtons.comment,
    mark_read: copy.actionButtons.mark_read,
  };
  return map[action] || action;
}

function documentFlowDisplayText(value) {
  const text = String(value || "").trim();
  if (!text || lang() === "zh") return text;
  const rules = [
    [/^(.+?) 发起了文件流程《(.+?)》。?$/, "$1 started document workflow \"$2\"."],
    [/^(.+?) 保存了文件流程《(.+?)》。?$/, "$1 saved document workflow \"$2\"."],
    [/^(.+?) 提交了草稿《(.+?)》进入审批流程。?$/, "$1 submitted draft \"$2\" into the approval workflow."],
    [/^(.+?) 提交了《(.+?)》的修订版本。?$/, "$1 submitted a revision for \"$2\"."],
    [/^(.+?) 已完成《(.+?)》审阅。?$/, "$1 completed review for \"$2\"."],
    [/^(.+?) 将《(.+?)》退回修改。?$/, "$1 returned \"$2\" for revision."],
    [/^(.+?) 已批准《(.+?)》。?$/, "$1 approved \"$2\"."],
    [/^(.+?) 已驳回《(.+?)》。?$/, "$1 rejected \"$2\"."],
    [/^(.+?) 要求对《(.+?)》继续修改。?$/, "$1 requested changes for \"$2\"."],
    [/^(.+?) 已完成《(.+?)》签字归档。?$/, "$1 signed and archived \"$2\"."],
    [/^(.+?) 在《(.+?)》中添加了意见。?$/, "$1 added a comment to \"$2\"."],
    [/^你已被授权查看《(.+?)》审批流程。?$/, "You have been granted view access to the approval workflow for \"$1\"."],
  ];
  for (const [pattern, replacement] of rules) {
    if (pattern.test(text)) return text.replace(pattern, replacement);
  }
  return text
    .replaceAll("发起了文件流程", "started document workflow")
    .replaceAll("保存了文件流程", "saved document workflow")
    .replaceAll("提交了草稿", "submitted draft")
    .replaceAll("进入审批流程", "into the approval workflow")
    .replaceAll("提交了", "submitted")
    .replaceAll("的修订版本", "revision")
    .replaceAll("已完成", "completed")
    .replaceAll("审阅", "review")
    .replaceAll("签字归档", "signing and archiving")
    .replaceAll("已批准", "approved")
    .replaceAll("已驳回", "rejected")
    .replaceAll("退回修改", "returned for revision")
    .replaceAll("要求对", "requested changes for")
    .replaceAll("继续修改", "further revision")
    .replaceAll("添加了意见", "added a comment")
    .replaceAll("《", "\"")
    .replaceAll("》", "\"")
    .replaceAll("。", ".");
}

function documentPreviewText(version) {
  if (!version) return "";
  return String(version.preview || "").trim();
}

function documentFlowUserOptions(selected = []) {
  const picked = new Set((selected || []).map((item) => String(item).toLowerCase()));
  return (appState.documentFlows.users || []).map((user) => {
    const email = user.email || "";
    const label = `${user.display_name || user.username || email} (${email})`;
    return `<option value="${escapeHtml(email)}" ${picked.has(email.toLowerCase()) ? "selected" : ""}>${escapeHtml(label)}</option>`;
  }).join("");
}

function ensureDocumentFlowShell() {
  const tabs = document.querySelector(".page-tabs");
  if (tabs && !tabs.querySelector("[data-page='doc-flow']")) {
    const button = document.createElement("button");
    button.className = "tab-btn";
    button.type = "button";
    button.dataset.page = "doc-flow";
    button.textContent = topNavLabels()["doc-flow"];
    tabs.appendChild(button);
    button.addEventListener("click", () => setActivePage("doc-flow", true));
  }
  const copy = documentFlowCopy();
  const main = document.querySelector("main.container");
  if (!main || document.getElementById("doc-flow")) return;
  const section = document.createElement("section");
  section.id = "doc-flow";
  section.className = "page";
  section.innerHTML = `
    <section class="doc-flow-page card">
      <aside class="doc-flow-sidebar">
        <div class="work-chat-head">
          <div>
            <div class="eyebrow">${copy.eyebrow}</div>
            <h1>${copy.title}</h1>
          </div>
          <span class="tag" data-doc-flow-admin-badge hidden>${copy.adminBadge}</span>
        </div>
        <div class="auth-note">${copy.subtitle}</div>
        <div class="work-chat-actions">
          <button class="btn btn-primary" type="button" data-doc-flow-create>${copy.create}</button>
          <button class="btn btn-ghost" type="button" data-doc-flow-refresh>${copy.refresh}</button>
        </div>
        <section class="io-progress-panel doc-flow-progress-panel">
          <div class="side-title">${copy.progressTitle}</div>
          <div class="io-progress__table-wrap">
            <table class="io-progress__table">
              <thead>
                <tr>
                  <th>${lang() === "zh" ? "文件 / 任务" : "File / Task"}</th>
                  <th>${lang() === "zh" ? "状态" : "Status"}</th>
                  <th>${lang() === "zh" ? "进度" : "Progress"}</th>
                  <th>${lang() === "zh" ? "类型" : "Type"}</th>
                </tr>
              </thead>
              <tbody data-role="io-progress-body"></tbody>
            </table>
          </div>
        </section>
        <div class="doc-flow-buckets" data-doc-flow-buckets></div>
        <div class="doc-flow-notifications card-soft" data-doc-flow-notifications></div>
      </aside>
      <section class="doc-flow-main">
        <div class="doc-flow-detail" data-doc-flow-detail>
          <div class="auth-note">${copy.emptyDetail}</div>
        </div>
      </section>
    </section>
  `;
  main.appendChild(section);
  renderIoProgress("doc-flow");
}

async function loadDocumentFlowUsers() {
  const resp = await fetch("/api/document-flows/users");
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
  appState.documentFlows.users = payload.users || [];
  return appState.documentFlows.users;
}

function renderDocumentFlowBuckets() {
  const copy = documentFlowCopy();
  const host = document.querySelector("[data-doc-flow-buckets]");
  if (!host) return;
  const buckets = appState.documentFlows.buckets || {};
  const defs = [
    ["pending", copy.pending],
    ["created", copy.created],
    ["cc", copy.cc],
    ["granted", copy.granted],
    ["all", copy.all],
  ];
  const html = defs.map(([key, label]) => {
    const items = Array.isArray(buckets[key]) ? buckets[key] : [];
    const list = items.length ? items.map((item) => `
      <button class="work-chat-item ${item.id === appState.documentFlows.selectedId ? "active" : ""}" type="button" data-doc-id="${escapeHtml(item.id)}">
        <strong>${escapeHtml(item.title || item.id)}</strong>
        <span>${escapeHtml(documentStatusLabel(item.current_status))} · ${escapeHtml(documentStepLabel(item.current_step || item.status_summary?.current_step || ""))}</span>
        <small>${escapeHtml(formatDateTime(item.updated_at))}</small>
      </button>
    `).join("") : `<div class="auth-note doc-flow-empty-inline">${copy.emptyList}</div>`;
    return `
      <section class="doc-flow-bucket">
        <div class="side-title">${escapeHtml(label)} <span class="doc-flow-count">${items.length}</span></div>
        <div class="work-chat-list">${list}</div>
      </section>
    `;
  }).join("");
  host.innerHTML = html;
  host.querySelectorAll("[data-doc-id]").forEach((button) => {
    button.addEventListener("click", () => selectDocumentFlow(button.dataset.docId || ""));
  });
}

function renderDocumentFlowNotifications() {
  const copy = documentFlowCopy();
  const host = document.querySelector("[data-doc-flow-notifications]");
  if (!host) return;
  const items = appState.documentFlows.notifications || [];
  host.innerHTML = `
    <div class="side-title">${copy.notifications}</div>
    <div class="doc-flow-notification-list">
      ${items.length ? items.map((item) => `
        <button class="doc-flow-notification ${item.is_read ? "" : "is-unread"}" type="button" data-doc-notification="${escapeHtml(item.id)}" data-doc-link="${escapeHtml(item.document_id || "")}">
          <strong>${escapeHtml(documentFlowDisplayText(item.content || "--"))}</strong>
          <span>${escapeHtml(formatDateTime(item.created_at))}</span>
        </button>
      `).join("") : `<div class="auth-note">${copy.noNotifications}</div>`}
    </div>
  `;
  host.querySelectorAll("[data-doc-notification]").forEach((button) => {
    button.addEventListener("click", async () => {
      const notificationId = button.dataset.docNotification || "";
      const documentId = button.dataset.docLink || "";
      try {
        await fetch("/api/document-flows/notifications/read", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ notification_id: notificationId }),
        });
      } catch {}
      if (documentId) {
        appState.documentFlows.selectedId = documentId;
        await loadDocumentFlows();
      } else {
        await loadDocumentFlows();
      }
    });
  });
}

async function loadDocumentFlows() {
  ensureDocumentFlowShell();
  if (!(appState.documentFlows.users || []).length) {
    await loadDocumentFlowUsers();
  }
  const resp = await fetch("/api/document-flows");
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
  appState.documentFlows.buckets = payload.buckets || { created: [], pending: [], cc: [], granted: [], all: [] };
  appState.documentFlows.notifications = payload.notifications || [];
  const badge = document.querySelector("[data-doc-flow-admin-badge]");
  if (badge) badge.hidden = !payload.admin_view;
  if (!appState.documentFlows.selectedId && appState.documentFlows.buckets.all?.[0]) {
    appState.documentFlows.selectedId = appState.documentFlows.buckets.all[0].id;
  }
  renderDocumentFlowBuckets();
  renderDocumentFlowNotifications();
  bindDocumentFlowControls();
  if (appState.documentFlows.selectedId) {
    await selectDocumentFlow(appState.documentFlows.selectedId);
  }
}

function rememberDocumentFlowOutput(detail) {
  if (!detail?.document) return;
  const doc = detail.document;
  const version = detail.current_version || {};
  const steps = Array.isArray(detail.steps) ? detail.steps : [];
  const cc = Array.isArray(detail.cc_recipients) ? detail.cc_recipients : [];
  const summary = [
    `Title: ${doc.title || doc.id}`,
    `Status: ${documentStatusLabel(doc.current_status)}`,
    `Current Step: ${documentStepLabel(doc.current_step || detail.workflow?.current_step || "")}`,
    `Created By: ${doc.created_by_name || doc.created_by || "--"}`,
    `Current Handler: ${doc.current_handler_name || doc.current_handler_id || "--"}`,
    version.filename ? `Current Version: v${version.version_number || 1} · ${version.filename}` : "",
    doc.flow_note ? `Workflow Note: ${doc.flow_note}` : "",
    doc.change_request_reason ? `Change Reason: ${doc.change_request_reason}` : "",
    cc.length ? `CC: ${cc.map((item) => item.display_name || item.user_id).join(", ")}` : "",
    "",
    "Preview:",
    version.preview || "",
    "",
    "Timeline:",
    steps.map((step) => `- ${documentStepLabel(step.step_type)} / ${step.assigned_name || step.assigned_user_id || "--"} / ${documentFlowCopy().stepStatus[step.status] || step.status}${step.comments ? ` / ${step.comments}` : ""}`).join("\n"),
  ].filter(Boolean).join("\n");
  appState.outputs["doc-flow"] = {
    workspace: "doc-flow",
    skillId: "document-review",
    title: `${doc.title || doc.id} ${lang() === "zh" ? "流程摘要" : "Workflow Summary"}`,
    prompt: doc.flow_note || "",
    result: summary.trim(),
    attachments: [],
    updatedAt: new Date().toISOString(),
    lastExport: appState.outputs["doc-flow"]?.lastExport || null,
  };
}

function renderDocumentFlowOutputCenter(detail) {
  const copy = documentFlowCopy();
  const exportState = appState.outputs["doc-flow"] || {};
  const meta = currentLocaleMeta("document-review");
  const docId = detail?.document?.id || "";
  const versionId = detail?.current_version?.id || "";
  const lastExport = exportState.lastExport || null;
  return `
    <section class="doc-flow-card">
      <div class="side-title">${lang() === "zh" ? "输出中心" : "Output Center"}</div>
      <div class="output-center doc-flow-output-center">
        <div class="output-center__head">
          <div>
            <div class="workspace-action-title">${lang() === "zh" ? "审批输出口" : "Approval Output"}</div>
            <div class="output-center__hint">${lang() === "zh" ? "签字归档文件可直接下载；流程摘要也可导出到统一输出目录。" : "Signed files can be downloaded directly, and the workflow summary can also be exported into the shared export directory."}</div>
          </div>
          <div class="output-center__controls">
            <select class="output-center__select" data-role="doc-export-format">
              <option value="md">Markdown (.md)</option>
              <option value="txt">Text (.txt)</option>
              <option value="json">JSON (.json)</option>
              <option value="docx">Word (.docx)</option>
              <option value="xlsx">Excel (.xlsx)</option>
              <option value="pptx">PowerPoint (.pptx)</option>
            </select>
            <button class="btn btn-primary" type="button" data-role="doc-export-run">${lang() === "zh" ? "导出流程摘要" : "Export Summary"}</button>
          </div>
        </div>
        <div class="output-center__meta">
          <div class="output-meta-card">
            <span>${lang() === "zh" ? "输出位置" : "Storage"}</span>
            <strong data-role="doc-export-storage">${escapeHtml(lastExport?.storage_dir || "/Users/billtin/Documents/Export Documents/document-review")}</strong>
          </div>
          <div class="output-meta-card">
            <span>${lang() === "zh" ? "进度" : "Progress"}</span>
            <strong data-role="doc-export-progress">${escapeHtml(lastExport?.progressLabel || (lang() === "zh" ? "等待导出" : "Waiting"))}</strong>
          </div>
          <div class="output-meta-card">
            <span>${lang() === "zh" ? "最新文件" : "Latest File"}</span>
            <strong data-role="doc-export-latest">${escapeHtml(lastExport?.filename || (lang() === "zh" ? "尚未生成" : "Not generated yet"))}</strong>
          </div>
        </div>
        <div class="output-center__actions" data-role="doc-export-actions">
          ${lastExport?.download_url ? `<button class="btn btn-ghost" type="button" data-role="doc-export-download">${lang() === "zh" ? "下载导出文件" : "Download Export"}</button>` : `<span class="output-center__empty">${lang() === "zh" ? `${meta.name} 的流程摘要会在这里导出。` : `The ${meta.name} workflow summary will export here.`}</span>`}
          ${docId && versionId ? `<button class="btn btn-ghost" type="button" data-role="doc-version-download">${copy.downloadCurrent}</button>` : ""}
        </div>
      </div>
    </section>
  `;
}

function bindDocumentFlowOutputCenter(detail) {
  const root = document.querySelector("[data-doc-flow-detail]");
  if (!root) return;
  const formatSelect = root.querySelector("[data-role='doc-export-format']");
  const runButton = root.querySelector("[data-role='doc-export-run']");
  const downloadExportButton = root.querySelector("[data-role='doc-export-download']");
  const downloadVersionButton = root.querySelector("[data-role='doc-version-download']");
  const progressNode = root.querySelector("[data-role='doc-export-progress']");
  const latestNode = root.querySelector("[data-role='doc-export-latest']");
  const storageNode = root.querySelector("[data-role='doc-export-storage']");
  const actionsNode = root.querySelector("[data-role='doc-export-actions']");
  if (formatSelect && !formatSelect.dataset.seeded) {
    formatSelect.value = preferredExportFormat("doc-flow");
    formatSelect.dataset.seeded = "1";
  }
  runButton?.addEventListener("click", async () => {
    const snapshot = appState.outputs["doc-flow"];
    if (!snapshot?.result?.trim()) {
      if (progressNode) progressNode.textContent = lang() === "zh" ? "当前没有可导出的流程摘要。" : "There is no workflow summary to export yet.";
      return;
    }
    const exportProgressId = `doc-flow-export-${Date.now()}`;
    const selectedFormat = formatSelect?.value || preferredExportFormat("doc-flow");
    if (progressNode) progressNode.textContent = lang() === "zh" ? "正在生成文件..." : "Generating file...";
    upsertIoProgress("doc-flow", {
      id: exportProgressId,
      file: snapshot.title || "Document Flow Output",
      type: lang() === "zh" ? "导出" : "Export",
      status: lang() === "zh" ? "生成中" : "Generating",
      progress: 55,
    });
    try {
      const resp = await fetch("/api/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          workspace: "document-review",
          format: selectedFormat,
          title: snapshot.title || "Document Flow Output",
          skill_id: snapshot.skillId || "document-review",
          prompt: snapshot.prompt || "",
          assistant_text: snapshot.result || "",
          attachments: [],
        }),
      });
      const data = await resp.json();
      if (!resp.ok || !data.ok) throw new Error(data.error || "request_failed");
      appState.outputs["doc-flow"] = {
        ...snapshot,
        lastExport: { ...data, progressLabel: lang() === "zh" ? "已完成" : "Ready" },
      };
      if (storageNode) storageNode.textContent = data.storage_dir || storageNode.textContent;
      if (progressNode) progressNode.textContent = lang() === "zh" ? "已完成" : "Ready";
      if (latestNode) latestNode.textContent = data.filename || latestNode.textContent;
      upsertIoProgress("doc-flow", {
        id: exportProgressId,
        file: data.filename || snapshot.title || "Document Flow Output",
        type: lang() === "zh" ? "导出" : "Export",
        status: lang() === "zh" ? "已完成" : "Completed",
        progress: 100,
      });
      if (actionsNode) {
        actionsNode.innerHTML = `
          <button class="btn btn-ghost" type="button" data-role="doc-export-download">${lang() === "zh" ? "下载导出文件" : "Download Export"}</button>
          ${detail?.document?.id && detail?.current_version?.id ? `<button class="btn btn-ghost" type="button" data-role="doc-version-download">${documentFlowCopy().downloadCurrent}</button>` : ""}
        `;
      }
      bindDocumentFlowOutputCenter(detail);
    } catch (error) {
      if (progressNode) progressNode.textContent = authErrorMessage(error.message);
      upsertIoProgress("doc-flow", {
        id: exportProgressId,
        file: snapshot.title || "Document Flow Output",
        type: lang() === "zh" ? "导出" : "Export",
        status: lang() === "zh" ? "失败" : "Failed",
        progress: 100,
      });
    }
  });
  downloadExportButton?.addEventListener("click", async () => {
    const url = appState.outputs["doc-flow"]?.lastExport?.download_url;
    const filename = appState.outputs["doc-flow"]?.lastExport?.filename || "document-flow-output";
    if (!url) return;
    const downloadId = `doc-flow-download-${Date.now()}`;
    upsertIoProgress("doc-flow", {
      id: downloadId,
      file: filename,
      type: lang() === "zh" ? "下载" : "Download",
      status: lang() === "zh" ? "准备中" : "Preparing",
      progress: 10,
    });
    const resp = await fetch(url);
    const blob = await resp.blob();
    const href = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = href;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(href);
    upsertIoProgress("doc-flow", {
      id: downloadId,
      file: filename,
      type: lang() === "zh" ? "下载" : "Download",
      status: lang() === "zh" ? "已完成" : "Completed",
      progress: 100,
    });
  });
  downloadVersionButton?.addEventListener("click", () => {
    if (detail?.document?.id && detail?.current_version?.id) {
      downloadDocumentFlowVersion(detail.document.id, detail.current_version.id).catch(() => {});
    }
  });
}

function documentActionButtons(detail) {
  const copy = documentFlowCopy();
  const viewer = detail.viewer || {};
  const currentStep = detail.status_summary?.current_step || detail.document?.current_step || "";
  const status = detail.document?.current_status || "";
  const actions = [];
  if (status === "draft" && viewer.is_creator) {
    actions.push("submit_draft", "comment");
  }
  if (viewer.can_act) {
    if (currentStep === "review") {
      actions.push("submit_revision", "review_pass", "return_for_revision", "comment");
    } else if (currentStep === "approval") {
      actions.push("approve", "reject", "request_changes", "comment");
    } else if (currentStep === "sign") {
      actions.push("sign", "comment");
    }
  }
  if (!viewer.can_act && !viewer.is_creator) {
    actions.push("mark_read");
  }
  if (viewer.is_creator && status === "returned_for_revision") {
    actions.push("submit_revision", "comment");
  }
  return [...new Set(actions)].map((action) => `
    <button class="btn ${action === "sign" || action === "approve" || action === "submit_revision" ? "btn-primary" : "btn-ghost"}" type="button" data-doc-action="${escapeHtml(action)}">${escapeHtml(copy.actionButtons[action] || action)}</button>
  `).join("");
}

function renderDocumentFlowDetail(detail) {
  const copy = documentFlowCopy();
  const host = document.querySelector("[data-doc-flow-detail]");
  if (!host) return;
  if (!detail || !detail.document) {
    host.innerHTML = `<div class="auth-note">${copy.emptyDetail}</div>`;
    return;
  }
  appState.documentFlows.detail = detail;
  rememberDocumentFlowOutput(detail);
  const doc = detail.document;
  const currentVersion = detail.current_version;
  const workflow = detail.workflow || {};
  const steps = detail.steps || [];
  const cc = detail.cc_recipients || [];
  const grants = detail.access_grants || [];
  const preview = documentPreviewText(currentVersion);
  host.innerHTML = `
    <div class="doc-flow-header">
      <div class="doc-flow-header-main">
        <div class="doc-flow-brand-chip">
          <img src="${themedFastoneLogo("full")}" alt="FASTONE" class="doc-flow-logo" />
        </div>
        <div>
        <div class="platform-kicker">${copy.eyebrow}</div>
        <h2 class="platform-title">${escapeHtml(doc.title || doc.id)}</h2>
        <p class="platform-desc">${escapeHtml(doc.flow_note || copy.subtitle)}</p>
          ${doc.is_signed || doc.is_locked ? `<div class="doc-flow-archive-badge">${copy.archiveBadge}</div>` : ""}
        </div>
      </div>
      <div class="mini-status">
        <span class="mini-pill">${escapeHtml(documentStatusLabel(doc.current_status))}</span>
        <span class="mini-pill">${escapeHtml(documentStepLabel(detail.status_summary?.current_step || doc.current_step || ""))}</span>
        <span class="mini-pill">${doc.is_locked ? copy.locked : copy.unlocked}</span>
      </div>
    </div>
    <div class="doc-flow-runtime-strip">
      <div class="doc-flow-runtime-card">
        <span>${lang() === "zh" ? "流程链路" : "Workflow Chain"}</span>
        <strong>${escapeHtml(`${steps.filter((step) => step.step_type === "review").length} ${lang() === "zh" ? "审阅" : "review"} · ${steps.filter((step) => step.step_type === "approval").length} ${lang() === "zh" ? "审批" : "approval"} · ${steps.filter((step) => step.step_type === "sign").length} ${lang() === "zh" ? "签字" : "sign"}`)}</strong>
      </div>
      <div class="doc-flow-runtime-card">
        <span>${lang() === "zh" ? "版本链" : "Version Chain"}</span>
        <strong>${escapeHtml(`${(detail.versions || []).length || 0} ${lang() === "zh" ? "个版本" : "versions"}${doc.based_on_document_id ? ` · ${lang() === "zh" ? "基于已签字版本" : "based on signed version"}` : ""}`)}</strong>
      </div>
      <div class="doc-flow-runtime-card">
        <span>${lang() === "zh" ? "可见范围" : "Visibility"}</span>
        <strong>${escapeHtml(`${cc.length} ${lang() === "zh" ? "位抄送" : "CC"} · ${grants.length} ${lang() === "zh" ? "位授权查看" : "grants"}`)}</strong>
      </div>
      <div class="doc-flow-runtime-card">
        <span>${lang() === "zh" ? "归档状态" : "Archive State"}</span>
        <strong>${escapeHtml(doc.is_signed || doc.is_locked ? (lang() === "zh" ? "已签字并锁定" : "Signed and locked") : (lang() === "zh" ? "可继续流转" : "Active workflow"))}</strong>
      </div>
    </div>
    <div class="workspace-info-row doc-flow-summary-row">
      <div class="status-mini-card"><span>${copy.createdBy}</span><strong>${escapeHtml(doc.created_by_name || doc.created_by || "--")}</strong></div>
      <div class="status-mini-card"><span>${copy.handler}</span><strong>${escapeHtml(doc.current_handler_name || doc.current_handler_id || "--")}</strong></div>
      <div class="status-mini-card"><span>${copy.updatedAt}</span><strong>${escapeHtml(formatDateTime(doc.updated_at))}</strong></div>
      <div class="status-mini-card"><span>${copy.currentVersion}</span><strong>${escapeHtml(currentVersion ? `v${currentVersion.version_number}` : "--")}</strong></div>
    </div>
    <div class="doc-flow-grid">
      <section class="doc-flow-card">
        <div class="side-title">${copy.currentVersion}</div>
        <div class="doc-flow-card-grid">
          <div><span>${copy.status}</span><strong>${escapeHtml(documentStatusLabel(doc.current_status))}</strong></div>
          <div><span>${copy.workflow}</span><strong>${escapeHtml(documentStepLabel(workflow.current_step || doc.current_step || ""))}</strong></div>
          <div><span>${copy.signed}</span><strong>${doc.is_signed ? copy.signed : copy.unsigned}</strong></div>
          <div><span>${copy.encrypted}</span><strong>${doc.is_encrypted ? copy.encrypted : copy.plain}</strong></div>
          <div><span>${copy.deadline}</span><strong>${escapeHtml(doc.deadline_at ? formatDateTime(doc.deadline_at) : "--")}</strong></div>
          <div><span>${copy.basedOn}</span><strong>${escapeHtml(doc.based_on_document_id || "--")}</strong></div>
        </div>
        ${doc.change_request_reason ? `<div class="doc-note"><strong>${copy.changeReason}</strong><br>${escapeHtml(doc.change_request_reason)}</div>` : ""}
        ${doc.is_signed || doc.is_locked ? `<div class="doc-note doc-note--archive">${copy.archiveNote}</div>` : ""}
        ${doc.is_signed || doc.is_locked ? `
          <div class="doc-flow-change-cta">
            <div>
              <span>${lang() === "zh" ? "重新发起变更" : "Restart as change workflow"}</span>
              <strong>${lang() === "zh" ? "保留旧签字版本，只新建变更链路" : "Keep the signed archive intact and open a new change flow"}</strong>
            </div>
            <button class="btn btn-primary" type="button" data-doc-start-change="1">${copy.restartSignedFlow}</button>
          </div>
        ` : ""}
        ${preview ? `<div class="doc-flow-preview">${escapeHtml(preview)}</div>` : `<div class="auth-note">${copy.noVersion}</div>`}
        <div class="doc-flow-actions">
          <button class="btn btn-ghost" type="button" data-doc-download="${escapeHtml(currentVersion?.id || "")}">${copy.downloadCurrent}</button>
          ${documentActionButtons(detail)}
        </div>
      </section>
      <section class="doc-flow-card">
        <div class="side-title">${copy.steps}</div>
        <div class="doc-flow-step-list">
          ${steps.length ? steps.map((step) => `
            <div class="doc-flow-step is-${escapeHtml(step.status)}">
              <strong>${escapeHtml(documentStepLabel(step.step_type))} · ${escapeHtml(step.assigned_name || step.assigned_user_id || "--")}</strong>
              <span>${escapeHtml(copy.stepStatus[step.status] || step.status)} · ${escapeHtml(documentActionTakenLabel(step.action_taken))}</span>
              <small>${escapeHtml(step.acted_at ? formatDateTime(step.acted_at) : "--")}</small>
              ${step.comments ? `<p>${escapeHtml(step.comments)}</p>` : ""}
            </div>
          `).join("") : `<div class="auth-note">${copy.noSteps}</div>`}
        </div>
      </section>
    </div>
    <div class="doc-flow-grid">
      <section class="doc-flow-card">
        <div class="side-title">${copy.versionHistory}</div>
        <div class="doc-flow-version-list">
          ${(detail.versions || []).length ? detail.versions.map((version) => `
            <div class="doc-flow-version">
              <div>
                <strong>v${escapeHtml(version.version_number)} · ${escapeHtml(version.filename || version.download_name || "--")}</strong>
                <span>${escapeHtml(version.created_by_name || version.created_by || "--")} · ${escapeHtml(formatDateTime(version.created_at))}</span>
                <small>${escapeHtml(version.change_summary || "--")}</small>
              </div>
              <button class="btn btn-ghost" type="button" data-doc-download="${escapeHtml(version.id)}">${copy.download}</button>
            </div>
          `).join("") : `<div class="auth-note">${copy.noVersion}</div>`}
        </div>
      </section>
      <section class="doc-flow-card">
        <div class="side-title">${copy.ccRecipients}</div>
        <div class="tag-row">${cc.length ? cc.map((item) => `<span class="tag">${escapeHtml(item.display_name || item.user_id || "--")}</span>`).join("") : `<span class="tag">${copy.noCc}</span>`}</div>
        <div class="side-title">${copy.grants}</div>
        <div class="tag-row">
          ${grants.length ? grants.map((item) => `<span class="tag">${escapeHtml(item.display_name || item.granted_user_id || "--")}<button type="button" data-doc-grant-revoke="${escapeHtml(item.granted_user_id || "")}">×</button></span>`).join("") : `<span class="tag">${copy.noGrants}</span>`}
        </div>
        ${(detail.viewer?.is_admin || detail.viewer?.can_view_all) ? `
          <div class="work-chat-admin-grants">
            <strong>${copy.grantTitle}</strong>
            <div class="work-chat-grant-row">
              <select data-doc-grant-user>${documentFlowUserOptions()}</select>
              <button class="btn btn-ghost" type="button" data-doc-grant-add>${copy.grantAdd}</button>
            </div>
            <div class="auth-note">${copy.viewerOnly}</div>
          </div>
        ` : ""}
      </section>
    </div>
    ${renderDocumentFlowOutputCenter(detail)}
  `;
  host.querySelectorAll("[data-doc-download]").forEach((button) => {
    button.addEventListener("click", () => downloadDocumentFlowVersion(doc.id, button.dataset.docDownload || ""));
  });
  host.querySelectorAll("[data-doc-action]").forEach((button) => {
    button.addEventListener("click", () => handleDocumentFlowAction(doc.id, button.dataset.docAction || ""));
  });
  host.querySelector("[data-doc-start-change]")?.addEventListener("click", () => {
    openDocumentFlowCreate({
      basedOnDocumentId: doc.id,
      title: `${doc.title || doc.id}${lang() === "zh" ? " - 变更流程" : " - Change Workflow"}`,
      flowNote: doc.flow_note || "",
      changeSummary: "",
      reviewers: (detail?.steps || []).filter((step) => step.step_type === "review").map((step) => step.assigned_user_id).filter(Boolean),
      approvers: (detail?.steps || []).filter((step) => step.step_type === "approval").map((step) => step.assigned_user_id).filter(Boolean),
      ccRecipients: (detail?.cc_recipients || []).map((item) => item.user_id).filter(Boolean),
      requireChangeReason: true,
    }).catch((error) => {
      ensureOverlayPanel(copy.createTitle, `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`);
    });
  });
  host.querySelector("[data-doc-grant-add]")?.addEventListener("click", async () => {
    const email = host.querySelector("[data-doc-grant-user]")?.value || "";
    await updateDocumentFlowGrant(doc.id, email, true);
  });
  host.querySelectorAll("[data-doc-grant-revoke]").forEach((button) => {
    button.addEventListener("click", async () => updateDocumentFlowGrant(doc.id, button.dataset.docGrantRevoke || "", false));
  });
  bindDocumentFlowOutputCenter(detail);
}

async function selectDocumentFlow(documentId) {
  if (!documentId) return;
  appState.documentFlows.selectedId = documentId;
  renderDocumentFlowBuckets();
  const resp = await fetch(`/api/document-flows/documents/${encodeURIComponent(documentId)}`);
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
  renderDocumentFlowDetail(payload);
}

async function updateDocumentFlowGrant(documentId, email, active) {
  if (!documentId || !email) return;
  const resp = await fetch(`/api/document-flows/documents/${encodeURIComponent(documentId)}/grant`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ granted_user_id: email, active }),
  });
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
  renderDocumentFlowDetail(payload);
  await loadDocumentFlows();
}

async function downloadDocumentFlowVersion(documentId, versionId) {
  const url = `/api/document-flows/documents/${encodeURIComponent(documentId)}/download?version_id=${encodeURIComponent(versionId || "")}`;
  const downloadId = `doc-flow-version-${Date.now()}`;
  upsertIoProgress("doc-flow", {
    id: downloadId,
    file: versionId || documentId,
    type: lang() === "zh" ? "版本下载" : "Version Download",
    status: lang() === "zh" ? "准备中" : "Preparing",
    progress: 15,
  });
  const resp = await fetch(url);
  if (!resp.ok) {
    let payload = {};
    try {
      payload = await resp.json();
    } catch {}
    upsertIoProgress("doc-flow", {
      id: downloadId,
      file: versionId || documentId,
      type: lang() === "zh" ? "版本下载" : "Version Download",
      status: lang() === "zh" ? "失败" : "Failed",
      progress: 100,
    });
    throw new Error(payload.error || "request_failed");
  }
  const blob = await resp.blob();
  const href = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const header = resp.headers.get("Content-Disposition") || "";
  const filename = /filename="([^"]+)"/.exec(header)?.[1] || "document.bin";
  link.href = href;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(href), 1200);
  upsertIoProgress("doc-flow", {
    id: downloadId,
    file: filename,
    type: lang() === "zh" ? "版本下载" : "Version Download",
    status: lang() === "zh" ? "已完成" : "Completed",
    progress: 100,
  });
}

async function handleDocumentFlowAction(documentId, action) {
  const copy = documentFlowCopy();
  if (!documentId || !action) return;
  if (action === "submit_draft") {
    return openDocumentDraftSubmitPanel(documentId);
  }
  if (action === "submit_revision") {
    return openDocumentRevisionPanel(documentId);
  }
  if (action === "comment") {
    return openDocumentCommentPanel(documentId);
  }
  const comments = window.prompt(copy.actionComment, "") || "";
  const resp = await fetch(`/api/document-flows/documents/${encodeURIComponent(documentId)}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, comments }),
  });
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
  renderDocumentFlowDetail(payload);
  await loadDocumentFlows();
}

function openDocumentDraftSubmitPanel(documentId) {
  const copy = documentFlowCopy();
  const detail = appState.documentFlows.detail;
  const currentCc = detail?.cc_recipients || [];
  const panel = ensureOverlayPanel(copy.actionButtons.submit_draft, `
    <form class="doc-flow-create-form" data-doc-submit-draft-form>
      <label class="auth-field">
        <span>${copy.reviewer}</span>
        <select name="reviewers" multiple size="6">${documentFlowUserOptions((detail?.steps || []).filter((step) => step.step_type === "review").map((step) => step.assigned_user_id))}</select>
      </label>
      <label class="auth-field">
        <span>${copy.approver}</span>
        <select name="approvers" multiple size="6">${documentFlowUserOptions((detail?.steps || []).filter((step) => step.step_type === "approval").map((step) => step.assigned_user_id))}</select>
      </label>
      <label class="auth-field">
        <span>${copy.ccUser}</span>
        <select name="cc_recipients" multiple size="5">${documentFlowUserOptions(currentCc.map((item) => item.user_id))}</select>
      </label>
      <label class="auth-field">
        <span>${copy.flowNote}</span>
        <textarea name="flow_note">${escapeHtml(detail?.document?.flow_note || "")}</textarea>
      </label>
      <button class="btn btn-primary" type="submit">${copy.actionButtons.submit_draft}</button>
      <div class="auth-feedback" data-doc-submit-draft-feedback></div>
    </form>
  `);
  panel.querySelector("[data-doc-submit-draft-form]")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const reviewers = Array.from(form.querySelector("select[name='reviewers']").selectedOptions).map((opt) => opt.value);
    const approvers = Array.from(form.querySelector("select[name='approvers']").selectedOptions).map((opt) => opt.value);
    const ccRecipients = Array.from(form.querySelector("select[name='cc_recipients']").selectedOptions).map((opt) => opt.value);
    try {
      const resp = await fetch(`/api/document-flows/documents/${encodeURIComponent(documentId)}/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "submit_draft",
          reviewers,
          approvers,
          cc_recipients: ccRecipients,
          flow_note: form.querySelector("textarea[name='flow_note']")?.value || "",
        }),
      });
      const payload = await resp.json();
      if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
      closeOverlayPanel();
      renderDocumentFlowDetail(payload);
      await loadDocumentFlows();
    } catch (error) {
      const feedback = panel.querySelector("[data-doc-submit-draft-feedback]");
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    }
  });
}

function openDocumentCommentPanel(documentId) {
  const copy = documentFlowCopy();
  const panel = ensureOverlayPanel(copy.commentTitle, `
    <form class="doc-flow-create-form" data-doc-comment-form>
      <label class="auth-field">
        <span>${copy.actionComment}</span>
        <textarea name="comments"></textarea>
      </label>
      <button class="btn btn-primary" type="submit">${copy.commentSubmit}</button>
      <div class="auth-feedback" data-doc-comment-feedback></div>
    </form>
  `);
  panel.querySelector("[data-doc-comment-form]")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    try {
      const resp = await fetch(`/api/document-flows/documents/${encodeURIComponent(documentId)}/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "comment", comments: String(formData.get("comments") || "") }),
      });
      const payload = await resp.json();
      if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
      closeOverlayPanel();
      renderDocumentFlowDetail(payload);
      await loadDocumentFlows();
    } catch (error) {
      const feedback = panel.querySelector("[data-doc-comment-feedback]");
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    }
  });
}

function openDocumentRevisionPanel(documentId) {
  const copy = documentFlowCopy();
  const panel = ensureOverlayPanel(copy.revisionTitle, `
    <form class="doc-flow-create-form" data-doc-revision-form>
      <div class="auth-note">${copy.revisionNote}</div>
      <label class="auth-field">
        <span>${copy.revisionFile}</span>
        <input type="file" name="file" required />
      </label>
      <label class="auth-field">
        <span>${copy.revisionSummary}</span>
        <textarea name="change_summary" required></textarea>
      </label>
      <label class="auth-field">
        <span>${copy.actionComment}</span>
        <textarea name="comments"></textarea>
      </label>
      <button class="btn btn-primary" type="submit">${copy.revisionSubmit}</button>
      <div class="auth-feedback" data-doc-revision-feedback></div>
    </form>
  `);
  panel.querySelector("[data-doc-revision-form]")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const file = form.querySelector("input[name='file']")?.files?.[0];
    const feedback = panel.querySelector("[data-doc-revision-feedback]");
    const progressId = `doc-flow-revision-${Date.now()}`;
    try {
      if (!file) throw new Error("file_required");
      upsertIoProgress("doc-flow", {
        id: progressId,
        file: file.name,
        type: lang() === "zh" ? "修订上传" : "Revision Upload",
        status: lang() === "zh" ? "上传中" : "Uploading",
        progress: 35,
      });
      const fileBase64 = await fileToBase64(file);
      const formData = new FormData(form);
      const resp = await fetch(`/api/document-flows/documents/${encodeURIComponent(documentId)}/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "submit_revision",
          filename: file.name,
          mime: file.type || "application/octet-stream",
          file_base64: fileBase64,
          preview: "",
          change_summary: String(formData.get("change_summary") || ""),
          comments: String(formData.get("comments") || ""),
        }),
      });
      const payload = await resp.json();
      if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
      upsertIoProgress("doc-flow", {
        id: progressId,
        file: file.name,
        type: lang() === "zh" ? "修订上传" : "Revision Upload",
        status: lang() === "zh" ? "已完成" : "Completed",
        progress: 100,
      });
      closeOverlayPanel();
      renderDocumentFlowDetail(payload);
      await loadDocumentFlows();
    } catch (error) {
      upsertIoProgress("doc-flow", {
        id: progressId,
        file: file?.name || documentId,
        type: lang() === "zh" ? "修订上传" : "Revision Upload",
        status: lang() === "zh" ? "失败" : "Failed",
        progress: 100,
      });
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    }
  });
}

async function openDocumentFlowCreate(defaults = {}) {
  const copy = documentFlowCopy();
  if (!(appState.documentFlows.users || []).length) {
    await loadDocumentFlowUsers();
  }
  const allDocs = appState.documentFlows.buckets?.all || [];
  const panel = ensureOverlayPanel(copy.createTitle, `
    <form class="doc-flow-create-form" data-doc-create-form>
      <label class="auth-field">
        <span>${copy.fileTitle}</span>
        <input type="text" name="title" value="${escapeHtml(defaults.title || "")}" required />
      </label>
      <label class="auth-field">
        <span>${copy.fileUpload}</span>
        <input type="file" name="file" />
      </label>
      <label class="auth-field">
        <span>${copy.textContent}</span>
        <textarea name="text_content">${escapeHtml(defaults.textContent || "")}</textarea>
      </label>
      ${defaults.requireChangeReason ? `<div class="auth-note">${copy.archiveNote}</div>` : ""}
      <div class="doc-flow-form-grid">
        <label class="auth-field">
          <span>${copy.reviewer}</span>
          <select name="reviewers" multiple size="6">${documentFlowUserOptions(defaults.reviewers || [])}</select>
        </label>
        <label class="auth-field">
          <span>${copy.approver}</span>
          <select name="approvers" multiple size="6">${documentFlowUserOptions(defaults.approvers || [])}</select>
        </label>
      </div>
      <label class="auth-field">
        <span>${copy.ccUser}</span>
        <select name="cc_recipients" multiple size="5">${documentFlowUserOptions(defaults.ccRecipients || [])}</select>
      </label>
      <label class="auth-field">
        <span>${copy.flowNote}</span>
        <textarea name="flow_note">${escapeHtml(defaults.flowNote || "")}</textarea>
      </label>
      <div class="doc-flow-form-grid">
        <label class="auth-field">
          <span>${copy.deadlineAt}</span>
          <input type="datetime-local" name="deadline_at" />
        </label>
        <label class="auth-field">
          <span>${copy.basedDoc}</span>
          <select name="based_on_document_id">
            <option value="">--</option>
            ${allDocs.map((item) => `<option value="${escapeHtml(item.id)}" ${item.id === defaults.basedOnDocumentId ? "selected" : ""}>${escapeHtml(item.title)}</option>`).join("")}
          </select>
        </label>
      </div>
      <label class="auth-field">
        <span>${copy.changeSummary}</span>
        <textarea name="change_summary" ${defaults.requireChangeReason ? "required" : ""}>${escapeHtml(defaults.changeSummary || "")}</textarea>
      </label>
      <div class="doc-flow-submit-row">
        <button class="btn btn-ghost" type="submit" data-save-draft="1">${copy.saveDraft}</button>
        <button class="btn btn-primary" type="submit">${copy.submitCreate}</button>
      </div>
      <div class="auth-feedback" data-doc-create-feedback></div>
    </form>
  `);
  panel.querySelector("[data-doc-create-form]")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const file = form.querySelector("input[name='file']")?.files?.[0];
    const feedback = panel.querySelector("[data-doc-create-feedback]");
    const progressId = `doc-flow-create-${Date.now()}`;
    try {
      const formData = new FormData(form);
      upsertIoProgress("doc-flow", {
        id: progressId,
        file: file?.name || String(formData.get("title") || ""),
        type: lang() === "zh" ? "流程上传" : "Workflow Upload",
        status: lang() === "zh" ? "准备中" : "Preparing",
        progress: 28,
      });
      const fileBase64 = file ? await fileToBase64(file) : "";
      const reviewers = Array.from(form.querySelector("select[name='reviewers']").selectedOptions).map((opt) => opt.value);
      const approvers = Array.from(form.querySelector("select[name='approvers']").selectedOptions).map((opt) => opt.value);
      const ccRecipients = Array.from(form.querySelector("select[name='cc_recipients']").selectedOptions).map((opt) => opt.value);
      const deadlineRaw = String(formData.get("deadline_at") || "");
      const deadlineAt = deadlineRaw ? Math.floor(new Date(deadlineRaw).getTime() / 1000) : 0;
      const submitter = event.submitter;
      const saveAsDraft = !!submitter?.matches("[data-save-draft]");
      const resp = await fetch("/api/document-flows/documents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: String(formData.get("title") || ""),
          filename: file?.name || "document.txt",
          mime: file?.type || "application/octet-stream",
          file_base64: fileBase64,
          text_content: String(formData.get("text_content") || ""),
          preview: String(formData.get("text_content") || "").slice(0, 2400),
          reviewers,
          approvers,
          cc_recipients: ccRecipients,
          flow_note: String(formData.get("flow_note") || ""),
          deadline_at: deadlineAt,
          based_on_document_id: String(formData.get("based_on_document_id") || ""),
          change_summary: String(formData.get("change_summary") || ""),
          change_request_reason: String(formData.get("change_summary") || ""),
          save_as_draft: saveAsDraft,
        }),
      });
      const payload = await resp.json();
      if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
      upsertIoProgress("doc-flow", {
        id: progressId,
        file: payload.document?.title || file?.name || String(formData.get("title") || ""),
        type: lang() === "zh" ? "流程上传" : "Workflow Upload",
        status: saveAsDraft ? (lang() === "zh" ? "已保存草稿" : "Saved as Draft") : (lang() === "zh" ? "已完成" : "Completed"),
        progress: 100,
      });
      closeOverlayPanel();
      appState.documentFlows.selectedId = payload.document?.id || payload.document?.document_id || payload.document?.current_workflow_id || "";
      renderDocumentFlowDetail(payload);
      await loadDocumentFlows();
    } catch (error) {
      upsertIoProgress("doc-flow", {
        id: progressId,
        file: file?.name || "document-flow",
        type: lang() === "zh" ? "流程上传" : "Workflow Upload",
        status: lang() === "zh" ? "失败" : "Failed",
        progress: 100,
      });
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    }
  });
}

function bindDocumentFlowControls() {
  const create = document.querySelector("[data-doc-flow-create]");
  if (create && !create.dataset.bound) {
    create.dataset.bound = "1";
    create.addEventListener("click", () => openDocumentFlowCreate().catch((error) => {
      ensureOverlayPanel(documentFlowCopy().createTitle, `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`);
    }));
  }
  const refresh = document.querySelector("[data-doc-flow-refresh]");
  if (refresh && !refresh.dataset.bound) {
    refresh.dataset.bound = "1";
    refresh.addEventListener("click", () => loadDocumentFlows().catch(() => {}));
  }
}

function startDocumentFlowRefresh() {
  if (appState.documentFlows.refreshTimer) clearInterval(appState.documentFlows.refreshTimer);
  appState.documentFlows.refreshTimer = setInterval(() => {
    if (appState.currentPage === "doc-flow" && appState.auth.authenticated) loadDocumentFlows().catch(() => {});
  }, 15000);
}

function ensureWorkMgmtPagesShell() {
  const main = document.querySelector("main.container");
  if (!main) return;
  if (!document.getElementById("workbench")) {
    const section = document.createElement("section");
    section.id = "workbench";
    section.className = "page";
    section.innerHTML = `
      <section class="card ops-page-shell">
        <div class="section-head ops-page-head">
          <div>
            <div class="eyebrow">Project Operations</div>
            <h2>${lang() === "zh" ? "Workbench 项目工作台" : "Project Workbench"}</h2>
            <p>${lang() === "zh" ? "项目、任务、风险和报告统一在一个工作面处理，先看状态，再进入具体项目。" : "Projects, tasks, risks, and reports are handled on one operating surface."}</p>
          </div>
          <div class="ops-page-head__actions">
            <button class="btn btn-ghost" type="button" data-workbench-page-refresh>${lang() === "zh" ? "刷新" : "Refresh"}</button>
            <button class="btn btn-primary" type="button" data-open-report-center-from-workbench>${lang() === "zh" ? "打开报告中心" : "Open Report Center"}</button>
          </div>
        </div>
        <div class="ops-trust-strip">
          <span>${lang() === "zh" ? "数据来源：项目/任务/文档中心" : "Source: Project / Task / Document center"}</span>
          <span>${lang() === "zh" ? "可信度：系统记录优先" : "Trust: system records first"}</span>
          <span>${lang() === "zh" ? "下一步：先处理超期和高风险项目" : "Next: clear overdue and high-risk items first"}</span>
        </div>
        <div class="ops-action-grid ops-action-grid--three">
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "项目检索" : "Project Search"}</strong>
            <span>${lang() === "zh" ? "按项目名、状态、负责人定位。" : "Find by name, status, or owner."}</span>
            <label class="auth-field">
              <input type="text" data-workbench-page-search placeholder="${escapeHtml(lang() === "zh" ? "输入项目名、状态、负责人" : "Search name, status, owner")}" />
            </label>
          </article>
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "报告动作" : "Report Action"}</strong>
            <span>${lang() === "zh" ? "进入日报、周报和管理复核。" : "Open daily, weekly, and management review reports."}</span>
            <button class="btn btn-ghost" type="button" data-open-report-center-from-workbench>${lang() === "zh" ? "打开报告中心" : "Open Report Center"}</button>
          </article>
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "全局搜索" : "Global Search"}</strong>
            <span>${lang() === "zh" ? "跨项目、任务、文档检索。" : "Search across projects, tasks, and documents."}</span>
            <label class="auth-field">
              <input type="text" data-workbench-page-global-search placeholder="${escapeHtml(lang() === "zh" ? "输入关键字后回车" : "Type keyword then Enter")}" />
            </label>
          </article>
        </div>
        <div class="workbench-decision-strip" data-workbench-decision-strip></div>
        <div data-workbench-operating-system style="margin-top:14px;"></div>
        <div class="summary-grid" data-workbench-page-summary></div>
        <div class="workbench-institutional-layout">
          <section class="workbench-primary-work" data-workbench-primary-work>
            <div class="auth-note">${lang() === "zh" ? "正在加载项目 War Room..." : "Loading project War Room..."}</div>
          </section>
          <aside class="workbench-secondary-panel" data-workbench-secondary-panel>
            <div class="auth-note">${lang() === "zh" ? "正在加载交易文件控制和 AI 工作流..." : "Loading deal document control and AI workflow..."}</div>
          </aside>
        </div>
        <section class="workbench-evidence-chain" data-workbench-evidence-chain></section>
        <div class="admin-user-list admin-user-list-compact workbench-legacy-projects" data-workbench-page-results></div>
        <div class="auth-note" data-workbench-page-global-results></div>
      </section>
    `;
    main.appendChild(section);
  }
  if (!document.getElementById("my-work")) {
    const section = document.createElement("section");
    section.id = "my-work";
    section.className = "page";
    section.innerHTML = `
      <section class="card ops-page-shell">
        <div class="section-head ops-page-head">
          <div>
            <div class="eyebrow">Personal Operations</div>
            <h2>${lang() === "zh" ? "My Work 我的工作" : "My Work"}</h2>
            <p>${lang() === "zh" ? "个人待办、审批、风险和最近动作集中展示，避免在多个页面来回跳。" : "Personal tasks, approvals, risks, and recent actions in one compact view."}</p>
          </div>
          <div class="ops-page-head__actions">
            <button class="btn btn-ghost" type="button" data-mywork-page-refresh>${lang() === "zh" ? "刷新" : "Refresh"}</button>
          </div>
        </div>
        <div class="ops-trust-strip">
          <span>${lang() === "zh" ? "数据来源：我的任务/审批/评论" : "Source: my tasks / approvals / comments"}</span>
          <span>${lang() === "zh" ? "下一步：优先处理待审批与超期项" : "Next: approvals and overdue items first"}</span>
        </div>
        <div class="ops-action-grid ops-action-grid--three">
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "待办队列" : "Task Queue"}</strong>
            <span>${lang() === "zh" ? "优先查看超期、阻塞和高优先级事项。" : "Prioritize overdue, blocked, and high-priority items."}</span>
          </article>
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "审批入口" : "Approval Entry"}</strong>
            <span>${lang() === "zh" ? "确认待批材料、责任人和截止时间。" : "Confirm pending materials, owners, and due dates."}</span>
          </article>
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "刷新状态" : "Refresh State"}</strong>
            <span>${lang() === "zh" ? "重新同步个人工作队列。" : "Resync the personal work queue."}</span>
            <button class="btn btn-ghost" type="button" data-mywork-page-refresh>${lang() === "zh" ? "刷新" : "Refresh"}</button>
          </article>
        </div>
        <div data-mywork-page-body></div>
      </section>
    `;
    main.appendChild(section);
  }
  if (!document.getElementById("reports")) {
    const section = document.createElement("section");
    section.id = "reports";
    section.className = "page";
    section.innerHTML = `
      <section class="card ops-page-shell">
        <div class="section-head ops-page-head">
          <div>
            <div class="eyebrow">Automated Reporting</div>
            <h2>${lang() === "zh" ? "Report Center 报告中心" : "Report Center"}</h2>
            <p>${lang() === "zh" ? "日报、周报和管理复核报告统一生成、筛选、评论和闭环。" : "Generate, filter, review, comment, and close reporting loops in one place."}</p>
          </div>
          <div class="ops-page-head__actions">
            <button class="btn btn-ghost" type="button" data-reports-page-refresh>${lang() === "zh" ? "刷新" : "Refresh"}</button>
          </div>
        </div>
        <div class="ops-trust-strip">
          <span>${lang() === "zh" ? "数据来源：日报/周报生成记录" : "Source: generated report records"}</span>
          <span>${lang() === "zh" ? "可信度：系统报告 + 人工评论" : "Trust: system report + human comments"}</span>
          <span>${lang() === "zh" ? "下一步：先筛选 follow_up_needed" : "Next: filter follow_up_needed first"}</span>
        </div>
        <div class="ops-action-grid ops-action-grid--three">
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "报告筛选" : "Report Filter"}</strong>
            <span>${lang() === "zh" ? "按日报、周报、项目报告快速切换。" : "Switch by daily, weekly, and project report types."}</span>
            <label class="auth-field">
              <select data-reports-page-type>
                <option value="">all</option>
                <option value="admin_daily_summary">admin_daily_summary</option>
                <option value="user_daily">user_daily</option>
                <option value="user_weekly">user_weekly</option>
                <option value="project_daily">project_daily</option>
                <option value="project_weekly">project_weekly</option>
              </select>
            </label>
          </article>
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "生成日报" : "Generate Daily"}</strong>
            <span>${lang() === "zh" ? "管理员可生成全局日报。" : "Admins can generate global daily reports."}</span>
            <button class="btn btn-primary" type="button" data-reports-page-gen-daily>${lang() === "zh" ? "生成日报" : "Generate Daily"}</button>
          </article>
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "生成周报" : "Generate Weekly"}</strong>
            <span>${lang() === "zh" ? "管理员可生成周度复盘。" : "Admins can generate weekly reviews."}</span>
            <button class="btn btn-ghost" type="button" data-reports-page-gen-weekly>${lang() === "zh" ? "生成周报" : "Generate Weekly"}</button>
          </article>
        </div>
        <div class="doc-flow-page card" style="margin-top:10px;">
          <aside class="doc-flow-sidebar">
            <div class="side-title">${lang() === "zh" ? "报告列表" : "Reports"}</div>
            <div class="work-chat-list" data-reports-page-list></div>
          </aside>
          <section class="doc-flow-main">
            <div data-reports-page-detail>${lang() === "zh" ? "请选择报告查看详情。" : "Select a report to view details."}</div>
            <form class="doc-flow-create-form" data-reports-page-form style="margin-top:12px;">
              <label class="auth-field">
                <span>${lang() === "zh" ? "添加评论/指令" : "Add Comment/Instruction"}</span>
                <textarea name="comment"></textarea>
              </label>
              <label class="auth-field">
                <span>${lang() === "zh" ? "状态" : "Status"}</span>
                <select name="status">
                  <option value="generated">generated</option>
                  <option value="reviewed">reviewed</option>
                  <option value="follow_up_needed">follow_up_needed</option>
                  <option value="resolved">resolved</option>
                </select>
              </label>
              <div class="work-chat-actions">
                <button class="btn btn-primary" type="submit">${lang() === "zh" ? "保存评论与状态" : "Save Comment & Status"}</button>
              </div>
              <div class="auth-feedback" data-reports-page-feedback></div>
            </form>
          </section>
        </div>
      </section>
    `;
    main.appendChild(section);
  }
  if (!document.getElementById("ai-agent")) {
    const section = document.createElement("section");
    section.id = "ai-agent";
    section.className = "page";
    section.innerHTML = `
      <section class="card ai-agent-shell">
        <div class="section-head ops-page-head">
          <div>
            <div class="eyebrow">AI Agent Hub</div>
            <h2>${lang() === "zh" ? "AI Agent 调用中枢" : "AI Agent Hub"}</h2>
            <p>${lang() === "zh" ? "把 Hermes 内部 Agent、欧亿 AI8 外部 Agent 和人机单独交流入口统一到一个受控工作面。" : "A controlled surface for Hermes internal agents, the external AI8 agent, and one-to-one human-agent exchange."}</p>
          </div>
          <div class="ops-page-head__actions">
            <button class="btn btn-ghost" type="button" data-ai-agent-refresh>${lang() === "zh" ? "刷新连接" : "Refresh Link"}</button>
            <button class="btn btn-primary" type="button" data-ai-agent-open-ai8>${lang() === "zh" ? "打开 AI8" : "Open AI8"}</button>
          </div>
        </div>
        <div class="ops-trust-strip">
          <span>${lang() === "zh" ? "数据来源：Hermes Agent / AI8 页面探测 / 审计记录" : "Source: Hermes Agent / AI8 page probe / audit trail"}</span>
          <span>${lang() === "zh" ? "原则：能直连则直连，不能直连则任务中转并回填" : "Principle: direct API when available; otherwise task handoff and return capture"}</span>
          <span>${lang() === "zh" ? "下一步：提交任务、在 AI8 执行、把结果保存回 Hermes" : "Next: submit task, execute in AI8, save result back to Hermes"}</span>
        </div>
        <div data-ai-agent-status></div>
        <div class="ai-agent-layout">
          <section class="ai-agent-primary">
            <article class="ai-agent-card ai-agent-card--hero">
              <div class="ai-agent-card__top">
                <span>01</span>
                <strong>${lang() === "zh" ? "人 ↔ AI Agent 单独交流入口" : "Human ↔ AI Agent Direct Exchange"}</strong>
              </div>
              <p>${lang() === "zh" ? "这里是独立入口，不混入金融/法律正式结论。适合先探索、追问、生成草稿，再把结果保存到项目、文件或 Hermes 记忆。" : "This is a separate exchange surface, kept apart from formal finance/legal conclusions. Explore, ask follow-ups, draft, then save results to projects, files, or Hermes memory."}</p>
              <label class="auth-field">
                <span>${lang() === "zh" ? "任务标题" : "Task title"}</span>
                <input type="text" data-ai-agent-title value="${escapeHtml(lang() === "zh" ? "AI8 外部 Agent 协作任务" : "AI8 External Agent Collaboration Task")}" />
              </label>
              <label class="auth-field">
                <span>${lang() === "zh" ? "任务内容" : "Task prompt"}</span>
                <textarea data-ai-agent-prompt placeholder="${escapeHtml(lang() === "zh" ? "输入要交给 AI8 Agent 的任务；提交后系统会生成可复制任务包，并尝试后端直连（如已配置 API）。" : "Enter the task for the AI8 agent; Hermes will create a copy-ready task packet and attempt direct API if configured.")}"></textarea>
              </label>
	              <div class="ai-agent-option-grid">
                <label class="auth-field">
                  <span>${lang() === "zh" ? "调用模式" : "Bridge mode"}</span>
                  <select data-ai-agent-mode>
                    <option value="auto">${lang() === "zh" ? "自动：API优先，失败则中转" : "Auto: API first, handoff fallback"}</option>
                    <option value="handoff">${lang() === "zh" ? "任务中转 / 人工回填" : "Task handoff / human return"}</option>
                    <option value="embed">${lang() === "zh" ? "页面嵌入辅助" : "Embedded page assist"}</option>
                  </select>
                </label>
                <label class="auth-field">
                  <span>${lang() === "zh" ? "结果去向" : "Return target"}</span>
                  <select data-ai-agent-target>
                    <option value="hermes-memory">${lang() === "zh" ? "Hermes 研究记忆" : "Hermes research memory"}</option>
                    <option value="project-war-room">${lang() === "zh" ? "项目 War Room" : "Project War Room"}</option>
                    <option value="file-center">${lang() === "zh" ? "文件中心" : "File Center"}</option>
                    <option value="draft-only">${lang() === "zh" ? "仅草稿" : "Draft only"}</option>
                  </select>
	                </label>
	                <label class="auth-field">
	                  <span>${lang() === "zh" ? "AI 输出状态" : "AI Output State"}</span>
	                  <select data-ai-agent-output-state>
	                    <option value="draft">${lang() === "zh" ? "草稿" : "Draft"}</option>
	                    <option value="pending_review" selected>${lang() === "zh" ? "待复核" : "Pending review"}</option>
	                    <option value="adopted">${lang() === "zh" ? "已采用" : "Adopted"}</option>
	                    <option value="rejected">${lang() === "zh" ? "已驳回" : "Rejected"}</option>
	                    <option value="archived">${lang() === "zh" ? "已归档" : "Archived"}</option>
	                  </select>
	                </label>
	              </div>
              <div class="ai-agent-actions">
                <button class="btn btn-primary" type="button" data-ai-agent-submit>${lang() === "zh" ? "提交给 AI8 Agent" : "Submit to AI8 Agent"}</button>
                <button class="btn btn-ghost" type="button" data-ai-agent-copy-prompt>${lang() === "zh" ? "复制任务包" : "Copy Task Packet"}</button>
                <button class="btn btn-ghost" type="button" data-ai-agent-save-result>${lang() === "zh" ? "保存回 Hermes" : "Save Back to Hermes"}</button>
              </div>
              <div class="auth-feedback" data-ai-agent-feedback></div>
              <div class="ai-agent-result" data-ai-agent-result></div>
            </article>
          </section>
          <aside class="ai-agent-side">
            <article class="ai-agent-card">
              <div class="ai-agent-card__top">
                <span>02</span>
                <strong>${lang() === "zh" ? "连接策略" : "Connection Strategy"}</strong>
              </div>
              <div class="ai-agent-bridge-steps">
                <div><b>API</b><span>${lang() === "zh" ? "如配置 AI8_API_URL / AI8_API_KEY，Hermes 后端直连并审计。" : "If AI8_API_URL / AI8_API_KEY is configured, Hermes calls directly and audits."}</span></div>
                <div><b>WEB</b><span>${lang() === "zh" ? "无 API 时打开/嵌入 AI8 页面，生成标准任务包。" : "Without API, open/embed AI8 and generate a standardized task packet."}</span></div>
                <div><b>RETURN</b><span>${lang() === "zh" ? "把外部结果粘贴回来，标记为草稿/待复核/已采用。" : "Paste external output back and mark draft/pending/adopted."}</span></div>
              </div>
            </article>
            <article class="ai-agent-card ai-agent-card--embed">
              <div class="ai-agent-card__top">
                <span>03</span>
                <strong>${lang() === "zh" ? "AI8 嵌入预览" : "AI8 Embedded Preview"}</strong>
              </div>
              <div class="ai-agent-embed-actions">
                <button class="btn btn-ghost" type="button" data-ai-agent-embed-expand>${lang() === "zh" ? "超宽模式" : "Expand"}</button>
                <button class="btn btn-ghost" type="button" data-ai-agent-embed-focus>${lang() === "zh" ? "聚焦模式" : "Focus"}</button>
              </div>
              <p>${lang() === "zh" ? "若浏览器或目标站点限制嵌入，请使用“打开 AI8”。" : "If the browser or target site blocks embedding, use Open AI8."}</p>
              <iframe title="AI8 Agent" src="https://ai8.rcouyi.com/chat" loading="lazy" referrerpolicy="no-referrer"></iframe>
            </article>
          </aside>
        </div>
      </section>
    `;
    main.appendChild(section);
  }
  if (!document.getElementById("file-center")) {
    const section = document.createElement("section");
    section.id = "file-center";
    section.className = "page";
    section.innerHTML = `
      <section class="card file-center-shell">
        <div class="section-head file-center-head">
          <div>
            <div class="eyebrow">Enterprise File Governance</div>
            <h2>${lang() === "zh" ? "公司文件汇总管理中心" : "Company File Center"}</h2>
            <p>${lang() === "zh" ? "文件入库、检索、版本、审批和归档集中处理。操作区已压缩为卡片任务矩阵，减少长条菜单对页面的切割。" : "Intake, search, versioning, approval, and archive are grouped into task cards to reduce long toolbar interruptions."}</p>
          </div>
          <div class="file-center-primary-actions">
            <button class="btn btn-ghost" type="button" data-file-center-refresh>${lang() === "zh" ? "刷新" : "Refresh"}</button>
            <button class="btn btn-primary" type="button" data-file-center-generate-daily>${lang() === "zh" ? "生成昨日汇总" : "Generate Daily Digest"}</button>
          </div>
        </div>
        <div class="file-center-action-grid">
          <article class="file-center-action-card file-center-action-card--wide">
            <div class="file-center-action-card__head">
              <span>01</span>
              <strong>${lang() === "zh" ? "范围与检索" : "Scope & Search"}</strong>
            </div>
            <p>${lang() === "zh" ? "先确定管理视角，再按标题、项目、状态或负责人快速定位文件。" : "Choose the governance scope, then locate files by title, project, status, or owner."}</p>
            <div class="file-center-field-grid">
              <label class="auth-field">
                <span>${lang() === "zh" ? "管理视角" : "View Scope"}</span>
                <select data-file-center-scope>
                  <option value="my">${lang() === "zh" ? "个人管理中心" : "My Center"}</option>
                  <option value="workspace">${lang() === "zh" ? "工作平台管理中心" : "Workspace Center"}</option>
                  <option value="global">${lang() === "zh" ? "全局管理中心" : "Global Center"}</option>
                </select>
              </label>
              <label class="auth-field">
                <span>${lang() === "zh" ? "平台标识" : "Workspace ID"}</span>
                <input type="text" data-file-center-workspace placeholder="finance / legal / doc-flow / work-chat" />
              </label>
              <label class="auth-field file-center-field-span">
                <span>${lang() === "zh" ? "文件检索" : "File Search"}</span>
                <input type="text" data-file-center-search placeholder="${escapeHtml(lang() === "zh" ? "标题/项目/状态/负责人" : "Title / project / status / owner")}" />
              </label>
            </div>
            <button class="btn btn-ghost file-center-card-action" type="button" data-file-center-query>${lang() === "zh" ? "查询文件" : "Search Files"}</button>
          </article>
          <article class="file-center-action-card">
            <div class="file-center-action-card__head">
              <span>02</span>
              <strong>${lang() === "zh" ? "新文件入库" : "New Intake"}</strong>
            </div>
            <p>${lang() === "zh" ? "创建可追踪文件记录，适合合同、报告、底稿和审批材料。" : "Create a governed file record for contracts, reports, workpapers, and approval packs."}</p>
            <label class="auth-field">
              <span>${lang() === "zh" ? "新文件标题" : "New File Title"}</span>
              <input type="text" data-file-center-title placeholder="${escapeHtml(lang() === "zh" ? "例如：采购合同-2026Q2" : "e.g. Procurement Contract - 2026Q2")}" />
            </label>
            <label class="auth-field">
              <span>${lang() === "zh" ? "文件分类" : "Category"}</span>
              <input type="text" data-file-center-category value="general" />
            </label>
            <button class="btn btn-primary file-center-card-action" type="button" data-file-center-create>${lang() === "zh" ? "上传并入库" : "Upload to Center"}</button>
          </article>
          <article class="file-center-action-card">
            <div class="file-center-action-card__head">
              <span>03</span>
              <strong>${lang() === "zh" ? "版本与流程" : "Version & Flow"}</strong>
            </div>
            <p>${lang() === "zh" ? "为选中文件新增版本，或直接发起审阅、审批、签字流程。" : "Add a version to the selected file or start review, approval, and signing."}</p>
            <label class="auth-field">
              <span>${lang() === "zh" ? "上传文件" : "Upload File"}</span>
              <input type="file" data-file-center-upload />
            </label>
            <div class="file-center-action-stack">
              <button class="btn btn-ghost" type="button" data-file-center-add-version>${lang() === "zh" ? "新增版本" : "Add Version"}</button>
              <button class="btn btn-ghost" type="button" data-file-center-start-review>${lang() === "zh" ? "发起审阅" : "Start Review"}</button>
              <button class="btn btn-ghost" type="button" data-file-center-start-approval>${lang() === "zh" ? "发起审批" : "Start Approval"}</button>
              <button class="btn btn-primary" type="button" data-file-center-start-sign>${lang() === "zh" ? "发起签字" : "Start Signing"}</button>
              <button class="btn btn-ghost" type="button" data-file-center-start-workflow>${lang() === "zh" ? "审阅+审批+签字" : "Review+Approve+Sign"}</button>
            </div>
          </article>
          <article class="file-center-action-card">
            <div class="file-center-action-card__head">
              <span>04</span>
              <strong>${lang() === "zh" ? "归档与反馈" : "Archive & Feedback"}</strong>
            </div>
            <p>${lang() === "zh" ? "完成签字归档，查看操作反馈；管理员或负责人可执行锁定。" : "Archive signed files and review operation feedback; locking is available to admins or owners."}</p>
            <button class="btn btn-ghost file-center-card-action" type="button" data-file-center-archive>${lang() === "zh" ? "签字归档" : "Sign & Archive"}</button>
            <div class="auth-feedback file-center-feedback" data-file-center-feedback></div>
          </article>
          <article class="file-center-action-card">
            <div class="file-center-action-card__head">
              <span>05</span>
              <strong>${lang() === "zh" ? "交叉检查" : "Cross Check"}</strong>
            </div>
            <p>${lang() === "zh" ? "检查重复文件、项目归属、敏感资料、版本缺口和归档锁定不一致。" : "Check duplicates, project ownership, sensitive files, version gaps, and archive lock mismatch."}</p>
            <button class="btn btn-ghost file-center-card-action" type="button" data-file-center-cross-check>${lang() === "zh" ? "打开交叉检查" : "Open Cross Check"}</button>
          </article>
          <article class="file-center-action-card">
            <div class="file-center-action-card__head">
              <span>06</span>
              <strong>${lang() === "zh" ? "导出与 DLP" : "Export & DLP"}</strong>
            </div>
            <p>${lang() === "zh" ? "导出前确认 need-to-know、敏感词、外发权限，下载进入审计留痕。" : "Confirm need-to-know, sensitive terms, and outbound permissions before export; downloads are logged."}</p>
            <button class="btn btn-ghost file-center-card-action" type="button" data-file-center-open-governance>${lang() === "zh" ? "查看 DLP 留痕" : "View DLP Trail"}</button>
          </article>
          <article class="file-center-action-card">
            <div class="file-center-action-card__head">
              <span>07</span>
              <strong>${lang() === "zh" ? "下一步建议" : "Next Step"}</strong>
            </div>
            <p>${lang() === "zh" ? "按“发现问题 → 查看依据 → 执行动作”推进文件闭环。" : "Move through find issue, review evidence, and act."}</p>
            <button class="btn btn-primary file-center-card-action" type="button" data-file-center-open-docflow>${lang() === "zh" ? "进入文件流程" : "Open Doc Flow"}</button>
          </article>
        </div>
        <div class="ops-trust-strip">
          <span>${lang() === "zh" ? "数据来源：文件、版本、审批和归档" : "Source: files, versions, approvals, archive"}</span>
          <span>${lang() === "zh" ? "可信度：签字锁定记录优先" : "Trust: signed and locked records first"}</span>
          <span>${lang() === "zh" ? "下一步：先看超期、待处理和最新版本" : "Next: overdue, pending, latest version"}</span>
        </div>
        <div class="summary-grid" data-file-center-summary style="margin-top:12px;"></div>
        <div data-file-center-deal-control style="margin-top:12px;"></div>
        <div class="admin-panel" data-file-center-analytics style="margin-top:12px;"></div>
        <div class="doc-flow-page card" style="margin-top:10px;">
          <aside class="doc-flow-sidebar">
            <div class="side-title">${lang() === "zh" ? "文件列表" : "Files"}</div>
            <div class="work-chat-list" data-file-center-list></div>
          </aside>
          <section class="doc-flow-main">
            <div data-file-center-detail>${lang() === "zh" ? "请选择文件查看详情。" : "Select a file to inspect details."}</div>
          </section>
        </div>
      </section>
    `;
    main.appendChild(section);
  }
  if (!document.getElementById("governance-center")) {
    const section = document.createElement("section");
    section.id = "governance-center";
    section.className = "page";
    section.innerHTML = `
      <section class="card ops-page-shell governance-center-shell">
        <div class="section-head ops-page-head">
          <div>
            <div class="eyebrow">Compliance & Audit Control</div>
            <h2>${lang() === "zh" ? "合规与审计中心" : "Compliance & Audit Center"}</h2>
            <p>${lang() === "zh" ? "把操作日志、审批日志、文件访问、AI 输出、导出记录、DLP 和权限视图集中到一个可执行工作面。" : "A single operating surface for action logs, approvals, file access, AI output, exports, DLP, and permission views."}</p>
          </div>
          <div class="ops-page-head__actions">
            <button class="btn btn-ghost" type="button" data-governance-center-refresh>${lang() === "zh" ? "刷新" : "Refresh"}</button>
            <button class="btn btn-primary" type="button" data-governance-open-files>${lang() === "zh" ? "打开文件中心" : "Open File Center"}</button>
          </div>
        </div>
        <div class="ops-trust-strip">
          <span>${lang() === "zh" ? "数据来源：审计日志 / 权限 / 会话 / 集成 / 文件外发" : "Source: audit logs / permissions / sessions / integrations / outbound files"}</span>
          <span>${lang() === "zh" ? "原则：need-to-know、全流程留痕、异常优先" : "Principle: need-to-know, full traceability, exceptions first"}</span>
          <span>${lang() === "zh" ? "下一步：先处理 DLP 命中、失败连接和高风险项目" : "Next: clear DLP hits, failed connections, and high-risk projects"}</span>
        </div>
        <div class="ops-action-grid ops-action-grid--four">
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "审计追踪" : "Audit Trail"}</strong>
            <span>${lang() === "zh" ? "操作、审批、导出、下载和敏感访问统一查看。" : "View actions, approvals, exports, downloads, and sensitive access."}</span>
          </article>
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "权限视图" : "Permission View"}</strong>
            <span>${lang() === "zh" ? "RBAC、同事可见范围、管理权限和最小授权原则。" : "RBAC, colleague visibility, admin scope, and least privilege."}</span>
          </article>
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "DLP 防线" : "DLP Line"}</strong>
            <span>${lang() === "zh" ? "敏感词、导出提示、下载留痕和水印策略。" : "Sensitive terms, export prompts, download logs, and watermark policy."}</span>
          </article>
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "闭环入口" : "Closure Entry"}</strong>
            <span>${lang() === "zh" ? "从异常进入文件中心、报告中心、项目工作台。" : "Move from exceptions into files, reports, and project workbench."}</span>
            <div class="file-center-action-stack">
              <button class="btn btn-ghost" type="button" data-governance-open-reports>${lang() === "zh" ? "报告中心" : "Reports"}</button>
              <button class="btn btn-ghost" type="button" data-governance-open-workbench>${lang() === "zh" ? "项目工作台" : "Workbench"}</button>
            </div>
          </article>
        </div>
        <div data-governance-center-body style="margin-top:12px;"></div>
      </section>
    `;
    main.appendChild(section);
  }
  if (!document.getElementById("intel-center")) {
    const section = document.createElement("section");
    section.id = "intel-center";
    section.className = "page";
    section.innerHTML = `
      <section class="card intel-page-shell">
        <div class="section-head ops-page-head">
          <div>
            <div class="eyebrow">Global Markets & Intelligence</div>
            <h2>${lang() === "zh" ? "Intelligence Center 情报中心" : "Intelligence Center"}</h2>
            <p>${lang() === "zh" ? "全球市场、Top30 新闻、风险与联动信息在同一页面统一决策。" : "Global markets, Top 30 intelligence, risks, and linked moves in one decision surface."}</p>
          </div>
          <div class="intel-page-header__meta">
            <span>${lang() === "zh" ? "最近更新时间" : "Last updated"}</span>
            <strong data-intel-page-updated>${escapeHtml(formatDateTime(Math.floor(Date.now() / 1000)))}</strong>
          </div>
        </div>
        <div class="ops-trust-strip">
          <span>${lang() === "zh" ? "数据来源：市场快照 / Top30 新闻 / K线 / 汇率 / 国债收益率" : "Source: market snapshot / Top 30 news / candles / FX / sovereign yields"}</span>
          <span>${lang() === "zh" ? "可信度：来源数与更新时间双校验" : "Trust: source count and freshness checks"}</span>
          <span>${lang() === "zh" ? "下一步：先看高风险新闻和市场联动" : "Next: high-risk stories and market linkage first"}</span>
        </div>
        <div class="ops-action-grid ops-action-grid--four intel-top-actions">
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "刷新总览" : "Refresh Overview"}</strong>
            <span>${lang() === "zh" ? "同步页面摘要、状态和当前筛选。" : "Sync summary, status, and filters."}</span>
            <button class="btn btn-ghost" type="button" data-intel-refresh>${lang() === "zh" ? "刷新" : "Refresh"}</button>
          </article>
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "刷新行情" : "Refresh Markets"}</strong>
            <span>${lang() === "zh" ? "更新全球指数与相关市场。" : "Update global indices and linked markets."}</span>
            <button class="btn btn-primary" type="button" data-intel-refresh-market>${lang() === "zh" ? "刷新行情" : "Refresh Markets"}</button>
          </article>
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "刷新新闻" : "Refresh News"}</strong>
            <span>${lang() === "zh" ? "抓取并更新新闻池。" : "Fetch and update the news pool."}</span>
            <button class="btn btn-ghost" type="button" data-intel-refresh-news>${lang() === "zh" ? "刷新新闻" : "Refresh News"}</button>
          </article>
          <article class="ops-action-card">
            <strong>${lang() === "zh" ? "生成 Top30" : "Generate Top 30"}</strong>
            <span>${lang() === "zh" ? "生成精选情报榜单。" : "Generate ranked intelligence."}</span>
            <button class="btn btn-ghost" type="button" data-intel-generate-digest>${lang() === "zh" ? "生成 Top30" : "Generate Top 30"}</button>
          </article>
        </div>
        <div class="auth-note">${lang() === "zh" ? "系统每天 08:00（Asia/Shanghai）自动生成并刷新数据中心数据。" : "The system auto-generates and refreshes Data Center content every day at 08:00 (Asia/Shanghai)."}</div>
        <div class="intel-toolbar" style="margin-top:12px;">
          <div class="intel-toolbar__row">
            <label class="intel-mini-field">
              <span>${lang() === "zh" ? "语言" : "Lang"}</span>
              <select data-intel-lang>
                <option value="zh">CN</option>
                <option value="en">EN</option>
              </select>
            </label>
            <label class="intel-mini-field">
              <span>${lang() === "zh" ? "分类" : "Category"}</span>
              <select data-intel-category>
                <option value="">${lang() === "zh" ? "全部" : "All"}</option>
                <option value="finance">${lang() === "zh" ? "金融" : "Finance"}</option>
                <option value="technology">${lang() === "zh" ? "科技" : "Tech"}</option>
                <option value="politics">${lang() === "zh" ? "政治" : "Policy"}</option>
              </select>
            </label>
            <label class="intel-mini-field">
              <span>${lang() === "zh" ? "时间" : "Window"}</span>
              <select data-intel-window>
                <option value="24h">24h</option>
                <option value="48h">48h</option>
                <option value="7d">7d</option>
              </select>
            </label>
            <label class="intel-mini-field intel-mini-field--grow">
              <span>${lang() === "zh" ? "新闻搜索" : "News Search"}</span>
              <input type="text" data-intel-news-search placeholder="${escapeHtml(lang() === "zh" ? "标题 / 来源 / 主题" : "Title / source / topic")}" />
            </label>
            <label class="intel-mini-field">
              <span>${lang() === "zh" ? "地区" : "Region"}</span>
              <select data-intel-region>
                <option value="">${lang() === "zh" ? "全部" : "All"}</option>
                <option value="us">${lang() === "zh" ? "美国" : "US"}</option>
                <option value="china">${lang() === "zh" ? "中国" : "China"}</option>
                <option value="europe">${lang() === "zh" ? "欧洲" : "Europe"}</option>
                <option value="asia">${lang() === "zh" ? "亚洲" : "Asia"}</option>
              </select>
            </label>
            <label class="intel-mini-field">
              <span>${lang() === "zh" ? "风险" : "Risk"}</span>
              <select data-intel-risk>
                <option value="">${lang() === "zh" ? "全部" : "All"}</option>
                <option value="high">${lang() === "zh" ? "高" : "High"}</option>
                <option value="medium">${lang() === "zh" ? "中" : "Medium"}</option>
              </select>
            </label>
            <label class="intel-mini-field">
              <span>${lang() === "zh" ? "排序" : "Sort"}</span>
              <select data-intel-sort>
                <option value="importance">${lang() === "zh" ? "重要性" : "Importance"}</option>
                <option value="time">${lang() === "zh" ? "时间" : "Time"}</option>
                <option value="relevance">${lang() === "zh" ? "相关性" : "Relevance"}</option>
              </select>
            </label>
            <label class="intel-mini-field intel-mini-field--grow">
              <span>${lang() === "zh" ? "标的" : "Symbol"}</span>
              <input type="text" data-intel-instrument-query placeholder="${escapeHtml(lang() === "zh" ? "AAPL / SPY / ^GSPC" : "AAPL / SPY / ^GSPC")}" />
            </label>
            <label class="intel-mini-field">
              <span>${lang() === "zh" ? "周期" : "Interval"}</span>
              <select data-intel-candle-interval>
                <option value="1m">1m</option>
                <option value="5m">5m</option>
                <option value="15m">15m</option>
                <option value="30m">30m</option>
                <option value="1h">1h</option>
                <option value="1d" selected>1d</option>
                <option value="1w">1w</option>
                <option value="1mo">1mo</option>
              </select>
            </label>
            <label class="intel-mini-field">
              <span>${lang() === "zh" ? "区间" : "Range"}</span>
              <select data-intel-candle-range>
                <option value="1mo">1mo</option>
                <option value="3mo">3mo</option>
                <option value="6mo" selected>6mo</option>
                <option value="1y">1y</option>
                <option value="2y">2y</option>
              </select>
            </label>
            <button class="btn btn-soft intel-toolbar__btn" type="button" data-intel-load-candle>${lang() === "zh" ? "K线" : "K-Line"}</button>
          </div>
          <div class="auth-feedback" data-intel-feedback></div>
        </div>
        <div data-intel-quality-strip></div>
        <section class="intel-highlight-grid" style="margin-top:12px;">
          <div class="summary-grid intel-summary-grid" data-intel-summary></div>
          <div class="admin-panel intel-block" data-intel-markets></div>
        </section>
        <div class="intel-layout intel-layout--news" style="margin-top:12px;">
          <section class="intel-main-stack">
            <div class="admin-panel intel-block" data-intel-news></div>
            <div class="admin-panel intel-block" data-intel-candle></div>
          </section>
          <aside class="intel-side-stack">
            <div class="admin-panel intel-block" data-intel-news-detail></div>
            <div class="admin-panel intel-block" data-intel-related-markets></div>
            <div class="admin-panel intel-block" data-intel-macro-rates></div>
            <div class="admin-panel intel-block" data-intel-source-mix></div>
            <div class="admin-panel intel-block" data-intel-trending-topics></div>
            <div class="admin-panel intel-block" data-intel-risk-alerts></div>
            <div class="admin-panel intel-block" data-intel-saved-items></div>
          </aside>
        </div>
        <div data-intel-state-layer></div>
      </section>
    `;
    main.appendChild(section);
  }
  const workbenchPage = document.getElementById("workbench");
  if (workbenchPage && workbenchPage.dataset.bound !== "1") {
    workbenchPage.dataset.bound = "1";
    let timer = null;
    workbenchPage.querySelectorAll("[data-workbench-page-refresh]").forEach((node) => node.addEventListener("click", () => loadWorkbenchPage().catch(() => {})));
    workbenchPage.querySelectorAll("[data-open-report-center-from-workbench]").forEach((node) => node.addEventListener("click", () => setActivePage("reports", true)));
    workbenchPage.querySelectorAll("[data-workbench-page-search]").forEach((node) => node.addEventListener("input", (event) => {
      clearTimeout(timer);
      const q = String(event.target?.value || "").trim();
      timer = setTimeout(() => loadWorkbenchPage(q).catch(() => {}), 180);
    }));
    workbenchPage.querySelectorAll("[data-workbench-page-global-search]").forEach((node) => node.addEventListener("keydown", async (event) => {
      if (event.key !== "Enter") return;
      event.preventDefault();
      const q = String(event.target?.value || "").trim();
      const host = workbenchPage.querySelector("[data-workbench-page-global-results]");
      if (!q) {
        if (host) host.textContent = "";
        return;
      }
      try {
        const found = await loadV2GlobalSearch(q);
        if (host) {
          host.textContent = `${lang() === "zh" ? "项目" : "Projects"}: ${found.projects.length} · ${lang() === "zh" ? "任务" : "Tasks"}: ${found.work_items.length} · ${lang() === "zh" ? "文档" : "Documents"}: ${found.documents.length}`;
        }
      } catch (error) {
        if (host) host.textContent = authErrorMessage(error.message);
      }
    }));
  }
  const myWorkPage = document.getElementById("my-work");
  if (myWorkPage && myWorkPage.dataset.bound !== "1") {
    myWorkPage.dataset.bound = "1";
    myWorkPage.querySelectorAll("[data-mywork-page-refresh]").forEach((node) => node.addEventListener("click", () => loadMyWorkPage().catch(() => {})));
  }
  const reportsPage = document.getElementById("reports");
  if (reportsPage && reportsPage.dataset.bound !== "1") {
    reportsPage.dataset.bound = "1";
    reportsPage.querySelector("[data-reports-page-refresh]")?.addEventListener("click", () => loadReportsPage().catch(() => {}));
    reportsPage.querySelector("[data-reports-page-type]")?.addEventListener("change", () => loadReportsPage().catch(() => {}));
    reportsPage.querySelector("[data-reports-page-gen-daily]")?.addEventListener("click", async () => {
      const feedback = reportsPage.querySelector("[data-reports-page-feedback]");
      try {
        await triggerV2ReportGenerate("daily", true);
        if (feedback) feedback.textContent = lang() === "zh" ? "日报任务已触发。" : "Daily generation triggered.";
        await loadReportsPage();
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
    reportsPage.querySelector("[data-reports-page-gen-weekly]")?.addEventListener("click", async () => {
      const feedback = reportsPage.querySelector("[data-reports-page-feedback]");
      try {
        await triggerV2ReportGenerate("weekly", true);
        if (feedback) feedback.textContent = lang() === "zh" ? "周报任务已触发。" : "Weekly generation triggered.";
        await loadReportsPage();
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
    reportsPage.querySelector("[data-reports-page-form]")?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const feedback = reportsPage.querySelector("[data-reports-page-feedback]");
      const selectedReportId = appState.workMgmt.selectedReportId;
      if (!selectedReportId) {
        if (feedback) feedback.textContent = lang() === "zh" ? "请先从左侧选择报告。" : "Please select a report first.";
        return;
      }
      const formData = new FormData(event.currentTarget);
      const comment = String(formData.get("comment") || "").trim();
      const status = String(formData.get("status") || "generated").trim();
      try {
        if (comment) await addV2ReportComment(selectedReportId, comment);
        await updateV2ReportStatus(selectedReportId, status);
        if (feedback) feedback.textContent = lang() === "zh" ? "已保存。" : "Saved.";
        event.currentTarget.querySelector("textarea[name='comment']").value = "";
        await loadReportsPage();
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
  }
  const aiAgentPage = document.getElementById("ai-agent");
  if (aiAgentPage && aiAgentPage.dataset.bound !== "1") {
    aiAgentPage.dataset.bound = "1";
    aiAgentPage.querySelector("[data-ai-agent-refresh]")?.addEventListener("click", () => loadAiAgentHubPage().catch(() => {}));
    aiAgentPage.querySelector("[data-ai-agent-open-ai8]")?.addEventListener("click", () => window.open("https://ai8.rcouyi.com/chat", "_blank", "noopener,noreferrer"));
    aiAgentPage.querySelector("[data-ai-agent-embed-expand]")?.addEventListener("click", () => {
      const shell = aiAgentPage.querySelector(".ai-agent-shell");
      const button = aiAgentPage.querySelector("[data-ai-agent-embed-expand]");
      if (!shell || !button) return;
      shell.classList.remove("ai-agent-shell--embed-focus");
      const focusButton = aiAgentPage.querySelector("[data-ai-agent-embed-focus]");
      if (focusButton) focusButton.textContent = lang() === "zh" ? "聚焦模式" : "Focus";
      const expanded = shell.classList.toggle("ai-agent-shell--embed-expanded");
      button.textContent = expanded
        ? (lang() === "zh" ? "恢复默认" : "Restore")
        : (lang() === "zh" ? "超宽模式" : "Expand");
    });
    aiAgentPage.querySelector("[data-ai-agent-embed-focus]")?.addEventListener("click", () => {
      const shell = aiAgentPage.querySelector(".ai-agent-shell");
      const button = aiAgentPage.querySelector("[data-ai-agent-embed-focus]");
      if (!shell || !button) return;
      shell.classList.remove("ai-agent-shell--embed-expanded");
      const expandButton = aiAgentPage.querySelector("[data-ai-agent-embed-expand]");
      if (expandButton) expandButton.textContent = lang() === "zh" ? "超宽模式" : "Expand";
      const focused = shell.classList.toggle("ai-agent-shell--embed-focus");
      button.textContent = focused
        ? (lang() === "zh" ? "退出聚焦" : "Exit Focus")
        : (lang() === "zh" ? "聚焦模式" : "Focus");
    });
    aiAgentPage.querySelector("[data-ai-agent-submit]")?.addEventListener("click", () => submitAiAgentTask().catch((error) => {
      const feedback = aiAgentPage.querySelector("[data-ai-agent-feedback]");
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    }));
    aiAgentPage.querySelector("[data-ai-agent-copy-prompt]")?.addEventListener("click", async () => {
      const packet = aiAgentTaskPacket();
      const feedback = aiAgentPage.querySelector("[data-ai-agent-feedback]");
      try {
        await navigator.clipboard.writeText(packet);
        if (feedback) feedback.textContent = lang() === "zh" ? "任务包已复制，可粘贴到 AI8。" : "Task packet copied. Paste it into AI8.";
      } catch {
        if (feedback) feedback.textContent = packet;
      }
    });
	    aiAgentPage.querySelector("[data-ai-agent-save-result]")?.addEventListener("click", async () => {
	      const resultNode = aiAgentPage.querySelector("[data-ai-agent-result]");
	      const text = String(resultNode?.innerText || "").trim();
	      const feedback = aiAgentPage.querySelector("[data-ai-agent-feedback]");
	      const outputState = String(aiAgentPage.querySelector("[data-ai-agent-output-state]")?.value || "pending_review");
	      try {
	        await saveAiAgentMemory(`[AI_OUTPUT_STATE:${outputState}]\n${text}`);
	        if (feedback) feedback.textContent = lang() === "zh" ? `AI Agent 结果已按“${outputState}”状态保存到 Hermes 记忆。` : `AI Agent result saved to Hermes memory as ${outputState}.`;
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
  }
  const fileCenterPage = document.getElementById("file-center");
  if (fileCenterPage && fileCenterPage.dataset.bound !== "1") {
    fileCenterPage.dataset.bound = "1";
    fileCenterPage.querySelector("[data-file-center-refresh]")?.addEventListener("click", () => loadFileCenterPage().catch(() => {}));
    fileCenterPage.querySelector("[data-file-center-query]")?.addEventListener("click", () => loadFileCenterPage().catch(() => {}));
    fileCenterPage.querySelector("[data-file-center-scope]")?.addEventListener("change", () => loadFileCenterPage().catch(() => {}));
    fileCenterPage.querySelector("[data-file-center-generate-daily]")?.addEventListener("click", async () => {
      const feedback = fileCenterPage.querySelector("[data-file-center-feedback]");
      try {
        await triggerV2FileCenterDailyDigest("", true);
        if (feedback) feedback.textContent = lang() === "zh" ? "文件中心日报已生成。" : "File center daily digest generated.";
        await loadFileCenterPage();
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
    fileCenterPage.querySelector("[data-file-center-create]")?.addEventListener("click", async () => {
      const feedback = fileCenterPage.querySelector("[data-file-center-feedback]");
      const input = fileCenterPage.querySelector("[data-file-center-upload]");
      const file = input?.files?.[0];
      const title = String(fileCenterPage.querySelector("[data-file-center-title]")?.value || "").trim();
      const category = String(fileCenterPage.querySelector("[data-file-center-category]")?.value || "general").trim() || "general";
      if (!file || !title) {
        if (feedback) feedback.textContent = lang() === "zh" ? "请填写标题并选择文件。" : "Please provide title and file.";
        return;
      }
      try {
        const base64 = await fileToBase64(file);
        await createV2FileCenterRecord({
          title,
          category,
          filename: file.name,
          mime: file.type || "application/octet-stream",
          base64,
          workspace_id: String(fileCenterPage.querySelector("[data-file-center-workspace]")?.value || "finance").trim() || "finance",
        });
        if (feedback) feedback.textContent = lang() === "zh" ? "文件已入库。" : "File uploaded.";
        if (input) input.value = "";
        await loadFileCenterPage();
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
    fileCenterPage.querySelector("[data-file-center-add-version]")?.addEventListener("click", async () => {
      await openFileCenterVersionPanel();
    });
    fileCenterPage.querySelector("[data-file-center-start-workflow]")?.addEventListener("click", async () => {
      await openFileCenterWorkflowPanel("full");
    });
    fileCenterPage.querySelector("[data-file-center-start-review]")?.addEventListener("click", async () => openFileCenterWorkflowPanel("review"));
    fileCenterPage.querySelector("[data-file-center-start-approval]")?.addEventListener("click", async () => openFileCenterWorkflowPanel("approval"));
    fileCenterPage.querySelector("[data-file-center-start-sign]")?.addEventListener("click", async () => openFileCenterWorkflowPanel("sign"));
    fileCenterPage.querySelector("[data-file-center-archive]")?.addEventListener("click", async () => {
      const feedback = fileCenterPage.querySelector("[data-file-center-feedback]");
      const fileId = appState.workMgmt.selectedFileId;
      if (!fileId) {
        if (feedback) feedback.textContent = lang() === "zh" ? "请先从左侧选择文件。" : "Select a file first.";
        return;
      }
      try {
        await archiveV2FileCenterFile(fileId, lang() === "zh" ? "手动归档" : "manual archive");
        if (feedback) feedback.textContent = lang() === "zh" ? "文件已签字归档并生成验签记录。" : "File signed, archived, and verification record created.";
        await loadFileCenterPage();
        await refreshSelectedFileCenterDetail();
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
    fileCenterPage.querySelector("[data-file-center-cross-check]")?.addEventListener("click", () => setActivePage("governance-center", true));
    fileCenterPage.querySelector("[data-file-center-open-governance]")?.addEventListener("click", () => setActivePage("governance-center", true));
    fileCenterPage.querySelector("[data-file-center-open-docflow]")?.addEventListener("click", () => setActivePage("doc-flow", true));
    fileCenterPage.addEventListener("click", async (event) => {
      const gateButton = event.target?.closest?.("[data-file-center-gate-action]");
      if (!gateButton) return;
      const action = String(gateButton.getAttribute("data-file-center-gate-action") || "");
      const feedback = fileCenterPage.querySelector("[data-file-center-feedback]");
      if (action === "approval") {
        await openFileCenterWorkflowPanel("full");
        return;
      }
      if (action === "sign") {
        await openFileCenterWorkflowPanel("sign");
        return;
      }
      if (action === "sblc") {
        navigateToWorkspaceSkill("banking-sblc", true);
        return;
      }
      if (action === "radar" || action === "kyc") {
        setActivePage("governance-center", true);
        return;
      }
      if (action === "export") {
        try {
          await triggerV2FileCenterDailyDigest("", true);
          if (feedback) feedback.textContent = lang() === "zh" ? "审核意见出口已生成文件中心日报。" : "Review opinion export generated as file center digest.";
          await loadFileCenterPage();
        } catch (error) {
          if (feedback) feedback.textContent = authErrorMessage(error.message);
        }
      }
    });
  }
  const governanceCenterPage = document.getElementById("governance-center");
  if (governanceCenterPage && governanceCenterPage.dataset.bound !== "1") {
    governanceCenterPage.dataset.bound = "1";
    governanceCenterPage.querySelector("[data-governance-center-refresh]")?.addEventListener("click", () => loadGovernanceCenterPage().catch(() => {}));
    governanceCenterPage.querySelector("[data-governance-open-files]")?.addEventListener("click", () => setActivePage("file-center", true));
    governanceCenterPage.querySelector("[data-governance-open-reports]")?.addEventListener("click", () => setActivePage("reports", true));
    governanceCenterPage.querySelector("[data-governance-open-workbench]")?.addEventListener("click", () => setActivePage("workbench", true));
  }
  const intelCenterPage = document.getElementById("intel-center");
  if (intelCenterPage && intelCenterPage.dataset.bound !== "1") {
    intelCenterPage.dataset.bound = "1";
    const refresh = () => loadIntelligenceCenterPage().catch(() => {});
    const localFilterRefresh = () => {
      // Keep filter interactions instant; avoid full network reload for every menu click.
      rerenderIntelNewsSurface(intelCenterPage);
    };
    const refreshBtn = intelCenterPage.querySelector("[data-intel-refresh]");
    const refreshMarketBtn = intelCenterPage.querySelector("[data-intel-refresh-market]");
    const refreshNewsBtn = intelCenterPage.querySelector("[data-intel-refresh-news]");
    const refreshDigestBtn = intelCenterPage.querySelector("[data-intel-generate-digest]");
    const loadCandleBtn = intelCenterPage.querySelector("[data-intel-load-candle]");
    intelCenterPage.querySelector("[data-intel-refresh]")?.addEventListener("click", async () => {
      await runIntelAction(intelCenterPage, refreshBtn, async () => {
        await loadIntelligenceCenterPage({ clearFeedback: false });
      }, {
        loading: lang() === "zh" ? "正在刷新数据中心..." : "Refreshing data center...",
        success: lang() === "zh" ? "数据中心已刷新。" : "Data center refreshed.",
      });
    });
    intelCenterPage.querySelector("[data-intel-lang]")?.addEventListener("change", refresh);
    intelCenterPage.querySelector("[data-intel-category]")?.addEventListener("change", localFilterRefresh);
    intelCenterPage.querySelector("[data-intel-window]")?.addEventListener("change", refresh);
    intelCenterPage.querySelector("[data-intel-region]")?.addEventListener("change", localFilterRefresh);
    intelCenterPage.querySelector("[data-intel-risk]")?.addEventListener("change", localFilterRefresh);
    intelCenterPage.querySelector("[data-intel-sort]")?.addEventListener("change", localFilterRefresh);
    intelCenterPage.querySelector("[data-intel-news-search]")?.addEventListener("input", () => {
      window.clearTimeout(appState.intel.newsSearchTimer);
      appState.intel.newsSearchTimer = window.setTimeout(() => {
        const newsNode = intelCenterPage.querySelector("[data-intel-news]");
        const items = appState.intel.lastTopNews?.data?.items || appState.intel.lastTopNews?.items || [];
        const filtered = filteredIntelNewsItems(items);
        if (!filtered.find((item) => intelNewsKey(item) === appState.intel.selectedNewsId)) {
          appState.intel.selectedNewsId = filtered.length ? intelNewsKey(filtered[0]) : "";
        }
        if (newsNode) newsNode.innerHTML = renderIntelNews(appState.intel.lastTopNews || {});
        const detailNode = intelCenterPage.querySelector("[data-intel-news-detail]");
        const selected = filtered.find((item) => intelNewsKey(item) === appState.intel.selectedNewsId) || null;
        if (detailNode) detailNode.innerHTML = renderIntelNewsDetailPanel(selected);
        syncIntelSidePanels(intelCenterPage, filtered);
        bindIntelNewsCards(intelCenterPage);
      }, 180);
    });
    intelCenterPage.querySelector("[data-intel-load-candle]")?.addEventListener("click", async () => {
      await runIntelAction(intelCenterPage, loadCandleBtn, async () => {
        await loadIntelCandlePanel();
      }, {
        loading: lang() === "zh" ? "正在加载K线..." : "Loading K-line...",
        success: lang() === "zh" ? "K线已更新。" : "K-line updated.",
      });
    });
    intelCenterPage.querySelector("[data-intel-refresh-market]")?.addEventListener("click", async () => {
      await runIntelAction(intelCenterPage, refreshMarketBtn, async () => {
        const resp = await adminIntelRefreshMarketData({
          instrumentTypes: ["index", "stock", "etf", "forex"],
          refreshQuotes: true,
          refreshCandles: true,
          interval: String(intelCenterPage.querySelector("[data-intel-candle-interval]")?.value || "1d"),
          range: String(intelCenterPage.querySelector("[data-intel-candle-range]")?.value || "6mo"),
          force: true,
        });
        await loadIntelligenceCenterPage({ clearFeedback: false });
        const quotes = resp?.data?.quotes || {};
        const candles = resp?.data?.candles || {};
        const qn = Number(quotes.fetched_count || 0);
        const cn = Number(candles.fetched_count || 0);
        return lang() === "zh"
          ? `行情刷新完成：报价 ${qn}，K线 ${cn}`
          : `Market refresh done: quotes ${qn}, candles ${cn}`;
      }, {
        loading: lang() === "zh" ? "正在刷新行情..." : "Refreshing markets...",
        success: lang() === "zh" ? "行情刷新任务已触发。" : "Market refresh triggered.",
      });
    });
    intelCenterPage.querySelector("[data-intel-refresh-news]")?.addEventListener("click", async () => {
      const window = String(intelCenterPage.querySelector("[data-intel-window]")?.value || "24h");
      await runIntelAction(intelCenterPage, refreshNewsBtn, async () => {
        const resp = await adminIntelRefreshNews([], window);
        const ingestion = resp?.data?.ingestion || {};
        const inserted = Number(ingestion.inserted_count || 0);
        const updated = Number(ingestion.updated_count || 0);
        const actionSummary = lang() === "zh"
          ? `新闻刷新完成：新增 ${inserted}，更新 ${updated}`
          : `News refresh done: +${inserted}, updated ${updated}`;
        await loadIntelligenceCenterPage({ clearFeedback: false });
        return actionSummary;
      }, {
        loading: lang() === "zh" ? "正在刷新新闻..." : "Refreshing news...",
        success: lang() === "zh" ? "新闻刷新任务已触发。" : "News refresh triggered.",
      });
    });
    intelCenterPage.querySelector("[data-intel-generate-digest]")?.addEventListener("click", async () => {
      const locale = String(intelCenterPage.querySelector("[data-intel-lang]")?.value || "zh");
      const window = String(intelCenterPage.querySelector("[data-intel-window]")?.value || "24h");
      await runIntelAction(intelCenterPage, refreshDigestBtn, async () => {
        const resp = await adminIntelGenerateDigest(window, [locale], 30, true);
        const selected = Number(resp?.data?.selected_count || 0);
        const actionSummary = lang() === "zh"
          ? `Top30 生成完成：已选 ${selected} 条`
          : `Top30 generation done: selected ${selected}`;
        await loadIntelligenceCenterPage({ clearFeedback: false });
        return actionSummary;
      }, {
        loading: lang() === "zh" ? "正在生成 Top30..." : "Generating Top 30...",
        success: lang() === "zh" ? "Top30 生成任务已触发。" : "Top30 generation triggered.",
      });
    });
  }
}

function workbenchToneState(tone) {
  const value = String(tone || "").toLowerCase();
  if (value === "error" || value === "risk") return "error";
  if (value === "warning" || value === "attention") return "warning";
  if (value === "success" || value === "healthy") return "success";
  return "neutral";
}

function renderWorkbenchDecisionStrip(payload) {
  const items = Array.isArray(payload?.management_decision_strip) ? payload.management_decision_strip : [];
  if (!items.length) {
    return `<div class="auth-note">${lang() === "zh" ? "暂无管理层决策摘要。" : "No executive decision summary yet."}</div>`;
  }
  return items.map((item) => `
    <article class="workbench-decision-card workbench-decision-card--${escapeHtml(workbenchToneState(item.tone))}">
      <span>${escapeHtml(item.label || "-")}</span>
      <strong>${escapeHtml(String(item.value ?? 0))}</strong>
      <em>${escapeHtml(item.next_action || "")}</em>
    </article>
  `).join("");
}

function renderWorkbenchWarRoom(payload) {
  const summary = payload?.war_room_summary || {};
  const items = Array.isArray(payload?.war_room_items) ? payload.war_room_items : [];
  const summaryCards = [
    [lang() === "zh" ? "可见项目" : "Visible Projects", summary.visible_projects ?? payload?.count ?? 0],
    [lang() === "zh" ? "未完成任务" : "Open Tasks", summary.open_tasks ?? 0],
    [lang() === "zh" ? "超期任务" : "Overdue Tasks", summary.overdue_tasks ?? 0],
    [lang() === "zh" ? "高风险事项" : "High Risk Items", summary.high_risk_items ?? 0],
  ];
  const rows = items.map((project) => {
    const risk = Number(project.high_risk_items || 0);
    const overdue = Number(project.overdue_tasks || 0);
    const signatureAttention = Number(project.signature_attention || 0);
    const state = signatureAttention || risk ? "error" : overdue ? "warning" : "success";
    return `
      <tr>
        <td>
          <strong>${escapeHtml(project.name || project.id || "-")}</strong>
          <span>${escapeHtml(project.owner_id || "-")} · ${escapeHtml(unifiedStatusLabel(project.status || "-"))}</span>
        </td>
        <td>${escapeHtml(String(project.open_tasks || 0))}</td>
        <td>${escapeHtml(String(project.pending_approvals || 0))}</td>
        <td>${escapeHtml(String(project.files || 0))} / ${escapeHtml(String(project.signed_locked_files || 0))}</td>
        <td>${escapeHtml(String(risk))} / ${escapeHtml(String(overdue))}</td>
        <td>${renderStatusBadge(signatureAttention ? (lang() === "zh" ? "验签关注" : "Signature Attention") : unifiedStatusLabel(state), state)}</td>
        <td>
          <span>${escapeHtml(project.next_action || "-")}</span>
          <button class="btn btn-ghost btn-mini" type="button" data-open-project-chat-summary="${escapeHtml(project.id || "")}">
            ${lang() === "zh" ? "证据/沟通" : "Evidence/Chat"}
          </button>
        </td>
      </tr>
    `;
  }).join("");
  return `
    <section class="workbench-work-card">
      <div class="workbench-card-head">
        <div>
          <span>${lang() === "zh" ? "Primary Work Area" : "Primary Work Area"}</span>
          <h3>${lang() === "zh" ? "项目 / 交易 War Room" : "Project / Deal War Room"}</h3>
        </div>
        <em>${lang() === "zh" ? "发现问题 → 查看依据 → 执行动作" : "Issue → Evidence → Action"}</em>
      </div>
      <div class="workbench-metric-strip">
        ${summaryCards.map(([label, value]) => `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(String(value || 0))}</strong></div>`).join("")}
      </div>
      <div class="workbench-table-wrap">
        <table class="workbench-war-table">
          <thead>
            <tr>
              <th>${lang() === "zh" ? "项目 / 负责人" : "Project / Owner"}</th>
              <th>${lang() === "zh" ? "任务" : "Tasks"}</th>
              <th>${lang() === "zh" ? "审批" : "Approvals"}</th>
              <th>${lang() === "zh" ? "文件/锁定" : "Files/Locked"}</th>
              <th>${lang() === "zh" ? "风险/超期" : "Risk/Overdue"}</th>
              <th>${lang() === "zh" ? "状态" : "State"}</th>
              <th>${lang() === "zh" ? "下一步" : "Next Action"}</th>
            </tr>
          </thead>
          <tbody>${rows || `<tr><td colspan="7">${workMgmtCopy().noData}</td></tr>`}</tbody>
        </table>
      </div>
    </section>
  `;
}

function renderWorkbenchSecondaryPanel(payload) {
  const control = payload?.deal_document_control || {};
  const ai = payload?.ai_output_control || {};
  const stages = Array.isArray(ai.policy) ? ai.policy : [];
  const controlCards = [
    [lang() === "zh" ? "文件总量" : "Total Files", control.total_files || 0],
    [lang() === "zh" ? "待处理步骤" : "Pending Steps", control.pending_file_steps || 0],
    [lang() === "zh" ? "签字锁定" : "Signed Locked", control.signed_locked || 0],
    [lang() === "zh" ? "验签关注" : "Signature Attention", control.signature_attention || 0],
  ];
  const aiCards = [
    [lang() === "zh" ? "AI 草稿" : "AI Draft", ai.draft || 0],
    [lang() === "zh" ? "待复核" : "Pending Review", ai.pending_review || 0],
    [lang() === "zh" ? "已采用" : "Adopted", ai.adopted || 0],
    [lang() === "zh" ? "已驳回" : "Rejected", ai.rejected || 0],
  ];
  return `
    <section class="workbench-side-card">
      <div class="workbench-card-head">
        <div>
          <span>${lang() === "zh" ? "Deal Document Control" : "Deal Document Control"}</span>
          <h3>${lang() === "zh" ? "交易文件控制" : "Deal Document Control"}</h3>
        </div>
      </div>
      <div class="workbench-side-grid">
        ${controlCards.map(([label, value]) => `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(String(value))}</strong></div>`).join("")}
      </div>
      <div class="workbench-process-ladder">
        <span>${lang() === "zh" ? "KYC/AML 上传审核" : "KYC/AML upload review"}</span>
        <span>${lang() === "zh" ? "SPA / SBLC 模板交叉检查" : "SPA / SBLC template cross-check"}</span>
        <span>${lang() === "zh" ? "MT799 / MT760 / 托管文件验签" : "MT799 / MT760 / escrow verification"}</span>
      </div>
      <button class="btn btn-ghost" type="button" onclick="setActivePage('file-center', true)">${lang() === "zh" ? "进入文件控制中心" : "Open File Control"}</button>
    </section>
    <section class="workbench-side-card">
      <div class="workbench-card-head">
        <div>
          <span>${lang() === "zh" ? "AI Output Governance" : "AI Output Governance"}</span>
          <h3>${lang() === "zh" ? "AI 输出正式流转" : "AI Output Workflow"}</h3>
        </div>
      </div>
      <div class="workbench-side-grid">
        ${aiCards.map(([label, value]) => `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(String(value))}</strong></div>`).join("")}
      </div>
      <div class="workbench-policy-list">
        ${stages.map((stage) => `
          <div>
            <strong>${escapeHtml(stage.label || stage.stage || "-")}</strong>
            <span>${escapeHtml(stage.next_action || "")}</span>
          </div>
        `).join("")}
      </div>
    </section>
    <section class="workbench-side-card workbench-side-card--quiet">
      <strong>${lang() === "zh" ? "三步闭环标准" : "Three-Step Closure"}</strong>
      <p>${lang() === "zh" ? "每个页面都按：发现问题、查看依据、执行动作组织。详情下沉到抽屉/面板，首屏只保留管理层需要的主结论。" : "Every page follows issue, evidence, action. Details move into panels; the first screen keeps management conclusions."}</p>
    </section>
  `;
}

function renderWorkbenchEvidenceChain(payload) {
  const rows = Array.isArray(payload?.evidence_chain) ? payload.evidence_chain : [];
  return `
    <div class="workbench-card-head">
      <div>
        <span>${lang() === "zh" ? "State / Audit Layer" : "State / Audit Layer"}</span>
        <h3>${lang() === "zh" ? "可追责证据链" : "Traceable Evidence Chain"}</h3>
      </div>
      <em>${lang() === "zh" ? "谁看过、谁改过、谁导出、AI 输出了什么，都要能回放。" : "Views, changes, exports, and AI outputs must be replayable."}</em>
    </div>
    <div class="workbench-evidence-list">
      ${rows.length ? rows.map((row) => `
        <article>
          <div>
            <strong>${escapeHtml(row.event || "-")}</strong>
            <span>${escapeHtml(row.actor || "system")} · ${escapeHtml(row.entity_type || "-")} · ${escapeHtml(row.target || "-")}</span>
          </div>
          <em>${escapeHtml(formatDateTime(row.ts || 0))}</em>
        </article>
      `).join("") : `<div class="auth-note">${lang() === "zh" ? "暂无审计事件。后续文件、审批、AI 输出操作会进入这里。" : "No audit events yet. File, approval, and AI-output activity will appear here."}</div>`}
    </div>
  `;
}

async function loadAi8AgentStatus() {
  const resp = await fetch("/api/ai-agent/ai8/status", { cache: "no-store" });
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "ai8_status_failed");
  appState.aiAgent.status = payload;
  appState.aiAgent.state = "ready";
  return payload;
}

function renderAiAgentStatus(payload = appState.aiAgent.status) {
  const zh = lang() === "zh";
  const connected = !!payload?.reachable;
  const apiReady = !!payload?.api_ready;
  const mode = apiReady ? "api" : connected ? "handoff" : "offline";
  return `
    <div class="ai-agent-status-strip">
      <div><span>${zh ? "AI8 页面" : "AI8 Page"}</span>${renderStatusBadge(connected ? (zh ? "可访问" : "Reachable") : (zh ? "不可访问" : "Offline"), connected ? "success" : "error")}</div>
      <div><span>${zh ? "后端直连" : "Backend API"}</span>${renderStatusBadge(apiReady ? (zh ? "已配置" : "Configured") : (zh ? "仅中转" : "Handoff only"), apiReady ? "success" : "warning")}</div>
      <div><span>${zh ? "推荐模式" : "Recommended mode"}</span><strong>${escapeHtml(mode === "api" ? (zh ? "API 直连" : "Direct API") : mode === "handoff" ? (zh ? "任务中转" : "Task handoff") : (zh ? "离线待恢复" : "Offline"))}</strong></div>
      <div><span>${zh ? "目标" : "Target"}</span><strong>${escapeHtml(payload?.title || "欧亿AI-8.0 Pro")}</strong></div>
    </div>
  `;
}

function aiAgentTaskPacket() {
  const page = document.getElementById("ai-agent");
  const title = String(page?.querySelector("[data-ai-agent-title]")?.value || "").trim() || (lang() === "zh" ? "AI8 外部 Agent 协作任务" : "AI8 External Agent Task");
  const prompt = String(page?.querySelector("[data-ai-agent-prompt]")?.value || "").trim();
  const target = String(page?.querySelector("[data-ai-agent-target]")?.value || "hermes-memory").trim();
  const zh = lang() === "zh";
  return [
    `# ${title}`,
    "",
    zh ? "你是接入 FASTONE Hermes 工作平台的外部 AI Agent。请输出可直接进入金融机构内部工作流的专业结果。" : "You are an external AI agent connected to FASTONE Hermes. Produce a professional result ready for an institutional finance workflow.",
    "",
    zh ? "## 任务" : "## Task",
    prompt || (zh ? "请先确认任务内容。" : "Please confirm the task content first."),
    "",
    zh ? "## 输出要求" : "## Output Requirements",
    zh ? "- 结论先行，避免 AI 痕迹和模板腔。" : "- Lead with conclusions and avoid AI-like boilerplate.",
    zh ? "- 区分事实、判断、风险、下一步动作。" : "- Separate facts, judgment, risks, and next actions.",
    zh ? "- 若涉及文件/交易/客户，列出需要回填 Hermes 的字段。" : "- If files/deals/clients are involved, list fields to return to Hermes.",
    zh ? `- 结果去向：${target}。` : `- Return target: ${target}.`,
  ].join("\n");
}

async function submitAiAgentTask() {
  const page = document.getElementById("ai-agent");
  const feedback = page?.querySelector("[data-ai-agent-feedback]");
  const resultNode = page?.querySelector("[data-ai-agent-result]");
  const title = String(page?.querySelector("[data-ai-agent-title]")?.value || "").trim();
  const prompt = String(page?.querySelector("[data-ai-agent-prompt]")?.value || "").trim();
  const mode = String(page?.querySelector("[data-ai-agent-mode]")?.value || "auto").trim();
  const target = String(page?.querySelector("[data-ai-agent-target]")?.value || "hermes-memory").trim();
  if (!prompt) {
    if (feedback) feedback.textContent = lang() === "zh" ? "请先输入要交给 AI8 Agent 的任务。" : "Please enter the task for AI8 first.";
    return;
  }
  if (feedback) feedback.textContent = lang() === "zh" ? "正在创建 AI8 任务中转记录..." : "Creating AI8 task handoff record...";
  if (resultNode) resultNode.innerHTML = renderLoadingSkeleton(3);
  const resp = await fetch("/api/ai-agent/ai8/handoff", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, prompt, mode, target, packet: aiAgentTaskPacket(), lang: lang() }),
  });
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "ai8_handoff_failed");
  appState.aiAgent.lastTask = payload;
  if (feedback) {
    feedback.textContent = payload.direct_api_used
      ? (lang() === "zh" ? "AI8 API 已返回结果，并写入审计记录。" : "AI8 API returned a result and audit record was written.")
      : (lang() === "zh" ? "已生成任务包。请打开 AI8 执行，完成后把结果粘贴回来保存。" : "Task packet created. Open AI8, run it, then paste the result back and save.");
  }
  if (resultNode) {
    resultNode.innerHTML = `
      <div class="ai-agent-result__head">
        <strong>${escapeHtml(payload.task?.title || title || "AI8 Task")}</strong>
        ${renderStatusBadge(payload.direct_api_used ? (lang() === "zh" ? "API 结果" : "API Result") : (lang() === "zh" ? "任务中转" : "Handoff"), payload.direct_api_used ? "success" : "warning")}
      </div>
      <label class="auth-field">
        <span>${lang() === "zh" ? "AI8 任务包 / 返回内容" : "AI8 task packet / returned output"}</span>
        <textarea data-ai-agent-return-text>${escapeHtml(payload.result || payload.packet || aiAgentTaskPacket())}</textarea>
      </label>
      <div class="ai-agent-return-actions">
        <a class="btn btn-primary" href="${escapeHtml(payload.open_url || "https://ai8.rcouyi.com/chat")}" target="_blank" rel="noopener noreferrer">${lang() === "zh" ? "在 AI8 执行" : "Run in AI8"}</a>
        <button class="btn btn-ghost" type="button" data-ai-agent-adopt-return>${lang() === "zh" ? "采用上方结果" : "Adopt above output"}</button>
      </div>
    `;
    resultNode.querySelector("[data-ai-agent-adopt-return]")?.addEventListener("click", () => {
      const text = String(resultNode.querySelector("[data-ai-agent-return-text]")?.value || "").trim();
      resultNode.dataset.adoptedText = text;
      if (feedback) feedback.textContent = lang() === "zh" ? "已标记为待保存结果。" : "Marked as result ready to save.";
    });
  }
}

async function saveAiAgentMemory(fallbackText = "") {
  const page = document.getElementById("ai-agent");
  const resultNode = page?.querySelector("[data-ai-agent-result]");
  const returnText = String(resultNode?.querySelector("[data-ai-agent-return-text]")?.value || resultNode?.dataset.adoptedText || fallbackText || "").trim();
  const prompt = String(page?.querySelector("[data-ai-agent-prompt]")?.value || "").trim();
  const target = String(page?.querySelector("[data-ai-agent-target]")?.value || "hermes-memory").trim();
  const resp = await fetch("/api/ai-agent/memory", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      workspace: "home",
      skill_id: "external-ai8-agent",
      target,
      prompt,
      result: returnText || (lang() === "zh" ? "AI8 外部 Agent 已接入 Hermes；当前记录为接入原则和任务中转能力。" : "AI8 external agent is connected to Hermes; this record captures bridge principles and task handoff capability."),
      status: "pending_review",
    }),
  });
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "memory_save_failed");
  return payload;
}

async function loadAiAgentHubPage() {
  ensureWorkMgmtPagesShell();
  const page = document.getElementById("ai-agent");
  if (!page) return;
  const statusNode = page.querySelector("[data-ai-agent-status]");
  if (statusNode) statusNode.innerHTML = renderLoadingSkeleton(1);
  try {
    const payload = await loadAi8AgentStatus();
    if (statusNode) statusNode.innerHTML = renderAiAgentStatus(payload);
  } catch (error) {
    appState.aiAgent.state = "error";
    if (statusNode) {
      statusNode.innerHTML = `<div class="ai-agent-status-strip"><div><span>${lang() === "zh" ? "AI8 页面" : "AI8 Page"}</span>${renderStatusBadge(lang() === "zh" ? "待恢复" : "Unavailable", "warning")}</div><div><strong>${escapeHtml(authErrorMessage(error.message))}</strong></div></div>`;
    }
  }
}

async function loadWorkbenchPage(searchQ = "") {
  ensureWorkMgmtPagesShell();
  const page = document.getElementById("workbench");
  if (!page) return;
  const summaryHost = page.querySelector("[data-workbench-page-summary]");
  const resultsHost = page.querySelector("[data-workbench-page-results]");
  const decisionHost = page.querySelector("[data-workbench-decision-strip]");
  const primaryHost = page.querySelector("[data-workbench-primary-work]");
  const secondaryHost = page.querySelector("[data-workbench-secondary-panel]");
  const evidenceHost = page.querySelector("[data-workbench-evidence-chain]");
  const osHost = page.querySelector("[data-workbench-operating-system]");
  const q = String(searchQ || page.querySelector("[data-workbench-page-search]")?.value || "").trim();
  try {
    const payload = await loadV2Workbench(`scope=my${q ? `&q=${encodeURIComponent(q)}` : ""}`);
    if (osHost) osHost.innerHTML = renderInstitutionalOperatingSystemLayer({ workbench: payload, myWork: {}, governance: appState.governance.data || {}, status: appState.status || {} });
    if (decisionHost) decisionHost.innerHTML = renderWorkbenchDecisionStrip(payload);
    if (summaryHost) {
      summaryHost.innerHTML = `
        <div class="summary-item"><span>${workMgmtCopy().myPending}</span><strong>${escapeHtml(String(payload.quick_views?.my_pending_items || 0))}</strong></div>
        <div class="summary-item"><span>${lang() === "zh" ? "待审批" : "Pending Approvals"}</span><strong>${escapeHtml(String(payload.quick_views?.pending_approvals || 0))}</strong></div>
        <div class="summary-item"><span>${workMgmtCopy().overdue}</span><strong>${escapeHtml(String(payload.quick_views?.overdue_tasks || 0))}</strong></div>
        <div class="summary-item"><span>${workMgmtCopy().risk}</span><strong>${escapeHtml(String(payload.quick_views?.high_risk_projects || 0))}</strong></div>
      `;
    }
    if (primaryHost) {
      primaryHost.innerHTML = renderWorkbenchWarRoom(payload);
      bindProjectChatSummaryButtons(primaryHost);
    }
    if (secondaryHost) secondaryHost.innerHTML = renderWorkbenchSecondaryPanel(payload);
    if (evidenceHost) evidenceHost.innerHTML = renderWorkbenchEvidenceChain(payload);
    if (resultsHost) {
      resultsHost.innerHTML = "";
    }
  } catch (error) {
    const message = `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`;
    if (primaryHost) primaryHost.innerHTML = message;
    if (resultsHost) resultsHost.innerHTML = message;
  }
}

async function loadMyWorkPage() {
  ensureWorkMgmtPagesShell();
  const page = document.getElementById("my-work");
  if (!page) return;
  const host = page.querySelector("[data-mywork-page-body]");
  try {
    const payload = await loadV2MyWork();
    if (host) host.innerHTML = renderMyWorkCards(payload);
  } catch (error) {
    if (host) host.innerHTML = `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`;
  }
}

function bindReportsPageListHandlers() {
  const page = document.getElementById("reports");
  if (!page) return;
  const detailHost = page.querySelector("[data-reports-page-detail]");
  const form = page.querySelector("[data-reports-page-form]");
  page.querySelectorAll("[data-report-id]").forEach((node) => {
    node.addEventListener("click", async () => {
      const reportId = node.getAttribute("data-report-id") || "";
      appState.workMgmt.selectedReportId = reportId;
      try {
        const payload = await loadV2ReportDetail(reportId);
        if (detailHost) detailHost.innerHTML = renderReportDetailCard(payload.report);
        if (form) form.querySelector("select[name='status']").value = payload.report?.status || "generated";
      } catch (error) {
        if (detailHost) detailHost.innerHTML = `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`;
      }
    });
  });
}

async function loadReportsPage() {
  ensureWorkMgmtPagesShell();
  const page = document.getElementById("reports");
  if (!page) return;
  const type = String(page.querySelector("[data-reports-page-type]")?.value || "").trim();
  const listHost = page.querySelector("[data-reports-page-list]");
  const detailHost = page.querySelector("[data-reports-page-detail]");
  const isAdmin = !!appState.auth.user && appState.auth.user.role === "admin";
  const genDailyBtn = page.querySelector("[data-reports-page-gen-daily]");
  const genWeeklyBtn = page.querySelector("[data-reports-page-gen-weekly]");
  if (genDailyBtn) genDailyBtn.hidden = !isAdmin;
  if (genWeeklyBtn) genWeeklyBtn.hidden = !isAdmin;
  try {
    const payload = await loadV2Reports(type ? `report_type=${encodeURIComponent(type)}` : "");
    if (listHost) listHost.innerHTML = renderReportRows(payload.reports);
    bindReportsPageListHandlers();
    const selected = appState.workMgmt.selectedReportId;
    if (selected && (payload.reports || []).some((item) => item.id === selected)) {
      const detail = await loadV2ReportDetail(selected);
      if (detailHost) detailHost.innerHTML = renderReportDetailCard(detail.report);
    } else if (detailHost) {
      detailHost.innerHTML = lang() === "zh" ? "请选择报告查看详情。" : "Select a report to view details.";
    }
  } catch (error) {
    if (listHost) listHost.innerHTML = `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`;
  }
}

function renderFileCenterRows(files) {
  const rows = Array.isArray(files) ? files : [];
  if (!rows.length) return `<div class="auth-note">${lang() === "zh" ? "暂无文件。" : "No files found."}</div>`;
  return rows.map((item) => `
    <button class="work-chat-item" type="button" data-file-id="${escapeHtml(item.id)}">
      <div class="work-chat-item__head">
        <div>
          <strong>${escapeHtml(item.title || item.id)}</strong>
          <span>${escapeHtml(item.workspace_id || "-")} · ${escapeHtml(item.category || "general")} · ${escapeHtml(unifiedStatusLabel(item.status || "draft"))}</span>
          <small>${escapeHtml(item.owner_user_id || "-")} · ${escapeHtml(formatDateTime(item.updated_at))}</small>
        </div>
      </div>
    </button>
  `).join("");
}

function renderFileCenterSummary(payload) {
  const totals = payload?.totals || {};
  return `
    <div class="summary-item"><span>${lang() === "zh" ? "文件总量" : "Files"}</span><strong>${escapeHtml(String(totals.files || 0))}</strong></div>
    <div class="summary-item"><span>${lang() === "zh" ? "待处理步骤" : "Pending Steps"}</span><strong>${escapeHtml(String(totals.pending_steps || totals.my_pending_steps || 0))}</strong></div>
    <div class="summary-item"><span>${lang() === "zh" ? "签字锁定" : "Signed Locked"}</span><strong>${escapeHtml(String(totals.signed_locked || totals.signed_locked_files || 0))}</strong></div>
    <div class="summary-item"><span>${lang() === "zh" ? "超期项" : "Overdue"}</span><strong>${escapeHtml(String(totals.overdue_pending || totals.overdue_steps || 0))}</strong></div>
  `;
}

function renderFileCenterDealControl(payload) {
  const totals = payload?.totals || {};
  const pending = Number(totals.pending_steps || totals.my_pending_steps || 0);
  const locked = Number(totals.signed_locked || totals.signed_locked_files || 0);
  const overdue = Number(totals.overdue_pending || totals.overdue_steps || 0);
  const cards = [
    {
      code: "KYC",
      title: lang() === "zh" ? "KYC / AML 材料" : "KYC / AML Pack",
      desc: lang() === "zh" ? "上传、主体字段、UBO、授权签字人与银行函一致性。" : "Upload, entity fields, UBO, authorized signatory, and bank letter consistency.",
      state: pending ? "warning" : "success",
      action: lang() === "zh" ? "补齐资料并交叉检查" : "Complete materials and cross-check",
      actionType: "kyc",
    },
    {
      code: "SPA",
      title: lang() === "zh" ? "合约 / SPA 审核" : "Contract / SPA Review",
      desc: lang() === "zh" ? "合约条款、金额、币种、期限、仲裁与开证保护条款。" : "Terms, amount, currency, term, arbitration, and issuer protections.",
      state: overdue ? "error" : "neutral",
      action: lang() === "zh" ? "发起审阅/审批" : "Start review/approval",
      actionType: "approval",
    },
    {
      code: "SBLC",
      title: lang() === "zh" ? "SBLC / SWIFT 控制" : "SBLC / SWIFT Control",
      desc: lang() === "zh" ? "模板、MT799、MT760、接证银行、开证银行和托管安排核对。" : "Template, MT799, MT760, advising/issuing bank, and escrow alignment.",
      state: pending ? "warning" : "success",
      action: lang() === "zh" ? "进入 Gate Control" : "Open Gate Control",
      actionType: "sblc",
    },
    {
      code: "SIGN",
      title: lang() === "zh" ? "签字 / 验签 / 锁定" : "Sign / Verify / Lock",
      desc: lang() === "zh" ? "签字绑定 SHA-256 摘要；已签版本不可覆盖，只能新增版本。" : "Signatures bind SHA-256; signed versions cannot be overwritten.",
      state: locked ? "success" : "neutral",
      action: lang() === "zh" ? "查看签名记录" : "Review signatures",
      actionType: "sign",
    },
    {
      code: "RADAR",
      title: lang() === "zh" ? "差异雷达" : "Discrepancy Radar",
      desc: lang() === "zh" ? "主体、金额、币种、银行、日期、角色、费用、有效期逐项比对。" : "Compare entity, amount, currency, banks, dates, roles, fees, validity.",
      state: pending || overdue ? "warning" : "success",
      action: lang() === "zh" ? "打开差异检查" : "Open discrepancy check",
      actionType: "radar",
    },
    {
      code: "OUT",
      title: lang() === "zh" ? "审核意见出口" : "Review Opinion Export",
      desc: lang() === "zh" ? "所有审阅、审批、签字、验签和不一致预警形成可导出审核意见。" : "Export review, approval, signing, verification, and discrepancy findings.",
      state: "neutral",
      action: lang() === "zh" ? "生成/查看日报" : "Generate or view digest",
      actionType: "export",
    },
  ];
  return `
    <section class="deal-doc-control-strip">
      <div class="workbench-card-head">
        <div>
          <span>${lang() === "zh" ? "Deal Document Control" : "Deal Document Control"}</span>
          <h3>${lang() === "zh" ? "交易文件全过程监督" : "End-to-End Deal Document Supervision"}</h3>
        </div>
        <em>${lang() === "zh" ? "上传 → 交叉检查 → 审阅审批 → 签字验签 → 归档" : "Upload → Cross-check → Review/Approve → Sign/Verify → Archive"}</em>
      </div>
      <div class="deal-doc-control-grid">
        ${cards.map((card) => `
          <article class="deal-doc-control-card deal-doc-control-card--${escapeHtml(card.state)}">
            <span>${escapeHtml(card.code)}</span>
            <strong>${escapeHtml(card.title)}</strong>
            <p>${escapeHtml(card.desc)}</p>
            <button class="deal-doc-control-action" type="button" data-file-center-gate-action="${escapeHtml(card.actionType)}">${escapeHtml(card.action)}</button>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderFileCenterBars(map, title) {
  const entries = Object.entries(map || {}).sort((a, b) => Number(b[1] || 0) - Number(a[1] || 0)).slice(0, 8);
  if (!entries.length) return "";
  const max = Math.max(...entries.map(([, v]) => Number(v || 0)), 1);
  const rows = entries.map(([name, value]) => {
    const count = Number(value || 0);
    const width = Math.max(6, Math.round((count / max) * 100));
    return `
      <div class="fc-bar-row">
        <span>${escapeHtml(name)}</span>
        <div class="fc-bar-track"><i style="width:${width}%"></i></div>
        <strong>${escapeHtml(String(count))}</strong>
      </div>
    `;
  }).join("");
  return `
    <section class="fc-analytic-card">
      <h4>${escapeHtml(title)}</h4>
      <div class="fc-bar-list">${rows}</div>
    </section>
  `;
}

function renderFileCenterAnalytics(scope, overviewPayload, extra = {}) {
  const statusMap = overviewPayload?.status_counts || {};
  const categoryMap = overviewPayload?.category_counts || {};
  const workspaceMap = {};
  (extra.workspace_breakdown || []).forEach((item) => {
    workspaceMap[String(item.workspace_id || "")] = Number(item.count || 0);
  });
  const dailyReports = Array.isArray(extra.daily_reports) ? extra.daily_reports : [];
  const trendRows = dailyReports.slice(0, 7).map((item) => {
    const c = item.content || {};
    return `
      <div class="fc-trend-row">
        <span>${escapeHtml(item.period_start || "--")}</span>
        <strong>${lang() === "zh" ? "新增" : "New"} ${escapeHtml(String(c.new_files || 0))}</strong>
        <strong>${lang() === "zh" ? "签字" : "Signed"} ${escapeHtml(String(c.signatures_completed || 0))}</strong>
        <strong>${lang() === "zh" ? "超期" : "Overdue"} ${escapeHtml(String(c.overdue_pending_steps || 0))}</strong>
      </div>
    `;
  }).join("");
  return `
    <div class="admin-hero admin-hero--team">
      <div class="admin-hero__brand">
        <div class="admin-hero__logo" aria-hidden="true"></div>
        <div class="admin-hero__copy">
          <span>${lang() === "zh" ? "File Governance Analytics" : "File Governance Analytics"}</span>
          <strong>${scope === "global" ? (lang() === "zh" ? "全局分析视图" : "Global Analytics View") : scope === "workspace" ? (lang() === "zh" ? "工作平台分析视图" : "Workspace Analytics View") : (lang() === "zh" ? "个人分析视图" : "My Analytics View")}</strong>
          <p>${lang() === "zh" ? "通过状态、分类、平台与日报趋势，快速识别瓶颈与异常。": "Spot bottlenecks with status, category, workspace, and daily trend views."}</p>
        </div>
      </div>
    </div>
    <div class="fc-analytics-grid">
      ${renderFileCenterBars(Object.fromEntries(Object.entries(statusMap).map(([k, v]) => [unifiedStatusLabel(k), v])), lang() === "zh" ? "状态分布" : "Status Distribution")}
      ${renderFileCenterBars(categoryMap, lang() === "zh" ? "分类分布" : "Category Distribution")}
      ${renderFileCenterBars(workspaceMap, lang() === "zh" ? "工作平台分布" : "Workspace Distribution")}
      <section class="fc-analytic-card">
        <h4>${lang() === "zh" ? "最近 7 日日报快照" : "Last 7 Daily Digests"}</h4>
        <div class="fc-trend-list">${trendRows || `<div class="auth-note">${lang() === "zh" ? "暂无日报数据。" : "No daily digest data yet."}</div>`}</div>
      </section>
    </div>
  `;
}

function fileCenterSignatureStatusLabel(status) {
  const zh = lang() === "zh";
  const labels = {
    valid: zh ? "验签通过" : "Verified",
    unsigned: zh ? "未签字" : "Unsigned",
    attention: zh ? "需复核" : "Attention",
    tampered: zh ? "疑似篡改" : "Tampered",
    invalid: zh ? "签名无效" : "Invalid",
    certificate_revoked: zh ? "证书已吊销" : "Certificate Revoked",
    certificate_expired: zh ? "证书过期" : "Certificate Expired",
    file_missing: zh ? "文件缺失" : "File Missing",
    version_missing: zh ? "版本缺失" : "Version Missing",
  };
  return labels[status] || status || (zh ? "未知" : "Unknown");
}

function renderFileCenterDetail(detail) {
  const file = detail?.file || detail;
  if (!file) return lang() === "zh" ? "请选择文件查看详情。" : "Select a file to inspect details.";
  const current = file.current_version || {};
  const versions = detail?.versions || [];
  const workflows = detail?.workflows || [];
  const signatures = detail?.signatures || [];
  const signatureSummary = detail?.signature_summary || {};
  const download = file.current_version_id
    ? `/api/v2/file-center/files/${encodeURIComponent(file.id)}/download?version_id=${encodeURIComponent(file.current_version_id)}`
    : "";
  const lockedNotice = file.is_locked
    ? `<div class="auth-note file-center-lock-note">${lang() === "zh" ? "当前版本已完成签字，内容已锁定。如需变更，请创建新版本；旧签字版本会永久保留并可验签。" : "The current signed version is locked. Create a new version for changes; the signed version remains preserved and verifiable."}</div>`
    : "";
  return `
    <article class="doc-flow-detail">
      <h3>${escapeHtml(file.title || file.id)}</h3>
      <div class="tag-row">
        <span class="tag">${escapeHtml(file.workspace_id || "-")}</span>
        <span class="tag">${escapeHtml(file.category || "-")}</span>
        <span class="tag status-tag">${escapeHtml(unifiedStatusLabel(file.status || "-"))}</span>
        <span class="tag">${escapeHtml(file.owner_user_id || "-")}</span>
      </div>
      <p>${lang() === "zh" ? "当前版本" : "Current Version"}: ${escapeHtml(current.filename || "-")} (v${escapeHtml(String(current.version_number || 0))})</p>
      <p>${lang() === "zh" ? "变更说明" : "Change Summary"}: ${escapeHtml(current.change_summary || "-")}</p>
      <p>${lang() === "zh" ? "签字/锁定/加密" : "Sign/Lock/Encrypt"}: ${file.is_signed ? "Y" : "N"} / ${file.is_locked ? "Y" : "N"} / ${file.is_encrypted ? "Y" : "N"}</p>
      ${lockedNotice}
      <div class="file-center-detail-grid">
        <section class="file-center-detail-card">
          <strong>${lang() === "zh" ? "验签状态" : "Signature Verification"}</strong>
          <span class="tag status-tag">${escapeHtml(fileCenterSignatureStatusLabel(signatureSummary.status || "unsigned"))}</span>
          <p>${lang() === "zh" ? "签名记录" : "Signature Records"}: ${Number(signatureSummary.total || 0)} · ${lang() === "zh" ? "异常" : "Exceptions"}: ${Number(signatureSummary.failed || 0)}</p>
          ${signatures.length ? signatures.slice(0, 4).map((sig) => `
            <div class="file-center-mini-row">
              <span>${escapeHtml(sig.signer_id || "-")} · ${escapeHtml(sig.signature_method || "platform")}</span>
              <strong>${escapeHtml(fileCenterSignatureStatusLabel(sig.verify_status))}</strong>
            </div>
          `).join("") : `<div class="auth-note">${lang() === "zh" ? "尚无签名记录。签字归档后会自动生成哈希与签名记录。" : "No signatures yet. Signing and archive will create hash-bound records."}</div>`}
        </section>
        <section class="file-center-detail-card">
          <strong>${lang() === "zh" ? "版本记录" : "Versions"}</strong>
          ${versions.length ? versions.slice(0, 6).map((version) => `
            <div class="file-center-mini-row">
              <span>v${escapeHtml(String(version.version_number || 0))} · ${escapeHtml(version.filename || "-")}</span>
              <strong>${version.is_signed_snapshot ? (lang() === "zh" ? "已锁定" : "Locked") : (lang() === "zh" ? "可流转" : "Active")}</strong>
            </div>
          `).join("") : `<div class="auth-note">${lang() === "zh" ? "暂无版本记录。" : "No version records."}</div>`}
        </section>
        <section class="file-center-detail-card">
          <strong>${lang() === "zh" ? "流程记录" : "Workflow Records"}</strong>
          ${workflows.length ? workflows.slice(0, 5).map((workflow) => `
            <div class="file-center-mini-row">
              <span>${escapeHtml(workflow.title || workflow.workflow_type || "-")} · ${escapeHtml(workflow.routing_mode || "sequential")}</span>
              <strong>${escapeHtml(unifiedStatusLabel(workflow.status || "-"))}</strong>
            </div>
          `).join("") : `<div class="auth-note">${lang() === "zh" ? "尚未发起流程。" : "No workflow started."}</div>`}
        </section>
      </div>
      <div class="work-chat-actions">
        ${download ? `<a class="btn btn-ghost" href="${escapeHtml(download)}" download>${lang() === "zh" ? "下载当前版本" : "Download Current Version"}</a>` : ""}
      </div>
    </article>
  `;
}

async function ensureFileCenterUsersLoaded() {
  if (!(appState.documentFlows.users || []).length) {
    try {
      await loadDocumentFlowUsers();
    } catch (error) {
      const email = appState.auth.user?.email || "";
      appState.documentFlows.users = email ? [{ email, display_name: appState.auth.user?.display_name || appState.auth.user?.username || email, username: appState.auth.user?.username || "" }] : [];
    }
  }
  return appState.documentFlows.users || [];
}

function selectedMultiValues(select) {
  return Array.from(select?.selectedOptions || []).map((option) => String(option.value || "").trim()).filter(Boolean);
}

function fileCenterFeedback(message) {
  const page = document.getElementById("file-center");
  const feedback = page?.querySelector("[data-file-center-feedback]");
  if (feedback) feedback.textContent = message;
}

async function refreshSelectedFileCenterDetail() {
  const page = document.getElementById("file-center");
  const detailNode = page?.querySelector("[data-file-center-detail]");
  const fileId = appState.workMgmt.selectedFileId;
  if (!fileId || !detailNode) return;
  const payload = await loadV2FileCenterDetail(fileId);
  appState.workMgmt.selectedFileDetail = payload;
  detailNode.innerHTML = renderFileCenterDetail(payload);
}

function buildFileCenterWorkflowSteps({ kind, routingMode, reviewers, approvers, signers }) {
  const steps = [];
  let order = 1;
  const appendGroup = (stepType, people) => {
    const unique = Array.from(new Set((people || []).map((item) => String(item || "").trim()).filter(Boolean)));
    unique.forEach((email, index) => {
      steps.push({
        step_type: stepType,
        assigned_user_id: email,
        sequence_order: routingMode === "parallel" ? order : order + index,
      });
    });
    if (unique.length) order += routingMode === "parallel" ? 1 : unique.length;
  };
  if (kind === "review" || kind === "full") appendGroup("review", reviewers);
  if (kind === "approval" || kind === "full") appendGroup("approval", approvers);
  if (kind === "sign" || kind === "full") appendGroup("sign", signers);
  return steps;
}

async function openFileCenterVersionPanel() {
  const page = document.getElementById("file-center");
  const fileId = appState.workMgmt.selectedFileId;
  const input = page?.querySelector("[data-file-center-upload]");
  const file = input?.files?.[0];
  if (!fileId || !file) {
    fileCenterFeedback(lang() === "zh" ? "请先选中文件并选择新版本文件。" : "Select a file and choose a new version file.");
    return;
  }
  const selected = appState.workMgmt.selectedFileDetail?.file || {};
  const panel = ensureOverlayPanel(lang() === "zh" ? "新增文件版本" : "Add File Version", `
    <form class="doc-flow-create-form" data-file-center-version-form>
      <div class="auth-note">${lang() === "zh" ? "已签字锁定的版本不可覆盖。系统会创建新版本并保留旧签字版本用于验签。" : "Signed versions cannot be overwritten. A new version is created while signed versions remain verifiable."}</div>
      <label class="auth-field">
        <span>${lang() === "zh" ? "当前文件" : "Current File"}</span>
        <input type="text" value="${escapeHtml(selected.title || fileId)}" disabled />
      </label>
      <label class="auth-field">
        <span>${lang() === "zh" ? "新版本文件" : "New Version File"}</span>
        <input type="text" value="${escapeHtml(file.name)}" disabled />
      </label>
      <label class="auth-field">
        <span>${lang() === "zh" ? "版本修改说明" : "Change Summary"}</span>
        <textarea name="change_summary" rows="4" required placeholder="${escapeHtml(lang() === "zh" ? "说明修改原因、关键差异、审批依据" : "Explain reason, key differences, and approval basis")}"></textarea>
      </label>
      <div class="auth-feedback" data-file-center-version-feedback></div>
      <div class="doc-flow-actions">
        <button class="btn btn-primary" type="submit">${lang() === "zh" ? "创建新版本" : "Create Version"}</button>
        <button class="btn btn-ghost" type="button" data-overlay-close="1">${lang() === "zh" ? "取消" : "Cancel"}</button>
      </div>
    </form>
  `);
  panel.querySelector("[data-file-center-version-form]")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const feedback = panel.querySelector("[data-file-center-version-feedback]");
    const form = new FormData(event.currentTarget);
    const changeSummary = String(form.get("change_summary") || "").trim();
    if (!changeSummary) {
      if (feedback) feedback.textContent = lang() === "zh" ? "修改说明不能为空。" : "Change summary is required.";
      return;
    }
    try {
      const base64 = await fileToBase64(file);
      await createV2FileCenterVersion(fileId, {
        filename: file.name,
        mime: file.type || "application/octet-stream",
        base64,
        change_summary: changeSummary,
      });
      closeOverlayPanel();
      if (input) input.value = "";
      fileCenterFeedback(lang() === "zh" ? "新版本已创建，旧签字版本已保留。" : "New version created; signed history remains preserved.");
      await loadFileCenterPage();
      await refreshSelectedFileCenterDetail();
    } catch (error) {
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    }
  });
}

async function openFileCenterWorkflowPanel(kind = "full") {
  const fileId = appState.workMgmt.selectedFileId;
  if (!fileId) {
    fileCenterFeedback(lang() === "zh" ? "请先从左侧选择文件。" : "Select a file first.");
    return;
  }
  await ensureFileCenterUsersLoaded();
  const detail = appState.workMgmt.selectedFileDetail || await loadV2FileCenterDetail(fileId);
  appState.workMgmt.selectedFileDetail = detail;
  const file = detail.file || {};
  const current = file.current_version || {};
  const self = appState.auth.user?.email || "";
  const titleMap = {
    review: lang() === "zh" ? "发起审阅流程" : "Start Review",
    approval: lang() === "zh" ? "发起审批流程" : "Start Approval",
    sign: lang() === "zh" ? "发起签字流程" : "Start Signing",
    full: lang() === "zh" ? "发起审阅/审批/签字闭环" : "Start Review/Approve/Sign",
  };
  const showReview = kind === "review" || kind === "full";
  const showApproval = kind === "approval" || kind === "full";
  const showSign = kind === "sign" || kind === "full";
  const panel = ensureOverlayPanel(titleMap[kind] || titleMap.full, `
    <form class="doc-flow-create-form file-center-workflow-form" data-file-center-workflow-form>
      <div class="auth-note">${lang() === "zh" ? "流程按“发现问题 → 查看依据 → 执行动作”闭环。签字会绑定文件 SHA-256 摘要；证书签字会自动生成或使用签名人内部证书。" : "Workflow follows issue, evidence, action. Signing binds SHA-256; certificate signing auto-creates or uses an internal signer certificate."}</div>
      <div class="file-center-detail-grid">
        <label class="auth-field">
          <span>${lang() === "zh" ? "文件" : "File"}</span>
          <input type="text" value="${escapeHtml(file.title || fileId)}" disabled />
        </label>
        <label class="auth-field">
          <span>${lang() === "zh" ? "当前版本" : "Current Version"}</span>
          <input type="text" value="${escapeHtml(current.filename || "-")} · v${escapeHtml(String(current.version_number || 0))}" disabled />
        </label>
      </div>
      <label class="auth-field">
        <span>${lang() === "zh" ? "流程标题" : "Workflow Title"}</span>
        <input name="title" type="text" value="${escapeHtml((file.title || fileId) + " - " + (titleMap[kind] || titleMap.full))}" required />
      </label>
      <div class="file-center-detail-grid">
        <label class="auth-field">
          <span>${lang() === "zh" ? "流转方式" : "Routing Mode"}</span>
          <select name="routing_mode">
            <option value="single">${lang() === "zh" ? "单人/单级" : "Single"}</option>
            <option value="parallel">${lang() === "zh" ? "多人并行" : "Parallel"}</option>
            <option value="sequential" selected>${lang() === "zh" ? "多人顺序" : "Sequential"}</option>
          </select>
        </label>
        <label class="auth-field">
          <span>${lang() === "zh" ? "截止时间" : "Due Date"}</span>
          <input name="due_date" type="datetime-local" />
        </label>
      </div>
      ${showReview ? `<label class="auth-field"><span>${lang() === "zh" ? "审阅人" : "Reviewers"}</span><select name="reviewers" multiple size="5">${documentFlowUserOptions([self])}</select></label>` : ""}
      ${showApproval ? `<label class="auth-field"><span>${lang() === "zh" ? "审批人" : "Approvers"}</span><select name="approvers" multiple size="5">${documentFlowUserOptions([self])}</select></label>` : ""}
      ${showSign ? `
        <label class="auth-field"><span>${lang() === "zh" ? "签字人" : "Signers"}</span><select name="signers" multiple size="5">${documentFlowUserOptions([self])}</select></label>
        <div class="file-center-detail-grid">
          <label class="auth-field">
            <span>${lang() === "zh" ? "签字方式" : "Signing Method"}</span>
            <select name="signature_method">
              <option value="platform">${lang() === "zh" ? "平台电子签名（账号确认 + 摘要签名）" : "Platform e-signature"}</option>
              <option value="certificate">${lang() === "zh" ? "证书数字签名（内部证书 + 摘要签名）" : "Certificate digital signature"}</option>
              <option value="visual">${lang() === "zh" ? "图片/手写签名（仅视觉展示，安全仍由平台签名保证）" : "Visual signature (display only; secured by platform signature)"}</option>
            </select>
          </label>
          <label class="auth-field">
            <span>${lang() === "zh" ? "签字位置/页码" : "Signature Placement"}</span>
            <input name="signature_placement" type="text" placeholder="${escapeHtml(lang() === "zh" ? "例如：第 12 页右下角 / 附件签署页" : "e.g. page 12 bottom-right / execution page")}" />
          </label>
        </div>
        <label class="auth-checkbox"><input name="lock_after_sign" type="checkbox" checked /> ${lang() === "zh" ? "完成签字后锁定当前版本" : "Lock current version after signing"}</label>
      ` : ""}
      <label class="auth-field">
        <span>${lang() === "zh" ? "附加说明/审核要求" : "Instructions"}</span>
        <textarea name="instructions" rows="4" placeholder="${escapeHtml(lang() === "zh" ? "说明审核重点、签字要求、补充材料要求" : "Review focus, signing requirements, or additional materials")}"></textarea>
      </label>
      <div class="auth-feedback" data-file-center-workflow-feedback></div>
      <div class="doc-flow-actions">
        <button class="btn btn-primary" type="submit">${lang() === "zh" ? "提交流程" : "Submit Workflow"}</button>
        <button class="btn btn-ghost" type="button" data-file-center-generate-cert>${lang() === "zh" ? "为本人生成签名证书" : "Generate My Certificate"}</button>
        <button class="btn btn-ghost" type="button" data-overlay-close="1">${lang() === "zh" ? "取消" : "Cancel"}</button>
      </div>
    </form>
  `);
  panel.querySelector("[data-file-center-generate-cert]")?.addEventListener("click", async () => {
    const feedback = panel.querySelector("[data-file-center-workflow-feedback]");
    try {
      const result = await createV2FileCenterCertificate({ user_id: self });
      if (feedback) feedback.textContent = lang() === "zh" ? `签名证书已生成：${result.certificate?.id || ""}` : `Certificate generated: ${result.certificate?.id || ""}`;
    } catch (error) {
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    }
  });
  panel.querySelector("[data-file-center-workflow-form]")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const feedback = panel.querySelector("[data-file-center-workflow-feedback]");
    const form = new FormData(event.currentTarget);
    const routingMode = String(form.get("routing_mode") || "sequential");
    const reviewers = showReview ? selectedMultiValues(event.currentTarget.querySelector('select[name="reviewers"]')) : [];
    const approvers = showApproval ? selectedMultiValues(event.currentTarget.querySelector('select[name="approvers"]')) : [];
    const signers = showSign ? selectedMultiValues(event.currentTarget.querySelector('select[name="signers"]')) : [];
    const steps = buildFileCenterWorkflowSteps({ kind, routingMode, reviewers, approvers, signers });
    if (!steps.length) {
      if (feedback) feedback.textContent = lang() === "zh" ? "请至少选择一名流程参与人。" : "Select at least one participant.";
      return;
    }
    try {
      await createV2FileCenterWorkflow({
        file_id: fileId,
        workflow_type: kind === "full" ? "review_approve_sign" : kind,
        title: String(form.get("title") || "").trim(),
        routing_mode: routingMode,
        due_date: String(form.get("due_date") || ""),
        instructions: String(form.get("instructions") || "").trim(),
        signature_method: String(form.get("signature_method") || "platform"),
        signature_placement: String(form.get("signature_placement") || "").trim(),
        lock_after_sign: form.get("lock_after_sign") !== null,
        steps,
      });
      closeOverlayPanel();
      fileCenterFeedback(lang() === "zh" ? "流程已发起，待办和审计记录已生成。" : "Workflow started; tasks and audit trail are recorded.");
      await loadFileCenterPage();
      await refreshSelectedFileCenterDetail();
    } catch (error) {
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    }
  });
}

function bindFileCenterListHandlers() {
  const page = document.getElementById("file-center");
  if (!page) return;
  const detail = page.querySelector("[data-file-center-detail]");
  const feedback = page.querySelector("[data-file-center-feedback]");
  page.querySelectorAll("[data-file-id]").forEach((node) => {
    node.addEventListener("click", async () => {
      const fileId = node.getAttribute("data-file-id") || "";
      appState.workMgmt.selectedFileId = fileId;
      try {
        const payload = await loadV2FileCenterDetail(fileId);
        appState.workMgmt.selectedFileDetail = payload;
        if (detail) detail.innerHTML = renderFileCenterDetail(payload);
        page.querySelectorAll("[data-file-id]").forEach((item) => item.classList.remove("active"));
        node.classList.add("active");
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
  });
}

async function loadFileCenterPage() {
  ensureWorkMgmtPagesShell();
  const page = document.getElementById("file-center");
  if (!page) return;
  const scopeSelect = page.querySelector("[data-file-center-scope]");
  const isAdmin = !!appState.auth.user && appState.auth.user.role === "admin";
  if (scopeSelect) {
    const globalOption = scopeSelect.querySelector("option[value='global']");
    if (globalOption) globalOption.hidden = !isAdmin;
    if (!isAdmin && String(scopeSelect.value || "") === "global") scopeSelect.value = "my";
  }
  const scope = String(scopeSelect?.value || "my").trim();
  const workspace = String(page.querySelector("[data-file-center-workspace]")?.value || "").trim();
  const q = String(page.querySelector("[data-file-center-search]")?.value || "").trim();
  const summaryNode = page.querySelector("[data-file-center-summary]");
  const dealControlNode = page.querySelector("[data-file-center-deal-control]");
  const analyticsNode = page.querySelector("[data-file-center-analytics]");
  const listNode = page.querySelector("[data-file-center-list]");
  const detailNode = page.querySelector("[data-file-center-detail]");
  const feedbackNode = page.querySelector("[data-file-center-feedback]");
  try {
    let overview;
    let analyticsOverview = null;
    let analyticsExtra = {};
    if (scope === "my") {
      [overview, analyticsOverview] = await Promise.all([
        loadV2FileCenterMyOverview(),
        loadV2FileCenterOverview("my"),
      ]);
    } else if (scope === "workspace") {
      [overview, analyticsOverview] = await Promise.all([
        loadV2FileCenterWorkspaceOverview(workspace || "finance"),
        loadV2FileCenterOverview("workspace", workspace || "finance"),
      ]);
    } else {
      const [globalOverview, globalStatusOverview, dailyPayload] = await Promise.all([
        loadV2FileCenterGlobalOverview(),
        loadV2FileCenterOverview("global"),
        loadV2FileCenterDailyReports(),
      ]);
      overview = {
        ...globalOverview,
        totals: {
          ...(globalOverview?.totals || {}),
          files: globalOverview?.totals?.files ?? globalStatusOverview?.totals?.files ?? 0,
          pending_steps: globalOverview?.totals?.pending_steps ?? globalStatusOverview?.totals?.pending_steps ?? 0,
          signed_locked: globalOverview?.totals?.signed_locked_files ?? globalStatusOverview?.totals?.signed_locked ?? 0,
          overdue_pending: globalOverview?.totals?.overdue_steps ?? globalStatusOverview?.totals?.overdue_pending ?? 0,
        },
      };
      analyticsOverview = globalStatusOverview;
      analyticsExtra = {
        workspace_breakdown: globalOverview?.workspace_breakdown || [],
        daily_reports: dailyPayload?.reports || [],
      };
    }
    if (summaryNode) summaryNode.innerHTML = renderFileCenterSummary(overview);
    if (dealControlNode) dealControlNode.innerHTML = renderFileCenterDealControl(overview);
    if (analyticsNode) analyticsNode.innerHTML = renderFileCenterAnalytics(scope, analyticsOverview || overview, analyticsExtra);
    const filesPayload = await loadV2FileCenterFiles({ q, ...(workspace ? { workspace_id: workspace } : {}) });
    if (listNode) listNode.innerHTML = renderFileCenterRows(filesPayload.files || []);
    bindFileCenterListHandlers();
    if (detailNode) detailNode.innerHTML = lang() === "zh" ? "请选择文件查看详情。" : "Select a file to inspect details.";
    if (feedbackNode) feedbackNode.textContent = "";
  } catch (error) {
    if (feedbackNode) feedbackNode.textContent = authErrorMessage(error.message);
    if (listNode) listNode.innerHTML = `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`;
  }
}

function renderIntelSummary(brief, topNews) {
  const briefData = brief?.data || brief || {};
  const topNewsData = topNews?.data || topNews || {};
  const nowTs = Math.floor(Date.now() / 1000);
  const marketSnapshot = briefData?.marketSnapshot || topNewsData?.marketSnapshot || {};
  const highlights = Array.isArray(marketSnapshot?.highlights) ? marketSnapshot.highlights : [];
  const topItems = Array.isArray(topNewsData?.items) ? topNewsData.items : Array.isArray(briefData?.topNews) ? briefData.topNews : [];
  const briefDate = firstText(
    briefData?.briefDate,
    topNewsData?.briefDate,
    topNewsData?.generatedAt ? new Date(Number(topNewsData.generatedAt) * 1000).toLocaleDateString(lang() === "zh" ? "zh-CN" : "en-US") : "",
  ) || new Date(nowTs * 1000).toLocaleDateString(lang() === "zh" ? "zh-CN" : "en-US");
  const generatedAt = Number(topNewsData?.generatedAt || briefData?.generatedAt || marketSnapshot?.lastUpdatedAt || nowTs);
  const marketHighlightValue = highlights.length
    ? `${highlights.length}`
    : String(Number(topNewsData?.marketHighlightCount || topNewsData?.market_highlight_count || 0) || 0);
  const topNewsCount = Number(topNewsData?.total || topNewsData?.selected_count || topItems.length || 0);
  return `
    <div class="summary-item"><span>${lang() === "zh" ? "简报日期" : "Brief Date"}</span><strong>${escapeHtml(briefDate)}</strong><em>${lang() === "zh" ? "管理层日简报" : "Executive brief"}</em></div>
    <div class="summary-item"><span>${lang() === "zh" ? "市场高亮" : "Market Highlights"}</span><strong>${escapeHtml(marketHighlightValue)}</strong><em>${lang() === "zh" ? "按波动幅度排序" : "Sorted by move"}</em></div>
    <div class="summary-item"><span>${lang() === "zh" ? "Top 新闻 30" : "Top News 30"}</span><strong>${escapeHtml(String(topNewsCount || 0))}</strong><em>${lang() === "zh" ? "精选情报数量" : "Ranked stories"}</em></div>
    <div class="summary-item"><span>${lang() === "zh" ? "更新时间" : "Updated"}</span><strong>${escapeHtml(formatDateTime(generatedAt))}</strong><em>${lang() === "zh" ? "本地工作台时间" : "Workbench time"}</em></div>
  `;
}

function renderIntelMarkets(overview) {
  const source = overview?.data || overview || {};
  const regions = Array.isArray(source?.regions) ? source.regions : [];
  const rows = [];
  regions.forEach((region) => {
    (region.countries || []).forEach((country) => {
      (country.indices || []).forEach((idx) => rows.push(idx));
    });
  });
  const ordered = rows
    .slice()
    .sort((a, b) => Math.abs(Number(b?.changePercent || 0)) - Math.abs(Number(a?.changePercent || 0)));
  const top = ordered.slice(0, 20).map((idx) => {
    const pct = Number(idx.changePercent || 0);
    const positive = pct >= 0;
    return `
      <article
        class="intel-mini-card intel-mini-card--action"
        role="button"
        tabindex="0"
        data-intel-market-card="1"
        data-symbol="${escapeHtml(String(idx.symbol || idx.indexCode || ""))}"
        data-name="${escapeHtml(String(idx.indexName || idx.indexCode || ""))}"
        data-market-status="${escapeHtml(String(idx.marketStatus || ""))}"
      >
        <div class="intel-mini-card__head">
          <strong>${escapeHtml(idx.indexName || idx.indexCode || "--")}</strong>
          <span class="${positive ? "is-up" : "is-down"}">${positive ? "+" : ""}${escapeHtml(pct.toFixed(2))}%</span>
        </div>
        <div class="intel-mini-card__meta">
          <span>${escapeHtml(idx.symbol || "--")}</span>
          <span>${escapeHtml(idx.currency || "--")}</span>
          <span>${escapeHtml(String(Number(idx.currentValue || 0).toFixed(2)))}</span>
        </div>
        <div class="fc-bar-track"><i style="width:${Math.min(100, Math.max(6, Math.round(Math.abs(pct) * 8)))}%; background:${positive ? "var(--work-ok)" : "var(--work-danger)"}"></i></div>
      </article>
    `;
  }).join("");
  const marketsBody = top || `
    <div class="auth-note">${lang() === "zh" ? "暂无行情数据。" : "No market data."}</div>
  `;
  const freshness = freshnessMeta(source?.lastUpdatedAt || Math.max(0, ...rows.map((row) => Number(row.lastUpdatedAt || 0))));
  return `
    <div class="fc-analytic-card">
      <div class="intel-block-title">
        <strong>${lang() === "zh" ? "全球市场指数快照" : "Global Index Snapshot"}</strong>
        <span>${freshness.ageText} ${renderStatusBadge(freshness.label, freshness.state)}</span>
      </div>
      <div class="intel-card-grid">
        ${marketsBody}
      </div>
    </div>
  `;
}

function intelNewsRiskLevel(item) {
  const score = Number(item?.importanceScore || item?.importance_score || 0);
  if (score >= 88) return "high";
  if (score >= 72) return "medium";
  return "normal";
}

function intelNewsRegion(item) {
  const hay = `${item?.title || ""} ${item?.summary || ""} ${item?.sourceName || ""}`.toLowerCase();
  if (/china|chinese|beijing|hong kong|shanghai|中国|北京|香港|上海/.test(hay)) return "china";
  if (/europe|paris|denmark|uk|britain|germany|france|欧洲|巴黎|丹麦|英国|法国|德国/.test(hay)) return "europe";
  if (/japan|korea|india|asia|iran|kuwait|亚洲|日本|韩国|印度|伊朗|科威特/.test(hay)) return "asia";
  if (/us |u\.s\.|america|white house|nyc|美国|白宫|纽约/.test(` ${hay}`)) return "us";
  return "";
}

function intelNewsTags(item) {
  const risk = intelNewsRiskLevel(item);
  const tags = [
    item?.category || "general",
    intelNewsRegion(item) || (lang() === "zh" ? "全球" : "Global"),
    risk === "high" ? (lang() === "zh" ? "高风险" : "High risk") : risk === "medium" ? (lang() === "zh" ? "中风险" : "Medium risk") : (lang() === "zh" ? "常规" : "Normal"),
  ];
  return tags.filter(Boolean).slice(0, 5);
}

function relatedMarketRowsForNews(item, limit = 4) {
  const source = appState.intel.lastMarketsOverview?.data || appState.intel.lastMarketsOverview || {};
  const regions = Array.isArray(source?.regions) ? source.regions : [];
  const rows = [];
  regions.forEach((region) => {
    (region.countries || []).forEach((country) => {
      (country.indices || []).forEach((idx) => rows.push(idx));
    });
  });
  const category = String(item?.category || "").toLowerCase();
  const preferred = rows.filter((row) => {
    const name = `${row.indexName || ""} ${row.symbol || ""}`.toLowerCase();
    if (category === "technology") return /nasdaq|hang seng|tech|纳斯达克|恒生/.test(name);
    if (category === "finance") return /s&p|dow|hang seng|沪深|上证|nasdaq|标普|道琼斯/.test(name);
    return true;
  });
  return (preferred.length ? preferred : rows)
    .slice()
    .sort((a, b) => Math.abs(Number(b?.changePercent || 0)) - Math.abs(Number(a?.changePercent || 0)))
    .slice(0, limit);
}

function renderRelatedMarketInfoBlock(item, options = {}) {
  const rows = relatedMarketRowsForNews(item, Number(options.limit || 4));
  const instrumentRows = (Array.isArray(appState.intel.chartPayloads) ? appState.intel.chartPayloads : [])
    .map((payload) => {
      const instrument = payload?.data?.instrument || {};
      const bars = Array.isArray(payload?.data?.bars) ? payload.data.bars : [];
      const latest = bars[bars.length - 1] || {};
      const prev = bars[Math.max(0, bars.length - 2)] || latest;
      const close = Number(latest.close || latest.open || 0);
      const prevClose = Number(prev.close || prev.open || close || 0);
      const pct = prevClose ? ((close - prevClose) / prevClose) * 100 : 0;
      return {
        type: String(instrument.instrumentType || instrument.instrument_type || "stock").toLowerCase(),
        symbol: String(instrument.symbol || "--"),
        name: String(instrument.name || instrument.name_en || instrument.name_zh || instrument.symbol || "--"),
        changePercent: pct,
      };
    })
    .filter((entry) => entry.symbol && entry.symbol !== "--");
  if (!rows.length && !instrumentRows.length) {
    return renderEmptyState(lang() === "zh" ? "暂无市场联动" : "No related markets", lang() === "zh" ? "行情快照刷新后会显示相关指数。" : "Related indices appear after market data refresh.");
  }
  const grouped = {
    index: rows.map((idx) => ({
      name: idx.indexName || idx.symbol || "--",
      symbol: idx.symbol || idx.indexCode || "--",
      changePercent: Number(idx.changePercent || 0),
    })),
    stock: instrumentRows.filter((entry) => entry.type === "stock"),
    etf: instrumentRows.filter((entry) => entry.type === "etf" || entry.type === "fund"),
    other: instrumentRows.filter((entry) => !["stock", "etf", "fund"].includes(entry.type)),
  };
  const renderRows = (label, list) => `
    <div class="related-market-group">
      <h4>${escapeHtml(label)}</h4>
      ${(list || []).slice(0, 4).map((entry) => {
        const pct = Number(entry.changePercent || 0);
        const positive = pct >= 0;
        return `
          <div class="related-market-row">
            <span>${escapeHtml(entry.name || entry.symbol || "--")}</span>
            <strong class="${positive ? "is-up" : "is-down"}">${positive ? "+" : ""}${escapeHtml(pct.toFixed(2))}%</strong>
            <em>${escapeHtml(entry.symbol || "--")}</em>
          </div>
        `;
      }).join("") || `<div class="auth-note">${lang() === "zh" ? "暂无" : "No data"}</div>`}
    </div>
  `;
  return `
    <div class="related-market-block">
      <div class="intel-block-title">
        <strong>${lang() === "zh" ? "相关市场" : "Related Markets"}</strong>
        <span>${lang() === "zh" ? "按波动幅度排序" : "Sorted by move"}</span>
      </div>
      ${renderRows(lang() === "zh" ? "指数" : "Indices", grouped.index)}
      ${renderRows(lang() === "zh" ? "股票" : "Stocks", grouped.stock)}
      ${renderRows(lang() === "zh" ? "ETF" : "ETF", grouped.etf)}
      ${renderRows(lang() === "zh" ? "商品/汇率" : "Commodity/FX", grouped.other)}
    </div>
  `;
}

function filteredIntelNewsItems(items) {
  const page = document.getElementById("intel-center");
  const q = String(page?.querySelector("[data-intel-news-search]")?.value || "").trim().toLowerCase();
  const category = String(page?.querySelector("[data-intel-category]")?.value || "").trim().toLowerCase();
  const region = String(page?.querySelector("[data-intel-region]")?.value || "").trim();
  const risk = String(page?.querySelector("[data-intel-risk]")?.value || "").trim();
  const sort = String(page?.querySelector("[data-intel-sort]")?.value || "importance").trim();
  let rows = Array.isArray(items) ? items.slice() : [];
  if (q) {
    rows = rows.filter((item) => `${getDisplayTitle(item)} ${getDisplaySummary(item).text} ${item?.sourceName || ""} ${item?.category || ""}`.toLowerCase().includes(q));
  }
  if (category) rows = rows.filter((item) => String(item?.category || "").toLowerCase() === category);
  if (region) rows = rows.filter((item) => intelNewsRegion(item) === region);
  if (risk) rows = rows.filter((item) => intelNewsRiskLevel(item) === risk);
  rows.sort((a, b) => {
    if (sort === "time") return Number(b?.publishedAt || 0) - Number(a?.publishedAt || 0);
    if (sort === "relevance") return Number(b?.relevanceToFinanceBusinessScore || 0) - Number(a?.relevanceToFinanceBusinessScore || 0);
    return Number(b?.importanceScore || 0) - Number(a?.importanceScore || 0);
  });
  return rows;
}

function intelNewsKey(item) {
  return String(item?.articleId || item?.id || item?.originalUrl || item?.title || "").trim();
}

function intelFilterMetaFromTag(tag) {
  const raw = String(tag || "").trim();
  const value = raw.toLowerCase().replace(/\s+/g, " ");
  const compact = value.replace(/[^a-z0-9\u4e00-\u9fa5]/g, "");
  if (["global", "全球", "all", "全部"].includes(value) || ["global", "全球", "all", "全部"].includes(compact)) {
    return { type: "reset", value: "__all__", label: raw };
  }
  const regionMap = {
    europe: "europe",
    欧洲: "europe",
    eu: "europe",
    us: "us",
    usa: "us",
    美国: "us",
    china: "china",
    中国: "china",
    asia: "asia",
    亚洲: "asia",
  };
  const riskMap = {
    highrisk: "high",
    高风险: "high",
    mediumrisk: "medium",
    中风险: "medium",
    normal: "",
    常规: "",
  };
  const categoryMap = {
    finance: "finance",
    金融: "finance",
    technology: "technology",
    tech: "technology",
    科技: "technology",
    politics: "politics",
    policy: "politics",
    政治: "politics",
  };
  if (Object.prototype.hasOwnProperty.call(regionMap, value) || Object.prototype.hasOwnProperty.call(regionMap, compact)) {
    return { type: "region", value: regionMap[value] ?? regionMap[compact] ?? "", label: raw };
  }
  if (Object.prototype.hasOwnProperty.call(riskMap, compact) || Object.prototype.hasOwnProperty.call(riskMap, value)) {
    return { type: "risk", value: riskMap[compact] ?? riskMap[value] ?? "", label: raw };
  }
  if (Object.prototype.hasOwnProperty.call(categoryMap, value) || Object.prototype.hasOwnProperty.call(categoryMap, compact)) {
    return { type: "category", value: categoryMap[value] ?? categoryMap[compact] ?? "", label: raw };
  }
  return { type: "search", value: raw, label: raw };
}

function intelFilterChipActive(meta) {
  const page = document.getElementById("intel-center");
  if (!page || !meta) return false;
  const region = String(page.querySelector("[data-intel-region]")?.value || "");
  const risk = String(page.querySelector("[data-intel-risk]")?.value || "");
  const category = String(page.querySelector("[data-intel-category]")?.value || "");
  const search = String(page.querySelector("[data-intel-news-search]")?.value || "").trim().toLowerCase();
  if (meta.type === "reset") return !region && !risk && !category && !search;
  if (meta.type === "region") return String(page.querySelector("[data-intel-region]")?.value || "") === String(meta.value || "");
  if (meta.type === "risk") return String(page.querySelector("[data-intel-risk]")?.value || "") === String(meta.value || "");
  if (meta.type === "category") return String(page.querySelector("[data-intel-category]")?.value || "") === String(meta.value || "");
  if (meta.type === "search") return String(page.querySelector("[data-intel-news-search]")?.value || "").trim().toLowerCase() === String(meta.value || "").trim().toLowerCase();
  return false;
}

function renderIntelFilterChip(tag, options = {}) {
  const meta = intelFilterMetaFromTag(tag);
  const active = intelFilterChipActive(meta);
  const title = meta.type === "region"
    ? (lang() === "zh" ? "按地区筛选" : "Filter by region")
    : meta.type === "risk"
      ? (lang() === "zh" ? "按风险筛选" : "Filter by risk")
      : meta.type === "reset"
        ? (lang() === "zh" ? "清空筛选并显示全部" : "Clear filters and show all")
      : meta.type === "category"
        ? (lang() === "zh" ? "按分类筛选" : "Filter by category")
        : (lang() === "zh" ? "按主题搜索" : "Search by topic");
  return `
    <button
      class="tag intel-filter-chip ${active ? "is-active" : ""} ${options.compact ? "intel-filter-chip--compact" : ""}"
      type="button"
      title="${escapeHtml(title)}"
      data-intel-filter-type="${escapeHtml(meta.type)}"
      data-intel-filter-value="${escapeHtml(meta.value)}"
      data-intel-filter-label="${escapeHtml(meta.label)}"
      onclick="applyIntelFilterChip(this); return false;"
    >${escapeHtml(meta.label)}</button>
  `;
}

function applyIntelFilterChip(button, rootOverride = null) {
  const root = rootOverride || button?.closest?.("#intel-center") || document.getElementById("intel-center");
  if (!root || !button) return;
  const type = String(button.getAttribute("data-intel-filter-type") || "");
  const value = String(button.getAttribute("data-intel-filter-value") || "");
  const label = String(button.getAttribute("data-intel-filter-label") || value);
  const setSelect = (selector, nextValue) => {
    const select = root.querySelector(selector);
    if (select) select.value = nextValue;
  };
  const currentValue = (selector) => String(root.querySelector(selector)?.value || "");
  const captureState = () => ({
    category: String(root.querySelector("[data-intel-category]")?.value || ""),
    region: String(root.querySelector("[data-intel-region]")?.value || ""),
    risk: String(root.querySelector("[data-intel-risk]")?.value || ""),
    search: String(root.querySelector("[data-intel-news-search]")?.value || "").trim(),
  });
  const applyState = (state) => {
    if (!state || typeof state !== "object") return;
    const searchInput = root.querySelector("[data-intel-news-search]");
    setSelect("[data-intel-category]", String(state.category || ""));
    setSelect("[data-intel-region]", String(state.region || ""));
    setSelect("[data-intel-risk]", String(state.risk || ""));
    if (searchInput) searchInput.value = String(state.search || "");
  };
  const isAllClear = (state) => {
    const target = state || captureState();
    return !String(target.category || "").trim()
      && !String(target.region || "").trim()
      && !String(target.risk || "").trim()
      && !String(target.search || "").trim();
  };
  const beforeState = captureState();
  let nextValue = value;
  let cleared = false;
  let restored = false;
  if (type === "reset") {
    if (isAllClear(beforeState)) {
      if (appState.intel.previousFilterState) {
        applyState(appState.intel.previousFilterState);
        appState.intel.previousFilterState = null;
        restored = true;
      }
    } else {
      appState.intel.previousFilterState = beforeState;
      setSelect("[data-intel-category]", "");
      setSelect("[data-intel-region]", "");
      setSelect("[data-intel-risk]", "");
      const input = root.querySelector("[data-intel-news-search]");
      if (input) input.value = "";
    }
    cleared = !restored;
  } else if (type === "region") {
    cleared = !value || currentValue("[data-intel-region]") === value;
    nextValue = cleared ? "" : value;
    setSelect("[data-intel-region]", nextValue);
  } else if (type === "risk") {
    cleared = !value || currentValue("[data-intel-risk]") === value;
    nextValue = cleared ? "" : value;
    setSelect("[data-intel-risk]", nextValue);
  } else if (type === "category") {
    cleared = currentValue("[data-intel-category]") === value;
    nextValue = cleared ? "" : value;
    setSelect("[data-intel-category]", nextValue);
  } else if (type === "search") {
    const input = root.querySelector("[data-intel-news-search]");
    cleared = String(input?.value || "").trim().toLowerCase() === label.trim().toLowerCase();
    if (input) input.value = cleared ? "" : label;
  }
  if (type !== "reset") {
    if (!cleared && String(value || "").trim()) {
      appState.intel.previousFilterState = beforeState;
    } else if (cleared && appState.intel.previousFilterState) {
      applyState(appState.intel.previousFilterState);
      appState.intel.previousFilterState = null;
      restored = true;
    }
  }
  const feedback = root.querySelector("[data-intel-feedback]");
  if (feedback) {
    feedback.dataset.state = "success";
    feedback.textContent = restored
      ? (lang() === "zh" ? "已恢复到上一步筛选状态。" : "Restored previous filter state.")
      : (cleared
        ? (lang() === "zh" ? `已取消筛选：${label || "全部"}，恢复显示全部。` : `Filter cleared: ${label || "All"}. Showing all.`)
        : (lang() === "zh" ? `已应用筛选：${label || (value || "全部")}` : `Filter applied: ${label || (value || "All")}`));
  }
  rerenderIntelNewsSurface(root);
}

if (typeof window !== "undefined") {
  window.applyIntelFilterChip = applyIntelFilterChip;
}

function rerenderIntelNewsSurface(root) {
  const page = root || document.getElementById("intel-center");
  if (!page) return;
  const items = appState.intel.lastTopNews?.data?.items || appState.intel.lastTopNews?.items || [];
  const filteredItems = filteredIntelNewsItems(items);
  const newsNode = page.querySelector("[data-intel-news]");
  if (newsNode) newsNode.innerHTML = renderIntelNews(appState.intel.lastTopNews || {});
  if (!filteredItems.some((item) => intelNewsKey(item) === appState.intel.selectedNewsId)) {
    appState.intel.selectedNewsId = intelNewsKey(filteredItems[0] || items[0] || "");
  }
  const selected = (items || []).find((item) => intelNewsKey(item) === appState.intel.selectedNewsId) || filteredItems[0] || items[0];
  const detailNode = page.querySelector("[data-intel-news-detail]");
  if (detailNode) detailNode.innerHTML = renderIntelNewsDetailPanel(selected);
  syncIntelSidePanels(page, filteredItems);
  bindIntelNewsCards(page);
}

function renderIntelNewsCard(item, index, featured = false) {
  const newsId = intelNewsKey(item);
  const isSelected = newsId && appState.intel.selectedNewsId === newsId;
  const isSaved = !!(newsId && Array.isArray(appState.intel.savedNewsIds) && appState.intel.savedNewsIds.includes(newsId));
  const title = getDisplayTitle(item);
  const summary = getDisplaySummary(item);
  const tags = intelNewsTags(item);
  const risk = intelNewsRiskLevel(item);
  const linkedMarkets = relatedMarketRowsForNews(item, 2);
  const freshness = freshnessMeta(item?.publishedAt || 0);
  return `
    <article class="intel-news-card ${featured ? "intel-news-card--featured" : ""} ${isSelected ? "is-selected" : ""}" data-news-id="${escapeHtml(newsId)}">
      <div class="intel-news-card__head">
        <strong>${featured ? `<span class="rank-chip">#${index}</span>` : `<span class="rank-chip rank-chip--subtle">#${index}</span>`}${escapeHtml(title)}</strong>
        <span>${escapeHtml(item.sourceName || "-")} · ${escapeHtml(formatDateTime(item.publishedAt || 0))}</span>
      </div>
      <div class="intel-news-card__badges">
        ${renderTranslationStatusBadge(summary.status)}
        ${renderStatusBadge(risk === "high" ? (lang() === "zh" ? "高风险" : "High risk") : risk === "medium" ? (lang() === "zh" ? "中风险" : "Medium risk") : (lang() === "zh" ? "常规" : "Normal"), risk === "high" ? "error" : risk === "medium" ? "warning" : "neutral")}
        ${renderStatusBadge(`${freshness.label} · ${freshness.ageText}`, freshness.state)}
      </div>
      ${summary.status === "fallback_en" ? `<div class="translation-fallback-note">${escapeHtml(summary.label)}</div>` : ""}
      <p>${escapeHtml(summary.text)}</p>
      <div class="intel-tag-row">${tags.map((tag) => renderIntelFilterChip(tag, { compact: true })).join("")}</div>
      <div class="intel-news-linked-row">
        ${linkedMarkets.length ? linkedMarkets.map((entry) => `<span class="mini-pill">${escapeHtml(entry.symbol || entry.indexCode || "--")}</span>`).join("") : `<span class="intel-news-linked-muted">${lang() === "zh" ? "暂无联动标的" : "No linked symbols"}</span>`}
      </div>
      <div class="intel-news-actions">
        <button class="btn btn-soft" type="button" data-intel-news-detail-btn="${escapeHtml(newsId)}">${lang() === "zh" ? "详情" : "Details"}</button>
        <a class="btn btn-ghost" href="${escapeHtml(item.originalUrl || "#")}" target="_blank" rel="noopener noreferrer">${lang() === "zh" ? "原文" : "Source"}</a>
        <button class="btn btn-ghost" type="button" data-intel-news-save="${escapeHtml(newsId)}">${isSaved ? (lang() === "zh" ? "已保存" : "Saved") : (lang() === "zh" ? "保存" : "Save")}</button>
      </div>
    </article>
  `;
}

function renderIntelNewsDetailPanel(item) {
  if (!item) {
    return renderEmptyState(lang() === "zh" ? "选择一条新闻查看详情" : "Select a story", lang() === "zh" ? "详情会展示摘要、原文入口和相关市场。" : "Details show summary, source, and related markets.");
  }
  const summary = getDisplaySummary(item);
  const title = getDisplayTitle(item);
  const rawOriginal = firstText(item?.summaryEn, item?.summary_en, item?.rawExcerpt, item?.raw_excerpt, item?.originalSummary);
  const risk = intelNewsRiskLevel(item);
  const sentiment = Number(item?.sentimentScore || 0);
  const linkedMarkets = relatedMarketRowsForNews(item, 4);
  return `
    <div class="news-detail-panel">
      <div class="intel-block-title">
        <strong>${lang() === "zh" ? "新闻详情" : "News Detail"}</strong>
        ${renderTranslationStatusBadge(summary.status)}
      </div>
      <h3>${escapeHtml(title)}</h3>
      <div class="admin-user-card__meta">${escapeHtml(item.sourceName || "-")} · ${escapeHtml(formatDateTime(item.publishedAt || 0))} · ${escapeHtml(item.category || "general")}</div>
      <div class="intel-detail-meta-row">
        ${renderStatusBadge(risk === "high" ? (lang() === "zh" ? "高风险" : "High risk") : risk === "medium" ? (lang() === "zh" ? "中风险" : "Medium risk") : (lang() === "zh" ? "常规" : "Normal"), risk === "high" ? "error" : risk === "medium" ? "warning" : "neutral")}
        ${renderStatusBadge(sentiment > 0 ? (lang() === "zh" ? "情绪偏正" : "Positive tone") : sentiment < 0 ? (lang() === "zh" ? "情绪偏负" : "Negative tone") : (lang() === "zh" ? "情绪中性" : "Neutral tone"), sentiment > 0 ? "success" : sentiment < 0 ? "error" : "neutral")}
      </div>
      ${summary.status === "fallback_en" ? `<div class="translation-fallback-note">${escapeHtml(summary.label)}</div>` : ""}
      <p class="news-detail-summary">${escapeHtml(summary.text)}</p>
      ${rawOriginal ? `<div class="news-detail-original"><h4>${lang() === "zh" ? "原文摘要" : "Original Summary"}</h4><p>${escapeHtml(rawOriginal)}</p></div>` : ""}
      <div class="intel-detail-linked">
        <h4>${lang() === "zh" ? "相关市场" : "Related Markets"}</h4>
        <div class="intel-tag-row">${linkedMarkets.map((entry) => `<span class="tag">${escapeHtml(entry.indexName || entry.symbol || "--")} ${Number(entry.changePercent || 0) >= 0 ? "+" : ""}${escapeHtml(Number(entry.changePercent || 0).toFixed(2))}%</span>`).join("")}</div>
      </div>
      ${renderRelatedMarketInfoBlock(item, { limit: 5 })}
      <div class="intel-news-actions">
        <a class="btn btn-primary" href="${escapeHtml(item.originalUrl || "#")}" target="_blank" rel="noopener noreferrer">${lang() === "zh" ? "打开原文" : "Open Source"}</a>
      </div>
    </div>
  `;
}

function renderIntelNews(topNews) {
  const source = topNews?.data || topNews || {};
  const items = filteredIntelNewsItems(Array.isArray(source?.items) ? source.items : []);
  const featured = items.slice(0, 3);
  const ranked = items.slice(3, 30);
  const clusters = Array.from(new Set(items.flatMap((item) => intelNewsTags(item)).filter(Boolean))).slice(0, 8);
  return `
    <div class="fc-analytic-card news-intel-panel">
      <div class="intel-block-title">
        <strong>${lang() === "zh" ? "Top30 情报流" : "Top 30 Intelligence Feed"}</strong>
        <span>${escapeHtml(source?.generatedAt ? formatDateTime(source.generatedAt) : formatDateTime(Math.floor(Date.now() / 1000)))}</span>
      </div>
      ${items.length ? `
        <div class="top30-section-title">${lang() === "zh" ? "Top 3 精选" : "Top 3 Featured Stories"}</div>
        <div class="topic-cluster-row">${clusters.map((tag) => renderIntelFilterChip(tag)).join("")}</div>
        <div class="featured-news-grid">
          ${featured.map((item, idx) => renderIntelNewsCard(item, idx + 1, true)).join("")}
        </div>
        <div class="top30-section-title">${lang() === "zh" ? "4-30 排行" : "Ranked List (4-30)"}</div>
        <div class="ranked-news-list">
          ${ranked.map((item, idx) => renderIntelNewsCard(item, idx + 4, false)).join("")}
        </div>
      ` : renderEmptyState(lang() === "zh" ? "暂无新闻数据" : "No news data", lang() === "zh" ? "请刷新新闻或调整筛选条件。" : "Refresh news or adjust filters.")}
    </div>
  `;
}

function renderIntelTrendingTopics(items) {
  const rows = Array.isArray(items) ? items : [];
  const topicMap = new Map();
  rows.forEach((item) => {
    intelNewsTags(item).forEach((tag) => {
      const key = String(tag || "").trim();
      if (!key) return;
      topicMap.set(key, (topicMap.get(key) || 0) + 1);
    });
  });
  const sorted = Array.from(topicMap.entries()).sort((a, b) => b[1] - a[1]).slice(0, 10);
  return `
    <div class="fc-analytic-card">
      <div class="intel-block-title">
        <strong>${lang() === "zh" ? "Topic Cluster" : "Topic Clusters"}</strong>
      </div>
      ${sorted.length
        ? `<div class="topic-cluster-row">${sorted.map(([topic, count]) => renderIntelFilterChip(topic).replace("</button>", ` · ${escapeHtml(String(count))}</button>`)).join("")}</div>`
        : renderEmptyState(lang() === "zh" ? "暂无聚类话题" : "No topic clusters")}
    </div>
  `;
}

function renderIntelSourceMix(items) {
  const rows = Array.isArray(items) ? items : [];
  const counts = new Map();
  rows.forEach((item) => {
    const key = String(item?.sourceName || "Unknown").trim() || "Unknown";
    counts.set(key, (counts.get(key) || 0) + 1);
  });
  const entries = Array.from(counts.entries()).sort((a, b) => b[1] - a[1]).slice(0, 8);
  const max = Math.max(1, ...entries.map(([, value]) => value));
  return `
    <div class="fc-analytic-card">
      <div class="intel-block-title">
        <strong>${lang() === "zh" ? "来源结构" : "Source Mix"}</strong>
        <span>${lang() === "zh" ? "降低单一来源偏差" : "Bias check"}</span>
      </div>
      ${entries.length ? entries.map(([source, count]) => `
        <div class="source-mix-row">
          <span>${escapeHtml(source)}</span>
          <div class="source-mix-track"><i style="width:${Math.max(8, Math.round((count / max) * 100))}%"></i></div>
          <strong>${escapeHtml(String(count))}</strong>
        </div>
      `).join("") : renderEmptyState(lang() === "zh" ? "暂无来源数据" : "No source data")}
    </div>
  `;
}

function renderIntelRiskAlerts(items) {
  const rows = (Array.isArray(items) ? items : []).filter((item) => intelNewsRiskLevel(item) !== "normal").slice(0, 6);
  return `
    <div class="fc-analytic-card">
      <div class="intel-block-title">
        <strong>${lang() === "zh" ? "风险提醒" : "Risk Alerts"}</strong>
      </div>
      ${rows.length ? rows.map((item) => {
        const risk = intelNewsRiskLevel(item);
        return `
          <div class="intel-alert-row">
            ${renderStatusBadge(risk === "high" ? (lang() === "zh" ? "高" : "High") : (lang() === "zh" ? "中" : "Medium"), risk === "high" ? "error" : "warning")}
            <span>${escapeHtml(getDisplayTitle(item))}</span>
          </div>
        `;
      }).join("") : renderEmptyState(lang() === "zh" ? "暂无风险提醒" : "No risk alerts")}
    </div>
  `;
}

function renderIntelSavedItems(items) {
  const savedIds = Array.isArray(appState.intel.savedNewsIds) ? appState.intel.savedNewsIds : [];
  const rows = (Array.isArray(items) ? items : []).filter((item) => savedIds.includes(intelNewsKey(item))).slice(0, 12);
  return `
    <div class="fc-analytic-card">
      <div class="intel-block-title">
        <strong>${lang() === "zh" ? "已保存新闻" : "Saved Stories"}</strong>
      </div>
      ${rows.length
        ? rows.map((item) => `<button class="intel-saved-item" type="button" data-intel-news-detail-btn="${escapeHtml(intelNewsKey(item))}">${escapeHtml(getDisplayTitle(item))}</button>`).join("")
        : renderEmptyState(lang() === "zh" ? "暂无保存项" : "No saved stories")}
    </div>
  `;
}

function renderIntelRelatedMarketPanel(items) {
  const rows = (appState.intel.lastMarketsOverview?.data?.regions || [])
    .flatMap((region) => region.countries || [])
    .flatMap((country) => country.indices || [])
    .sort((a, b) => Math.abs(Number(b?.changePercent || 0)) - Math.abs(Number(a?.changePercent || 0)))
    .slice(0, 8);
  return `
    <div class="fc-analytic-card">
      <div class="intel-block-title">
        <strong>${lang() === "zh" ? "Related Market Movers" : "Related Market Movers"}</strong>
      </div>
      ${rows.length
        ? rows.map((idx) => `
          <div class="related-market-row">
            <span>${escapeHtml(idx.indexName || idx.symbol || "--")}</span>
            <strong class="${Number(idx.changePercent || 0) >= 0 ? "is-up" : "is-down"}">${Number(idx.changePercent || 0) >= 0 ? "+" : ""}${escapeHtml(Number(idx.changePercent || 0).toFixed(2))}%</strong>
            <em>${escapeHtml(idx.symbol || idx.indexCode || "--")}</em>
          </div>
        `).join("")
        : renderEmptyState(lang() === "zh" ? "暂无市场联动" : "No market movers")}
    </div>
  `;
}

function formatFxDisplayValue(symbol, value) {
  const num = Number(value || 0);
  if (!Number.isFinite(num) || !num) return "--";
  return /JPY/i.test(String(symbol || "")) ? num.toFixed(3) : num.toFixed(4);
}

function normalizeYieldPercent(symbol, value) {
  const num = Number(value || 0);
  if (!Number.isFinite(num) || !num) return 0;
  const tenXSymbols = new Set(["^IRX", "^FVX", "^TNX", "^TYX", "^UK10Y", "^JP10Y"]);
  return tenXSymbols.has(String(symbol || "").toUpperCase()) ? (num / 10) : num;
}

function macroThresholdState(type, changePercent) {
  const abs = Math.abs(Number(changePercent || 0));
  if (type === "fx") {
    if (abs >= 1.2) return "error";
    if (abs >= 0.7) return "warning";
    return "success";
  }
  if (abs >= 3.0) return "error";
  if (abs >= 1.6) return "warning";
  return "success";
}

function macroStateLabel(state) {
  if (lang() === "zh") {
    if (state === "error") return "异常";
    if (state === "warning") return "关注";
    return "正常";
  }
  if (state === "error") return "Abnormal";
  if (state === "warning") return "Watch";
  return "Normal";
}

function macroAllRows(payload) {
  const data = payload?.data || payload || {};
  const fx = Array.isArray(data.fx) ? data.fx : [];
  const bonds = Array.isArray(data.sovereignYields) ? data.sovereignYields : [];
  return [
    ...fx.map((row) => ({ ...row, macroType: "fx", latestValue: Number(row.latestPrice || 0) })),
    ...bonds.map((row) => ({ ...row, macroType: "bond", latestValue: normalizeYieldPercent(row.symbol, row.latestYield) })),
  ];
}

function renderMacroMiniKline(payload) {
  const bars = Array.isArray(payload?.data?.bars) ? payload.data.bars : [];
  const instrument = payload?.data?.instrument || {};
  if (!bars.length) {
    return `<div class="auth-note">${lang() === "zh" ? "暂无6个月K线数据" : "No 6M K-line data"}</div>`;
  }
  const width = 420;
  const height = 140;
  const padX = 10;
  const padY = 12;
  const closes = bars.map((bar) => Number(bar.close || bar.open || 0)).filter((v) => Number.isFinite(v));
  if (!closes.length) {
    return `<div class="auth-note">${lang() === "zh" ? "暂无6个月K线数据" : "No 6M K-line data"}</div>`;
  }
  const max = Math.max(...closes);
  const min = Math.min(...closes);
  const span = Math.max(0.000001, max - min);
  const stepX = (width - padX * 2) / Math.max(1, closes.length - 1);
  const points = closes.map((value, idx) => {
    const x = padX + idx * stepX;
    const ratio = (value - min) / span;
    const y = (height - padY) - ratio * (height - padY * 2);
    return `${Math.round(x)},${Math.round(y)}`;
  }).join(" ");
  const first = closes[0];
  const last = closes[closes.length - 1];
  const delta = last - first;
  const deltaPct = first ? (delta / first) * 100 : 0;
  const up = delta >= 0;
  const chartColor = up ? "var(--work-ok)" : "var(--work-danger)";
  return `
    <div class="macro-kline-card">
      <div class="macro-kline-head">
        <strong>${escapeHtml(String(instrument.name || instrument.name_en || instrument.name_zh || instrument.symbol || "--"))}</strong>
        <span class="${up ? "is-up" : "is-down"}">${up ? "+" : ""}${escapeHtml(deltaPct.toFixed(2))}% · 6M</span>
      </div>
      <svg viewBox="0 0 ${width} ${height}" class="macro-kline-svg" role="img" aria-label="macro-kline-6m">
        <polyline fill="none" stroke="${chartColor}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round" points="${points}" />
      </svg>
      <div class="macro-kline-foot">
        <span>${lang() === "zh" ? "区间低点" : "6M Low"}: ${escapeHtml(min.toFixed(2))}</span>
        <span>${lang() === "zh" ? "区间高点" : "6M High"}: ${escapeHtml(max.toFixed(2))}</span>
      </div>
    </div>
  `;
}

async function loadIntelMacroCandle(symbol = "") {
  const source = appState.intel.lastMacroRates;
  const rows = macroAllRows(source);
  if (!rows.length) {
    appState.intel.lastMacroCandlePayload = null;
    appState.intel.selectedMacroSymbol = "";
    return;
  }
  const selectedSymbol = String(symbol || appState.intel.selectedMacroSymbol || "^TNX").toUpperCase();
  const chosen = rows.find((row) => String(row.symbol || "").toUpperCase() === selectedSymbol)
    || rows.find((row) => String(row.symbol || "").toUpperCase() === "^TNX")
    || rows[0];
  const instrumentId = String(chosen?.instrumentId || "");
  if (!instrumentId) {
    appState.intel.lastMacroCandlePayload = null;
    appState.intel.selectedMacroSymbol = String(chosen?.symbol || "");
    return;
  }
  const payload = await loadIntelInstrumentCandles(instrumentId, "1d", "6mo", true);
  appState.intel.lastMacroCandlePayload = payload;
  appState.intel.selectedMacroSymbol = String(chosen?.symbol || "");
}

function renderIntelMacroRatesPanel(payload) {
  const data = payload?.data || payload || {};
  const fx = Array.isArray(data.fx) ? data.fx : [];
  const bonds = Array.isArray(data.sovereignYields) ? data.sovereignYields : [];
  const updatedAt = Number(data.lastUpdatedAt || 0);
  const freshness = freshnessMeta(updatedAt);
  const selectedSymbol = String(appState.intel.selectedMacroSymbol || "").toUpperCase();
  const allRows = macroAllRows(payload);
  const alerts = allRows
    .map((row) => {
      const state = macroThresholdState(row.macroType, row.changePercent);
      return { ...row, state };
    })
    .filter((row) => row.state !== "success")
    .sort((a, b) => Math.abs(Number(b.changePercent || 0)) - Math.abs(Number(a.changePercent || 0)))
    .slice(0, 6);
  const fxRows = fx.map((row) => {
    const pct = Number(row.changePercent || 0);
    const state = macroThresholdState("fx", pct);
    const symbol = String(row.symbol || "").toUpperCase();
    const active = selectedSymbol && symbol === selectedSymbol;
    return `
      <button class="related-market-row macro-rate-row ${active ? "is-active" : ""}" type="button" data-intel-macro-symbol="${escapeHtml(symbol)}">
        <span>${escapeHtml(row.name || row.symbol || "--")}</span>
        <strong class="${pct >= 0 ? "is-up" : "is-down"}">${pct >= 0 ? "+" : ""}${escapeHtml(pct.toFixed(2))}%</strong>
        <em>${escapeHtml(formatFxDisplayValue(row.symbol, row.latestPrice))}</em>
        ${renderStatusBadge(macroStateLabel(state), state)}
      </button>
    `;
  }).join("");
  const bondRows = bonds.map((row) => {
    const pct = Number(row.changePercent || 0);
    const state = macroThresholdState("bond", pct);
    const symbol = String(row.symbol || "").toUpperCase();
    const active = selectedSymbol && symbol === selectedSymbol;
    const y = normalizeYieldPercent(row.symbol, row.latestYield);
    return `
      <button class="related-market-row macro-rate-row ${active ? "is-active" : ""}" type="button" data-intel-macro-symbol="${escapeHtml(symbol)}">
        <span>${escapeHtml(row.name || row.symbol || "--")}</span>
        <strong class="${pct >= 0 ? "is-up" : "is-down"}">${pct >= 0 ? "+" : ""}${escapeHtml(pct.toFixed(2))}%</strong>
        <em>${y ? `${escapeHtml(y.toFixed(2))}%` : "--"}</em>
        ${renderStatusBadge(macroStateLabel(state), state)}
      </button>
    `;
  }).join("");
  const alertRows = alerts.length
    ? alerts.map((row) => {
      const pct = Number(row.changePercent || 0);
      return `
        <div class="macro-alert-row">
          ${renderStatusBadge(macroStateLabel(row.state), row.state)}
          <span>${escapeHtml(String(row.name || row.symbol || "--"))}</span>
          <strong class="${pct >= 0 ? "is-up" : "is-down"}">${pct >= 0 ? "+" : ""}${escapeHtml(pct.toFixed(2))}%</strong>
        </div>
      `;
    }).join("")
    : `<div class="auth-note">${lang() === "zh" ? "当前未触发异常阈值。" : "No anomaly threshold breach currently."}</div>`;
  return `
    <div class="fc-analytic-card">
      <div class="intel-block-title">
        <strong>${lang() === "zh" ? "外汇与国债当日情报" : "FX & Sovereign Yield Daily Intel"}</strong>
        <span>${freshness.ageText} ${renderStatusBadge(freshness.label, freshness.state)}</span>
      </div>
      <div class="related-market-group">
        <h4>${lang() === "zh" ? "异常阈值提醒" : "Anomaly Threshold Alerts"}</h4>
        ${alertRows}
      </div>
      <div class="related-market-group">
        <h4>${lang() === "zh" ? "世界主要汇率" : "Major FX Pairs"}</h4>
        ${fxRows || `<div class="auth-note">${lang() === "zh" ? "暂无汇率数据" : "No FX data"}</div>`}
      </div>
      <div class="related-market-group">
        <h4>${lang() === "zh" ? "主要国债当日利率" : "Major Sovereign Daily Yields"}</h4>
        ${bondRows || `<div class="auth-note">${lang() === "zh" ? "暂无国债收益率数据" : "No sovereign yield data"}</div>`}
      </div>
      <div class="related-market-group">
        <h4>${lang() === "zh" ? "6个月K线图（点击上方标的切换）" : "6M K-line (click instrument to switch)"}</h4>
        ${renderMacroMiniKline(appState.intel.lastMacroCandlePayload)}
      </div>
    </div>
  `;
}

function syncIntelSidePanels(page, items) {
  const root = page || document.getElementById("intel-center");
  if (!root) return;
  const relatedNode = root.querySelector("[data-intel-related-markets]");
  const macroNode = root.querySelector("[data-intel-macro-rates]");
  const sourceNode = root.querySelector("[data-intel-source-mix]");
  const topicNode = root.querySelector("[data-intel-trending-topics]");
  const riskNode = root.querySelector("[data-intel-risk-alerts]");
  const savedNode = root.querySelector("[data-intel-saved-items]");
  if (relatedNode) relatedNode.innerHTML = renderIntelRelatedMarketPanel(items);
  if (macroNode) macroNode.innerHTML = renderIntelMacroRatesPanel(appState.intel.lastMacroRates);
  if (sourceNode) sourceNode.innerHTML = renderIntelSourceMix(items);
  if (topicNode) topicNode.innerHTML = renderIntelTrendingTopics(items);
  if (riskNode) riskNode.innerHTML = renderIntelRiskAlerts(items);
  if (savedNode) savedNode.innerHTML = renderIntelSavedItems(items);
  bindIntelMacroPanel(root);
}

function bindIntelMacroPanel(root) {
  if (!root) return;
  root.querySelectorAll("[data-intel-macro-symbol]").forEach((button) => {
    if (button.dataset.boundMacroSymbol === "1") return;
    button.dataset.boundMacroSymbol = "1";
    button.addEventListener("click", async () => {
      const symbol = String(button.getAttribute("data-intel-macro-symbol") || "").trim();
      if (!symbol) return;
      const feedback = root.querySelector("[data-intel-feedback]");
      if (feedback) {
        feedback.dataset.state = "loading";
        feedback.textContent = lang() === "zh" ? "正在加载6个月K线..." : "Loading 6M K-line...";
      }
      try {
        await loadIntelMacroCandle(symbol);
        const items = appState.intel.lastTopNews?.data?.items || appState.intel.lastTopNews?.items || [];
        syncIntelSidePanels(root, filteredIntelNewsItems(items));
        if (feedback) {
          feedback.dataset.state = "success";
          feedback.textContent = lang() === "zh" ? "6个月K线已更新。" : "6M K-line updated.";
        }
      } catch (error) {
        if (feedback) {
          feedback.dataset.state = "error";
          feedback.textContent = authErrorMessage(error.message);
        }
      }
    });
  });
}

function bindIntelNewsCards(page) {
  const root = page || document.getElementById("intel-center");
  if (!root) return;
  root.querySelectorAll("[data-intel-filter-type]").forEach((button) => {
    if (button.dataset.boundIntelFilter === "1") return;
    button.dataset.boundIntelFilter = "1";
    if (button.getAttribute("onclick")) return;
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      applyIntelFilterChip(button, root);
    });
  });
  root.querySelectorAll("[data-intel-news-detail-btn]").forEach((button) => {
    if (button.dataset.bound === "1") return;
    button.dataset.bound = "1";
    button.addEventListener("click", () => {
      const id = String(button.getAttribute("data-intel-news-detail-btn") || "");
      const items = appState.intel.lastTopNews?.data?.items || appState.intel.lastTopNews?.items || [];
      const item = items.find((candidate) => intelNewsKey(candidate) === id);
      appState.intel.selectedNewsId = id;
      const detailNode = root.querySelector("[data-intel-news-detail]");
      if (detailNode) detailNode.innerHTML = renderIntelNewsDetailPanel(item);
      const newsNode = root.querySelector("[data-intel-news]");
      if (newsNode) newsNode.innerHTML = renderIntelNews(appState.intel.lastTopNews || {});
      syncIntelSidePanels(root, items);
      bindIntelNewsCards(root);
    });
  });
  root.querySelectorAll("[data-intel-news-save]").forEach((button) => {
    if (button.dataset.boundSave === "1") return;
    button.dataset.boundSave = "1";
    button.addEventListener("click", () => {
      const id = String(button.getAttribute("data-intel-news-save") || "").trim();
      if (!id) return;
      const saved = new Set(Array.isArray(appState.intel.savedNewsIds) ? appState.intel.savedNewsIds : []);
      if (saved.has(id)) saved.delete(id);
      else saved.add(id);
      appState.intel.savedNewsIds = Array.from(saved).slice(0, 60);
      try {
        localStorage.setItem("intel:center:saved_news", JSON.stringify(appState.intel.savedNewsIds));
      } catch {}
      const items = appState.intel.lastTopNews?.data?.items || appState.intel.lastTopNews?.items || [];
      const newsNode = root.querySelector("[data-intel-news]");
      if (newsNode) newsNode.innerHTML = renderIntelNews(appState.intel.lastTopNews || {});
      syncIntelSidePanels(root, items);
      bindIntelNewsCards(root);
    });
  });
}

function renderIntelCandleCard(payload) {
  const bars = Array.isArray(payload?.data?.bars) ? payload.data.bars : [];
  const instrument = payload?.data?.instrument || {};
  if (!bars.length) {
    return "";
  }
  const width = 980;
  const height = 340;
  const pad = 28;
  const maxHigh = Math.max(...bars.map((b) => Number(b.high || 0)));
  const minLow = Math.min(...bars.map((b) => Number(b.low || 0)));
  const span = Math.max(0.000001, maxHigh - minLow);
  const step = Math.max(4, (width - pad * 2) / Math.max(1, bars.length));
  const candleWidth = Math.max(2, Math.min(10, step * 0.62));
  const toY = (value) => {
    const ratio = (Number(value || 0) - minLow) / span;
    return Math.round((height - pad) - ratio * (height - pad * 2));
  };
  const candlesticks = bars.map((bar, idx) => {
    const x = Math.round(pad + idx * step + step / 2);
    const openY = toY(bar.open);
    const closeY = toY(bar.close);
    const highY = toY(bar.high);
    const lowY = toY(bar.low);
    const top = Math.min(openY, closeY);
    const h = Math.max(1, Math.abs(closeY - openY));
    const bullish = Number(bar.close || 0) >= Number(bar.open || 0);
    const color = bullish ? "#16a34a" : "#dc2626";
    return `
      <line x1="${x}" y1="${highY}" x2="${x}" y2="${lowY}" stroke="${color}" stroke-width="1.2" />
      <rect x="${Math.round(x - candleWidth / 2)}" y="${top}" width="${Math.round(candleWidth)}" height="${h}" fill="${color}" opacity="0.82" />
    `;
  }).join("");
  const firstTime = bars[0]?.time ? formatDateTime(bars[0].time) : "--";
  const lastTime = bars[bars.length - 1]?.time ? formatDateTime(bars[bars.length - 1].time) : "--";
  return `
    <div class="fc-analytic-card intel-chart-card">
      <div class="intel-chart-head">
        <h4>${lang() === "zh" ? "K线图" : "K-Line Chart"} · ${escapeHtml(instrument.symbol || "--")} · ${escapeHtml(instrument.name || "--")}</h4>
        <div class="intel-chart-tags">
          <span class="tag">${lang() === "zh" ? "区间" : "Range"}: ${escapeHtml(payload?.data?.range || "--")}</span>
          <span class="tag">${lang() === "zh" ? "周期" : "Interval"}: ${escapeHtml(payload?.data?.interval || "--")}</span>
          <span class="tag">${lang() === "zh" ? "样本" : "Bars"}: ${bars.length}</span>
          <span class="tag">${lang() === "zh" ? "时间窗" : "Window"}: ${escapeHtml(firstTime)} → ${escapeHtml(lastTime)}</span>
        </div>
      </div>
      <svg viewBox="0 0 ${width} ${height}" class="intel-kline-svg" role="img" aria-label="candlestick chart">
        <rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>
        <line x1="${pad}" y1="${pad}" x2="${pad}" y2="${height - pad}" stroke="rgba(148,163,184,.35)" stroke-width="1"></line>
        <line x1="${pad}" y1="${height - pad}" x2="${width - pad}" y2="${height - pad}" stroke="rgba(148,163,184,.35)" stroke-width="1"></line>
        ${candlesticks}
      </svg>
    </div>
  `;
}

function renderIntelCandlePanel(payloads) {
  const list = Array.isArray(payloads) ? payloads : payloads ? [payloads] : [];
  const cards = list
    .map((payload) => renderIntelCandleCard(payload))
    .filter(Boolean)
    .join("");
  if (!cards) {
    return `
      <div class="fc-analytic-card intel-chart-card">
        <div class="intel-chart-head">
          <h4>${lang() === "zh" ? "K线图" : "K-Line Chart"}</h4>
        </div>
        <div class="auth-note">${lang() === "zh" ? "点击上方全球市场卡片，或输入标的后加载 K 线。" : "Click a market card above or enter a symbol to load charts."}</div>
      </div>
    `;
  }
  return `
    <div class="intel-candle-grid">
      ${cards}
    </div>
  `;
}

function upsertIntelChartPayload(payload, options = {}) {
  const instrumentId = String(payload?.data?.instrument?.instrumentId || payload?.data?.instrument?.id || "");
  const symbol = String(payload?.data?.instrument?.symbol || "");
  const key = instrumentId || symbol;
  if (!key) return;
  const existing = Array.isArray(appState.intel.chartPayloads) ? appState.intel.chartPayloads : [];
  const filtered = existing.filter((item) => {
    const itemId = String(item?.data?.instrument?.instrumentId || item?.data?.instrument?.id || "");
    const itemSymbol = String(item?.data?.instrument?.symbol || "");
    return (itemId || itemSymbol) !== key;
  });
  const next = [payload, ...filtered].slice(0, Number(options.limit || 6));
  appState.intel.chartPayloads = next;
  appState.intel.lastCandlePayload = payload;
  try {
    localStorage.setItem("intel:center:chart_stack", JSON.stringify(next));
    localStorage.setItem("intel:center:last_candle", JSON.stringify(payload));
  } catch {}
}

async function loadIntelChartByQuery(query, options = {}) {
  const page = document.getElementById("intel-center");
  if (!page) throw new Error("intel_page_not_found");
  const host = page.querySelector("[data-intel-candle]");
  if (!host) throw new Error("kline_host_not_found");
  const locale = String(page.querySelector("[data-intel-lang]")?.value || "zh");
  let interval = String(options.interval || page.querySelector("[data-intel-candle-interval]")?.value || "1d");
  const range = String(options.range || page.querySelector("[data-intel-candle-range]")?.value || "6mo");
  if (String(options.marketStatus || "").toLowerCase() === "closed" && ["1m", "5m", "15m", "30m", "1h"].includes(interval)) {
    interval = "1d";
    const intervalSelect = page.querySelector("[data-intel-candle-interval]");
    if (intervalSelect) intervalSelect.value = "1d";
  }
  const found = await searchIntelInstruments(query, locale, "", 10);
  const item = (found?.data?.items || []).find((candidate) => String(candidate.symbol || "").toUpperCase() === String(query || "").toUpperCase())
    || (found?.data?.items || [])[0];
  if (!item?.instrumentId) {
    throw new Error(lang() === "zh" ? "未找到该标的。" : "Instrument not found.");
  }
  appState.intel.selectedInstrumentId = String(item.instrumentId || "");
  appState.intel.selectedInstrumentSymbol = String(item.symbol || "");
  const candles = await loadIntelInstrumentCandles(appState.intel.selectedInstrumentId, interval, range, true);
  const bars = Array.isArray(candles?.data?.bars) ? candles.data.bars : [];
  if (!bars.length) {
    throw new Error(lang() === "zh" ? "该标的当前没有可用K线数据" : "No K-line data available for this instrument");
  }
  upsertIntelChartPayload(candles);
  host.innerHTML = renderIntelCandlePanel(appState.intel.chartPayloads);
  bindIntelMarketCards(page);
  const queryInput = page.querySelector("[data-intel-instrument-query]");
  if (queryInput) queryInput.value = String(item.symbol || query || "");
  return item;
}

async function loadIntelCandlePanel() {
  const page = document.getElementById("intel-center");
  if (!page) return;
  const feedback = page.querySelector("[data-intel-feedback]");
  const query = String(page.querySelector("[data-intel-instrument-query]")?.value || "").trim();
  if (!query) {
    if (feedback) feedback.textContent = lang() === "zh" ? "请先输入标的代码，例如 AAPL / SPY / ^GSPC。" : "Enter a symbol first, e.g. AAPL / SPY / ^GSPC.";
    return;
  }
  try {
    const item = await loadIntelChartByQuery(query);
    if (feedback) feedback.textContent = lang() === "zh" ? `已加载 ${item.symbol} K线。` : `Loaded ${item.symbol} candlestick chart.`;
  } catch (error) {
    if (feedback) feedback.textContent = authErrorMessage(error.message);
    const host = page.querySelector("[data-intel-candle]");
    if (host && !host.innerHTML.trim()) host.innerHTML = renderIntelCandlePanel(appState.intel.chartPayloads);
  }
}

function bindIntelMarketCards(page) {
  (page || document.getElementById("intel-center"))?.querySelectorAll("[data-intel-market-card]").forEach((card) => {
    if (card.dataset.bound === "1") return;
    card.dataset.bound = "1";
    const trigger = async () => {
      const symbol = String(card.getAttribute("data-symbol") || "").trim();
      const marketStatus = String(card.getAttribute("data-market-status") || "").trim();
      if (!symbol) return;
      const feedback = page?.querySelector("[data-intel-feedback]");
      try {
        if (feedback) feedback.textContent = lang() === "zh" ? `正在加载 ${symbol} K线...` : `Loading ${symbol} chart...`;
        const item = await loadIntelChartByQuery(symbol, { marketStatus });
        if (feedback) feedback.textContent = lang() === "zh" ? `已加载 ${item.symbol} K线。` : `Loaded ${item.symbol} candlestick chart.`;
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    };
    card.addEventListener("click", trigger);
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        trigger();
      }
    });
  });
}

function setIntelFeedbackState(page, message, state = "") {
  const feedbackNode = page?.querySelector?.("[data-intel-feedback]");
  if (!feedbackNode) return;
  feedbackNode.textContent = message || "";
  if (state) feedbackNode.dataset.state = state;
  else delete feedbackNode.dataset.state;
}

function setIntelButtonState(button, state = "") {
  if (!button) return;
  button.classList.remove("is-loading", "is-success", "is-error");
  button.disabled = false;
  if (state === "loading") {
    button.classList.add("is-loading");
    button.disabled = true;
    return;
  }
  if (state === "success") {
    button.classList.add("is-success");
    return;
  }
  if (state === "error") button.classList.add("is-error");
}

async function runIntelAction(page, button, action, messages = {}) {
  setIntelButtonState(button, "loading");
  setIntelFeedbackState(page, messages.loading || (lang() === "zh" ? "处理中..." : "Processing..."), "loading");
  try {
    const actionMessage = await action();
    setIntelButtonState(button, "success");
    setIntelFeedbackState(page, String(actionMessage || messages.success || (lang() === "zh" ? "已完成。" : "Done.")), "success");
  } catch (error) {
    setIntelButtonState(button, "error");
    setIntelFeedbackState(page, authErrorMessage(error.message), "error");
  } finally {
    window.setTimeout(() => setIntelButtonState(button, ""), 1200);
  }
}

async function loadIntelligenceCenterPage(options = {}) {
  ensureWorkMgmtPagesShell();
  const page = document.getElementById("intel-center");
  if (!page) return;
  const clearFeedback = options?.clearFeedback !== false;
  const locale = String(page.querySelector("[data-intel-lang]")?.value || lang() || "zh");
  const category = String(page.querySelector("[data-intel-category]")?.value || "");
  const window = String(page.querySelector("[data-intel-window]")?.value || "24h");
  const summaryNode = page.querySelector("[data-intel-summary]");
  const marketsNode = page.querySelector("[data-intel-markets]");
  const candleNode = page.querySelector("[data-intel-candle]");
  const newsNode = page.querySelector("[data-intel-news]");
  const detailNode = page.querySelector("[data-intel-news-detail]");
  const stateLayerNode = page.querySelector("[data-intel-state-layer]");
  const updatedNode = page.querySelector("[data-intel-page-updated]");
  const qualityStripNode = page.querySelector("[data-intel-quality-strip]");
  const cacheKey = `intel:center:last:${locale}:${window}:${category || "all"}`;
  const showLoading = options?.showLoading !== false;
  if (showLoading && stateLayerNode) {
    stateLayerNode.innerHTML = renderStateLayer(options?.syncing ? "syncing" : "loading", { rows: 4 });
  }
  if (!appState.intel.savedNewsIds.length) {
    try {
      const saved = JSON.parse(localStorage.getItem("intel:center:saved_news") || "[]");
      if (Array.isArray(saved)) appState.intel.savedNewsIds = saved.filter(Boolean).slice(0, 60);
    } catch {}
  }
  const renderNewsDetailFromState = () => {
    const rows = appState.intel.lastTopNews?.data?.items || appState.intel.lastTopNews?.items || [];
    const filtered = filteredIntelNewsItems(rows);
    if (!appState.intel.selectedNewsId && filtered.length) {
      appState.intel.selectedNewsId = intelNewsKey(filtered[0]);
    }
    const selected = filtered.find((item) => intelNewsKey(item) === appState.intel.selectedNewsId) || filtered[0] || null;
    if (detailNode) detailNode.innerHTML = renderIntelNewsDetailPanel(selected);
    syncIntelSidePanels(page, filtered);
  };
  try {
    const cachedText = localStorage.getItem(cacheKey);
    if (cachedText) {
      const cached = JSON.parse(cachedText);
      appState.intel.lastDailyBrief = cached?.brief || null;
      appState.intel.lastMarketsOverview = cached?.markets || null;
      appState.intel.lastTopNews = cached?.topNews || null;
      appState.intel.lastMacroRates = cached?.macroRates || null;
      appState.intel.lastMacroCandlePayload = cached?.macroCandle || null;
      appState.intel.selectedMacroSymbol = String(cached?.selectedMacroSymbol || appState.intel.selectedMacroSymbol || "");
      if (summaryNode && !summaryNode.innerHTML.trim()) summaryNode.innerHTML = renderIntelSummary(cached?.brief || {}, cached?.topNews || {});
      if (marketsNode && !marketsNode.innerHTML.trim()) {
        marketsNode.innerHTML = renderIntelMarkets(cached?.markets || {});
        bindIntelMarketCards(page);
      }
      if (newsNode && !newsNode.innerHTML.trim()) newsNode.innerHTML = renderIntelNews(cached?.topNews || {});
      if (qualityStripNode && !qualityStripNode.innerHTML.trim()) qualityStripNode.innerHTML = renderIntelQualityStrip(cached?.topNews || {}, cached?.markets || {});
      renderNewsDetailFromState();
      bindIntelNewsCards(page);
      if (candleNode && !candleNode.innerHTML.trim()) {
        const cachedCandleStackText = localStorage.getItem("intel:center:chart_stack");
        if (cachedCandleStackText) {
          const candlePayloads = JSON.parse(cachedCandleStackText);
          if (Array.isArray(candlePayloads) && candlePayloads.some((item) => Array.isArray(item?.data?.bars) && item.data.bars.length)) {
            appState.intel.chartPayloads = candlePayloads;
            appState.intel.lastCandlePayload = candlePayloads[0] || null;
            candleNode.innerHTML = renderIntelCandlePanel(candlePayloads);
          }
        }
      }
      if (updatedNode) updatedNode.textContent = formatDateTime(Math.floor(Date.now() / 1000));
    }
  } catch {}
  try {
    const [brief, markets, topNews, macroRates] = await Promise.all([
      loadIntelDailyBrief(locale),
      loadIntelMarketsOverview(locale),
      loadIntelNewsTop(window, 30, locale, category),
      ensureIntelMacroRatesOverview(locale),
    ]);
    appState.intel.lastDailyBrief = brief;
    appState.intel.lastMarketsOverview = markets;
    appState.intel.lastTopNews = topNews;
    appState.intel.lastMacroRates = macroRates;
    try {
      await loadIntelMacroCandle(appState.intel.selectedMacroSymbol || "");
    } catch {
      appState.intel.lastMacroCandlePayload = null;
    }
    if (summaryNode) summaryNode.innerHTML = renderIntelSummary(brief, topNews);
    if (marketsNode) marketsNode.innerHTML = renderIntelMarkets(markets);
    if (candleNode) candleNode.innerHTML = renderIntelCandlePanel(appState.intel.chartPayloads);
    if (newsNode) newsNode.innerHTML = renderIntelNews(topNews);
    if (qualityStripNode) qualityStripNode.innerHTML = renderIntelQualityStrip(topNews, markets);
    renderNewsDetailFromState();
    bindIntelNewsCards(page);
    bindIntelMarketCards(page);
    renderPlatformCommandStrip();
    if (updatedNode) updatedNode.textContent = formatDateTime(topNews?.data?.generatedAt || Math.floor(Date.now() / 1000));
    try {
      const cachedPayload = {
        brief,
        markets,
        topNews,
        macroRates,
        macroCandle: appState.intel.lastMacroCandlePayload,
        selectedMacroSymbol: appState.intel.selectedMacroSymbol,
      };
      localStorage.setItem(cacheKey, JSON.stringify(cachedPayload));
    } catch {}
    if (clearFeedback) setIntelFeedbackState(page, "", "");
    if (stateLayerNode) stateLayerNode.innerHTML = "";
  } catch (error) {
    const msg = authErrorMessage(error.message);
    setIntelFeedbackState(page, msg, "error");
    if (stateLayerNode) {
      const raw = String(error?.message || "").toLowerCase();
      const noPermission = raw.includes("authentication_required") || raw.includes("permission_denied") || raw.includes("admin_required");
      stateLayerNode.innerHTML = renderStateLayer(noPermission ? "no-permission" : "error", { detail: msg });
    }
    if (summaryNode && !summaryNode.innerHTML.trim()) summaryNode.innerHTML = `<div class="auth-feedback">${escapeHtml(msg)}</div>`;
    // Keep the last successful market/news panels visible when refresh fails,
    // so users don't experience a blank page on transient auth/network errors.
  }
}

function ensureWorkChatShell() {
  const tabs = document.querySelector(".page-tabs");
  if (tabs && !tabs.querySelector("[data-page='work-chat']")) {
    const button = document.createElement("button");
    button.className = "tab-btn";
    button.type = "button";
    button.dataset.page = "work-chat";
    button.textContent = topNavLabels()["work-chat"];
    tabs.appendChild(button);
    button.addEventListener("click", () => setActivePage("work-chat", true));
  }
  const main = document.querySelector("main.container");
  if (!main || document.getElementById("work-chat")) return;
  const section = document.createElement("section");
  section.id = "work-chat";
  section.className = "page";
  section.innerHTML = `
    <section class="work-chat-page card">
      <aside class="work-chat-sidebar">
        <div class="work-chat-head">
          <div>
            <div class="eyebrow">${lang() === "zh" ? "Secure Team Chat" : "Secure Team Chat"}</div>
            <h1>${lang() === "zh" ? "协作会话" : "Collaboration"}</h1>
          </div>
          <span class="tag" data-work-chat-admin-badge hidden>${lang() === "zh" ? "管理员全部会话" : "Admin All Sessions"}</span>
        </div>
        <div class="work-chat-actions">
          <button class="btn btn-primary" type="button" data-chat-create="group">${lang() === "zh" ? "创建群聊" : "New Group"}</button>
          <button class="btn btn-ghost" type="button" data-chat-create="direct">${lang() === "zh" ? "发起私聊" : "New Direct"}</button>
          <button class="btn btn-ghost" type="button" data-chat-refresh>${lang() === "zh" ? "刷新" : "Refresh"}</button>
        </div>
        <div class="work-chat-list" data-work-chat-list></div>
      </aside>
      <section class="work-chat-main">
        <div class="work-chat-detail" data-work-chat-detail>
          <div class="work-chat-empty-state">
            <img src="${themedFastoneLogo("full")}" alt="FASTONE" class="work-chat-empty-icon" />
            <div class="auth-note">${lang() === "zh" ? "选择一个会话，或创建群聊 / 私聊开始。" : "Select a conversation, or create a group / direct chat to begin."}</div>
          </div>
        </div>
      </section>
    </section>
  `;
  main.appendChild(section);
}

function currentRouteKey() {
  const file = location.pathname.split("/").pop() || "index.html";
  return file.includes("skills-top20")
    ? "skills"
    : file.includes("skill-uk-hk-financial-contract-counsel")
      ? "legal"
      : file.includes("index")
        ? "index"
        : "console";
}

function currentLangRoute(nextLang) {
  const suffix = `?platform=${encodeURIComponent(appState.currentSkillId)}#${appState.currentPage}`;
  return `${LANG_ROUTES[nextLang][currentRouteKey()]}${suffix}`;
}

function fastoneAsset(name) {
  return `./assets/${name}`;
}

function fastoneLogoAsset(name) {
  return `./public/assets/logo/${name}`;
}

function fastoneThemeMode() {
  const mode = String(document.body?.dataset.theme || document.documentElement?.dataset.theme || "dark").toLowerCase();
  return mode === "light" ? "light" : "dark";
}

function themedFastoneLogo(kind = "full") {
  const mode = fastoneThemeMode();
  if (kind === "mark") return fastoneLogoAsset(mode === "light" ? "fastone-logo-light.png" : "fastone-logo-dark.png");
  return fastoneLogoAsset(mode === "light" ? "fastone-logo-light.png" : "fastone-logo-dark.png");
}

function applyFastoneBranding() {
  const zh = lang() === "zh";
  const pageLabelMap = zh
    ? { index: "首页", console: "工作平台", legal: "法务平台", skills: "技能中心" }
    : { index: "Home", console: "Workspace", legal: "Legal", skills: "Skills Hub" };
  document.title = `FASTONE Capital Operations Platform · ${pageLabelMap[currentRouteKey()] || (zh ? "工作平台" : "Workspace")}`;
  document.querySelectorAll(".brand-text").forEach((node) => {
    let img = node.querySelector(".fastone-top-logo-img");
    if (!img) {
      node.innerHTML = `<img class="fastone-top-logo-img" src="" alt="FASTONE INTERNATIONAL" />`;
      img = node.querySelector(".fastone-top-logo-img");
    }
    if (img) img.src = themedFastoneLogo("full");
  });
  document.querySelectorAll(".brand-mark").forEach((node) => {
    let img = node.querySelector(".fastone-mark-img");
    if (!img) {
      node.innerHTML = `<img class="fastone-mark-img" src="" alt="FASTONE" />`;
      img = node.querySelector(".fastone-mark-img");
    }
    if (img) img.src = themedFastoneLogo("mark");
  });
  // Normalize top-left brand area to one logo only.
  document.querySelectorAll(".topbar .brand").forEach((brandNode) => {
    if (brandNode.dataset.logoNormalized === "1") return;
    const mark = brandNode.querySelector(".brand-mark");
    if (mark) mark.remove();
    brandNode.classList.add("brand--single-logo");
    brandNode.dataset.logoNormalized = "1";
  });
  document.querySelectorAll(".auth-fastone-logo").forEach((node) => {
    node.src = themedFastoneLogo("full");
  });
  document.querySelectorAll(".institutional-rail__brand img").forEach((node) => {
    node.src = themedFastoneLogo("full");
  });
  const heroEyebrow = document.querySelector(".hero-panel .eyebrow");
  if (heroEyebrow) heroEyebrow.textContent = zh ? "FASTONE 资本运营平台" : "FASTONE CAPITAL OPERATIONS PLATFORM";
}

function ensureTopActionSwitches() {
  const host = document.querySelector(".top-actions");
  if (!host) return;
  host.querySelectorAll(".topbar-controls:not([data-core-switches])").forEach((node) => node.remove());
  host.querySelectorAll(":scope > button").forEach((button) => {
    const keep =
      button.hasAttribute("data-auth-account")
      || button.hasAttribute("data-auth-pending-approval")
      || button.hasAttribute("data-auth-team-status")
      || button.hasAttribute("data-auth-admin")
      || button.hasAttribute("data-auth-logout");
    if (!keep) button.remove();
  });
  let controls = host.querySelector("[data-core-switches]");
  if (!controls) {
    controls = document.createElement("div");
    controls.className = "topbar-controls";
    controls.dataset.coreSwitches = "1";
    controls.innerHTML = `
      <div class="compact-switch lang-switch" role="group" aria-label="Language">
        <button type="button" class="switch-pill" data-lang-switch="zh">CN</button>
        <button type="button" class="switch-pill" data-lang-switch="en">ENG</button>
      </div>
      <div class="compact-switch theme-switch" role="group" aria-label="Theme">
        <button type="button" class="icon-toggle" data-theme-toggle-mode="light" aria-label="Light theme">☀</button>
        <button type="button" class="icon-toggle" data-theme-toggle-mode="dark" aria-label="Dark theme">☾</button>
      </div>
    `;
    host.appendChild(controls);
  } else if (host.lastElementChild !== controls) {
    host.appendChild(controls);
  }
}

function insertBeforeCoreSwitches(host, node) {
  const controls = host.querySelector("[data-core-switches]");
  if (controls) {
    host.insertBefore(node, controls);
    return;
  }
  host.appendChild(node);
}

function canManageUserApprovals() {
  const user = appState.auth.user;
  if (!user) return false;
  if (user.role === "admin") return true;
  const permissions = user.permissions;
  return !!(permissions && typeof permissions === "object" && permissions.user_admin);
}

async function fetchPendingApprovalUsers() {
  if (!canManageUserApprovals()) return [];
  const resp = await fetch("/api/admin/users");
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "admin_required");
  const users = Array.isArray(payload.users) ? payload.users : [];
  appState.adminPending.directory = users;
  return users.filter((item) => String(item?.approval_status || "approved") === "pending");
}

async function submitUserApprovalAction(identifier, action, extra = {}) {
  const body = { identifier, action, ...(extra || {}) };
  const resp = await fetch("/api/admin/users/approval", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
  return payload;
}

function pendingApprovalBubbleText(count) {
  const c = Number(count || 0);
  if (lang() === "zh") return `批准 ${c}`;
  return `Approve ${c}`;
}

function platformLabel(item) {
  return lang() === "zh" ? item.zh : item.en;
}

function approvalConfigDefaults(user) {
  const permissions = user?.permissions || {};
  const currentPlatforms = Array.isArray(permissions.platforms)
    ? permissions.platforms.filter((item) => item && item !== "*")
    : [];
  const currentColleagues = Array.isArray(permissions.colleagues)
    ? permissions.colleagues.filter((item) => item && item !== "*")
    : [];
  return {
    platforms: currentPlatforms.length ? currentPlatforms : ["financial-analysis", "work-chat"],
    colleagues: currentColleagues,
  };
}

function renderApprovalConfigBlocks(user) {
  const defaults = approvalConfigDefaults(user);
  const platformChecks = APPROVAL_PLATFORM_OPTIONS.map((item) => `
    <label class="pending-config-check">
      <input type="checkbox" name="approval_platform" value="${escapeHtml(item.id)}" ${defaults.platforms.includes(item.id) ? "checked" : ""} />
      <span>${escapeHtml(platformLabel(item))}</span>
    </label>
  `).join("");
  const targetEmail = String(user?.email || "").toLowerCase();
  const colleagueCandidates = (appState.adminPending.directory || [])
    .filter((item) => String(item?.approval_status || "approved") === "approved")
    .filter((item) => String(item?.email || "").toLowerCase() !== targetEmail);
  const colleagueChecks = colleagueCandidates.map((item) => {
    const email = String(item.email || "");
    const label = item.display_name || item.username || email;
    return `
      <label class="pending-config-check">
        <input type="checkbox" name="approval_colleague" value="${escapeHtml(email)}" ${defaults.colleagues.includes(email) ? "checked" : ""} />
        <span>${escapeHtml(label)} <em>${escapeHtml(email)}</em></span>
      </label>
    `;
  }).join("");
  return `
    <div class="pending-config-grid">
      <div class="pending-config-col">
        <strong>${lang() === "zh" ? "先勾选可访问工作平台（必选）" : "Select allowed workspaces first (required)"}</strong>
        <div class="pending-config-list">${platformChecks}</div>
      </div>
      <div class="pending-config-col">
        <strong>${lang() === "zh" ? "勾选可见同事（必选）" : "Select visible colleagues (required)"}</strong>
        <div class="pending-config-list">${colleagueChecks || `<div class="auth-note">${lang() === "zh" ? "当前没有可选同事，请先创建并批准同事账号。" : "No colleagues available yet. Create and approve colleagues first."}</div>`}</div>
      </div>
    </div>
    <label class="auth-field" style="margin-top:8px;">
      <span>${lang() === "zh" ? "拒绝备注（可选）" : "Reject note (optional)"}</span>
      <input type="text" name="reject_reason" autocomplete="off" placeholder="${escapeHtml(lang() === "zh" ? "例如：资料不完整，需补充" : "e.g. Missing information, please resubmit")}" />
    </label>
  `;
}

function buildApprovalPermissionsFromCard(card) {
  const selectedPlatforms = Array.from(card.querySelectorAll("input[name='approval_platform']:checked")).map((node) => String(node.value || "").trim()).filter(Boolean);
  const selectedColleagues = Array.from(card.querySelectorAll("input[name='approval_colleague']:checked")).map((node) => String(node.value || "").trim().toLowerCase()).filter(Boolean);
  const pages = Array.from(new Set(["home", ...APPROVAL_PLATFORM_OPTIONS.filter((item) => selectedPlatforms.includes(item.id)).map((item) => item.page || "home")]));
  return {
    pages,
    platforms: selectedPlatforms,
    colleagues: selectedColleagues,
    user_admin: false,
    view_team_status: false,
    view_document_flows: selectedPlatforms.includes("doc-flow"),
  };
}

function renderPendingApprovalQuickPanel(users) {
  const copy = authCopy();
  if (!users.length) {
    return `<div class="auth-note">${lang() === "zh" ? "当前没有待批准注册。" : "There are no pending registrations."}</div>`;
  }
  return `
    <div class="admin-pending-panel">
      <div class="admin-pending-panel__head">
        <div>
          <strong>${copy.pendingApprovals || "Pending Registrations"}</strong>
          <span>${copy.pendingApprovalsNote || ""}</span>
        </div>
        <span class="admin-pending-bubble">${users.length}</span>
      </div>
      <div class="admin-pending-list">
        ${users.map((user) => `
          <div class="admin-pending-item" data-user-identifier="${escapeHtml(user.email || user.username || "")}">
            <div>
              <strong>${escapeHtml(user.display_name || user.username || user.email || "")}</strong>
              <span>${escapeHtml(user.email || "")} · ${escapeHtml(user.phone || "--")}</span>
            </div>
            ${renderApprovalConfigBlocks(user)}
            <div class="admin-pending-actions">
              <button class="btn btn-primary" type="button" data-quick-approve="1">${lang() === "zh" ? "配置并批准" : "Configure & Approve"}</button>
              <button class="btn btn-ghost" type="button" data-quick-reject="1">${copy.rejectUser || "Reject"}</button>
            </div>
            <div class="auth-feedback" data-quick-feedback></div>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}

function bindPendingApprovalQuickPanel(panel) {
  panel.querySelectorAll(".admin-pending-item").forEach((card) => {
    const identifier = card.dataset.userIdentifier || "";
    const feedback = card.querySelector("[data-quick-feedback]");
    card.querySelector("[data-quick-approve]")?.addEventListener("click", async () => {
      try {
        const permissions = buildApprovalPermissionsFromCard(card);
        if (!permissions.platforms.length) throw new Error("approval_platforms_required");
        if (!permissions.colleagues.length) throw new Error("approval_colleagues_required");
        await submitUserApprovalAction(identifier, "approve", { permissions });
        await refreshPendingApprovalBubble({ autoPopup: false });
        openPendingApprovalBubblePanel();
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
    card.querySelector("[data-quick-reject]")?.addEventListener("click", async () => {
      const sure = window.confirm(lang() === "zh" ? "确认拒绝该注册申请？被拒绝用户将无法登录。": "Reject this registration? Rejected users cannot sign in.");
      if (!sure) return;
      try {
        const rejectReason = String(card.querySelector("input[name='reject_reason']")?.value || "").trim();
        await submitUserApprovalAction(identifier, "reject", { reason: rejectReason });
        await refreshPendingApprovalBubble({ autoPopup: false });
        openPendingApprovalBubblePanel();
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
  });
}

function openPendingApprovalBubblePanel() {
  const copy = authCopy();
  const users = Array.isArray(appState.adminPending.users) ? appState.adminPending.users : [];
  const panel = ensureOverlayPanel(copy.pendingApprovals || "Pending Registrations", renderPendingApprovalQuickPanel(users));
  bindPendingApprovalQuickPanel(panel);
}

async function refreshPendingApprovalBubble({ autoPopup = false } = {}) {
  if (!appState.auth.authenticated || !canManageUserApprovals()) {
    appState.adminPending.users = [];
    appState.adminPending.count = 0;
    ensureAuthControls();
    return;
  }
  try {
    const users = await fetchPendingApprovalUsers();
    appState.adminPending.users = users;
    appState.adminPending.count = users.length;
    ensureAuthControls();
    if (autoPopup && users.length > 0 && !appState.adminPending.autoPopupShown) {
      appState.adminPending.autoPopupShown = true;
      openPendingApprovalBubblePanel();
    }
  } catch {}
}

function startPendingApprovalPolling() {
  if (appState.adminPending.timer) clearInterval(appState.adminPending.timer);
  if (!appState.auth.authenticated || !canManageUserApprovals()) return;
  appState.adminPending.timer = setInterval(() => {
    refreshPendingApprovalBubble({ autoPopup: false }).catch(() => {});
  }, 30000);
}

function bindLanguageSwitch() {
  document.querySelectorAll("[data-lang-switch]").forEach((button) => {
    if (button.dataset.boundLangSwitch === "1") return;
    button.dataset.boundLangSwitch = "1";
    button.addEventListener("click", () => {
      const nextLang = button.getAttribute("data-lang-switch");
      if (!nextLang || nextLang === lang()) return;
      location.href = currentLangRoute(nextLang);
    });
  });
  document.querySelectorAll("[data-lang-switch]").forEach((button) => {
    button.classList.toggle("is-active", button.getAttribute("data-lang-switch") === lang());
    button.setAttribute("aria-pressed", button.classList.contains("is-active") ? "true" : "false");
  });
}

function themeLabel(theme) {
  if (lang() === "zh") {
    return theme === "dark" ? "浅色模式" : "深色模式";
  }
  return theme === "dark" ? "Light Mode" : "Dark Mode";
}

function authCopy() {
  if (lang() === "zh") {
    return {
      title: "本地安全登录",
      loginTab: "登录",
      registerTab: "注册",
      welcomeEyebrow: "FASTONE · HERMES AI AGENT",
      welcomeTitle: "欢迎进入 FASTONE Hermes AI Agent",
      welcomeText: "登录后进入企业工作平台，统一处理财务分析、法务审阅、协同沟通与审批流。系统在本地安全环境中持续记录与追踪执行过程。",
      registerText: "首次使用请完成注册。注册时需提供邮箱、手机号码和登录密码。",
      registerPending: "注册申请已提交，正在等待管理员批准。批准前暂不能登录使用。",
      email: "邮箱",
      identifier: "邮箱或用户名",
      username: "用户名",
      phone: "手机号码",
      password: "密码",
      confirmPassword: "确认密码",
      displayName: "姓名或称呼（选填）",
      loginButton: "登录进入工作台",
      registerButton: "注册并进入工作台",
      loggingIn: "登录中...",
      registering: "注册中...",
      switchToRegister: "没有账号？立即注册",
      switchToLogin: "已有账号？直接登录",
      legalNote: "本地登录仅用于本机访问控制，不替代你已配置的业务系统授权。",
      summaryTitle: "欢迎词",
      summaryBody: "欢迎回来。今日工作流已就绪，登录后可直接进入你的专属工作空间。",
      loggedInAs: "当前用户",
      logout: "退出登录",
      account: "账号设置",
      admin: "账号管理",
      authLanguage: "语言",
      changePassword: "修改密码",
      currentPassword: "当前密码",
      newPassword: "新密码",
      savePassword: "保存新密码",
      saving: "保存中...",
      passwordSaved: "密码已更新。",
      adminSummary: "管理员可查看登录态与工作态，并统一管理账号权限与密码策略。",
      adminSchedule: "日报于每日 08:00 自动生成；月报于每月最后一天 10:00 自动生成，并提供 Excel 下载。",
      adminUsersTitle: "账号与权限",
      pendingApprovals: "待批准注册",
      pendingApprovalsNote: "以下注册者需管理员批准后才能登录使用；拒绝后账号不可使用。",
      approveUser: "批准",
      rejectUser: "拒绝",
      approvalStatus: "审批状态",
      approvalPending: "待批准",
      approvalApproved: "已批准",
      approvalRejected: "已拒绝",
      adminCreateUser: "添加账号",
      adminCreateUserNote: "管理员可以直接创建本地账号，并指定角色与基础权限。",
      createUserButton: "创建账号",
      userCreated: "账号已创建。",
      adminReportsTitle: "运行报表",
      dailyActivityReport: "每日在线/离线时长报告",
      monthlyActivityReport: "月度工作统计报告",
      monthlyDownload: "下载 Excel 月报",
      monthlyWorkCount: "工作总次数",
      monthlyExportCount: "输出文件总数",
      monthlyLoginCount: "登录次数",
      monthlyExportedFiles: "输出文件",
      monthlyMostUsedPlatform: "最常用平台",
      monthlyAnomalyTitle: "本月异常摘要",
      monthlyLowActivity: "低活跃用户",
      monthlyInactiveUsers: "未登录用户",
      monthlyExportWatch: "导出异常",
      monthlyHighExport: "高频导出",
      reportDate: "报告日期",
      reportMonth: "统计月份",
      generatedAt: "生成时间",
      onlineDuration: "在线时长",
      offlineDuration: "离线时长",
      onlineRatio: "整体在线占比",
      topActiveUsers: "昨日最活跃 3 人",
      mostlyOfflineUsers: "昨日几乎未登录人员",
      anomalyAlerts: "异常预警",
      anomalyConsecutiveLow: "连续两天几乎未登录",
      anomalyLowYesterday: "昨日在线异常偏低",
      anomalyHighYesterday: "昨日在线异常偏高",
      teamSearch: "搜索登录人状态",
      teamSearchPlaceholder: "搜索姓名、邮箱、用户名、平台、动作或在线状态",
      none: "无",
      activityPending: "系统将于每天早上 8:00 自动生成上一日的在线/离线时长报告。",
      teamStatus: "团队状态",
      grantTeamStatus: "允许查看团队状态",
      currentPlatform: "当前所在平台",
      currentAction: "当前动作",
      idleRemaining: "剩余空闲时间",
      onlineLight: "状态灯",
      permissionDenied: "当前账号没有查看团队状态的权限。",
      role: "角色",
      permissions: "权限",
      loginStatus: "登录状态",
      workStatus: "工作状态",
      resetPassword: "重置密码",
      deleteUser: "删除账号",
      savePermissions: "保存权限",
      close: "关闭",
      loggedIn: "在线",
      loggedOut: "离线",
      lastSeen: "最近活动",
      noStatus: "暂无工作状态",
    };
  }
  return {
    title: "Local Secure Access",
    loginTab: "Login",
    registerTab: "Register",
    welcomeEyebrow: "FASTONE · HERMES AI AGENT",
    welcomeTitle: "Welcome to FASTONE Hermes AI Agent",
    welcomeText: "Sign in to access the enterprise workspace for finance, legal review, collaboration, and approvals. Activity is tracked in a secure local environment for reliable execution.",
      registerText: "First-time users should register with email, mobile number, and a password.",
      registerPending: "Registration submitted. Please wait for administrator approval before signing in.",
      email: "Email",
      identifier: "Email or Username",
      username: "Username",
      phone: "Mobile Number",
    password: "Password",
    confirmPassword: "Confirm Password",
    displayName: "Name (optional)",
    loginButton: "Sign In to Workspace",
    registerButton: "Register and Enter",
    loggingIn: "Signing in...",
    registering: "Registering...",
    switchToRegister: "No account yet? Register now",
    switchToLogin: "Already registered? Sign in",
    legalNote: "Local sign-in controls device access only. It does not replace your connected business-system authorizations.",
    summaryTitle: "Welcome Note",
    summaryBody: "Welcome back. Your core workflows are ready. Sign in to continue in your dedicated workspace.",
    loggedInAs: "Signed in as",
    logout: "Log Out",
    account: "Account",
    admin: "Admin",
    authLanguage: "Language",
    changePassword: "Change Password",
    currentPassword: "Current Password",
    newPassword: "New Password",
    savePassword: "Save Password",
    saving: "Saving...",
    passwordSaved: "Password updated.",
    adminSummary: "Admins can review login and workspace activity, and centrally manage permissions and password policy.",
    adminSchedule: "The daily report is generated automatically at 08:00 each day, and the monthly report is generated at 10:00 on the last day of each month with Excel download.",
    adminUsersTitle: "Accounts & Permissions",
    pendingApprovals: "Pending Registrations",
    pendingApprovalsNote: "These users need administrator approval before they can sign in. Rejected users cannot use the workspace.",
    approveUser: "Approve",
    rejectUser: "Reject",
    approvalStatus: "Approval Status",
    approvalPending: "Pending",
    approvalApproved: "Approved",
    approvalRejected: "Rejected",
    adminCreateUser: "Add Account",
    adminCreateUserNote: "Administrators can create local accounts directly and assign role and baseline permissions.",
    createUserButton: "Create Account",
    userCreated: "Account created.",
    adminReportsTitle: "Operational Reports",
    dailyActivityReport: "Daily Online / Offline Duration Report",
    monthlyActivityReport: "Monthly Work Activity Report",
    monthlyDownload: "Download Excel",
    monthlyWorkCount: "Total Work Count",
    monthlyExportCount: "Total Exports",
    monthlyLoginCount: "Login Count",
    monthlyExportedFiles: "Exported Files",
    monthlyMostUsedPlatform: "Most Used Platform",
    monthlyAnomalyTitle: "Monthly Anomaly Summary",
    monthlyLowActivity: "Low Activity",
    monthlyInactiveUsers: "No Login",
    monthlyExportWatch: "Export Watch",
    monthlyHighExport: "High Export",
    reportDate: "Report Date",
    reportMonth: "Report Month",
    generatedAt: "Generated At",
    onlineDuration: "Online Duration",
    offlineDuration: "Offline Duration",
    onlineRatio: "Overall Online Ratio",
    topActiveUsers: "Top 3 Active Yesterday",
    mostlyOfflineUsers: "Mostly Offline Yesterday",
    anomalyAlerts: "Anomaly Alerts",
    anomalyConsecutiveLow: "Almost inactive for 2 consecutive days",
    anomalyLowYesterday: "Unusually low online time yesterday",
    anomalyHighYesterday: "Unusually high online time yesterday",
    teamSearch: "Search Team Status",
    teamSearchPlaceholder: "Search name, email, username, platform, action, or status",
    none: "None",
    activityPending: "The system generates the previous day's online/offline duration report automatically every day at 8:00 AM.",
    teamStatus: "Team Status",
    grantTeamStatus: "Allow team status visibility",
    currentPlatform: "Current Platform",
    currentAction: "Current Action",
    idleRemaining: "Idle Remaining",
    onlineLight: "Status Light",
    permissionDenied: "This account is not allowed to view team status.",
    role: "Role",
    permissions: "Permissions",
    loginStatus: "Login Status",
    workStatus: "Work Status",
    resetPassword: "Reset Password",
    deleteUser: "Delete User",
    savePermissions: "Save Permissions",
    close: "Close",
    loggedIn: "Online",
    loggedOut: "Offline",
    lastSeen: "Last Seen",
    noStatus: "No work status reported",
  };
}

function authErrorMessage(code) {
  const zh = {
    invalid_email: "邮箱格式不正确。",
    invalid_phone: "手机号码格式不正确。",
    password_too_short: "密码至少需要 8 位。",
    email_already_exists: "该邮箱已经注册。",
    user_not_found: "未找到该邮箱对应的账号。",
    invalid_password: "密码不正确。",
    invalid_username: "用户名格式不正确，只能使用字母、数字、点、下划线或横线。",
    username_already_exists: "该用户名已被使用。",
    passwords_do_not_match: "两次输入的密码不一致。",
    authentication_required: "请先登录后再继续。",
    admin_required: "需要管理员权限。",
    cannot_delete_admin: "不能删除管理员账号。",
    invalid_user_record: "账号记录异常，请联系管理员。",
    permission_denied: "没有权限查看该会话。",
    read_only_access: "当前账号只有查看权限，不能发送消息。",
    direct_chat_requires_two_users: "私聊必须且只能包含两位用户。",
    group_chat_requires_two_or_more_users: "群聊至少需要三位用户。",
    group_chat_requires_three_or_more_users: "群聊至少需要三位用户。",
    empty_message: "消息不能为空。",
    conversation_not_found: "未找到该会话。",
    title_required: "请填写文件标题。",
    workflow_requires_reviewer_or_approver: "至少需要指定审阅人或审批人。",
    change_request_reason_required: "已签字归档文件重新发起变更流程时，必须填写修改说明。",
    document_not_found: "未找到该文件流程。",
    workflow_not_found: "未找到对应流程。",
    file_required: "请上传文件或填写文本内容。",
    invalid_file_payload: "文件内容读取失败，请重新上传。",
    file_too_large: "文件过大，请上传 25MB 以内文件。",
    shared_file_not_found: "未找到要更新的共享文件，请刷新后重试。",
    file_version_not_found: "未找到该文件版本。",
    file_storage_failed: "文件保存失败，请稍后重试。",
    file_not_found: "文件不存在或已被清理。",
    review_step_required: "当前节点不是审阅节点，不能执行该操作。",
    approval_step_required: "当前节点不是审批节点，不能执行该操作。",
    sign_step_required: "当前节点不是签字节点，不能执行该操作。",
    no_pending_step_for_user: "当前账号没有待处理的流程节点。",
    document_locked: "文件已签字归档，不能直接修改。",
    based_on_document_not_found: "未找到原始签字文件。",
    notification_not_found: "未找到该通知。",
    version_not_found: "未找到该文件版本。",
    document_decrypt_failed: "签字归档文件读取失败。",
    account_pending_approval: "注册申请正在等待管理员批准。批准前暂不能登录使用。",
    account_rejected: "该注册申请已被管理员拒绝，账号不可使用。",
    approval_permissions_required: "批准前必须先配置工作平台和可见同事。",
    approval_platforms_required: "请先勾选至少一个可访问工作平台。",
    approval_colleagues_required: "请先勾选至少一位可见同事。",
    unsupported_action: "当前操作暂不支持。",
    no_new_messages: "没有新增消息可用于生成摘要。",
    summary_generation_failed: "摘要生成失败，系统已回退到安全路径，请稍后重试。",
    message_not_found: "未找到该消息。",
    invalid_mode: "清理模式无效。",
    message_ids_required: "请至少提供一条消息 ID。",
    invalid_policy_window: "保留策略时间窗口无效（需满足归档 <= 软删 <= 硬删）。",
    invalid_view: "消息视图参数无效。",
  };
  const en = {
    invalid_email: "The email format is invalid.",
    invalid_phone: "The mobile number format is invalid.",
    password_too_short: "Password must be at least 8 characters.",
    email_already_exists: "This email is already registered.",
    user_not_found: "No account was found for this email.",
    invalid_password: "The password is incorrect.",
    invalid_username: "Username is invalid. Use letters, numbers, dots, underscores, or hyphens only.",
    username_already_exists: "This username is already in use.",
    passwords_do_not_match: "The two passwords do not match.",
    authentication_required: "Please sign in first.",
    admin_required: "Administrator access is required.",
    cannot_delete_admin: "The administrator account cannot be deleted.",
    invalid_user_record: "The account record is invalid. Please contact the administrator.",
    permission_denied: "You do not have permission to view this conversation.",
    read_only_access: "This account has read-only access and cannot send messages.",
    direct_chat_requires_two_users: "A direct chat must include exactly two users.",
    group_chat_requires_two_or_more_users: "A group chat requires at least three users.",
    group_chat_requires_three_or_more_users: "A group chat requires at least three users.",
    empty_message: "Message content is required.",
    conversation_not_found: "Conversation was not found.",
    title_required: "A document title is required.",
    workflow_requires_reviewer_or_approver: "At least one reviewer or approver is required.",
    change_request_reason_required: "A signed document must include a change reason before a new workflow can start.",
    document_not_found: "Document workflow was not found.",
    workflow_not_found: "The workflow record was not found.",
    file_required: "Please upload a file or provide text content.",
    invalid_file_payload: "The file payload could not be read. Please upload it again.",
    file_too_large: "File is too large. Please upload a file under 25MB.",
    shared_file_not_found: "The shared file to update was not found. Refresh and try again.",
    file_version_not_found: "The file version was not found.",
    file_storage_failed: "Failed to store the file. Please try again.",
    file_not_found: "The file does not exist or was cleaned up.",
    review_step_required: "This action is only available on a review step.",
    approval_step_required: "This action is only available on an approval step.",
    sign_step_required: "This action is only available on a signing step.",
    no_pending_step_for_user: "There is no pending workflow step for this account.",
    document_locked: "This document has been signed and archived, so it cannot be edited directly.",
    based_on_document_not_found: "The original signed document could not be found.",
    notification_not_found: "Notification was not found.",
    version_not_found: "Document version was not found.",
    document_decrypt_failed: "The signed archive could not be opened.",
    account_pending_approval: "This registration is still waiting for administrator approval.",
    account_rejected: "This registration was rejected by an administrator and cannot be used.",
    approval_permissions_required: "You must configure workspace and colleague access before approval.",
    approval_platforms_required: "Select at least one allowed workspace before approval.",
    approval_colleagues_required: "Select at least one visible colleague before approval.",
    unsupported_action: "This action is not supported yet.",
    no_new_messages: "No new messages are available for summary generation.",
    summary_generation_failed: "Summary generation failed. A safe fallback path was used. Please retry.",
    message_not_found: "Message was not found.",
    invalid_mode: "Invalid cleanup mode.",
    message_ids_required: "Please provide at least one message id.",
    invalid_policy_window: "Invalid retention policy window (archive <= soft-delete <= hard-delete).",
    invalid_view: "Invalid message view parameter.",
  };
  return (lang() === "zh" ? zh : en)[code] || code || (lang() === "zh" ? "操作失败，请稍后再试。" : "Request failed. Please try again.");
}

function authSchemeOptions() {
  const zh = lang() === "zh";
  return [
    { id: "a", label: zh ? "A 机构深色" : "A Institutional Dark" },
    { id: "b", label: zh ? "B 纸面浅色" : "B Paper Light" },
    { id: "c", label: zh ? "C 指挥分栏" : "C Command Split" },
  ];
}

function currentAuthScheme() {
  try {
    const raw = String(localStorage.getItem(AUTH_SCHEME_KEY) || "a").trim().toLowerCase();
    if (raw === "b" || raw === "c") return raw;
  } catch {}
  return "a";
}

function applyAuthScheme(shell, scheme) {
  if (!shell) return;
  const card = shell.querySelector(".auth-card");
  if (!card) return;
  const next = ["a", "b", "c"].includes(String(scheme || "").toLowerCase()) ? String(scheme || "").toLowerCase() : "a";
  card.classList.remove("auth-card--scheme-a", "auth-card--scheme-b", "auth-card--scheme-c");
  card.classList.add(`auth-card--scheme-${next}`);
  shell.querySelectorAll("[data-auth-scheme]").forEach((button) => {
    const active = String(button.getAttribute("data-auth-scheme") || "") === next;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  });
  try { localStorage.setItem(AUTH_SCHEME_KEY, next); } catch {}
}

function ensureAuthShell() {
  let shell = document.getElementById("authShell");
  if (shell) return shell;
  const copy = authCopy();
  const scheme = "a";
  const schemeOptions = authSchemeOptions();
  shell = document.createElement("div");
  shell.id = "authShell";
  shell.className = "auth-shell";
  shell.innerHTML = `
    <div class="auth-backdrop"></div>
    <div class="auth-card auth-card--scheme-${escapeHtml(scheme)}">
      <section class="auth-welcome">
        <div class="auth-lang-switch">
          <span>${copy.authLanguage}</span>
          <div class="auth-lang-actions">
            <button class="btn ${lang() === "zh" ? "btn-primary" : "btn-ghost"}" type="button" data-auth-lang="zh">${lang() === "zh" ? "中文" : "Chinese"}</button>
            <button class="btn ${lang() === "en" ? "btn-primary" : "btn-ghost"}" type="button" data-auth-lang="en">English</button>
          </div>
        </div>
        <div class="auth-scheme-switch">
          <span>${lang() === "zh" ? "登录方案" : "Login Scheme"}</span>
          <div class="auth-scheme-actions">
            ${schemeOptions.map((item) => `
              <button class="btn ${item.id === scheme ? "btn-primary active" : "btn-ghost"}" type="button" data-auth-scheme="${escapeHtml(item.id)}" aria-pressed="${item.id === scheme ? "true" : "false"}">${escapeHtml(item.label)}</button>
            `).join("")}
          </div>
        </div>
        <div class="auth-brand-lockup">
          <img src="${themedFastoneLogo("full")}" alt="FASTONE" class="auth-fastone-logo" />
        </div>
        <div class="eyebrow">${copy.welcomeEyebrow}</div>
        <h1>${copy.welcomeTitle}</h1>
        <p>${copy.welcomeText}</p>
        <div class="auth-summary-card">
          <span>${copy.summaryTitle}</span>
          <strong>${copy.summaryBody}</strong>
        </div>
        <div class="auth-kpi-strip">
          <span class="auth-kpi-chip">${lang() === "zh" ? "待审批优先处理" : "Approval queue first"}</span>
          <span class="auth-kpi-chip">${lang() === "zh" ? "MFA / SSO 已启用" : "MFA / SSO enabled"}</span>
          <span class="auth-kpi-chip">${lang() === "zh" ? "审计链路实时留痕" : "Audit trail always on"}</span>
        </div>
        <div class="auth-note">${copy.legalNote}</div>
      </section>
      <section class="auth-panel">
        <div class="auth-tabs">
          <button class="tab-btn active" type="button" data-auth-tab="login">${copy.loginTab}</button>
          <button class="tab-btn" type="button" data-auth-tab="register">${copy.registerTab}</button>
        </div>
        <form class="auth-form auth-form-login" data-auth-form="login" autocomplete="off" autocapitalize="none" spellcheck="false">
          <label class="auth-field">
            <span>${copy.identifier}</span>
            <input type="text" name="identifier" autocomplete="off" autocapitalize="none" spellcheck="false" required />
          </label>
          <label class="auth-field">
            <span>${copy.password}</span>
            <input type="password" name="password" autocomplete="off" autocapitalize="none" spellcheck="false" data-lpignore="true" data-1p-ignore="true" data-bwignore="true" required />
          </label>
          <button class="btn btn-primary auth-submit" type="submit">${copy.loginButton}</button>
          <button class="auth-switch" type="button" data-auth-switch="register">${copy.switchToRegister}</button>
        </form>
        <form class="auth-form auth-form-register auth-hidden" data-auth-form="register" autocomplete="off" autocapitalize="none" spellcheck="false">
          <label class="auth-field">
            <span>${copy.email}</span>
            <input type="email" name="email" autocomplete="email" required />
          </label>
          <label class="auth-field">
            <span>${copy.username}</span>
            <input type="text" name="username" autocomplete="username" />
          </label>
          <label class="auth-field">
            <span>${copy.phone}</span>
            <input type="tel" name="phone" autocomplete="tel" required />
          </label>
          <label class="auth-field">
            <span>${copy.displayName}</span>
            <input type="text" name="display_name" autocomplete="name" />
          </label>
          <label class="auth-field">
            <span>${copy.password}</span>
            <input type="password" name="password" autocomplete="new-password" autocapitalize="none" spellcheck="false" data-lpignore="true" data-1p-ignore="true" data-bwignore="true" required />
          </label>
          <label class="auth-field">
            <span>${copy.confirmPassword}</span>
            <input type="password" name="confirm_password" autocomplete="new-password" autocapitalize="none" spellcheck="false" data-lpignore="true" data-1p-ignore="true" data-bwignore="true" required />
          </label>
          <div class="auth-register-note">${copy.registerText}</div>
          <button class="btn btn-primary auth-submit" type="submit">${copy.registerButton}</button>
          <button class="auth-switch" type="button" data-auth-switch="login">${copy.switchToLogin}</button>
        </form>
        <div class="auth-feedback" data-auth-feedback></div>
      </section>
    </div>
  `;
  document.body.appendChild(shell);

  const setTab = (nextTab) => {
    shell.querySelectorAll("[data-auth-tab]").forEach((button) => {
      const active = button.dataset.authTab === nextTab;
      button.classList.toggle("active", active);
    });
    shell.querySelectorAll("[data-auth-form]").forEach((form) => {
      form.classList.toggle("auth-hidden", form.dataset.authForm !== nextTab);
    });
    const feedback = shell.querySelector("[data-auth-feedback]");
    if (feedback) feedback.textContent = "";
  };

  shell.querySelectorAll("[data-auth-tab]").forEach((button) => {
    button.addEventListener("click", () => setTab(button.dataset.authTab || "login"));
  });
  shell.querySelectorAll("[data-auth-switch]").forEach((button) => {
    button.addEventListener("click", () => setTab(button.dataset.authSwitch || "login"));
  });
  shell.querySelectorAll("[data-auth-lang]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextLang = button.dataset.authLang === "en" ? "en" : "zh";
      if (nextLang !== lang()) location.href = currentLangRoute(nextLang);
    });
  });
  shell.querySelectorAll("[data-auth-scheme]").forEach((button) => {
    button.addEventListener("click", () => {
      const next = String(button.getAttribute("data-auth-scheme") || "a");
      applyAuthScheme(shell, next);
    });
  });

  shell.querySelector("[data-auth-form='login']")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const button = form.querySelector(".auth-submit");
    const feedback = shell.querySelector("[data-auth-feedback]");
    const formData = new FormData(form);
    button.disabled = true;
    button.textContent = authCopy().loggingIn;
    try {
      const resp = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          identifier: String(formData.get("identifier") || "").trim(),
          password: String(formData.get("password") || ""),
        }),
      });
      const payload = await resp.json();
      if (!resp.ok || !payload.ok) throw new Error(payload.error || "login_failed");
      if (payload.session_token) sessionStorage.setItem(AUTH_TOKEN_KEY, payload.session_token);
      appState.auth.authenticated = true;
      appState.auth.user = payload.user || null;
      appState.auth.idleTimeoutSeconds = Number(payload.idle_timeout_seconds || (appState.auth.user?.role === "admin" ? 120 : 180));
      appState.auth.lastActivityAt = Date.now();
      appState.auth.lastHeartbeatAt = 0;
      form.reset();
      hideAuthShell();
      await bootWorkbench();
    } catch (error) {
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    } finally {
      button.disabled = false;
      button.textContent = authCopy().loginButton;
    }
  });

  shell.querySelector("[data-auth-form='register']")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const button = form.querySelector(".auth-submit");
    const feedback = shell.querySelector("[data-auth-feedback]");
    const formData = new FormData(form);
    const password = String(formData.get("password") || "");
    const confirmPassword = String(formData.get("confirm_password") || "");
    if (password !== confirmPassword) {
      if (feedback) feedback.textContent = authErrorMessage("passwords_do_not_match");
      return;
    }
    button.disabled = true;
    button.textContent = authCopy().registering;
    try {
      const resp = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: String(formData.get("email") || "").trim(),
          username: String(formData.get("username") || "").trim(),
          phone: String(formData.get("phone") || "").trim(),
          display_name: String(formData.get("display_name") || "").trim(),
          password,
        }),
      });
      const payload = await resp.json();
      if (!resp.ok || !payload.ok) throw new Error(payload.error || "register_failed");
      form.reset();
      if (feedback) feedback.textContent = authCopy().registerPending || authErrorMessage("account_pending_approval");
    } catch (error) {
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    } finally {
      button.disabled = false;
      button.textContent = authCopy().registerButton;
    }
  });

  return shell;
}

function showAuthShell() {
  const shell = ensureAuthShell();
  clearAuthPasswordFields(shell);
  shell.hidden = false;
  document.body.classList.add("auth-locked");
}

function hideAuthShell() {
  const shell = document.getElementById("authShell");
  if (!shell) return;
  shell.hidden = true;
  document.body.classList.remove("auth-locked");
}

function clearAuthPasswordFields(shell = document.getElementById("authShell")) {
  if (!shell) return;
  shell.querySelectorAll("input[type='password']").forEach((input) => {
    input.value = "";
  });
}

async function loadAuthSession() {
  const resp = await fetch("/api/auth/session");
  const payload = await resp.json();
  appState.auth.authenticated = !!payload.authenticated;
  appState.auth.user = payload.user || null;
  appState.auth.idleTimeoutSeconds = Number(payload.idle_timeout_seconds || 0);
  appState.adminPending.autoPopupShown = false;
  return payload;
}

function noteAuthActivity() {
  if (!appState.auth.authenticated) return;
  appState.auth.lastActivityAt = Date.now();
  updateAuthIdleWarning();
}

async function performLogout({ reload = false, timedOut = false } = {}) {
  try {
    await fetch("/api/auth/logout", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
  } catch {}
  localStorage.removeItem(AUTH_TOKEN_KEY);
  sessionStorage.removeItem(AUTH_TOKEN_KEY);
  appState.auth.authenticated = false;
  appState.auth.user = null;
  appState.auth.idleTimeoutSeconds = 0;
  appState.auth.lastActivityAt = 0;
  appState.auth.lastHeartbeatAt = 0;
  if (appState.authHeartbeatTimer) clearInterval(appState.authHeartbeatTimer);
  if (appState.authIdleTimer) clearInterval(appState.authIdleTimer);
  if (appState.cronStatusTimer) clearInterval(appState.cronStatusTimer);
  if (appState.statusRefreshTimer) clearInterval(appState.statusRefreshTimer);
  if (appState.workChat.refreshTimer) clearInterval(appState.workChat.refreshTimer);
  if (appState.adminPending.timer) clearInterval(appState.adminPending.timer);
  appState.authHeartbeatTimer = null;
  appState.authIdleTimer = null;
  appState.cronStatusTimer = null;
  appState.statusRefreshTimer = null;
  appState.workChat.refreshTimer = null;
  appState.adminPending.timer = null;
  appState.adminPending.users = [];
  appState.adminPending.count = 0;
  appState.adminPending.autoPopupShown = false;
  closeOverlayPanel();
  ensureAuthShell();
  const shell = document.getElementById("authShell");
  const feedback = shell?.querySelector("[data-auth-feedback]");
  if (feedback) {
    feedback.textContent = timedOut
      ? (lang() === "zh" ? "因长时间无工作动作，当前账号已自动退出。" : "You were signed out automatically due to inactivity.")
      : "";
  }
  clearAuthPasswordFields(shell);
  updateAuthIdleWarning();
  showAuthShell();
  if (reload) location.reload();
}

function bindAuthActivityTracking() {
  if (appState.authActivityBound) return;
  appState.authActivityBound = true;
  const mark = () => noteAuthActivity();
  ["pointerdown", "keydown", "input", "change", "submit"].forEach((eventName) => {
    document.addEventListener(eventName, mark, true);
  });
}

function ensureAuthControls() {
  const host = document.querySelector(".top-actions");
  if (!host || !appState.auth.authenticated || !appState.auth.user) return;
  const copy = authCopy();
  const controls = host.querySelector("[data-core-switches]");
  if (!host.querySelector("[data-auth-user]")) {
    const chip = document.createElement("span");
    chip.className = "dock-chip";
    chip.dataset.authUser = "1";
    const anchor = host.querySelector("[data-auth-account]")
      || host.querySelector("[data-auth-team-status]")
      || host.querySelector("[data-auth-admin]")
      || host.querySelector("[data-auth-logout]")
      || controls
      || null;
    host.insertBefore(chip, anchor);
  }
  if (!host.querySelector("[data-auth-account]")) {
    const button = document.createElement("button");
    button.className = "btn btn-ghost";
    button.type = "button";
    button.dataset.authAccount = "1";
    button.addEventListener("click", openAccountCenter);
    insertBeforeCoreSwitches(host, button);
  }
  const canManageApprovals = canManageUserApprovals();
  if (canManageApprovals && !host.querySelector("[data-auth-pending-approval]")) {
    const button = document.createElement("button");
    button.className = "dock-chip auth-pending-bubble";
    button.type = "button";
    button.dataset.authPendingApproval = "1";
    button.addEventListener("click", openPendingApprovalBubblePanel);
    insertBeforeCoreSwitches(host, button);
  }
  if (!canManageApprovals) {
    host.querySelectorAll("[data-auth-pending-approval]").forEach((node) => node.remove());
  }
  if (appState.auth.user?.permissions?.view_team_status && !host.querySelector("[data-auth-team-status]")) {
    const button = document.createElement("button");
    button.className = "btn btn-ghost";
    button.type = "button";
    button.dataset.authTeamStatus = "1";
    button.addEventListener("click", openTeamStatusCenter);
    insertBeforeCoreSwitches(host, button);
  }
  if (appState.auth.user?.role === "admin" && !host.querySelector("[data-auth-admin]")) {
    const button = document.createElement("button");
    button.className = "btn btn-ghost";
    button.type = "button";
    button.dataset.authAdmin = "1";
    button.addEventListener("click", openAdminCenter);
    insertBeforeCoreSwitches(host, button);
  }
  if (!host.querySelector("[data-auth-logout]")) {
    const button = document.createElement("button");
    button.className = "btn btn-ghost";
    button.type = "button";
    button.dataset.authLogout = "1";
    button.addEventListener("click", async () => {
      await performLogout({ reload: true });
    });
    insertBeforeCoreSwitches(host, button);
  }
  if (!host.querySelector("[data-auth-idle-warning]")) {
    const chip = document.createElement("span");
    chip.className = "dock-chip auth-idle-warning";
    chip.dataset.authIdleWarning = "1";
    chip.hidden = true;
    host.insertBefore(chip, host.querySelector("[data-auth-logout]") || null);
  }
  const chip = host.querySelector("[data-auth-user]");
  const account = host.querySelector("[data-auth-account]");
  const pending = host.querySelector("[data-auth-pending-approval]");
  const teamStatus = host.querySelector("[data-auth-team-status]");
  const admin = host.querySelector("[data-auth-admin]");
  const logout = host.querySelector("[data-auth-logout]");
  if (chip) {
    const displayName = appState.auth.user.display_name || appState.auth.user.username || appState.auth.user.email || "";
    chip.textContent = displayName.toUpperCase();
  }
  if (account) account.textContent = copy.account;
  if (pending) {
    pending.textContent = pendingApprovalBubbleText(appState.adminPending.count || 0);
    pending.hidden = Number(appState.adminPending.count || 0) <= 0;
  }
  if (teamStatus) teamStatus.textContent = copy.teamStatus;
  if (admin) admin.textContent = copy.admin;
  if (logout) logout.textContent = copy.logout;
  if (chip && logout && chip.nextElementSibling !== logout) host.insertBefore(chip, logout);
  const latestControls = host.querySelector("[data-core-switches]");
  if (latestControls && host.lastElementChild !== latestControls) {
    host.appendChild(latestControls);
  }
  ensureTopNavLayout();
  updateAuthIdleWarning();
}

function authIdleWarningLabel(seconds) {
  const remaining = Math.max(0, Math.ceil(Number(seconds || 0)));
  return lang() === "zh"
    ? `空闲退出 ${remaining}s`
    : `Auto sign-out ${remaining}s`;
}

function updateAuthIdleWarning() {
  const node = document.querySelector("[data-auth-idle-warning]");
  if (!node) return;
  if (!appState.auth.authenticated || !appState.auth.lastActivityAt || !appState.auth.idleTimeoutSeconds) {
    node.hidden = true;
    node.textContent = "";
    return;
  }
  const elapsed = Math.max(0, Math.floor((Date.now() - appState.auth.lastActivityAt) / 1000));
  const remaining = Math.max(0, Number(appState.auth.idleTimeoutSeconds || 0) - elapsed);
  if (remaining > 30) {
    node.hidden = true;
    node.textContent = "";
    return;
  }
  node.hidden = false;
  node.textContent = authIdleWarningLabel(remaining);
}

function closeOverlayPanel() {
  const existing = document.getElementById("authOverlayPanel");
  if (existing) existing.remove();
}

function ensureOverlayPanel(title, bodyHtml) {
  closeOverlayPanel();
  const panel = document.createElement("div");
  panel.id = "authOverlayPanel";
  panel.className = "overlay-panel";
  panel.innerHTML = `
    <div class="overlay-panel__backdrop" data-overlay-close="1"></div>
    <div class="overlay-panel__card">
      <div class="overlay-panel__head">
        <strong>${escapeHtml(title)}</strong>
        <button class="btn btn-ghost" type="button" data-overlay-close="1">${authCopy().close}</button>
      </div>
      <div class="overlay-panel__body">${bodyHtml}</div>
    </div>
  `;
  panel.querySelectorAll("[data-overlay-close]").forEach((node) => {
    node.addEventListener("click", closeOverlayPanel);
  });
  document.body.appendChild(panel);
  return panel;
}

function formatDateTime(seconds) {
  if (!seconds) return "--";
  const date = new Date(Number(seconds) * 1000);
  return date.toLocaleString(lang() === "zh" ? "zh-CN" : "en-US", { hour12: false });
}

function formatIdleSeconds(seconds) {
  const total = Math.max(0, Number(seconds || 0));
  if (!total) return "--";
  const mins = Math.floor(total / 60);
  const secs = total % 60;
  if (lang() === "zh") return mins > 0 ? `${mins}分 ${secs}秒` : `${secs}秒`;
  return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
}

function formatDurationLong(seconds) {
  const total = Math.max(0, Number(seconds || 0));
  const hours = total / 3600;
  if (lang() === "zh") return `${hours.toFixed(2)} 小时`;
  return `${hours.toFixed(2)} h`;
}

function formatHoursValue(value) {
  const hours = Math.max(0, Number(value || 0));
  return `${hours.toFixed(2)}${lang() === "zh" ? " 小时" : " h"}`;
}

function idleSeverityClass(seconds, loggedIn = true) {
  if (!loggedIn) return "";
  const remaining = Math.max(0, Number(seconds || 0));
  if (remaining <= 10) return "is-critical";
  if (remaining <= 30) return "is-warning";
  return "is-normal";
}

async function openAccountCenter() {
  const copy = authCopy();
  const user = appState.auth.user || {};
  const panel = ensureOverlayPanel(copy.account, `
    <div class="account-panel">
      <div class="account-panel__summary">
        <div><span>Email</span><strong>${escapeHtml(user.email || "--")}</strong></div>
        <div><span>${escapeHtml(copy.role)}</span><strong>${escapeHtml(user.role || "user")}</strong></div>
      </div>
      <form class="account-password-form" autocomplete="off" autocapitalize="none" spellcheck="false">
        <label class="auth-field">
          <span>${copy.currentPassword}</span>
          <input type="password" name="current_password" autocomplete="new-password" autocapitalize="none" spellcheck="false" data-lpignore="true" data-1p-ignore="true" data-bwignore="true" required />
        </label>
        <label class="auth-field">
          <span>${copy.newPassword}</span>
          <input type="password" name="new_password" autocomplete="new-password" autocapitalize="none" spellcheck="false" data-lpignore="true" data-1p-ignore="true" data-bwignore="true" required />
        </label>
        <button class="btn btn-primary" type="submit">${copy.savePassword}</button>
        <div class="auth-feedback" data-account-feedback></div>
      </form>
    </div>
  `);
  panel.querySelector(".account-password-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const button = form.querySelector("button[type='submit']");
    const feedback = panel.querySelector("[data-account-feedback]");
    const formData = new FormData(form);
    button.disabled = true;
    button.textContent = copy.saving;
    try {
      const resp = await fetch("/api/auth/password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          current_password: String(formData.get("current_password") || ""),
          new_password: String(formData.get("new_password") || ""),
        }),
      });
      const payload = await resp.json();
      if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
      if (feedback) feedback.textContent = copy.passwordSaved;
      form.reset();
    } catch (error) {
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    } finally {
      button.disabled = false;
      button.textContent = copy.savePassword;
    }
  });
}

function renderAdminUsersTable(users) {
  const copy = authCopy();
  const flowLabel = lang() === "zh" ? "允许查看文件流程" : "Allow document-flow visibility";
  const approvalLabels = {
    pending: copy.approvalPending || "Pending",
    approved: copy.approvalApproved || "Approved",
    rejected: copy.approvalRejected || "Rejected",
  };
  return users.map((user) => {
    const login = user.login_status || {};
    const work = login.work_status || {};
    const logged = login.logged_in ? copy.loggedIn : copy.loggedOut;
    const platformText = work.page || work.workspace || copy.noStatus;
    const actionText = work.skill_id || copy.noStatus;
    const idleText = login.logged_in ? formatIdleSeconds(login.idle_remaining_seconds) : "--";
    const idleClass = idleSeverityClass(login.idle_remaining_seconds, login.logged_in);
    const pages = (user.permissions?.pages || []).join(",");
    const platforms = (user.permissions?.platforms || []).join(",");
    const canViewTeamStatus = !!user.permissions?.view_team_status;
    const canViewDocumentFlows = !!user.permissions?.view_document_flows;
    const approvalStatus = user.approval_status || "approved";
    return `
      <div class="admin-user-card ${approvalStatus === "pending" ? "admin-user-card--pending" : ""} ${approvalStatus === "rejected" ? "admin-user-card--rejected" : ""}" data-user-identifier="${escapeHtml(user.email || user.username || "")}">
        <div class="admin-user-card__head">
          <div>
            <strong>${escapeHtml(user.display_name || user.username || user.email)}</strong>
            <div class="admin-user-card__meta">${escapeHtml(user.email || "")} · ${escapeHtml(user.username || "--")}</div>
          </div>
          <div class="tag-row admin-user-card__badges">
            <span class="tag">${escapeHtml(user.role || "user")}</span>
            <span class="tag approval-tag is-${escapeHtml(approvalStatus)}">${escapeHtml(approvalLabels[approvalStatus] || approvalStatus)}</span>
          </div>
        </div>
        <div class="admin-user-card__grid">
          <div><span>${copy.approvalStatus || "Approval"}</span><strong>${escapeHtml(approvalLabels[approvalStatus] || approvalStatus)}</strong></div>
          <div><span>${copy.onlineLight}</span><strong><span class="status-dot ${login.logged_in ? "is-online" : "is-offline"}"></span>${escapeHtml(logged)}</strong></div>
          <div><span>${copy.lastSeen}</span><strong>${escapeHtml(formatDateTime(login.last_seen_at))}</strong></div>
          <div><span>${copy.currentPlatform}</span><strong>${escapeHtml(platformText)}</strong></div>
          <div><span>${copy.currentAction}</span><strong>${escapeHtml(actionText)}</strong></div>
          <div class="admin-idle-cell ${idleClass}"><span>${copy.idleRemaining}</span><strong>${escapeHtml(idleText)}</strong></div>
          <div class="admin-user-card__wide"><span>${copy.workStatus}</span><strong>${escapeHtml([work.provider, work.model].filter(Boolean).join(" / ") || copy.noStatus)}</strong></div>
        </div>
        <div class="admin-user-card__permissions">
          <label class="auth-field">
            <span>${copy.role}</span>
            <select name="role">
              <option value="user" ${user.role === "user" ? "selected" : ""}>user</option>
              <option value="admin" ${user.role === "admin" ? "selected" : ""}>admin</option>
            </select>
          </label>
          <label class="auth-field">
            <span>Pages</span>
            <input type="text" name="pages" value="${escapeHtml(pages)}" />
          </label>
          <label class="auth-field">
            <span>Platforms</span>
            <input type="text" name="platforms" value="${escapeHtml(platforms)}" />
          </label>
          <label class="auth-field admin-user-card__toggle">
            <span>${copy.grantTeamStatus}</span>
            <input type="checkbox" name="view_team_status" ${canViewTeamStatus ? "checked" : ""} />
          </label>
          <label class="auth-field admin-user-card__toggle">
            <span>${flowLabel}</span>
            <input type="checkbox" name="view_document_flows" ${canViewDocumentFlows ? "checked" : ""} />
          </label>
        </div>
        <div class="admin-user-card__actions">
          ${approvalStatus !== "rejected" && user.role !== "admin" ? `<button class="btn btn-ghost" type="button" data-admin-reject="1">${copy.rejectUser || "Reject"}</button>` : ""}
          <button class="btn btn-ghost" type="button" data-admin-reset="1">${copy.resetPassword}</button>
          <button class="btn btn-primary" type="button" data-admin-save="1">${copy.savePermissions}</button>
          ${user.role === "admin" ? "" : `<button class="btn btn-ghost" type="button" data-admin-delete="1">${copy.deleteUser}</button>`}
        </div>
        <div class="auth-feedback" data-admin-feedback></div>
      </div>
    `;
  }).join("");
}

function renderAdminCreateUserForm() {
  const copy = authCopy();
  const flowLabel = lang() === "zh" ? "允许查看文件流程" : "Allow document-flow visibility";
  return `
    <div class="admin-user-card admin-create-user-card">
      <div class="admin-user-card__head">
        <div>
          <strong>${copy.adminCreateUser}</strong>
          <div class="admin-user-card__meta">${copy.adminCreateUserNote}</div>
        </div>
      </div>
      <form class="admin-create-user-form" autocomplete="off" autocapitalize="none" spellcheck="false">
        <div class="admin-user-card__permissions">
          <label class="auth-field">
            <span>${copy.email}</span>
            <input type="email" name="email" autocomplete="off" required />
          </label>
          <label class="auth-field">
            <span>${copy.username}</span>
            <input type="text" name="username" autocomplete="off" />
          </label>
          <label class="auth-field">
            <span>${copy.phone}</span>
            <input type="tel" name="phone" autocomplete="off" required />
          </label>
          <label class="auth-field">
            <span>${copy.displayName}</span>
            <input type="text" name="display_name" autocomplete="off" />
          </label>
          <label class="auth-field">
            <span>${copy.password}</span>
            <input type="password" name="password" autocomplete="new-password" data-lpignore="true" data-1p-ignore="true" data-bwignore="true" required />
          </label>
          <label class="auth-field">
            <span>${copy.role}</span>
            <select name="role">
              <option value="user">user</option>
              <option value="admin">admin</option>
            </select>
          </label>
          <label class="auth-field">
            <span>Pages</span>
            <input type="text" name="pages" value="*" />
          </label>
          <label class="auth-field">
            <span>Platforms</span>
            <input type="text" name="platforms" value="*" />
          </label>
          <label class="auth-field admin-user-card__toggle">
            <span>${copy.grantTeamStatus}</span>
            <input type="checkbox" name="view_team_status" />
          </label>
          <label class="auth-field admin-user-card__toggle">
            <span>${flowLabel}</span>
            <input type="checkbox" name="view_document_flows" />
          </label>
        </div>
        <div class="admin-user-card__actions">
          <button class="btn btn-primary" type="submit">${copy.createUserButton}</button>
        </div>
        <div class="auth-feedback" data-admin-create-feedback></div>
      </form>
    </div>
  `;
}

function renderPendingApprovals(users) {
  const copy = authCopy();
  const pending = (users || []).filter((user) => (user.approval_status || "approved") === "pending");
  if (!pending.length) return "";
  return `
    <div class="admin-pending-panel">
      <div class="admin-pending-panel__head">
        <div>
          <strong>${copy.pendingApprovals || "Pending Registrations"}</strong>
          <span>${copy.pendingApprovalsNote || ""}</span>
        </div>
        <span class="admin-pending-bubble">${pending.length}</span>
      </div>
      <div class="admin-pending-list">
        ${pending.map((user) => `
          <div class="admin-pending-item" data-user-identifier="${escapeHtml(user.email || user.username || "")}">
            <div>
              <strong>${escapeHtml(user.display_name || user.username || user.email)}</strong>
              <span>${escapeHtml(user.email || "")} · ${escapeHtml(user.phone || "--")} · ${escapeHtml(formatDateTime(user.created_at))}</span>
            </div>
            ${renderApprovalConfigBlocks(user)}
            <div class="admin-pending-actions">
              <button class="btn btn-primary" type="button" data-admin-approve="1">${lang() === "zh" ? "配置并批准" : "Configure & Approve"}</button>
              <button class="btn btn-ghost" type="button" data-admin-reject="1">${copy.rejectUser || "Reject"}</button>
            </div>
            <div class="auth-feedback" data-admin-feedback></div>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}

async function loadAdminUsers() {
  const resp = await fetch("/api/admin/users");
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "admin_required");
  appState.adminUsers = payload.users || [];
  return appState.adminUsers;
}

async function loadAdminActivityReport() {
  const resp = await fetch("/api/admin/activity-report");
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "admin_required");
  return payload;
}

async function loadAdminMonthlyReport() {
  const resp = await fetch("/api/admin/monthly-report");
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "admin_required");
  return payload;
}

async function fetchApiJson(url, options = null) {
  const resp = await fetch(url, options || undefined);
  let payload = {};
  try {
    payload = await resp.json();
  } catch {
    payload = {};
  }
  if (!resp.ok || !payload.ok) {
    const code = String(payload.error || "").trim() || (resp.status === 401 ? "authentication_required" : "request_failed");
    if (resp.status === 401 || code === "authentication_required") {
      await performLogout({ timedOut: true });
      throw new Error("authentication_required");
    }
    throw new Error(code);
  }
  return payload;
}

async function loadV2Workbench(query = "") {
  const url = query ? `/api/v2/dashboard/workbench?${query}` : "/api/v2/dashboard/workbench";
  const payload = await fetchApiJson(url);
  appState.workMgmt.workbench = payload;
  return payload;
}

async function loadV2MyWork() {
  const payload = await fetchApiJson("/api/v2/my-work");
  appState.workMgmt.myWork = payload;
  return payload;
}

async function loadV2Reports(query = "") {
  const url = query ? `/api/v2/reports?${query}` : "/api/v2/reports";
  const payload = await fetchApiJson(url);
  appState.workMgmt.reports = payload.reports || [];
  return payload;
}

async function loadV2ReportDetail(reportId) {
  return fetchApiJson(`/api/v2/reports/${encodeURIComponent(reportId)}`);
}

async function addV2ReportComment(reportId, comment) {
  return fetchApiJson(`/api/v2/reports/${encodeURIComponent(reportId)}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ comment }),
  });
}

async function updateV2ReportStatus(reportId, status, note = "") {
  return fetchApiJson(`/api/v2/reports/${encodeURIComponent(reportId)}/status`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, note }),
  });
}

async function triggerV2ReportGenerate(mode = "daily", force = true) {
  return fetchApiJson("/api/v2/reports/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode, force }),
  });
}

async function loadV2AdminOverview() {
  const payload = await fetchApiJson("/api/v2/admin/overview");
  appState.workMgmt.adminOverview = payload;
  return payload;
}

async function loadV2AdminProjectChatOverview() {
  return fetchApiJson("/api/v2/admin/project-chat-summaries/overview");
}

async function loadV2ProjectChatSummaryCurrent(projectId) {
  return fetchApiJson(`/api/v2/projects/${encodeURIComponent(projectId)}/chat-summary/current`);
}

async function loadV2ProjectChatSummaryHistory(projectId, limit = 50) {
  return fetchApiJson(`/api/v2/projects/${encodeURIComponent(projectId)}/chat-summary/history?limit=${encodeURIComponent(String(limit))}`);
}

async function loadV2ProjectChatMessages(projectId, view = "default", limit = 120) {
  return fetchApiJson(`/api/v2/projects/${encodeURIComponent(projectId)}/chat/messages?view=${encodeURIComponent(view)}&limit=${encodeURIComponent(String(limit))}`);
}

async function generateV2ProjectChatSummary(projectId, payload = {}) {
  return fetchApiJson(`/api/v2/projects/${encodeURIComponent(projectId)}/chat-summary/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
}

async function regenerateV2ProjectChatSummary(projectId, summaryId, payload = {}) {
  return fetchApiJson(`/api/v2/projects/${encodeURIComponent(projectId)}/chat-summary/${encodeURIComponent(summaryId)}/regenerate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
}

async function cleanupV2ProjectChat(projectId, payload = { mode: "all" }) {
  return fetchApiJson(`/api/v2/projects/${encodeURIComponent(projectId)}/chat-summary/cleanup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
}

async function loadV2ProjectChatPolicy(projectId) {
  return fetchApiJson(`/api/v2/projects/${encodeURIComponent(projectId)}/chat-summary/retention-policy`);
}

async function loadV2ProjectChatCleanupLogs(projectId, limit = 80) {
  return fetchApiJson(`/api/v2/projects/${encodeURIComponent(projectId)}/chat-summary/cleanup-logs?limit=${encodeURIComponent(String(limit))}`);
}

async function markV2ProjectChatMessageKey(projectId, messageId, isKey = true) {
  const action = isKey ? "mark-key" : "unmark-key";
  return fetchApiJson(`/api/v2/projects/${encodeURIComponent(projectId)}/chat/messages/${encodeURIComponent(messageId)}/${action}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{}",
  });
}

async function loadV2GlobalSearch(keyword) {
  const q = String(keyword || "").trim();
  if (!q) return { ok: true, projects: [], work_items: [], documents: [] };
  return fetchApiJson(`/api/v2/search?q=${encodeURIComponent(q)}`);
}

async function loadV2FileCenterOverview(scope = "my", workspaceId = "") {
  const params = new URLSearchParams();
  params.set("scope", scope);
  if (workspaceId) params.set("workspace_id", workspaceId);
  return fetchApiJson(`/api/v2/file-center/overview?${params.toString()}`);
}

async function loadV2FileCenterFiles(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters || {}).forEach(([key, value]) => {
    const text = String(value ?? "").trim();
    if (text) params.set(key, text);
  });
  const query = params.toString();
  return fetchApiJson(query ? `/api/v2/file-center/files?${query}` : "/api/v2/file-center/files");
}

async function loadV2FileCenterDetail(fileId) {
  return fetchApiJson(`/api/v2/file-center/files/${encodeURIComponent(fileId)}`);
}

async function createV2FileCenterRecord(payload) {
  return fetchApiJson("/api/v2/file-center/files", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
}

async function createV2FileCenterVersion(fileId, payload) {
  return fetchApiJson(`/api/v2/file-center/files/${encodeURIComponent(fileId)}/versions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
}

async function createV2FileCenterWorkflow(payload) {
  return fetchApiJson("/api/v2/file-center/workflows", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
}

async function actV2FileCenterStep(workflowId, stepId, payload) {
  return fetchApiJson(`/api/v2/file-center/workflows/${encodeURIComponent(workflowId)}/steps/${encodeURIComponent(stepId)}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
}

async function archiveV2FileCenterFile(fileId, reason = "") {
  return fetchApiJson(`/api/v2/file-center/files/${encodeURIComponent(fileId)}/archive`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
}

async function loadV2FileCenterCertificates(userId = "") {
  const query = userId ? `?user_id=${encodeURIComponent(userId)}` : "";
  return fetchApiJson(`/api/v2/file-center/certificates${query}`);
}

async function createV2FileCenterCertificate(payload = {}) {
  return fetchApiJson("/api/v2/file-center/certificates", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
}

async function revokeV2FileCenterCertificate(certificateId, reason = "") {
  return fetchApiJson(`/api/v2/file-center/certificates/${encodeURIComponent(certificateId)}/revoke`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
}

async function loadV2FileCenterMyOverview() {
  return fetchApiJson("/api/v2/file-center/my/overview");
}

async function loadV2FileCenterWorkspaceOverview(workspaceId) {
  return fetchApiJson(`/api/v2/file-center/workspaces/${encodeURIComponent(workspaceId)}/overview`);
}

async function loadV2FileCenterGlobalOverview() {
  return fetchApiJson("/api/v2/file-center/admin/global-overview");
}

async function triggerV2FileCenterDailyDigest(date = "", force = true) {
  return fetchApiJson("/api/v2/file-center/reports/generate-daily", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ date, force }),
  });
}

async function loadV2FileCenterDailyReports(date = "") {
  const query = date ? `?date=${encodeURIComponent(date)}` : "";
  return fetchApiJson(`/api/v2/file-center/reports/daily${query}`);
}

async function loadIntelMarketsOverview(langCode = "zh") {
  return fetchApiJson(`/api/intelligence/markets/overview?lang=${encodeURIComponent(langCode)}`);
}

async function loadIntelDailyBrief(langCode = "zh") {
  return fetchApiJson(`/api/intelligence/daily-brief?lang=${encodeURIComponent(langCode)}`);
}

async function loadIntelNewsTop(window = "24h", limit = 30, langCode = "zh", category = "") {
  const params = new URLSearchParams();
  params.set("window", window || "24h");
  params.set("limit", String(limit || 30));
  params.set("lang", langCode || "zh");
  if (category) params.set("category", category);
  return fetchApiJson(`/api/intelligence/news/top?${params.toString()}`);
}

async function loadIntelMacroRatesOverview(langCode = "zh") {
  const [fxPayload, indexPayload] = await Promise.all([
    searchIntelInstruments("", langCode || "zh", "forex", 100),
    searchIntelInstruments("", langCode || "zh", "index", 100),
  ]);
  const fxItems = Array.isArray(fxPayload?.data?.items) ? fxPayload.data.items : [];
  const idxItems = Array.isArray(indexPayload?.data?.items) ? indexPayload.data.items : [];
  const fxTargets = [
    { symbol: "EURUSD=X", zh: "欧元/美元", en: "EUR/USD" },
    { symbol: "GBPUSD=X", zh: "英镑/美元", en: "GBP/USD" },
    { symbol: "USDJPY=X", zh: "美元/日元", en: "USD/JPY" },
    { symbol: "USDCNH=X", zh: "美元/离岸人民币", en: "USD/CNH" },
    { symbol: "AUDUSD=X", zh: "澳元/美元", en: "AUD/USD" },
    { symbol: "USDCHF=X", zh: "美元/瑞郎", en: "USD/CHF" },
  ];
  const yieldTargets = [
    { symbol: "^FVX", zh: "美国5年国债", en: "US 5Y Treasury" },
    { symbol: "^TNX", zh: "美国10年国债", en: "US 10Y Treasury" },
    { symbol: "^TYX", zh: "美国30年国债", en: "US 30Y Treasury" },
    { symbol: "^UK10Y", zh: "英国10年国债", en: "UK 10Y Gilt" },
    { symbol: "^JP10Y", zh: "日本10年国债", en: "Japan 10Y JGB" },
  ];
  const pickBySymbol = (rows, symbol) => rows.find((item) => String(item?.symbol || "").toUpperCase() === String(symbol || "").toUpperCase());
  const fx = fxTargets.map((target) => {
    const found = pickBySymbol(fxItems, target.symbol);
    return {
      symbol: target.symbol,
      name: langCode === "zh" ? target.zh : target.en,
      instrumentId: String(found?.instrumentId || ""),
      latestPrice: Number(found?.latestPrice || 0),
      changePercent: Number(found?.changePercent || 0),
      quoteTime: Number(found?.quoteTime || 0),
    };
  });
  const sovereignYields = yieldTargets.map((target) => {
    const found = pickBySymbol(idxItems, target.symbol);
    return {
      symbol: target.symbol,
      name: langCode === "zh" ? target.zh : target.en,
      instrumentId: String(found?.instrumentId || ""),
      latestYield: Number(found?.latestPrice || 0),
      changePercent: Number(found?.changePercent || 0),
      quoteTime: Number(found?.quoteTime || 0),
    };
  });
  const lastUpdatedAt = Math.max(
    0,
    ...fx.map((item) => Number(item.quoteTime || 0)),
    ...sovereignYields.map((item) => Number(item.quoteTime || 0)),
  );
  return { ok: true, data: { fx, sovereignYields, lastUpdatedAt } };
}

function intelMacroHasCoverage(payload) {
  const data = payload?.data || payload || {};
  const fx = Array.isArray(data.fx) ? data.fx : [];
  const bonds = Array.isArray(data.sovereignYields) ? data.sovereignYields : [];
  const hasFx = fx.some((row) => Number(row?.latestPrice || 0) > 0);
  const hasBond = bonds.some((row) => Number(row?.latestYield || 0) > 0);
  return { hasFx, hasBond, ok: hasFx && hasBond };
}

async function ensureIntelMacroRatesOverview(langCode = "zh") {
  let payload = await loadIntelMacroRatesOverview(langCode || "zh");
  const coverage = intelMacroHasCoverage(payload);
  if (coverage.ok) return payload;
  try {
    await adminIntelRefreshMarketData({
      instrumentTypes: ["forex", "index"],
      symbols: ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCNH=X", "AUDUSD=X", "USDCHF=X", "^FVX", "^TNX", "^TYX", "^UK10Y", "^JP10Y"],
      refreshCandles: true,
      force: true,
      interval: "1d",
      range: "6mo",
    });
    payload = await loadIntelMacroRatesOverview(langCode || "zh");
  } catch {}
  return payload;
}

async function adminIntelRefreshMarkets(indexCodes = [], force = true) {
  return fetchApiJson("/api/admin/intelligence/markets/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ indexCodes, force }),
  });
}

async function adminIntelRefreshNews(sourceCodes = [], window = "24h", force = true) {
  return fetchApiJson("/api/admin/intelligence/news/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sourceCodes, window, force }),
  });
}

async function adminIntelGenerateDigest(window = "24h", languages = ["zh"], limit = 30, forceRegenerate = true) {
  return fetchApiJson("/api/admin/intelligence/news/generate-digest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ window, languages, limit, forceRegenerate }),
  });
}

async function searchIntelInstruments(q, langCode = "zh", type = "", limit = 20) {
  const params = new URLSearchParams();
  params.set("q", String(q || "").trim());
  params.set("lang", langCode || "zh");
  if (type) params.set("type", type);
  params.set("limit", String(limit || 20));
  return fetchApiJson(`/api/intelligence/instruments/search?${params.toString()}`);
}

async function loadIntelInstrumentDetail(instrumentId, langCode = "zh") {
  return fetchApiJson(`/api/intelligence/instruments/${encodeURIComponent(instrumentId)}?lang=${encodeURIComponent(langCode || "zh")}`);
}

async function loadIntelInstrumentCandles(instrumentId, interval = "1d", range = "6mo", adjusted = true) {
  const params = new URLSearchParams();
  params.set("interval", interval || "1d");
  params.set("range", range || "6mo");
  params.set("adjusted", adjusted ? "true" : "false");
  return fetchApiJson(`/api/intelligence/instruments/${encodeURIComponent(instrumentId)}/candles?${params.toString()}`);
}

async function adminIntelRefreshMarketData(payload = {}) {
  return fetchApiJson("/api/admin/intelligence/market-data/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
}

async function loadTeamStatusUsers(query = "") {
  const url = query ? `/api/team/status?q=${encodeURIComponent(query)}` : "/api/team/status";
  const resp = await fetch(url);
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "permission_denied");
  return payload.users || [];
}

function renderTeamStatusCards(users) {
  const copy = authCopy();
  return users.map((user) => `
    <div class="admin-user-card admin-user-card--team">
      <div class="admin-user-card__head">
        <div>
          <strong>${escapeHtml(user.display_name || user.username || user.email)}</strong>
          <div class="admin-user-card__meta">${escapeHtml(user.email || "")}</div>
        </div>
        <span class="tag">${escapeHtml(user.role || "user")}</span>
      </div>
      <div class="admin-user-card__grid">
        <div><span>${copy.onlineLight}</span><strong><span class="status-dot ${user.logged_in ? "is-online" : "is-offline"}"></span>${escapeHtml(user.logged_in ? copy.loggedIn : copy.loggedOut)}</strong></div>
        <div><span>${copy.lastSeen}</span><strong>${escapeHtml(formatDateTime(user.last_seen_at))}</strong></div>
        <div><span>${copy.currentPlatform}</span><strong>${escapeHtml(user.current_page || user.current_workspace || copy.noStatus)}</strong></div>
        <div><span>${copy.currentAction}</span><strong>${escapeHtml(user.current_action || copy.noStatus)}</strong></div>
        <div><span>${copy.onlineDuration}</span><strong>${escapeHtml(formatHoursValue(user.online_hours))}</strong></div>
        <div><span>${copy.offlineDuration}</span><strong>${escapeHtml(formatHoursValue(user.offline_hours))}</strong></div>
        <div><span>${copy.monthlyWorkCount}</span><strong>${escapeHtml(String(user.work_count ?? 0))}</strong></div>
        <div><span>${copy.monthlyExportCount}</span><strong>${escapeHtml(String(user.export_count ?? 0))}</strong></div>
        <div class="admin-idle-cell ${idleSeverityClass(user.idle_remaining_seconds, user.logged_in)}"><span>${copy.idleRemaining}</span><strong>${escapeHtml(user.logged_in ? formatIdleSeconds(user.idle_remaining_seconds) : "--")}</strong></div>
        <div><span>${copy.workStatus}</span><strong>${escapeHtml([user.provider, user.model].filter(Boolean).join(" / ") || copy.noStatus)}</strong></div>
      </div>
    </div>
  `).join("");
}

function renderAdminActivityReport(report) {
  const copy = authCopy();
  const rows = Array.isArray(report?.users) ? report.users : [];
  const summary = report?.summary || {};
  const topActive = Array.isArray(summary.top_active_users) ? summary.top_active_users : [];
  const mostlyOffline = Array.isArray(summary.mostly_offline_users) ? summary.mostly_offline_users : [];
  const anomalies = summary.anomalies || {};
  const formatSummaryPeople = (items) => items.length
    ? items.map((item) => `${item.display_name || item.email} (${formatDurationLong(item.online_seconds)})`).join(" · ")
    : copy.none;
  const renderAlertLine = (label, items) => `
    <div class="admin-user-card__wide">
      <span>${label}</span>
      <strong>${escapeHtml(formatSummaryPeople(Array.isArray(items) ? items : []))}</strong>
    </div>
  `;
  const list = rows.length ? rows.map((user) => `
    <div class="admin-user-card__grid" style="margin-top:10px;">
      <div><span>${escapeHtml(user.display_name || user.email || "--")}</span><strong>${escapeHtml(user.email || "--")}</strong></div>
      <div><span>${copy.onlineDuration}</span><strong>${escapeHtml(typeof user.online_hours === "number" ? `${user.online_hours.toFixed(2)}${lang() === "zh" ? " 小时" : " h"}` : formatDurationLong(user.online_seconds))}</strong></div>
      <div><span>${copy.offlineDuration}</span><strong>${escapeHtml(typeof user.offline_hours === "number" ? `${user.offline_hours.toFixed(2)}${lang() === "zh" ? " 小时" : " h"}` : formatDurationLong(user.offline_seconds))}</strong></div>
      <div><span>${copy.role}</span><strong>${escapeHtml(user.role || "user")}</strong></div>
    </div>
  `).join("") : `<div class="auth-note">${escapeHtml(copy.activityPending)}</div>`;
  return `
    <div class="admin-user-card">
      <div class="admin-user-card__head">
        <div>
          <strong>${copy.dailyActivityReport}</strong>
          <div class="admin-user-card__meta">${copy.reportDate} · ${escapeHtml(report?.report_date || "--")} · ${copy.generatedAt} · ${escapeHtml(report?.generated_at_local || formatDateTime(report?.generated_at) || "--")}</div>
        </div>
        <span class="tag">${escapeHtml(report?.timezone || "Asia/Shanghai")}</span>
      </div>
      <div class="admin-user-card__grid" style="margin-top:10px;">
        <div><span>${copy.onlineRatio}</span><strong>${escapeHtml(String(summary.online_ratio_percent ?? 0))}%</strong></div>
        <div><span>${copy.topActiveUsers}</span><strong>${escapeHtml(formatSummaryPeople(topActive))}</strong></div>
        <div class="admin-user-card__wide"><span>${copy.mostlyOfflineUsers}</span><strong>${escapeHtml(formatSummaryPeople(mostlyOffline))}</strong></div>
      </div>
      <div class="admin-user-card__grid admin-anomaly-grid" style="margin-top:10px;">
        <div class="admin-user-card__wide"><span>${copy.anomalyAlerts}</span><strong></strong></div>
        ${renderAlertLine(copy.anomalyConsecutiveLow, anomalies.consecutive_low_activity)}
        ${renderAlertLine(copy.anomalyLowYesterday, anomalies.low_activity_yesterday)}
        ${renderAlertLine(copy.anomalyHighYesterday, anomalies.high_activity_yesterday)}
      </div>
      ${list}
    </div>
  `;
}

function renderAdminMonthlyReport(report) {
  const copy = authCopy();
  const rows = Array.isArray(report?.users) ? report.users : [];
  const summary = report?.summary || {};
  const hourUnit = lang() === "zh" ? " 小时" : " h";
  const list = rows.length ? rows.map((user) => `
    <div class="admin-user-card__grid" style="margin-top:10px;">
      <div><span>${escapeHtml(user.display_name || user.email || "--")}</span><strong>${escapeHtml(user.email || "--")}</strong></div>
      <div><span>${copy.monthlyLoginCount}</span><strong>${escapeHtml(String(user.login_count ?? 0))}</strong></div>
      <div><span>${copy.monthlyWorkCount}</span><strong>${escapeHtml(String(user.work_count ?? 0))}</strong></div>
      <div><span>${copy.monthlyExportCount}</span><strong>${escapeHtml(String(user.export_count ?? 0))}</strong></div>
      <div><span>${copy.onlineDuration}</span><strong>${escapeHtml(`${Number(user.online_hours || 0).toFixed(2)}${hourUnit}`)}</strong></div>
      <div><span>${copy.offlineDuration}</span><strong>${escapeHtml(`${Number(user.offline_hours || 0).toFixed(2)}${hourUnit}`)}</strong></div>
      <div><span>${copy.monthlyMostUsedPlatform}</span><strong>${escapeHtml(user.most_used_platform || copy.none)}</strong></div>
      <div class="admin-user-card__wide"><span>${copy.monthlyExportedFiles}</span><strong>${escapeHtml((user.exported_files || []).join(" · ") || copy.none)}</strong></div>
    </div>
  `).join("") : `<div class="auth-note">${escapeHtml(copy.activityPending)}</div>`;
  return `
    <div class="admin-user-card">
      <div class="admin-user-card__head">
        <div>
          <strong>${copy.monthlyActivityReport}</strong>
          <div class="admin-user-card__meta">${copy.reportMonth} · ${escapeHtml(report?.report_month || "--")} · ${copy.generatedAt} · ${escapeHtml(report?.generated_at_local || formatDateTime(report?.generated_at) || "--")}</div>
        </div>
        ${report?.download_url ? `<a class="btn btn-primary" href="${escapeHtml(report.download_url)}">${copy.monthlyDownload}</a>` : `<span class="tag">${escapeHtml(report?.timezone || "Asia/Shanghai")}</span>`}
      </div>
      <div class="admin-user-card__grid" style="margin-top:10px;">
        <div><span>${copy.onlineDuration}</span><strong>${escapeHtml(`${Number(summary.total_online_hours || 0).toFixed(2)}${hourUnit}`)}</strong></div>
        <div><span>${copy.offlineDuration}</span><strong>${escapeHtml(`${Number(summary.total_offline_hours || 0).toFixed(2)}${hourUnit}`)}</strong></div>
        <div><span>${copy.monthlyWorkCount}</span><strong>${escapeHtml(String(summary.total_work_count ?? 0))}</strong></div>
        <div><span>${copy.monthlyExportCount}</span><strong>${escapeHtml(String(summary.total_export_count ?? 0))}</strong></div>
      </div>
      ${list}
    </div>
  `;
}

function renderMonthlyAnomalySummary(report) {
  const copy = authCopy();
  const rows = Array.isArray(report?.users) ? report.users : [];
  const lowActivity = rows
    .filter((user) => Number(user.online_hours || 0) > 0 && Number(user.online_hours || 0) < 0.5)
    .slice(0, 8);
  const inactive = rows
    .filter((user) => Number(user.login_count || 0) === 0)
    .slice(0, 8);
  const noExportAfterWork = rows
    .filter((user) => Number(user.work_count || 0) >= 3 && Number(user.export_count || 0) === 0)
    .slice(0, 8);
  const highExport = rows
    .filter((user) => Number(user.export_count || 0) >= 20)
    .slice(0, 8);
  const names = (items, detail) => items.length
    ? items.map((user) => `${user.display_name || user.email}${detail ? ` (${detail(user)})` : ""}`).join(" · ")
    : copy.none;
  return `
    <div class="admin-user-card admin-anomaly-summary">
      <div class="admin-user-card__head">
        <div>
          <strong>${copy.monthlyAnomalyTitle}</strong>
          <div class="admin-user-card__meta">${copy.reportMonth} · ${escapeHtml(report?.report_month || "--")}</div>
        </div>
        <span class="tag">${escapeHtml(rows.length ? `${rows.length} users` : copy.none)}</span>
      </div>
      <div class="admin-user-card__grid admin-anomaly-grid">
        <div class="admin-user-card__wide"><span>${copy.monthlyLowActivity}</span><strong>${escapeHtml(names(lowActivity, (user) => formatHoursValue(user.online_hours)))}</strong></div>
        <div class="admin-user-card__wide"><span>${copy.monthlyInactiveUsers}</span><strong>${escapeHtml(names(inactive))}</strong></div>
        <div class="admin-user-card__wide"><span>${copy.monthlyExportWatch}</span><strong>${escapeHtml(names(noExportAfterWork, (user) => `${user.work_count || 0} work / 0 export`))}</strong></div>
        <div class="admin-user-card__wide"><span>${copy.monthlyHighExport}</span><strong>${escapeHtml(names(highExport, (user) => `${user.export_count || 0}`))}</strong></div>
      </div>
    </div>
  `;
}

async function openAdminCenter() {
  const copy = authCopy();
  let users = [];
  let report = null;
  let monthlyReport = null;
  let overview = null;
  let chatOverview = null;
  let v2Reports = [];
  try {
    const [usersPayload, dailyReport, monthReport, v2Overview, chatGovOverview, reportsPayload] = await Promise.all([
      loadAdminUsers(),
      loadAdminActivityReport(),
      loadAdminMonthlyReport(),
      loadV2AdminOverview(),
      loadV2AdminProjectChatOverview(),
      loadV2Reports(),
    ]);
    users = usersPayload;
    report = dailyReport;
    monthlyReport = monthReport;
    overview = v2Overview;
    chatOverview = chatGovOverview;
    v2Reports = reportsPayload.reports || [];
  } catch (error) {
    ensureOverlayPanel(copy.admin, `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`);
    return;
  }
  const adminUserCount = Array.isArray(users) ? users.length : 0;
  const adminOnlineCount = Array.isArray(users)
    ? users.filter((user) => String(user.online_status || "").toLowerCase() === "online").length
    : 0;
  const monthlyRows = Array.isArray(monthlyReport?.users) ? monthlyReport.users : [];
  const monthlyAbnormalCount = monthlyRows.filter((user) => {
    const onlineHours = Number(user.online_hours || 0);
    const loginCount = Number(user.login_count || 0);
    const exportCount = Number(user.export_count || 0);
    const workCount = Number(user.work_count || 0);
    return loginCount === 0 || (onlineHours > 0 && onlineHours < 0.5) || (workCount >= 3 && exportCount === 0);
  }).length;
  const panel = ensureOverlayPanel(copy.admin, `
    <div class="admin-panel">
      <div class="admin-hero">
        <div class="admin-hero__brand">
          <div class="admin-hero__logo" aria-hidden="true"></div>
          <div class="admin-hero__copy">
            <span>${lang() === "zh" ? "FASTONE 管理后台" : "FASTONE Control Center"}</span>
            <strong>${copy.admin}</strong>
            <p>${lang() === "zh" ? "统一查看账号、授权、活跃度、月报与异常摘要。" : "A single place to review accounts, access, activity, monthly reports, and exception signals."}</p>
          </div>
        </div>
        <div class="admin-hero__stats">
          <div class="admin-hero__stat">
            <span>${lang() === "zh" ? "账号总数" : "Accounts"}</span>
            <strong>${escapeHtml(String(adminUserCount))}</strong>
          </div>
          <div class="admin-hero__stat">
            <span>${lang() === "zh" ? "当前在线" : "Online Now"}</span>
            <strong>${escapeHtml(String(adminOnlineCount))}</strong>
          </div>
          <div class="admin-hero__stat">
            <span>${lang() === "zh" ? "本月异常" : "Monthly Exceptions"}</span>
            <strong>${escapeHtml(String(monthlyAbnormalCount))}</strong>
          </div>
        </div>
      </div>
      <div class="auth-note">${copy.adminSummary}</div>
      <div class="admin-note-strip">
        <div class="admin-note-strip__item">
          <span>${copy.adminReportsTitle}</span>
          <strong>${copy.adminSchedule}</strong>
        </div>
      </div>
      <div class="summary-grid" style="margin-top:12px;">
        <div class="summary-item"><span>${lang() === "zh" ? "项目总数" : "Projects"}</span><strong>${escapeHtml(String(overview?.totals?.projects ?? 0))}</strong></div>
        <div class="summary-item"><span>${lang() === "zh" ? "任务总数" : "Work Items"}</span><strong>${escapeHtml(String(overview?.totals?.work_items ?? 0))}</strong></div>
        <div class="summary-item"><span>${lang() === "zh" ? "未解决问题" : "Unresolved Issues"}</span><strong>${escapeHtml(String(overview?.totals?.unresolved_issues ?? 0))}</strong></div>
        <div class="summary-item"><span>${lang() === "zh" ? "报告总量" : "Reports"}</span><strong>${escapeHtml(String(overview?.totals?.reports ?? 0))}</strong></div>
        <div class="summary-item"><span>${lang() === "zh" ? "聊天摘要" : "Chat Summaries"}</span><strong>${escapeHtml(String(overview?.totals?.project_chat_summaries ?? 0))}</strong></div>
        <div class="summary-item"><span>${lang() === "zh" ? "聊天消息" : "Chat Messages"}</span><strong>${escapeHtml(String(overview?.totals?.project_chat_messages ?? 0))}</strong></div>
        <div class="summary-item"><span>${lang() === "zh" ? "摘要积压项目" : "Summary Backlog"}</span><strong>${escapeHtml(String(chatOverview?.totals?.backlog_projects ?? 0))}</strong></div>
        <div class="summary-item"><span>${lang() === "zh" ? "摘要过期项目" : "Stale Summary Projects"}</span><strong>${escapeHtml(String(chatOverview?.totals?.stale_projects ?? 0))}</strong></div>
      </div>
      <div class="work-chat-actions" style="margin-top:10px;">
        <button class="btn btn-primary" type="button" data-open-report-center>${lang() === "zh" ? "打开报告中心" : "Open Report Center"}</button>
        <button class="btn btn-ghost" type="button" data-open-workbench>${lang() === "zh" ? "打开 Workbench" : "Open Workbench"}</button>
        <button class="btn btn-ghost" type="button" data-open-mywork>${lang() === "zh" ? "打开 My Work" : "Open My Work"}</button>
      </div>
      <div class="auth-note" style="margin-top:10px;">
        ${lang() === "zh" ? "最新自动报告：" : "Latest auto reports: "}
        ${escapeHtml(v2Reports.slice(0, 3).map((item) => `${item.report_type}(${item.period_start})`).join(" · ") || "--")}
      </div>
      <div class="admin-report-stack">
        ${renderAdminActivityReport(report)}
        ${renderAdminMonthlyReport(monthlyReport)}
      </div>
      ${renderMonthlyAnomalySummary(monthlyReport)}
      ${renderPendingApprovals(users)}
      <div class="admin-section-head">
        <span>${copy.adminUsersTitle}</span>
      </div>
      ${renderAdminCreateUserForm()}
      <div class="admin-user-list">${renderAdminUsersTable(users)}</div>
    </div>
  `);
  panel.querySelector("[data-open-workbench]")?.addEventListener("click", () => openWorkbenchCenter().catch(() => {}));
  panel.querySelector("[data-open-mywork]")?.addEventListener("click", () => openMyWorkCenter().catch(() => {}));
  panel.querySelector("[data-open-report-center]")?.addEventListener("click", () => openReportCenter().catch(() => {}));
  panel.querySelector(".admin-create-user-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const feedback = form.querySelector("[data-admin-create-feedback]");
    const button = form.querySelector("button[type='submit']");
    const formData = new FormData(form);
    const pages = String(formData.get("pages") || "").split(",").map((item) => item.trim()).filter(Boolean);
    const platforms = String(formData.get("platforms") || "").split(",").map((item) => item.trim()).filter(Boolean);
    button.disabled = true;
    try {
      const resp = await fetch("/api/admin/users/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: String(formData.get("email") || "").trim(),
          username: String(formData.get("username") || "").trim(),
          phone: String(formData.get("phone") || "").trim(),
          display_name: String(formData.get("display_name") || "").trim(),
          password: String(formData.get("password") || ""),
          role: String(formData.get("role") || "user"),
          permissions: {
            pages: pages.length ? pages : ["*"],
            platforms: platforms.length ? platforms : ["*"],
            view_team_status: !!form.querySelector("input[name='view_team_status']")?.checked,
            view_document_flows: !!form.querySelector("input[name='view_document_flows']")?.checked,
            user_admin: String(formData.get("role") || "user") === "admin",
          },
        }),
      });
      const payload = await resp.json();
      if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
      if (feedback) feedback.textContent = copy.userCreated;
      form.reset();
      form.querySelector("input[name='pages']").value = "*";
      form.querySelector("input[name='platforms']").value = "*";
      const nextUsers = await loadAdminUsers();
      const list = panel.querySelector(".admin-user-list");
      if (list) list.innerHTML = renderAdminUsersTable(nextUsers);
    } catch (error) {
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    } finally {
      button.disabled = false;
    }
  });
  panel.querySelectorAll(".admin-user-card, .admin-pending-item").forEach((card) => {
    const identifier = card.dataset.userIdentifier || "";
    const feedback = card.querySelector("[data-admin-feedback]");
    const updateApproval = async (action) => {
      try {
        const requestBody = { identifier, action };
        if (action === "approve") {
          const permissions = buildApprovalPermissionsFromCard(card);
          if (!permissions.platforms.length) throw new Error("approval_platforms_required");
          if (!permissions.colleagues.length) throw new Error("approval_colleagues_required");
          requestBody.permissions = permissions;
        } else if (action === "reject") {
          const rejectReason = String(card.querySelector("input[name='reject_reason']")?.value || "").trim();
          if (rejectReason) requestBody.reason = rejectReason;
        }
        const resp = await fetch("/api/admin/users/approval", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        });
        const result = await resp.json();
        if (!resp.ok || !result.ok) throw new Error(result.error || "request_failed");
        await openAdminCenter();
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    };
    card.querySelector("[data-admin-approve]")?.addEventListener("click", () => updateApproval("approve"));
    card.querySelector("[data-admin-reject]")?.addEventListener("click", () => updateApproval("reject"));
    card.querySelector("[data-admin-reset]")?.addEventListener("click", async () => {
      const nextPassword = window.prompt(lang() === "zh" ? `为 ${identifier} 输入新密码` : `Enter a new password for ${identifier}`);
      if (!nextPassword) return;
      try {
        const resp = await fetch("/api/admin/users/password", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ identifier, password: nextPassword }),
        });
        const payload = await resp.json();
        if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
        if (feedback) feedback.textContent = copy.passwordSaved;
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
    card.querySelector("[data-admin-save]")?.addEventListener("click", async () => {
      const role = card.querySelector("select[name='role']")?.value || "user";
      const pages = String(card.querySelector("input[name='pages']")?.value || "").split(",").map((item) => item.trim()).filter(Boolean);
      const platforms = String(card.querySelector("input[name='platforms']")?.value || "").split(",").map((item) => item.trim()).filter(Boolean);
      const viewTeamStatus = !!card.querySelector("input[name='view_team_status']")?.checked;
      const viewDocumentFlows = !!card.querySelector("input[name='view_document_flows']")?.checked;
      try {
        const resp = await fetch("/api/admin/users/permissions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ identifier, role, permissions: { pages, platforms, user_admin: role === "admin", view_team_status: viewTeamStatus, view_document_flows: viewDocumentFlows } }),
        });
        const payload = await resp.json();
        if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
        if (feedback) feedback.textContent = lang() === "zh" ? "权限已更新。" : "Permissions updated.";
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
    card.querySelector("[data-admin-delete]")?.addEventListener("click", async () => {
      if (!window.confirm(lang() === "zh" ? `确认删除 ${identifier} 吗？` : `Delete ${identifier}?`)) return;
      try {
        const resp = await fetch("/api/admin/users/delete", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ identifier }),
        });
        const payload = await resp.json();
        if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
        card.remove();
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
  });
}

async function openTeamStatusCenter() {
  const copy = authCopy();
  try {
    const users = await loadTeamStatusUsers();
    const panel = ensureOverlayPanel(copy.teamStatus, `
      <div class="admin-panel">
        <div class="admin-hero admin-hero--team">
          <div class="admin-hero__brand">
            <div class="admin-hero__logo" aria-hidden="true"></div>
            <div class="admin-hero__copy">
              <span>${lang() === "zh" ? "FASTONE 团队态势" : "FASTONE Team Pulse"}</span>
              <strong>${copy.teamStatus}</strong>
              <p>${lang() === "zh" ? "集中查看成员在线状态、最后活跃时间、当前动作与工作平台位置。" : "Review live presence, last activity, current action, and active workspace placement in one compact surface."}</p>
            </div>
          </div>
          <div class="admin-hero__stats">
            <div class="admin-hero__stat">
              <span>${lang() === "zh" ? "成员数" : "Members"}</span>
              <strong>${escapeHtml(String((users || []).length))}</strong>
            </div>
            <div class="admin-hero__stat">
              <span>${lang() === "zh" ? "在线中" : "Online Now"}</span>
              <strong>${escapeHtml(String((users || []).filter((user) => String(user.online_status || "").toLowerCase() === "online").length))}</strong>
            </div>
            <div class="admin-hero__stat">
              <span>${lang() === "zh" ? "快超时预警" : "Timeout Watch"}</span>
              <strong>${escapeHtml(String((users || []).filter((user) => Number(user.idle_seconds || 0) > 0 && Number(user.idle_seconds || 0) < 1800).length))}</strong>
            </div>
          </div>
        </div>
        <label class="auth-field admin-search-field">
          <span>${copy.teamSearch}</span>
          <input type="text" data-team-search-input placeholder="${escapeHtml(copy.teamSearchPlaceholder)}" />
        </label>
        <div class="admin-user-list admin-user-list-compact" data-team-search-results>${renderTeamStatusCards(users)}</div>
      </div>
    `);
    const input = panel.querySelector("[data-team-search-input]");
    const results = panel.querySelector("[data-team-search-results]");
    let timer = null;
    input?.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(async () => {
        try {
          const nextUsers = await loadTeamStatusUsers(input.value || "");
          if (results) results.innerHTML = renderTeamStatusCards(nextUsers);
        } catch (error) {
          if (results) results.innerHTML = `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`;
        }
      }, 180);
    });
  } catch (error) {
    ensureOverlayPanel(copy.teamStatus, `<div class="auth-feedback">${escapeHtml(error.message === "permission_denied" ? copy.permissionDenied : authErrorMessage(error.message))}</div>`);
  }
}

function renderPageHeader(config = {}) {
  const title = String(config.title || (lang() === "zh" ? "Hermes" : "Hermes"));
  const description = String(config.description || "");
  const updatedText = String(config.updatedText || formatDateTime(Math.floor(Date.now() / 1000)));
  return `
    <div class="page-header">
      <div class="page-header__main">
        <div class="eyebrow">Hermes Flagship</div>
        <h2>${escapeHtml(title)}</h2>
        <p>${escapeHtml(description)}</p>
      </div>
      <div class="page-header__meta">
        <span>${lang() === "zh" ? "最近同步" : "Last sync"}</span>
        <strong>${escapeHtml(updatedText)}</strong>
      </div>
    </div>
  `;
}

function renderMetricCard(metric = {}) {
  return `
    <article class="metric-card">
      <span>${escapeHtml(String(metric.label || "--"))}</span>
      <strong>${escapeHtml(String(metric.value ?? "--"))}</strong>
      <small>${escapeHtml(String(metric.detail || ""))}</small>
      ${metric.badge ? `<div class="metric-card__badge">${renderStatusBadge(metric.badge.label, metric.badge.state || "neutral")}</div>` : ""}
    </article>
  `;
}

function renderTaskListCard(tasks = [], state = "ready") {
  const filter = String(appState.hermes.taskFilter || "all");
  const now = Math.floor(Date.now() / 1000);
  const rows = (Array.isArray(tasks) ? tasks : []).filter((task) => {
    if (filter === "high") return String(task?.priority || "").toLowerCase() === "high";
    if (filter === "pending") return !["done", "cancelled"].includes(String(task?.status || "").toLowerCase());
    if (filter === "overdue") {
      const deadline = Number(task?.deadline_at || task?.due_at || 0);
      return deadline > 0 && deadline < now && !["done", "cancelled"].includes(String(task?.status || "").toLowerCase());
    }
    return true;
  }).slice(0, 8);
  return `
    <section class="hermes-panel task-list-card">
      <div class="intel-block-title">
        <strong>${lang() === "zh" ? "Key Tasks" : "Key Tasks"}</strong>
        <label class="mini-select">
          <span>${lang() === "zh" ? "聚焦" : "Focus"}</span>
          <select data-hermes-task-filter>
            <option value="all" ${filter === "all" ? "selected" : ""}>${lang() === "zh" ? "全部" : "All"}</option>
            <option value="high" ${filter === "high" ? "selected" : ""}>${lang() === "zh" ? "高优先级" : "High"}</option>
            <option value="pending" ${filter === "pending" ? "selected" : ""}>${lang() === "zh" ? "待处理" : "Pending"}</option>
            <option value="overdue" ${filter === "overdue" ? "selected" : ""}>${lang() === "zh" ? "超期" : "Overdue"}</option>
          </select>
        </label>
      </div>
      ${state === "loading" ? renderLoadingSkeleton(4) : ""}
      ${!rows.length && state !== "loading" ? renderEmptyState(lang() === "zh" ? "暂无高优先任务" : "No high-priority tasks") : ""}
      ${rows.length ? rows.map((task) => `
        <article class="hermes-list-item">
          <div>
            <strong>${escapeHtml(task.title || task.id || "--")}</strong>
            <span>${escapeHtml(unifiedStatusLabel(task.status || "pending"))} · ${escapeHtml(task.priority || "medium")} · ${escapeHtml(task.project_id || task.source || "--")}</span>
            <small>${escapeHtml(task.deadline_at ? formatDateTime(task.deadline_at) : (task.due_at ? formatDateTime(task.due_at) : (lang() === "zh" ? "无截止时间" : "No deadline")))}</small>
          </div>
          <button class="btn btn-ghost" type="button" data-hermes-action="open-mywork">${lang() === "zh" ? "处理" : "Handle"}</button>
        </article>
      `).join("") : ""}
    </section>
  `;
}

function renderActivityTimelineCard(items = [], state = "ready") {
  const rows = Array.isArray(items) ? items.slice(0, 10) : [];
  return `
    <section class="hermes-panel activity-timeline-card">
      <div class="intel-block-title"><strong>${lang() === "zh" ? "Activity Timeline" : "Activity Timeline"}</strong></div>
      ${state === "loading" ? renderLoadingSkeleton(4) : ""}
      ${!rows.length && state !== "loading" ? renderEmptyState(lang() === "zh" ? "暂无动态" : "No activities yet") : ""}
      ${rows.length ? rows.map((item) => `
        <div class="timeline-row">
          <time>${escapeHtml(item.timeText || "--")}</time>
          <div>
            <strong>${escapeHtml(item.title || "--")}</strong>
            <span>${escapeHtml(item.detail || "--")}</span>
          </div>
        </div>
      `).join("") : ""}
    </section>
  `;
}

function renderSystemStatusCard(payload = {}, state = "ready") {
  const routeHealth = payload?.route_health || {};
  const degraded = Object.values(routeHealth).filter((item) => {
    const status = String(item?.status || "").toLowerCase();
    return status !== "ready" && status !== "setup_required";
  }).length;
  const mode = state === "syncing"
    ? "syncing"
    : state === "error"
      ? "error"
      : degraded
        ? "warning"
        : "success";
  const label = mode === "syncing"
    ? (lang() === "zh" ? "同步中" : "Syncing")
    : mode === "error"
      ? (lang() === "zh" ? "失败" : "Failed")
      : mode === "warning"
        ? (lang() === "zh" ? "部分可用" : "Partial")
        : (lang() === "zh" ? "正常" : "Healthy");
  return `
    <section class="hermes-panel system-status-card">
      <div class="intel-block-title"><strong>${lang() === "zh" ? "System Status" : "System Status"}</strong></div>
      <div class="system-status-card__main">
        ${renderStatusBadge(label, mode === "success" ? "success" : mode === "warning" ? "warning" : mode === "error" ? "error" : "neutral")}
      </div>
      <div class="auth-note">${escapeHtml(payload?.routeStatus || payload?.route_status || (lang() === "zh" ? "等待状态更新" : "Waiting for route status"))}</div>
    </section>
  `;
}

function renderQuickActionsCard() {
  return `
    <section class="hermes-panel quick-actions-card">
      <div class="intel-block-title"><strong>${lang() === "zh" ? "Quick Actions" : "Quick Actions"}</strong></div>
      <div class="quick-actions-grid">
        <button class="btn btn-primary" type="button" data-hermes-action="create-item">${lang() === "zh" ? "新建事项" : "New Item"}</button>
        <button class="btn btn-ghost" type="button" data-hermes-action="open-workbench">${lang() === "zh" ? "查看全部任务" : "All Tasks"}</button>
        <button class="btn btn-ghost" type="button" data-hermes-action="refresh">${lang() === "zh" ? "手动刷新" : "Refresh"}</button>
        <button class="btn btn-ghost" type="button" data-hermes-action="open-intel">${lang() === "zh" ? "打开情报" : "Open Intel"}</button>
        <button class="btn btn-ghost" type="button" data-hermes-action="open-ai-agent">${lang() === "zh" ? "AI Agent" : "AI Agent"}</button>
      </div>
    </section>
  `;
}

function renderHermesReadinessStrip(payload = {}) {
  const statusPayload = payload.status || {};
  const workbench = payload.workbench || {};
  const myWork = payload.myWork || {};
  const routeHealth = statusPayload.route_health || {};
  const activeRouteItems = Object.values(routeHealth).filter((item) => String(item?.status || "").toLowerCase() !== "setup_required");
  const routeCount = activeRouteItems.length;
  const readyRoutes = activeRouteItems.filter((item) => String(item?.status || "").toLowerCase() === "ready" || item?.available).length;
  const quickViews = workbench.quick_views || {};
  return `
    <div class="readiness-strip">
      <div><span>${lang() === "zh" ? "网关" : "Gateway"}</span>${renderStatusBadge(statusPayload.hermes_online ? (lang() === "zh" ? "在线" : "Online") : (lang() === "zh" ? "离线" : "Offline"), statusPayload.hermes_online ? "success" : "error")}</div>
      <div><span>${lang() === "zh" ? "AI 路由" : "AI Routes"}</span><strong>${readyRoutes}/${routeCount || readyRoutes}</strong></div>
      <div><span>${lang() === "zh" ? "项目风险" : "Project Risk"}</span><strong>${escapeHtml(String(quickViews.high_risk_projects || 0))}</strong></div>
      <div><span>${lang() === "zh" ? "今日任务" : "Today Tasks"}</span><strong>${escapeHtml(String((myWork.tasks_today || []).length || 0))}</strong></div>
      <div><span>${lang() === "zh" ? "报告状态" : "Reports"}</span><strong>${escapeHtml(String((myWork.my_reports || []).length || 0))}</strong></div>
    </div>
  `;
}

async function loadGovernanceControlData() {
  try {
    const resp = await fetch("/api/governance/control-center", { cache: "no-store" });
    const payload = await resp.json();
    if (!resp.ok || !payload.ok) throw new Error(payload.error || "governance_failed");
    appState.governance.data = payload;
    appState.governance.state = "ready";
    return payload;
  } catch (error) {
    appState.governance.state = "error";
    appState.governance.error = error?.message || "governance_failed";
    return null;
  }
}

function governanceCopy() {
  const zh = lang() === "zh";
  return {
    title: zh ? "透明盔甲控制层" : "Transparent Armor Control Layer",
    subtitle: zh ? "合规留痕、管理决策、系统集成、安全防线、项目协同、移动审批、知识资产和极简触达集中在一个工作面。" : "Compliance traceability, executive decisioning, integration, security, project work, mobile approval, knowledge assets, and frictionless UX in one surface.",
    compliance: zh ? "合规与留痕" : "Compliance Trace",
    cockpit: zh ? "管理层驾驶舱" : "Executive Cockpit",
    integration: zh ? "集成中台" : "Integration Hub",
    security: zh ? "安全 / DLP" : "Security / DLP",
    warRoom: zh ? "项目 War Room" : "Project War Room",
    mobile: zh ? "三步审批" : "3-Step Approval",
    knowledge: zh ? "AI 知识资产库" : "AI Knowledge Assets",
    ux: zh ? "极简 UX" : "Frictionless UX",
  };
}

function ensureSecurityWatermark() {
  if (!appState.auth.authenticated || !appState.auth.user) return;
  let watermark = document.querySelector("[data-security-watermark]");
  if (!watermark) {
    watermark = document.createElement("div");
    watermark.className = "security-watermark";
    watermark.dataset.securityWatermark = "1";
    document.body.appendChild(watermark);
  }
  const user = appState.auth.user || {};
  watermark.textContent = `FASTONE · ${user.email || user.username || "authorized user"} · ${new Date().toLocaleDateString()}`;
}

function renderGovernanceControlLayer(payload = {}, context = {}) {
  const copy = governanceCopy();
  const compliance = payload?.compliance || {};
  const rbac = payload?.rbac || {};
  const integration = payload?.integration || {};
  const security = payload?.security || {};
  const knowledge = payload?.knowledge || {};
  const executive = payload?.executive_summary || {};
  const armor = payload?.transparent_armor || {};
  const armorPillars = Array.isArray(armor.pillars) ? armor.pillars : [];
  const auditStream = Array.isArray(compliance.recent_audit_stream) ? compliance.recent_audit_stream.slice(0, 8) : [];
  const auditTimeline = Array.isArray(compliance.audit_timeline) ? compliance.audit_timeline.slice(0, 10) : [];
  const aiOutputs = Array.isArray(compliance.ai_outputs) ? compliance.ai_outputs : [];
  const auditScopes = Array.isArray(compliance.audit_scopes) ? compliance.audit_scopes : [];
  const rbacMatrix = Array.isArray(rbac.matrix) ? rbac.matrix : [];
  const integrationItems = Array.isArray(integration.items) ? integration.items : [];
  const dlpPolicies = Array.isArray(security.policies) ? security.policies : [];
  const warRooms = Array.isArray(payload?.war_room?.items) ? payload.war_room.items.slice(0, 6) : [];
  const riskQueue = Array.isArray(payload?.risk_queue?.items) ? payload.risk_queue.items.slice(0, 8) : [];
  const crossChecks = Array.isArray(payload?.cross_check?.items) ? payload.cross_check.items.slice(0, 8) : [];
  const mobileSteps = Array.isArray(payload?.mobile?.steps) ? payload.mobile.steps : [];
  const knowledgeRoutes = Array.isArray(knowledge.routes) ? knowledge.routes : [];
  const workbench = context.workbench || {};
  const myWork = context.myWork || {};
  const quickViews = workbench.quick_views || {};
  const pendingDocs = Array.isArray(myWork.pending_documents) ? myWork.pending_documents.length : 0;
  const highRiskProjects = Number(quickViews.high_risk_projects || 0);
  const overdue = Number(quickViews.overdue_tasks || 0);
  const decisionsToday = Number(quickViews.pending_approvals || 0) + pendingDocs;
  const zh = lang() === "zh";
  const cards = [
    {
      key: "compliance",
      title: copy.compliance,
      value: String(compliance.audit_events ?? 0),
      meta: zh ? `导出 ${compliance.exports_this_month || 0} · 敏感操作 ${compliance.sensitive_operations || 0}` : `Exports ${compliance.exports_this_month || 0} · Sensitive ${compliance.sensitive_operations || 0}`,
      state: "success",
      detail: zh ? "RBAC、AI 输出、导出和文件操作可追踪。" : "RBAC, AI output, exports, and file activity are traceable.",
    },
    {
      key: "cockpit",
      title: copy.cockpit,
      value: String(highRiskProjects + overdue + decisionsToday),
      meta: zh ? `高风险 ${highRiskProjects} · 超期 ${overdue} · 决策 ${decisionsToday}` : `Risk ${highRiskProjects} · Overdue ${overdue} · Decisions ${decisionsToday}`,
      state: highRiskProjects || overdue ? "warning" : "success",
      detail: zh ? "管理层先看异常，再进入项目或情报。" : "Leadership sees exceptions first, then drills into projects or intel.",
    },
    {
      key: "integration",
      title: copy.integration,
      value: `${integration.google_connected || 0}/${integration.google_profiles || 0}`,
      meta: zh ? `Composio ${integration.composio_connected || 0}/${integration.composio_profiles || 0} · Skills ${integration.skills_total || 0}` : `Composio ${integration.composio_connected || 0}/${integration.composio_profiles || 0} · Skills ${integration.skills_total || 0}`,
      state: "neutral",
      detail: zh ? "Google、Composio、Slack、文件、情报和 Agent 汇总为统一入口。" : "Google, Composio, Slack, files, intel, and agents are unified.",
    },
    {
      key: "security",
      title: copy.security,
      value: security.watermark_enabled ? (zh ? "已启用" : "On") : "--",
      meta: zh ? `会话 ${security.active_sessions || 0} · DLP 提醒 · 下载留痕` : `Sessions ${security.active_sessions || 0} · DLP prompts · Download logs`,
      state: "success",
      detail: zh ? "页面水印、敏感词提醒、导出前提示和权限提示已形成基础防线。" : "Watermark, sensitive-term prompts, export warnings, and permission hints are in place.",
    },
    {
      key: "warroom",
      title: copy.warRoom,
      value: String((workbench.projects || []).length || 0),
      meta: zh ? `文件版本、节点、风险、责任人` : "Versions, milestones, risk, owners",
      state: "neutral",
      detail: zh ? "按项目/交易/客户组织工作，而不是只按部门页面切换。" : "Work is organized around projects, deals, and clients, not only pages.",
    },
    {
      key: "mobile",
      title: copy.mobile,
      value: "3",
      meta: zh ? "批准 / 退回 / 要补材料" : "Approve / Return / Request info",
      state: "neutral",
      detail: zh ? "移动端压缩为待办、判断、动作三步。" : "Mobile flow compresses into queue, decision, action.",
    },
    {
      key: "knowledge",
      title: copy.knowledge,
      value: String(knowledge.skills_total || 0),
      meta: zh ? `模板 ${knowledge.templates_available || 0} · Hermes ${knowledge.hermes_skills || 0}` : `Templates ${knowledge.templates_available || 0} · Hermes ${knowledge.hermes_skills || 0}`,
      state: "neutral",
      detail: zh ? "Skills、案例、模板、流程和情报统一沉淀为新人可学资产。" : "Skills, cases, templates, procedures, and intel become reusable assets.",
    },
    {
      key: "ux",
      title: copy.ux,
      value: zh ? "三步" : "3-step",
      meta: zh ? "少菜单、少颜色、少干扰" : "Less menu, color, and noise",
      state: "success",
      detail: zh ? "核心功能三步触达，页面维持三层色彩结构。" : "Core tasks are reachable in three steps with a three-layer color system.",
    },
  ];
  return `
    <section class="transparent-armor-shell">
      <div class="transparent-armor-head">
        <div>
          <div class="eyebrow">TRANSPARENT ARMOR</div>
          <h2>${escapeHtml(copy.title)}</h2>
          <p>${escapeHtml(copy.subtitle)}</p>
        </div>
        <div class="transparent-armor-rbac">
          <span>${zh ? "当前角色" : "Current Role"}</span>
          <strong>${escapeHtml(String(rbac.role || "user"))}</strong>
          <em>${escapeHtml((rbac.platforms || []).includes("*") ? (zh ? "全平台权限" : "All platforms") : `${(rbac.platforms || []).length} ${zh ? "个平台" : "platforms"}`)}</em>
        </div>
      </div>
      <div class="transparent-armor-exec">
        <div>
          <span>${zh ? "管理层摘要" : "Executive Summary"}</span>
          <strong>${escapeHtml(executive.headline || (zh ? "先看异常，再进入项目和审批。" : "See exceptions first, then enter projects and approvals."))}</strong>
        </div>
        <div><span>${zh ? "高优先风险" : "Priority Risks"}</span><strong>${escapeHtml(String(executive.critical_risks ?? payload?.risk_queue?.critical_count ?? 0))}</strong></div>
        <div><span>${zh ? "交叉检查" : "Cross Checks"}</span><strong>${escapeHtml(String(executive.cross_check_findings ?? crossChecks.length))}</strong></div>
        <div><span>${zh ? "DLP 命中" : "DLP Hits"}</span><strong>${escapeHtml(String(executive.dlp_hits ?? 0))}</strong></div>
      </div>
      <div class="transparent-armor-grid">
        ${cards.map((card) => `
          <article class="transparent-armor-card transparent-armor-card--${escapeHtml(card.key)}">
            <div class="transparent-armor-card__top">
              <span>${escapeHtml(card.title)}</span>
              ${renderStatusBadge(card.state === "warning" ? (zh ? "关注" : "Watch") : (zh ? "就绪" : "Ready"), card.state)}
            </div>
            <strong>${escapeHtml(card.value)}</strong>
            <em>${escapeHtml(card.meta)}</em>
            <p>${escapeHtml(card.detail)}</p>
          </article>
        `).join("")}
      </div>
      <div class="transparent-armor-acceptance">
        <div class="transparent-armor-detail__head">
          <strong>${escapeHtml(armor.name || (zh ? "金融机构级透明盔甲 8 项验收矩阵" : "Institutional Transparent Armor Acceptance Matrix"))}</strong>
          <span>${zh ? `完成 ${armor.completed ?? armorPillars.length}/${armor.total ?? armorPillars.length}` : `Completed ${armor.completed ?? armorPillars.length}/${armor.total ?? armorPillars.length}`}</span>
        </div>
        <div class="armor-pillar-grid">
          ${armorPillars.map((item, index) => `
            <article class="armor-pillar-card">
              <div class="armor-pillar-card__top">
                <b>${String(index + 1).padStart(2, "0")}</b>
                ${renderStatusBadge(item.status === "complete" ? (zh ? "已完成" : "Complete") : (item.status || "pending"), item.status === "complete" ? "success" : "warning")}
              </div>
              <strong>${escapeHtml(item.title || "--")}</strong>
              <span>${escapeHtml(item.evidence || "--")}</span>
              <em>${escapeHtml(item.entry || "--")} · ${escapeHtml(item.next_action || "--")}</em>
            </article>
          `).join("") || renderEmptyState(zh ? "暂无透明盔甲验收矩阵" : "No acceptance matrix yet")}
        </div>
      </div>
      <div class="transparent-armor-detail-grid">
        <article class="transparent-armor-detail transparent-armor-detail--wide">
          <div class="transparent-armor-detail__head">
            <strong>${zh ? "管理层风险队列" : "Executive Risk Queue"}</strong>
            <span>${zh ? "按高风险、超期、待审批和文件阻塞排序" : "Prioritized by risk, overdue, approvals, and file blockers"}</span>
          </div>
          ${riskQueue.length ? `
            <div class="governance-risk-list">
              ${riskQueue.map((item) => `
                <div class="governance-risk-row">
                  ${renderStatusBadge(item.severity || (zh ? "中" : "medium"), String(item.severity || "").includes("critical") || String(item.severity || "").includes("high") ? "warning" : "neutral")}
                  <div>
                    <strong>${escapeHtml(item.title || "--")}</strong>
                    <span>${escapeHtml(item.project_name || item.project_id || item.workspace_id || (zh ? "未绑定项目" : "No project"))} · ${escapeHtml(item.owner || (zh ? "未指定责任人" : "No owner"))}</span>
                    <em>${escapeHtml(item.next_step || "--")}</em>
                  </div>
                </div>
              `).join("")}
            </div>
          ` : renderEmptyState(zh ? "暂无高优先级风险队列；系统会持续聚合项目风险、超期任务和文件审批阻塞。" : "No priority risk queue yet; the system aggregates project risk, overdue tasks, and file blockers.")}
        </article>
        <article class="transparent-armor-detail transparent-armor-detail--wide">
          <div class="transparent-armor-detail__head">
            <strong>${zh ? "文件 / 项目 / 审批交叉检查" : "File / Project / Approval Cross-Check"}</strong>
            <span>${zh ? "发现重复、缺归属、锁定不一致、版本缺口" : "Find duplicates, missing ownership, lock mismatch, and version gaps"}</span>
          </div>
          ${crossChecks.length ? `
            <div class="governance-risk-list governance-risk-list--checks">
              ${crossChecks.map((item) => `
                <div class="governance-risk-row">
                  ${renderStatusBadge(item.severity || (zh ? "中" : "medium"), String(item.severity || "").includes("high") ? "warning" : "neutral")}
                  <div>
                    <strong>${escapeHtml(item.title || item.type || "--")}</strong>
                    <span>${escapeHtml(item.type || "--")} ${item.count ? `· ${escapeHtml(String(item.count))}` : ""} ${Array.isArray(item.terms) && item.terms.length ? `· ${escapeHtml(item.terms.join(" / "))}` : ""}</span>
                    <em>${escapeHtml(item.recommendation || "--")}</em>
                  </div>
                </div>
              `).join("")}
            </div>
          ` : renderEmptyState(zh ? "暂无交叉检查异常；重复文件、敏感资料缺项目、归档锁定不一致会在这里提示。" : "No cross-check findings; duplicate files, sensitive files without projects, and archive lock mismatch will appear here.")}
        </article>
        <article class="transparent-armor-detail transparent-armor-detail--wide">
          <div class="transparent-armor-detail__head">
            <strong>${zh ? "审计流 / 留痕入口" : "Audit Stream"}</strong>
            <span>${auditScopes.map((item) => escapeHtml(item)).join(" · ") || (zh ? "操作、审批、下载、导出、AI 输出" : "Actions, approvals, downloads, exports, AI outputs")}</span>
          </div>
          ${auditStream.length ? `
            <div class="transparent-armor-audit-list">
              ${auditStream.map((item) => {
                const terms = Array.isArray(item.dlp_terms) ? item.dlp_terms.filter(Boolean) : [];
                const timeText = item.ts ? formatDateTime(item.ts) : (item.ts_text || "--");
                return `
                  <div class="transparent-armor-audit-row">
                    <div>
                      <strong>${escapeHtml(item.event || "event")}</strong>
                      <span>${escapeHtml(item.actor || "system")} · ${escapeHtml(timeText)}</span>
                    </div>
                    <em>${terms.length ? escapeHtml(terms.join(" / ")) : (zh ? "常规留痕" : "Standard log")}</em>
                  </div>
                `;
              }).join("")}
            </div>
          ` : renderEmptyState(zh ? "暂无审计事件；后续导出、下载和审批会自动进入留痕。" : "No audit events yet; exports, downloads, and approvals will be logged.")}
        </article>
        <article class="transparent-armor-detail transparent-armor-detail--wide">
          <div class="transparent-armor-detail__head">
            <strong>${zh ? "可追责时间线" : "Accountable Timeline"}</strong>
            <span>${zh ? "按对象追踪谁看过、谁改过、谁下载、谁导出、AI 输出了什么" : "Track who viewed, changed, downloaded, exported, and what AI produced by object"}</span>
          </div>
          ${auditTimeline.length ? `
            <div class="accountable-timeline">
              ${auditTimeline.map((item) => `
                <div class="accountable-timeline__row">
                  ${renderStatusBadge(item.category || "operation", item.category === "file" ? "info" : item.category === "ai_output" ? "warning" : "neutral")}
                  <div>
                    <strong>${escapeHtml(item.object || "--")}</strong>
                    <span>${escapeHtml(item.actor || "system")} · ${escapeHtml(item.event || "--")} · ${escapeHtml(item.ts || "--")}</span>
                  </div>
                </div>
              `).join("")}
            </div>
          ` : renderEmptyState(zh ? "暂无可追责时间线。" : "No accountable timeline yet.")}
        </article>
        <article class="transparent-armor-detail">
          <div class="transparent-armor-detail__head">
            <strong>${zh ? "AI 输出状态" : "AI Output Status"}</strong>
            <span>${zh ? "草稿、待复核、已采用、已驳回必须区分" : "Draft, pending review, adopted, and rejected must be separated"}</span>
          </div>
          <div class="ai-output-state-grid">
            ${aiOutputs.map((item) => `
              <div class="ai-output-state-card">
                ${renderStatusBadge(item.status || "draft", item.status === "draft" ? "neutral" : item.status === "pending_review" ? "warning" : "success")}
                <strong>${escapeHtml(item.title || "--")}</strong>
                <span>${escapeHtml(String(item.count ?? 0))} · ${escapeHtml(item.rule || "--")}</span>
                <em>${escapeHtml(item.next_step || "--")}</em>
              </div>
            `).join("") || renderEmptyState(zh ? "暂无 AI 输出状态。" : "No AI output status yet.")}
          </div>
        </article>
        <article class="transparent-armor-detail">
          <div class="transparent-armor-detail__head">
            <strong>${zh ? "RBAC / Need-to-know" : "RBAC / Need-to-know"}</strong>
            <span>${zh ? "角色、范围、最小可见原则" : "Role, scope, least visibility"}</span>
          </div>
          <div class="transparent-armor-policy-list">
            ${rbacMatrix.map((item) => `
              <div class="transparent-armor-policy-row">
                ${renderStatusBadge(item.role || "role", item.role === "admin" ? "warning" : "neutral")}
                <div>
                  <strong>${escapeHtml(item.scope || "--")}</strong>
                  <span>${escapeHtml(item.need_to_know || "--")}</span>
                </div>
              </div>
            `).join("") || renderEmptyState(zh ? "暂无权限矩阵" : "No RBAC matrix")}
          </div>
        </article>
        <article class="transparent-armor-detail">
          <div class="transparent-armor-detail__head">
            <strong>${zh ? "集成状态中心" : "Integration Status Center"}</strong>
            <span>${zh ? "连接状态、失败原因、修复建议" : "Status, failure reason, remediation"}</span>
          </div>
          <div class="transparent-armor-policy-list">
            ${integrationItems.map((item) => {
              const state = item.status === "healthy" ? "success" : (item.status === "partial" ? "warning" : "neutral");
              return `
                <div class="transparent-armor-policy-row">
                  ${renderStatusBadge(item.status || "unknown", state)}
                  <div>
                    <strong>${escapeHtml(item.name || "--")} · ${escapeHtml(String(item.connected ?? 0))}/${escapeHtml(String(item.total ?? 0))}</strong>
                    <span>${escapeHtml(item.next_step || "--")}</span>
                  </div>
                </div>
              `;
            }).join("") || renderEmptyState(zh ? "暂无集成状态" : "No integration status")}
          </div>
        </article>
        <article class="transparent-armor-detail">
          <div class="transparent-armor-detail__head">
            <strong>${zh ? "安全 / DLP 防线" : "Security / DLP Line"}</strong>
            <span>${zh ? "先落地平台可控项，不假装替代 MDM" : "Platform controls first; MDM remains separate"}</span>
          </div>
          <div class="transparent-armor-policy-list">
            ${dlpPolicies.map((item) => `
              <div class="transparent-armor-policy-row">
                ${renderStatusBadge(item.status === "active" ? (zh ? "启用" : "Active") : item.status, item.status === "active" ? "success" : "warning")}
                <div>
                  <strong>${escapeHtml(item.title || "--")}</strong>
                  <span>${escapeHtml(item.detail || "--")}</span>
                </div>
              </div>
            `).join("") || renderEmptyState(zh ? "暂无 DLP 策略" : "No DLP policies")}
          </div>
        </article>
        <article class="transparent-armor-detail transparent-armor-detail--wide">
          <div class="transparent-armor-detail__head">
            <strong>${zh ? "项目 War Room" : "Project War Room"}</strong>
            <span>${zh ? "按项目/交易/客户组织，而不是被菜单切碎" : "Organized by project, deal, and client instead of fragmented menus"}</span>
          </div>
          <div class="transparent-armor-war-grid">
            ${warRooms.map((item) => `
              <div class="transparent-armor-war-card">
                <div>
                  <strong>${escapeHtml(item.name || item.id || "--")}</strong>
                  <span>${escapeHtml(item.owner || "--")} · ${escapeHtml(item.status || "--")}</span>
                </div>
                <div class="transparent-armor-war-metrics">
                  <span>${zh ? "任务" : "Tasks"} ${escapeHtml(String(item.open_tasks || 0))}</span>
                  <span>${zh ? "超期" : "Overdue"} ${escapeHtml(String(item.overdue_tasks || 0))}</span>
                  <span>${zh ? "高风险" : "High risk"} ${escapeHtml(String(item.high_risk || 0))}</span>
                  <span>${zh ? "文件" : "Docs"} ${escapeHtml(String(item.documents || 0))}</span>
                </div>
              </div>
            `).join("") || renderEmptyState(zh ? "暂无可见项目；创建或加入项目后会显示关键节点、责任人、文件和风险。" : "No visible projects yet; project milestones, owners, files, and risk will appear here.")}
          </div>
        </article>
        <article class="transparent-armor-detail">
          <div class="transparent-armor-detail__head">
            <strong>${zh ? "移动三步审批" : "Mobile 3-Step Approval"}</strong>
            <span>${zh ? "碎片化场景下只保留关键判断" : "Only key judgment in mobile moments"}</span>
          </div>
          <div class="transparent-armor-step-list">
            ${mobileSteps.map((item, index) => `
              <div class="transparent-armor-step">
                <b>${index + 1}</b>
                <div>
                  <strong>${escapeHtml(item.title || "--")}</strong>
                  <span>${escapeHtml(item.detail || "--")}</span>
                </div>
              </div>
            `).join("") || renderEmptyState(zh ? "暂无移动审批配置" : "No mobile approval flow")}
          </div>
        </article>
        <article class="transparent-armor-detail">
          <div class="transparent-armor-detail__head">
            <strong>${zh ? "AI 知识资产库" : "AI Knowledge Assets"}</strong>
            <span>${zh ? "新人可学，项目可复用" : "Learnable for new joiners, reusable for projects"}</span>
          </div>
          <div class="transparent-armor-policy-list">
            ${knowledgeRoutes.map((item) => `
              <div class="transparent-armor-policy-row">
                ${renderStatusBadge(item.entry || "asset", "neutral")}
                <div>
                  <strong>${escapeHtml(item.title || "--")}</strong>
                  <span>${escapeHtml(item.purpose || "--")}</span>
                </div>
              </div>
            `).join("") || renderEmptyState(zh ? "暂无知识资产路径" : "No knowledge asset routes")}
          </div>
        </article>
      </div>
      <div class="transparent-armor-flow">
        <span>${zh ? "三步触达：总控台 → 风险/待办 → 审批或项目工作室" : "Three-step flow: command → risk/task → approval or war room"}</span>
        <span>${zh ? "Need-to-know：权限、同事可见范围、导出和下载均有提示或留痕" : "Need-to-know: permissions, colleague scope, exports, and downloads are prompted or logged"}</span>
        <span>${zh ? "知识复用：Skill 指南、SBLC/DLC 流程、尽调和模板统一进入资产库" : "Knowledge reuse: skills, SBLC/DLC procedures, diligence, and templates feed the asset library"}</span>
      </div>
    </section>
  `;
}

async function loadGovernanceCenterPage() {
  ensureWorkMgmtPagesShell();
  const page = document.getElementById("governance-center");
  if (!page) return;
  const host = page.querySelector("[data-governance-center-body]");
  if (!host) return;
  host.innerHTML = renderLoadingSkeleton(4);
  try {
    const [governanceResult, workbenchResult, myWorkResult] = await Promise.allSettled([
      loadGovernanceControlData(),
      loadV2DashboardWorkbench("my"),
      loadV2MyWork(),
    ]);
    const governance = governanceResult.status === "fulfilled" ? governanceResult.value : null;
    const workbench = workbenchResult.status === "fulfilled" ? workbenchResult.value : {};
    const myWork = myWorkResult.status === "fulfilled" ? myWorkResult.value : {};
    if (!governance) throw new Error("governance_failed");
    host.innerHTML = `
      ${renderInstitutionalOperatingSystemLayer({ workbench, myWork, governance, status: appState.status || {} })}
      ${renderGovernanceControlLayer(governance, { workbench, myWork })}
    `;
  } catch (error) {
    const needsLogin = String(error.message || appState.governance.error || "").includes("authentication_required");
    host.innerHTML = renderErrorState(
      needsLogin
        ? (lang() === "zh" ? "请先登录后查看合规审计中心" : "Please sign in to view Compliance Center")
        : (lang() === "zh" ? "合规审计中心暂时不可用" : "Compliance center is temporarily unavailable"),
      authErrorMessage(error.message || appState.governance.error || "governance_failed"),
    );
  }
}

function renderRiskNoticeCard(items = []) {
  const rows = (Array.isArray(items) ? items : []).slice(0, 6);
  return `
    <section class="hermes-panel risk-notice-card">
      <div class="intel-block-title"><strong>${lang() === "zh" ? "Attention Items" : "Attention Items"}</strong></div>
      ${rows.length ? rows.map((item) => `
        <div class="intel-alert-row">
          ${renderStatusBadge(item.level || (lang() === "zh" ? "中" : "Medium"), item.state || "warning")}
          <span>${escapeHtml(item.title || "--")}</span>
        </div>
      `).join("") : renderEmptyState(lang() === "zh" ? "暂无需人工介入事项" : "No manual intervention needed")}
    </section>
  `;
}

function renderChartCard(points = [], state = "ready") {
  const rows = Array.isArray(points) ? points.slice(0, 14) : [];
  const maxValue = Math.max(1, ...rows.map((item) => Number(item.value || 0)));
  return `
    <section class="hermes-panel chart-card">
      <div class="intel-chart-head">
        <h4>${lang() === "zh" ? "Main Trend" : "Main Trend"}</h4>
        <div class="intel-chart-tags">
          <span class="tag">${lang() === "zh" ? "时间范围：14天" : "Range: 14 days"}</span>
        </div>
      </div>
      ${state === "loading" ? renderLoadingSkeleton(3) : ""}
      ${!rows.length && state !== "loading" ? renderEmptyState(lang() === "zh" ? "暂无趋势数据" : "No trend data") : ""}
      ${rows.length ? `
        <div class="hermes-mini-chart">
          ${rows.map((item) => `<span style="height:${Math.max(10, Math.round((Number(item.value || 0) / maxValue) * 96))}px" title="${escapeHtml(`${item.label}: ${item.value}`)}"></span>`).join("")}
        </div>
      ` : ""}
    </section>
  `;
}

function renderHermesExecutiveBrief({ workbench = {}, myWork = {}, statusPayload = {}, governance = {}, alerts = [] } = {}) {
  const zh = lang() === "zh";
  const quickViews = workbench.quick_views || {};
  const tasks = Array.isArray(myWork.tasks_today) ? myWork.tasks_today : [];
  const pendingDocs = Array.isArray(myWork.pending_documents) ? myWork.pending_documents.length : 0;
  const market = intelQualityMetrics();
  const sblcDocs = sblcPackageItems();
  const sblcRequired = sblcDocumentPackageData().filter((doc) => doc.required);
  const sblcMissing = sblcRequired.filter((doc) => !sblcPackageStatus(doc.id).items.length).length;
  const governanceRisk = Number(governance?.risk_queue?.critical_count || 0);
  const overdue = Number(quickViews.overdue_tasks || 0);
  const ai8Route = statusPayload?.route_health?.ai8 || {};
  const ai8Ready = String(ai8Route?.status || "").toLowerCase() === "ready" || ai8Route?.available;
  const systemIssues = statusPayload.hermes_online ? 0 : 1;
  const rows = [
    {
      key: "decision",
      label: zh ? "今日需决策" : "Decisions Today",
      value: String(Number(quickViews.pending_approvals || 0) + pendingDocs),
      detail: zh ? "审批、文件、待补资料" : "Approvals, files, missing material",
      state: pendingDocs ? "warning" : "success",
      action: zh ? "进入我的待办" : "Open My Work",
      page: "my-work",
    },
    {
      key: "risk",
      label: zh ? "高风险事项" : "High-Risk Items",
      value: String(Math.max(governanceRisk, alerts.length, Number(quickViews.high_risk_projects || 0), overdue)),
      detail: zh ? `项目阻塞、DLP、超期 ${overdue}` : `Blockers, DLP, overdue ${overdue}`,
      state: alerts.length || governanceRisk || overdue ? "error" : "success",
      action: zh ? "看合规异常" : "Review Compliance",
      page: "governance-center",
    },
    {
      key: "sblc",
      label: "SBLC / DLC",
      value: sblcDocs.length ? `${Math.max(0, sblcRequired.length - sblcMissing)}/${sblcRequired.length}` : "--",
      detail: sblcDocs.length ? (zh ? "Gate 资料包完成度" : "Gate package completion") : (zh ? "等待上传交易材料" : "Awaiting deal package"),
      state: sblcMissing ? "warning" : (sblcDocs.length ? "success" : "neutral"),
      action: zh ? "进入文件 Gate" : "Open File Gate",
      page: "file-center",
    },
    {
      key: "file-review",
      label: zh ? "文件待审" : "File Reviews",
      value: String(pendingDocs),
      detail: zh ? "审阅、审批、签字与补材料" : "Review, approval, signature, missing docs",
      state: pendingDocs ? "warning" : "success",
      action: zh ? "处理文件" : "Review Files",
      page: "file-center",
    },
    {
      key: "ai-agent",
      label: zh ? "AI Agent 健康" : "AI Agent Health",
      value: ai8Ready ? (zh ? "就绪" : "Ready") : (zh ? "需配置" : "Setup"),
      detail: ai8Route?.reason || (zh ? "AI8、人机入口、任务回填" : "AI8, human bridge, task return"),
      state: ai8Ready ? "success" : "warning",
      action: zh ? "打开 Agent" : "Open Agent",
      page: "ai-agent",
    },
    {
      key: "knowledge",
      label: zh ? "知识资产" : "Knowledge Assets",
      value: zh ? "已沉淀" : "Mapped",
      detail: zh ? "Skill、模板、案例与审核意见进入记忆库" : "Skills, templates, cases, review opinions mapped",
      state: "success",
      action: zh ? "查看 Skill" : "Open Skills",
      page: "skills",
    },
    {
      key: "market",
      label: zh ? "市场信号" : "Market Signal",
      value: market.totalNews ? `${Math.round((market.zhReady / market.totalNews) * 100)}%` : "--",
      detail: market.totalNews ? (zh ? "中文情报覆盖" : "CN intelligence coverage") : (zh ? "等待情报刷新" : "Awaiting intel refresh"),
      state: market.fallback ? "warning" : "success",
      action: zh ? "打开情报" : "Open Intel",
      page: "intel-center",
    },
    {
      key: "system",
      label: zh ? "系统异常" : "System Exceptions",
      value: String(systemIssues),
      detail: zh ? "网关、路由、集成状态" : "Gateway, routing, integration",
      state: systemIssues ? "error" : "success",
      action: zh ? "刷新状态" : "Refresh",
      actionType: "refresh",
    },
  ];
  return `
    <section class="executive-brief-shell">
      <div class="executive-brief-head">
        <div>
          <div class="eyebrow">EXECUTIVE BRIEF</div>
          <h2>${zh ? "今天先处理什么" : "What needs attention today"}</h2>
          <p>${zh ? "首页只保留管理层 10 秒内必须判断的待决策、高风险、交易 Gate、文件待审、AI Agent、市场信号和系统异常。" : "The homepage keeps only decisions, risks, deal gates, file reviews, AI Agent, market signals, and system exceptions."}</p>
        </div>
        <div class="executive-brief-head__meta">
          <span>${zh ? "更新" : "Updated"}</span>
          <strong>${escapeHtml(formatDateTime(Math.floor(Date.now() / 1000)))}</strong>
        </div>
      </div>
      <div class="executive-brief-grid">
        ${rows.map((item) => `
          <article class="executive-brief-card executive-brief-card--${escapeHtml(item.state)}">
            <div class="executive-brief-card__top">
              <span>${escapeHtml(item.label)}</span>
              ${renderStatusBadge(item.state === "error" ? (zh ? "风险" : "Risk") : item.state === "warning" ? (zh ? "关注" : "Watch") : item.state === "success" ? (zh ? "正常" : "OK") : (zh ? "待资料" : "Pending"), item.state)}
            </div>
            <strong>${escapeHtml(item.value)}</strong>
            <em>${escapeHtml(item.detail)}</em>
            <button class="btn ${item.state === "error" ? "btn-primary" : "btn-ghost"}" type="button" ${item.skill ? `data-executive-skill="${escapeHtml(item.skill)}"` : item.actionType ? `data-hermes-action="${escapeHtml(item.actionType)}"` : `data-executive-page="${escapeHtml(item.page)}"`}>${escapeHtml(item.action)}</button>
          </article>
        `).join("")}
      </div>
      <div class="decision-strip decision-strip--executive">
        <span>${zh ? "闭环路径" : "Closure Path"}</span>
        <strong>${zh ? "发现问题 → 查看依据 → 执行动作" : "Find issue → Review evidence → Act"}</strong>
        <em>${zh ? "所有正式结论必须经过复核、采用或驳回状态标记。" : "Formal conclusions must be marked reviewed, adopted, or rejected."}</em>
      </div>
    </section>
  `;
}

function ensureHermesFlagshipSection() {
  const home = document.getElementById("home");
  if (!home) return;
  let section = home.querySelector("[data-hermes-flagship]");
  if (!section) {
    section = document.createElement("section");
    section.className = "section";
    section.setAttribute("data-hermes-flagship", "1");
    section.innerHTML = `
      <div class="hermes-flagship-shell">
        <div data-hermes-flagship-body></div>
        <div data-hermes-state-layer></div>
      </div>
    `;
    const anchor = home.querySelector(".section");
    if (anchor) home.insertBefore(section, anchor);
    else home.appendChild(section);
  }
}

function bindHermesFlagshipActions(section) {
  const root = section || document.querySelector("[data-hermes-flagship]");
  if (!root) return;
  root.querySelectorAll("[data-hermes-action]").forEach((button) => {
    if (button.dataset.boundHermesAction === "1") return;
    button.dataset.boundHermesAction = "1";
    button.addEventListener("click", async () => {
      const action = String(button.getAttribute("data-hermes-action") || "").trim();
      if (action === "open-intel") {
        setActivePage("intel-center", true);
        return;
      }
      if (action === "open-ai-agent") {
        setActivePage("ai-agent", true);
        return;
      }
      if (action === "open-workbench") {
        setActivePage("workbench", true);
        return;
      }
      if (action === "open-mywork") {
        setActivePage("my-work", true);
        return;
      }
      if (action === "refresh") {
        await loadHermesFlagshipData({ syncing: true, showLoading: false });
        return;
      }
      if (action === "create-item") {
        setActivePage("workbench", true);
      }
    });
  });
  root.querySelectorAll("[data-hermes-task-filter]").forEach((select) => {
    if (select.dataset.boundHermesFilter === "1") return;
    select.dataset.boundHermesFilter = "1";
    select.addEventListener("change", () => {
      appState.hermes.taskFilter = String(select.value || "all");
      loadHermesFlagshipData({ showLoading: false }).catch(() => {});
    });
  });
  root.querySelectorAll("[data-executive-page]").forEach((button) => {
    if (button.dataset.boundExecutivePage === "1") return;
    button.dataset.boundExecutivePage = "1";
    button.addEventListener("click", () => setActivePage(button.getAttribute("data-executive-page") || "home", true));
  });
  root.querySelectorAll("[data-executive-skill]").forEach((button) => {
    if (button.dataset.boundExecutiveSkill === "1") return;
    button.dataset.boundExecutiveSkill = "1";
    button.addEventListener("click", () => navigateToWorkspaceSkill(button.getAttribute("data-executive-skill") || "banking-sblc", true));
  });
}

function renderHermesKnowledgeAssetStrip() {
  const zh = lang() === "zh";
  const items = [
    {
      title: zh ? "场景化 Skill" : "Scenario Skills",
      detail: zh ? "合同审查、SBLC/DLC、尽调、财报、客户跟进按任务检索。" : "Contract, SBLC/DLC, DD, earnings, client follow-up by task.",
      action: zh ? "进入 Skill" : "Open Skills",
      page: "skills",
    },
    {
      title: zh ? "交易模板库" : "Deal Templates",
      detail: zh ? "SPA、KYC、银行函、托管、审核意见与导出标准集中沉淀。" : "SPA, KYC, bank letters, escrow, review opinions, export standards.",
      action: zh ? "查看文件中心" : "Open Files",
      page: "file-center",
    },
    {
      title: zh ? "AI 输出状态化" : "AI Output State",
      detail: zh ? "AI 内容必须标记草稿、待复核、已采用或已驳回。" : "AI output must be draft, review, adopted, or rejected.",
      action: zh ? "打开 Agent" : "Open Agent",
      page: "ai-agent",
    },
    {
      title: zh ? "历史经验记忆" : "Institutional Memory",
      detail: zh ? "平台设计原则、流程闭环和审计要求写入 Hermes 研究记忆。" : "Design principles, closure workflow, and audit rules live in Hermes memory.",
      action: zh ? "看合规" : "Open Compliance",
      page: "governance-center",
    },
  ];
  return `
    <section class="knowledge-asset-brief">
      <div class="workbench-card-head">
        <div>
          <span>${zh ? "Knowledge Asset Layer" : "Knowledge Asset Layer"}</span>
          <h3>${zh ? "Hermes 公司经验资产库" : "Hermes Institutional Knowledge Base"}</h3>
        </div>
        <em>${zh ? "新人按场景学习，项目按模板复用，AI 输出进入正式流程。" : "Newcomers learn by scenario; projects reuse templates; AI output enters workflow."}</em>
      </div>
      <div class="knowledge-asset-brief__grid">
        ${items.map((item) => `
          <article class="knowledge-asset-brief__card">
            <strong>${escapeHtml(item.title)}</strong>
            <p>${escapeHtml(item.detail)}</p>
            <button class="btn btn-ghost" type="button" data-executive-page="${escapeHtml(item.page)}">${escapeHtml(item.action)}</button>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function buildInstitutionalOperatingModel({ workbench = {}, myWork = {}, governance = {}, status = {} } = {}) {
  const zh = lang() === "zh";
  const quickViews = workbench.quick_views || {};
  const projects = Array.isArray(workbench.projects) ? workbench.projects : [];
  const warItems = Array.isArray(workbench.war_room_items) ? workbench.war_room_items : [];
  const tasks = Array.isArray(myWork.tasks_today) ? myWork.tasks_today : [];
  const pendingDocs = Array.isArray(myWork.pending_documents) ? myWork.pending_documents : [];
  const riskItems = Array.isArray(governance?.risk_queue?.items) ? governance.risk_queue.items : [];
  const crossChecks = Array.isArray(governance?.cross_check?.items) ? governance.cross_check.items : [];
  const auditTimeline = Array.isArray(governance?.compliance?.audit_timeline) ? governance.compliance.audit_timeline : [];
  const aiOutputs = Array.isArray(governance?.compliance?.ai_outputs) ? governance.compliance.ai_outputs : [];
  const sblcRequired = sblcDocumentPackageData().filter((doc) => doc.required);
  const sblcCompleted = sblcRequired.filter((doc) => sblcPackageStatus(doc.id).items.length).length;
  const highRisk = Number(quickViews.high_risk_projects || 0);
  const overdue = Number(quickViews.overdue_tasks || 0);
  const pendingApprovals = Number(quickViews.pending_approvals || 0);
  const ai8Route = status?.route_health?.ai8 || {};
  const systemIssue = status?.hermes_online ? 0 : 1;
  const actionQueue = [
    ...riskItems.slice(0, 4).map((item) => ({
      priority: "P0",
      state: "error",
      title: item.title || (zh ? "高风险事项" : "High-risk item"),
      object: item.project_name || item.project_id || item.workspace_id || (zh ? "未绑定交易" : "Unlinked deal"),
      owner: item.owner || (zh ? "待指定" : "Unassigned"),
      due: item.due || item.deadline || (zh ? "今日复核" : "Review today"),
      action: item.next_step || (zh ? "查看依据并确定处理人" : "Review evidence and assign owner"),
    })),
    ...tasks.filter((task) => String(task?.priority || "").toLowerCase() === "high" || String(task?.status || "").toLowerCase().includes("overdue")).slice(0, 4).map((task) => ({
      priority: "P1",
      state: String(task?.status || "").toLowerCase().includes("overdue") ? "error" : "warning",
      title: task.title || task.id || (zh ? "待办事项" : "Task"),
      object: task.project_id || (zh ? "项目队列" : "Project queue"),
      owner: task.assignee_id || task.owner_id || (zh ? "本人/负责人" : "Me/owner"),
      due: task.due_at ? formatDateTime(task.due_at) : (zh ? "今日" : "Today"),
      action: zh ? "处理或重新设定截止时间" : "Act or reset due date",
    })),
    ...pendingDocs.slice(0, 3).map((doc) => ({
      priority: "P1",
      state: "warning",
      title: doc.title || doc.file_title || (zh ? "文件待审" : "File review"),
      object: doc.file_id || doc.workspace_id || (zh ? "文件中心" : "File center"),
      owner: doc.owner_user_id || doc.assignee_id || (zh ? "文件负责人" : "File owner"),
      due: zh ? "待审阅/签字" : "Review/signing pending",
      action: zh ? "进入文件 Gate Control" : "Open File Gate Control",
    })),
    ...(systemIssue ? [{
      priority: "P0",
      state: "error",
      title: zh ? "系统异常" : "System exception",
      object: "Hermes",
      owner: "Ops",
      due: zh ? "立即" : "Immediate",
      action: zh ? "刷新状态并检查路由" : "Refresh status and inspect routes",
    }] : []),
  ].slice(0, 10);
  const dealObjects = (warItems.length ? warItems : projects).slice(0, 6).map((item) => ({
    id: item.id || item.project_id || item.name || "--",
    title: item.name || item.title || item.id || "--",
    owner: item.owner_id || item.owner || (zh ? "未指定" : "Unassigned"),
    status: item.status || "active",
    files: Number(item.files || item.documents || 0),
    risk: Number(item.high_risk_items || item.high_risk || item.issue_blocker_count || 0),
    next: item.next_action || (zh ? "查看项目证据和待办" : "Review project evidence and tasks"),
  }));
  const exceptions = [
    ...crossChecks.slice(0, 5).map((item) => ({
      type: item.type || "cross_check",
      state: String(item.severity || "").includes("high") ? "error" : "warning",
      title: item.title || item.type || (zh ? "交叉检查异常" : "Cross-check exception"),
      evidence: item.recommendation || item.detail || (zh ? "查看文件字段差异" : "Review file field discrepancy"),
      owner: item.owner || "Compliance",
    })),
    ...(overdue ? [{
      type: "overdue",
      state: "error",
      title: zh ? `超期事项 ${overdue}` : `${overdue} overdue items`,
      evidence: zh ? "统一行动队列需要负责人解释和新期限" : "Action queue needs owner explanation and new date",
      owner: "PMO",
    }] : []),
    ...(sblcCompleted < sblcRequired.length ? [{
      type: "gate_blocker",
      state: "warning",
      title: zh ? "SBLC/DLC Gate 资料未齐" : "SBLC/DLC gate package incomplete",
      evidence: `${sblcCompleted}/${sblcRequired.length}`,
      owner: "Deal Team",
    }] : []),
  ].slice(0, 8);
  const memoPoints = [
    zh ? `今日待决策 ${pendingApprovals + pendingDocs.length} 项，超期 ${overdue} 项，高风险项目 ${highRisk} 个。` : `${pendingApprovals + pendingDocs.length} decisions today, ${overdue} overdue, ${highRisk} high-risk projects.`,
    zh ? `SBLC/DLC Gate 完成 ${sblcCompleted}/${sblcRequired.length}，未齐材料不得进入下一步。` : `SBLC/DLC gate completion ${sblcCompleted}/${sblcRequired.length}; incomplete gates should not proceed.`,
    zh ? `AI8 Agent：${ai8Route.available || ai8Route.status === "ready" ? "可用" : "需配置"}，AI 输出须复核后采用。` : `AI8 Agent: ${ai8Route.available || ai8Route.status === "ready" ? "ready" : "setup needed"}; AI outputs require review before adoption.`,
  ];
  return { actionQueue, dealObjects, exceptions, auditTimeline, aiOutputs, memoPoints, sblcCompleted, sblcRequired, highRisk, overdue, pendingApprovals, pendingDocs };
}

function renderInstitutionalOperatingSystemLayer(input = {}) {
  const zh = lang() === "zh";
  const model = buildInstitutionalOperatingModel(input);
  const gateRows = (sblcIssuerControlData().gates || []).slice(0, 6).map((row) => {
    const gate = { id: row[0], title: row[1], owner: row[2], evidence: row[3], blocker: row[4] };
    const status = sblcGateControlStatus(gate);
    return { gate, status };
  });
  return `
    <section class="institutional-os-layer">
      <div class="workbench-card-head">
        <div>
          <span>${zh ? "Institutional Operating System" : "Institutional Operating System"}</span>
          <h3>${zh ? "交易操作系统总线" : "Deal Operating System Bus"}</h3>
        </div>
        <em>${zh ? "交易对象 → 风险/例外 → 证据 → Owner → 动作 → 审计回放" : "Deal object → risk/exception → evidence → owner → action → audit replay"}</em>
      </div>
      <div class="institutional-os-grid institutional-os-grid--top">
        <article class="institutional-os-card institutional-os-card--memo">
          <div class="institutional-os-card__head">
            <strong>${zh ? "管理层 Memo" : "Executive Memo"}</strong>
            ${renderStatusBadge(zh ? "今日" : "Today", "info")}
          </div>
          <div class="institutional-os-memo">
            ${model.memoPoints.map((item) => `<p>${escapeHtml(item)}</p>`).join("")}
          </div>
          <button class="btn btn-ghost" type="button" data-executive-page="reports">${zh ? "进入报告中心" : "Open Reports"}</button>
        </article>
        <article class="institutional-os-card">
          <div class="institutional-os-card__head">
            <strong>${zh ? "统一行动队列" : "Unified Action Queue"}</strong>
            ${renderStatusBadge(String(model.actionQueue.length), model.actionQueue.some((item) => item.state === "error") ? "error" : "warning")}
          </div>
          <div class="institutional-os-list">
            ${model.actionQueue.length ? model.actionQueue.map((item) => `
              <div class="institutional-os-row">
                ${renderStatusBadge(item.priority, item.state)}
                <div>
                  <strong>${escapeHtml(item.title)}</strong>
                  <span>${escapeHtml(item.object)} · ${escapeHtml(item.owner)} · ${escapeHtml(item.due)}</span>
                  <em>${escapeHtml(item.action)}</em>
                </div>
              </div>
            `).join("") : renderEmptyState(zh ? "暂无高优先行动。" : "No priority actions.")}
          </div>
        </article>
      </div>
      <div class="institutional-os-grid">
        <article class="institutional-os-card">
          <div class="institutional-os-card__head">
            <strong>${zh ? "交易对象主线" : "Deal / Project Objects"}</strong>
            ${renderStatusBadge(String(model.dealObjects.length), "neutral")}
          </div>
          <div class="institutional-os-list">
            ${model.dealObjects.length ? model.dealObjects.map((item) => `
              <div class="institutional-os-row">
                ${renderStatusBadge(item.risk ? (zh ? "风险" : "Risk") : unifiedStatusLabel(item.status), item.risk ? "warning" : "success")}
                <div>
                  <strong>${escapeHtml(item.title)}</strong>
                  <span>${escapeHtml(item.owner)} · ${zh ? "文件" : "Files"} ${escapeHtml(String(item.files))} · ${zh ? "风险" : "Risk"} ${escapeHtml(String(item.risk))}</span>
                  <em>${escapeHtml(item.next)}</em>
                </div>
              </div>
            `).join("") : renderEmptyState(zh ? "暂无交易对象；项目建立后会自动聚合文件、审批、AI 输出和风险。" : "No deal objects yet; projects will aggregate files, approvals, AI outputs, and risks.")}
          </div>
        </article>
        <article class="institutional-os-card">
          <div class="institutional-os-card__head">
            <strong>${zh ? "Gate Engine" : "Gate Engine"}</strong>
            ${renderStatusBadge(`${model.sblcCompleted}/${model.sblcRequired.length}`, model.sblcCompleted === model.sblcRequired.length ? "success" : "warning")}
          </div>
          <div class="institutional-os-list">
            ${gateRows.map(({ gate, status }) => `
              <div class="institutional-os-row">
                ${renderStatusBadge(status.label, status.state)}
                <div>
                  <strong>${escapeHtml(gate.title || gate.id)}</strong>
                  <span>${escapeHtml(status.blocker || "")}</span>
                  <em>${escapeHtml(status.next || "")}</em>
                </div>
              </div>
            `).join("")}
          </div>
        </article>
        <article class="institutional-os-card">
          <div class="institutional-os-card__head">
            <strong>${zh ? "例外管理台账" : "Exception Register"}</strong>
            ${renderStatusBadge(String(model.exceptions.length), model.exceptions.some((item) => item.state === "error") ? "error" : "warning")}
          </div>
          <div class="institutional-os-list">
            ${model.exceptions.length ? model.exceptions.map((item) => `
              <div class="institutional-os-row">
                ${renderStatusBadge(item.type, item.state)}
                <div>
                  <strong>${escapeHtml(item.title)}</strong>
                  <span>${escapeHtml(item.owner)}</span>
                  <em>${escapeHtml(item.evidence)}</em>
                </div>
              </div>
            `).join("") : renderEmptyState(zh ? "暂无例外；资料缺失、字段冲突、权限越界、签字失败会进入这里。" : "No exceptions; missing docs, field conflicts, permission breaches, and signature failures appear here.")}
          </div>
        </article>
        <article class="institutional-os-card">
          <div class="institutional-os-card__head">
            <strong>${zh ? "审计回放" : "Audit Replay"}</strong>
            ${renderStatusBadge(String(model.auditTimeline.length), "neutral")}
          </div>
          <div class="institutional-os-list">
            ${model.auditTimeline.slice(0, 5).map((item) => `
              <div class="institutional-os-row">
                ${renderStatusBadge(item.category || "log", item.category === "ai_output" ? "warning" : "neutral")}
                <div>
                  <strong>${escapeHtml(item.object || item.event || "--")}</strong>
                  <span>${escapeHtml(item.actor || "system")} · ${escapeHtml(item.ts || "--")}</span>
                  <em>${escapeHtml(item.event || "--")}</em>
                </div>
              </div>
            `).join("") || renderEmptyState(zh ? "暂无审计回放事件。" : "No audit replay events.")}
          </div>
        </article>
      </div>
      <div class="institutional-os-flow">
        <span>${zh ? "AI Agent：草稿 → 待复核 → 已采用/已驳回 → 归档" : "AI Agent: draft → review → adopted/rejected → archived"}</span>
        <span>${zh ? "文件：上传 → 差异雷达 → 审阅/审批 → 签字/验签 → 审核意见出口" : "Files: upload → radar → review/approval → sign/verify → opinion export"}</span>
        <span>${zh ? "风控：例外台账必须有 owner、截止时间、证据和关闭原因" : "Risk: every exception needs owner, deadline, evidence, and closure reason"}</span>
      </div>
    </section>
  `;
}

async function loadHermesFlagshipData(options = {}) {
  ensureHermesFlagshipSection();
  const section = document.querySelector("[data-hermes-flagship]");
  const bodyNode = section?.querySelector("[data-hermes-flagship-body]");
  const stateLayerNode = section?.querySelector("[data-hermes-state-layer]");
  if (!section || !bodyNode) return;
  if (!appState.auth.authenticated) {
    bodyNode.innerHTML = `
      ${renderPageHeader({
        title: "Hermes",
        description: lang() === "zh" ? "管理层执行简报：登录后显示真实风险、审批、交易、市场信号与 AI/系统健康。" : "Executive brief: sign in to view live risk, approvals, deals, market signals, and AI/system health.",
        updatedText: formatDateTime(Math.floor(Date.now() / 1000)),
      })}
      ${renderHermesExecutiveBrief({ statusPayload: appState.status || {}, workbench: { quick_views: {} }, myWork: {}, governance: {}, alerts: [] })}
    `;
    if (stateLayerNode) {
      stateLayerNode.innerHTML = renderStateLayer("no-permission", {
        detail: lang() === "zh" ? "请登录后查看真实管理层指标和审计数据。" : "Sign in to view live executive metrics and audit data.",
      });
    }
    bindHermesFlagshipActions(section);
    return;
  }
  const syncing = !!options?.syncing;
  if (options?.showLoading !== false && stateLayerNode) {
    stateLayerNode.innerHTML = renderStateLayer(syncing ? "syncing" : "loading", { rows: 4 });
  }
  const statusPayload = appState.status || {};
  try {
    const settled = await Promise.allSettled([
      loadV2Workbench("scope=my"),
      loadV2MyWork(),
      loadGovernanceControlData(),
    ]);
    const workbench = settled[0]?.status === "fulfilled" ? settled[0].value : { projects: [], quick_views: {} };
    const myWork = settled[1]?.status === "fulfilled" ? settled[1].value : { tasks_today: [], pending_documents: [], my_reports: [] };
    const governance = settled[2]?.status === "fulfilled" ? settled[2].value : appState.governance.data;
    if (settled[0]?.status !== "fulfilled" && settled[1]?.status !== "fulfilled") {
      throw new Error(settled[0]?.reason?.message || settled[1]?.reason?.message || "hermes_data_failed");
    }
    const partial = settled.some((item) => item.status !== "fulfilled");
    appState.hermes.data = { workbench, myWork, status: statusPayload };
    appState.hermes.state = partial ? "partial" : "ready";
    appState.hermes.error = "";
    const sprint = statusPayload?.sprint_supervision || {};
    const timelineItems = Array.isArray(sprint?.items) ? sprint.items : [];
    const chartPoints = timelineItems.length
      ? timelineItems.slice(-14).map((item) => ({ label: `${lang() === "zh" ? "D" : "D"}${Number(item.day || 0)}`, value: String(item.status || "").toLowerCase() === "done" ? 100 : String(item.status || "").toLowerCase() === "blocked" ? 40 : 70 }))
      : [];
    const tasks = Array.isArray(myWork?.tasks_today) ? myWork.tasks_today : [];
    const alerts = [
      ...(Array.isArray(workbench?.projects) ? workbench.projects : [])
        .filter((project) => Number(project?.issue_blocker_count || 0) > 0)
        .slice(0, 3)
        .map((project) => ({ title: project?.name || project?.id || "--", level: lang() === "zh" ? "高" : "High", state: "error" })),
      ...(tasks.filter((task) => String(task?.priority || "").toLowerCase() === "high").slice(0, 3).map((task) => ({ title: task?.title || task?.id || "--", level: lang() === "zh" ? "中" : "Medium", state: "warning" }))),
    ];
    const activity = [
      ...tasks.slice(0, 5).map((task) => ({
        timeText: formatDateTime(task?.updated_at || task?.created_at || Math.floor(Date.now() / 1000)),
        title: task?.title || task?.id || "--",
        detail: `${unifiedStatusLabel(task?.status || "pending")} · ${task?.project_id || "--"}`,
      })),
      ...timelineItems.slice(0, 5).map((item) => ({
        timeText: lang() === "zh" ? `第${Number(item?.day || 0)}天` : `Day ${Number(item?.day || 0)}`,
        title: String(item?.title || "--"),
        detail: String(item?.status || "--"),
      })),
    ].slice(0, 10);
    const quickViews = workbench?.quick_views || {};
    const overviewCards = [
      { label: lang() === "zh" ? "进行中任务" : "In-Progress Tasks", value: Number(quickViews.my_pending_items || tasks.length || 0), detail: lang() === "zh" ? "当前进行中" : "Current active items" },
      { label: lang() === "zh" ? "高优先级提醒" : "High Priority Alerts", value: alerts.length, detail: lang() === "zh" ? "需要关注" : "Needs attention", badge: alerts.length ? { label: lang() === "zh" ? "关注" : "Watch", state: "warning" } : null },
      { label: lang() === "zh" ? "今日新增动态" : "New Updates Today", value: activity.length, detail: lang() === "zh" ? "按更新时间" : "By latest update" },
      { label: lang() === "zh" ? "待处理事项" : "Pending Approvals", value: Number(quickViews.pending_approvals || 0), detail: lang() === "zh" ? "等待审批" : "Awaiting approval" },
      { label: lang() === "zh" ? "同步健康状态" : "Sync Health", value: statusPayload?.hermes_online ? (lang() === "zh" ? "正常" : "Healthy") : (lang() === "zh" ? "异常" : "Issue"), detail: lang() === "zh" ? "网关与路由" : "Gateway and routing", badge: { label: statusPayload?.hermes_online ? (lang() === "zh" ? "在线" : "Online") : (lang() === "zh" ? "离线" : "Offline"), state: statusPayload?.hermes_online ? "success" : "error" } },
      { label: lang() === "zh" ? "风险等级概览" : "Risk Overview", value: alerts.length ? (lang() === "zh" ? "中高" : "Medium-High") : (lang() === "zh" ? "常规" : "Normal"), detail: lang() === "zh" ? "综合任务/阻塞" : "Tasks and blockers", badge: alerts.length ? { label: lang() === "zh" ? "风险" : "Risk", state: "warning" } : null },
    ];
    bodyNode.innerHTML = `
      ${renderPageHeader({
        title: "Hermes",
        description: lang() === "zh" ? "管理层执行简报：风险、审批、交易、市场信号与 AI/系统健康集中判断。" : "Executive brief for risk, approvals, deals, market signals, and AI/system health.",
        updatedText: formatDateTime(Math.floor(Date.now() / 1000)),
      })}
      ${renderHermesExecutiveBrief({ workbench, myWork, statusPayload, governance, alerts })}
      ${renderHermesReadinessStrip({ status: statusPayload, workbench, myWork })}
      <details class="executive-secondary-details">
        <summary>
          <span>${lang() === "zh" ? "展开二级工作层" : "Open secondary work layer"}</span>
          <strong>${lang() === "zh" ? "治理、任务、动态、图表和知识资产已下沉" : "Governance, tasks, activity, charts, and knowledge assets are kept below the fold"}</strong>
        </summary>
        <div class="executive-secondary-details__body">
          ${renderInstitutionalOperatingSystemLayer({ workbench, myWork, governance, status: statusPayload })}
          ${renderGovernanceControlLayer(governance, { workbench, myWork, status: statusPayload })}
          ${renderHermesKnowledgeAssetStrip()}
          <section class="hermes-overview-grid">
            ${overviewCards.map((card) => renderMetricCard(card)).join("")}
          </section>
          <section class="hermes-main-content">
            <div class="hermes-main-left">
              ${renderTaskListCard(tasks, syncing ? "syncing" : "ready")}
              ${renderActivityTimelineCard(activity, syncing ? "syncing" : "ready")}
              ${renderChartCard(chartPoints, syncing ? "syncing" : "ready")}
            </div>
            <aside class="hermes-main-right">
              ${renderSystemStatusCard({ route_health: statusPayload?.route_health || {}, routeStatus: appState.routeStatus || "" }, syncing ? "syncing" : "ready")}
              ${renderQuickActionsCard()}
              ${renderRiskNoticeCard(alerts)}
              ${renderActivityTimelineCard(activity.slice(0, 5), syncing ? "syncing" : "ready")}
            </aside>
          </section>
        </div>
      </details>
    `;
    bindHermesFlagshipActions(section);
    if (stateLayerNode) {
      stateLayerNode.innerHTML = partial
        ? renderStateLayer("partial", { detail: lang() === "zh" ? "部分数据暂不可用，已展示可用模块。" : "Some data is unavailable; available modules are shown." })
        : "";
    }
    renderPlatformCommandStrip();
  } catch (error) {
    const raw = String(error?.message || "").toLowerCase();
    const noPermission = raw.includes("authentication_required") || raw.includes("permission_denied");
    appState.hermes.state = noPermission ? "no-permission" : "error";
    appState.hermes.error = authErrorMessage(error.message);
    if (stateLayerNode) {
      stateLayerNode.innerHTML = renderStateLayer(noPermission ? "no-permission" : "error", {
        detail: authErrorMessage(error.message),
      });
    }
    renderPlatformCommandStrip();
  }
}

function workMgmtCopy() {
  const zh = lang() === "zh";
  return {
    title: zh ? "多项目协同中枢" : "Multi-Project Command Center",
    subtitle: zh ? "统一查看项目进度、个人待办与自动报告，支持快速检索、筛选与切换。" : "Manage project progress, personal workload, and automated reports in one unified view with fast search and filters.",
    openWorkbench: zh ? "进入项目工作台" : "Open Workbench",
    openMyWork: zh ? "进入我的工作" : "Open My Work",
    openReports: zh ? "进入报告中心" : "Open Reports",
    projects: zh ? "可见项目" : "Visible Projects",
    myPending: zh ? "我的待办" : "My Pending",
    overdue: zh ? "超期任务" : "Overdue Tasks",
    risk: zh ? "高风险项目" : "High-Risk Projects",
    noData: zh ? "暂无可展示数据，请先创建项目或稍后刷新。" : "No data available yet. Create a project first or refresh later.",
    refresh: zh ? "刷新" : "Refresh",
  };
}

function ensureWorkMgmtHomeSection() {
  const home = document.getElementById("home");
  if (!home) return;
  const copy = workMgmtCopy();
  let section = home.querySelector("[data-workmgmt-home]");
  if (!section) {
    section = document.createElement("section");
    section.className = "section";
    section.setAttribute("data-workmgmt-home", "1");
    section.innerHTML = `
      <div class="section-head">
        <div>
          <div class="eyebrow">Work Management</div>
          <h2>${copy.title}</h2>
          <p>${copy.subtitle}</p>
        </div>
      </div>
      <div class="card">
        <div class="summary-grid" data-workmgmt-summary-grid>
          <div class="summary-item"><span>${copy.projects}</span><strong data-workmgmt-projects>--</strong></div>
          <div class="summary-item"><span>${copy.myPending}</span><strong data-workmgmt-pending>--</strong></div>
          <div class="summary-item"><span>${copy.overdue}</span><strong data-workmgmt-overdue>--</strong></div>
          <div class="summary-item"><span>${copy.risk}</span><strong data-workmgmt-risk>--</strong></div>
        </div>
        <div class="hero-actions" style="margin-top:14px;">
          <button class="btn btn-primary" type="button" data-open-workbench>${copy.openWorkbench}</button>
          <button class="btn btn-ghost" type="button" data-open-mywork>${copy.openMyWork}</button>
          <button class="btn btn-ghost" type="button" data-open-report-center>${copy.openReports}</button>
          <button class="btn btn-ghost" type="button" data-refresh-workmgmt>${copy.refresh}</button>
        </div>
        <div class="auth-note" style="margin-top:10px;" data-workmgmt-home-note></div>
      </div>
    `;
    const generalChatSection = home.querySelector(".section .chat-card")?.closest(".section");
    if (generalChatSection) {
      home.insertBefore(section, generalChatSection);
    } else {
      home.appendChild(section);
    }
  }
  if (!appState.workMgmt.homeMounted) {
    appState.workMgmt.homeMounted = true;
    section.querySelector("[data-open-workbench]")?.addEventListener("click", () => openWorkbenchCenter().catch(() => {}));
    section.querySelector("[data-open-mywork]")?.addEventListener("click", () => openMyWorkCenter().catch(() => {}));
    section.querySelector("[data-open-report-center]")?.addEventListener("click", () => openReportCenter().catch(() => {}));
    section.querySelector("[data-refresh-workmgmt]")?.addEventListener("click", () => loadWorkMgmtHomeData().catch(() => {}));
  }
}

function renderWorkMgmtHomeSummary(payload) {
  const section = document.querySelector("[data-workmgmt-home]");
  if (!section) return;
  const projects = Number(payload?.workbench?.count || 0);
  const pending = Number(payload?.myWork?.tasks_today?.length || 0) + Number(payload?.workbench?.quick_views?.my_pending_items || 0);
  const overdue = Number(payload?.workbench?.quick_views?.overdue_tasks || 0);
  const risk = Number(payload?.workbench?.quick_views?.high_risk_projects || 0);
  const note = section.querySelector("[data-workmgmt-home-note]");
  section.querySelector("[data-workmgmt-projects]").textContent = String(projects);
  section.querySelector("[data-workmgmt-pending]").textContent = String(pending);
  section.querySelector("[data-workmgmt-overdue]").textContent = String(overdue);
  section.querySelector("[data-workmgmt-risk]").textContent = String(risk);
  if (note) {
    note.textContent = projects
      ? (lang() === "zh" ? `已接入多项目中心，当前可见 ${projects} 个项目。` : `${projects} projects are currently visible in the work management center.`)
      : workMgmtCopy().noData;
  }
  renderPlatformCommandStrip();
}

async function loadWorkMgmtHomeData() {
  if (!appState.auth.authenticated) return;
  ensureWorkMgmtHomeSection();
  try {
    const [workbench, myWork] = await Promise.all([
      loadV2Workbench("scope=my"),
      loadV2MyWork(),
    ]);
    renderWorkMgmtHomeSummary({ workbench, myWork });
  } catch (error) {
    const note = document.querySelector("[data-workmgmt-home-note]");
    if (note) note.textContent = authErrorMessage(error.message);
  }
}

function renderWorkbenchProjectRows(projects) {
  const rows = Array.isArray(projects) ? projects : [];
  if (!rows.length) return `<div class="auth-note">${workMgmtCopy().noData}</div>`;
  return `
    <div class="admin-user-list admin-user-list-compact">
      ${rows.map((project) => `
        <div class="admin-user-card">
          <div class="admin-user-card__head">
            <div>
              <strong>${escapeHtml(project.name || project.id)}</strong>
              <div class="admin-user-card__meta">${escapeHtml(project.id || "")} · ${escapeHtml(unifiedStatusLabel(project.status || "--"))}</div>
            </div>
            <span class="tag">${escapeHtml(project.role_in_project || "member")}</span>
          </div>
          <div class="admin-user-card__grid">
            <div><span>${lang() === "zh" ? "未完成任务" : "Unfinished"}</span><strong>${escapeHtml(String(project.unfinished_task_count || 0))}</strong></div>
            <div><span>${lang() === "zh" ? "待审批" : "Pending Approval"}</span><strong>${escapeHtml(String(project.pending_approval_count || 0))}</strong></div>
            <div><span>${lang() === "zh" ? "问题/阻塞" : "Issues/Blockers"}</span><strong>${escapeHtml(String(project.issue_blocker_count || 0))}</strong></div>
            <div><span>${lang() === "zh" ? "最近更新" : "Updated"}</span><strong>${escapeHtml(formatDateTime(project.last_updated || project.updated_at))}</strong></div>
            <div class="admin-user-card__wide"><span>${lang() === "zh" ? "最新进展" : "Latest Progress"}</span><strong>${escapeHtml(project.latest_progress || "--")}</strong></div>
          </div>
          <div class="work-chat-actions" style="margin-top:10px;">
            <button class="btn btn-ghost" type="button" data-open-project-chat-summary="${escapeHtml(project.id || "")}">
              ${lang() === "zh" ? "Chat 摘要中心" : "Chat Summary Center"}
            </button>
          </div>
        </div>
      `).join("")}
    </div>
  `;
}

function bindProjectChatSummaryButtons(host = document) {
  host.querySelectorAll("[data-open-project-chat-summary]").forEach((button) => {
    if (button.dataset.boundProjectChatSummary === "1") return;
    button.dataset.boundProjectChatSummary = "1";
    button.addEventListener("click", () => {
      const projectId = String(button.getAttribute("data-open-project-chat-summary") || "").trim();
      if (!projectId) return;
      openProjectChatSummaryCenter(projectId).catch(() => {});
    });
  });
}

function renderProjectChatSummarySections(summary) {
  if (!summary) {
    return `<div class="auth-note">${lang() === "zh" ? "当前还没有摘要，建议先手动生成一次。" : "No summary yet. Generate one to initialize project context."}</div>`;
  }
  const section = (title, items) => `
    <div class="admin-user-card" style="margin-top:10px;">
      <div class="admin-user-card__head"><strong>${escapeHtml(title)}</strong></div>
      <div class="auth-note">${(items || []).length ? (items || []).map((item) => `• ${escapeHtml(String(item || ""))}`).join("<br>") : "--"}</div>
    </div>
  `;
  return `
    <div class="admin-user-card">
      <div class="admin-user-card__head">
        <strong>${lang() === "zh" ? "当前项目摘要" : "Current Project Summary"}</strong>
        <span class="tag">${escapeHtml(summary.summary_type || "manual")} · v${escapeHtml(String(summary.summary_version || 1))}</span>
      </div>
      <div class="admin-user-card__meta">${escapeHtml(formatDateTime(summary.generated_at))} · ${lang() === "zh" ? "来源消息" : "Source messages"} ${escapeHtml(String(summary.source_message_count || 0))}</div>
      <div class="auth-note">${escapeHtml(summary.summary_content_text || "--")}</div>
    </div>
    ${section(lang() === "zh" ? "主要进展" : "Main Progress", summary.main_progress)}
    ${section(lang() === "zh" ? "确认决策" : "Confirmed Decisions", summary.confirmed_decisions)}
    ${section(lang() === "zh" ? "任务/责任更新" : "Task & Ownership Updates", summary.task_ownership_updates)}
    ${section(lang() === "zh" ? "文件/流程更新" : "File / Workflow Updates", summary.file_document_updates)}
    ${section(lang() === "zh" ? "问题/风险/阻塞" : "Issues / Risks / Blockers", summary.issues_risks_blockers)}
    ${section(lang() === "zh" ? "下一步动作" : "Next Actions", summary.next_actions)}
  `;
}

function renderProjectChatMessageRows(payload) {
  const messages = Array.isArray(payload?.messages) ? payload.messages : [];
  if (!messages.length) return `<div class="auth-note">${lang() === "zh" ? "没有可显示消息。" : "No messages in this view."}</div>`;
  return messages.map((msg) => `
    <div class="work-chat-message ${msg.is_key_message ? "mine" : ""}">
      <span>${escapeHtml(msg.sender_name || msg.sender_id || "System")} · ${escapeHtml(formatDateTime(msg.created_at))} · ${escapeHtml(msg.lifecycle_status || "active")}</span>
      <p>${escapeHtml(msg.content || "")}</p>
      <div class="work-chat-actions" style="margin-top:6px;">
        <button class="btn btn-ghost" type="button" data-project-chat-mark-key="${escapeHtml(msg.id)}">${msg.is_key_message ? (lang() === "zh" ? "取消关键" : "Unmark Key") : (lang() === "zh" ? "标记关键" : "Mark Key")}</button>
      </div>
    </div>
  `).join("");
}

async function openProjectChatSummaryCenter(projectId) {
  const title = lang() === "zh" ? `项目聊天摘要 · ${projectId}` : `Project Chat Summary · ${projectId}`;
  let current;
  let history;
  let defaultMessages;
  let keyMessages;
  let policy;
  let cleanupLogs;
  try {
    [current, history, defaultMessages, keyMessages, policy, cleanupLogs] = await Promise.all([
      loadV2ProjectChatSummaryCurrent(projectId),
      loadV2ProjectChatSummaryHistory(projectId, 20),
      loadV2ProjectChatMessages(projectId, "default", 100),
      loadV2ProjectChatMessages(projectId, "key", 80),
      loadV2ProjectChatPolicy(projectId),
      loadV2ProjectChatCleanupLogs(projectId, 40),
    ]);
  } catch (error) {
    ensureOverlayPanel(title, `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`);
    return;
  }
  const summary = current?.summary || null;
  const panel = ensureOverlayPanel(title, `
    <div class="admin-panel">
      <div class="admin-hero admin-hero--team">
        <div class="admin-hero__brand">
          <div class="admin-hero__logo" aria-hidden="true"></div>
          <div class="admin-hero__copy">
            <strong>${escapeHtml(current?.project?.name || projectId)}</strong>
            <p>${lang() === "zh" ? "Summary-first：先看摘要，再看关键消息和最近消息。" : "Summary-first: summary first, then key/recent messages."}</p>
          </div>
        </div>
        <div class="admin-hero__stats">
          <div class="admin-hero__stat"><span>${lang() === "zh" ? "活跃消息" : "Active Messages"}</span><strong>${escapeHtml(String(current?.message_counts?.active || 0))}</strong></div>
          <div class="admin-hero__stat"><span>${lang() === "zh" ? "归档消息" : "Archived Messages"}</span><strong>${escapeHtml(String(current?.message_counts?.archived || 0))}</strong></div>
          <div class="admin-hero__stat"><span>${lang() === "zh" ? "关键消息" : "Key Messages"}</span><strong>${escapeHtml(String(current?.message_counts?.key_messages || 0))}</strong></div>
        </div>
      </div>
      <div class="work-chat-actions" style="margin:10px 0;">
        <button class="btn btn-primary" type="button" data-project-chat-generate>${lang() === "zh" ? "生成摘要" : "Generate Summary"}</button>
        ${summary ? `<button class="btn btn-ghost" type="button" data-project-chat-regenerate="${escapeHtml(summary.id)}">${lang() === "zh" ? "重生成" : "Regenerate"}</button>` : ""}
        <button class="btn btn-ghost" type="button" data-project-chat-cleanup>${lang() === "zh" ? "执行清理" : "Run Cleanup"}</button>
      </div>
      <div class="auth-note">${lang() === "zh" ? `策略：归档 ${policy?.retention_policy?.archive_after_days ?? "--"} 天 / 软删 ${policy?.retention_policy?.soft_delete_after_days ?? "--"} 天 / 硬删 ${policy?.retention_policy?.hard_delete_after_days ?? "--"} 天` : `Policy: archive ${policy?.retention_policy?.archive_after_days ?? "--"}d / soft-delete ${policy?.retention_policy?.soft_delete_after_days ?? "--"}d / hard-delete ${policy?.retention_policy?.hard_delete_after_days ?? "--"}d`}</div>
      <div class="auth-note">${current?.state?.is_stale ? (lang() === "zh" ? "状态：摘要已过期，建议立即重新生成。" : "State: summary is stale, regenerate recommended.") : (lang() === "zh" ? "状态：摘要为最新。" : "State: summary is up-to-date.")}</div>
      <div data-project-chat-summary-block>${renderProjectChatSummarySections(summary)}</div>
      <div class="doc-flow-page card" style="margin-top:12px;">
        <aside class="doc-flow-sidebar">
          <div class="side-title">${lang() === "zh" ? "摘要历史" : "Summary History"}</div>
          <div class="work-chat-list">
            ${(history?.summaries || []).map((item) => `
              <button class="work-chat-item" type="button" data-project-chat-history-id="${escapeHtml(item.id)}">
                <strong>v${escapeHtml(String(item.summary_version || 1))} · ${escapeHtml(item.summary_type || "manual")}</strong>
                <span>${escapeHtml(formatDateTime(item.generated_at))}</span>
              </button>
            `).join("") || `<div class="auth-note">--</div>`}
          </div>
        </aside>
        <section class="doc-flow-main">
          <div class="admin-section-head"><span>${lang() === "zh" ? "关键消息" : "Key Messages"}</span></div>
          <div class="work-chat-messages" data-project-chat-key-list>${renderProjectChatMessageRows(keyMessages)}</div>
          <div class="admin-section-head" style="margin-top:10px;"><span>${lang() === "zh" ? "默认消息视图" : "Default Message View"}</span></div>
          <div class="work-chat-messages" data-project-chat-default-list>${renderProjectChatMessageRows(defaultMessages)}</div>
          <div class="admin-section-head" style="margin-top:10px;"><span>${lang() === "zh" ? "最近清理日志" : "Recent Cleanup Logs"}</span></div>
          <div class="auth-note">${(cleanupLogs?.cleanup_logs || []).slice(0, 8).map((item) => `${formatDateTime(item.executed_at)} · ${item.action_type} · ${item.affected_message_count}`).join("<br>") || "--"}</div>
          <div class="auth-feedback" data-project-chat-feedback></div>
        </section>
      </div>
    </div>
  `);
  const feedback = panel.querySelector("[data-project-chat-feedback]");

  panel.querySelector("[data-project-chat-generate]")?.addEventListener("click", async () => {
    try {
      if (feedback) feedback.textContent = lang() === "zh" ? "正在生成..." : "Generating...";
      await generateV2ProjectChatSummary(projectId, { trigger_type: "manual", provider_type: "hybrid", force: false });
      openProjectChatSummaryCenter(projectId);
    } catch (error) {
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    }
  });
  panel.querySelector("[data-project-chat-regenerate]")?.addEventListener("click", async (event) => {
    const summaryId = String(event.currentTarget?.getAttribute("data-project-chat-regenerate") || "").trim();
    if (!summaryId) return;
    try {
      if (feedback) feedback.textContent = lang() === "zh" ? "正在重生成..." : "Regenerating...";
      await regenerateV2ProjectChatSummary(projectId, summaryId, { provider_type: "hybrid" });
      openProjectChatSummaryCenter(projectId);
    } catch (error) {
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    }
  });
  panel.querySelector("[data-project-chat-cleanup]")?.addEventListener("click", async () => {
    try {
      if (feedback) feedback.textContent = lang() === "zh" ? "正在执行清理..." : "Running cleanup...";
      await cleanupV2ProjectChat(projectId, { mode: "all" });
      openProjectChatSummaryCenter(projectId);
    } catch (error) {
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    }
  });
  panel.querySelectorAll("[data-project-chat-mark-key]").forEach((node) => {
    node.addEventListener("click", async () => {
      const messageId = String(node.getAttribute("data-project-chat-mark-key") || "").trim();
      if (!messageId) return;
      const isUnmark = node.textContent?.toLowerCase().includes("unmark") || node.textContent?.includes("取消");
      try {
        await markV2ProjectChatMessageKey(projectId, messageId, !isUnmark);
        openProjectChatSummaryCenter(projectId);
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
  });
  panel.querySelectorAll("[data-project-chat-history-id]").forEach((node) => {
    node.addEventListener("click", async () => {
      const summaryId = String(node.getAttribute("data-project-chat-history-id") || "").trim();
      if (!summaryId) return;
      try {
        const detail = await fetchApiJson(`/api/v2/projects/${encodeURIComponent(projectId)}/chat-summary/${encodeURIComponent(summaryId)}`);
        const host = panel.querySelector("[data-project-chat-summary-block]");
        if (host) host.innerHTML = renderProjectChatSummarySections(detail.summary);
      } catch (error) {
        if (feedback) feedback.textContent = authErrorMessage(error.message);
      }
    });
  });
}

async function openWorkbenchCenter() {
  const copy = workMgmtCopy();
  let payload;
  try {
    payload = await loadV2Workbench("scope=my");
  } catch (error) {
    ensureOverlayPanel(copy.openWorkbench, `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`);
    return;
  }
  const panel = ensureOverlayPanel(copy.openWorkbench, `
    <div class="admin-panel">
      <div class="admin-hero admin-hero--team">
        <div class="admin-hero__brand">
          <div class="admin-hero__logo" aria-hidden="true"></div>
          <div class="admin-hero__copy">
            <span>${lang() === "zh" ? "Project Operations" : "Project Operations"}</span>
            <strong>${copy.openWorkbench}</strong>
          </div>
        </div>
      </div>
      <label class="auth-field admin-search-field">
        <span>${lang() === "zh" ? "项目检索" : "Project Search"}</span>
        <input type="text" data-workbench-search placeholder="${escapeHtml(lang() === "zh" ? "输入项目名、状态、负责人" : "Search by name, status, owner")}" />
      </label>
      <div class="summary-grid" style="margin-bottom:12px;">
        <div class="summary-item"><span>${copy.myPending}</span><strong>${escapeHtml(String(payload.quick_views?.my_pending_items || 0))}</strong></div>
        <div class="summary-item"><span>${lang() === "zh" ? "待审批" : "Pending Approvals"}</span><strong>${escapeHtml(String(payload.quick_views?.pending_approvals || 0))}</strong></div>
        <div class="summary-item"><span>${copy.overdue}</span><strong>${escapeHtml(String(payload.quick_views?.overdue_tasks || 0))}</strong></div>
        <div class="summary-item"><span>${copy.risk}</span><strong>${escapeHtml(String(payload.quick_views?.high_risk_projects || 0))}</strong></div>
      </div>
      <div data-workbench-results>${renderWorkbenchProjectRows(payload.projects)}</div>
      <label class="auth-field admin-search-field" style="margin-top:12px;">
        <span>${lang() === "zh" ? "全局搜索（项目/任务/文档）" : "Global Search (Project/Task/Document)"}</span>
        <input type="text" data-global-search placeholder="${escapeHtml(lang() === "zh" ? "输入关键字后回车" : "Type keyword and press Enter")}" />
      </label>
      <div class="auth-note" data-global-search-results></div>
    </div>
  `);
  const searchInput = panel.querySelector("[data-workbench-search]");
  const results = panel.querySelector("[data-workbench-results]");
  const globalInput = panel.querySelector("[data-global-search]");
  const globalResults = panel.querySelector("[data-global-search-results]");
  let timer = null;
  searchInput?.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(async () => {
      try {
        const q = String(searchInput.value || "").trim();
        const next = await loadV2Workbench(`scope=my${q ? `&q=${encodeURIComponent(q)}` : ""}`);
        if (results) {
          results.innerHTML = renderWorkbenchProjectRows(next.projects);
          bindProjectChatSummaryButtons(results);
        }
      } catch (error) {
        if (results) results.innerHTML = `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`;
      }
    }, 180);
  });
  globalInput?.addEventListener("keydown", async (event) => {
    if (event.key !== "Enter") return;
    event.preventDefault();
    try {
      const q = String(globalInput.value || "").trim();
      const found = await loadV2GlobalSearch(q);
      if (globalResults) {
        globalResults.innerHTML = `${lang() === "zh" ? "项目" : "Projects"}: ${found.projects.length} · ${lang() === "zh" ? "任务" : "Tasks"}: ${found.work_items.length} · ${lang() === "zh" ? "文档" : "Documents"}: ${found.documents.length}`;
      }
    } catch (error) {
      if (globalResults) globalResults.textContent = authErrorMessage(error.message);
    }
  });
  bindProjectChatSummaryButtons(panel);
}

function renderMyWorkCards(payload) {
  const tasks = Array.isArray(payload?.tasks_today) ? payload.tasks_today : [];
  const pendingDocs = Array.isArray(payload?.pending_documents) ? payload.pending_documents : [];
  const reports = Array.isArray(payload?.my_reports) ? payload.my_reports : [];
  return `
    <div class="summary-grid">
      <div class="summary-item"><span>${lang() === "zh" ? "今日任务" : "Tasks Today"}</span><strong>${escapeHtml(String(tasks.length))}</strong></div>
      <div class="summary-item"><span>${lang() === "zh" ? "待处理文档" : "Pending Docs"}</span><strong>${escapeHtml(String(pendingDocs.length))}</strong></div>
      <div class="summary-item"><span>${lang() === "zh" ? "我的报告" : "My Reports"}</span><strong>${escapeHtml(String(reports.length))}</strong></div>
      <div class="summary-item"><span>${lang() === "zh" ? "我的项目" : "My Projects"}</span><strong>${escapeHtml(String((payload?.projects || []).length))}</strong></div>
    </div>
    <div class="admin-user-list admin-user-list-compact" style="margin-top:12px;">
      ${(tasks.slice(0, 8)).map((item) => `
        <div class="admin-user-card">
          <div class="admin-user-card__head">
            <strong>${escapeHtml(item.title || item.id)}</strong>
            <span class="tag status-tag">${escapeHtml(unifiedStatusLabel(item.status || "--"))}</span>
          </div>
          <div class="admin-user-card__meta">${escapeHtml(item.project_id || "")} · ${escapeHtml(item.priority || "medium")}</div>
        </div>
      `).join("") || `<div class="auth-note">${lang() === "zh" ? "今日暂无任务更新。" : "No task updates for today."}</div>`}
    </div>
  `;
}

async function openMyWorkCenter() {
  try {
    const payload = await loadV2MyWork();
    ensureOverlayPanel(lang() === "zh" ? "My Work 我的工作" : "My Work", `
      <div class="admin-panel">
        <div class="admin-hero admin-hero--team">
          <div class="admin-hero__brand">
            <div class="admin-hero__logo" aria-hidden="true"></div>
            <div class="admin-hero__copy">
              <strong>${lang() === "zh" ? "My Work 我的工作" : "My Work"}</strong>
            </div>
          </div>
        </div>
        ${renderMyWorkCards(payload)}
      </div>
    `);
  } catch (error) {
    ensureOverlayPanel(lang() === "zh" ? "My Work 我的工作" : "My Work", `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`);
  }
}

function renderReportRows(reports) {
  const rows = Array.isArray(reports) ? reports : [];
  if (!rows.length) return `<div class="auth-note">${lang() === "zh" ? "暂无报告。" : "No reports found."}</div>`;
  return rows.slice(0, 100).map((item) => `
    <button class="work-chat-item" type="button" data-report-id="${escapeHtml(item.id)}">
      <strong>${escapeHtml(item.report_type)}</strong>
      <span>${escapeHtml(item.project_id || item.user_id || "--")} · ${escapeHtml(unifiedStatusLabel(item.status || "generated"))}</span>
      <small>${escapeHtml(item.period_start || "--")} ~ ${escapeHtml(item.period_end || "--")}</small>
    </button>
  `).join("");
}

function renderReportDetailCard(report) {
  if (!report) return `<div class="auth-note">${lang() === "zh" ? "请选择左侧报告查看详情。" : "Select a report from the left list."}</div>`;
  const comments = Array.isArray(report.comments) ? report.comments : [];
  return `
    <div class="admin-user-card">
      <div class="admin-user-card__head">
        <strong>${escapeHtml(report.report_type || report.id)}</strong>
        <span class="tag status-tag">${escapeHtml(unifiedStatusLabel(report.status || "generated"))}</span>
      </div>
      <div class="admin-user-card__meta">${escapeHtml(report.period_start || "--")} ~ ${escapeHtml(report.period_end || "--")} · ${escapeHtml(formatDateTime(report.generated_at))}</div>
      <pre style="white-space:pre-wrap;word-break:break-word;margin-top:10px;">${escapeHtml(JSON.stringify(report.content || {}, null, 2))}</pre>
      <div class="admin-section-head"><span>${lang() === "zh" ? "评论 / 指令" : "Comments / Instructions"}</span></div>
      <div>${comments.map((item) => `<div class="auth-note"><strong>${escapeHtml(item.commented_by_name || item.commented_by)}</strong>: ${escapeHtml(item.comment || "")}</div>`).join("") || `<div class="auth-note">${lang() === "zh" ? "暂无评论。" : "No comments yet."}</div>`}</div>
    </div>
  `;
}

async function openReportCenter() {
  const title = lang() === "zh" ? "Report Center 报告中心" : "Report Center";
  let payload;
  try {
    payload = await loadV2Reports();
  } catch (error) {
    ensureOverlayPanel(title, `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`);
    return;
  }
  const isAdmin = !!appState.auth.user && appState.auth.user.role === "admin";
  const panel = ensureOverlayPanel(title, `
    <div class="admin-panel">
      <div class="admin-hero admin-hero--team">
        <div class="admin-hero__brand">
          <div class="admin-hero__logo" aria-hidden="true"></div>
          <div class="admin-hero__copy"><strong>${title}</strong></div>
        </div>
      </div>
      <div class="work-chat-actions" style="margin-bottom:12px;">
        <button class="btn btn-ghost" type="button" data-report-refresh>${lang() === "zh" ? "刷新" : "Refresh"}</button>
        ${isAdmin ? `<button class="btn btn-primary" type="button" data-report-gen-daily>${lang() === "zh" ? "生成日报" : "Generate Daily"}</button>` : ""}
        ${isAdmin ? `<button class="btn btn-ghost" type="button" data-report-gen-weekly>${lang() === "zh" ? "生成周报" : "Generate Weekly"}</button>` : ""}
      </div>
      <label class="auth-field admin-search-field">
        <span>${lang() === "zh" ? "筛选类型" : "Type Filter"}</span>
        <select data-report-type-filter>
          <option value="">all</option>
          <option value="admin_daily_summary">admin_daily_summary</option>
          <option value="user_daily">user_daily</option>
          <option value="user_weekly">user_weekly</option>
          <option value="project_daily">project_daily</option>
          <option value="project_weekly">project_weekly</option>
        </select>
      </label>
      <div class="doc-flow-page card" style="margin-top:10px;">
        <aside class="doc-flow-sidebar">
          <div class="side-title">${lang() === "zh" ? "报告列表" : "Reports"}</div>
          <div class="work-chat-list" data-report-list>${renderReportRows(payload.reports)}</div>
        </aside>
        <section class="doc-flow-main">
          <div data-report-detail>${renderReportDetailCard(null)}</div>
          <form class="doc-flow-create-form" data-report-comment-form style="margin-top:12px;">
            <label class="auth-field">
              <span>${lang() === "zh" ? "添加评论/指令" : "Add Comment/Instruction"}</span>
              <textarea name="comment"></textarea>
            </label>
            <label class="auth-field">
              <span>${lang() === "zh" ? "状态" : "Status"}</span>
              <select name="status">
                <option value="generated">generated</option>
                <option value="reviewed">reviewed</option>
                <option value="follow_up_needed">follow_up_needed</option>
                <option value="resolved">resolved</option>
              </select>
            </label>
            <div class="work-chat-actions">
              <button class="btn btn-primary" type="submit">${lang() === "zh" ? "提交评论并更新状态" : "Save Comment & Status"}</button>
            </div>
            <div class="auth-feedback" data-report-comment-feedback></div>
          </form>
        </section>
      </div>
    </div>
  `);
  let selectedReportId = "";
  const listNode = panel.querySelector("[data-report-list]");
  const detailNode = panel.querySelector("[data-report-detail]");
  const feedbackNode = panel.querySelector("[data-report-comment-feedback]");
  const formNode = panel.querySelector("[data-report-comment-form]");
  const typeFilter = panel.querySelector("[data-report-type-filter]");

  async function refreshList() {
    try {
      const type = String(typeFilter?.value || "").trim();
      const next = await loadV2Reports(type ? `report_type=${encodeURIComponent(type)}` : "");
      if (listNode) listNode.innerHTML = renderReportRows(next.reports);
      bindReportRows();
    } catch (error) {
      if (listNode) listNode.innerHTML = `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`;
    }
  }

  async function bindReportRows() {
    panel.querySelectorAll("[data-report-id]").forEach((node) => {
      node.addEventListener("click", async () => {
        const reportId = node.getAttribute("data-report-id") || "";
        selectedReportId = reportId;
        try {
          const detail = await loadV2ReportDetail(reportId);
          if (detailNode) detailNode.innerHTML = renderReportDetailCard(detail.report);
          if (formNode) {
            formNode.querySelector("select[name='status']").value = detail.report?.status || "generated";
          }
        } catch (error) {
          if (detailNode) detailNode.innerHTML = `<div class="auth-feedback">${escapeHtml(authErrorMessage(error.message))}</div>`;
        }
      });
    });
  }

  await bindReportRows();
  typeFilter?.addEventListener("change", refreshList);
  panel.querySelector("[data-report-refresh]")?.addEventListener("click", refreshList);
  panel.querySelector("[data-report-gen-daily]")?.addEventListener("click", async () => {
    try {
      await triggerV2ReportGenerate("daily", true);
      await refreshList();
    } catch (error) {
      if (feedbackNode) feedbackNode.textContent = authErrorMessage(error.message);
    }
  });
  panel.querySelector("[data-report-gen-weekly]")?.addEventListener("click", async () => {
    try {
      await triggerV2ReportGenerate("weekly", true);
      await refreshList();
    } catch (error) {
      if (feedbackNode) feedbackNode.textContent = authErrorMessage(error.message);
    }
  });
  formNode?.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!selectedReportId) {
      if (feedbackNode) feedbackNode.textContent = lang() === "zh" ? "请先选择一条报告。" : "Please select a report first.";
      return;
    }
    const formData = new FormData(formNode);
    try {
      const comment = String(formData.get("comment") || "").trim();
      const status = String(formData.get("status") || "generated").trim();
      if (comment) await addV2ReportComment(selectedReportId, comment);
      await updateV2ReportStatus(selectedReportId, status);
      const detail = await loadV2ReportDetail(selectedReportId);
      if (detailNode) detailNode.innerHTML = renderReportDetailCard(detail.report);
      if (feedbackNode) feedbackNode.textContent = lang() === "zh" ? "已保存。" : "Saved.";
      formNode.querySelector("textarea[name='comment']").value = "";
    } catch (error) {
      if (feedbackNode) feedbackNode.textContent = authErrorMessage(error.message);
    }
  });
}

function workChatUserOptions(selected = []) {
  const picked = new Set((selected || []).map((item) => String(item).toLowerCase()));
  return (appState.workChat.users || []).map((user) => {
    const email = user.email || "";
    const label = `${user.display_name || user.username || email} (${email})`;
    return `<option value="${escapeHtml(email)}" ${picked.has(email.toLowerCase()) ? "selected" : ""}>${escapeHtml(label)}</option>`;
  }).join("");
}

function workChatDisplayName(conv) {
  const raw = String(conv?.name || conv?.id || "").trim();
  if (lang() !== "en") return raw;
  const exact = {
    "工作群聊天": "Work Chat",
    "工作群聊": "Work Group Chat",
    "群聊": "Group Chat",
    "私聊": "Direct Chat",
    "管理员全部会话": "Admin All Sessions",
  };
  if (exact[raw]) return exact[raw];
  return raw
    .replaceAll("工作群聊天", "Work Chat")
    .replaceAll("工作群聊", "Work Group Chat")
    .replaceAll("群聊", "Group Chat")
    .replaceAll("私聊", "Direct Chat")
    .replaceAll("管理员全部会话", "Admin All Sessions");
}

function humanFileSize(bytes) {
  const value = Number(bytes || 0);
  if (!Number.isFinite(value) || value <= 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let idx = 0;
  let size = value;
  while (size >= 1024 && idx < units.length - 1) {
    size /= 1024;
    idx += 1;
  }
  return `${size >= 10 || idx === 0 ? Math.round(size) : size.toFixed(1)} ${units[idx]}`;
}

function workChatFileTargetOptions(files = []) {
  const baseLabel = lang() === "zh" ? "作为新文件上传" : "Upload as new file";
  const list = files.map((file) => {
    const ver = Number(file.current_version_number || 0);
    const size = humanFileSize(file.size || 0);
    const label = `${file.title || file.filename || file.id} · v${ver} · ${size}`;
    return `<option value="${escapeHtml(file.id)}">${escapeHtml(label)}</option>`;
  }).join("");
  return `<option value="">${escapeHtml(baseLabel)}</option>${list}`;
}

function renderWorkChatSharedFiles(files = []) {
  if (!files.length) {
    return `<div class="auth-note">${lang() === "zh" ? "当前会话还没有共享文件。" : "No shared files in this conversation yet."}</div>`;
  }
  return files.map((file) => {
    const latest = (file.versions || []).slice(-1)[0] || null;
    const versionLabel = `v${Number(file.current_version_number || 0)}`;
    const links = (file.versions || []).slice(-5).reverse().map((version) => {
      const vLabel = `v${Number(version.version_number || 0)}`;
      const dateLabel = formatDateTime(version.created_at);
      return `
        <a class="tag" href="${escapeHtml(version.download_url || "#")}" ${version.download_url ? "download" : ""}>
          ${escapeHtml(vLabel)} · ${escapeHtml(dateLabel)}
        </a>
      `;
    }).join("");
    return `
      <article class="work-chat-file-card">
        <div class="work-chat-file-head">
          <strong>${escapeHtml(file.title || file.filename || file.id)}</strong>
          <span>${escapeHtml(versionLabel)} · ${escapeHtml(humanFileSize(file.size || 0))}</span>
        </div>
        <div class="work-chat-file-meta">
          <span>${escapeHtml(file.filename || "")}</span>
          ${latest?.download_url ? `<a class="btn btn-ghost" href="${escapeHtml(latest.download_url)}" download>${lang() === "zh" ? "下载最新" : "Download Latest"}</a>` : ""}
        </div>
        <div class="tag-row">${links || `<span class="tag">${lang() === "zh" ? "暂无版本历史" : "No version history"}</span>`}</div>
      </article>
    `;
  }).join("");
}

function renderWorkChatAttachments(attachments = []) {
  if (!attachments.length) return "";
  const cards = attachments.map((item) => `
    <a class="work-chat-attachment" href="${escapeHtml(item.download_url || "#")}" ${item.download_url ? "download" : ""}>
      <strong>${escapeHtml(item.filename || "file")}</strong>
      <span>v${escapeHtml(String(item.version_number || 1))} · ${escapeHtml(humanFileSize(item.size || 0))}</span>
    </a>
  `).join("");
  return `<div class="work-chat-attachments">${cards}</div>`;
}

async function loadWorkChatUsers() {
  const resp = await fetch("/api/work-chat/users");
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
  appState.workChat.users = payload.users || [];
  return appState.workChat.users;
}

async function loadWorkChat() {
  ensureWorkChatShell();
  if (!(appState.workChat.users || []).length) await loadWorkChatUsers();
  const resp = await fetch("/api/work-chat/conversations");
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
  appState.workChat.conversations = payload.conversations || [];
  const badge = document.querySelector("[data-work-chat-admin-badge]");
  if (badge) badge.hidden = !payload.admin_view;
  if (!appState.workChat.selectedId && appState.workChat.conversations[0]) {
    appState.workChat.selectedId = appState.workChat.conversations[0].id;
  }
  renderWorkChatList();
  if (appState.workChat.selectedId) await selectWorkChat(appState.workChat.selectedId);
  bindWorkChatControls();
}

function renderWorkChatList() {
  const list = document.querySelector("[data-work-chat-list]");
  if (!list) return;
  const conversations = appState.workChat.conversations || [];
  list.innerHTML = conversations.length ? conversations.map((conv) => {
    const viewer = conv.viewer || {};
    const status = conv.status || {};
    const labels = [
      conv.type === "direct" ? (lang() === "zh" ? "私聊" : "Direct") : (lang() === "zh" ? "群聊" : "Group"),
      viewer.is_granted ? (lang() === "zh" ? "授权查看" : "Granted") : "",
      conv.created_by === appState.auth.user?.email ? (lang() === "zh" ? "我创建" : "Owner") : "",
    ].filter(Boolean);
    return `
      <button class="work-chat-item ${conv.id === appState.workChat.selectedId ? "active" : ""}" type="button" data-chat-id="${escapeHtml(conv.id)}">
        <div class="work-chat-item__head">
          <span class="work-chat-avatar" aria-hidden="true"></span>
          <div>
            <strong>${escapeHtml(workChatDisplayName(conv))}</strong>
            <span>${labels.map(escapeHtml).join(" · ")}</span>
            <small>${lang() === "zh" ? "在线" : "Online"} ${status.online_member_count || 0} · ${status.has_unread ? (lang() === "zh" ? "未读" : "Unread") : (lang() === "zh" ? "已读" : "Read")}</small>
          </div>
        </div>
      </button>
    `;
  }).join("") : `<div class="auth-note">${lang() === "zh" ? "暂无可见会话。" : "No visible conversations yet."}</div>`;
  list.querySelectorAll("[data-chat-id]").forEach((button) => {
    button.addEventListener("click", () => selectWorkChat(button.dataset.chatId || ""));
  });
}

async function selectWorkChat(conversationId, dateFilter = "") {
  if (!conversationId) return;
  appState.workChat.selectedId = conversationId;
  appState.workChat.messageDateFilter = dateFilter || "";
  renderWorkChatList();
  const query = dateFilter ? `?date=${encodeURIComponent(dateFilter)}` : "";
  const [detailResp, messagesResp] = await Promise.all([
    fetch(`/api/work-chat/conversations/${encodeURIComponent(conversationId)}`),
    fetch(`/api/work-chat/conversations/${encodeURIComponent(conversationId)}/messages${query}`),
  ]);
  const detailPayload = await detailResp.json();
  const messagesPayload = await messagesResp.json();
  if (!detailResp.ok || !detailPayload.ok) throw new Error(detailPayload.error || "request_failed");
  if (!messagesResp.ok || !messagesPayload.ok) throw new Error(messagesPayload.error || "request_failed");
  appState.workChat.messages = messagesPayload.messages || [];
  appState.workChat.messageMeta = messagesPayload || {};
  renderWorkChatDetail(detailPayload.conversation);
  renderWorkChatMessages(detailPayload.conversation);
}

function renderWorkChatDetail(conv) {
  const detail = document.querySelector("[data-work-chat-detail]");
  if (!detail || !conv) return;
  const viewer = conv.viewer || {};
  const status = conv.status || {};
  const isAdmin = !!appState.auth.user && appState.auth.user.role === "admin";
  const meta = appState.workChat.messageMeta || {};
  const dateFilter = appState.workChat.messageDateFilter || "";
  const sharedFiles = conv.shared_files || [];
  const lastMessageLabel = status.last_message_at
    ? formatDateTime(status.last_message_at)
    : (lang() === "zh" ? "暂无消息" : "No messages yet");
  const accessLabel = viewer.can_send
    ? (lang() === "zh" ? "成员可发送" : "Member access")
    : (lang() === "zh" ? "只读查看" : "Read-only access");
  const visibilityLabel = viewer.is_granted
    ? (lang() === "zh" ? "管理员授权可见" : "Visible by admin grant")
    : (conv.type === "direct" ? (lang() === "zh" ? "双人私聊隔离" : "Private direct channel") : (lang() === "zh" ? "群聊成员可见" : "Visible to group members"));
  const typingLabel = status.is_typing
    ? (lang() === "zh" ? "有人正在输入" : "Someone is typing")
    : (lang() === "zh" ? "当前无输入" : "No one typing");
  detail.innerHTML = `
    <div class="work-chat-title-row">
      <div class="work-chat-title-main">
        <div class="work-chat-title-logo">
          <img src="${themedFastoneLogo("full")}" alt="FASTONE" class="work-chat-title-logo-img" />
        </div>
        <div class="work-chat-title-copy">
          <span class="platform-kicker">${lang() === "zh" ? "FASTONE SECURE CHAT" : "FASTONE SECURE CHAT"}</span>
          <h2>${escapeHtml(workChatDisplayName(conv))}</h2>
          <p>${escapeHtml(conv.type === "direct" ? (lang() === "zh" ? "两人私聊" : "Direct chat") : (lang() === "zh" ? "工作群聊" : "Group chat"))}</p>
        </div>
      </div>
      <div class="mini-status">
        <span class="mini-pill">${lang() === "zh" ? "在线成员" : "Online"} ${status.online_member_count || 0}</span>
        <span class="mini-pill">${status.has_unread ? (lang() === "zh" ? "有未读" : "Unread") : (lang() === "zh" ? "无未读" : "No unread")}</span>
        <span class="mini-pill">${escapeHtml(lastMessageLabel)}</span>
      </div>
    </div>
    <div class="work-chat-runtime-strip">
      <div class="work-chat-runtime-card">
        <span>${lang() === "zh" ? "最近消息" : "Last Message"}</span>
        <strong>${escapeHtml(lastMessageLabel)}</strong>
      </div>
      <div class="work-chat-runtime-card">
        <span>${lang() === "zh" ? "会话权限" : "Access Mode"}</span>
        <strong>${escapeHtml(accessLabel)}</strong>
      </div>
      <div class="work-chat-runtime-card">
        <span>${lang() === "zh" ? "可见范围" : "Visibility"}</span>
        <strong>${escapeHtml(visibilityLabel)}</strong>
      </div>
      <div class="work-chat-runtime-card">
        <span>${lang() === "zh" ? "实时状态" : "Live State"}</span>
        <strong>${escapeHtml(typingLabel)}</strong>
      </div>
    </div>
    <div class="work-chat-members">
      ${(conv.members || []).map((member) => `<span class="tag">${escapeHtml(member.display_name || member.user_id)} · ${escapeHtml(member.role || "member")}</span>`).join("")}
    </div>
    <div class="work-chat-files">
      <div class="work-chat-files-head">
        <strong>${lang() === "zh" ? "会话共享文件" : "Shared Files"}</strong>
        <span>${lang() === "zh" ? "支持下载历史版本，也可在同一文件上继续更新版本。" : "Download history versions or keep updating the same shared file."}</span>
      </div>
      <div class="work-chat-files-list">${renderWorkChatSharedFiles(sharedFiles)}</div>
    </div>
    ${isAdmin ? `
      <div class="work-chat-admin-grants">
        <strong>${lang() === "zh" ? "授权查看" : "Access Grants"}</strong>
        <div class="work-chat-grant-row">
          <select data-chat-grant-user>${workChatUserOptions()}</select>
          <button class="btn btn-ghost" type="button" data-chat-grant-add>${lang() === "zh" ? "授权" : "Grant"}</button>
        </div>
        <div class="tag-row">
          ${(conv.access_grants || []).map((grant) => `
            <span class="tag">${escapeHtml(grant.display_name || grant.granted_user_id)}
              <button type="button" data-chat-grant-revoke="${escapeHtml(grant.granted_user_id)}">×</button>
            </span>
          `).join("") || `<span class="tag">${lang() === "zh" ? "暂无授权" : "No grants"}</span>`}
        </div>
      </div>
      <div class="work-chat-date-tools">
        <div>
          <strong>${lang() === "zh" ? "记录调取" : "Record Lookup"}</strong>
          <span>${lang() === "zh" ? `默认显示最近 ${meta.visible_days || 7} 天，本地保留 ${meta.retention_days || 15} 天。` : `Showing the latest ${meta.visible_days || 7} days by default. Local records are kept for ${meta.retention_days || 15} days.`}</span>
        </div>
        <input type="date" data-work-chat-date value="${escapeHtml(dateFilter)}">
        <button class="btn btn-ghost" type="button" data-work-chat-load-date>${lang() === "zh" ? "调取当天" : "Load Day"}</button>
        <button class="btn btn-ghost" type="button" data-work-chat-latest>${lang() === "zh" ? "最近记录" : "Latest"}</button>
      </div>
    ` : ""}
    <div class="work-chat-messages" data-work-chat-messages></div>
    <div class="work-chat-composer">
      <textarea data-work-chat-input ${viewer.can_send ? "" : "disabled"} placeholder="${viewer.can_send ? (lang() === "zh" ? "输入消息，Ctrl/Command + Enter 发送" : "Type a message. Ctrl/Command + Enter to send") : (lang() === "zh" ? "当前为只读查看，不能发送消息。" : "Read-only access. Sending is disabled.")}"></textarea>
      <button class="btn btn-primary" type="button" data-work-chat-send ${viewer.can_send ? "" : "disabled"}>${lang() === "zh" ? "发送" : "Send"}</button>
    </div>
    <div class="work-chat-file-tools">
      <select data-work-chat-file-target ${viewer.can_send ? "" : "disabled"}>
        ${workChatFileTargetOptions(sharedFiles)}
      </select>
      <input type="file" data-work-chat-file-input ${viewer.can_send ? "" : "disabled"}>
      <input type="text" data-work-chat-file-note ${viewer.can_send ? "" : "disabled"} placeholder="${lang() === "zh" ? "文件说明（可选）" : "File note (optional)"}">
      <button class="btn btn-ghost" type="button" data-work-chat-file-upload ${viewer.can_send ? "" : "disabled"}>${lang() === "zh" ? "上传/更新文件" : "Upload/Update File"}</button>
      <div class="auth-feedback" data-work-chat-file-feedback></div>
    </div>
  `;
  renderWorkChatMessages(conv);
  detail.querySelector("[data-work-chat-send]")?.addEventListener("click", () => sendWorkChatMessage(conv.id));
  detail.querySelector("[data-work-chat-input]")?.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") sendWorkChatMessage(conv.id);
  });
  detail.querySelector("[data-chat-grant-add]")?.addEventListener("click", async () => {
    const email = detail.querySelector("[data-chat-grant-user]")?.value || "";
    await updateWorkChatGrant(conv.id, email, true);
  });
  detail.querySelectorAll("[data-chat-grant-revoke]").forEach((button) => {
    button.addEventListener("click", async () => updateWorkChatGrant(conv.id, button.dataset.chatGrantRevoke || "", false));
  });
  detail.querySelector("[data-work-chat-load-date]")?.addEventListener("click", async () => {
    const selectedDate = detail.querySelector("[data-work-chat-date]")?.value || "";
    if (selectedDate) await selectWorkChat(conv.id, selectedDate);
  });
  detail.querySelector("[data-work-chat-latest]")?.addEventListener("click", async () => selectWorkChat(conv.id, ""));
  detail.querySelector("[data-work-chat-file-upload]")?.addEventListener("click", async () => uploadWorkChatFile(conv.id));
}

function renderWorkChatMessages(conv) {
  const box = document.querySelector("[data-work-chat-messages]");
  if (!box) return;
  const current = appState.auth.user?.email || "";
  const messages = appState.workChat.messages || [];
  const meta = appState.workChat.messageMeta || {};
  const collapseSeconds = Number(meta.collapse_seconds || 300);
  const cutoff = Math.floor(Date.now() / 1000) - collapseSeconds;
  const older = messages.filter((msg) => Number(msg.created_at || 0) < cutoff);
  const recent = messages.filter((msg) => Number(msg.created_at || 0) >= cutoff);
  const renderItem = (msg) => `
    <div class="work-chat-message ${msg.sender_id === current ? "mine" : ""}">
      <span>${escapeHtml(msg.sender_name || msg.sender_id)} · ${escapeHtml(formatDateTime(msg.created_at))}</span>
      <p>${escapeHtml(msg.content)}</p>
      ${renderWorkChatAttachments(msg.attachments || [])}
    </div>
  `;
  const dateNote = appState.workChat.messageDateFilter
    ? `<div class="work-chat-retention-note">${lang() === "zh" ? `正在查看 ${escapeHtml(appState.workChat.messageDateFilter)} 的记录。` : `Viewing records for ${escapeHtml(appState.workChat.messageDateFilter)}.`}</div>`
    : `<div class="work-chat-retention-note">${lang() === "zh" ? `显示最近 ${meta.visible_days || 7} 天；5 分钟前记录自动折叠。` : `Showing the latest ${meta.visible_days || 7} days. Messages older than 5 minutes are collapsed.`}</div>`;
  if (!messages.length) {
    box.innerHTML = `${dateNote}<div class="auth-note">${lang() === "zh" ? "暂无消息。" : "No messages yet."}</div>`;
  } else {
    const olderBlock = older.length ? `
      <details class="work-chat-older" ${recent.length ? "" : "open"}>
        <summary>${lang() === "zh" ? `较早记录（${older.length} 条）` : `Older records (${older.length})`}</summary>
        <div>${older.map(renderItem).join("")}</div>
      </details>
    ` : "";
    box.innerHTML = `${dateNote}${olderBlock}${recent.map(renderItem).join("")}`;
  }
  box.scrollTop = box.scrollHeight;
}

async function uploadWorkChatFile(conversationId) {
  const inputNode = document.querySelector("[data-work-chat-file-input]");
  const targetNode = document.querySelector("[data-work-chat-file-target]");
  const noteNode = document.querySelector("[data-work-chat-file-note]");
  const feedbackNode = document.querySelector("[data-work-chat-file-feedback]");
  const file = inputNode?.files?.[0];
  if (!file) {
    if (feedbackNode) feedbackNode.textContent = lang() === "zh" ? "请先选择一个文件。" : "Please choose a file first.";
    return;
  }
  try {
    if (feedbackNode) feedbackNode.textContent = lang() === "zh" ? "正在上传..." : "Uploading...";
    const base64 = await fileToBase64(file, (percent) => {
      if (feedbackNode) feedbackNode.textContent = `${lang() === "zh" ? "正在上传" : "Uploading"} ${percent}%`;
    });
    const payload = {
      filename: file.name,
      mime: file.type || "application/octet-stream",
      base64,
      shared_file_id: String(targetNode?.value || "").trim(),
      note: String(noteNode?.value || "").trim(),
    };
    const resp = await fetch(`/api/work-chat/conversations/${encodeURIComponent(conversationId)}/files`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await resp.json();
    if (!resp.ok || !body.ok) throw new Error(body.error || "request_failed");
    if (inputNode) inputNode.value = "";
    if (noteNode) noteNode.value = "";
    if (feedbackNode) feedbackNode.textContent = lang() === "zh" ? "文件已上传。" : "File uploaded.";
    await selectWorkChat(conversationId);
  } catch (error) {
    if (feedbackNode) feedbackNode.textContent = authErrorMessage(error.message);
  }
}

async function sendWorkChatMessage(conversationId) {
  const input = document.querySelector("[data-work-chat-input]");
  const content = String(input?.value || "").trim();
  if (!content) return;
  const resp = await fetch(`/api/work-chat/conversations/${encodeURIComponent(conversationId)}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) {
    window.alert(authErrorMessage(payload.error || "request_failed"));
    return;
  }
  input.value = "";
  await selectWorkChat(conversationId);
}

async function updateWorkChatGrant(conversationId, email, active) {
  if (!email) return;
  const resp = await fetch(`/api/work-chat/conversations/${encodeURIComponent(conversationId)}/grants`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ granted_user_id: email, active }),
  });
  const payload = await resp.json();
  if (!resp.ok || !payload.ok) {
    window.alert(authErrorMessage(payload.error || "request_failed"));
    return;
  }
  await selectWorkChat(conversationId);
  await loadWorkChat();
}

function bindWorkChatControls() {
  const refresh = document.querySelector("[data-chat-refresh]");
  if (refresh && !refresh.dataset.bound) {
    refresh.dataset.bound = "1";
    refresh.addEventListener("click", () => loadWorkChat());
  }
  document.querySelectorAll("[data-chat-create]").forEach((button) => {
    if (button.dataset.bound) return;
    button.dataset.bound = "1";
    button.addEventListener("click", () => openWorkChatCreate(button.dataset.chatCreate || "group"));
  });
}

async function openWorkChatCreate(type = "group") {
  if (!(appState.workChat.users || []).length) await loadWorkChatUsers();
  const isDirect = type === "direct";
  const title = isDirect ? (lang() === "zh" ? "发起私聊" : "New Direct Chat") : (lang() === "zh" ? "创建群聊" : "New Group Chat");
  const panel = ensureOverlayPanel(title, `
    <form class="work-chat-create-form">
      ${isDirect ? "" : `<label class="auth-field"><span>${lang() === "zh" ? "群聊名称" : "Group Name"}</span><input name="name" type="text" autocomplete="off" /></label>`}
      <label class="auth-field">
        <span>${isDirect ? (lang() === "zh" ? "选择 1 位用户" : "Select 1 user") : (lang() === "zh" ? "选择成员" : "Select members")}</span>
        <select name="members" multiple size="8">${workChatUserOptions()}</select>
      </label>
      <button class="btn btn-primary" type="submit">${lang() === "zh" ? "创建" : "Create"}</button>
      <div class="auth-feedback" data-chat-create-feedback></div>
    </form>
  `);
  panel.querySelector(".work-chat-create-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const selected = Array.from(form.querySelector("select[name='members']").selectedOptions).map((option) => option.value);
    try {
      const resp = await fetch("/api/work-chat/conversations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: isDirect ? "direct" : "group", name: String(new FormData(form).get("name") || ""), members: selected }),
      });
      const payload = await resp.json();
      if (!resp.ok || !payload.ok) throw new Error(payload.error || "request_failed");
      closeOverlayPanel();
      appState.workChat.selectedId = payload.conversation?.id || "";
      await loadWorkChat();
    } catch (error) {
      const feedback = panel.querySelector("[data-chat-create-feedback]");
      if (feedback) feedback.textContent = authErrorMessage(error.message);
    }
  });
}

function startWorkChatRefresh() {
  if (appState.workChat.refreshTimer) clearInterval(appState.workChat.refreshTimer);
  appState.workChat.refreshTimer = setInterval(() => {
    if (appState.currentPage === "work-chat" && appState.auth.authenticated) loadWorkChat().catch(() => {});
  }, 15000);
}

function startWorkMgmtRefresh() {
  if (appState.workMgmt.refreshTimer) clearInterval(appState.workMgmt.refreshTimer);
  appState.workMgmt.refreshTimer = setInterval(() => {
    if (!appState.auth.authenticated) return;
    if (appState.currentPage === "home") {
      loadWorkMgmtHomeData().catch(() => {});
      loadHermesFlagshipData({ showLoading: false, syncing: true }).catch(() => {});
    }
    if (appState.currentPage === "workbench") loadWorkbenchPage().catch(() => {});
    if (appState.currentPage === "my-work") loadMyWorkPage().catch(() => {});
    if (appState.currentPage === "reports") loadReportsPage().catch(() => {});
    if (appState.currentPage === "file-center") loadFileCenterPage().catch(() => {});
    if (appState.currentPage === "ai-agent") loadAiAgentHubPage().catch(() => {});
    if (appState.currentPage === "intel-center") loadIntelligenceCenterPage().catch(() => {});
  }, 30000);
}

async function sendAuthHeartbeat() {
  if (!appState.auth.authenticated) return;
  const now = Date.now();
  const idleTimeoutMs = Math.max(0, Number(appState.auth.idleTimeoutSeconds || 0) * 1000);
  if (idleTimeoutMs && appState.auth.lastActivityAt && (now - appState.auth.lastActivityAt) >= idleTimeoutMs) {
    await performLogout({ timedOut: true });
    return;
  }
  if (!appState.auth.lastActivityAt || appState.auth.lastActivityAt <= appState.auth.lastHeartbeatAt) return;
  const workspace = appState.currentPage === "legal"
    ? "legal"
    : appState.currentPage === "home"
      ? "home"
      : appState.currentPage === "workbench"
        ? "workbench"
        : appState.currentPage === "my-work"
          ? "my-work"
          : appState.currentPage === "reports"
          ? "reports"
        : appState.currentPage === "file-center"
              ? "file-center"
        : appState.currentPage === "ai-agent"
          ? "ai-agent"
        : appState.currentPage === "intel-center"
          ? "intel-center"
        : appState.currentPage === "work-chat"
          ? "work-chat"
          : appState.currentPage === "doc-flow"
            ? "doc-flow"
            : "finance";
  const skillId = currentWorkspaceSkillId(workspace);
  const route = appState.routeState[workspace] || {};
  try {
    const resp = await fetch("/api/auth/heartbeat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        page: appState.currentPage,
        workspace,
        skill_id: skillId,
        provider: route.provider || "",
        model: route.model || "",
      }),
    });
    if (resp.status === 401) {
      await performLogout({ timedOut: true });
      return;
    }
    if (resp.ok) appState.auth.lastHeartbeatAt = now;
  } catch {}
}

function startAuthHeartbeatRefresh() {
  if (appState.authHeartbeatTimer) clearInterval(appState.authHeartbeatTimer);
  if (appState.authIdleTimer) clearInterval(appState.authIdleTimer);
  appState.authHeartbeatTimer = setInterval(sendAuthHeartbeat, 15000);
  appState.authIdleTimer = setInterval(async () => {
    if (!appState.auth.authenticated) return;
    const idleTimeoutMs = Math.max(0, Number(appState.auth.idleTimeoutSeconds || 0) * 1000);
    if (!idleTimeoutMs || !appState.auth.lastActivityAt) return;
    updateAuthIdleWarning();
    if ((Date.now() - appState.auth.lastActivityAt) >= idleTimeoutMs) {
      await performLogout({ timedOut: true });
    }
  }, 1000);
  updateAuthIdleWarning();
  sendAuthHeartbeat();
}

function applyTheme(theme) {
  const nextTheme = theme === "light" ? "light" : "dark";
  document.documentElement.dataset.theme = nextTheme;
  document.body.dataset.theme = nextTheme;
  document.querySelectorAll("[data-theme-toggle-mode]").forEach((button) => {
    const mode = button.getAttribute("data-theme-toggle-mode");
    const active = mode === nextTheme;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  });
  try {
    localStorage.setItem(THEME_KEY, nextTheme);
  } catch {}
  applyFastoneBranding();
}

function bindThemeToggle() {
  let savedTheme = "";
  try {
    savedTheme = localStorage.getItem(THEME_KEY) || "";
  } catch {}
  if (!savedTheme) {
    try {
      savedTheme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    } catch {
      savedTheme = "dark";
    }
  }
  document.querySelectorAll("[data-theme-toggle-mode]").forEach((button) => {
    if (button.dataset.boundThemeToggle === "1") return;
    button.dataset.boundThemeToggle = "1";
    button.addEventListener("click", () => {
      const mode = button.getAttribute("data-theme-toggle-mode");
      if (!mode || (mode !== "light" && mode !== "dark")) return;
      applyTheme(mode);
    });
  });
  applyTheme(savedTheme);
}

function initInitialPage() {
  const hash = location.hash.replace("#", "");
  if (PAGE_KEYS.has(hash)) {
    setActivePage(hash);
    return;
  }
  const requested = new URLSearchParams(location.search).get("platform");
  if (requested && sectionForSkill(requested) === "legal") {
    setActivePage("legal");
  } else {
    setActivePage(document.body.dataset.defaultPage || "finance");
  }
}

async function init() {
  applyFastoneBranding();
  ensureTopActionSwitches();
  bindInstitutionalShortcuts();
  bindThemeToggle();
  bindDensityControls();
  bindLanguageSwitch();
  bindAuthActivityTracking();
  ensureAuthShell();
  renderInstitutionalWorkspaceShell();
  renderPlatformCommandStrip();
  const session = await loadAuthSession();
  if (!session.authenticated) {
    ensureWorkMgmtPagesShell();
    initInitialPage();
    ensureHermesFlagshipSection();
    await loadHermesFlagshipData({ showLoading: false });
    showAuthShell();
    return;
  }
  await bootWorkbench();
}

async function bootWorkbench() {
  if (appState.booted) {
    hideAuthShell();
    ensureAuthControls();
    ensureSecurityWatermark();
    await refreshPendingApprovalBubble({ autoPopup: true });
    startPendingApprovalPolling();
    noteAuthActivity();
    startAuthHeartbeatRefresh();
    startStatusRefresh();
    return;
  }
  appState.booted = true;
  hideAuthShell();
  ensureAuthControls();
  ensureSecurityWatermark();
  await refreshPendingApprovalBubble({ autoPopup: true });
  startPendingApprovalPolling();
  noteAuthActivity();
  pruneConversationStore();
  ensureDocumentFlowShell();
  ensureWorkChatShell();
  ensureWorkMgmtPagesShell();
  renderInstitutionalPageAuditStrips();
  ensureTopNavLayout();
  bindNav();
  bindInternalWorkspaceLinks();
  applyFastoneBranding();
  renderInstitutionalWorkspaceShell();
  initInitialPage();
  ensureRouteStatusCards();
  await loadStatus();
  startStatusRefresh();
  await loadGoogleWorkspaceProfiles();
  await loadComposioProfiles();
  await loadCronStatus();
  startCronStatusRefresh();
  await loadSkills();
  renderExecutiveDock();
  renderPlatformCommandStrip();
  renderSkillsGrid();
  applyWorkspaceMeta();
  normalizeHomeLayout();
  ensureHermesFlagshipSection();
  ensureWorkMgmtHomeSection();
  await loadWorkMgmtHomeData();
  await loadHermesFlagshipData({ showLoading: true });
  ensureEnterpriseCommandCenter();
  renderConversationHistory("home", document.getElementById("homeMessages"));
  renderConversationHistory("finance", document.getElementById("financeMessages"));
  renderConversationHistory("legal", document.getElementById("legalMessages"));
  await loadWeatherForecast();
  startDocumentFlowRefresh();
  ensureAttachmentRow("home", "homeInput");
  ensureOutputCenter("home", "homeMessages", () => currentLocaleMeta(currentWorkspaceSkillId("home")));
  bindWorkspaceFilePicker("finance", "financeFile", "financeFileName", "financeFileStatus");
  bindWorkspaceFilePicker("legal", "legalFile", "legalFileName", "legalFileStatus");
  buildToolMenus("home", "homeInput", () => ({
    welcome: lang() === "zh" ? "这是 FASTONE Hermes AI Agent 的人机交流入口。" : "This is the FASTONE Hermes AI Agent human exchange surface.",
    modes: lang() === "zh"
      ? [
          ["general", "General", "通用聊天和快速问答"],
          ["summary", "Summary", "摘要整理和信息压缩"],
          ["draft", "Draft", "生成清晰回复或说明"],
        ]
      : [
          ["general", "General", "Open chat and quick questions"],
          ["summary", "Summary", "Condense notes and working material"],
          ["draft", "Draft", "Draft a clean reply or section"],
        ],
    templates: lang() === "zh"
      ? [
          ["快速摘要", "先压缩重点，再列下一步", "请先用简洁结构总结重点，再列出下一步建议。"],
          ["生成回复", "把要点整理成清晰回复", "请把我的零散要点整理成一段清晰、专业的回复。"],
        ]
      : [
          ["Quick Summary", "Condense the main points first", "Please summarize the key points clearly, then list the next actions."],
          ["Draft Reply", "Turn notes into a clean message", "Please turn my rough notes into a concise, professional reply."],
        ],
  }));
  buildToolMenus("finance", "financeInput", () => currentLocaleMeta(appState.currentSkillId));
  buildToolMenus("legal", "legalInput", () => currentLocaleMeta(new URLSearchParams(location.search).get("platform") || "uk_hk_financial_contract_counsel"));
  syncWorkspaceActionRow("finance", "financeInput", "financeMessages", () => currentLocaleMeta(appState.currentSkillId));
  syncWorkspaceActionRow("legal", "legalInput", "legalMessages", () => currentLocaleMeta(new URLSearchParams(location.search).get("platform") || "uk_hk_financial_contract_counsel"));
  ensureOutputCenter("finance", "financeMessages", () => currentLocaleMeta(appState.currentSkillId));
  ensureOutputCenter("legal", "legalMessages", () => currentLocaleMeta(new URLSearchParams(location.search).get("platform") || "uk_hk_financial_contract_counsel"));
  ensureSidebarProgressPanel("finance");
  ensureSidebarProgressPanel("legal");
  bindComposer("homeInput", "homeSend", "homeMessages", "home", () => ({
    welcome: lang() === "zh" ? "这是 FASTONE Hermes AI Agent 的人机交流入口。" : "This is the FASTONE Hermes AI Agent human exchange surface.",
    modes: [["general", "General", "General"]],
    templates: [],
  }));
  bindComposer("financeInput", "financeSend", "financeMessages", "finance", () => currentLocaleMeta(appState.currentSkillId));
  bindComposer("legalInput", "legalSend", "legalMessages", "legal", () => currentLocaleMeta(new URLSearchParams(location.search).get("platform") || "uk_hk_financial_contract_counsel"));
  ensureTelegramBridge();
  startWorkMgmtRefresh();
  startWorkChatRefresh();
  startAuthHeartbeatRefresh();
}

document.addEventListener("DOMContentLoaded", init);
