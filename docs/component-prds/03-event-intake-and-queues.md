# C03 Event Intake, Normalization, and Priority Queues PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C03 |
| Status | Approved for implementation |
| Launch phase | Foundation |
| Criticality | P0; every asynchronous trigger and replay enters through C03 |
| Primary owner | Lineage control-plane team |
| Required approvers | Architecture, security, operations, C06 workflow owner |
| Upstream dependencies | C01 contracts, C02 source events, SCM/deployment/test/review/publication sources |
| Downstream dependencies | C04, C06, C14, C18 |
| Authoritative sources | AWS architecture §§5-6, 9.1, 14-17; component design §§6, 10-12 |

## 2. Purpose and Outcomes

C03 is the durable front door for lineage work. It authenticates producers,
validates and normalizes events, computes immutable event-type-specific
idempotency identities, records every routing decision, and uses EventBridge
plus priority SQS queues to absorb spikes without losing work or allowing
baseline/backfill to starve deployed-artifact decisions.

Measurable outcomes:

- Accept a 10,000-event burst without loss and sustain 100 normalized events per
  second under production-like tests.
- Every accepted source delivery maps to exactly one visible outcome:
  normalized/routed, duplicate, recorded coalesced, quarantined, or DLQ.
- Duplicate delivery creates one business trigger while preserving attempt
  count and source delivery audit.
- Tier-1 queue-age and routing SLOs remain within policy during concurrent
  baseline/backfill load.

## 3. Scope and Non-Goals

### In scope

- HTTP/EventBridge/API destinations for governed SCM, deployment, inventory,
  baseline, runtime, review, publication, reconciliation, and operator replay.
- Producer authentication/authorization, source delivery verification,
  schema/size validation, normalization, correlation enrichment, and archive.
- Idempotency, duplicate/conflicting duplicate handling, and narrowly governed
  coalescing.
- Content-based EventBridge routing and priority SQS queues/DLQs.
- Queue admission, per-domain partition attributes, replay/redrive controls,
  and end-to-end intake audit/telemetry.

### Non-goals

- Orchestrating long-running work or choosing analyzer steps (C06).
- Reclassifying repositories or deciding no impact (C04/C05).
- Exactly-once transport; delivery is assumed at least once.
- Dropping older events merely because a newer event exists.
- Embedding repository content, evidence packages, or large manifests in event
  or workflow payloads.

## 4. Actors and Use Cases

| Actor/system | Use case |
|---|---|
| SCM/deployment system | Submit immutable commit/artifact triggers |
| C02 | Emit inventory snapshot/reconciliation triggers |
| Application owner/C17 | Request a baseline or record a proposal decision |
| C11 | Emit runtime session lifecycle/evidence-ready events |
| C16 | Submit/emit publication lifecycle events |
| Operator | Inspect quarantine/DLQ, replay archive range, or govern redrive |
| C06 | Consume prioritized work with normalized contracts and idempotency state |

Key scenarios include duplicate webhook delivery, out-of-order commits,
deployment without digest, a never-deployed PR commit superseded by a newer PR
commit, emergency hotfix deployment, poison message, queue spike, and governed
archive replay after a repaired consumer defect.

## 5. Component Boundary

### Owned behavior

- Ingress endpoint/rule and producer verification.
- `EventEnvelope` normalization and correlation initialization.
- Idempotency record and normalized-event immutable reference.
- EventBridge bus/archive/rules, SQS priority queues, DLQs, queue policies, and
  routing decision records.

### Inputs

- Typed producer event or S3 reference/checksum for an oversized body.
- Producer registration, contract version, routing/admission policy.
- Optional trusted correlation parent.

### Outputs

- Normalized `EventEnvelope` reference and route/priority/admission attributes.
- Duplicate/coalesced/quarantine/DLQ/replay records and metrics.

### Forbidden behavior

- Forming an idempotency key with an empty commit SHA, artifact digest,
  environment, organization, repository, or event type.
