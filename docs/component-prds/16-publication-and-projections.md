# C16 Fenced Publication and Graph/Search Projections PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C16 |
| Status | Approved for implementation |
| Launch phase | Required before approved lineage becomes queryable |
| Criticality | P0; protects active graph from concurrent, stale, partial, or unapproved mutation |
| Primary owner | Lineage graph publication team |
| Required approvers | Architecture, graph/search, data foundation, governance, operations/DR |
| Upstream dependencies | C01, C06, C12, C15 approved manifest, C14 artifact compatibility |
| Downstream dependencies | C17-C18 |
| Authoritative sources | AWS architecture §§6.12-6.13, 12.2-15; shared state/error model |

## 2. Purpose and Outcomes

C16 is the only service allowed to make approved lineage active. It validates an
immutable accepted manifest, conditionally reserves one application/environment
against the expected prior graph version, issues a lease and fencing token,
stages Neptune into an immutable target-version namespace, verifies it, and
atomically advances the active pointer. It then rebuilds/refreshes OpenSearch and
records a projection watermark. S3 accepted manifests remain authority.

Measurable outcomes:

- Zero unapproved, partial, stale-worker, or expected-version-conflicting graph
  mutation becomes active.
- Concurrent publication for one application/environment produces at most one
  active pointer advance; losing proposal rebases/supersedes without data loss.
- A worker with an expired/lower fencing token cannot commit even if its staging
  work finishes later.
- Neptune/OpenSearch can be emptied and rebuilt from accepted manifests with
  matching node/edge/evidence/version checksums within RPO/RTO.

## 3. Scope and Non-Goals

### In scope

- Accepted-manifest and artifact/version validation, publication reservation/
  lease/fencing, immutable graph export/stage/verify, atomic active pointer,
  proposal callback/state record, OpenSearch projection/watermark, redrive/
  rebase/supersede, retention/cleanup, rebuild/reconciliation/DR.

### Non-goals

- Creating/approving/correcting proposals (C15).
- Letting UI/users/workers directly mutate active Neptune/OpenSearch.
- Treating Neptune/OpenSearch as evidence or accepted-state authority.
- In-place mutation of the namespace addressed by the active pointer.
- Rolling back accepted S3 manifests to hide bad publication; rollback is a new
  governed active pointer/publication from an accepted manifest.

## 4. Actors and Use Cases

| Actor/component | Use case |
|---|---|
| C15 | Request publication of exact approved proposal/manifest/base graph |
| Publication worker | Stage/verify immutable graph target under lease/fence |
| Projection worker | Build OpenSearch from newly active graph/manifest and report watermark |
| C17 query layer | Resolve active pointer/version and expose projection lag |
| Operator | Redrive failed publish, reconcile pointer/namespaces/watermarks, rebuild |
| DR operator | Restore/fail over from replicated manifests/state and verify checksums |

## 5. Component Boundary

### Owned behavior

- `PublicationReservation`, `ActiveGraphPointer`, immutable Neptune graph version,
  graph export, OpenSearch projection/watermark and rebuild/reconcile state.

### Inputs

- C15 approved proposal/version/decision and C12 `AcceptedLineageManifest` exact
  reference/checksum/Object Lock status.
- Expected prior graph version, application/environment, artifact binding,
  publication/projection policy and idempotency.

### Outputs

- Target/active graph version, publication result/audit, proposal callback,
  projection watermark/status, rebuild/reconciliation reports.

### Forbidden behavior

- Accepting draft/rejected/superseded/unlocked/mismatched manifest.
- Mutating active version namespace while readers use it.
- Advancing pointer without valid current reservation/lease/fencing token and
  expected prior graph version.
