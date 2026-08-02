# C05 Application Context, Dependency, and Determinant Indexes PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C05 |
| Status | Approved for implementation |
| Launch phase | Baseline and incremental foundation |
| Criticality | P0; incremental soundness and excluded-repository triggers depend on these indexes |
| Primary owner | Lineage context and dependency team |
| Required approvers | Architecture, analyzer, deployment/platform, schema/catalog, Test Automation owners |
| Upstream dependencies | C01 identity, C02 inventory, C04 eligibility |
| Downstream dependencies | C06-C14, C17-C18 |
| Authoritative sources | AWS architecture §§8.1, 8.3, 9.2-9.3, 13, 17; element-level v2 R9 |

## 2. Purpose and Outcomes

C05 produces a version-pinned `ApplicationContextSnapshot` and the reverse
indexes needed to answer two questions safely: which repositories and evidence
form this business application, and which accepted/proposed edges must be
reconsidered when a file, symbol, schema, configuration key, dependency,
contract, test, or infrastructure binding changes.

Measurable outcomes:

- Every baseline pins one context/dependency-index version with explained
  application associations and coverage gaps.
- Every accepted candidate edge and open hole has a nonempty `DeterminantSet`
  or a visible `DETERMINANTS_INCOMPLETE` defect.
- Relevant shared library, infrastructure, contract, and test changes resolve
  affected applications; irrelevant capacity/documentation changes record
  explicit no-impact decisions.
- Scheduled full scans show zero full-scan divergence from determinant-based
  incremental results; any non-zero divergence is a defect.

## 3. Scope and Non-Goals

### In scope

- Application/repository association resolution with ranked evidence.
- Immutable context snapshots containing repository/path decisions, deployments,
  schemas/contracts/native jobs/tests, and selected interaction context.
- DependencyRecord indexes for shared library consumers, infrastructure
  bindings, contract producers/consumers, and test-scenario coverage.
- DeterminantSet schema and reverse indexes across files, symbols, schemas,
  configuration keys, build inputs, dependency versions, policy/analyzer
  versions, and generated inputs.
- Incremental invalidation planning, no-impact reasoning, freshness, and
  full-scan divergence reports.

### Non-goals

- Classifying repositories or lanes (C04).
- Parsing code to discover analyzer-owned symbol/dataflow determinants (C08).
- Scheduling/performing analysis (C06-C11).
- Assuming changed-file proximity or forward reachability alone is sound.
- Directly asserting field derivation from infrastructure or interaction data.

## 4. Actors and Use Cases

| Actor/component | Use case |
|---|---|
| Application owner | Inspect repositories, deployments, contracts, tests, and association evidence |
| C06 | Plan baseline and targeted incremental work from immutable context/indexes |
| C08 | Read context and add precise analyzer determinants |
| C13/C14 | Attach determinants to edges/holes and decide invalidation/freshness |
| Platform operator | Reconcile indexes, diagnose fan-out, and run full-scan divergence |

Representative scenarios:

1. `application.yaml` changes a Spring qualifier; C05 invalidates every edge/hole
   determined by that configuration key even when no Java file changed.
2. A shared library serializer signature changes; C05 finds pinned consumers and
   schedules only affected deployed/application artifacts.
3. Infrastructure CPU/memory tags change; C05 records no lineage impact. A
   topic route/env endpoint changes; affected applications are re-evaluated.
4. An Avro schema field changes; connected producers/consumers and their
   determinants are returned.
5. A test scenario changes; mapped runtime evidence becomes stale and targeted
   recollection is proposed.

## 5. Component Boundary

### Owned behavior

- Context association precedence and snapshot assembly.
- Dependency/index schemas, writes, reverse lookups, versioning, reconciliation.
- Determinant invalidation planning and change-impact reason records.

### Inputs

- C02 inventory snapshot and source completeness.
- C04 effective classification/path/lane decisions.
- C01 registry version/canonical URNs.
- C08/C13 determinant additions and accepted graph/proposal references.
- Repository/deployment/schema/infrastructure/test changes from C03.

### Outputs

- `ApplicationContextSnapshot`, `DependencyRecord`, `DeterminantSet`,
  `InvalidationPlan`, and `IndexReconciliationReport` references/checksums.

### Forbidden behavior

- Guessing owner/application when evidence remains tied.
- Treating a shared library commit as active canonical lineage before an
  affected consuming artifact is analyzed/deployed.
