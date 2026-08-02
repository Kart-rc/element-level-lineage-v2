# C02 Source Adapters and Repository Inventory PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C02 |
| Status | Approved for implementation |
| Launch phase | Foundation and baseline |
| Criticality | P0; classification and baseline completeness depend on a trustworthy estate snapshot |
| Primary owner | Lineage integrations team |
| Required approvers | Architecture, SCM/platform owners, Test Automation Service owner, security |
| Upstream dependencies | C01 contracts/identity; enterprise SCM, deployment, catalog/schema, native-lineage, CloudWatch, and test APIs |
| Downstream dependencies | C03-C06, C14, C17-C18 |
| Authoritative sources | AWS architecture §§7-8, 13-17; component design §§6 and 10 |

## 2. Purpose and Outcomes

C02 discovers the complete enterprise estate relevant to lineage and produces
immutable, reconciliable inventory snapshots. It separates discovery from
eligibility: every repository remains visible even if C04 later excludes it
from standalone analysis.

Measurable outcomes:

- 100% of repositories returned by configured enterprise SCM organizations are
  represented in a snapshot or in an explicit source failure record.
- Every business-application baseline pins one `RepositoryInventorySnapshot`
  with per-source completeness and source watermark.
- Scheduled source-to-snapshot reconciliation finds no unexplained missing,
  duplicate, or stale repository/deployment record.
- A 10,000 repositories inventory completes within 60 minutes under approved
  source quotas, excluding a declared upstream outage.

## 3. Scope and Non-Goals

### In scope

- Versioned adapters for Test Automation Service, SCM, deployment/artifact
  systems, service catalog, schema/contract/catalog systems, Spark/dbt/Airflow
  native-lineage catalogs, test/scenario systems, and selected CloudWatch
  deployment/interaction context.
- Paginated/rate-limited discovery, source checkpoints, watermarks, resumable
  collection, canonical ID resolution through C01, and immutable snapshots.
- Application/repository association evidence with ranked provenance.
- Completeness, freshness, source health, and reconciliation reports.
- Active, archived, transferred, forked, and renamed repository observations.

### Non-goals

- Classifying a repository or assigning Lane A/B/C (C04).
- Treating a CloudWatch interaction as a lineage edge.
- Cloning repositories or parsing their source (C08).
- Mutating SCM/catalog/deployment systems.
- Hiding an unavailable source by returning an apparently complete empty list.

## 4. Actors and Use Cases

| Actor | Use case |
|---|---|
| Application owner | Select an application and see which repositories/evidence formed its baseline |
| Platform operator | Configure a source, observe lag/errors, resume a checkpoint, and reconcile coverage |
| Adapter developer | Add a typed source/version without changing downstream snapshot semantics |
| C04 classifier | Receive every repository plus deterministic metadata/evidence |
| C05 context builder | Receive application, deployment, schema, native job, test, and interaction associations |
| Auditor | Reproduce what sources returned at a historical inventory watermark |

Representative scenarios:

1. Inventory all enterprise organizations, then select active repositories for
   one Test Automation Service business application.
2. Discover a documentation-named repository containing authoritative Avro and
   OpenAPI contracts without deciding its classification.
3. Resume after SCM throttling without duplicating pages or mixing watermarks.
4. Mark one schema catalog `PARTIAL` while retaining complete SCM/deployment
   content and preventing a false complete baseline.
5. Reconcile a deployment digest that is absent from the prior snapshot.

## 5. Component Boundary

### Owned behavior

- Source credentials/configuration references and adapter execution.
- Normalized observations and immutable `RepositoryInventorySnapshot`.
- Per-source checkpoints, health/freshness/completeness, and reconciliation.

### Inputs

- Baseline/scheduled inventory request with organization/application scope.
- Source registry and adapter versions.
- C01 registry version and canonical identity service.
- Read-only external APIs/log queries under governed limits.

### Outputs

- Snapshot S3 URI/checksum and `inventory.snapshot.created` event.
- Source status/checkpoint, reconciliation result, and explicit coverage gaps.

### Forbidden behavior

- Excluding a repository by name, inferred type, lack of deployment, or missing
  ownership.
- Advancing a source watermark before its page/results are durably included.
- Storing source credentials or raw application payload/log bodies.
- Combining pages captured under incompatible source snapshot tokens without a
  visible consistency qualification.
