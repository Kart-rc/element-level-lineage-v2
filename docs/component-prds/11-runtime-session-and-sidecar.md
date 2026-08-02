# C11 Integration Runtime Session Controller and Sidecar PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C11 |
| Status | Approved for implementation |
| Launch phase | Runtime gate after deterministic collection works |
| Criticality | P0 for runtime-enabled applications; production hard-deny is a launch security gate |
| Primary owner | Runtime evidence team |
| Required approvers | Architecture, application/test platform, privacy/security, operations, trust engine |
| Upstream dependencies | C01, C04-C06, registered integration tests, AppConfig, integration account identity |
| Downstream dependencies | C12-C13, C15, C17-C18 |
| Authoritative sources | AWS architecture §10 and privacy gates; element-level v2 R6/R8 |

## 2. Purpose and Outcomes

C11 creates bounded, signed integration-test sessions and operates a fail-open
sidecar that emits metadata-only boundary evidence. It proves which authorized
paths executed for one test/artifact and supports structural corroboration. It
does not capture payloads or prove internal transformation. Production is
denied by independent template, IAM, AppConfig, organization, validator, and
sidecar-attestation controls.

Measurable outcomes:

- Zero raw/reversible payload, body, header, credential, SQL parameter, or
  unbounded attribute content persists in transport, logs, evidence, or errors.
- Tests begin only after every expected sidecar is `READY`; terminal completeness
  reconciles every expected monotonic sequence and closing manifest.
- Missing sidecar/sequence/manifest, event/byte limit, or storage failure yields
  `INCOMPLETE`/`TRUNCATED`, never silent sampling or confidence promotion.
- 100% of production enablement/submission attempts are technically denied and
  audited; application availability never depends on collector health.

## 3. Scope and Non-Goals

### In scope

- Runtime request authorization, signed expiring session/grant, AppConfig
  control, expected-sidecar readiness barrier, sidecar collection, CloudWatch
  ingress validation, explicit Kinesis ordering, S3 persistence, drain/
  completeness, finally disable, expiry kill switch, and reconciliation.
- Metadata schemas/field paths/types, operation/direction, trace/test/artifact
  identity, session-scoped irreversible fingerprints for approved fields, and
  counts/windows/checksums.

### Non-goals

- Production field-level/runtime lineage collection.
- Capturing raw/encoded payloads, request/response bodies, headers, credentials,
  SQL values, exception payloads, or arbitrary logs.
- Proving transformation/derivational correctness or proving unexecuted paths do
  not exist.
- Failing application containers or business tests solely because the collector
  cannot collect evidence.
- Converting an observed service interaction into lineage by itself.

## 4. Actors and Use Cases

| Actor/component | Use case |
|---|---|
| C06 | Request named tests/session, wait for readiness, start tests, drain/disable |
| Test Automation Service | Attest registered integration test run and expected workloads/sidecars |
| Application sidecar | Observe allowlisted boundary metadata and emit ordered evidence fail-open |
| AppConfig validator | Permit only signed, expiring integration configuration |
| Runtime validator | Reject prohibited/invalid evidence and assign ordered stream partition |
| C13 | Use only `COMPLETE` evidence for bounded structural corroboration |
| Operator/security | Kill/expire session, investigate gaps/privacy/production attempts, reconcile |

## 5. Component Boundary

### Owned behavior

- `RuntimeEvidenceSession`, grants/keys/AppConfig profile, sidecar protocol,
  runtime envelope validator, Kinesis routing/correlation, completeness manifest,
  disable/expiry/kill/reconciliation.

### Inputs

- Registered test run/scenarios, application/repository/commit/artifact digest,
  expected sidecars/versions, environment, schema/field allowlist, budgets,
  fingerprint policy, context/test mappings.

### Outputs

- Immutable validated runtime evidence/sidecar manifests/session manifest,
  terminal status/completeness, coverage/gaps/privacy/audit and C13 reference.

### Forbidden behavior

