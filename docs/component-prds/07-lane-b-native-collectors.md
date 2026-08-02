# C07 Lane B Native Lineage Collectors PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C07 |
| Status | Approved for implementation |
| Launch phase | First collection lane; pilot weeks 0-6 |
| Criticality | P0; provides exact executed column lineage and the derivational oracle used to calibrate other lanes |
| Primary owner | Native lineage integrations team |
| Required approvers | Spark platform, dbt/warehouse, Airflow, contracts/identity, trust engine |
| Upstream dependencies | C01 identity/contracts, C02 native inventory, C04 Lane B routing, C05 context, C06 scheduling, engine/catalog APIs |
| Downstream dependencies | C12-C15, C17-C18 |
| Authoritative sources | Element-level v2 R2/R5/R6; AWS architecture §§8, 11, 13-14 |

## 2. Purpose and Outcomes

C07 captures column lineage from engines that already compute it to execute or
compile a plan. It configures Spark OpenLineage listeners, parses dbt manifest
and catalog artifacts, and attributes Airflow-orchestrated SQL/native runs. It
emits exact per-run, artifact-bound mappings where the engine is authoritative
and explicit unresolved records where it is not.

Measurable outcomes:

- 100% of governed pilot Spark/dbt/Airflow Lane B jobs emit a terminal
  `NativeLineageRun` or a visible missing/incomplete alert; no silent job gap.
- Resolved native columns are bound to canonical URNs, engine run, environment,
  and immutable artifact digest.
- `select *` expansion uses the exact catalog snapshot for the run/compile; zero
  guessed columns and zero raw-Jinja lineage parsing.
- Facet/resolution coverage is measured on the real estate before confidence or
  rollout gates assume oracle coverage; unresolved reason counts are published.

## 3. Scope and Non-Goals

### In scope

- Spark listener/transport setup and OpenLineage column-lineage facet ingestion.
- dbt `manifest.json`, `catalog.json`, compiled SQL/run-result association, and
  catalog-based wildcard expansion.
- Airflow DAG/task/run attribution to the native SQL/Spark/dbt execution and
  artifact/environment.
- Native event validation, canonical identity, deduplication, completeness,
  unresolved reason codes, and immutable `NativeLineageRun` packages.
- Version/facet compatibility and estate coverage telemetry.

### Non-goals

- Static/agentic inference for custom application code (C08/C09).
- Guessing lineage inside opaque UDFs, dynamic SQL, foreign sources, or missing
  facets.
- Applying the Lane A PR CI drift workflow; Lane B's authoritative moment is
  engine execution/compile-run association.
- Claiming native execution covers unexecuted paths or all possible future runs.
- Promoting other-lane derivation merely because the native consumer received a
  field; C13 applies the required structural/derivational asymmetry.

## 4. Actors and Use Cases

| Actor/component | Use case |
|---|---|
| Spark platform owner | Enable cluster-level OpenLineage listener without producer code change |
| dbt platform/team | Publish manifest/catalog/run results on compile/run |
| Airflow owner | Bind DAG/task/run to Spark/dbt/SQL engine execution |
| C13 trust engine | Treat exact native plan mapping as derivational oracle for that native edge |
| Application owner | See native mappings, run/digest, coverage, and unresolved reasons |
| Operator | Detect missing listener/facet/catalog/run association and replay ingestion |

## 5. Component Boundary

### Owned behavior

- Engine-native configuration adapters, event/artifact validation, and native
  mapping extraction.
- `NativeLineageRun` assembly/completeness and unresolved record emission.

### Inputs

- C04 Lane B assignment and C05 job/context/schema references.
- Spark OpenLineage events/facets and engine run metadata.
- dbt manifest/catalog/compiled artifacts/run results.
- Airflow DAG/task/run and downstream native job identifiers.
- C01 registry version and canonical schema/catalog identities.

### Outputs

- Immutable `NativeLineageRun`, native edge candidates, unresolved entries,
  coverage/completeness and evidence references.

### Forbidden behavior

- Parsing raw Jinja as executed dbt SQL.
- Expanding wildcard fields without a pinned matching catalog/schema snapshot.
- Omitting an unresolved column/site/job without a reason.
- Accepting a mutable tag/branch/job name as artifact digest.
- Marking a custom-code producing edge derivationally verified based only on the
  downstream native job seeing its output.
