# C12 Immutable Evidence Store and Analysis Cache PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C12 |
| Status | Approved for implementation |
| Launch phase | Foundation before collectors/workflows |
| Criticality | P0; evidence, packages, proposals, labels, and accepted manifests are the rebuild authority |
| Primary owner | Lineage data foundation team |
| Required approvers | Architecture, security/privacy, records governance, operations/DR, publication owners |
| Upstream dependencies | C01 shared contracts/identity, AWS KMS/S3/DynamoDB/Organizations/CloudTrail |
| Downstream dependencies | C02-C18 |
| Authoritative sources | AWS architecture §§6.10-6.12, 12-16; component design §§7, 9, 11 |

## 2. Purpose and Outcomes

C12 preserves the immutable facts from which lineage decisions and projections
can be reproduced. It provides encrypted, versioned, checksummed, retention-
governed S3 namespaces; strict `EvidenceReference` semantics; operational
DynamoDB indexes; content-addressed cache reuse; legal hold; integrity scanning;
cross-Region replication; and rebuild/restore evidence.

Measurable outcomes:

- 100% of material workflow outputs are immutable S3 objects referenced by
  version ID and SHA-256 before a stage is accepted.
- Identical content-addressed writes are idempotent; a key/content mismatch is
  a visible conflict and never overwrite.
- Accepted manifests/reviewer labels/evidence under retention cannot be mutated
  or deleted outside governed S3 Object Lock/legal-hold procedures.
- Neptune/OpenSearch and operational indexes can be deleted and rebuilt from
  accepted manifests/evidence within the four-hour RTO and 15-minute RPO.

## 3. Scope and Non-Goals

### In scope

- S3 evidence/data account buckets, prefixes/access points, versioning, KMS,
  public/TLS controls, S3 Object Lock, retention/lifecycle/legal hold, inventory,
  replication, integrity, backup/restore and access audit.
- `EvidenceReference`, immutable write/read/verify/list protocols.
- Content-addressed analysis/native/agent/schema/cache records and lookup indexes.
- DynamoDB metadata/idempotency/cache/pointer indexes with PITR; TTL only for
  temporary leases/session operational rows.

### Non-goals

- Being the active graph/search query engine (C16/C17).
- Treating DynamoDB cache/index metadata as evidence authority.
- Allowing a cache result to bypass component/version/authorization validation.
- Storing raw integration/production payloads or arbitrary unbounded logs.
- Deleting retained evidence because a projection or proposal is superseded.

## 4. Actors and Use Cases

| Actor/component | Use case |
|---|---|
| Collector/analyzer | Write attempt-scoped evidence/package and receive immutable reference |
| C06/C13-C16 | Verify input/result checksum/version before state transition |
| Cache consumer | Look up exact content identity and reuse an authorized verified result |
| Reviewer/auditor | Read allowed evidence/proposal/label/manifest history |
| Records administrator | Apply retention/legal hold and governed release |
| Operator | Detect corruption/replication lag, restore/rebuild indexes/projections |

## 5. Component Boundary

### Owned behavior

- Evidence/cache physical/contract storage, immutable-write protocol, references,
  metadata indexes, access boundaries, lifecycle/integrity/replication/restore.

### Inputs

- Typed content bytes/stream, schema/version, expected SHA-256/length, business
  identity/cache key, producer/run/attempt, data/retention/access class.

### Outputs

- Verified `EvidenceReference`, cache lookup/result, integrity/access/replication/
  retention events, rebuild manifests and restore evidence.

### Forbidden behavior

- Last-write-wins to an immutable business/cache key.
- Returning an unverified object without version/checksum/schema/access checks.
- Applying TTL to evidence, proposals, labels, accepted manifests, graph pointers,
  eligibility history, or required audit.