- Issuing a session without registered test/artifact/environment match.
- Starting tests before all expected compatible sidecars report `READY`.
- Logging/storing/transporting raw or reversible content.
- Enabling in production or accepting production account/OU/environment evidence.
- Silently sampling/truncating when event/byte limits are reached.
- Marking `COMPLETE` before durable evidence, sequence, manifest, checksum, and
  disable confirmation.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C11-FR-001 | C11 must create a session only for a registered integration test run whose application, repository, commit, artifact digest, expected workloads, and environment exactly match C05/Test Automation evidence. | P0 |
| C11-FR-002 | The signed session must include session/test/application/repository IDs, commit/digest, environment exactly `integration`, start/expiry, expected sidecars/minimum versions, schema/field allowlist, maximum events/bytes, fingerprint and sampling/truncation policies. | P0 |
| C11-FR-003 | AppConfig validators must reject unsigned/expired/malformed/mismatched sessions and every production account, OU, environment, application template, or target. | P0 |
| C11-FR-004 | The sidecar must attest integration environment/workload/artifact/session identity, validate the signed grant, register version/capabilities, heartbeat, and report `READY`; C11 must require all expected sidecars ready before test start. | P0 |
| C11-FR-005 | The sidecar may emit only schema URN/hash, field path/logical type/nullability/presence, protocol/operation/direction, trace/span/test IDs, commit/digest, instrumentation version, session-keyed fingerprint where approved, observation count/window, monotonic sequence, and checksum. | P0 |
| C11-FR-006 | Runtime contracts/validators must reject raw or encoded values, payload/body, request/response body, headers, credentials/auth material, SQL parameters, payload-bearing exception text, reversible tokens, free-form logs, and arbitrary/generic attributes. | P0 |
| C11-FR-007 | Fingerprints must use a session-scoped keyed HMAC issued only to active integration sidecars; sensitive/low-cardinality fields are denied and the key becomes inaccessible after close/expiry. | P0 |
| C11-FR-008 | Every sidecar must assign a monotonic sequence to accepted local evidence and finish with a closing manifest containing first/last sequence, emitted/dropped/rejected counts, bytes, aggregate checksum, and terminal time. | P0 |
| C11-FR-009 | Sidecar instrumentation must be asynchronous/fail-open for the application; collector/transport failure must not fail the application container or alter payload/latency beyond approved budget. | P0 |
| C11-FR-010 | Sidecar evidence must enter allowlisted CloudWatch lineage log groups; a validator must authenticate/validate/deduplicate and explicitly assign Kinesis partition `sessionId#sidecarId` to preserve per-sidecar order. | P0 |
| C11-FR-011 | The validator must reject prohibited/mismatched/out-of-budget envelopes before Kinesis/S3, retaining only sanitized hash/reason/audit; identical duplicates are idempotent and conflicting same sequence is a conflict. | P0 |
| C11-FR-012 | Evidence must persist immutably in C12 before drain completion; C11 must reconcile registration, heartbeat, every monotonic sequence, closing manifest, counts/bytes/checksum, persistence, and expected sidecar set. | P0 |
| C11-FR-013 | A missing sequence/sidecar/manifest, checksum mismatch, incompatible sidecar, event/byte cap, expired session, or incomplete persistence must produce `INCOMPLETE` or `TRUNCATED` and prevent confidence promotion. | P0 |
| C11-FR-014 | C06/C11 must disable AppConfig in a finally path after tests or any failure/cancel/expiry, and independent session expiry must revoke grants/keys even if orchestration/control services fail. | P0 |
| C11-FR-015 | C11 must implement production hard-deny by omitting collector from production templates where possible, no production ingestion permission, AppConfig validation deny, Organizations/account policy deny, sidecar environment attestation, registered-test grant condition, and validator deny/audit. | P0 |
| C11-FR-016 | C11 must reconcile active/expired sessions, AppConfig state, grants/keys, expected sidecars, evidence/manifests, and C13 consumption and remediate/alert discrepancies. | P0 |
| C11-FR-017 | C11 output must label runtime evidence `EXECUTED_BOUNDARY_METADATA`; it must not assign derivational confidence or assert an edge from interaction alone. | P0 |
| C11-FR-018 | Sampling is disabled for Tier-1 runtime evidence at launch; any future sampling mode must be explicit in session/coverage, cannot silently activate on overload, and cannot yield `COMPLETE` for omitted required events. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C11-NFR-001 | Sidecar overhead must remain below 2% p95 CPU, 128 MiB memory, and 5 ms p95 boundary-call latency in the approved integration load fixture. | P0 |
| C11-NFR-002 | Runtime intake must handle a 10x incident-test storm and at least 10,000 events/second per Region with no silent loss; explicit truncation is allowed only by session cap. | P0 |
| C11-NFR-003 | Session control/intake must be 99.9% available monthly; expiry/production-deny remain effective during control-plane/Region failure. | P0 |
| C11-NFR-004 | 95% of terminal sessions must finish persistence/completeness/disable within five minutes after tests end; all must expire by signed deadline. | P0 |

