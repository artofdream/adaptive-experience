# Strategic Architecture Study: Native Mobile Feasibility, FinOps & DevOps Pipeline

> **Date**: 2026-08-28  
> **Stakeholders**: `@aea-product-owner`, `@aea-cost-guardian`, `@aea-devsecops-platform`, `@aea-senior-software-engineer`, `@aea-knowledge-guardian`  
> **Traceability**: Issue #272, BG-001, BG-007, FR-016, ADR-001, ADR-007, ADR-008, ADR-013, NFR-017  
> **Tags**: #aea  

---

## 1. Executive Summary & Product Vision Expansion

This strategic study establishes the feasibility, cost structure (FinOps), and DevOps pipeline for launching **Native Mobile Companion Applications** (Android Kotlin / Jetpack Compose leading to iOS SwiftUI) for the **Adaptive Experience Architecture (AEA)**.

### Core Architectural Principle
> **100% Backend & API Contract Reuse.**  
> Native mobile clients consume the exact same edge BFF REST endpoints (`/api/v1/sessions/...`), Server-Sent Events (SSE) stream (`/api/v1/sessions/{id}/stream`), and zero-PII vault checkout (`NFR-017` / `ADR-013`) as the Web Adaptive Workspace. No platform service rewrites are required.

---

## 2. Acquisition & Financial Summary (FinOps)

| Category | Requirement | Cost / Fee | Purpose |
| :--- | :--- | :--- | :--- |
| **Android Developer Account** | Google Play Console | **$25 (One-time)** | App store distribution & Internal Test track management |
| **Apple Developer Account** | Apple Developer Program | **$99 / year** | App Store publishing, TestFlight & APNs push certificates |
| **Cloud Infrastructure (AWS)** | ECS Fargate + RDS + MSK | **~$65 – $120 / month** | Reused existing AEA Pilot cloud stack (`aea.artof.link`) |
| **Push Notifications** | Firebase Cloud Messaging (FCM) | **$0 (Free Tier)** | FCM push notification relays for annual occasion reminders (`FR-016`) |
| **Build Automation** | Fastlane + GitLab CI | **$0 (Open Source)** | Automated compilation, signing, and Play Store / TestFlight upload |

---

## 3. Recommended MCP Servers & Developer Platforms

1. **Figma MCP (`plugin-figma-figma`)**: Syncs Figma mobile UI frames directly to Kotlin Jetpack Compose and SwiftUI layout code.
2. **GitLab MCP**: Automated issue management, MR reviews, pipeline log tailing, and MWPS auto-merge authority.
3. **PostgreSQL MCP**: Direct inspection of `sessions`, `workspace_events`, and `customer_occasion_memory` tables.
4. **Fastlane & GitLab CI**: Automated Android `.aab` and iOS `.ipa` compilation, signing, and beta track distribution.

---

## 4. Second Brain References

- [[path-b-dual-viewport-specification]] — Path B Dual-Viewport Architecture Specification.
- [[2026-08-28-session-memory-log-path-b-ux-spec-272]] — Session Memory Log for Dual-Viewport Specification.
- [[CF-054-path-b-dual-viewport]] — Coherence Finding for Dual-Viewport Presentation.