- Letting OpenSearch success define graph approval/authority.
- Serving a projection version as current without its active pointer/watermark.
- Deleting old graph versions before retention/rollback/audit/rebuild policy.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C16-FR-001 | C16 must accept only a C15 `APPROVED` exact proposal version/checksum and C12 Object-Locked `AcceptedLineageManifest` whose reviewer/decision/application/environment/base/artifact/policy signatures validate. | P0 |
| C16-FR-002 | Publication idempotency must include application, environment, proposal/version, manifest checksum, expected prior graph version, and publication policy; identical requests return prior/resume state and conflicting content is rejected. | P0 |
| C16-FR-003 | C16 must conditionally acquire an application/environment publication reservation requiring the active pointer equal the expected prior graph version and no incompatible live reservation. | P0 |
| C16-FR-004 | Reservation must issue immutable target graph version, owner/attempt, lease expiry, monotonically increasing fencing token, expected prior graph version, manifest reference/checksum and state. | P0 |
| C16-FR-005 | Lease renewal must be conditional on same owner/attempt/fencing/current state and bounded; loss/expiry prevents commit even if worker continues local/staging work. | P0 |
| C16-FR-006 | C16 must generate/verify a checksummed graph export from the accepted manifest and stage Neptune nodes/edges/evidence into an immutable target-version namespace; it must never mutate the active namespace. | P0 |
| C16-FR-007 | Staging must be idempotent by target/entity identity and detect conflicting duplicate properties/edges rather than last-write-win. | P0 |
| C16-FR-008 | Before activation, C16 must verify manifest/export/staged graph versions, canonical URNs, application/environment, expected prior/target, node/edge/evidence/confidence counts, required indexes, referential integrity and checksums/sample/full validation by policy. | P0 |
| C16-FR-009 | One DynamoDB transaction must recheck reservation owner/unexpired lease/fencing token, active pointer expected prior, target verification and approved proposal, then advance `ActiveGraphPointer` and record publication/proposal transition. | P0 |
| C16-FR-010 | A worker with stale/lower fencing token, expired lease, changed active pointer, superseded proposal or mismatched manifest must be unable to advance state. | P0 |
| C16-FR-011 | After pointer activation, C16 must build/refresh OpenSearch only from the newly active version/manifest, atomically expose an index alias/version, and record monotonic `ProjectionWatermark` with graph version/count/checksum/time. | P0 |
| C16-FR-012 | OpenSearch failure/lag after graph activation must not roll back approved Neptune pointer; it must expose lag/error, retry idempotently, and make C17 use documented graph/search freshness behavior. | P0 |
| C16-FR-013 | Publication retry/redrive must resume verified stages using exact references/fence semantics; partial target namespace is never active and may be rebuilt/cleaned only by governed retention procedure. | P0 |
| C16-FR-014 | If expected prior graph changed, C16 must stop with version conflict and request C15 rebase/supersede; it must not merge/rebase graph implicitly. | P0 |
| C16-FR-015 | C16 must retain publication attempts, reservations, graph exports, accepted manifests, prior graph versions, pointer history, projection watermarks, failures and audit according to rollback/governance policy. | P0 |
| C16-FR-016 | C16 must reconcile accepted/approved requests, reservations/leases, target namespaces, active pointers, proposal states, OpenSearch aliases/watermarks and C17 observed versions and repair/alert discrepancies. | P0 |
| C16-FR-017 | C16 must rebuild Neptune/OpenSearch from C12 accepted manifests and active pointer history, validate exact counts/checksums/versions, and prove query readiness before traffic/alias cutover. | P0 |
| C16-FR-018 | Rollback must select a previously accepted immutable manifest or new corrected proposal through the same reservation/fencing/verification protocol and create a new pointer/audit event. | P0 |
| C16-FR-019 | Graph/search schema/index evolution must be versioned, backward/query compatible or use parallel target namespaces/indexes and verified cutover; no in-place incompatible migration. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C16-NFR-001 | 95% of approved changes up to 100,000 affected edges must be Neptune-active and OpenSearch-queryable within 60 seconds; larger baselines publish within measured size-class SLO. | P0 |
| C16-NFR-002 | C16 must support 100 concurrent different-application publications and serialize conflicting same-application publication without global lock. | P0 |
| C16-NFR-003 | Active pointer/reservation service must be 99.99% available monthly; publication failure must leave prior active graph readable. | P0 |
| C16-NFR-004 | Projection rebuild/failover must meet 15-minute RPO/four-hour RTO with exact accepted-manifest/pointer/count/checksum reconciliation. | P0 |