- Granting one collector writer access to another component/data-class prefix.
- Treating mutable Neptune/OpenSearch contents as recovery truth.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C12-FR-001 | C12 must provide separate governed namespaces/access points for raw allowed source metadata, normalized evidence, analysis/native/agent/opaque/runtime packages, proposals, reviewer labels, accepted manifests, graph exports, and content-addressed caches. | P0 |
| C12-FR-002 | Every durable bucket must enable versioning, KMS encryption, TLS-only policy, public-access block, ownership enforcement, CloudTrail/S3 access events, lifecycle, replication hooks, and S3 Object Lock where retention authority requires. | P0 |
| C12-FR-003 | Every stored artifact must have an `EvidenceReference` with bucket/key/version, SHA-256, bytes, media/compression, schema ID/version, evidence/provenance/producer versions, artifact/effective version, data/retention class, KMS class, run/attempt, and creation identity/time. | P0 |
| C12-FR-004 | Immutable write must stage attempt-scoped content, validate schema/privacy/size, compute/verify SHA-256, persist, read/HEAD verify version/length/checksum/KMS, then conditionally register business identity/reference before success. | P0 |
| C12-FR-005 | Identical business/cache identity and content checksum must return the verified existing reference; different checksum under the same immutable identity must create `CONTENT_IDENTITY_CONFLICT` and never overwrite. | P0 |
| C12-FR-006 | Readers must fetch by exact version ID/reference, revalidate authorization/schema/checksum/length, and reject mutable alias/latest reads for workflow/trust/publication decisions. | P0 |
| C12-FR-007 | Accepted manifests, material review labels/decisions, publication audit, and governed evidence must use S3 Object Lock retention; corrections/supersession create new objects and links. | P0 |
| C12-FR-008 | Retention/lifecycle/legal hold must be data-class/policy/version driven, auditable, conflict-checked against active hold, replication, investigation, and accepted-graph rebuild dependencies before expiration/deletion. | P0 |
| C12-FR-009 | Content-addressed cache keys must include every determinant/version declared by the producing component and map to immutable verified content; C12 must not invent or omit producer key parts. | P0 |
| C12-FR-010 | Cache lookup must verify organization/domain authorization, key schema/version, producer/model/analyzer/policy compatibility, object integrity, expiry/deprecation, and data-class constraints before returning a result. | P0 |
| C12-FR-011 | Racing first writers must use a conditional cache/business record; one identical result wins idempotently, while differing results are preserved as conflict and the key is quarantined. | P0 |
| C12-FR-012 | C12 must provide immutable manifests for large collections with entry reference/checksum/count, manifest checksum, deterministic order, page/shard metadata, and completeness. | P0 |
| C12-FR-013 | Integrity scanning must use S3 Inventory/version/object metadata and sampled/full checksums by data class, detect missing/version/KMS/length/checksum/retention/replication anomalies, and quarantine corrupt references. | P0 |
| C12-FR-014 | Cross-Region replication must preserve versions, retention/legal holds, KMS class, metadata, and checksums; replication status/lag must be queryable and gate DR readiness. | P0 |
| C12-FR-015 | Operational DynamoDB tables must use KMS, PITR, deletion protection, conditional writes, backups/replication as designed; TTL is allowed only for explicitly temporary leases/session records after immutable terminal evidence exists. | P0 |
| C12-FR-016 | C12 must support rebuilding cache/lookup/operational indexes and C16 graph/search projections from immutable manifests without modifying source artifacts. | P0 |
| C12-FR-017 | A deletion/retention release/legal-hold action must require scoped records authorization, object/version manifest, dry-run impact, reason, policy, approval, audit, and post-action reconciliation. | P0 |
| C12-FR-018 | Storage formats/compression may evolve only via versioned schemas/readers/migration manifests; original retained bytes and provenance remain accessible according to policy. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C12-NFR-001 | A verified small-object write/read must complete within 2 seconds p95; 99% of 1 GiB streaming artifacts within 10 minutes under production-like network/load. | P0 |
| C12-NFR-002 | C12 must sustain aggregate 5 GiB/second write and 10 GiB/second read bursts plus 10,000 object operations/second without cross-prefix starvation at validated AWS quotas. | P0 |
| C12-NFR-003 | Evidence durability uses S3 service guarantees; control/index availability must be 99.95% monthly and failure must not accept unverified stage/publication results. | P0 |
| C12-NFR-004 | Cross-Region retained evidence/index recovery must meet 15-minute RPO/four-hour RTO; full projection rebuild performance is governed by C16 but source availability/integrity is C12's gate. | P0 |

