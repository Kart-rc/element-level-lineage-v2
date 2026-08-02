# Shared Contract Catalog

**Status:** Normative
**Contract owners:** C01 (schema/identity), named producer (content), C12
(immutable persistence conventions)

## 1. Contract Rules

Every externally stored or transmitted contract must have:

- `$id` or equivalent canonical contract identifier.
- Semantic schema version and producing software/policy versions.
- Immutable business identity fields; missing identity fails validation or
  enters a named quarantine path.
- UTC RFC 3339 timestamps and globally unique event/artifact identifiers.
- `additionalProperties: false` at runtime, security, review, publication, and
  other privacy-sensitive boundaries.
- Enumerated extension variants rather than arbitrary property bags.
- A named Producer, Consumers, authority, retention class, and compatibility
  policy.
- Valid, boundary, and invalid examples committed with the schema.
- For S3-referenced content: URI, SHA-256 checksum, byte count, media type,
  compression, schema ID/version, KMS key class, and creation time.

Unknown schema major versions are deterministic invalid. A consumer may accept
a newer minor version only when its compatibility suite proves every new field
optional and semantics unchanged. Consumers preserve unknown versioned
extensions only when their enclosing schema explicitly permits that typed
variant.

## 2. Canonical Artifact Inventory

| Contract | Producer | Consumers | Authority | Compatibility |
|---|---|---|---|---|
| `CanonicalUrn` | C01 | All components | C01 registry | Grammar changes require new major version |
| `IdentityAliasRecord` | C01 | C02, C07-C13, C16-C17 | S3 history/DynamoDB effective index | Additive aliases; conflict semantics stable |
| `EventEnvelope` | C03 | C04, C06, C14, C18 | EventBridge archive plus idempotency state | Typed data schema versioned independently |
| `RepositoryInventorySnapshot` | C02 | C04-C06, C18 | S3 | Additive sources/fields in minor versions |
| `RepositoryEligibilityDecision` | C04 | C05-C06, C14, C17-C18 | S3 history/DynamoDB effective | Enum additions require consumer readiness |
| `ApplicationContextSnapshot` | C05 | C06-C13, C15, C17 | S3 | Immutable version, additive context sections |
| `DependencyRecord` | C05 | C06, C14, C18 | S3/DynamoDB index | Type enum governed |
| `DeterminantSet` | C05/C08 | C06, C13-C14 | S3 | Determinant kinds are typed variants |
| `CollectionRun` | C06 | C03, C12-C18 | DynamoDB plus audit | State additions require terminal/nonterminal declaration |
| `NativeLineageRun` | C07 | C12-C13 | S3 | OpenLineage facets plus governed extensions |
| `DeterministicAnalysisPackage` | C08 | C09, C12-C14 | S3 | Analyzer version participates in identity |
| `Hole` | C08/C13 | C09, C13, C15, C17 | S3 proposal inputs | Reason enum additive only with UI fallback |
| `AgentResolution` | C09 | C12-C13 | S3/cache index | Model/prompt/tool policy in cache identity |
| `OpaqueEvidencePackage` | C10 | C12-C13 | S3 | Advisory policy version required |
| `RuntimeEvidenceSession` | C11 | C06, C12-C13, C17-C18 | DynamoDB plus S3 manifest | State machine/version fixed per session |
| `RuntimeEvidenceEnvelope` | C11 | C11 validator, C12-C13 | S3 after validation | Strict allowlist; no generic map |
| `EvidenceReference` | C12 | C06, C09, C13-C17 | S3 content plus metadata | Checksum algorithm changes require major version |
| `VerifiedLineageCandidateSet` | C13 | C14-C15 | S3 | Confidence policy/version mandatory |
| `ArtifactLineageBinding` | C14 | Deploy systems, C15-C18 | Signed S3 artifact/registry | Signature profile versioned |
| `LineageProposal` | C15 | C16-C17 | S3 plus lifecycle index | Immutable proposal version |
| `ReviewCorrection` | C15/C17 | C13, C15-C16 | S3 | New version, never in-place mutation |
| `ReviewLabel` | C15 | Calibration analytics/C13 | S3/analytics catalog | Immutable per material edge decision |
| `AcceptedLineageManifest` | C16 | C12, C16-C18 | S3 Object Lock | Immutable graph version |
| `PublicationReservation` | C16 | C16 | DynamoDB | Token/lease semantics require major version |
| `ActiveGraphPointer` | C16 | C17-C18 | DynamoDB | Conditional transaction only |
| `ProjectionWatermark` | C16 | C17-C18 | DynamoDB/OpenSearch metadata | Monotonic per graph version |