## 7. Data and Durable State

`PublicationReservation` includes application/environment, proposal/version/
checksum, accepted manifest ref/checksum/signature, expected prior/target graph,
owner/attempt, fencing token, lease start/expiry/renewals, state, graph export/
verification/projection refs, errors and audit.

`ActiveGraphPointer` includes application/environment/domain, active graph
version, accepted manifest/export refs/checksums, publication/fencing token,
expected prior, activation time, proposal/decision/artifact/policy versions,
Neptune namespace, OpenSearch projection watermark/status and pointer version.

`GraphExportManifest` lists canonical nodes/edges/evidence/confidence/version
files with shard refs/checksums/counts, graph schema/index version, application/
environment/base/target and aggregate checksum.

`ProjectionWatermark` includes graph version, OpenSearch index/alias/schema,
expected/actual document counts/checksum, started/completed, lag/status/error,
retry/rebuild and audit.

C12 stores accepted/export/rebuild/audit. DynamoDB stores reservation/pointer/
watermark/idempotency/history with PITR/conditional transactions. Neptune stores
versioned immutable namespaces; OpenSearch stores versioned indexes/aliases.

## 8. Interfaces and Contracts

- `POST /v1/publications` accepts approved proposal/decision/manifest refs,
  expected prior, policy and idempotency; returns publication/target/status.
- `POST /v1/publications/{id}:renew|redrive|cancel|reconcile` requires expected
  state/fencing token/role/reason.
- Internal stage APIs register graph export, staging, verification, pointer commit
  and projection result with exact attempt/fence/checksum.
- `GET /v1/graph-pointers/{environment}/{application}`, publication history,
  projection watermarks and rebuild status provide authoritative read metadata.
- `POST /v1/projections:rebuild` accepts accepted-manifest set/active history,
  target Region/schema and dry-run/verification/cutover policy.
- Events: `publication.reserved|staged|verified|active|failed|conflicted`,
  `projection.started|ready|lagging|failed|rebuilt`, `graph.pointer.changed`.

## 9. Processing and State Model

```text
REQUESTED -> RESERVING -> EXPORTING -> STAGING -> VERIFYING
          -> COMMITTING -> GRAPH_ACTIVE -> PROJECTING -> ACTIVE
```

Alternatives: `DUPLICATE`, `VERSION_CONFLICT`, `FAILED_REDRIVABLE`,
`CANCELLED_BEFORE_COMMIT`, `PROJECTION_LAGGING`, `SUPERSEDED`.

1. Verify approved decision/manifest/Object Lock/signature/artifact/base/policy.
2. Conditional reserve and issue target/lease/fencing token.
3. Generate/read graph export and stage immutable target namespace under fence
   heartbeats; idempotently validate conflicts.
4. Verify target/manifest/count/checksum/referential/index invariants.
5. Transactionally recheck fence/lease/prior/proposal and advance pointer/state.
6. Notify C15 graph active, emit pointer event, project OpenSearch and watermark.
7. Reconcile C17 visibility; complete or keep projection lagging/retry status.