## 7. Data and Durable State

Recommended key structure:

```text
s3://lineage-evidence-<env>/<data-class>/<organization>/<component>/
  <schema-major>/<business-id-hash>/<content-sha256>/<artifact-name>
```

Attempt staging uses a distinct write-only prefix and is promoted by immutable
reference registration, not object copy overwrite. Accepted manifests use a
graph-version namespace under S3 Object Lock. Reviewer labels use immutable
proposal/edge/decision IDs. Graph exports are derived and rebuildable but
checksummed/versioned for publication verification.

`EvidenceMetadataRecord` mirrors reference/search fields, business/cache key,
producer/run/attempt, access/retention/hold, replication/integrity/status, prior/
supersedes links, and checksums. It is an index; object/version remains content
authority.

`CacheRecord` holds typed key schema/version/parts hash, producer/version/data
class, object reference/checksum, state `WRITING|ACTIVE|CONFLICT|DEPRECATED|
CORRUPT|EXPIRED`, lease/attempt and timestamps. TTL only applies to `WRITING`
lease, not active result/history.

## 8. Interfaces and Contracts

- `POST /v1/evidence:writes` creates an upload/write intent with schema,
  expected identity/checksum/length, class and idempotency; returns scoped
  attempt location/credentials or streaming endpoint.
- `POST /v1/evidence/writes/{id}:commit` verifies object/version/checksum/schema/
  privacy and conditionally registers; returns `EvidenceReference`.
- `POST /v1/evidence:verify` accepts reference and expected contract/access;
  returns exact status/integrity/retention/replication metadata.
- `GET /v1/evidence/{reference}` or signed scoped access requires exact version,
  purpose, actor/domain, and logs access. Broad presigned URLs are prohibited.
- `POST /v1/cache:lookup|put` uses typed cache key contract, authorization,
  expected producer versions, and immutable result reference/checksum.
- `POST /v1/manifests:validate`, integrity/replication/rebuild/list APIs operate
  over immutable references with pagination/S3 result manifests.

All service responses use references, not large content bodies. Direct S3 roles
are preferred for high-volume component-specific writes with bucket-policy
conditions enforcing exact prefix/KMS/schema metadata and commit registration.

## 9. Processing and State Model

### Immutable write

```text
INTENT -> UPLOADING -> VALIDATING -> OBJECT_VERIFIED
       -> REGISTERING -> ACTIVE
```

Alternative: `DUPLICATE`, `CONFLICT`, `QUARANTINED`, `CORRUPT`, `FAILED`.

1. Authorize producer/data class/business identity and validate intent.
2. Create scoped attempt/lease; upload with exact KMS/metadata/limits.
3. Validate closed contract/privacy/content and compute/compare SHA-256/bytes.
4. HEAD/read exact S3 version; verify encryption/retention/metadata/checksum.
5. Conditional metadata/business/cache registration decides active/duplicate/
   conflict. Return only verified reference.
6. Integrity/replication/lifecycle processes continuously reconcile objects and
   indexes; staging garbage expires only after proving no active reference.

### Cache lookup