- Sampling away governed native run events without a visible incomplete state.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C07-FR-001 | C07 must enable the approved Spark OpenLineage listener/column-lineage facet at cluster policy/configuration level for governed jobs without producer code change. | P0 |
| C07-FR-002 | C07 must validate and ingest Spark job/run identity, parent/application context, inputs/outputs, column facet, engine/listener version, environment, and artifact digest. | P0 |
| C07-FR-003 | C07 must parse dbt manifest and catalog on every governed compile/run, associate compiled SQL/run results, and never derive mappings from raw Jinja templates. | P0 |
| C07-FR-004 | dbt `select *` and wildcard expansion must use the exact warehouse catalog/schema snapshot bound to the manifest/run; missing/mismatched catalog must produce unresolved output. | P0 |
| C07-FR-005 | Airflow-orchestrated SQL/Spark/dbt lineage must be attributed to DAG ID/version, task/run, downstream native execution, application, environment, and artifact digest without treating orchestration dependencies as column mappings. | P0 |
| C07-FR-006 | Every native run must emit exact resolved column mappings where the engine provides them and typed `unresolved: true` entries with affected inputs/outputs and reason where it does not. | P0 |
| C07-FR-007 | Required unresolved reasons must include opaque UDF, dynamic/uncompiled SQL, foreign/unsupported source, missing/malformed facet, missing/mismatched catalog, unresolved identity, unsupported facet/engine version, and incomplete run. | P0 |
| C07-FR-008 | Native outputs must be bound to immutable run and artifact digest; missing digest must quarantine or mark incomplete and must not enter accepted candidate state. | P0 |
| C07-FR-009 | C07 must resolve datasets/fields through C01 against one pinned registry version while preserving native names and unknown/ambiguous outcomes. | P0 |
| C07-FR-010 | `NativeLineageRun` must be immutable, content-checksummed, idempotent by engine/job/run/artifact/environment/collector version, and complete for every declared input/output facet. | P0 |
| C07-FR-011 | Duplicate events/artifacts with identical content must return the same package; conflicting content for one native run identity must enter conflict and never overwrite. | P0 |
| C07-FR-012 | Exact native plan mappings are eligible as the derivational oracle for those native edges; C07 must emit provenance/capability, not directly assign final confidence. | P0 |
| C07-FR-013 | Native evidence crossing from a Lane B consumer to a Lane A producer may corroborate field arrival/execution structurally but must not claim how the producer derived the field. | P0 |
| C07-FR-014 | C07 must report job/run/facet/column resolution and unresolved coverage by engine/version/archetype/application/domain before rollout or confidence calibration decisions. | P0 |
| C07-FR-015 | A scheduled reconciliation must compare C02 expected Lane B jobs/runs with received terminal packages and alert missing/stale listener/manifest/catalog evidence. | P0 |
| C07-FR-016 | Engine/facet/parser version support must be a typed compatibility matrix with reject/quarantine behavior for unknown breaking versions. | P0 |
| C07-FR-017 | Lane B output must bypass Lane A PR drift generation and update lineage per authoritative run/compile semantics. | P0 |
| C07-FR-018 | Additional native engines may be added only through the common conformance kit and an approved exactness/capability statement. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C07-NFR-001 | 95% of valid native run events/artifact notifications must produce a persisted package within 60 seconds; 99% within five minutes under planned load. | P0 |
| C07-NFR-002 | C07 must process at least 1,000 native run events/second burst and 10 million column mappings/day per Region without silent sampling or loss. | P0 |
| C07-NFR-003 | Reprocessing identical native evidence with the same collector/parser/C01 versions must produce byte-identical packages/checksums. | P0 |
| C07-NFR-004 | Native intake/persistence must be 99.9% available monthly and recover/reconcile within C18 RPO/RTO. | P0 |

## 7. Data and Durable State

`NativeLineageRun` contains:

- package/job/run/parent IDs, engine (`SPARK`, `DBT`, `AIRFLOW_SQL`), engine and
  collector/parser/facet versions.
- application/repository/commit/artifact digest/environment and C01/context
  versions.
- start/end/status, source event/artifact/checksum references.
- canonical/native input/output datasets/fields.
- exact mapping/transform expression/type where authoritative.
- path/operation/task/plan node identifiers and schema/catalog snapshot.
- each unresolved scope/reason/evidence.
- declared versus received facet/object/column counts, package completeness,
  coverage dimensions, provenance capability (`EXACT_NATIVE_PLAN`,
  `NATIVE_EXECUTION_ONLY`, `UNRESOLVED`).
- canonical checksum and immutable C12 reference.