## 7. Data and Durable State

`RuntimeEvidenceSession` contains all C11-FR-002 fields plus signing/key/grant/
AppConfig policy versions, state/transitions, sidecar registrations/heartbeats,
test start/end, sequence/manifests/persistence, status/reason, disable/expiry,
evidence/session-manifest references, and correlation.

`RuntimeEvidenceEnvelope` is closed (`additionalProperties: false`) and contains
session/sidecar/event/monotonic sequence, allowed context/field/operation fields,
observation/fingerprint where approved, observed time/instrumentation version,
and envelope checksum. It has no generic map.

`SidecarClosingManifest` includes identity/version/digest, sequence range,
attempted/emitted/rejected/dropped counts by reason, bytes, rolling checksum,
heartbeats, close time/status, and signature.

DynamoDB holds sessions/leases/idempotency/sequence/completeness/AppConfig state;
C12 S3 holds validated evidence and immutable manifests; AppConfig holds only
signed bounded session configuration; KMS/Secrets grants the ephemeral HMAC key.

## 8. Interfaces and Contracts

- `POST /v1/runtime-sessions` accepts registered test/context reference,
  expected sidecars, allowlist/budgets/policies, expected environment, and
  idempotency; returns session/status, never the HMAC key.
- `POST /v1/runtime-sessions/{id}/sidecars:register|heartbeat|close` uses workload
  identity and signed grant, exact sidecar/artifact/version.
- `POST /v1/runtime-sessions/{id}:testsStarted|testsEnded|cancel|kill|reconcile`
  requires expected state/version and authorized caller.
- Sidecar writes closed JSON lines to dedicated CloudWatch lineage log stream;
  subscription invokes validator. Validator returns accepted/rejected status
  operationally and writes Kinesis with explicit partition key.
- Kinesis consumer validates per-sidecar sequence/idempotency and writes C12
  partitioned S3 evidence/manifests.
- Events expose readiness, test barrier, sequence gap, truncation, disabled,
  terminal completeness, privacy/production denial, and reconciliation.

## 9. Processing and State Model

```text
REQUESTED -> ENABLING -> READY -> COLLECTING -> DRAINING
          -> DISABLED -> COMPLETE
```

Terminal alternatives: `INCOMPLETE`, `TRUNCATED`, `FAILED`, `EXPIRED`,
`CANCELLED`.

1. Validate registered test/context/integration environment and create signed
   session/expiry/budgets; issue scoped AppConfig/grants/key.
2. Sidecars attest/register/heartbeat. `READY` requires exact expected set and
   compatible versions/digest.
3. Authorize test start; collect allowed evidence asynchronously and sequence.
4. Validate/deduplicate/rate-budget/partition/persist evidence.
5. On test end/failure/cancel/expiry, enter drain; request closing manifests and
   wait only until deadline.
6. Execute disable/revoke/key-inaccessibility in finally and verify AppConfig.
7. Reconcile expected/received sequences/manifests/counts/checksums/persistence/
   disable and select terminal completeness.
