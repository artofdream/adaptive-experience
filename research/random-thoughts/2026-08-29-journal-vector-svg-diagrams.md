# Journal vector SVG diagrams and base64 corruption fix

> **Tags**: #aea #second-brain #framework #journal #svg #knowledge-first
> **Captured**: 2026-08-29
> **GitLab**: Fixes journal image rendering
> **Owners to inherit**: @aea-ux-designer, @aea-knowledge-guardian, @aea-mr-coordinator

## Background & Root Cause Analysis

Sponsor asked why the Journal page showed a broken image icon for `Claim vs probe`.

### Root Cause
1. The `.jpg` files (`claim-vs-probe.jpg`, `two-hostnames.jpg`, `four-lines.jpg`) originally checked into `docs/framework/assets/` were ASCII base64-encoded strings (with `two-hostnames.jpg` even containing a truncated string `<remaining_truncated 2810 bytes>`), not raw binary JPEG data.
2. Browsers receiving `Content-Type: image/jpeg` could not decode the ASCII base64 payload as valid JPEG headers (`FF D8 FF E0`), triggering the browser broken image fallback.

### Solution
1. Replaced all 3 journal raster/corrupted files with handcrafted, pure vector standalone `.svg` diagrams:
   - `docs/framework/assets/claim-vs-probe.svg` (Claim vs probe: merged ticket / status claims vs dual-viewport probes)
   - `docs/framework/assets/two-hostnames.svg` (Two hostnames: architecture.artof.link vs aea.artof.link)
   - `docs/framework/assets/four-lines.svg` (Four lines, one day: Challenge, Solve, Ship, Lesson)
2. Updated `docs/framework/journal.md` to reference `.svg` assets.
3. Clean zero-dependency build, infinite crisp vector scaling on Retina/mobile viewports, and zero base64 corruption risks.

Existing IDs: [[2026-08-29-public-framework-svg-diagrams]], [[2026-08-29-framework-nav-hygiene-and-freshness]].