- Reporting `COMPLETE` when a required source/page failed or expired.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C02-FR-001 | C02 must inventory every configured SCM organization/repository, including active, archived, transferred, renamed, forked, and inaccessible-with-reason records. | P0 |
| C02-FR-002 | C02 must query the Test Automation Service for application, repository, scenario, owner, and domain associations and preserve source IDs/evidence. | P0 |
| C02-FR-003 | C02 must collect immutable commit SHAs, deployment IDs, artifact digests, environments, deploy times, and application bindings from governed deployment sources. | P0 |
| C02-FR-004 | C02 must inventory authoritative schemas/contracts/catalog objects and native Spark/dbt/Airflow jobs/runs without interpreting their lineage. | P0 |
| C02-FR-005 | C02 may collect allowlisted CloudWatch deployment and service-interaction context, but must label it `INTERACTION_CONTEXT` and never emit a lineage edge. | P0 |
| C02-FR-006 | Every adapter must expose source/version, requested scope, start/end watermark, pages/items, retry/throttle state, collection time, and one of `COMPLETE`, `PARTIAL`, `UNAVAILABLE`, or `STALE`. | P0 |
| C02-FR-007 | A `RepositoryInventorySnapshot` must be immutable, checksummed, source-by-source complete, and bound to a C01 registry version. | P0 |
| C02-FR-008 | C02 must normalize source IDs through C01 while preserving native IDs and unresolved/ambiguous identity outcomes. | P0 |
| C02-FR-009 | Adapter paging must be resumable from a durable checkpoint and must not advance the source watermark until the corresponding normalized observations are durably staged. | P0 |
| C02-FR-010 | Duplicate source observations with identical identity/content must collapse deterministically; conflicting content for the same source identity/watermark must enter `CONFLICT`. | P0 |
| C02-FR-011 | Required-source failure must propagate a snapshot coverage gap and prevent `COMPLETE`; optional-source failure must be visible with its policy designation. | P0 |
| C02-FR-012 | C02 must rank application/repository association evidence: governed catalog or Test Automation ownership, deployment binding, explicit contract/config reference, observed interaction, then inference requiring review. | P0 |
| C02-FR-013 | Scheduled reconciliation must compare source counts/IDs/watermarks with snapshots and emit missing, unexpected, duplicate, stale, and changed observations. | P0 |
| C02-FR-014 | Adapter contracts must be typed/versioned and must reject unknown major versions or arbitrary property maps. | P0 |
| C02-FR-015 | Source configuration changes must be versioned and effective-dated; a snapshot must pin one configuration version per source. | P0 |
| C02-FR-016 | C02 must support incremental inventory events while retaining scheduled full inventory as the completeness oracle. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C02-NFR-001 | A 10,000-repository full inventory must complete within 60 minutes under approved source quotas and retain a source-segmented duration report. | P0 |
| C02-NFR-002 | Adapter concurrency must obey configured per-source/account rate limits and honor `Retry-After` without starving other sources. | P0 |
| C02-NFR-003 | Snapshot publication must be 99.9% available monthly, excluding a declared required-source outage that correctly produces `PARTIAL`/`UNAVAILABLE`. | P0 |
| C02-NFR-004 | No source page acknowledged as checkpointed may be lost after process/Region recovery within C18 RPO/RTO. | P0 |

## 7. Data and Durable State

`SourceRegistration`:

- source ID/type/account/organization, adapter/schema versions, owner.
- credential secret reference and cross-account role ARN, never secret value.
- required/optional policy by inventory purpose.
- scopes, allowlisted fields/log groups, rate/concurrency limits.
- watermark/checkpoint semantics, freshness threshold, retention class.
- effective/expiry and configuration checksum.

`SourceCollectionAttempt`:

- inventory run/source/config version, request scope, attempt and lease.
- start/end watermark or snapshot token, current page/checkpoint.
- page/item/dedup/conflict counts, rate/throttle metrics.
- status/error and staged evidence references.

`RepositoryInventorySnapshot` conforms to the contract catalog and includes:

- organization plus inventory watermark/version.
- repositories with native/canonical IDs, immutable HEAD, lifecycle state, URL
  metadata, ownership/application evidence, manifests/descriptors references.
- deployed artifacts/environments, schemas/contracts/catalog/native jobs,
  test/scenario mappings, and interaction-context references.
- source statuses/checksums/counts and global completeness summary.

