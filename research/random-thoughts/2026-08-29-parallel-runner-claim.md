# Evaluate: parallel-runner path and scope claim (29 Aug 2026)

Related: #297. Proposed. Not adopted. Not a sensor yet.

## Why this note exists

On 29 Aug several runners opened MRs at once (!319, !323, !324, !325, !326, !327). That is a useful antifragility probe. Git already shows two edits to the same file. It does not show the miss that repeated:

1. A runner treats another runner's status word as a probe.
2. A runner implements past an evaluate-only or confirm-only "done when."

Class example (titles only, not a verdict on !325): #282 asks DSO to confirm ARM64 feasibility. !325 is titled as a runtime and RDS change. Scope, not a merge conflict.

## Claim under evaluation

Before an MR opens, the runner names the paths and the issue's "done when." A second runner on those paths, or a diff that exceeds confirm-only / evaluate-only, fails closed.

MRC stays a merge hat, not a GitLab username. A status word still needs a probe in the same session.

## What this is not

- Not a claim board, bot, or CI gate in this MR.
- Not CONSTRAINTS.md (#289). Not a DATE_RE edit (#291). Not a judge model (#292).
- Not a Kimi swarm. Not a new CF-id. Not shop restyle. Not 3DX Lab.
- Not a claim that AEA is antifragile. Dual-viewport after CSS remains Unknown.

## Team decision (done when)

Comment on #297: adopt as guide / adopt as sensor / reject. If adopt, a **second** issue does the actual rule. This note does not close #297.