Operational DynamoDB indexes track expected run, ingestion idempotency,
completion, reconciliation, and package pointer. S3 holds OpenLineage/dbt/Airflow
evidence and immutable packages. Raw engine payload fields outside the contract
are rejected or stored only in restricted quarantine under security policy.

## 8. Interfaces and Contracts

### Spark

Spark OpenLineage event enters an authenticated EventBridge/API path and is
referenced from C03/C06. Required supported facets include job/run, inputs,
outputs, schema, column lineage, parent/run context, and governed artifact
digest extension. Listener configuration exposes endpoint, namespace mapping,
retry/spool limits, version, and fail-open job behavior.

### dbt

`POST /v1/native/dbt-runs` accepts checksummed S3 references to manifest,
catalog, compiled artifacts, and run results plus repository/commit/artifact,
environment, invocation ID, and adapter version. It rejects raw-template-only
input for mapping generation.

### Airflow

`airflow.task.native-run-linked` supplies DAG/version/task/run, application,
repository/digest/environment, operator type, and exact downstream Spark/dbt/SQL
run/artifact references. Task ordering alone is not a lineage candidate.

### Output

`native.lineage.package.created|incomplete|conflicted` carries package reference,
checksum, counts, context/artifact identity, and correlation for C12/C13/C18.

## 9. Processing and State Model

```text
EXPECTED/RECEIVED -> VALIDATING -> RESOLVING_IDENTITY -> EXTRACTING
                  -> COMPLETENESS_CHECK -> PACKAGE_WRITING -> COMPLETE
```

Alternative: `INCOMPLETE`, `UNRESOLVED`, `CONFLICT`, `QUARANTINED`, `FAILED`.

Processing:

1. Pin collector/parser/C01/context compatibility and verify input checksum,
   source, engine run, environment, and artifact digest.
2. Deduplicate by native run identity plus content checksum.
3. Extract native plan mappings only from approved facets/compiled artifacts.
4. Resolve exact catalog snapshot and expand wildcards; if unavailable, emit
   unresolved for the affected scope.
5. Canonicalize dataset/field URNs; preserve identity gaps.
6. Validate input/output/mapping counts, unresolved coverage, run terminality,
   and checksums.
7. Write/read-back immutable package, conditionally set completion pointer, emit
   status event, and reconcile expected job/run.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `NATIVE_EVENT_SCHEMA_INVALID` | `DETERMINISTIC_INVALID` | Quarantine source/version; no package success |
| `ARTIFACT_DIGEST_MISSING_OR_MISMATCHED` | `INCOMPLETE`/`CONFLICT` | No accepted candidate; resolve binding/recollect |
| `COLUMN_FACET_MISSING` | `INCOMPLETE` | Explicit unresolved/coverage; alert governed job |
| `OPAQUE_UDF` | `INCOMPLETE` semantic | Preserve surrounding exact mappings and named unresolved scope |
| `CATALOG_MISSING_OR_MISMATCHED` | `INCOMPLETE`/`CONFLICT` | Do not expand/guess wildcard; request matching catalog |
| `IDENTITY_AMBIGUOUS` | `CONFLICT` | Preserve native ID/candidates; no forced canonical edge |
| `NATIVE_RUN_CONTENT_CONFLICT` | `CONFLICT` | Preserve both checksums/evidence; review/reconcile |
| `UNSUPPORTED_ENGINE_FACET_VERSION` | `DETERMINISTIC_INVALID` | Quarantine and compatibility alert; no permissive parse |
| `STORE_OR_DEPENDENCY_THROTTLED` | `TRANSIENT` | Bounded retry/idempotent resume |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C07-SEC-001 | Engine/listener/dbt/Airflow producers must authenticate to exact application/account/environment namespaces and use least-privilege write-only evidence paths. | P0 |
| C07-SEC-002 | Native contracts must allow metadata, schema, field, plan, and transform expressions but must reject raw row values, SQL parameters, credentials, query result payloads, and arbitrary attributes. | P0 |
| C07-SEC-003 | S3/indexes must use TLS, KMS/private access, immutable versioning/retention, domain ABAC, and audited reads/writes. | P0 |
| C07-SEC-004 | Listener/cluster policy and parser compatibility changes must be signed/versioned, canaried, approved, and audited. | P0 |
| C07-SEC-005 | Error/log content must be allowlisted and redact SQL literals/parameters and payload-bearing engine exceptions. | P0 |

## 12. Scale, Performance, and Availability

- Size by native runs and field mappings, not repository count alone. Initial
  load gate covers 1,000 events/second burst and 10 million mappings/day.