8. Emit immutable session manifest to C13; only `COMPLETE` is eligible for
   structural corroboration.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `SESSION_NOT_INTEGRATION` | `DETERMINISTIC_INVALID` security | Deny/alert/audit; no config/grant/key |
| `TEST_OR_ARTIFACT_MISMATCH` | `DETERMINISTIC_INVALID` | Reject session/sidecar; no ready |
| `SIDECAR_MISSING_OR_INCOMPATIBLE` | `INCOMPLETE` | Do not start or terminal incomplete by policy/deadline |
| `RUNTIME_EVIDENCE_PRIVACY_VIOLATION` | `DETERMINISTIC_INVALID` security | Reject before stream/store; sanitize, revoke/kill by policy |
| `SEQUENCE_CONFLICT_OR_GAP` | `CONFLICT`/`INCOMPLETE` | Preserve checksums/reconcile; no complete/promotion |
| `EVENT_OR_BYTE_LIMIT` | `INCOMPLETE` | Mark `TRUNCATED`; stop/close, no silent sampling |
| `TRANSPORT_OR_STORE_THROTTLED` | `TRANSIENT` | Bounded buffer/retry; on deadline incomplete, app unaffected |
| `DISABLE_UNCONFIRMED` | `INCOMPLETE` security-critical | Retry/expiry/alert; no complete |
| `PRODUCTION_ENABLE_OR_SUBMIT` | `DETERMINISTIC_INVALID` security | Multi-layer deny and immediate audit/alert |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C11-SEC-001 | Session creation, AppConfig, sidecar, CloudWatch, validator, Kinesis, C12, and KMS grants must use mutually constrained test/workload/account/environment identities and least-privilege roles. | P0 |
| C11-SEC-002 | Runtime schema and validation must fail closed on all forbidden or unknown fields, encoded/reversible variants, payload-bearing error text, and generic maps; logs retain sanitized field path/hash/reason only. | P0 |
| C11-SEC-003 | Session HMAC keys must be short-lived/nonexportable where supported, scoped to active integration workloads/window, unavailable after terminal/expiry, and never stored in session/evidence/logs. | P0 |
| C11-SEC-004 | Production deny must be tested at template, IAM/SCP/resource policy, AppConfig validator, sidecar attestation, session grant, validator, and C12 bucket policy layers. | P0 |
| C11-SEC-005 | Session/config/grant/key/evidence access/kill/denial changes must be CloudTrail/data-event audited with sensitive-content redaction. | P0 |
| C11-SEC-006 | Runtime evidence must use TLS/private endpoints, KMS separated by environment/data class, retention/deletion, domain ABAC, and no broad production role access. | P0 |

## 12. Scale, Performance, and Availability

- Runtime Kinesis/control capacity is isolated from repository event queues.
  Partition key `sessionId#sidecarId` preserves local order and distributes
  sessions; hot-sidecar/session cap is explicit.
- Sidecar uses bounded in-memory/disk spool, backpressure, and fail-open drop
  accounting; it never blocks/changes application payload processing.
- CloudWatch subscription/validator/Kinesis/S3 quotas are load-tested above 10x
  expected integration storm. Event/byte cap yields `TRUNCATED` before service
  exhaustion.
- Expiry uses trusted service-side time and independent revocation path. Warm-
  Region recovery never enables a production grant and preserves terminal/
  incomplete evidence within RPO/RTO.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C11-OBS-001 | Session state/latency/terminal | application/test/artifact/environment/status/reason | P0 |