Validate key schema/parts/producer compatibility, actor/domain/data class,
record state/expiry, then exact object verification. Integrity failure marks
cache corrupt and returns miss/error according to producer policy; it never
returns unverified bytes.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `EVIDENCE_SCHEMA_OR_PRIVACY_INVALID` | `DETERMINISTIC_INVALID` | Quarantine/reject; sanitized reason; no active ref |
| `OBJECT_CHECKSUM_OR_LENGTH_MISMATCH` | `DETERMINISTIC_INVALID` | Mark corrupt/quarantine; block stage/cache/publication |
| `CONTENT_IDENTITY_CONFLICT` | `CONFLICT` | Preserve versions/checksums; no overwrite; owner alert |
| `OBJECT_VERSION_NOT_FOUND` | `INCOMPLETE` | Reject read/result; integrity/recovery investigation |
| `ACCESS_OR_DATA_CLASS_DENIED` | `DETERMINISTIC_INVALID` security | Deny/audit; no existence leakage beyond policy |
| `S3_DYNAMODB_KMS_THROTTLED` | `TRANSIENT` | Bounded retry/idempotent attempt; no premature success |
| `REPLICATION_LAG_OR_FAILURE` | `INCOMPLETE` DR | Alert/gate failover/retention action by policy |
| `RETENTION_OR_LEGAL_HOLD_CONFLICT` | `CONFLICT` | Deny delete/release; record governing hold/policy |
| `CACHE_RECORD_CORRUPT_OR_CONFLICT` | `CONFLICT` | Quarantine key; force producer recompute/review, no result |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C12-SEC-001 | Evidence/data account buckets/tables/keys must be isolated from application/control/query accounts with Organizations-scoped roles, private endpoints, TLS-only, public block, KMS separation by environment/data class, and explicit access points/prefixes. | P0 |
| C12-SEC-002 | Producer roles must be write-only/read-minimal to exact attempt prefixes and KMS context; reader roles must be purpose/domain/data-class scoped; no wildcard cross-class data-plane permission. | P0 |
| C12-SEC-003 | S3 Object Lock/retention/legal hold and destructive actions must use records-governance role separation, MFA/break-glass where required, approval/audit, and deny ordinary administrators. | P0 |
| C12-SEC-004 | Closed schemas/privacy validators must reject raw production/integration payloads, secrets/credentials, arbitrary attributes, and payload-bearing logs before active evidence registration. | P0 |
| C12-SEC-005 | CloudTrail management/S3 data events and DynamoDB/KMS access audit must identify actor/purpose/object version/checksum/decision; security logs cannot copy sensitive content. | P0 |
| C12-SEC-006 | Malware/content scanning for source archives uses isolated readers and records verdict/checksum without weakening Object Lock or exposing contents broadly. | P1 |

## 12. Scale, Performance, and Availability

- S3 prefixes distribute by organization/component/business hash/content hash;
  no date-only hot prefix or shared mutable object.
- Multipart streaming handles large packages; per-component quotas/cost tags and
  lifecycle tiers prevent runtime/native bursts from starving manifests.
- DynamoDB keys distribute cache/idempotency/index load and use adaptive/on-
  demand/provisioned capacity validated under event spikes. Large listings use
  S3 Inventory/Glue/Athena or manifest workers, not table scans on hot paths.
- Versioned KMS keys/aliases and replication roles are pre-created in warm
  Region. Failover reads only objects whose replication/integrity/retention
  status meets policy.
- Cost dashboards cover bytes/objects/versions/replication/retrieval/KMS by
  component/data class/domain; cost pressure cannot disable retention silently.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C12-OBS-001 | Write/read/verify latency/status/bytes | component/class/schema/Region/KMS | P0 |
| C12-OBS-002 | Duplicate/conflict/corrupt/missing | business/cache key class/producer/owner | P0 |
| C12-OBS-003 | Integrity scan findings | bucket/prefix/schema/version/anomaly | P0 |
| C12-OBS-004 | Replication lag/failure/RPO readiness | class/bucket/Region; DR alert | P0 |
| C12-OBS-005 | Retention/hold/lifecycle/delete actions | policy/class/actor/result; audit alert | P0 |
| C12-OBS-006 | Cache hit/miss/conflict/deprecated/corrupt | producer/key schema/version/domain | P0 |
| C12-OBS-007 | Access denied/unusual reads/data class | actor/purpose/prefix/domain | P0 |
| C12-OBS-008 | Storage/KMS/transfer cost/quota | component/class/domain/Region | P1 |

