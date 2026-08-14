# Business Goals, Epics, and User Stories

> Source of truth: `archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx`
> (Consolidated Mapping sheet). Model: 7 business goals · 7 epics · 23 functional
> user stories · 17 non-functional user stories · 40 requirements (23 FR + 17 NFR).

## Business Goals and Epics

| Business Goal | Epic | Purpose |
|---|---|---|
| BG-001 Develop an AI-Enhanced Customer Ordering Experience | EP-001 AI-Enhanced Flower Discovery & Ordering | AI-assisted shopping where customers discover, select, and customize flowers. |
| BG-002 Provide 24/7 AI-Powered Customer Support | EP-002 Generative AI Customer Assistant | Round-the-clock AI chatbot support for customer questions and assistance. |
| BG-003 Deliver Personalized Flower Recommendations | EP-003 AI Recommendation Engine | Intelligent recommendations based on occasion, budget, preferences, and history. |
| BG-004 Automate Customer Service Activities | EP-004 AI Customer Service Automation | Reduce manual support workload by automating repetitive interactions. |
| BG-005 Improve Inventory Decision-Making Using AI Insights | EP-005 AI-Assisted Inventory Management | Improve stock visibility, forecasting, and inventory decisions. |
| BG-006 Optimize Order Fulfillment and Delivery Experience | EP-006 Smart Order Processing & Delivery Management | Improve the order lifecycle from checkout through delivery confirmation. |
| BG-007 Enhance Customer Engagement and Retention | EP-007 AI Customer Relationship Management | Improve repeat business through insights, reminders, and personalized engagement. |

## Functional User Stories

| Story | Epic | Scope | User story |
|---|---|---|---|
| US-001 | EP-001 | MVP | As a customer, I want AI assistance while searching for flowers, so that I can quickly find suitable arrangements. |
| US-002 | EP-001 | MVP | As a customer, I want to describe my occasion and preferences, so that AI can suggest suitable flowers. |
| US-003 | EP-001 | MVP | As a customer, I want to customize a bouquet, so that I can create a personalized gift. |
| US-004 | EP-002 | MVP | As a customer, I want to communicate with an AI assistant anytime, so that I can receive support outside business hours. |
| US-005 | EP-002 | MVP | As a customer, I want answers about flowers, pricing, and policies, so that I can make informed decisions. |
| US-006 | EP-002 | Future | As a customer, I want complex questions transferred to staff, so that my issues can still be resolved. |
| US-007 | EP-003 | MVP | As a customer, I want AI recommendations based on my needs, so that I can choose appropriate flowers. |
| US-008 | EP-003 | Future | As a returning customer, I want recommendations based on previous orders, so that I can reorder easily. |
| US-009 | EP-004 | MVP | As a customer, I want automated responses to common questions, so that I receive immediate answers. |
| US-010 | EP-004 | Future | As a store employee, I want AI to handle routine inquiries, so that I can focus on complex tasks. |
| US-011 | EP-005 | MVP | As a florist, I want accurate inventory tracking, so that customers see available products. |
| US-012 | EP-005 | Future | As a manager, I want AI inventory insights, so that I can plan purchases better. |
| US-013 | EP-006 | MVP | As a customer, I want to place an order online, so that I can purchase flowers conveniently. |
| US-014 | EP-006 | MVP | As a customer, I want delivery scheduling, so that flowers arrive at the correct time. |
| US-015 | EP-006 | MVP | As a customer, I want delivery tracking, so that I know the order status. |
| US-016 | EP-007 | Future | As a customer, I want reminders for special occasions, so that I do not forget important dates. |
| US-017 | EP-007 | Future | As a manager, I want customer insights, so that I can improve marketing campaigns. |
| US-018 | EP-006 | MVP | As a customer, I want an itemized and continuously updated order summary, so that I can review all charges before checkout. |
| US-019 | EP-006 | MVP | As a customer, I want secure payment and authoritative confirmation, so that I know my order was accepted only after payment succeeds. |
| US-020 | EP-001 | MVP | As a customer, I want unaffected choices to remain stable when part of the workspace refreshes, so that I do not lose progress. |
| US-021 | EP-001 | MVP | As a customer, I want to review and correct what the AI inferred, so that recommendations reflect my actual needs. |
| US-022 | EP-001 | MVP | As a customer, I want the workspace to ignore outdated results, so that current choices are not overwritten. |
| US-023 | EP-006 | MVP | As a customer, I want authoritative order-status updates, so that I know when my order is prepared, dispatched, delayed, delivered, or completed. |

## Non-Functional User Stories

| Story | Epic | Category | Scope | User story |
|---|---|---|---|---|
| NFR-US-001 | EP-001 | Usability | MVP | As a customer, I want the AI shopping experience to be easy to use, so that I can find flowers without confusion. |
| NFR-US-002 | EP-001 | Compatibility | MVP | As a customer, I want the website to work on my preferred device, so that I can order flowers anywhere. |
| NFR-US-003 | EP-002 | Availability | MVP | As a customer, I want the AI assistant available whenever I need help, so that I can receive support outside business hours. |
| NFR-US-004 | EP-002 | Performance | MVP | As a customer, I want fast AI responses, so that I do not experience delays while getting assistance. |
| NFR-US-005 | EP-002 | Transparency | MVP | As a customer, I want to know when I am interacting with AI, so that I understand the source of responses. |
| NFR-US-006 | EP-003 | Accuracy | MVP | As a customer, I want relevant recommendations, so that AI suggestions are useful for my occasion. |
| NFR-US-007 | EP-003 | Security | MVP | As a customer, I want my personal preferences protected, so that I can trust AI recommendations. |
| NFR-US-008 | EP-004 | Reliability | Future | As a customer, I want reliable AI responses, so that automated support is dependable. |
| NFR-US-009 | EP-005 | Data Integrity | MVP | As a florist, I want accurate inventory information, so that I do not make decisions using outdated data. |
| NFR-US-010 | EP-005 | Reliability | Future | As a manager, I want reliable inventory analytics, so that I can trust AI recommendations. |
| NFR-US-011 | EP-006 | Performance | MVP | As a customer, I want accurate delivery tracking, so that I know my order status. |
| NFR-US-012 | EP-006 | Security | MVP | As a customer, I want my delivery information protected, so that my personal details remain secure. |
| NFR-US-013 | EP-007 | Security | MVP | As a customer, I want my information protected, so that I trust personalized communications. |
| NFR-US-014 | EP-007 | Scalability | Future | As a business owner, I want the AI platform to evolve, so that future AI capabilities can be added easily. |
| NFR-US-015 | EP-001 | Maintainability / Governance | MVP | As a product owner, I want governed and versioned message topics, so that the workspace can evolve safely. |
| NFR-US-016 | EP-001 | Observability / Auditability | MVP | As an operator, I want traceable message workflows, so that failures and decisions can be audited. |
| NFR-US-017 | EP-001 | Privacy / Security | MVP | As a customer, I want my personal and payment data shared only where needed, so that my information remains protected. |

## Scope summary

- MVP stories: 30 · Future stories: 10 (across the 40 functional + non-functional stories).
- FR-006 / T-09 Support Escalation is Future scope, a conditional overlay outside the initial MVP.
