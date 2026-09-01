# Session Memory Log: #351 keystore File-var canvas → Second Brain

> **Date**: 2026-09-01
> **Stakeholders**: `@aea-knowledge-guardian`, `@aea-devsecops-platform`, sponsor
> **Traceability**: GitLab #351, #347; #308 and #321 remain closed
> **Tags**: #aea

---

## 1. Executive summary

This session turned the sponsor-facing #351 canvas into a git-versioned
Second Brain node so Cursor, Codex, Claude, Copilot, Gemini, and Grok inherit
the GitLab File-variable trap without opening a local `.canvas.tsx`.

---

## 2. Decisions and trade-offs

1. **Canvas is session UI, not the vault.** Capture mermaid + steps under
   `research/random-thoughts/`. Do not commit canvases or secrets.
2. **Sponsor vs DSO split stays.** Base64 paste is sponsor. `base64 -d` in
   `android-bundle-release` is DSO. First `.aab` closes #347, not this note.
3. **Do not reopen #308 / #321.** Firebase JSON and Android-app API-key
   restrict (package + SHA-1) are current. Refreshing the GitLab Variables
   page does not require recreating AWS or `GOOGLE_SERVICES_JSON`.
4. **This note does not `Closes #351`.** Decode job is still DSO.
5. **Diagram hygiene (sponsor side note).** Review older Second Brain notes
   and add mermaid where text-only hides a console or CI path. Principle:
   [[2026-09-01-second-brain-diagram-clarity]]. Not a mass rewrite this
   session.

---

## 3. Second Brain references

- [[2026-09-01-android-upload-keystore-gitlab-file-var]]
- [[2026-08-29-native-mobile-companion-system-docs-and-toolkit]]
- [[2026-08-28-native-mobile-app-feasibility-and-devops-study]]
- [[ADR-019]]
