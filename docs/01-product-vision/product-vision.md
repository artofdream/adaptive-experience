# Product Vision

## Vision
Create an AI-native florist experience where customers express needs naturally and the interface evolves as understanding grows.

## Business goals
1. BG-001 Develop an AI-Enhanced Customer Ordering Experience.
2. BG-002 Provide 24/7 AI-Powered Customer Support.
3. BG-003 Deliver Personalized Flower Recommendations.
4. BG-004 Automate Customer Service Activities.
5. BG-005 Improve Inventory Decision-Making Using AI Insights.
6. BG-006 Optimize Order Fulfillment and Delivery Experience.
7. BG-007 Enhance Customer Engagement and Retention.

## Principles
- Thought before form
- Knowledge before navigation
- Shared understanding before recommendation
- Experiences earn attention
- Continuity before immediacy
- Latest relevant intent wins
- AI interprets; domain services validate

## Multi-surface & native mobile vision (Future extension & roadmap)
- **Single session, multi-surface presentation**: A unified session model (`ADR-001`), Contract-First API (`ADR-008`), and Zero-PII security (`NFR-017`) project adaptively across desktop and mobile form factors. The reference implementation delivers a Responsive Web Dual-Viewport Presentation (desktop 8-Tile spatial layout transitioning to a 3-Stage *Need → Pick → Pay* linear concierge flow on mobile viewports).
- **Native Android & iOS companion experience (Future extension vision)**: Architectural vision and feasibility study for dedicated native mobile companion applications (Android Kotlin / Jetpack Compose leading to iOS SwiftUI) consuming identical BFF endpoints without backend rewrites. (Reference codebase currently provides the Responsive Web Dual-Viewport experience; native binaries are not implemented).
- **Proactive annual occasion engagement (Future extension vision)**: Architectural blueprint for integrating native push notification relays (FCM/APNs) with `EngagementCrmService` (`FR-016`) to proactively remind shoppers of upcoming annual occasions (e.g., *Mom's Birthday*) 30 days in advance. (Push relays and live notification delivery are not shipped in the current reference foundation).