| C11-OBS-002 | Sidecar expected/registered/ready/heartbeat/version | session/workload/sidecar; barrier/stale alert | P0 |
| C11-OBS-003 | Evidence accepted/rejected/duplicate/conflict | schema/field/reason/sidecar/session; privacy alert | P0 |
| C11-OBS-004 | Sequence/gap/manifest/checksum/completeness | sidecar/session/test; any gap alert | P0 |
| C11-OBS-005 | Event/byte/spool/drop/truncation | sidecar/session/account | P0 |
| C11-OBS-006 | AppConfig/grant/key/disable/expiry | state/age/account; unconfirmed/overdue alert | P0 |
| C11-OBS-007 | Production-deny attempts | layer/account/OU/workload/caller; immediate security alert | P0 |
| C11-OBS-008 | Sidecar/application overhead | version/archetype/CPU/memory/latency | P1 |

Metrics reconcile attempted = emitted + locally rejected + dropped-with-reason;
validator received = accepted + duplicate + rejected + conflict; accepted = S3
persisted + outstanding until deadline. C17 shows completeness and gaps.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C11-AC-001 | Given a valid integration test/artifact, session becomes `READY` only after every expected compatible sidecar attests; premature test start is denied/audited. |
| C11-AC-002 | Given allowed metadata, per-sidecar sequences arrive through explicit partitioning, persist, reconcile to closing manifests/checksum, disable, and yield `COMPLETE`. |
| C11-AC-003 | Given raw/encoded payload, body/header/credential/SQL/error content, unknown field, or generic map, validator denies before stream/store and retained telemetry is sanitized. |
| C11-AC-004 | Given missing sequence/sidecar/manifest, conflicting sequence, cap, or store deadline, session is incomplete/truncated and C13 cannot promote confidence. |
| C11-AC-005 | Given test/application/sidecar/transport failure or cancel, application/test behavior is not altered by collector and finally disables/expires grants/key. |
| C11-AC-006 | Given enable/submission from every production-control layer, 100% are denied/audited and no runtime evidence reaches Kinesis/S3. |
| C11-AC-007 | Given complete runtime evidence for a candidate, C13 may strengthen structural confidence only; derivational remains unchanged absent allowed derivational evidence. |
| C11-AC-008 | The 10x storm/overhead/recovery tests meet C11 NFRs with exact sequence/count/byte reconciliation and no silent sample/loss. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C11-CT-001 | State/contract | Valid/invalid sessions and all transitions | Validate/transition | Exact state machine/conditions/idempotency | Transition report |
| C11-CT-002 | Readiness | Expected, missing, wrong version/digest/environment sidecars | Register/start tests | Ready only exact set; premature denied | Session/timeline |
| C11-CT-003 | Privacy schema | Every forbidden key, encoded variant, error text, generic map | Emit/validate | Reject before Kinesis/S3; sanitized audit | Validator/store scan |
| C11-CT-004 | Sequence | Ordered, duplicate, out-of-order, gap, conflict sequences | Ingest/drain | Dedup/order/reconcile; gap/conflict incomplete | Sequence report |
| C11-CT-005 | Manifest | Matching/missing/mismatched counts/bytes/checksum | Close/drain | Complete only matching all | Session manifest |
| C11-CT-006 | Limits | At/over event and byte caps; transport pressure | Collect | Explicit truncate/incomplete, no silent sampling | Metrics/manifest |
| C11-CT-007 | Fail-open/finally | Sidecar/validator/stream/store/test failure and cancel | Execute | App unaffected; finally disable/revoke/expire; status exact | App/session/audit |
| C11-CT-008 | HMAC/privacy | Eligible, low-cardinality, sensitive field; key expiry/reuse | Fingerprint | Scoped irreversible only; denied fields/key reuse absent | Key/validator evidence |
| C11-CT-009 | Production hard-deny | Attempt each seven control layers | Enable/emit/store | Every attempt denied/audited; zero evidence persisted | Security test matrix |
| C11-CT-010 | Identity/idempotency | Duplicate/conflicting event/session/sidecar evidence | Execute | Same effect or conflict; no overwrite/cross-session mix | State/evidence history |
| C11-CT-011 | Confidence boundary | Complete/incomplete evidence on known transform | Reconcile | Structural-only promotion for complete; derivational unchanged | C13 result golden |
| C11-CT-012 | Load/recovery | 10x/10k events sec, hot sidecar, restart/Region failure | Execute/recover | NFRs, exact reconciliation, expiry/deny survive | Load/DR report |