S3 is authoritative for snapshots/staged pages; DynamoDB holds registration,
checkpoint, snapshot pointer, and reconciliation indexes.

## 8. Interfaces and Contracts

### Start inventory

`POST /v1/inventory-runs` accepts organization, optional application/domain,
purpose (`BASELINE`, `SCHEDULED_FULL`, `RECONCILIATION`, `INCREMENTAL_REFRESH`),
required watermark, source policy/config version, and idempotency key. It
returns run ID and status URI; C06 normally invokes it.

### Adapter interface

```text
describe() -> adapter capabilities/schema/watermark model
open(scope, configVersion, priorCheckpoint?) -> snapshot token/checkpoint
readPage(token, checkpoint, limit) -> observations, nextCheckpoint, source metadata
close(token) -> final watermark/count/checksum
health() -> authorization, quota, schema compatibility, freshness
```

Observations are typed (`RepositoryObserved`, `DeploymentObserved`,
`SchemaObserved`, `NativeJobObserved`, `TestScenarioObserved`,
`InteractionObserved`) and wrapped in an `EvidenceReference` after staging.

### Snapshot publication

Publication requires all configured adapters terminal, normalized/staged page
checksums verified, completeness calculated, and a conditional snapshot-pointer
write. C02 emits `inventory.snapshot.created` with immutable S3 reference,
checksum, status, organization/application, source watermarks, and correlation.

## 9. Processing and State Model

```text
REQUESTED -> SOURCE_PLANNED -> COLLECTING -> NORMALIZING
          -> RECONCILING -> SNAPSHOT_WRITING -> PUBLISHED
```

Alternative outcomes are `PARTIAL`, `UNAVAILABLE`, `STALE`, `FAILED`, and
`CANCELLED`; the snapshot itself uses source status rather than pretending a
partial run is absent.

Algorithm:

1. Validate request/config and pin C01/source config versions.
2. Plan adapters and required/optional designation.
3. Acquire per-source lease; open a source-consistent token where available.
4. Page under rate limits. Stage raw allowlisted metadata and normalized
   observations with checksums; then conditionally advance checkpoint.
5. Resolve canonical IDs in C01 batches. Preserve unknown/ambiguous results.
6. Deduplicate by source-native immutable identity and content checksum; record
   conflicting observations separately.
7. Close adapter, validate counts/watermark/checksum, and assign source status.
8. Reconcile cross-source associations under precedence without deciding
   repository class.
9. Write immutable snapshot, verify checksum/read-back, advance latest pointer,
   and emit event.

Resume starts from the last durably acknowledged page. If a source token
expires, the adapter restarts a new attempt and either proves snapshot
consistency or marks the result `PARTIAL`/`STALE`; it never splices silently.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `SOURCE_THROTTLED` | `TRANSIENT` | Honor retry hint/jitter; retain checkpoint; isolate source |
| `SOURCE_AUTH_DENIED` | `DETERMINISTIC_INVALID` | Mark source unavailable, alert owner, no credential details in logs |
| `SOURCE_SCHEMA_INCOMPATIBLE` | `DETERMINISTIC_INVALID` | Quarantine adapter/source version; do not publish complete |
| `SOURCE_PAGE_MISSING` | `INCOMPLETE` | Mark partial and reconcile missing range |
| `SOURCE_TOKEN_EXPIRED` | `INCOMPLETE` | Restart consistent attempt or publish visible stale/partial status |
| `IDENTITY_AMBIGUOUS` | `CONFLICT` | Preserve observation and candidates for downstream review |
| `OBSERVATION_CONFLICT` | `CONFLICT` | Preserve both checksums/source metadata; no last-write-wins |
| `CHECKPOINT_WRITE_FAILED` | `TRANSIENT` | Retry before acknowledging page; duplicate reread is idempotent |
| `SNAPSHOT_CHECKSUM_FAILED` | `DETERMINISTIC_INVALID` | Do not advance pointer or emit success event |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C02-SEC-001 | Adapters must use short-lived read-only credentials from governed cross-account roles or Secrets Manager references with source/scope least privilege. | P0 |
| C02-SEC-002 | SCM checkout credentials, payload/log bodies, source tokens, and secrets must not appear in snapshots, logs, metrics, events, or exception text. | P0 |
| C02-SEC-003 | CloudWatch queries must use explicit allowlisted accounts/log groups/fields and retain query/audit metadata; free-form production log export is prohibited. | P0 |
| C02-SEC-004 | Source registrations, role assumption, configuration changes, inventory requests, snapshot reads, and reconciliation actions must be audited. | P0 |
| C02-SEC-005 | Snapshot and staging prefixes must use KMS, TLS-only/private access, organization/domain authorization, retention, and access logging. | P0 |