Inventory-to-index and accepted-manifest-to-object reconciliation produce signed
reports. Any missing accepted-manifest dependency or unexpected mutable version
is a launch/operational defect.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C12-AC-001 | Given valid content, write commits only after exact object version/schema/KMS/length/SHA-256/read-back validation and returns a complete `EvidenceReference`. |
| C12-AC-002 | Given identical business/cache key/content twice, one active object/reference is reused; given different content, conflict preserves both and no overwrite occurs. |
| C12-AC-003 | Given an accepted manifest/reviewer label under retention/legal hold, mutation/deletion by ordinary/admin/producer roles fails and immutable audit remains. |
| C12-AC-004 | Given corrupted/missing/version-mismatched content, reader/cache/stage/publication rejects it and integrity alert/recovery path activates. |
| C12-AC-005 | Given unauthorized cross-domain/data-class access or payload-bearing invalid artifact, C12 denies before active registration/read and emits sanitized audit. |
| C12-AC-006 | Given expired temporary lease versus durable record, TTL removes only the lease after terminal evidence; no durable evidence/decision/pointer is TTL eligible. |
| C12-AC-007 | Given primary projection/index loss, immutable accepted manifests/evidence rebuild operational indexes and C16 projections with matching counts/checksums. |
| C12-AC-008 | Load/replication/failover/restore meets C12 NFR/RPO/RTO with exact object/version/checksum/retention reconciliation. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C12-CT-001 | IaC/security | Synthesized buckets/tables/keys/access points | Assert policies/config | Version/KMS/TLS/public/Object Lock/PITR/deletion/least privilege exact | CDK/policy report |
| C12-CT-002 | Write/read | Valid small/large/streaming artifacts | Stage/commit/read verify | Exact reference/version/bytes/SHA-256/schema | Golden refs/content hashes |
| C12-CT-003 | Idempotency/conflict | Same identity+same/different content racing | Commit | Duplicate reuse or conflict, never overwrite | Object/index histories |
| C12-CT-004 | Contract/privacy | Invalid schema, raw payload, secret, generic map, oversized | Commit | Reject/quarantine before active registration; sanitized | Validator/store/log scan |
| C12-CT-005 | Access isolation | Cross-component/domain/class/account roles | Put/get/list/delete/KMS | Only exact allowed actions; deny/audit no leakage | IAM/access analyzer/audit |
| C12-CT-006 | Retention/hold | Locked manifest/label/evidence and roles | Mutate/delete/release/expire | Governed deny/approved procedure only | S3 retention/audit |
| C12-CT-007 | Cache | Exact/missing/version-changed/deprecated/corrupt/conflict keys | Lookup/put | Valid hit or exact miss/error/quarantine | Cache matrix |
| C12-CT-008 | Integrity | Tamper metadata/version, remove/corrupt replica/index | Scan/read | Detection, quarantine, alert/rebuild; no bad read | Integrity report |
| C12-CT-009 | TTL/lifecycle | Lease/session temp plus all durable classes | Advance time/lifecycle | Only eligible temp/staged objects removed under proof | Inventory before/after |
| C12-CT-010 | Replication/legal hold | Versions/retention/hold across Regions | Replicate/failover | Metadata/checksum/hold preserved; lag gates failover | Replication report |
| C12-CT-011 | Rebuild | Delete cache/index and empty Neptune/OpenSearch | Rebuild from manifests | Counts/checksums/active versions exact | Rebuild report |
| C12-CT-012 | Load/DR | 5/10 GiB sec bursts, 10k ops sec, throttle/Region failure | Write/read/recover | NFR/RPO/RTO, fairness, no unverified success | Load/DR report |

