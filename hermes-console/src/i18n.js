const dict = {
  en: {
    dashboard: 'Dashboard',
    chat: 'Chat',
    workspace: 'Workspace',
    tasks: 'Tasks',
    kpi: 'KPI',
    strategy: 'Strategy',
    control: 'Control',
    console: 'Control Console',
    runtime: 'AI Organization Runtime',
    liveVia: 'Live via http://127.0.0.1:8787',
    impact: 'AI Impact',
    impactCaption: 'Business-level value created by Hermes automation',
    actions: 'Actions',
    workflows: 'Workflows',
    avgScore: 'Avg Score',
    confidence: 'Confidence',
    live: 'Live',
    workModes: 'Work Modes',
    workModesCaption: 'Config-driven capabilities for this workspace',
    templates: 'Templates',
    templatesCaption: 'Reusable workspace starting points',
    legal: 'Legal Review',
    legalCaption: 'Submit trade-finance documents or legal queries for AI-powered structured review.',
    legalPlaceholder: 'Describe the legal matter or paste the contract text…',
    legalSubmit: 'Run Legal Review',
    legalRunning: 'Running…',
    legalReset: 'New Review',
    legalPolling: 'Legal workflow in progress',
    legalOutput: 'Legal Analysis',
    legalDecision: 'Decision',
    legalArtifact: 'Structured Artifact',
    legalError: 'Workflow Failed',
    legalStartFailed: 'Failed to start legal workflow',
    legalTimeout: 'Legal workflow timed out after 4 minutes',
  },
  zh: {
    dashboard: '仪表盘',
    chat: '聊天',
    workspace: '工作区',
    tasks: '任务',
    kpi: '指标',
    strategy: '策略',
    control: '控制台',
    console: '控制台',
    runtime: 'AI 组织运行时',
    liveVia: '实时连接 http://127.0.0.1:8787',
    impact: 'AI价值',
    impactCaption: 'Hermes 自动化创造的业务价值',
    actions: '自动操作',
    workflows: '流程完成',
    avgScore: '平均评分',
    confidence: '可信度',
    live: '在线',
    workModes: '工作模式',
    workModesCaption: '由配置驱动的工作区能力',
    templates: '模板',
    templatesCaption: '可复用的工作区起点',
    legal: '法律审查',
    legalCaption: '提交贸易融资文件或法律问题，获取 AI 结构化审查报告。',
    legalPlaceholder: '描述法律事项或粘贴合同文本…',
    legalSubmit: '启动法律审查',
    legalRunning: '执行中…',
    legalReset: '新建审查',
    legalPolling: '法律工作流执行中',
    legalOutput: '法律分析',
    legalDecision: '决策结论',
    legalArtifact: '结构化产出',
    legalError: '工作流失败',
    legalStartFailed: '法律工作流启动失败',
    legalTimeout: '法律工作流超时（4分钟）',
  },
}

let currentLang = 'en'

export function t(key) {
  return dict[currentLang]?.[key] || dict.en[key] || key
}

export function setLang(lang) {
  currentLang = dict[lang] ? lang : 'en'
  localStorage.setItem('lang', currentLang)
}

export function initLang() {
  currentLang = localStorage.getItem('lang') || 'en'
  if (!dict[currentLang]) currentLang = 'en'
}

export function getLang() {
  return currentLang
}