- Treating infrastructure binding/interaction evidence as field derivation.
- Dropping a determinant because the referenced file/symbol was deleted.
- Declaring no impact from changed-file/path comparison alone.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C05-FR-001 | C05 must create an immutable `ApplicationContextSnapshot` pinned to inventory, C01 registry, C04 policy/decision, source watermark, and context-builder versions. | P0 |
| C05-FR-002 | Application/repository association must use precedence: governed catalog/Test Automation ownership, deployment/artifact metadata, explicit config/contract reference, observed interaction, then inference requiring review. | P0 |
| C05-FR-003 | Tied or missing material association evidence must remain an explicit context conflict/gap; C05 must not choose by repository name similarity. | P0 |
| C05-FR-004 | Context must include all classified repository/path units, commit/digest/environment, owners/domains, deployments, schemas/contracts, native jobs, test scenarios, and selected interaction evidence with source completeness. | P0 |
| C05-FR-005 | C05 must index a shared library/package and pinned/ranged version to every consuming repository/workload/artifact with evidence and validity interval. | P0 |
| C05-FR-006 | C05 must index infrastructure routes, topics, queues, endpoints, schemas, environment variables, task wiring, and service-discovery bindings to affected applications, while distinguishing capacity-only attributes. | P0 |
| C05-FR-007 | C05 must index every contract/schema to producing and consuming workloads/fields where known and preserve unresolved producer ambiguity. | P0 |
| C05-FR-008 | C05 must index test scenarios to application/workload, expected sidecars, schema/field coverage, artifact digest, and runtime-evidence freshness. | P0 |
| C05-FR-009 | Every edge/hole analysis package must supply or inherit a `DeterminantSet` covering files, symbols, schemas, configuration keys, build/generated inputs, dependency versions, and analyzer/policy/contract versions that can change it. | P0 |
| C05-FR-010 | Reverse indexes must answer determinant-to-edge/hole/workload/application and dependency/binding/contract/test-to-application with the exact index version used. | P0 |
| C05-FR-011 | Invalidation must follow changed determinants and dependency/binding semantics, not merely the changed-file set or forward call-graph reachability. | P0 |
| C05-FR-012 | Deleted/renamed determinants must invalidate prior dependents and preserve tombstone/alias evidence until the resulting proposal is reviewed. | P0 |
| C05-FR-013 | Capacity-only infrastructure and pure documentation changes may produce `NO_LINEAGE_IMPACT` only from versioned typed rules and must retain evaluated attributes/reason. | P0 |
| C05-FR-014 | Test changes affecting lineage-relevant scenarios must mark mapped runtime evidence stale and request targeted recollection; unrelated test metadata changes must record no impact. | P0 |
| C05-FR-015 | Scheduled full scan must compare its complete edge/hole result with the accumulated incremental result and publish full-scan divergence; non-zero unexplained divergence is a defect. | P0 |
| C05-FR-016 | Index/context version activation must be conditional/atomic and retain immutable prior versions so in-flight runs never mix index versions. | P0 |
| C05-FR-017 | C05 should provide preview/fan-out estimates and owner/cost before activating a large invalidation plan. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C05-NFR-001 | One repository change invalidation query must return within 2 seconds p95 for 99% of estate changes; larger fan-out returns a manifest within 30 seconds p95. | P0 |
| C05-NFR-002 | A context/dependency build for 10,000 repositories must complete within 90 minutes and produce exact inventory/index reconciliation counts. | P0 |
| C05-NFR-003 | Index reads/effective pointers must be 99.95% available monthly; immutable versions must restore within C18 RPO/RTO. | P0 |
| C05-NFR-004 | Repeating context/index/invalidation construction with the same inputs/versions must produce byte-identical manifests/checksums. | P0 |

## 7. Data and Durable State

### `ApplicationContextSnapshot`

- application/domain/owner canonical identities and association evidence.
- inventory/C01/C04/source/context-builder versions and completeness.
- repository/path units with class/lane, commit, deployed digests/environments.
- schema/contract/native job/test/interaction references.
- dependency/index version, conflict/gap list, counts/checksum.

### `DependencyRecord`

Typed variants:

- `LIBRARY_CONSUMER`: package/library/version/exported interface -> consumer
  repository/workload/artifact and lockfile/SBOM/build evidence.
- `INFRASTRUCTURE_BINDING`: route/topic/queue/endpoint/schema/environment
  variable/task/service discovery -> application/workload/environment.
- `CONTRACT_RELATION`: schema/contract/version -> producer/consumer/workload.
- `TEST_MAPPING`: scenario/version -> workload, expected sidecar, covered
  schemas/fields, artifact/test run.

