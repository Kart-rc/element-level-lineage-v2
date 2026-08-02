# C01 Canonical Contracts, URNs, and Identity Resolution PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C01 |
| Status | Approved for implementation |
| Launch phase | Foundation |
| Criticality | P0; every downstream edge and artifact depends on stable identity |
| Primary owner | Lineage platform contracts team |
| Required approvers | Architecture, data governance, security, graph/query owners |
| Upstream dependencies | Governed organization/environment registry; schema/catalog source identifiers |
| Downstream dependencies | C02-C18 |
| Authoritative sources | Component package design §§6, 9; AWS architecture principles 1-4; element-level v2 open question on cross-lane identity |

## 2. Purpose and Outcomes

C01 gives every component the same meaning for an application, repository,
artifact, service, job, dataset, field, endpoint, and effective version. It
publishes versioned schemas and resolves source-native aliases into canonical
URNs without hiding ambiguity.

Measurable outcomes:

- 100% of persisted lineage candidates have resolvable canonical source and
  target URNs or an explicit `AMBIGUOUS_IDENTITY`/`UNKNOWN_IDENTITY` result.
- Replaying the same identity inputs and registry version produces a byte-
  identical resolution result.
- No two distinct authoritative assets acquire the same active canonical URN
  in contract and collision tests.
- New minor contract versions pass every registered producer-consumer
  compatibility suite before release.

## 3. Scope and Non-Goals

### In scope

- Canonical URN grammar, normalization, comparison, parsing, and rendering.
- Entity kinds, environment and effective-version identity.
- Alias registration and source-specific resolvers.
- Resolution precedence, ambiguity, conflict, split, merge, deprecation, and
  redirect behavior.
- Contract registry, semantic version policy, schema publication, examples,
  canonical serialization, and checksums.
- Batch and single-item resolution APIs plus local contract libraries.

### Non-goals

- Discovering repositories/assets (C02).
- Deciding repository eligibility or analysis lane (C04).
- Deciding whether a candidate edge is true (C13).
- Mutating accepted lineage to repair identity. A correction creates a new
  alias/registry version and a new proposal/version.
- Guessing an identity from similarity when multiple candidates remain.

## 4. Actors and Use Cases

| Actor | Job |
|---|---|
| Contract author | Publish a reviewed schema version and examples |
| Adapter/collector developer | Convert source-native IDs into canonical identity inputs |
| Analyzer | Refer to stable fields across files, schemas, engines, and versions |
| Reconciliation engine | Deduplicate evidence and surface unresolved identity conflicts |
| Reviewer | Understand aliases, redirects, environment, and version evidence |
| Query client | Address the active asset and request aliases/version history |
| Operator | Diagnose collision, registry lag, invalid contract, or compatibility failure |

Primary use cases:

1. Resolve a Spark OpenLineage field, a dbt catalog column, a static-parser
   symbol, and an integration sidecar field to the same dataset/field URN.
2. Keep the same artifact deployed to integration and production distinct while
   linking both to the same repository and application.
3. Bind an edge to artifact digest `sha256:...` without changing the logical
   identity used for current traversal.
4. Preserve two plausible candidates as ambiguity rather than selecting one by
   string similarity.
5. Migrate a renamed dataset through an explicit redirect without rewriting
   immutable evidence or accepted manifests.

## 5. Component Boundary

### Owned behavior

- The normative grammar under **Canonical URN Grammar**.
- The contract and alias registries and their immutable version history.
- Deterministic resolution against a pinned registry version.
- Contract artifacts in `contracts/{schemas,openapi,examples}/` and generated
  typed clients/models.

### Upstream inputs

- Governed organization/environment values.
- Source-native system, account, namespace, object, version, and element path.
- Catalog/schema authoritative IDs and source priority.
- Explicit human-governed alias, merge, split, and redirect decisions.

### Downstream outputs

- `CanonicalUrn`, `IdentityAliasRecord`, and `IdentityResolutionResult`.
- Contract schemas, examples, compatibility results, and released client models.

### Forbidden behavior

- Returning one candidate when precedence cannot break a tie.
- Omitting environment from environment-dependent identity.
- Using display labels, mutable repository names, branch names, or empty digest
  values as immutable identity.
