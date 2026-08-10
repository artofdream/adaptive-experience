# Requirements Specification

> Source of truth: `archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx`.
> 23 functional requirements (FR) + 17 non-functional requirements (NFR) = 40 total.
> FR-018–FR-023 and NFR-015–NFR-017 are architecture-derived (see Annex B of the
> requirements report).

## Functional Requirements

| ID | Story | Category | Scope | Requirement |
|---|---|---|---|---|
| FR-001 | US-001 | Discovery and Intent | MVP | The system shall allow customers to search and browse flower arrangements using conversational AI assistance. |
| FR-002 | US-002 | Discovery and Intent | MVP | The system shall analyze customer inputs such as occasion, budget, and preferences to suggest flower arrangements. |
| FR-003 | US-003 | Customization | Future | The system shall allow customers to customize flower type, color, size, and personal messages. |
| FR-004 | US-004 | Discovery and Intent | MVP | The system shall provide a Generative AI chatbot available 24/7. |
| FR-005 | US-005 | Discovery and Intent | MVP | The AI assistant shall answer questions using approved florist product and policy information. |
| FR-006 | US-006 | Support Automation | Future | The system shall escalate unresolved customer requests to a human representative. |
| FR-007 | US-007 | Recommendations | MVP | The system shall generate recommendations based on occasion, budget, preferences, and availability. |
| FR-008 | US-008 | Recommendations | Future | The system shall use previous purchase history to provide personalized recommendations. |
| FR-009 | US-009 | Support Automation | MVP | The system shall automatically respond to frequently asked customer questions. |
| FR-010 | US-010 | Support Automation | Future | The system shall automate responses related to order status, delivery information, and product availability. |
| FR-011 | US-011 | Inventory | MVP | The system shall maintain real-time inventory availability. |
| FR-012 | US-012 | Inventory | Future | The system shall analyze inventory trends and provide forecasting recommendations. |
| FR-013 | US-013 | Ordering and Delivery | MVP | The system shall allow customers to create and submit flower orders online. |
| FR-014 | US-014 | Ordering and Delivery | MVP | The system shall allow customers to select delivery date, time, and recipient information. |
| FR-015 | US-015 | Ordering and Delivery | MVP | The system shall provide order preparation, dispatch, and delivery status updates. |
| FR-016 | US-016 | Engagement and CRM | Future | The system shall send AI-generated reminders for birthdays, anniversaries, and events. |
| FR-017 | US-017 | Engagement and CRM | Future | The system shall provide customer engagement analytics. |
| FR-018 | US-018 | Ordering and Delivery | MVP | The system shall display an itemized order summary containing selected products, customization charges, delivery fees, taxes, discounts, and total before checkout. |
| FR-019 | US-019 | Ordering and Delivery | MVP | The system shall initiate payment through an approved external payment provider and shall not create a confirmed order until an authoritative payment outcome is received. |
| FR-020 | US-020 | Workspace Behavior | MVP | The system shall preserve completed customer decisions and unaffected tile state when recommendations, pricing, or delivery information is refreshed. |
| FR-021 | US-021 | Workspace Behavior | MVP | The system shall allow customers to review and correct the structured occasion, budget, recipient, style, flower preference, and timing information inferred from their conversation. |
| FR-022 | US-022 | Workspace Behavior | MVP | The system shall reject stale responses whose context version does not match the active experience state. |
| FR-023 | US-023 | Order Tracking | MVP | The system shall publish order preparation, dispatch, delivery, delay, and completion status through a versioned order-status topic and display the latest authoritative state to the customer. |

## Non-Functional Requirements

| ID | Story | Category | Scope | Requirement |
|---|---|---|---|---|
| NFR-001 | NFR-US-001 | Usability | MVP | The AI ordering interface shall provide an intuitive experience requiring minimal customer training. |
| NFR-002 | NFR-US-002 | Compatibility | MVP | The website shall support desktop, tablet, and mobile browsers. |
| NFR-003 | NFR-US-003 | Availability | MVP | The AI assistant shall maintain 99.5% availability. |
| NFR-004 | NFR-US-004 | Performance | MVP | The AI assistant shall respond to standard queries within 3 seconds. |
| NFR-005 | NFR-US-005 | Transparency | MVP | The system shall clearly identify AI-generated responses. |
| NFR-006 | NFR-US-006 | Accuracy | MVP | AI recommendations shall be generated using accurate product, preference, and availability data. |
| NFR-007 | NFR-US-007 | Security | MVP | Customer preference data shall be encrypted and securely stored. |
| NFR-008 | NFR-US-008 | Reliability | Future | The system shall maintain AI response quality monitoring and error tracking. |
| NFR-009 | NFR-US-009 | Data Integrity | MVP | Inventory data shall remain synchronized between ordering and inventory systems. |
| NFR-010 | NFR-US-010 | Reliability | Future | Inventory analysis shall use current and validated inventory data. |
| NFR-011 | NFR-US-011 | Performance | MVP | Order status updates shall be reflected within one minute of changes. |
| NFR-012 | NFR-US-012 | Security | MVP | Customer delivery information shall be encrypted during storage and transmission. |
| NFR-013 | NFR-US-013 | Security | MVP | Customer data shall comply with privacy and protection requirements. |
| NFR-014 | NFR-US-014 | Scalability | Future | The system shall support future AI model enhancements without major redesign. |
| NFR-015 | NFR-US-015 | Maintainability / Governance | MVP | Every MVP topic shall have an accountable owner, a versioned payload schema, and documented publisher and subscriber permissions. |
| NFR-016 | NFR-US-016 | Observability / Auditability | MVP | The system shall record message ID, topic, source, correlation ID, context version, publication time, outcome, and authorized security context for auditable workflow tracing. |
| NFR-017 | NFR-US-017 | Privacy / Security | MVP | Customer and payment payloads shall contain only the minimum fields required by each authorized subscriber, and sensitive fields shall not be exposed to unauthorized tiles or services. |

## Functional requirements by category

| Category | Requirements |
|---|---|
| Discovery and Intent | FR-001, FR-002, FR-004, FR-005 |
| Customization | FR-003 |
| Support Automation | FR-006, FR-009, FR-010 |
| Recommendations | FR-007, FR-008 |
| Inventory | FR-011, FR-012 |
| Ordering and Delivery | FR-013, FR-014, FR-015, FR-018, FR-019 |
| Engagement and CRM | FR-016, FR-017 |
| Workspace Behavior | FR-020, FR-021, FR-022 |
| Order Tracking | FR-023 |

## Scope notes

**FR-010 (Future) vs MVP support and tracking.** FR-010 automates responses about
order status, delivery information, and product availability beyond the MVP
surfaces. It does **not** replace:

- **FR-009 / ASO** — MVP automated FAQ from approved product and policy content
- **FR-015 / FR-023 / T-08** — authoritative order-status display via
  `order.status.updated`
- domain Inventory / Delivery facts shown through validated tiles

FR-006 / T-09 remains Future human escalation, separate from both FR-009 and
FR-010.