- Treating coalescing as deduplication or coalescing a deployed artifact.
- Routing an event before source authentication and contract validation.
- Using EventBridge as worker backpressure or SQS as content authority.
- Redriving around current validation, authorization, idempotency, or routing.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C03-FR-001 | C03 must authenticate/authorize the producer, verify source delivery integrity where supported, and map it to a registered organization/account before normalization. | P0 |
| C03-FR-002 | Every accepted event must use the versioned `EventEnvelope` and typed data contract, with event ID/type/time, organization, source delivery, correlation, schema, and immutable content reference/checksum. | P0 |
| C03-FR-003 | SCM idempotency must include organization, repository, commit SHA, event type, analyzer version, and policy version; a missing commit SHA must be quarantined. | P0 |
| C03-FR-004 | Deployment idempotency must include organization, repository, artifact digest, environment, event type, analyzer version, and policy version; a missing digest/environment must be quarantined. | P0 |
| C03-FR-005 | Identical duplicate business identity/content must return the prior normalized outcome and increment delivery attempts without emitting a second business trigger. | P0 |
| C03-FR-006 | The same business identity with a different content checksum must enter `DUPLICATE_CONFLICTING_CONTENT`; C03 must preserve both source deliveries and must not last-write-win. | P0 |
| C03-FR-007 | Coalescing may supersede only an older, never-deployed PR commit under versioned policy after both identities and a `COALESCED_BY` relation are recorded; every deployed artifact and hotfix must remain actionable. | P0 |
| C03-FR-008 | C03 must route normalized events through content-based EventBridge rules and retain them in an EventBridge archive for governed replay. | P0 |
| C03-FR-009 | C03 must provide separate SQS queues/DLQs for Tier-1 incremental, standard incremental, baseline, backfill/reconciliation, LLM-limited residual, and runtime-correlation work. | P0 |
| C03-FR-010 | Routing must assign queue, priority, domain/admission key, enqueue time, schema/policy versions, and immutable normalized-event reference; no large body may be copied into SQS. | P0 |
| C03-FR-011 | Queue admission must reserve Tier-1 capacity, rate-limit per domain, and expose rejection/defer decisions without deleting the accepted event. | P0 |
| C03-FR-012 | Every queue consumer contract must assume duplicates/out-of-order delivery and include business idempotency identity and expected state/version. | P0 |
| C03-FR-013 | Schema/auth/privacy/missing-identity failures must be deterministic quarantine; transient service failures use bounded retry; repeated consumer failures enter the queue-specific DLQ. | P0 |
| C03-FR-014 | Archive replay and DLQ redrive must be scoped, authorized, rate-limited, audited, and pass through current validation, routing, idempotency, and admission policy. | P0 |
| C03-FR-015 | C03 must record an outcome for every ingress delivery, including rejected authentication attempts using only sanitized source metadata. | P0 |
| C03-FR-016 | Event contract/routing policy changes must be versioned, canaried, and reversible without reinterpreting archived event bytes. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C03-NFR-001 | C03 must accept a burst of 10,000 valid normalized triggers without loss and sustain 100 triggers/second for 30 minutes in the production-like load environment. | P0 |
| C03-NFR-002 | Valid ingress-to-queue latency must be below 2 seconds p95 and 5 seconds p99 under normal load. | P0 |
| C03-NFR-003 | Intake and queue infrastructure must be Multi-AZ and achieve 99.95% monthly availability for accepted-event durability. | P0 |
| C03-NFR-004 | Event archive/normalized content and idempotency state must recover within C18's 15-minute RPO and four-hour RTO with no duplicate business effects. | P0 |

## 7. Data and Durable State

`ProducerRegistration` contains producer ID/type/account/organization, auth
method/key/certificate reference, allowed event types/schemas, network/source
conditions, max size/rate, owner, effective/expiry, and policy version.

`IdempotencyRecord` contains business key hash, event type, immutable identity
parts (redacted as policy requires), normalized content checksum/reference,
first/current source delivery IDs, attempt count, status, route, run ID if
created, lease/TTL for processing only, and immutable audit references.

`RoutingDecision` contains event ID/business identity, routing policy version,
matched rule, queue/DLQ ARN alias, priority, domain/admission key, decision
reason, enqueue timestamp, deferral, and checksum.

`QuarantineRecord` and `RedriveRequest` follow the shared state/error model.
EventBridge archive preserves original normalized events under retention policy;
C12 S3 stores oversized source/normalized content and audit-grade copies.

## 8. Interfaces and Contracts

### Ingress

- `POST /v1/events/{producerId}` for registered webhook/API producers.
- EventBridge PutEvents for governed AWS producers with source/detail-type
  resource policies.
- Internal commands such as `POST /v1/baseline-runs` produce the same normalized
  event path rather than directly invoking C06.

Responses:

- `202 ACCEPTED`: normalized and durably recorded for routing.
- `200 DUPLICATE`: prior result/run reference returned.
- `202 QUARANTINED`: authenticated producer but deterministic content failure;
  only when producer policy allows asynchronous correction.
