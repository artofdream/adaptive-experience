# AWS MCP credentials on cts-ai — 2026-09-03

> **Captured**: 2026-09-03
> **Owner**: `@aea-devsecops-platform` with `@aea-knowledge-guardian`
> **Tags**: #aea #second-brain #aws #mcp #cts-ai #path-b
> **Related**: [[2026-09-02-session-handover-cloud-agents-local-cts-ai]] · [[2026-09-02-session-memory-log-cts-ai-docker-wsl-repair]] · [[2026-09-03-path-b-florist-384-redeploy-prove]] · [[2026-09-02-session-memory-log-florist-queue-rog-handoff]] · [[2026-09-02-native-web-gap-closing-technical-handoff]]

Path B AWS work when cts-ai is offline needs Cursor AWS MCP. When cts-ai is online, **local AWS CLI is enough**; MCP is the backup.

## Probe (this session)

| Check | Result |
|---|---|
| Namespaces | `plugin-aws-core-aws-mcp`, `user-aws-mcp`, `plugin-aws-amplify-aws-mcp` — `namespaceStatus: ready` (not `needsAuth`) |
| Also ready | `plugin-aws-serverless-aws-serverless-mcp`, `plugin-deploy-on-aws-awspricing`, `plugin-deploy-on-aws-awsiac` |
| `mcp_auth` | Not invoked — ready, not `needsAuth` |
| MCP `sts get-caller-identity` (all three AWS proxies) | Account `737290977112` · `arn:aws:iam::737290977112:user/cts` · UserId `AIDA2XKPXP5MOGVDJVJAT` |
| Local CLI on cts-ai (`aws-cli/2.36.24`) | Same Account / Arn |
| Region | `us-east-1` |

Credentials are **live** on this machine today. No Terraform apply. No secrets printed.

## In-chat auth cannot work

AWS Core / user `aws-mcp` connectors are **stdio** (`uvx mcp-proxy-for-aws` → `https://aws-mcp.us-east-1.api.aws/mcp`). Cursor `AuthenticateMcpServer` / the in-chat Connect card is HTTP-only and returns **`stdio_unsupported`**. Do not retry that card.

The stdio proxy inherits the **local AWS credential chain** (CLI profile / SSO / IAM user). Refresh that chain, then toggle the MCP server or reload the window.

## Sponsor clicks (next expiry — do not paste keys in chat)

Target: account **737290977112**, region **us-east-1**.

1. Cursor **Settings** (gear) → **MCP**.
2. Confirm these servers are enabled (green): **aws-mcp** (user) and **AWS Core** / **Aws-mcp** plugin. Amplify’s proxy is the same family.
3. Do **not** click Connect / Authenticate in chat (`stdio_unsupported`).
4. Refresh creds **outside chat**:
   - If IAM Identity Center: AWS CLI `aws sso login` on the profile that maps to `737290977112`.
   - If `aws login` (CLI 2.32+): run it locally on cts-ai; do not paste the browser code here.
   - If IAM user keys for `user/cts`: update them only in the AWS CLI / OS credential store or the AWS Core plugin credential fields in **Settings → MCP / Plugins → AWS Core**. Never paste access keys or secret keys into chat.
5. In **Settings → MCP**, disable then enable `aws-mcp` (or Command Palette → **Developer: Reload Window**).
6. Ask an agent for `sts get-caller-identity` only. Expect Account `737290977112` and an Arn under that account.

Until that refresh is done after a future expiry, use **local AWS CLI on cts-ai** (same identity used for the #384 migration / ECS RunTask). cts-ai online is enough; MCP is backup.

## Lane guard

Do not take florist **#395** (`feat/395-florist-today-prepare-list`) or ROG ADB **#381**.
