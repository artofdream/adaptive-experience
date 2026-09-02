# Session Handover: Cloud Runner Autonomy, Live Deploys & Workstation Offline Protocol

> **Date**: 2026-09-02
> **Author**: @aea-knowledge-guardian with @aea-devsecops-platform, @aea-project-manager, @aea-mr-coordinator
> **Tags**: #aea #second-brain #handover #session-memory #cloud-runner #m19 #visual-guide

---

## 1. Executive Summary & System State

- **Public Architecture Surface**: [`https://architecture.artof.link/comparison.html`](https://architecture.artof.link/comparison.html) is live, featuring responsive HTML tables and crisp vector SVGs (`everyday-formula-flow.svg`, `five-floors-building.svg`) with zero character-width or emoji misalignments.
- **Native Android Companion (M19)**: Internal Testing link active on Google Play Console; physical device testing confirmed by sponsor ("all good now"). Live BFF integration (`Need`, `Pick`, `Pay`) operational.
- **Local Workstation (`cts-ai`) Status**: Going offline / unavailable for ~2 hours. Git working tree is cleanly synchronized with `origin/main`. 0 background tasks active locally.
- **Cloud Infrastructure (`@dso`)**: AWS ECS Fargate agent runner (`aea-agent-runner`) and GitLab CI cloud fleet are 100% cloud-hosted and independent of local workstation.

---

## 2. Active Priorities for Cloud Runners & Online Autonomous Agents

While `cts-ai` is offline, autonomous cloud agents can pull and execute the following prioritized tickets:

| Issue | Target | Description | Stakeholder |
|---|---|---|---|
| **#367** | `platform/` | Automated golden contract tests for BFF checkout request payloads (Native vs Web parity). | `@aea-senior-software-engineer` |
| **#368** | `edge/`, `clients/` | Inject `X-AEA-Client` header to split Grafana metrics by client surface (Web vs Native). | `@aea-devsecops-platform` |
| **#370** | `docs/` | Native ↔ Web feature parity matrix and companion issue hygiene. | `@aea-product-owner` |
| **#372** | `docs/` | Update `docs/framework/stack.md` to reflect that the Native Companion is live (not just intended). | `@aea-coherence-guardian` |

---

## 3. Local Workstation Playbook (Upon Return of `cts-ai`)

When the local workstation is active again, it is dedicated to interactive physical device tasks:

1. **Local ADB Sideloading**:
   - Location: `C:\apps\android\sdk\platform-tools\adb.exe`
   - Command: `adb install -r clients/mobile/android/app/build/outputs/apk/debug/app-debug.apk`
2. **Live Logcat Streaming**:
   - Command: `adb logcat -s AEA_Companion:D NeedScreen:D PickScreen:D PayScreen:D KtorClient:D`
3. **Dual-Viewport & Empirical Journey Evidence Recording (CF-054)**:
   - Capture video directly from phone screen: `adb shell screenrecord --time-limit 30 /sdcard/companion-probe.mp4` &rarr; `adb pull /sdcard/companion-probe.mp4 docs/framework/assets/`

---

## 4. Verification & Quality Guard Invariant

- Pre-flight quality guards: **14/14 PASS** (`python scripts/run_all_guards.py`).
- Secrets posture: **CLEAN** (`python scripts/check_secrets_posture.py`).
- Dependency pin cadence: **UP TO DATE** (`2026-08` review valid).