## 3. `CanonicalUrn`

Canonical URNs use normalized UTF-8 and percent-encoding for reserved
characters:

```text
urn:lineage:<organization>:<environment>:<kind>:<namespace>:<name>[@<effective-version>][#<element-path>]
```

- `organization`, `environment`, `kind`, and `namespace` are lower-case governed
  slugs.
- `name` retains authoritative case only for case-sensitive sources; its
  normalized comparison key is stored separately.
- `kind` is one of `application`, `repository`, `artifact`, `service`, `job`,
  `dataset`, `schema`, `field`, `endpoint`, `topic`, `queue`, `file`, or a
  registered extension kind.
- Dataset/field identity uses the authoritative catalog/schema key when
  available; source-specific names become aliases.
- `effective-version` is an immutable artifact digest, schema version, graph
  version, or governed run version appropriate to the kind.
- `element-path` uses JSON Pointer escaping for nested fields.

Examples:

```text
urn:lineage:acme:integration:dataset:kafka.orders:created@v3#/gross_amount
urn:lineage:acme:prod:artifact:payments:api@sha256-741abc
urn:lineage:acme:prod:dataset:warehouse.analytics:fct_orders@2026-08-02#/total_revenue_usd
```

## 4. `EventEnvelope`

```json
{
  "eventId": "01J...",
  "eventType": "repository.commit.observed",
  "occurredAt": "2026-08-02T14:31:22Z",
  "receivedAt": "2026-08-02T14:31:24Z",
  "organizationId": "acme",
  "correlation": {
    "collectionRunId": "run-...",
    "traceId": "..."
  },
  "schema": {"id": "urn:contract:event-envelope", "version": "1.0.0"},
  "source": {"system": "github", "account": "enterprise", "deliveryId": "..."},
  "data": {}
}
```

Typed `data` variants include:

- `repository.commit.observed`: organization, repository ID, commit SHA,
  branch/ref, changed paths, source delivery identity.
- `artifact.deployed`: organization, repository, artifact digest, environment,
  deployment ID, application, deploy time, emergency-path flag.
- `baseline.requested`: application, requested snapshot watermark, requester.
- `runtime.session.requested`: application/repository/test run, commit, digest,
  expected sidecars, allowlist and budgets.
- `proposal.decision.recorded`: proposal/version, reviewer, decision and
  immutable decision reference.
- `publication.requested/completed`: proposal/version, expected prior/target
  graph version and manifest reference.

SCM idempotency identity:

```text
organization + repository + commitSha + eventType
+ analyzerVersion + policyVersion
```

Deployment idempotency identity:

```text
organization + repository + artifactDigest + environment + eventType
+ analyzerVersion + policyVersion
```

## 5. `RepositoryInventorySnapshot`

Identity: organization plus inventory watermark. The immutable body includes:

- Application/domain/owner associations with evidence and precedence.
- Every discovered repository, default branch, active/archive state, immutable
  HEAD commit, and source watermark.
- Deployed artifacts and environments with digests.
- Build/deployment descriptors, manifests, schemas/contracts, native jobs,
  test scenarios, and selected interaction context references.
- Source-by-source status: `COMPLETE`, `PARTIAL`, `UNAVAILABLE`, or `STALE`, with
  page/watermark, failure reason, retry history, and collected time.
- Counts/checksums enabling later source-to-snapshot reconciliation.

## 6. `RepositoryEligibilityDecision`

Identity: repository/path plus policy version and effective time. Fields:

- Classification: `APPLICATION_RUNTIME`, `DATA_PIPELINE`,
  `CONTRACT_SCHEMA_SOURCE`, `SHARED_LIBRARY`, `INFRASTRUCTURE`, `DOCUMENTATION`,
  `TEST_AUTOMATION`, `MIXED_MONOREPO`, or `UNKNOWN`.
