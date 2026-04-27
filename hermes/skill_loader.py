from pathlib import Path


BASE_SKILL_FILES = [
    "skills/core/skill.md",
    "skills/core/role_and_limits.md",
    "skills/core/output_standards.md",
    "skills/core/compliance_rules.md",
]


FINANCE_LAW_FILES = [
    "skills/finance_law/legal_review_template.md",
    "skills/finance_law/finance_clause_library.md",
    "skills/finance_law/facility_agreement_playbook.md",
    "skills/finance_law/guarantee_review_playbook.md",
    "skills/finance_law/security_documents_playbook.md",
    "skills/finance_law/cross_border_finance_checklist.md",
]


TRADE_FINANCE_FILES = [
    "skills/trade_finance/sblc_dlc_review_checklist.md",
    "skills/trade_finance/ucp600_guide.md",
    "skills/trade_finance/isp98_guide.md",
    "skills/trade_finance/urdg758_guide.md",
    "skills/trade_finance/fraud_red_flags.md",
]


TEMPLATE_FILES = [
    "skills/templates/risk_memo_template.md",
    "skills/templates/clause_redraft_template.md",
    "skills/templates/negotiation_tracker.md",
    "skills/templates/cp_checklist_template.md",
    "skills/templates/closing_agenda_template.md",
]


def select_skill_files(user_input: str):
    text = user_input.lower()

    files = list(BASE_SKILL_FILES)

    finance_keywords = [
        "facility", "loan", "credit agreement", "授信", "贷款",
        "guarantee", "担保", "保证", "indemnity", "security",
        "charge", "pledge", "抵押", "质押", "cross-border", "跨境"
    ]

    trade_keywords = [
        "sblc", "dlc", "letter of credit", "信用证", "保函",
        "demand guarantee", "performance bond", "ucp600", "ucp 600",
        "isp98", "isp 98", "urdg758", "urdg 758", "mt760", "mt799"
    ]

    template_keywords = [
        "memo", "risk memo", "checklist", "清单", "redraft",
        "clause", "条款", "negotiation", "谈判", "closing", "cp"
    ]

    if any(keyword in text for keyword in finance_keywords):
        files.extend(FINANCE_LAW_FILES)

    if any(keyword in text for keyword in trade_keywords):
        files.extend(TRADE_FINANCE_FILES)

    if any(keyword in text for keyword in template_keywords):
        files.extend(TEMPLATE_FILES)

    return list(dict.fromkeys(files))


def load_skill_files(user_input: str = ""):
    selected_files = select_skill_files(user_input)
    contents = []

    for file_path in selected_files:
        path = Path(file_path)
        if path.exists():
            contents.append(f"\n\n# FILE: {file_path}\n")
            contents.append(path.read_text(encoding="utf-8"))

    return "\n".join(contents)
