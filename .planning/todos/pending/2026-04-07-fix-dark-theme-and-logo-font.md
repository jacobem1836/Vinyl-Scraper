---
title: Fix dark theme not rendering and logo font
priority: high
phase: ui
created: 2026-04-07
---

## Issues

1. **Dark theme not displaying** — CSS has correct `--color-bg: #0a0a0a` and `body { background: var(--color-bg) }`, server serves correct file, but UI renders with white/light background. Verified via curl that served CSS is correct. Likely a template or serving issue not caught by file inspection.

2. **CRATE logo font** — Ensure the CRATE wordmark in the nav uses Bodoni Moda Bold (`static/fonts/BodoniModa-Bold.woff2` is self-hosted, `@font-face` declared in style.css). Verify it's actually loading and rendering correctly.
