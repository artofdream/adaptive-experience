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

## Multi-surface & native mobile vision
- **Single session, multi-surface presentation**: A unified session model (`ADR-001`), Contract-First API (`ADR-008`), and Zero-PII security (`NFR-017`) project adaptively across both Web Adaptive Workspaces (desktop 8-Tile spatial layout) and Native Mobile Concierge apps (3-Stage *Need → Pick → Pay* linear flow).
- **Native Android & iOS companion experience**: High-performance, native mobile applications (Android Kotlin / Jetpack Compose leading to iOS SwiftUI) consuming identical BFF endpoints without backend rewrites.
- **Proactive annual occasion engagement**: Integration of native push notification relays (FCM/APNs) with `EngagementCrmService` (`FR-016`) to proactively remind shoppers of upcoming annual occasions (e.g., *Mom's Birthday*) 30 days in advance.