- Updating evidence/manifests when an alias changes.
- Releasing a breaking schema change as a minor or patch version.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C01-FR-001 | C01 must parse, validate, normalize, and render the Canonical URN Grammar with round-trip equality for every registered entity kind. | P0 |
| C01-FR-002 | A canonical URN must include organization, environment, kind, namespace, name, and the effective version/element path when required by that kind. | P0 |
| C01-FR-003 | C01 must preserve a logical unversioned identity and separately represent artifact/schema/effective versions so current traversal and historical evidence are both addressable. | P0 |
| C01-FR-004 | Resolution must be deterministic against an explicit registry version and emit the registry/policy version used. | P0 |
| C01-FR-005 | C01 must implement Resolution Precedence: governed catalog ID, authoritative schema ID, explicit registered alias, deployment binding, source-native stable ID, then heuristic candidates requiring review. | P0 |
| C01-FR-006 | Zero candidates must return `UNKNOWN_IDENTITY`; multiple top-precedence candidates must return `AMBIGUOUS_IDENTITY` with all candidate URNs and evidence. | P0 |
| C01-FR-007 | C01 must reject an alias that creates an active collision, an environment leak, an alias cycle, or a redirect cycle. | P0 |
| C01-FR-008 | Alias/redirect/merge/split decisions must be immutable, effective-dated, reviewer-attributed, and superseded only by a new registry version. | P0 |
| C01-FR-009 | Field element paths must use a canonical escaped path representation and preserve nested-array/map semantics without case folding the authoritative field name. | P0 |
| C01-FR-010 | The contract registry must publish machine-readable schema ID, semantic version, owner, Producer, Consumers, compatibility mode, valid/boundary/invalid examples, and release checksum. | P0 |
| C01-FR-011 | C01 must block contract release when a registered producer or consumer compatibility suite fails. | P0 |
| C01-FR-012 | Canonical serialization must sort object keys and unordered identity inputs, normalize Unicode and timestamps, and produce a stable SHA-256 checksum. | P0 |
| C01-FR-013 | Batch resolution must preserve input order, return an outcome for every item, and isolate deterministic invalid items without failing valid neighbors. | P0 |
| C01-FR-014 | Registry reads must support an explicit version and an effective-at timestamp; a run must not observe mixed registry versions. | P0 |
| C01-FR-015 | Deprecated URNs must remain resolvable for historical evidence and return a redirect/deprecation record; they must never be silently rewritten in immutable artifacts. | P0 |
| C01-FR-016 | A new entity kind or alias-source type must be registered as a typed versioned variant before use; arbitrary extension maps are prohibited. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C01-NFR-001 | Single cached resolution must complete within 20 ms p95 and a 1,000-item batch within 500 ms p95 in the production-like performance environment. | P0 |
| C01-NFR-002 | C01 must sustain 5,000 resolution operations per second per Region with horizontal scaling and no cross-tenant cache leakage. | P0 |
| C01-NFR-003 | Registry reads must remain available at 99.95% monthly; callers must be able to use a previously pinned local immutable registry snapshot during a transient control-plane outage. | P0 |
| C01-NFR-004 | Resolution results for identical inputs, registry version, and policy version must be byte-identical across supported language implementations. | P0 |

## 7. Data and Durable State

### Canonical URN Grammar

```text
urn:lineage:<organization>:<environment>:<kind>:<namespace>:<name>[@<effective-version>][#<element-path>]
```

Rules:

- The literal scheme is lower-case `urn:lineage`.
- Organization, environment, kind, and namespace are governed lower-case slugs
  matching `[a-z0-9][a-z0-9._-]{0,127}`.
- Reserved characters in name/path segments use uppercase percent encoding.
- Unicode is NFC-normalized before encoding.
- Kind-specific case rules are registry data. Comparison never uses the host
  locale.
- Effective artifact versions use `sha256-<hex>`; schema/job versions use a
  typed version prefix registered for that kind.
- Nested element paths use JSON Pointer escaping; a kind discriminator retains
  array element, map key, map value, and wildcard semantics.

### Durable records

`IdentityAliasRecord` contains alias source/system/account/native ID, canonical
URN, confidence authority (not edge confidence), evidence, registry version,
effective/expiry, status, reviewer, rationale, prior record, and checksum.

`IdentityResolutionResult` contains input checksum, normalized input, registry
and policy versions, status (`RESOLVED`, `UNKNOWN_IDENTITY`,
`AMBIGUOUS_IDENTITY`, `INVALID_IDENTITY`, `DEPRECATED_IDENTITY`), canonical URN
when singular, candidate list/evidence, redirects, and decision checksum.

S3 stores immutable registry releases and history. DynamoDB holds the effective
alias lookup index keyed by source/account/native identity plus registry
version. Local generated snapshots are checksummed read caches, not authority.

## 8. Interfaces and Contracts

### Resolve one identity

```http
POST /v1/identity:resolve
Idempotency-Key: <input-checksum+registry-version>
```