- `400/401/403/413`: malformed, unauthenticated/unauthorized, or oversized
  request, with sanitized audit.
- `409 DUPLICATE_CONFLICTING_CONTENT`.
- `429/503`: request not durably accepted; producer may retry same delivery ID.

### Queue message

```json
{
  "eventRef": "s3://...#sha256=...",
  "eventId": "...",
  "eventType": "artifact.deployed",
  "businessKeyHash": "...",
  "priority": "TIER1",
  "domainAdmissionKey": "payments",
  "routingPolicyVersion": "routing-v1",
  "enqueuedAt": "2026-08-02T14:31:24Z",
  "correlation": {"collectionRunId": "...", "traceId": "..."}
}
```

The message is below 64 KiB by policy. Consumers fetch/verify referenced content
and conditionally transition the idempotency/work record before acting.

### Replay/redrive

Requests require source (archive or DLQ), event time/IDs, reason, target policy
version, maximum count/rate, dry-run summary, authorization, and expiry. C03
emits start/progress/complete/cancel audit and links new attempts to originals.

## 9. Processing and State Model

```text
RECEIVED -> AUTHENTICATED -> VALIDATED -> NORMALIZED
         -> IDEMPOTENCY_DECIDED -> ARCHIVED -> ROUTED -> ENQUEUED
```

Alternative outcomes: `REJECTED_AUTH`, `QUARANTINED`, `DUPLICATE`,
`DUPLICATE_CONFLICT`, `COALESCED`, `DEFERRED`, and `DLQ`.

Processing order:

1. Enforce network/request size/rate and verify producer signature/role.
2. Parse only the registered schema/version and reject unsafe/unknown major
   versions or generic payload maps.
3. Resolve organization/repository/source identity and normalize timestamps,
   correlation, and S3 references/checksums.
4. Validate event-type immutable fields before hashing the business key.
5. Conditional idempotency write determines new, same duplicate, conflicting
   duplicate, or in-progress outcome.
6. Evaluate a possible coalescing policy separately and persist relation.
7. Put normalized envelope on EventBridge and verify success; archive/rule
   policies route to SQS and operational consumers.
8. Persist routing/admission outcome and expose it to C17/C18.

Out-of-order events are retained with occurrence/receipt times. Ordering is
resolved by C06/C14 against immutable artifact/effective versions, not by
discarding at intake.

## 10. Failure Semantics

| Code | Class | Behavior |
|---|---|---|
| `PRODUCER_AUTH_FAILED` | `DETERMINISTIC_INVALID` | Reject; sanitized security audit/metric; no event body logging |
| `EVENT_SCHEMA_INVALID` | `DETERMINISTIC_INVALID` | Quarantine/reject by producer contract; no queue |
| `IMMUTABLE_IDENTITY_MISSING` | `DETERMINISTIC_INVALID` | Quarantine; never compute an empty/shared key |
| `DUPLICATE_CONFLICTING_CONTENT` | `CONFLICT` | Preserve both; alert owner; no second trigger |
| `EVENTBRIDGE_THROTTLED` | `TRANSIENT` | Bounded retry before accepted outcome; source may safely redeliver |
| `QUEUE_SEND_FAILED` | `TRANSIENT` | Event remains archived/visible; route retry/reconciliation |
| `ADMISSION_DEFERRED` | `INCOMPLETE` operational | Keep durable event and retry admission; expose age |
| `CONSUMER_REPEATED_FAILURE` | `POISON_REPEATED` | DLQ, alarm/runbook, governed redrive |
| `REPLAY_POLICY_REJECTED` | `DETERMINISTIC_INVALID` | No replay; retain request/audit reason |

No 2xx accepted response is returned until the event/idempotency outcome is
durable enough to recover and route/reconcile it.

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C03-SEC-001 | Every producer must use an approved signature, IAM/resource policy, mTLS, or OIDC mechanism bound to allowed organization/account/event types. | P0 |
| C03-SEC-002 | Ingress, EventBridge, SQS, archive, S3 references, idempotency, and DLQs must use TLS, KMS, least-privilege resource policies, private endpoints where applicable, and separate producer/consumer roles. | P0 |
| C03-SEC-003 | Event schemas must prohibit raw payload values, credentials, tokens, request/response bodies, generic headers, and arbitrary attribute maps. | P0 |
| C03-SEC-004 | Logs/DLQs/quarantine must store only allowlisted metadata and checksums; a security-invalid body must not be copied to broad operational stores. | P0 |
| C03-SEC-005 | Replay/redrive/coalescing/routing policy changes must require scoped operator authorization, reason, expiry where applicable, and immutable audit. | P0 |