## 16. Integration Obligations

- **INT-070 C01/C05/C06↔C11:** registered test/context/identity/digest/expected
  sidecars create one exact integration-only workflow/session.
- **INT-071 AppConfig↔C11:** signed validation, readiness enable, finally disable,
  expiry/kill, invalid and production targets pass.
- **INT-072 Sidecar↔CloudWatch/validator/Kinesis/C12:** allowed evidence,
  partition/order/dedup/gap/cap/privacy/persistence/manifests interoperate.
- **INT-073 C11↔C13:** complete versus incomplete/truncated and structural-only
  confidence semantics pass.
- **INT-074 C11↔C15/C17:** session/test/artifact/evidence/coverage/gaps/privacy/
  terminal/timeline are reviewable with ABAC.
- **INT-075 C11↔C18:** production hard-deny at every layer, audit/alarms/runbooks,
  secret/privacy scans, and kill exercises pass.
- **INT-076 C11↔C03/C06 replay/redrive:** duplicate/replay/stale callbacks never
  create a second session or re-enable terminal/expired collection.
- **INT-077 C11↔C18 load/DR:** 10x storm, quota/sidecar/control/Region failures,
  expiry and recovery meet NFR/RPO/RTO with no production exposure.

## 17. Definition of Done

- Session/control APIs, AppConfig profile/validators, Go sidecar, closed runtime
  schemas, CloudWatch validator, explicit Kinesis partitioning, S3 consumer,
  manifests/completeness/finally/expiry/reconciliation are implemented.
- C11 P0 requirements and C11-CT-001 through C11-CT-012 pass.
- INT-070 through INT-077 pass in production-shaped integration and denied
  production accounts.
- Privacy scans prove no forbidden/raw/reversible content across source, logs,
  stream, stores, metrics, traces, DLQ/quarantine, and errors.
- Production-deny matrix, fail-open, incomplete no-promotion, 10x storm,
  overhead, expiry, load, and DR reports meet every criterion.
- Session/privacy/sequence/manifest/kill/disable/production-attempt/restore
  runbooks and alarms are exercised with real IDs.

## 18. Implementation Notes

```text
contracts/schemas/runtime/
services/runtime-controller/
services/runtime-validator/
workers/runtime-evidence-consumer/
sidecars/lineage-observer/
infra/lib/constructs/runtime-sessions.ts
infra/lib/constructs/runtime-stream.ts
docs/runbooks/runtime-evidence/
tests/contract/runtime/
tests/integration/runtime/
tests/security/runtime/
tests/load/runtime/
```

Use Go 1.24 for the sidecar, TypeScript 5 for control/validator/IaC, Python 3.12
for large completeness/reconciliation if needed. Use AWS AppConfig validators,
CloudWatch Logs subscriptions, and Kinesis Data Streams; do not replace the
selected runtime path with a generic Kafka bus.

Build order: closed contracts/privacy tests; session/deny/AppConfig; sidecar
attestation/allowlist/HMAC/sequence/manifest/fail-open; validator/partition/
consumer; drain/finally/completeness; C13; load/security/DR. Default production
template omits the sidecar and all production paths deny grants/ingestion.

## 19. Traceability

| Source decision | C11 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Bounded integration-only session/readiness | C11-FR-001 through C11-FR-004 | C11-CT-001/002 | INT-070/071 |
| Metadata-only/sequence/manifest/fail-open | C11-FR-005 through C11-FR-013/017 | C11-CT-003 through C11-CT-008, C11-CT-010, C11-CT-011 | INT-072/073/074 |
| Finally disable/expiry/production deny | C11-FR-014 through C11-FR-016; C11-SEC-001-006 | C11-CT-007/009 | INT-071/075/076 |
| Scale/overhead/recovery | C11-NFR-001 through C11-NFR-004 | C11-CT-012 | INT-077; runtime enterprise gate |
