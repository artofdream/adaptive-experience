# BFF and Edge API Gateway

This directory implements the M1 browser perimeter defined by ADR-007 and
ADR-010. Browser traffic terminates at the TLS gateway and reaches the BFF;
neither component owns experience state, workflow, context versions, or domain
validation.

## Local startup

```sh
python edge/scripts/run_integration_tests.py
```

The local HTTPS endpoint is `https://localhost:8443`. Its certificate is
ephemeral and self-signed. The local bearer token is a non-production fixture
declared in Compose; production authentication material must come from the
deployment environment.

The root URL serves the MVP browser shell. It offers one plain-language
conversation entry point, visible ordering progress, a persistent “What we
understand” region, correction reassurance, keyboard focus treatment, semantic
landmarks, and an optional three-step help dialog. These are the executable
NFR-001 baseline; usability research remains the production validation method.

The UI uses standards-based HTML, CSS, and JavaScript for current evergreen
desktop, tablet, and mobile browsers. Its tested viewport contract is:

- desktop above 960px: conversation and Shared Understanding remain side by side;
- tablet from 641px to 960px: primary regions form one column and tiles form two;
- mobile through 640px: one-column reading order, full-width primary action,
  minimum 44px interactive targets, wrapping user content, and compact progress.

Reduced-motion and forced-colour preferences are preserved. Release validation
must cover the current two major versions of Chrome, Edge, Firefox, and Safari,
plus Chrome on Android and Safari on iOS; automated structural assertions guard
the responsive contract in every pipeline.

The BFF container has no host port. Nginx is the only published backend entry
point and strips internal identity headers before proxying. Browser assets,
responses, and logs contain no PostgreSQL or Kafka connection details.

## API boundary

Wired end-to-end through authenticated `HttpOrchestration` to Internal
Orchestration (M2 Conversation and Shared Understanding):

- `POST /api/v1/session` creates an opaque browser session and CSRF token, then
  ensures the matching internal experience session.
- `POST /api/v1/conversation/messages` accepts a T-01 customer message and
  returns its message ID, correlation ID, and new context version immediately;
  AI processing continues asynchronously through `customer.message.submitted`.
- `GET /api/v1/conversation` returns the authenticated session's least-data
  conversation projection (up to 50 visible messages).
- `GET /api/v1/shared-understanding` returns only the six governed intent facets,
  current context version, and up to three thought-completion suggestions.
- `PATCH /api/v1/shared-understanding` delegates partial corrections with the
  authenticated subject, correlation ID, and observed context version.
- AI-derived conversation acknowledgements and Shared Understanding projections
  always include `ai_generated`, the active `assistant_mode`, and a plain-language
  disclosure telling customers to review and correct the interpretation
  (NFR-005). These fields remain present when the availability fallback is used.
- `GET /healthz` is an unauthenticated liveness check without dependency data.

Perimeter placeholders (Edge transport, auth, CSRF, and least-data shaping only).
Internal Orchestration does not yet expose matching HTTP resources; the BFF must
not invent authoritative command acceptance, workspace tiles, or stream events:

- `POST /api/v1/commands` validates transport shape and fails closed until
  Orchestration publishes an internal command surface.
- `GET /api/v1/workspace` returns an empty least-data projection
  (`context_version` 0, no tiles) until an internal workspace projection exists.
- `GET /api/v1/stream` keeps the reconnectable SSE contract and honors
  `Last-Event-ID`, but emits no events until Orchestration publishes a stream.

The integration runner builds the containers, waits for both health checks,
verifies the HTTPS gateway, and executes ten standard assistant queries through
the real TLS, authentication, BFF, and Orchestration path. The run reports p95
and maximum latency and fails if any measured response exceeds the NFR-004
three-second limit. This reference-path guard complements the 2.5-second maximum
AI-provider timeout; production deployments must retain equivalent percentile
telemetry for their configured provider and infrastructure. The runner always
tears the stack down. Run
`python -m unittest discover -s edge/tests -v` for the same security and
boundary suite used by GitLab CI. The BFF
uses an authenticated `HttpOrchestration` adapter. Runtime configuration
requires `AEA_ORCHESTRATION_URL` and `AEA_ORCHESTRATION_TOKEN` and fails closed
without them. The BFF holds no PostgreSQL or Kafka credentials; validation and
mutation authority remain in the internal Orchestration service.