## 12. Scale, Performance, and Availability

Queues:

1. Tier-1 incremental: reserved consumer capacity; oldest age P0 alert.
2. Standard incremental: may borrow unused baseline capacity through C06.
3. Baseline: cannot consume Tier-1 reservations.
4. Backfill/reconciliation: lowest priority, explicit admission.
5. LLM residual: separately rate/cost limited.
6. Runtime correlation: isolated from repository-control spikes.

Use EventBridge for routing, not backlog. SQS Standard provides scale; every
consumer is idempotent. Message retention must exceed maximum outage/recovery
and approval-independent processing window. DLQ retention must allow governed
investigation. Queue policies require exact sources/accounts and encryption.

Load tests combine 10,000 immediate events, 30-minute sustained input, 10%
duplicates, 1% invalid, domain skew, baseline backlog, and consumer slowdown.
Pass requires no accepted-event loss, exact outcome counts, and Tier-1 SLOs.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C03-OBS-001 | Ingress count/latency/outcome | producer, event type, organization, schema/policy | P0 |
| C03-OBS-002 | Duplicate/conflict/coalesced/quarantine | event type, reason, owner; conflict/security alerts | P0 |
| C03-OBS-003 | Queue depth/oldest age/throughput | priority, domain, queue/DLQ; Tier-1 SLO alert | P0 |
| C03-OBS-004 | Routing/admission decisions | rule/policy version, matched route, deferred reason | P0 |
| C03-OBS-005 | Archive replay/DLQ redrive | actor, scope, rate, success/failure, duplicate effect | P0 |
| C03-OBS-006 | EventBridge/SQS quota/cost | account, bus/queue, API, payload bytes | P1 |

Metrics reconcile `received = rejected + quarantined + duplicate + conflict +
coalesced + accepted`; accepted reconciles to route/deferred/DLQ and eventual
C06 run/no-impact outcome.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C03-AC-001 | Given two identical SCM deliveries, C03 records two attempts and one normalized business trigger/run identity. |
| C03-AC-002 | Given a deployment event without artifact digest or environment, C03 quarantines it with `IMMUTABLE_IDENTITY_MISSING` and creates no shared/empty idempotency key. |
| C03-AC-003 | Given the same business key with different content, C03 records conflict and neither overwrites nor emits a second business trigger. |
| C03-AC-004 | Given an older undeployed PR and a newer PR under an enabled policy, coalescing records both/relation; given any deployed/hotfix artifact, no coalescing removes its lineage decision. |
| C03-AC-005 | Given concurrent baseline/backfill and a 10,000-event spike, all accepted events reconcile and Tier-1 latency/age remain within C03 and platform SLOs. |
| C03-AC-006 | Given a poison consumer event, it reaches the correct DLQ after bounded attempts; governed redrive revalidates/idempotently completes after repair. |
| C03-AC-007 | Given archive replay of already completed events, attempt/audit counts increase but business runs/proposals/publications are not duplicated. |
| C03-AC-008 | Given unauthenticated or payload-bearing input, C03 rejects it, emits sanitized security telemetry, and no prohibited body appears in logs/archive/queue/DLQ. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C03-CT-001 | Contract | Valid typed event for every source/type | Validate/normalize | Canonical `EventEnvelope` and checksum | Golden envelopes |
| C03-CT-002 | Contract/negative | Unknown major, missing required, arbitrary map, oversized inline body | Submit | Exact rejection/quarantine; no route | Validation/audit |
| C03-CT-003 | Security | Bad signature/role/source account | Submit | Reject before body normalization; sanitized alert | Security audit |
| C03-CT-004 | Idempotency | Same SCM/deployment delivery twice | Submit concurrently | One business trigger, two attempts, prior result returned | DynamoDB/event counts |
| C03-CT-005 | Conflict | Same business key, different checksum | Submit | Conflict record; zero second route | Conflict evidence |
| C03-CT-006 | Boundary | Missing commit; missing digest/environment | Submit | `IMMUTABLE_IDENTITY_MISSING`; no empty key | Quarantine/key scan |
| C03-CT-007 | Coalescing | Older/newer undeployed PR then deployed hotfix | Apply policy | Only PR may coalesce; hotfix always queued | Relation/routing records |
| C03-CT-008 | Routing | One event per type/priority/domain | Route | Exactly expected queue/rule attributes | Rule assertion/report |
| C03-CT-009 | Failure/DLQ | Consumer fails beyond receive policy | Consume | Correct DLQ/alert/runbook; original event preserved | Attempt/DLQ history |
| C03-CT-010 | Replay/redrive | Completed, quarantined, and repaired poison events | Replay/redrive scoped set | Current validation/policy; idempotent results; full audit | Replay report |
| C03-CT-011 | Privacy | Forbidden fields/secret-bearing errors | Submit and inspect stores | Rejected/redacted; prohibited terms/content absent | Store/log privacy scan |
| C03-CT-012 | Load/fairness | 10,000 burst plus sustained/domain-skew/baseline backlog | Run load | No loss; exact outcome counts; Tier-1 and throughput SLOs | Load report/dashboard |