- Use Kinesis/EventBridge/SQS as appropriate for intake rate, S3 for native
  artifacts, and horizontally scalable Batch/Lambda parsers; per-run ordering is
  reconstructed by immutable run ID/sequence, not global FIFO.
- Native event transport must not fail the application/job. Local bounded spool
  and asynchronous retry are allowed; overflow creates visible incomplete/loss
  telemetry, never silent sampling.
- Parser/cache keys include source checksums, engine/facet/parser/C01/context
  versions. Same artifacts reuse packages across application context only when
  environment/identity semantics match.
- Reconciliation/restore rebuild operational indexes from C12 packages under
  C18 RPO/RTO.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C07-OBS-001 | Expected versus received terminal runs | engine/application/domain/cluster/job; missing/stale alert | P0 |
| C07-OBS-002 | Facet and column resolution coverage | engine/facet/parser/version/archetype/reason | P0 |
| C07-OBS-003 | Ingest/package latency/throughput | engine/Region/status | P0 |
| C07-OBS-004 | Unresolved/conflict/digest/catalog/identity gaps | reason/application/owner | P0 |
| C07-OBS-005 | Listener/spool/drop/retry health | cluster/version/account; any governed loss alert | P0 |
| C07-OBS-006 | Oracle overlap/correction | native provenance versus reviewed accepted result | P0 |
| C07-OBS-007 | Cost/cache | mappings/jobs/bytes/parser/cache by engine/domain | P1 |

Coverage is reported as measured distribution. The platform does not assume the
Spark column facet resolves 60% or any threshold until actual pilot results
exist; rollout gates use the measured report.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C07-AC-001 | Given a Spark SQL run with exact column facet/digest, C07 emits canonical exact mappings, run/evidence/coverage, and an oracle-capable provenance package without producer code change. |
| C07-AC-002 | Given a Spark opaque UDF or missing facet, resolved surrounding mappings remain and affected scope is explicit unresolved with reason/count; nothing is guessed/omitted. |
| C07-AC-003 | Given dbt manifest/catalog/compiled SQL with `select *`, C07 expands fields from the matching catalog; missing/mismatched catalog yields unresolved and no raw-Jinja parse. |
| C07-AC-004 | Given an Airflow task linked to a native run, C07 attributes run context but creates column mappings only from the linked engine plan, not DAG ordering. |
| C07-AC-005 | Given duplicate and conflicting native events, one identical package is reused or conflict preserves both; no overwrite/duplicate candidate occurs. |
| C07-AC-006 | Given a native consumer receives a Lane A-produced field, C07 emits its exact native consumer mapping; C13 integration promotes structural corroboration only for the producer boundary. |
| C07-AC-007 | Given expected job with missing/stale listener/catalog package, reconciliation creates an owned gap/alert and baseline/run cannot claim complete native coverage. |
| C07-AC-008 | Load and recovery meet C07 NFRs with exact expected/received/package/mapping counts and no silent sample/drop. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C07-CT-001 | Spark golden | Exact projection/join/alias/aggregate column facets | Ingest | Expected canonical mappings/transforms/checksum | OpenLineage/package goldens |
| C07-CT-002 | Spark unresolved | Opaque UDF, foreign source, missing/malformed facet | Ingest | Typed unresolved/counts; surrounding exact facts retained | Package/coverage |
| C07-CT-003 | dbt golden | Manifest/catalog/compiled/run with models/tests/sources | Parse | Expected exact mappings and run binding | Artifact/package goldens |
| C07-CT-004 | dbt wildcard | `select *` with matching, missing, mismatched catalog | Parse | Exact expansion or unresolved; no guessed/Jinja result | Mapping/unresolved diff |
| C07-CT-005 | Airflow boundary | DAG tasks linked/unlinked to native executions | Attribute | Only linked native plan yields column mapping | Task/run package |
| C07-CT-006 | Digest/environment | Correct, missing, mismatched digest and two environments | Ingest | Correct isolation; invalid/incomplete/conflict outcomes | Identity/package evidence |
| C07-CT-007 | Identity | Cross-lane aliases resolved/unknown/ambiguous | Resolve/package | Canonical mapping or explicit gap; no forced ID | C01/result package |
| C07-CT-008 | Idempotency/conflict | Duplicate identical then conflicting run payload | Ingest concurrently | One package or conflict, no overwrite | Index/evidence history |
| C07-CT-009 | Compatibility/security | Unknown facet version plus values/parameters/arbitrary attrs | Validate | Quarantine/reject/redact; no package leak | Validation/privacy scan |
| C07-CT-010 | Reconciliation | Expected jobs/runs with missing/stale/complete evidence | Reconcile | Exact gap/status/owner alerts | Reconciliation report |
| C07-CT-011 | Oracle semantics | Native edge and upstream Lane A producer overlap | Send to trust fixture | Native edge oracle; upstream structural-only corroboration | C13 result golden |
| C07-CT-012 | Load/recovery | 1,000 events/sec, 10M mappings/day, duplicates, worker/Region restart | Execute/rebuild | NFRs, exact counts, no silent loss, index rebuild | Load/recovery report |