Request names schema ID/version, registry version (or `effectiveAt`), source
system/account, entity kind, namespace/name, environment, effective version,
element path, authoritative IDs, and evidence references. Response is an
`IdentityResolutionResult`. HTTP mapping:

- `200`: resolved, deprecated, unknown, or ambiguous business outcome.
- `400`: invalid contract/URN input.
- `409`: requested registry version/effective time conflict.
- `429/503`: transient capacity/dependency failure with retry hint.

Unknown/ambiguous are 200 because they are modeled outcomes C13/C15 must expose,
not malformed requests.

### Resolve batch

`POST /v1/identity:resolveBatch` accepts at most 1,000 items and 2 MiB. Each item
has its own input identity and result; all items use one registry/policy version.

### Register alias decision

`POST /v1/identity-alias-decisions` requires governance authorization,
idempotency key, evidence, rationale, effective time, expiry if temporary, and
expected current alias version. It produces a new registry candidate release;
it does not mutate the active registry until review/release succeeds.

### Contract registry

- `GET /v1/contracts/{contractId}/versions/{version}` returns schema, metadata,
  examples, checksum, and compatibility declaration.
- `POST /v1/contracts:checkCompatibility` returns producer and consumer suite
  results against the proposed version.
- Release emits `contract.version.released` through C03 after immutable storage.

All schemas and shared types conform to the [contract catalog](shared/contract-catalog.md).

## 9. Processing and State Model

### Resolution Precedence

For a pinned registry version:

1. Validate and normalize contract input.
2. If an exact governed catalog/schema ID maps to one active canonical URN,
   return it.
3. Otherwise resolve an explicit source-native alias.
4. Otherwise resolve an immutable deployment/artifact binding.
5. Otherwise compare a source-native stable identity under registered kind
   rules.
6. Return heuristic candidates only as `AMBIGUOUS_IDENTITY` or
   `UNKNOWN_IDENTITY`; never promote them automatically.
7. Apply effective-dated redirects to the result metadata, without rewriting
   the queried/evidence identity.
8. Canonically serialize and checksum the complete result.

The resolver evaluates all candidates within a precedence tier before
selection. Multiple active matches at the highest non-empty tier are a
conflict, even when one string is more similar.

### Registry lifecycle

```text
DRAFT -> COMPATIBILITY_CHECKED -> APPROVED -> ACTIVE -> SUPERSEDED
                      \-> REJECTED
```

Activation is atomic by registry version. A run pins one `ACTIVE` version at
start and records it in all outputs. Rollback activates a prior immutable
release as a new active-pointer event; it does not delete the failed release.

## 10. Failure Semantics

| Code | Class | Behavior |
|---|---|---|
| `INVALID_URN` | `DETERMINISTIC_INVALID` | Reject item with failing grammar segment; do not retry |
| `UNKNOWN_IDENTITY` | `INCOMPLETE` business outcome | Preserve input/evidence; surface coverage gap |
| `AMBIGUOUS_IDENTITY` | `CONFLICT` | Return every top candidate; route to C15 when material |
| `ALIAS_COLLISION` | `CONFLICT` | Reject registry proposal; identify both active records |
| `ALIAS_CYCLE` | `DETERMINISTIC_INVALID` | Reject registry proposal with cycle path |
| `REGISTRY_VERSION_NOT_FOUND` | `DETERMINISTIC_INVALID` | Quarantine requesting run/config |
| `REGISTRY_TEMPORARILY_UNAVAILABLE` | `TRANSIENT` | Use pinned verified local snapshot or bounded retry |
| `CONTRACT_INCOMPATIBLE` | `DETERMINISTIC_INVALID` | Block release and retain suite results |
| `DUPLICATE_CONFLICTING_CONTENT` | `CONFLICT` | Preserve checksums; no last-write-wins |

The common [state and error model](shared/state-and-error-model.md) governs
retry, quarantine, DLQ, redrive, replay, and audit.

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C01-SEC-001 | Registry release and alias decisions must require enterprise identity, least-privilege governance role, rationale, evidence, and CloudTrail audit. | P0 |
| C01-SEC-002 | Read APIs must enforce organization/domain isolation and must not expose aliases/evidence from an unauthorized tenant or sensitive metadata class. | P0 |
| C01-SEC-003 | Registry artifacts and indexes must use TLS, KMS encryption, private endpoints, versioning, PITR where applicable, and separate read/write roles. | P0 |
| C01-SEC-004 | Identity input and logs must not contain payload values, credentials, authentication tokens, or arbitrary source attributes; logs use allowlisted fields and hashes. | P0 |
| C01-SEC-005 | Generated client packages must be signed and consumers must verify package integrity and schema checksum in CI. | P1 |