## 16. Integration Obligations

- **INT-013 C02↔C03:** snapshot/reconciliation events are checksummed,
  idempotent, archived, and routed.
- **INT-014 External producers↔C03:** SCM/deployment/test events pass source
  authentication, versioned contract, duplicate, conflict, and missing-identity
  cases.
- **INT-015 C03↔C04:** repository triggers reach classification with the exact
  normalized identity/policy and preserve UNKNOWN/quarantine outcomes.
- **INT-016 C03↔C06:** every accepted route becomes one workflow/no-impact
  decision despite duplicate and out-of-order delivery.
- **INT-017 C03↔C14:** every deployed artifact, including hotfix, reconciles to a
  lineage binding/alert; coalescing cannot hide it.
- **INT-018 C03↔C18:** queue/DLQ/archive metrics reconcile; replay/redrive,
  outage, and cross-Region recovery preserve business idempotency.
- **INT-019 C03↔C17:** users/operators can see intake, duplicate, quarantine,
  deferred, queue, DLQ, and replay status without direct AWS console access.

## 17. Definition of Done

- All producer/event schemas, source policies, normalization examples, routes,
  queues, DLQs, archive, idempotency, and replay APIs are implemented as IaC.
- C03 P0 requirements and C03-CT-001 through C03-CT-012 pass.
- INT-013 through INT-019 pass with deployed production-shaped components.
- The load/fairness report proves exact event reconciliation, 10,000 burst,
  sustained throughput, and Tier-1 protection.
- Security/privacy evidence proves producer isolation, forbidden-field denial,
  encrypted least privilege, sanitized failures, and replay audit.
- DLQ/redrive, EventBridge replay, admission, source auth, and Region recovery
  runbooks are exercised and linked to alarms.

## 18. Implementation Notes

```text
contracts/schemas/events/
contracts/examples/events/
services/event-normalizer/
services/event-normalizer/src/idempotency/
infra/lib/constructs/event-bus.ts
infra/lib/constructs/priority-queues.ts
infra/lib/constructs/event-archive.ts
tests/contract/events/
tests/integration/event-intake/
tests/load/event-intake/
tests/chaos/event-intake/
```

Implement control services in TypeScript 5 on Lambda. Use EventBridge custom
bus/archive and SQS Standard queues. DynamoDB conditional writes hold
idempotency/routing state. Put normalized/oversized immutable envelopes in C12
S3. Do not use FIFO assumptions or introduce Kafka/MSK for initial scope.

Build order: schemas/source verification; normalization/idempotency; bus/archive;
queues/DLQs/rules; admission/coalescing; replay/redrive; load/security/recovery.
Canary routing policy versions by producer/event type and compare outcomes
before activation.

## 19. Traceability

| Source decision | C03 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| EventBridge routes; SQS buffers | C03-FR-008 through C03-FR-012 | C03-CT-008/009/012 | INT-016/018; foundation gate |
| At-least-once/idempotency and immutable identities | C03-FR-003 through C03-FR-007 | C03-CT-004 through C03-CT-007 | INT-014/016/017 |
| No silent event/drop; replay/redrive | C03-FR-013 through C03-FR-015 | C03-CT-009/010 | INT-018/019; chaos gate |
| 10,000 burst and priority isolation | C03-NFR-001/002; C03-FR-009/011 | C03-CT-012 | Enterprise load/fairness gate |
| Security/privacy | C03-SEC-001 through C03-SEC-005 | C03-CT-002/003/011 | INT-014/018; security gate |