All records include canonical IDs, validity interval, evidence, source/index
version, status/tombstone, and checksum.

### `DeterminantSet`

Typed determinants: `FILE`, `SYMBOL`, `SCHEMA`, `CONFIG_KEY`, `BUILD_INPUT`,
`GENERATED_INPUT`, `DEPENDENCY_VERSION`, `CONTRACT_VERSION`, `POLICY_VERSION`,
`ANALYZER_VERSION`, and `RUNTIME_SCENARIO`. Each includes content/version hash,
location/selector, role, evidence, and validity. The set is canonically sorted
and content-addressed.

### `InvalidationPlan`

Contains change event, prior/current context/index versions, changed/tombstoned
determinants, affected edges/holes/workloads/applications, reason path,
class-specific action, priority, fan-out/cost estimate, no-impact decisions,
gaps/conflicts, and manifest checksum.

S3 is authoritative for snapshots/manifests/reports. DynamoDB stores effective
pointers and reverse indexes with application/domain/repository sharding.

## 8. Interfaces and Contracts

- `POST /v1/application-contexts:build` accepts application, inventory/C01/C04
  versions, prior context, and idempotency; returns run/reference.
- `GET /v1/application-contexts/{applicationId}/versions/{version}` returns an
  immutable reference/checksum and completeness, not an oversized embedded body.
- `POST /v1/dependencies:upsertManifest` accepts C02/C08 produced typed records
  by S3 reference, expected index version, and checksum.
- `POST /v1/invalidation-plans` accepts normalized change event reference,
  expected active context/index/graph versions, dry-run, and policy.
- `POST /v1/full-scan-divergence` compares checksummed full/incremental manifests.
- Events: `application.context.activated`, `dependency.index.activated`,
  `invalidation.plan.created`, `lineage.no-impact.recorded`,
  `incremental.divergence.detected`.

All list/query APIs paginate and return the index/version watermark. Empty result
is distinguishable from incomplete/unavailable index.

## 9. Processing and State Model

### Context/index lifecycle

```text
REQUESTED -> ASSEMBLING -> RESOLVING -> VALIDATING -> STAGED
          -> RECONCILED -> ACTIVE -> SUPERSEDED
```

`INCOMPLETE`, `CONFLICT`, and `FAILED` remain queryable. Activation requires
expected prior pointer and immutable read-back/checksum.

### Invalidation algorithm

1. Pin change event, active context/dependency/determinant indexes, accepted
   graph, and policy versions.
2. Normalize changed/deleted files, symbols, schemas, configuration key values,
   build/generated inputs, dependency/contract versions, infrastructure
   attributes, and test scenarios.
3. Traverse reverse determinants to candidate edges/holes/workloads.
4. Apply class-specific dependency semantics:
   - application/pipeline: affected determinants.
   - shared library: changed exported serializer/mapper/schema/config interface
     -> compatible/pinned consumers; canonical state changes after consumer
     artifact analysis/deployment.
   - infrastructure: lineage-relevant bindings only; capacity attributes no
     impact.
   - contract: connected producers/consumers.
   - test: coverage/freshness and targeted recollection.
   - documentation/mixed/unknown: C04 path action/review.
5. Compute reason paths and union affected work. Never subtract solely because
   forward reachability did not find a path.
6. Validate completeness/conflicts, estimate fan-out, write immutable plan, and
   emit through C03 to C06.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `CONTEXT_SOURCE_INCOMPLETE` | `INCOMPLETE` | Preserve partial context; block/qualify baseline per criticality |
| `APPLICATION_ASSOCIATION_CONFLICT` | `CONFLICT` | Preserve candidates/evidence; review required |
| `DETERMINANTS_INCOMPLETE` | `INCOMPLETE` | Do not claim bounded incremental soundness; schedule full/expanded analysis |
| `INDEX_VERSION_CONFLICT` | `CONFLICT` | Recompute against new active version; do not mix |
| `INDEX_WRITE_THROTTLED` | `TRANSIENT` | Bounded retry/checkpoint/idempotency |
| `DEPENDENCY_AMBIGUOUS` | `CONFLICT` | Include conservative affected candidates and visible review item |
| `NO_IMPACT_RULE_INVALID` | `DETERMINISTIC_INVALID` | Do not issue no-impact; quarantine policy/input |
| `FULL_SCAN_DIVERGENCE` | `DETERMINISTIC_INVALID` defect | Alert, retain diff, block stricter incremental enforcement until corrected |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C05-SEC-001 | Context/index reads and writes must enforce organization/domain RBAC and sensitive metadata ABAC; consumers receive only required namespaces. | P0 |
| C05-SEC-002 | Snapshots/indexes must store metadata/evidence references, not repository credentials, raw payloads, configuration secret values, or payload-bearing logs. | P0 |
| C05-SEC-003 | S3/DynamoDB must use KMS, TLS/private access, PITR/version history, and separate builders/readers/activators with no wildcard cross-domain data permissions. | P0 |
| C05-SEC-004 | No-impact rules, context association overrides, index activation, and divergence waivers must be versioned, approved, and audited. | P0 |
| C05-SEC-005 | Configuration determinants must record key/path and irreversible content/version hash where needed, never secret plaintext. | P0 |

