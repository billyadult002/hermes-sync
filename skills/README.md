# Hermes AI Agent Skills

This directory contains the professional skill system for Hermes Legal-Finance Agent.

## 1. Core

| File | Purpose |
|---|---|
| core/skill.md | Master skill and routing rules |
| core/role_and_limits.md | Role, legal limits and disclaimers |
| core/output_standards.md | Output structure and risk rating |
| core/compliance_rules.md | Compliance and prohibited assistance rules |

## 2. Finance Law

| File | Purpose |
|---|---|
| finance_law/legal_review_template.md | General legal review template |
| finance_law/finance_clause_library.md | Standard finance clauses |
| finance_law/facility_agreement_playbook.md | Facility agreement review |
| finance_law/guarantee_review_playbook.md | Guarantee and indemnity review |
| finance_law/security_documents_playbook.md | Security document review |
| finance_law/cross_border_finance_checklist.md | Cross-border finance checklist |

## 3. Trade Finance

| File | Purpose |
|---|---|
| trade_finance/sblc_dlc_review_checklist.md | SBLC/DLC review checklist |
| trade_finance/ucp600_guide.md | UCP 600 guidance |
| trade_finance/isp98_guide.md | ISP98 guidance |
| trade_finance/urdg758_guide.md | URDG 758 guidance |
| trade_finance/fraud_red_flags.md | Fraud and compliance red flags |

## 4. Templates

| File | Purpose |
|---|---|
| templates/risk_memo_template.md | Risk memo format |
| templates/clause_redraft_template.md | Clause redraft format |
| templates/negotiation_tracker.md | Negotiation tracker |
| templates/cp_checklist_template.md | Conditions precedent checklist |
| templates/closing_agenda_template.md | Closing agenda |

## 5. Evals

| File | Purpose |
|---|---|
| evals/test_cases.md | Test cases |
| evals/expected_behaviour.md | Expected behaviour |

## 6. Usage

The Hermes application should load:

1. Core skill files by default.
2. Finance law files when the user asks about facility agreements, loans, guarantees, security or cross-border finance.
3. Trade finance files when the user asks about SBLC, DLC, demand guarantees, UCP 600, ISP98, URDG 758 or bank instruments.
4. Templates when the user asks for a memo, checklist, negotiation tracker or closing agenda.