## 16. Integration Obligations

- **INT-042 C01/C04/C05↔C07:** Lane B job/context/aliases resolve to one pinned
  environment/artifact identity and wrong lane is rejected.
- **INT-043 C06↔C07:** native expected/ingestion/parse/retry/reconcile workflow
  handles S3 references/checksums and terminal completeness.
- **INT-044 Spark/dbt/Airflow↔C07:** configuration, facets/artifacts, exactness,
  unresolved, compatibility, failure, and no-producer-code behavior pass.
- **INT-045 C07↔C12:** immutable packages, duplicate/conflict/cache and recovery
  preserve checksums/authority.
- **INT-046 C07↔C13:** exact native mappings are derivational oracle; execution
  overlap to other lanes obeys structural-only asymmetry and incomplete no-
  promotion.
- **INT-047 C07↔C15/C17:** users see run/digest, exact/unresolved mappings,
  evidence, coverage, conflicts, and corrections; labels feed measured accuracy.
- **INT-048 C07↔C18:** missing listener/facet, privacy denial, load, reconciliation,
  replay/rebuild, audit, and Region recovery gates pass.

## 17. Definition of Done

- Spark cluster listener policy, dbt artifact integration, Airflow attribution,
  schemas/parsers/compatibility matrix, package/completeness/reconciliation, and
  immutable storage are implemented for the pilot.
- C07 P0 requirements and C07-CT-001 through C07-CT-012 pass.
- INT-042 through INT-048 pass with production-shaped engine/platform versions.
- Pilot coverage report measures facet/column resolution/unresolved by actual
  engine/version/archetype and is reviewed before oracle-dependent rollout.
- Load/recovery proves C07 NFRs, exact expected/received/package counts, no
  silent sampling, and rebuild.
- Security/privacy proves metadata-only contracts, namespace auth, encrypted
  immutable storage, signed config, redacted SQL/errors, and audit.
- Missing-native-evidence, listener rollback, parser compatibility, replay,
  reconciliation, and restore runbooks are exercised with real IDs.

## 18. Implementation Notes

```text
contracts/schemas/native-lineage/
services/native-ingest/
workers/native/spark-openlineage/
workers/native/dbt/
workers/native/airflow-attribution/
infra/lib/constructs/native-lineage-intake.ts
docs/runbooks/native-lineage/
tests/fixtures/native/{spark,dbt,airflow}/
tests/contract/native-lineage/
tests/integration/native-lineage/
tests/load/native-lineage/
```

Use Python 3.12 parsers/workers, TypeScript 5 control/IaC, and the official
OpenLineage model/schema where applicable with governed typed facets. Do not
fork a divergent lineage event format. Spark setup is cluster-level listener
configuration; dbt works from immutable generated artifacts; Airflow links to
engine-native execution.

Build order: contracts/golden fixtures; Spark listener/ingest; dbt parser and
catalog wildcard; Airflow attribution; completeness/reconciliation; C13
semantics; load/security/recovery. Roll out per engine version/cluster/domain
with measured coverage and rollback to prior listener/parser.

## 19. Traceability

| Source decision | C07 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Lane B first and engine-native exact | C07-FR-001 through C07-FR-006 | C07-CT-001 through C07-CT-005 | INT-043/044; Lane B pilot gate |
| Artifact-bound and no silent unresolved | C07-FR-007 through C07-FR-011/014/015 | C07-CT-002/004/006/008/010 | INT-045/047/048 |
| Native derivational oracle/asymmetry | C07-FR-012/013/017 | C07-CT-011 | INT-046; confidence gate |
| Compatibility/scale/recovery | C07-FR-016; C07-NFR-001 through C07-NFR-004 | C07-CT-009/012 | INT-044/048; enterprise gate |
| Security/privacy | C07-SEC-001 through C07-SEC-005 | C07-CT-009/012 | INT-044/048 |