## 12. Scale, Performance, and Availability

- Index 10,000 repositories plus all applications, path units, artifacts,
  dependencies, schemas, configuration keys, tests, edges, and holes.
- Partition reverse indexes by organization/type/hash prefix; fan-out results
  over API limits use S3 manifests and Step Functions Distributed Map.
- Cache immutable context/index versions locally by checksum. A run records one
  version and cannot observe pointer changes midrun.
- Per-domain fan-out admission prevents a central library change from starving
  Tier-1 deployment changes; C06 applies final scheduling fairness.
- Full index rebuild and restore are tested from S3 under the four-hour RTO;
  latest data/index events meet 15-minute RPO.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C05-OBS-001 | Context coverage/conflicts | application/domain/source/class/lane; critical gap alert | P0 |
| C05-OBS-002 | Dependency/index counts/freshness | type, source, index version, owner | P0 |
| C05-OBS-003 | Determinant completeness | archetype/analyzer/provenance; missing set alert | P0 |
| C05-OBS-004 | Invalidation fan-out/latency/reasons | change type/class/domain/priority | P0 |
| C05-OBS-005 | No-impact decisions | rule/policy/change type/owner; reconciliation audit | P0 |
| C05-OBS-006 | Full-scan divergence | missing/extra/modified edges/holes by archetype; non-zero alert | P0 |
| C05-OBS-007 | Index query/throttle/cost | table/index/partition/domain | P1 |

C17 exposes context/index versions, reason paths, coverage, no-impact, and
divergence without granting direct DynamoDB access.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C05-AC-001 | Given a mixed application inventory, C05 publishes one immutable context containing every classified path, artifact, schema, native job, test mapping, association evidence, and source gap. |
| C05-AC-002 | Given an `application.yaml` qualifier-only change, affected injected implementation edges/holes are selected even though no source file changed. |
| C05-AC-003 | Given a shared serializer interface change, only evidenced consuming workloads/artifacts are planned; accepted lineage does not change until consumer analysis/deployment. |
| C05-AC-004 | Given CPU/tag versus topic/endpoint environment changes, the former records no impact and the latter returns exactly bound applications with reason paths. |
| C05-AC-005 | Given a contract field or lineage-relevant test change, connected workloads or stale runtime scenarios are targeted; unrelated test metadata records no impact. |
| C05-AC-006 | Given an edge determinant was deleted, prior dependents are invalidated and tombstone evidence remains until review. |
| C05-AC-007 | Given a scheduled full scan differs from incremental state, a full-scan divergence defect/alert blocks enforcement advancement and preserves the exact diff. |
| C05-AC-008 | The production-shaped load/rebuild tests meet C05 NFRs with exact inventory/context/index and determinant/result reconciliation. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C05-CT-001 | Unit/golden | Pilot mixed application inventory | Build context | Canonical expected snapshot/checksum | Golden snapshot |
| C05-CT-002 | Precedence/conflict | Multiple association evidence tiers/tie | Resolve | Higher tier selected; tie remains conflict | Rule trace/conflict |
| C05-CT-003 | Index | Library/infra/contract/test typed records | Build/query both directions | Exact forward/reverse results/version | Index golden |
| C05-CT-004 | Determinants | File/symbol/schema/config/build/dependency inputs | Canonicalize/index | Complete stable set and reverse links | Determinant golden |
| C05-CT-005 | Config boundary | Only configuration key changes injection | Plan | All and only determined edges/holes targeted | Plan/reason paths |
| C05-CT-006 | Shared library | Exported serializer change and unrelated internal change | Plan | Consumers targeted only for relevant interface/determinants | Fan-out manifest |
| C05-CT-007 | Infrastructure | CPU/tag and topic/route/env endpoint changes | Plan | No-impact versus exact binding targets | Decisions/audit |
| C05-CT-008 | Contract/test | Schema field and scenario coverage changes | Plan | Producer/consumer targets; evidence freshness updates | Plan/freshness |
| C05-CT-009 | Delete/rename | Determinant deleted/renamed | Plan | Prior dependents targeted; tombstone/alias retained | Plan/index history |
| C05-CT-010 | Idempotency/conflict | Duplicate index manifest then competing expected version | Activate | One version; conflict forces recompute, no mix | Pointer/history |
| C05-CT-011 | Divergence | Full scan has missing/extra/modified edges | Compare | Exact non-zero defect/alert; no suppression | Diff/report |
| C05-CT-012 | Load/recovery | 10,000 repositories, central library fan-out, restart/restore | Build/query/plan/rebuild | NFRs and exact reconciliation; no Tier-1 loss | Load/recovery report |