## 12. Scale, Performance, and Availability

- Planning size: 10,000 repositories, 10,000+ daily deployment observations,
  six initial archetypes, and hundreds of schema/native/test sources.
- Source tasks run independently so one slow adapter does not serialize all
  inventory; concurrency remains below source and account quotas.
- Pages are bounded by count and byte size. Large source results are S3 staged,
  not returned in Step Functions state.
- Inventory fairness reserves capacity for Tier-1 deployment refresh while a
  scheduled full scan runs.
- A source registration has circuit-breaker thresholds to avoid repeated
  authorization/schema failures; opening the breaker emits a P0 coverage alert.
- Multi-AZ control state, S3 cross-Region replication, checkpoint recovery, and
  snapshot restore follow C18's 15-minute RPO/four-hour RTO.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C02-OBS-001 | Inventory run duration/status/counts | source, organization, application, purpose; alert required-source failure | P0 |
| C02-OBS-002 | Source freshness/watermark lag | source/account/config; alert past governed threshold | P0 |
| C02-OBS-003 | Page throughput/throttle/retry | source/account/adapter version | P0 |
| C02-OBS-004 | Snapshot coverage | repositories, deployments, schemas, native jobs, tests; complete/partial/unavailable/stale | P0 |
| C02-OBS-005 | Reconciliation differences | missing/unexpected/duplicate/conflict/stale by source and owner | P0 |
| C02-OBS-006 | Cost | API calls, log bytes scanned, compute/storage by source/domain | P1 |

C17 exposes snapshot version, source status, missing evidence, and run timeline.
C18 dashboards link alarms to source-specific runbooks and last good watermark.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C02-AC-001 | Given a 10,000-repository SCM fixture with pagination, renames, transfers, archives, and forks, a full run publishes exactly one observation per source-native identity and matches source counts/checksum. |
| C02-AC-002 | Given one required schema source fails after page N, the snapshot is `PARTIAL`, completed source content remains available, the missing range is explicit, and baseline completion is not falsely reported. |
| C02-AC-003 | Given throttling and process restart, C02 resumes from the last durable checkpoint, rereads at most the unacknowledged page, and produces the same snapshot checksum as uninterrupted collection. |
| C02-AC-004 | Given an observed interaction between services, the snapshot labels it context; no candidate lineage edge is emitted. |
| C02-AC-005 | Given ambiguous C01 aliases, both candidates/evidence remain in the snapshot and C04 receives an explicit identity gap. |
| C02-AC-006 | Given a deployment absent from the previous snapshot, scheduled reconciliation emits the exact missing artifact/environment decision and starts governed refresh through C03. |
| C02-AC-007 | Given invalid source authorization/schema, C02 does not retry wastefully or leak credentials; it records deterministic status, owner action, metric, and audit. |
| C02-AC-008 | The production-like load test satisfies C02-NFR-001/002 with no dropped page, lost checkpoint, or unexplained reconciliation difference. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C02-CT-001 | Adapter contract | Valid/invalid responses for every adapter version | Describe/open/read/close | Typed normalized observations; invalid major rejected | Contract report/examples |
| C02-CT-002 | Unit/paging | 3 pages plus duplicate item | Collect | All pages once logically; duplicate collapsed by checksum | Page/checkpoint trace |
| C02-CT-003 | Failure/restart | Crash after stage before checkpoint | Resume | Page may reread; snapshot content remains single/idempotent | Attempt and checksum history |
| C02-CT-004 | Rate limit | Source emits 429/Retry-After | Collect concurrently | Hint honored; other sources continue; no busy retry | Timeline/metrics |
| C02-CT-005 | Partial | Required source fails page N | Finalize | Source/snapshot `PARTIAL`; missing range and owner action visible | Snapshot/alert |
| C02-CT-006 | Security | Invalid role and secret-bearing exception | Collect | Deterministic unavailable; secret redacted; audit emitted | Sanitized logs/audit |
| C02-CT-007 | Identity | One resolved, one unknown, one ambiguous alias | Normalize | Each business outcome preserved without loss | Snapshot fragment |
| C02-CT-008 | Conflict | Same source identity/watermark, different content | Deduplicate | `OBSERVATION_CONFLICT`; both checksums retained | Conflict record |
| C02-CT-009 | Context boundary | Production log containing payload plus allowlisted interaction fields | Query/normalize | Only allowlisted context retained; no edge or payload | Privacy scan/result |
| C02-CT-010 | Reconciliation | Source current set differs from snapshot | Reconcile | Exact missing/unexpected/stale/changed rows and refresh triggers | Reconciliation report |
| C02-CT-011 | Consistency | Source token expires midrun | Resume/restart | Proven consistent snapshot or visible partial/stale; no silent splice | Token/attempt evidence |
| C02-CT-012 | Load/recovery | 10,000 repositories, source skew, worker restart | Run full inventory | Time/SLO met; counts/checksums exact; checkpoint recoverable | Load report/dashboard |