- Eligible paths and excluded paths for a mixed monorepo.
- Lane assignment `A`, `B`, or `C` per producer/workload; absence is a coverage
  gap, not a default.
- Inclusion/exclusion reason codes and ranked evidence references.
- Application/domain/owner, dependencies, policy version, effective/expiry,
  override reviewer/rationale, content signature, and reconciliation time.

## 7. `ApplicationContextSnapshot`, `DependencyRecord`, and `DeterminantSet`

`ApplicationContextSnapshot` identity is application plus snapshot version. It
pins inventory version, repository/path decisions, commit/digest, schemas,
native jobs, deployment bindings, test scenarios, interaction context, and
dependency-index version.

`DependencyRecord` variants:

- Library consumer: library/package/version range -> repository/artifact.
- Infrastructure binding: route/topic/queue/endpoint/config -> application.
- Contract relationship: schema/contract -> producer or consumer workload.
- Test mapping: scenario -> application/workload/expected sidecar.

`DeterminantSet` records every file, symbol, schema, config key, dependency
version, generated input, analyzer/policy version, and source digest that could
change an edge or hole. Determinants are content-addressed and reverse-indexed.

## 8. `CollectionRun`

Identity: `collectionRunId`. Required fields:

- Run type: baseline, incremental, runtime, verification, publication,
  reconciliation, projection rebuild, or recovery.
- Application/repository/commit/artifact/environment identities as applicable.
- Policy/analyzer/contract versions.
- Trigger event and immutable context references.
- Current stage, ordered stage attempts, start/end, retry/redrive, error class,
  owner action, progress counters, and terminal outcome.
- Child workflow/job/session IDs and common correlation fields.

No stage embeds a large evidence body. It records an `EvidenceReference`.

## 9. Analysis Contracts

### 9.1 `NativeLineageRun`

Contains engine, job/run, artifact digest, input/output dataset/field URNs,
exact mapping/transform when provided by the engine, OpenLineage facet version,
resolved/unresolved status and reason, execution time, schema/catalog
references, and completeness checksum.

### 9.2 `DeterministicAnalysisPackage`

Identity: repository/artifact digest plus analyzer version and policy version.
Contains source snapshot checksum, workload/archetype, canonical candidate
edges, evidence spans, call/data-flow facts, `DeterminantSet`, `Hole` records,
coverage by supported construct, unsupported constructs, and a stable canonical
serialization checksum.

### 9.3 `Hole`

```json
{
  "holeId": "hole-content-id",
  "sourceLocation": {"path": "src/...", "startLine": 14, "endLine": 21},
  "reason": "DYNAMIC_DISPATCH",
  "affectedSinkUrn": "urn:lineage:...",
  "determinantsRef": "s3://...#sha256=...",
  "state": "OPEN"
}
```

Closure requires a deterministic resolution, verified agent resolution, or
review disposition. A dropped candidate returns the same hole identity to
`OPEN` with a verification reason.

### 9.4 `AgentResolution`

Identity/cache key:

```text
codeSliceHash + schemaHash + modelVersion + promptVersion + toolPolicyVersion
```

Contains hole ID, tool-call transcript references, bounded cited file:line
spans with quote hashes, candidate edges, budget usage, completion status,
unresolved reason, gateway/model/prompt versions, and checksum. It cannot
contain a whole-repository context dump or uncited emitted edge.

### 9.5 `OpaqueEvidencePackage`

Contains system/environment/digest, observation window/count, allowlisted field
URNs, session-scoped/nonreversible fingerprint comparison, match ambiguity,
collision/precision policy, evidence strength, retention, and permanent
advisory designation.

## 10. Runtime Contracts

### 10.1 `RuntimeEvidenceSession`

Identity: runtime session ID. Required fields:

- Test run, application, repository, commit, artifact digest.
- Environment exactly `integration`.
- Requested/start/expiry times and signed authorization reference.
- Expected sidecar IDs and minimum versions.
- Schema/field allowlist, maximum events/bytes, fingerprint policy, sampling/
  truncation policy, and Kinesis routing policy.