## 16. Integration Obligations

- **INT-078 C01/C02-C11↔C12:** every producer contract writes/reads only its
  authorized data class and complete `EvidenceReference`; privacy/schema invalid
  content fails closed.
- **INT-079 C06↔C12:** stage starts/results verify exact versions/checksums;
  duplicate/redrive/stale attempts cannot overwrite authority.
- **INT-080 C08/C09/C10↔C12:** content-addressed analysis/agent/opaque cache keys,
  first writer/conflict/invalidation/auth and reproducibility interoperate.
- **INT-081 C11↔C12:** runtime validator is the only allowed path; sequence/
  manifests/retention and production deny prevent raw/unapproved writes.
- **INT-082 C12↔C13/C15:** evidence/proposals/labels read exact immutable versions;
  corrections/supersession preserve history.
- **INT-083 C12↔C16/C17:** accepted manifests/graph exports/pointers/projection
  rebuild and evidence ABAC/access audit pass.
- **INT-084 C12↔C18 security/records:** IAM/KMS/private access/Object Lock/legal
  hold/retention/delete/audit/privacy scans and runbooks pass.
- **INT-085 C12↔C18 operations:** integrity/replication/load/cost/backup/restore/
  index+projection rebuild meet RPO/RTO/exact reconciliation.

## 17. Definition of Done

- IaC creates production-shaped evidence/data account buckets, access points,
  KMS, Object Lock, retention/lifecycle/replication/inventory, DynamoDB state,
  APIs/protocols, validators, integrity/rebuild jobs, and dashboards/alarms.
- C12 P0 requirements and C12-CT-001 through C12-CT-012 pass.
- INT-078 through INT-085 pass against all production-shaped producers/readers.
- Security/records evidence proves no wildcard cross-class access, privacy-
  invalid active object, unauthorized retention/hold bypass, sensitive audit,
  or improper TTL.
- Load/replication/integrity/failover/restore/rebuild reports meet NFR/RPO/RTO
  and match object/version/checksum/count/retention/active graph evidence.
- Conflict/corruption/access/retention/legal-hold/replication/KMS/rebuild/DR
  runbooks and alarms are exercised with real artifact IDs.

## 18. Implementation Notes

```text
contracts/schemas/evidence/
services/evidence-registry/
services/evidence-validator/
workers/evidence-integrity/
workers/evidence-rebuild/
infra/lib/stacks/data-stack.ts
infra/lib/constructs/evidence-store.ts
infra/lib/constructs/control-tables.ts
docs/runbooks/evidence-store/
tests/contract/evidence/
tests/integration/evidence/
tests/security/evidence/
tests/load/evidence/
tests/chaos/evidence/
```

Use TypeScript 5/CDK for data/control APIs/IaC and Python 3.12 for integrity/
large manifest/rebuild workers. Prefer S3 checksum headers plus independently
computed SHA-256 recorded in the closed contract; ETag is not a content checksum.
Enable S3 Object Lock at bucket creation because it cannot be retrofitted safely
as an assumption.

Build order: schemas/reference; secure immutable stores/tables; write/read/
verify; per-component prefixes; cache; retention/hold; replication/integrity;
rebuild; load/security/DR. Migration uses new versioned prefix/manifests; never
in-place rewrite of retained evidence.

## 19. Traceability

| Source decision | C12 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| S3 immutable truth, projections rebuildable | C12-FR-001-008/012-016 | C12-CT-001-006/008/010/011 | INT-078/079/082/083/085 |
| Content-addressed reuse/idempotency | C12-FR-004-006/009-011 | C12-CT-002/003/007 | INT-080 |
| Privacy/security/retention/legal hold | C12-FR-007/008/017; C12-SEC-001-006 | C12-CT-004-006/009 | INT-081/084 |
| Enterprise load/integrity/DR | C12-FR-013-016; C12-NFR-001-004 | C12-CT-008/010-012 | INT-085; resilience/DR gate |
