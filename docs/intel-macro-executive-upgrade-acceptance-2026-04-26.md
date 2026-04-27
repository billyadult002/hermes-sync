# Intelligence Center Executive Upgrade Acceptance (2026-04-26)

Version target: `20260426brand9`

## Scope
- Add executive-grade macro section in Intelligence Center:
  - Major global FX pairs
  - Major sovereign daily yields (US/UK/JP)
  - Anomaly-threshold alerts
  - 6-month K-line chart with instrument switching

## Completed
- [x] Added macro panel block in Intelligence side stack (`data-intel-macro-rates`)
- [x] Added major FX list: EUR/USD, GBP/USD, USD/JPY, USD/CNH, AUD/USD, USD/CHF
- [x] Added sovereign yields list: US 5Y/10Y/30Y, UK 10Y, JP 10Y
- [x] Added anomaly logic with executive states: `Normal / Watch / Abnormal`
- [x] Added threshold alert section at top of macro panel
- [x] Added 6M K-line chart card
- [x] Added click-to-switch symbol behavior on FX/yield rows
- [x] Extended market-data refresh to include `forex`
- [x] Added backend default instrument seeds for FX and sovereign yield symbols
- [x] Added cache persistence for macro rates + selected symbol + macro 6M candle

## QA Checklist
- [x] JS syntax check passed
- [x] Python syntax check passed
- [x] New selectors and bindings exist in code
- [x] Asset version bumped to avoid stale-cache rendering

## Notes
- Sovereign yield symbols are normalized to percentage display for executive readability.
- If a provider temporarily has no quote/candle for a symbol, panel remains stable and shows graceful fallback text.