Before step 5, failure leaves active pointer unchanged. After step 5, graph is
approved active; projection failure is a separate recoverable read-model state.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `MANIFEST_OR_APPROVAL_INVALID` | `DETERMINISTIC_INVALID` | No reservation/stage; audit exact mismatch |
| `EXPECTED_PRIOR_GRAPH_CHANGED` | `CONFLICT` | Stop; rebase/supersede via C15 |
| `RESERVATION_BUSY` | `TRANSIENT`/`CONFLICT` | Wait/defer or surface competing proposal; no global lock |
| `LEASE_EXPIRED_OR_STALE_FENCE` | `CONFLICT` | Deny renew/result/commit; reconcile target |
| `TARGET_CONTENT_CONFLICT` | `CONFLICT` | Fail verification; preserve diagnostics, no active |
| `TARGET_VERIFICATION_FAILED` | `DETERMINISTIC_INVALID` | No pointer advance; retain report/target under policy |
| `NEPTUNE_THROTTLED_OR_UNAVAILABLE` | `TRANSIENT` | Bounded retry/redrive before commit; prior active remains |
| `POINTER_TRANSACTION_CONFLICT` | `CONFLICT` | Re-read current; no blind retry across changed expected prior |
| `OPENSEARCH_PROJECTION_FAILED_OR_LAGGING` | `INCOMPLETE` projection | Graph remains active; alert/retry/rebuild/watermark visible |
| `REBUILD_MISMATCH` | `DETERMINISTIC_INVALID` | No cutover; retain old serving projections/report |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C16-SEC-001 | Only C16 publication roles may write target Neptune namespaces, graph pointers or OpenSearch indexes/aliases; C15/UI/analyzers/query users have no mutation permission. | P0 |
| C16-SEC-002 | Publication roles must be application/environment/stage scoped, use private networking/TLS/KMS/Secrets, exact C12 prefixes/Neptune/OpenSearch resources where possible, and separate reserve/stage/commit/operate duties. | P0 |
| C16-SEC-003 | Sensitive metadata fields/evidence references must retain ABAC/redaction in graph/search; projection must not denormalize unauthorized evidence bodies or payloads. | P0 |
| C16-SEC-004 | Accepted manifest/signature/Object Lock, fence/pointer transaction, target counts/checksums and image/IaC versions must be audited for every attempt/cutover/rollback/rebuild. | P0 |
| C16-SEC-005 | Cancel/redrive/rebuild/cleanup/rollback/schema migration requires scoped operator role, reason, expected state/fence, dry-run/verification and immutable audit; no direct console mutation is an approved path. | P0 |

## 12. Scale, Performance, and Availability

- Partition publication locks by organization/environment/application; unrelated
  apps publish concurrently. Domain-wide proposal uses a manifest of app-scoped
  publications plus a governed aggregate visibility contract, not a global
  mutable transaction.
- Graph exports shard by node/edge hash; Batch prepares/validates large exports.
  Neptune bulk/Gremlin/OpenCypher loader choice is benchmarked, idempotent and
  versioned. OpenSearch bulk indexes versioned targets then atomically moves alias.
- Active graph pointer reads use strongly consistent DynamoDB where decision
  requires. C17 caches only with pointer version/watermark and bounded TTL.
- Neptune writer/read replicas and OpenSearch Multi-AZ remain serving prior
  active versions during publication failure. Rebuild/failover uses warm Region
  C12/DynamoDB replicated state and IaC.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C16-OBS-001 | Publication state/latency/counts | application/domain/size/policy/Region | P0 |
| C16-OBS-002 | Reservation/lease/fencing/conflict | app/token/age/owner/reason | P0 |
| C16-OBS-003 | Stage/verify node-edge-evidence counts/checksums | target/base/schema/status | P0 |
| C16-OBS-004 | Pointer transaction/active version | app/env/old/new/proposal/fence | P0 |
| C16-OBS-005 | Projection watermark/lag/failure | graph/index/alias/schema/seconds | P0 |
| C16-OBS-006 | Orphan target/stale worker/reconciliation | namespace/proposal/state/action | P0 |
| C16-OBS-007 | Neptune/OpenSearch capacity/query/build/cost | cluster/domain/app/operation | P1 |
| C16-OBS-008 | Rebuild/DR RPO/RTO/count/checksum | Region/manifest set/status | P0 |

