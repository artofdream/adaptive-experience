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

The BFF container has no host port. Nginx is the only published backend entry
point and strips internal identity headers before proxying. Browser assets,
responses, and logs contain no PostgreSQL or Kafka connection details.

## API boundary

- `POST /api/v1/session` creates an opaque browser session and CSRF token.
- `POST /api/v1/commands` performs transport validation and delegates command
  acceptance to Orchestration. Responses include correlation ID and observed
  context version.
- `POST /api/v1/conversation/messages` accepts a T-01 customer message and
  returns its message ID, correlation ID, and new context version immediately;
  AI processing continues asynchronously through `customer.message.submitted`.
- `GET /api/v1/conversation` returns the authenticated session's least-data
  conversation projection (up to 50 visible messages).
- `GET /api/v1/workspace` returns a least-data workspace projection.
- `GET /api/v1/stream` emits reconnectable server-sent events and honors
  `Last-Event-ID`.
- `GET /healthz` is an unauthenticated liveness check without dependency data.

The integration runner builds the containers, waits for both health checks,
verifies the HTTPS gateway, and always tears the stack down. Run
`python -m unittest discover -s edge/tests -v` for the same security and
boundary suite used by GitLab CI. The BFF
uses a product-neutral `OrchestrationPort`; later M2 behavior supplies its
implementation without moving authority into the edge.
