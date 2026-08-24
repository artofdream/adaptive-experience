# Promotion checklist (manual → GitLab)

Use when lifting any file from `research/grok-branch/` into GitLab.

## Per finding

- [ ] Read the recommendation MD end-to-end
- [ ] Confirm still valid on current `origin/main` (mirror may lag)
- [ ] Open or reuse GitLab issue; link CF-ID
- [ ] Branch from `main`: name suggested in the MD (`fix/cf-0xx-...`)
- [ ] Implement **only** that finding’s scope
- [ ] Run local guards if scripts/docs IDs touched: `python scripts/run_all_guards.py`
- [ ] Open focused MR; assign `@aea-mr-coordinator` when ready
- [ ] Do not auto-merge from Grok/sandbox

## Order

1. CF-048  
2. CF-049  
3. CF-050  
4. CF-051  
5. CF-052  
6. CF-053  

## After merge

- [ ] Optional: note resolution under `research/grok-branch/findings/`  
- [ ] GitHub mirror updates on its own (one-way from GitLab `main`)