C17 displays active graph and projection watermark/lag. Reconciliation asserts
one active pointer target exists/verified, proposal state matches, and no stale
fence changed it.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C16-AC-001 | Given exact approved Object-Locked manifest/base, C16 reserves/stages/verifies/transactionally advances one active pointer and projects matching OpenSearch watermark. |
| C16-AC-002 | Given two concurrent proposals for the same expected prior, at most one activates; the other receives version conflict and requires C15 rebase/supersede. |
| C16-AC-003 | Given worker lease expiry/newer fencing token, old worker cannot renew/register/commit even after staging completes. |
| C16-AC-004 | Given partial Neptune write/count/checksum/referential failure, target never becomes active and prior pointer remains serving. |
| C16-AC-005 | Given OpenSearch failure after pointer advance, Neptune graph remains active, lag is visible, C17 uses documented behavior, and idempotent retry reaches exact watermark. |
| C16-AC-006 | Given duplicate/redrive, completed verified stages reuse exact outputs without duplicate graph version/pointer/proposal transition. |
| C16-AC-007 | Given empty/corrupt Neptune/OpenSearch operational projections, rebuild from accepted manifests/pointer history matches nodes/edges/evidence/checksums before cutover. |
| C16-AC-008 | Load/failure/Region recovery meet NFR/RPO/RTO with prior active availability and exact proposal/manifest/pointer/projection reconciliation. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C16-CT-001 | Contract/security | Approved versus draft/rejected/unlocked/mismatched manifests | Request | Only exact approved accepted manifest reserves | Validation/audit report |
| C16-CT-002 | Happy path | Small/large accepted manifest/base | Publish | Exact target/count/checksum/pointer/proposal/watermark | Publication golden |
| C16-CT-003 | Concurrency | Two same-app proposals same prior; many different apps | Publish concurrently | One same-app winner; unrelated parallel; no global lock | State/history/load |
| C16-CT-004 | Fencing | Lease expiry/renewal race/new worker/old late callback | Stage/commit | Only current fence operates/commits | Token/state/audit |
| C16-CT-005 | Partial/conflict | Missing/conflicting node/edge, checksum/count/ref integrity failure | Stage/verify | No activation; prior serving; diagnostics retained | Verification report |
| C16-CT-006 | Pointer transaction | Expected prior/proposal/reservation changes at commit | Commit | Atomic success or conflict, never partial pointer/state | DynamoDB transaction history |
| C16-CT-007 | OpenSearch lag | Fail/throttle midway after graph active | Project/query/retry | Visible lag, no rollback, exact eventual alias/watermark | Watermark/query report |
| C16-CT-008 | Idempotency/redrive | Duplicate request/fail at each stage/redrive | Publish | One target/active transition; valid stage reuse | Attempt/stage refs |
| C16-CT-009 | Authorization/privacy | UI/analyzer/cross-domain/direct console and sensitive fields | Mutate/project/query | Mutation denied/audited; ABAC/redaction preserved | IAM/security scan |
| C16-CT-010 | Reconciliation/cleanup | Orphan targets/stale reservations/mismatched proposal/watermark | Reconcile/cleanup | Exact safe action; retained versions not deleted early | Reconciliation report |
| C16-CT-011 | Rebuild/rollback | Empty projections, prior accepted manifest, bad candidate rebuild | Rebuild/cutover/rollback | Verified exact cutover; mismatch stays isolated; rollback new event | Rebuild/rollback report |
| C16-CT-012 | Load/chaos/DR | 100 concurrent apps, large graphs, service/Region failure | Publish/recover | NFR/RPO/RTO/prior availability/exact reconciliation | Load/chaos/DR report |

## 16. Integration Obligations

