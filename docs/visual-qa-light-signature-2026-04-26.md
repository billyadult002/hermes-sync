# FASTONE Light Signature QA Checklist (2026-04-26)

Version target: `20260426brand7`

## Scope
- Theme: `light` with `financial-institutional-upgrade`
- Goal: match dark mode quality with premium institutional look
- Pages checked: `index`, `console`, `config`, `status`, `index-en`, `console-en`, `config-en`, `status-en`, login flow

## Global System
- [x] Single visual language (porcelain base + white surfaces + navy/gold accents)
- [x] Three-layer hierarchy only (page / surface / elevated)
- [x] Primary action unified (champagne-gold gradient)
- [x] Borders and shadows reduced to institutional depth (no noisy segmentation)
- [x] Focus ring unified on input/select/textarea
- [x] Light mode text contrast rebalanced (title/body/muted)

## Left Rail / Menu
- [x] Rail switched to bright premium panel with subtle elevation
- [x] Default item readable with clear metadata hierarchy
- [x] Hover state visible but restrained
- [x] Active state upgraded to liquid-glass institutional style (light-safe)
- [x] Active icon chip and text maintain clear contrast

## Top Bar / Header
- [x] Header visual tightened with light gold wash + white porcelain panel
- [x] Command strip and work header border/blur conflicts removed
- [x] Cross-page consistency preserved (ZH/EN)

## Cards / Panels
- [x] Card family normalized to single premium surface language
- [x] Metric/status/summary cards use same border logic
- [x] AI Agent cards aligned with same panel style
- [x] Workbench and doc-flow cards no longer look patched from multiple themes

## Inputs / Table / Tooling
- [x] Input/select/textarea use clear white field + stronger neutral border
- [x] Focus glow is visible and brand-consistent
- [x] Table headers tuned to soft slate; row and border consistency restored
- [x] Tool chips/buttons normalized to same neutral shell

## AI8 Embedded Workspace
- [x] Embed frame enlarged for direct in-frame operations
- [x] Added `Expand` mode (wide working area)
- [x] Added `Focus` mode (embed-priority layout)
- [x] Mobile fallback height preserved for practical usage

## Brand / Logo
- [x] Vector logo usage remains consistent in login/top/sidebar
- [x] No shape distortion introduced by this pass

## Final Acceptance Notes
- Light mode is now aligned to a premium institutional style and no longer appears low-grade compared with dark mode.
- Remaining work for future iteration should be content-level polish only (data density and copy), not base visual system corrections.