## 16. Integration Obligations

- **INT-027 C01/C02/C04↔C05:** one pinned context resolves canonical identities,
  inventory, classifications, lanes, evidence precedence, and gaps.
- **INT-028 C05↔C06:** invalidation manifests schedule exactly planned work,
  preserve priority/fan-out, and use one index version.
- **INT-029 C05↔C08/C13:** analyzer/verified edge and hole determinants round-trip
  into reverse indexes; missing determinants prevent bounded claims.
- **INT-030 C05↔C14:** config/library/infra/contract/test changes produce correct
  CI/deployment freshness and no-impact decisions.
- **INT-031 C05↔C11:** test mapping controls expected sidecars/scenarios and
  lineage-relevant test changes mark runtime evidence stale.
- **INT-032 C05↔C17:** application context, association/conflict, reason path,
  no-impact, and divergence are visible with authorization.
- **INT-033 C05↔C18:** index reconciliation, large fan-out fairness, outage,
  restore/rebuild, audit, and divergence alert/runbooks pass.

## 17. Definition of Done

- Contracts, context builder, typed indexes, determinant schema, invalidation
  planner, full-scan comparator, and immutable/effective storage are implemented.
- C05 P0 requirements and C05-CT-001 through C05-CT-012 pass.
- INT-027 through INT-033 pass with production-shaped components.
- Config-only, shared-library, infrastructure, contract, test, monorepo, delete/
  rename, and no-impact steel-thread cases retain exact plan/result evidence.
- The enterprise build/query/load/rebuild report meets NFRs and exact
  reconciliation.
- Full-scan divergence is zero in the acceptance corpus or fails the gate with
  an owned defect; it is never accepted as a tuning tolerance.
- Security, index activation/rollback, fan-out, divergence, and restore runbooks
  are exercised; dashboards/alarms link real run IDs.

## 18. Implementation Notes

```text
contracts/schemas/context/
contracts/schemas/dependencies/
contracts/schemas/determinants/
services/context-builder/
services/dependency-index/
services/invalidation-planner/
workers/reconciliation/full-scan-divergence/
infra/lib/constructs/context-indexes.ts
tests/contract/context/
tests/integration/context-invalidation/
tests/load/context-indexes/
```

Use TypeScript 5 for context/index/control APIs and Python 3.12 for large
reconciliation/diff workers. S3 holds immutable manifests; DynamoDB holds
effective pointers/reverse indexes. Large fan-out is an S3 manifest, never a
Step Functions payload. Do not use Neptune as the determinant authority.

Build order: context schema/builder; typed dependency indexes; determinant
ingestion/reverse indexes; invalidation rules; full-scan comparison; UI/ops;
load/rebuild. Feature flags may preview new invalidation rules but no-impact
decisions require active versioned policy.

## 19. Traceability

| Source decision | C05 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Application context separately versioned | C05-FR-001 through C05-FR-004/016 | C05-CT-001/002/010 | INT-027/032 |
| Excluded repos trigger affected apps | C05-FR-005 through C05-FR-008/013/014 | C05-CT-003/006/007/008 | INT-028/030/031 |
| Determinant-based incremental soundness | C05-FR-009 through C05-FR-012/015 | C05-CT-004/005/009/011 | INT-029/030; incremental steel thread |
| Scale, fairness, rebuild | C05-NFR-001 through C05-NFR-004 | C05-CT-012 | INT-033; enterprise/DR gates |
| Security/privacy/governance | C05-SEC-001 through C05-SEC-005 | C05-CT-007/010 | INT-032/033 |