- **INT-110 C12/C15↔C16:** Object-Locked accepted manifest/approval/checksum/base/
  artifact validation, exact access and lifecycle pass.
- **INT-111 C06↔C16:** workflow submit/retry/redrive/cancel/reconcile uses exact
  idempotency/stage/fence/result and no duplicate state.
- **INT-112 C16↔DynamoDB/Neptune:** reservation/lease/fence/stage/verify/atomic
  pointer/concurrent/stale worker/partial failure behavior pass.
- **INT-113 C16↔OpenSearch:** active-version bulk build/alias/watermark/lag/retry/
  schema/ABAC behavior passes.
- **INT-114 C16↔C17:** active pointer, bounded graph and search versions,
  projection lag/error and query cutover semantics are consistent.
- **INT-115 C16↔C15:** proposal publishing/active/failed/version-conflict callbacks
  preserve state and drive rebase/supersede/redrive exactly.
- **INT-116 C16↔C18 security/operations:** IAM/network/KMS/audit/alarms/runbooks/
  reconciliation/cleanup/capacity/cost/chaos pass.
- **INT-117 C12/C16/C18 DR:** restore accepted manifests/pointer history and
  rebuild Neptune/OpenSearch within RPO/RTO with exact checksums before traffic.

## 17. Definition of Done

- Publication contracts/services/IaC implement manifest validation, app-scoped
  reservation/lease/fencing, export, immutable target, verification, atomic
  pointer, proposal callback, OpenSearch projection/watermark, reconciliation,
  rebuild/rollback and telemetry.
- C16 P0 requirements and C16-CT-001 through C16-CT-012 pass.
- INT-110 through INT-117 pass with production-shaped data/state/graph/search/
  review/query/operations components.
- Concurrency/stale fence/partial failure/redrive tests prove no unapproved or
  partially active graph and prior active remains available.
- Security/privacy proves only C16 mutation, stage-role separation, ABAC, no
  payload denormalization, audited operations and no direct-console path.
- Load/chaos/rebuild/DR reports meet NFR/RPO/RTO and exact accepted manifest/
  proposal/pointer/node/edge/evidence/watermark reconciliation.
- Publication/fence/version conflict/projection lag/rebuild/rollback/cleanup/DR
  runbooks and alarms are exercised with real IDs.

## 18. Implementation Notes

```text
contracts/schemas/publication/
services/publication-controller/
workers/graph-exporter/
workers/neptune-projector/
workers/opensearch-projector/
workers/projection-reconciler/
infra/lib/stacks/projection-stack.ts
infra/lib/constructs/publication-state.ts
docs/runbooks/publication/
tests/contract/publication/
tests/integration/publication/
tests/load/publication/
tests/chaos/publication/
```

Use TypeScript 5 for controller/transaction/IaC and Python 3.12 for graph export/
projection/rebuild workers. Benchmark Neptune bulk loader versus idempotent
transactions and pin one versioned strategy per graph schema/size. OpenSearch
uses versioned indexes plus atomic alias cutover; never rebuild in place.

Build order: contracts/state/fencing; export; target stage/verify; pointer txn;
C15 callback; OpenSearch/watermark/C17; reconcile/redrive; rebuild/rollback;
load/security/DR. Feature canary publishes a nonserving application/domain and
verifies before allowing production active pointer transitions.

## 19. Traceability

| Source decision | C16 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Approved manifest plus fenced publication | C16-FR-001-010/013-015/018 | C16-CT-001-006/008/011 | INT-110-112/115; publication gate |
| Rebuildable Neptune/OpenSearch projections | C16-FR-006-008/011-012/016-019 | C16-CT-005/007/010-012 | INT-113/114/117 |
| Concurrency/performance/availability | C16-NFR-001-004 | C16-CT-003/012 | INT-112/116; enterprise gate |
| Security/privacy/audit/operations | C16-SEC-001-005 | C16-CT-009-012 | INT-116/117; security/DR gates |