- State and each transition attempt.
- Registration, heartbeat, sequence-range, final-manifest and checksum status
  per expected sidecar.

### 10.2 `RuntimeEvidenceEnvelope`

Allowed keys are closed and typed:

- session/sidecar/event ID and monotonic sequence.
- application/repository/commit/artifact/test/trace/span identity.
- schema URN/hash, field path, logical type, nullability/presence.
- protocol, operation, direction, observation window/count.
- session-scoped keyed fingerprint where policy allows.
- instrumentation version, observed time, and envelope checksum.

Forbidden content includes raw/encoded values, payload/body, headers,
credentials, authentication material, SQL parameters, exception text carrying
payloads, reversible tokens, and arbitrary attributes/maps.

## 11. Evidence and Trust Contracts

### 11.1 `EvidenceReference`

Contains immutable S3 URI/version, SHA-256, byte count, media type, schema
ID/version, evidence type, provenance, producer version, artifact/effective
version, retention/legal-hold class, KMS data class, and creation identity/time.

### 11.2 Candidate edge

Every `LineageEdgeCandidate` contains:

- Canonical source and target URNs plus level.
- Transformation as a typed expression/reference where known.
- Channel and path guard.
- Artifact/environment/effective version.
- Evidence references and provenance set.
- Determinants and open/closed hole references.
- Structural and derivational confidence objects, never a shared float.

### 11.3 `VerifiedLineageCandidateSet`

Contains base graph version, deduplicated candidates, G1-G5 results, dropped
edges and returned holes, downgrades, conflicts, unresolved holes, coverage,
both confidence axes with policy/calibration version, and deterministic checksum.

## 12. Review and Publication Contracts

### 12.1 `LineageProposal`

Identity: proposal ID plus immutable version. Contains application, base graph
version, before/after manifests, added/removed/modified/confidence/coverage/
unresolved diffs, evidence/provenance, repository/commit/digest/test context,
lifecycle state, creator, prior proposal version, and checksum.

### 12.2 `ReviewCorrection` and `ReviewLabel`

A correction contains proposal/version, material edge, proposed and corrected
representation, reviewer, rationale, time, and prior checksum. It creates a new
proposal version.

A label contains `engineSaid`, `humanSaid`, edge, provenance, archetype,
repository, commit, reviewer, acknowledgement mode, and time. Bulk acceptance
uses `unreviewed`; only material per-edge acknowledgement becomes a labelled
calibration example.

### 12.3 `AcceptedLineageManifest`

Contains graph version, proposal/version/checksum, expected prior graph version,
application/environment, complete canonical nodes/edges/evidence/confidence,
reviewer/decision/time, policy/analyzer/contract versions, content checksum,
and signature. It is immutable under Object Lock.

### 12.4 Publication control

`PublicationReservation` contains application/environment, proposal/version,
expected prior/target graph versions, lease owner/expiry, monotonically issued
fencing token, and state.

`ActiveGraphPointer` contains environment/application/domain, graph version,
accepted manifest reference/checksum, fencing token, changed time, and
projection watermarks. It advances only in the conditioned publication
transaction.

## 13. Confidence Contract

Each axis uses:

```json
{
  "band": "UNCALIBRATED",
  "evidenceRefs": ["s3://...#sha256=..."],
  "policyVersion": "confidence-v1",
  "calibrationVersion": null,
  "calibrated": false,
  "reasons": ["DETERMINISTIC_REACHABILITY"]
}
```

Bands and numeric thresholds are policy data. Until calibrated against the
labelled corpus, both axes render `UNCALIBRATED`. Lane B exact plan evidence is
the only initial derivational oracle. OTel/runtime execution changes structural
evidence only. Sole-LLM provenance remains capped below the top band.

## 14. Contract Conformance Evidence

Before a contract version is released, retain:

- JSON Schema/OpenAPI lint results.
- Valid, boundary, invalid, privacy, and oversized examples.
- Backward/forward producer-consumer compatibility matrix.
- Canonical serialization and checksum golden files.
- Consumer tests for unknown minor and rejected major versions.
- Proof that forbidden runtime fields and generic maps fail closed.
- Ownership, review, release note, and deprecation date where applicable.
