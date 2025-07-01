---
mode: 'edit'
---

# =========== 📊 ENGINEERING PRINCIPLES

- Build stateless microservices. Persist state externally (Redis, S3, DocumentDB, Postgres).
- All APIs must be exposed via a Gateway (NGINX, Traefik, or AWS API Gateway).
- Apply: circuit breakers, retries, exponential backoff, and timeout policies.
- Prefer serverless-first deployment (AWS Lambda, Azure Functions).
- Secrets/configuration:
  - Defined in `src/settings.py` (using Pydantic)
  - Values loaded from `.env`
- Use `setup.cfg` for dependencies. Pin versions **only** with explicit rationale.
- KISS over OOP: prefer pure functions and dataclasses over classes unless warranted.
- Comments must **add value**. Avoid restating code (❌ `# connect to MongoDB`)
- Testing naming pattern: ✅ `test_price_schema_when_valid_payload` ✅ `test_price_schema_when_invalid_price`
- Every FastAPI endpoint must have at least a smoke test.
- All workflows must include integration tests.

# =========== 🚰 TYPE SAFETY & STRUCTURED DATA

- Forbidden: ❌ `dict[str, Any]` ❌ `JSONResponse` for structured payloads
- Required: ✅ Use `TypedDict` for all structured entities:
    - API payloads - Database documents
    - Message broker contracts
    - Configuration structures ✅ TypedDicts must:
        - Be placed under `src/<module>/models/`
        - Include full docstrings for every field
- Use `BaseModel` for FastStream schemas (message broker contracts, and its API payloads)

Example:

```python
class UserData(TypedDict):
    """User data structure.

    Fields:
        id: Unique identifier
        username: Display name
        created_at: ISO 8601 timestamp
    """
    id: str
    username: str
    created_at: datetime
```

- For optional fields, use `NotRequired[]` from `typing`:

```python
class UserProfile(TypedDict):
    name: str
    age: NotRequired[int]
    bio: NotRequired[str]
```

- Prefer modern type syntax (PEP 604/585): ✅ `str | None` over `Optional[str]` ✅ `dict` over `Dict` ✅ `list` over `List`

Post-refactor type cleanup:

> ruff check --fix --unsafe-fixes

# =========== 🔀 MICROSERVICES & BROKER INTEGRATION

- Integrate FastAPI with API Gateway (for rate-limiting, auth, routing)
- Respect separation-of-concerns between controller, service, and adapter layers
- Use RabbitMQ for async messaging
- Always interface message brokers via `faststream`
  - Validate payloads using TypedDicts and FastAPI schemas
  - Handle retries/backoffs gracefully

# =========== ☁️ SERVERLESS ARCHITECTURE

- Optimize cold starts (lazy imports, minimal dependencies)
- Use AWS DocumentDB for NoSQL
- Configure autoscaling and concurrency with IaC (CDK or Serverless Framework)

# =========== 🔐 MIDDLEWARE & SECURITY

- Custom middleware required for:

  - Structured logging (loguru)
  - Distributed tracing (OpenTelemetry)
  - Metrics collection (Prometheus)

- Security practices:

  - OAuth2 with scopes on protected endpoints
  - Rate-limiting and DDoS protection
  - CORS, CSP headers set explicitly
  - OWASP Zap regression scan in CI/CD

# =========== 🚀 PERFORMANCE & SCALABILITY

- Use `async def` for all I/O-bound FastAPI routes
- Introduce caching (Redis, CDN) where read pressure is high
- Use Elasticsearch for text-based or fuzzy queries
- Service meshes (Istio, Linkerd) must handle retries, health checks, and circuit breaking

# =========== 📈 MONITORING & LOGGING

- Log using `loguru` with structured JSON output
- Centralize logs via CloudWatch or ELK stack
- Telemetry stack:
  - Metrics: Prometheus + Grafana
  - Traces: OpenTelemetry + Jaeger or X-Ray

# =========== 🧪 TESTING & COVERAGE

- Mandatory test types: ✅ Unit tests (mock I/O: RabbitMQ, S3, DBs) ✅ Endpoint tests (for each FastAPI route) ✅ Integration tests (multi-component flows)

- Test naming pattern: test\_\<function|class>\_\<scenario>

- Run tests with:

  > pytest && coverage report -m

- Minimum coverage: 90%

- CI must validate that the code runs **without live external dependencies**

# =========== 🧰 TYPE CHECKING

- Only Python 3.12+ is allowed
- All `src/` modules must have full type coverage
- `tests/` are excluded from `no-untyped-def`

Mypy configuration:

```ini
[mypy]
python_version = 3.12
disallow_untyped_defs = True

[mypy-tests.*]
disallow_untyped_defs = False
```

# =========== 📚 REFERENCES

- FastAPI → [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- FastStream → [https://faststream.dev](https://faststream.dev)
- OpenTelemetry → [https://opentelemetry.io/docs/instrumentation/python/](https://opentelemetry.io/docs/instrumentation/python/)
- Serverless Patterns → [https://serverlessland.com/patterns](https://serverlessland.com/patterns)