Threat cases include alias poisoning, Unicode/confusable collisions, cross-
environment aliasing, tenant key omission, redirect cycles, registry rollback,
and oversized/pathological parse input. Tests must cover each.

## 12. Scale, Performance, and Availability

- Size for at least 10,000 repositories, 400+ pilot datasets growing to millions
  of fields, all historical artifact versions, and 10,000 deployment decisions
  per day.
- Batch resolution limit is 1,000 items/2 MiB; larger jobs page with one pinned
  registry version.
- Cache keys include organization, environment, registry version, policy
  version, and normalized input checksum.
- Cache TTL may evict resolution results but never registry history.
- DynamoDB partitioning must avoid a single organization/environment hot key;
  load tests use the expected largest namespace and high-alias fields.
- Regional registry artifacts replicate under C18's 15-minute RPO. A verified
  local snapshot supports read continuity within the four-hour RTO objective.

## 13. Observability

| ID | Signal | Required dimensions/alert | Priority |
|---|---|---|---|
| C01-OBS-001 | Resolution count/latency/status | organization, source, kind, registry version; alert p95/SLO | P0 |
| C01-OBS-002 | Unknown/ambiguous/collision rate | application, source, kind, owner; alert on Tier-1 material spike | P0 |
| C01-OBS-003 | Contract compatibility result | contract/version, producer/consumer, failure code | P0 |
| C01-OBS-004 | Registry activation/rollback | actor, old/new version, checksum, rationale; immutable audit | P0 |
| C01-OBS-005 | Cache hit/miss and snapshot age | Region, registry version; alert if pinned snapshot exceeds policy | P1 |

Logs and traces carry the common correlation contract where a collection run
exists. Resolution decisions expose evidence references but not sensitive
metadata bodies. The C17 timeline links material identity conflicts to the
affected run and proposal.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C01-AC-001 | Given canonical examples for every registered kind, when each is parsed, normalized, rendered, and parsed again, then the semantic identity and canonical bytes are equal. |
| C01-AC-002 | Given Spark, dbt, parser, and sidecar aliases for one field, when resolved against one registry version, then all return the same environment-scoped field URN and evidence records the chosen precedence. |
| C01-AC-003 | Given two equal-precedence authoritative candidates, when resolved, then C01 returns `AMBIGUOUS_IDENTITY` with both candidates and no selected URN. |
| C01-AC-004 | Given an alias proposal that crosses tenants/environments or creates a cycle/collision, when submitted, then release is blocked, sanitized audit is emitted, and active registry state is unchanged. |
| C01-AC-005 | Given a compatible minor contract, all registered suites pass before activation; given a removed/changed required field under the same major version, activation fails. |
| C01-AC-006 | Given identical inputs across TypeScript, Python, and Go contract libraries, canonical serialization and SHA-256 golden outputs match byte-for-byte. |
| C01-AC-007 | Given a registry dependency outage, a run pinned to a verified snapshot continues resolution without mixing versions; an unpinned new run fails visibly after bounded retry. |
| C01-AC-008 | Given the performance dataset, single/batch p95 and throughput meet C01-NFR-001/002 with zero cross-tenant result leakage. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C01-CT-001 | Unit/property | Generated valid URNs for every kind, Unicode and reserved characters | Parse -> normalize -> render -> parse | Round-trip equality and stable bytes | Seed, cases, golden checksums |
| C01-CT-002 | Unit/negative | Empty organization, bad percent escape, unsupported kind, empty digest | Validate | Exact `INVALID_URN`; no registry call | Validation report |
| C01-CT-003 | Unit | Same alias inputs in randomized order | Resolve repeatedly | Byte-identical result/checksum | 100-run checksum report |
| C01-CT-004 | Unit/conflict | Two top-precedence catalog IDs map to different URNs | Resolve | `AMBIGUOUS_IDENTITY`; both evidence claims retained | Result fixture |
| C01-CT-005 | Unit/security | Unicode confusable, cross-tenant/environment alias, cycle and collision | Propose alias | Proposal rejected; active version unchanged; sanitized audit | Audit and registry before/after |
| C01-CT-006 | Contract | Current consumers plus additive optional minor field | Run compatibility suite | All consumers pass; release eligible | Compatibility matrix |
| C01-CT-007 | Contract/negative | Remove required field without major bump | Run compatibility suite | `CONTRACT_INCOMPATIBLE`; release blocked | Failure diff |
| C01-CT-008 | Cross-language golden | Shared input JSON for TypeScript/Python/Go | Canonicalize and checksum | Exact byte/checksum equality | Golden artifacts |
| C01-CT-009 | Failure/recovery | Registry API unavailable; valid pinned snapshot | Resolve batch | Uses exact pinned version; warning metric; no version mix | Trace and snapshot checksum |
| C01-CT-010 | Idempotency | Same alias decision/key/content delivered twice | Apply | One registry candidate and two delivery attempts | Conditional-write record |
| C01-CT-011 | Conflict | Same decision key with different checksum | Apply | `DUPLICATE_CONFLICTING_CONTENT`; neither silently overwrites | Conflict record |
| C01-CT-012 | Load | Production-shaped aliases, 1,000-item batches, tenant skew | Sustain target load | C01-NFR-001/002 pass; no hot partition/error loss | Load report/dashboard export |

