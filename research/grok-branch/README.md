# Grok workstream (fix via markdown only)

> **Branch concept:** `grok` — local markdown work products.  
> **Not pushed automatically.** Promote to GitLab by hand (issue → branch → MR).  
> **Canonical tracker:** GitLab. **GitHub:** one-way mirror of `main` only.

## Layout

```
research/grok-branch/
├── README.md                 # this file
├── PROMOTION-CHECKLIST.md    # manual steps per finding
├── findings/
│   └── 2026-08-23-grok-independent-assessment.md
└── recommendations/
    ├── 2026-08-23-gap-analysis-value-cost.md
    ├── CF-048-daily-brief-honesty.md          # do first
    ├── CF-049-m15-ssr-lcp-honesty.md
    ├── CF-050-migration-runner-root.md
    ├── CF-051-fr016-017-narrative.md
    ├── CF-052-m14-merchant-domain.md
    ├── CF-053-m17-pgvector-status.md
    └── CF-049-through-053-index.md
```

## Fix order (one MR each)

1. **CF-048** — daily brief honesty  
2. **CF-049** — M15 SSR/LCP labels  
3. **CF-050** — migration runner 019–022  
4. **CF-051** — FR-016/017 narrative  
5. **CF-052** — M14 merchant domain claim  
6. **CF-053** — pgvector status wording  

Each recommendation MD includes: problem, desired outcome, proposed file changes, out of scope, acceptance checks, suggested branch name, evidence paths.

## SOP still applies

- No invented BG/US/FR/NFR IDs  
- One finding → one issue → one branch → one MR  
- Docker integration before MR when runtime code changes (e.g. CF-050 Option A)  
- `glab` / GitLab only for real delivery  
