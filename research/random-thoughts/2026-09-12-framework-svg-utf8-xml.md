# Framework SVG assets must be UTF-8 well-formed XML

> **Tags**: #aea #second-brain #framework #svg #knowledge-first
> **Captured**: 2026-09-12
> **GitLab**: #435
> **Owners to inherit**: @aea-knowledge-guardian, @aea-coherence-guardian

Windows-1252 `0x92`/`0xb7` and C0 controls in `docs/framework/assets/*.svg` made browsers reject `<img>` despite HTTP 200. Guard: `test_framework_asset_svgs_are_utf8_xml`. Related [[2026-08-29-public-framework-svg-diagrams]] · [[2026-09-11-session-memory-log-framework-knowledge-site-423]].