## 16. Integration Obligations

- **INT-001 C01↔C02:** inventory aliases resolve under the snapshot's pinned
  registry version; invalid/ambiguous items remain explicit inventory gaps.
- **INT-002 C01↔C07/C08/C11:** one canonical multi-lane fixture proves Spark,
  dbt, deterministic parser, and runtime field identifiers converge.
- **INT-003 C01↔C13:** ambiguity prevents candidate deduplication/promotion and
  appears as a conflict with all evidence.
- **INT-004 C01↔C15/C17:** a reviewer can inspect and correct an identity alias;
  correction activates a new registry version and a new proposal version.
- **INT-005 C01↔C16:** published nodes/edges contain valid canonical URNs and a
  graph version cannot mix registry versions.
- **INT-006 C01↔C18:** registry outage, rollback, cross-account denial, audit,
  backup, and restore meet common operational gates.

The shared dependency matrix provides full steps, injected failures, pass
rules, and retained evidence for these IDs.

## 17. Definition of Done

C01 is implemented only when:

- Normative JSON Schemas/OpenAPI, valid/invalid examples, and typed libraries
  exist for all C01-owned contracts.
- Every P0 requirement and C01 component test passes in CI.
- INT-001 through INT-006 pass against production-shaped component versions.
- Cross-language canonicalization golden files match.
- Security tests prove tenant/environment isolation, collision/cycle denial,
  audit, and sensitive-log controls.
- Load/availability tests retain results meeting the stated SLOs.
- Registry release/rollback and ambiguity/collision runbooks are exercised.
- Dashboards and alarms link to owner/runbook and emit in the deployed
  nonproduction environment.
- The traceability matrix links actual run/report/artifact IDs, not a verbal
  assertion of success.

## 18. Implementation Notes

### Approved repository paths

```text
contracts/schemas/identity/
contracts/schemas/shared/
contracts/openapi/identity-api.yaml
contracts/examples/identity/
packages/typescript-contracts/
packages/python-contracts/
packages/go-contracts/
services/identity-resolver/
infra/lib/constructs/contract-registry.ts
tests/contract/identity/
tests/integration/identity/
```

Use TypeScript 5 for the API/control service and contract build, with generated
Python 3.12 and Go 1.24 models. Store immutable registry releases in C12 S3 and
the effective lookup/pointer in DynamoDB. Do not add Neptune as a C01 dependency.

Build order:

1. Grammar and canonical golden fixtures.
2. Schemas, compatibility harness, and generated libraries.
3. Immutable registry release/pointer.
4. Pure resolver and alias conflict detection.
5. APIs and event emission.
6. C02/C07/C08/C11/C13 integrations, then load/security/recovery.

Initial feature flags may gate a new resolver source or entity kind. A flag must
not change canonical grammar or silently fall back from ambiguity to a guess.
Rollback activates a prior immutable registry version and alerts affected runs.

## 19. Traceability

| Source decision | C01 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Canonical URN layer is critical across lanes | C01-FR-001 through C01-FR-009 | C01-CT-001 through C01-CT-005 | INT-001 through INT-005; baseline steel thread |
| Contracts are versioned and governed | C01-FR-010 through C01-FR-016 | C01-CT-006 through C01-CT-011 | Contract compatibility gate |
| Scale to 10,000 repositories | C01-NFR-001 through C01-NFR-004 | C01-CT-012 | Enterprise load gate |
| Least privilege, immutable audit, no payload | C01-SEC-001 through C01-SEC-005 | C01-CT-005/009/011 | INT-006; security/privacy gates |
| No silent identity gaps/conflicts | C01-FR-005 through C01-FR-008; C01-OBS-002 | C01-CT-004/005 | INT-003/004; review steel thread |