## 16. Integration Obligations

- **INT-007 C01↔C02:** all observations resolve under one pinned registry
  version; unknown/ambiguous results remain explicit.
- **INT-008 C02↔C03:** snapshot-created and reconciliation triggers validate,
  deduplicate, archive, and route with immutable reference/checksum.
- **INT-009 C02↔C04:** every discovered repository/path reaches eligibility;
  no adapter applies class exclusions.
- **INT-010 C02↔C05:** application/deployment/schema/native/test/context evidence
  builds a version-pinned context snapshot under documented precedence.
- **INT-011 C02↔C17:** inventory/source completeness and reconciliation gaps are
  queryable and correlated to the user run timeline.
- **INT-012 C02↔C18:** throttling, source outage, secret redaction, audit,
  checkpoint restore, and cross-Region snapshot recovery meet operations gates.

## 17. Definition of Done

- Typed registrations and adapter conformance kits exist for every required
  launch source, with valid/invalid/golden fixtures.
- All C02 P0 requirements and C02-CT-001 through C02-CT-012 pass.
- INT-007 through INT-012 pass against deployed nonproduction integrations.
- A 10,000-repository snapshot/load report proves counts, duration, fairness,
  idempotent resume, and reconciliation.
- Security evidence proves least privilege, credential/payload redaction,
  allowlisted CloudWatch context, encryption, and audit.
- Source failure, expired token, partial snapshot, reconciliation, and restore
  runbooks have exercise IDs and owner acknowledgements.
- Dashboards/alarms and the C17 source-status view use real deployed telemetry.

## 18. Implementation Notes

```text
contracts/schemas/inventory/
services/source-adapters/common/
services/source-adapters/test-automation/
services/source-adapters/scm/
services/source-adapters/deployment/
services/source-adapters/catalog-schema/
services/source-adapters/native-lineage/
services/source-adapters/cloudwatch-context/
services/inventory-builder/
infra/lib/constructs/inventory-state.ts
tests/contract/adapters/
tests/integration/inventory/
tests/load/inventory/
```

Use TypeScript 5 for adapter/control services. Use Lambda only for bounded API
pages/normalization; use Batch for unusually large reconciliation/normalization.
S3 holds staged pages/snapshots and DynamoDB holds checkpoints/pointers.

Build source adapters behind a common conformance suite. Start with Test
Automation, SCM, deployment, and catalog/schema; add native/test/context sources
without changing the snapshot envelope. Feature flags may enable a source or
mark it optional for a pilot, but required-source policy is versioned/audited.

## 19. Traceability

| Source decision | C02 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Inventory every repository; never silently exclude | C02-FR-001/006/007/011/013 | C02-CT-001/005/010/012 | INT-009; baseline steel thread |
| Test Automation application baseline context | C02-FR-002/012 | C02-CT-001/007 | INT-010 |
| Deployment/digest and schema/native/test context | C02-FR-003/004/005 | C02-CT-009/010 | INT-008/010; hotfix steel thread |
| Resumable, idempotent, source-consistent collection | C02-FR-009/010/015; C02-NFR-004 | C02-CT-002/003/004/008/011 | INT-012; recovery gate |
| 10,000-repository capacity | C02-NFR-001/002 | C02-CT-012 | Enterprise baseline gate |
| Privacy and least privilege | C02-SEC-001 through C02-SEC-005 | C02-CT-006/009 | INT-012; security/privacy gate |
