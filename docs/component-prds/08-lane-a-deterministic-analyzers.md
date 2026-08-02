# C08 Lane A Deterministic Analyzers PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C08 |
| Status | Approved for implementation |
| Launch phase | Pilot weeks 4-14 after C07/corpus instrumentation begins |
| Criticality | P0; establishes the provable lineage floor and the complete set of named residual holes |
| Primary owner | Static analysis and analyzer framework team |
| Required approvers | Architecture, language/framework owners, security, trust-engine owner |
| Upstream dependencies | C01 identity/contracts, C04 Lane A route, C05 context/indexes, C06 Batch orchestration, C12 evidence |
| Downstream dependencies | C09, C13-C15, C17-C18 |
| Authoritative sources | Element-level v2 R3/R5/R9; AWS architecture §§8-9, 13-16 |

## 2. Purpose and Outcomes

C08 analyzes readable custom code without a model. It emits only provable edges,
records the exact `DeterminantSet` for every edge and residual, and converts
every unprovable lineage-relevant site into a typed `Hole`. The same immutable
input/version must produce a byte-identical package.

Measurable outcomes:

- 100% of lineage-relevant sink sites in supported fixtures are represented by
  provable edges or named holes; none is silently skipped.
- `holes_opened`, `holes_closed`, unsupported constructs, and coverage are
  attributable by archetype/analyzer/version and reconcile to package content.
- Repeating analysis of one commit/artifact/context/version yields a byte-
  identical `DeterministicAnalysisPackage` and checksum.
- Every edge/hole includes complete determinants sufficient for configuration,
  schema, dependency, build, and source changes to invalidate it.

## 3. Scope and Non-Goals

### In scope

- Analyzer framework and plugin capability/compatibility contract.
- Initial Spring Boot with Kafka serde and FastAPI with Pydantic analyzers;
  Dask follows measured archetype priority.
- Source/schema/build fact extraction, symbol/call/data-flow graph, boundary
  source/sink recognition, deterministic transformations, evidence spans,
  determinants, holes, coverage, and stable package serialization.
- Sandboxed immutable checkout/artifact preparation and content-addressed cache.

### Non-goals

- Resolving uncertain/dynamic sites probabilistically (C09).
- Treating heuristics as provable because they are usually correct.
- Proving executed/live paths (C07/C11/C13).
- Reading or storing production payload values.
- Supporting every language/framework at launch or hiding unsupported code.

## 4. Actors and Use Cases

| Actor/component | Use case |
|---|---|
| Analyzer developer | Implement one archetype plugin against conformance/golden tests |
| C06 | Run isolated Batch analysis with pinned resources/versions |
| C09 | Receive bounded holes and approved analysis tools/facts |
| C13 | Verify provable edges/evidence/reachability and merge resolutions |
| Application owner | Inspect deterministic evidence, holes, unsupported constructs, and coverage |
| Operator | Diagnose parser crash/resource limit/determinism regression and replay cached work |

## 5. Component Boundary

### Owned behavior

- Analyzer SPI, supported construct/capability declaration, parsing/semantic fact
  graph, provable-edge rule, hole inventory, determinants, stable package.

### Inputs

- Immutable repository source snapshot or built source artifact reference and
  checksum, repository/commit/artifact/environment.
- C05 context, schemas/contracts/dependencies/config manifests, C01 registry.
- Analyzer/policy/toolchain version and resource budget.

### Outputs

- `DeterministicAnalysisPackage`, `LineageEdgeCandidate` with deterministic
  provenance, `Hole`, `DeterminantSet`, analyzer facts/tool indexes, coverage.

### Forbidden behavior

- Emitting an edge without a mechanically traceable source-to-sink proof and
  evidence span/fact references.
- Dropping an unresolved site, unsupported construct, parse error, or resource-
  limited file from coverage.
- Calling a model/LLM or unapproved network service.
- Treating unresolved dependency/configuration as a default implementation.
- Producing timestamps/random IDs/noncanonical iteration in package content.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C08-FR-001 | C08 must analyze an immutable repository commit/source snapshot and bind every package to repository, commit, artifact digest/environment where available, context, C01, analyzer, policy, and toolchain versions. | P0 |
| C08-FR-002 | The analyzer framework must require each plugin to declare languages/frameworks/versions, supported sources/sinks/transforms/configuration, unsupported constructs, required build facts, and resource profile. | P0 |
| C08-FR-003 | Initial P0 plugins must cover Spring Boot with Kafka serializers/deserializers and FastAPI with Pydantic request/response/event models; unsupported versions/features must remain explicit. | P0 |
| C08-FR-004 | C08 must emit only provable edges backed by normalized source/sink symbols, a deterministic data-flow/reachability proof, and file:line evidence spans/fact IDs. | P0 |
| C08-FR-005 | Every lineage-relevant site that cannot be proved must emit a `Hole` with stable hole ID, source location, reason, affected sink, candidate scope/facts, determinants, and state; it must not be omitted. | P0 |
| C08-FR-006 | Required hole reasons must include dynamic dispatch, reflection, dependency injection ambiguity, opaque/external call, dynamic SQL/query, unsupported syntax/framework/version, missing schema/dependency/build/config, alias ambiguity, parse failure, and resource limit. | P0 |
| C08-FR-007 | C08 must publish `holes_opened`, deterministic edges, unsupported sites, analyzed/skipped-with-reason files/sinks/fields, and coverage denominators that reconcile to package records. | P0 |
| C08-FR-008 | The same normalized inputs/versions must produce byte-identical facts, edges, holes, determinants, ordering, serialization, and package checksum across repeated/parallel runs. | P0 |
| C08-FR-009 | Every edge and hole must carry a complete `DeterminantSet`, including files, symbols, schemas, configuration keys, build/generated inputs, dependency/contract versions, and analyzer/policy/toolchain versions that can change the result. | P0 |
| C08-FR-010 | C08 must model configuration/dependency injection/profile/feature-flag choices as facts and emit a hole when a unique target cannot be selected; changed configuration key must invalidate affected results through C05. | P0 |
| C08-FR-011 | Supported transforms must be typed (direct/rename/cast/constant/arithmetic/concatenate/conditional/aggregate/collection path) with cited proof; unsupported or partially known expression becomes a hole rather than free-text certainty. | P0 |
| C08-FR-012 | Analyzer output must be content-addressed by source/artifact/context/schema/dependency/config/analyzer/policy/toolchain checksums and reusable only when every key part matches. | P0 |
| C08-FR-013 | C08 must expose read-only bounded analysis facts used by C09: symbol resolution, source spans, call graph, data-flow facts, schema lookup keys, and hole-scoped candidate context. | P0 |
| C08-FR-014 | Repository preparation/build steps must be declared, sandboxed, network-denied by default, dependency-pinned, resource/time bounded, and recorded; inability to build/resolve must become explicit incomplete/holes. | P0 |
| C08-FR-015 | A parser crash/resource timeout must isolate the workload/file, preserve completed facts, emit explicit incomplete coverage, and never return a deceptively complete package. | P0 |
| C08-FR-016 | Analyzer investment and supported construct expansion must be prioritized from C15 correction rate/holes by archetype, not unmeasured assumptions. | P1 |
| C08-FR-017 | A Dask custom-code analyzer may activate only after the common conformance, golden, determinism, determinant, security, and correction-measurement gates pass. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C08-NFR-001 | A representative medium repository must analyze within 15 minutes p95 and 95% of targeted incrementals within five minutes p95 at approved Batch resource classes. | P0 |
| C08-NFR-002 | C08 must support 500 concurrent repository jobs and complete the 10,000-repository baseline within C06's 12-hour platform window under validated cache/size distributions. | P0 |
| C08-NFR-003 | Analyzer determinism must be proven by 100 repeated runs and cross-worker/Region golden checks with zero checksum divergence. | P0 |
| C08-NFR-004 | One crash/resource-exhausted/malicious repository must not affect another tenant/workload or retain source in a reused workspace. | P0 |

## 7. Data and Durable State

`AnalyzerRequest` contains immutable source/context/schema/dependency/config
references/checksums, repository/commit/artifact/environment, workload/path,
archetype/lane, C01/analyzer/policy/toolchain versions, and resource budget.

`DeterministicAnalysisPackage` contains:

- request/input checksums and analyzer capability statement.
- normalized source file/symbol/schema/config/dependency facts.
- call/data-flow graphs as checksummed indexed artifacts.
- provable edge candidates with proof/evidence/determinants.
- `Hole` records and unsupported/parse/resource-limit records.
- file/sink/field/construct counts and coverage/status.
- stable package schema/serialization/checksum and immutable evidence refs.

Stable `holeId` is a hash of repository/workload, semantic sink identity,
normalized source location/symbol, reason class, affected sink, and analyzer
major version; line-only movement uses symbol/AST identity to avoid needless
label churn where possible.

Operational state tracks request/idempotency/cache/attempt/status and ephemeral
workspace cleanup. C12 S3 is package authority; C05 indexes determinants; C09
reads hole-scoped fact indexes through controlled tools.

## 8. Interfaces and Contracts

### Analyzer SPI

```text
capabilities() -> supported language/framework/version/source/sink/transform facts
prepare(request, workspace) -> pinned build/schema/config facts or explicit gaps
analyze(workload, facts) -> provable candidates, holes, determinants, coverage
canonicalize(output) -> DeterministicAnalysisPackage bytes/checksum
```

Plugins cannot write directly to graph/proposals or call C09/model services.

### Batch invocation/result

C06 submits `AnalyzerRequest` by S3 reference/checksum. The container writes
package/fact indexes to attempt-scoped C12 prefixes, reads them back/verifies,
then conditionally registers status. Result event carries only reference,
checksum, counts, coverage, cache identity, and correlation.

### Tool fact access

C09 calls C08-owned read-only operations with hole scope/authorization:
`read_span`, `resolve_symbol`, `call_graph`, and schema/fact references. Search
is constrained to the immutable source snapshot and returns paths/spans, not a
whole repository dump.

## 9. Processing and State Model

```text
REQUESTED -> CACHE_CHECK -> WORKSPACE_PREPARE -> FACT_EXTRACTION
          -> DATAFLOW_ANALYSIS -> HOLE_ACCOUNTING -> CANONICALIZE
          -> PACKAGE_VERIFY -> COMPLETE
```

Alternative: `COMPLETE_WITH_HOLES`, `INCOMPLETE`, `UNSUPPORTED`, `QUARANTINED`,
`FAILED_RESOURCE`, `FAILED`.

Algorithm:

1. Validate/pin inputs; check exact content-addressed package cache.
2. Create isolated encrypted workspace; materialize exact commit/source and
   verify checksum; load only pinned schemas/dependencies/config facts.
3. Parse and build normalized AST/symbol/call/data-flow/config graphs.
4. Enumerate lineage boundary sources/sinks and transformations.
5. Emit a candidate only when deterministic rules prove source-to-sink mapping,
   transformation, and reachable semantic path.
6. Emit a stable Hole for each remaining lineage-relevant site and record all
   unsupported/incomplete coverage.
7. Compute determinants and coverage reconciliation; canonical sort/serialize.
8. Write/read-back package/facts, register cache/status, emit result, and destroy
   workspace in finally.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `SOURCE_CHECKSUM_MISMATCH` | `DETERMINISTIC_INVALID` | Quarantine; no analysis/cache |
| `UNSUPPORTED_LANGUAGE_FRAMEWORK` | `INCOMPLETE` | Explicit unsupported coverage/package; no guessed edges |
| `PARSE_FAILURE` | `INCOMPLETE`/defect | Isolate file/site, emit hole/coverage; alert analyzer defect if supported construct |
| `BUILD_FACTS_MISSING` | `INCOMPLETE` | Emit affected holes/coverage; no default dependency/config |
| `RESOURCE_LIMIT` | `INCOMPLETE` | Terminate bounded job, preserve valid completed facts, mark incomplete |
| `NONDETERMINISTIC_OUTPUT` | `DETERMINISTIC_INVALID` defect | Do not activate/cache; retain diff and block analyzer version |
| `CACHE_CONTENT_CONFLICT` | `CONFLICT` | Preserve checksums; quarantine cache key/version |
| `BATCH_CAPACITY_OR_STORE_FAILURE` | `TRANSIENT` | Bounded retry with same input/cache identity |
| `WORKSPACE_CLEANUP_FAILED` | `INCOMPLETE` security-critical | Isolate worker, alert/audit; do not reuse workspace |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C08-SEC-001 | Batch jobs must use short-lived source credentials, tenant/run-specific roles, private subnets/endpoints, controlled or denied egress, and exact C12 prefixes/KMS keys. | P0 |
| C08-SEC-002 | Workspaces must be encrypted, unique, nonshared, destroyed in finally, and verified absent before worker reuse; source/artifacts must not enter logs. | P0 |
| C08-SEC-003 | Build scripts/plugins/dependencies run sandboxed with pinned digests, no privilege escalation/host mounts, resource limits, and untrusted-repository threat controls. | P0 |
| C08-SEC-004 | Analyzer packages/evidence may contain metadata, symbols, source file:line spans and minimal cited snippets under ABAC, but must not contain credentials, payload values, secret config values, or unbounded source dumps. | P0 |
| C08-SEC-005 | Analyzer/plugin/toolchain releases must be signed/versioned, pass SAST/dependency/container/conformance/determinism tests, and emit immutable activation audit. | P0 |

## 12. Scale, Performance, and Availability

- Analyzer resource classes are measured by archetype/repository size/fact graph,
  with CPU/memory/disk/time limits and an oversized-workload explicit path.
- Content cache avoids repeated full analysis for identical artifacts/contexts;
  cache hit bypasses Batch only after checksum/schema/authorization verification.
- C06 caps concurrency from validated Batch/source/schema/C12 quotas; Tier-1
  incremental capacity is reserved from baseline/backfill.
- Large facts/packages move through S3 references; Step Functions/Lambda payloads
  remain small.
- Containers/artifacts are reproducible and available in warm Region; immutable
  packages replicate and operational cache/index rebuilds within C18 RPO/RTO.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C08-OBS-001 | Analysis duration/resource/status | archetype/analyzer/version/repo size/priority | P0 |
| C08-OBS-002 | Deterministic edges and `holes_opened` | reason/archetype/framework/version/application | P0 |
| C08-OBS-003 | Coverage/unsupported/parse/build/resource gaps | file/sink/field/construct and owner | P0 |
| C08-OBS-004 | Determinant completeness/invalidation | kind/analyzer/archetype; missing determinant alert | P0 |
| C08-OBS-005 | Determinism/cache | checksum divergence, cache hit/conflict by version | P0 |
| C08-OBS-006 | Workspace/security | cleanup, egress, sandbox, secret scan; immediate alert | P0 |
| C08-OBS-007 | Correction rate feedback | deterministic provenance/archetype/analyzer version | P1 |

Metrics reconcile every enumerated lineage-relevant sink to deterministic
candidate or hole/unsupported/incomplete record. A percentage without numerator,
denominator, and gap reasons is not accepted.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C08-AC-001 | Given golden Spring Boot/Kafka and FastAPI/Pydantic fixtures, C08 emits exactly the provable mappings/transforms and one named hole for every uncertain sink/site. |
| C08-AC-002 | Given identical pinned inputs in 100 repeated/parallel/cross-worker runs, package bytes/checksum are identical. |
| C08-AC-003 | Given configuration-only dependency injection change, affected determinants select/recompute different implementation facts and no stale edge survives incremental analysis. |
| C08-AC-004 | Given dynamic dispatch/reflection/opaque call/unsupported syntax, C08 emits typed holes/coverage and never a heuristic edge. |
| C08-AC-005 | Given parser/resource failure, valid completed facts remain attributable but package is visibly incomplete and cannot masquerade as full coverage. |
| C08-AC-006 | Given identical cache key, package is reused after checksum/authorization; changing any source/schema/config/dependency/analyzer/policy/toolchain key prevents stale reuse. |
| C08-AC-007 | Given malicious repository/build input, sandbox/network/credential/workspace controls prevent escape/exfiltration and isolate other jobs. |
| C08-AC-008 | Enterprise load meets C08 NFRs with exact requested/completed/cached/incomplete reconciliation and Tier-1 incremental performance. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C08-CT-001 | Golden/Spring | Kafka serde, mapper, branch, DI, config, schema fixture | Analyze | Exact provable edges/transforms/holes/determinants | Package golden |
| C08-CT-002 | Golden/FastAPI | Pydantic aliases/nesting/validation/response/events fixture | Analyze | Exact expected package/coverage | Package golden |
| C08-CT-003 | Hole coverage | Dynamic/reflection/opaque/unsupported/missing inputs | Analyze | One stable typed hole per site; no guessed edge | Hole manifest |
| C08-CT-004 | Determinism | Same fixture 100 times, randomized worker/hash order, two Regions | Analyze | Byte-identical package/checksum | Determinism report |
| C08-CT-005 | Determinants | Source/schema/config/build/dependency variants | Change one input/plan | Exact affected results, no changed-file-only gap | Invalidation matrix |
| C08-CT-006 | Config injection | Only profile/qualifier/configuration key changes | Analyze incrementally | Correct implementation edge/hole replacement | Before/after package |
| C08-CT-007 | Cache | Same and one-key-changed requests | Lookup/analyze | Exact hit or required miss; conflict quarantined | Cache records |
| C08-CT-008 | Failure isolation | Parse exception, timeout, memory/disk limit | Analyze | Explicit incomplete/coverage; neighbor jobs succeed | Batch/results |
| C08-CT-009 | Security | Malicious build/plugin, egress, secret file/log, workspace residue | Analyze/scan | Denied/redacted/isolated/cleaned; audit/alert | Security report |
| C08-CT-010 | Contract | Analyzer plugin versions/capabilities and invalid package | Run conformance | Supported plugins pass; invalid/unknown rejected | Conformance report |
| C08-CT-011 | Tool facts | Hole-scoped span/symbol/call/schema requests | Query | Exact bounded read-only facts; unauthorized scope denied | Tool response/audit |
| C08-CT-012 | Load/recovery | 10,000 distribution, 500 concurrency, cache mix, worker/Region restart | Execute/rebuild | Window/NFRs/exact reconciliation/cleanup | Load/recovery report |

## 16. Integration Obligations

- **INT-049 C01/C04/C05↔C08:** Lane A request pins identity/context/config/
  dependency/determinants and wrong lane/version/checksum fails closed.
- **INT-050 C06↔C08:** Batch submit/budget/heartbeat/result/retry/redrive/cache and
  workspace finally behavior pass.
- **INT-051 C08↔C09:** only named open holes expose bounded approved facts/tools;
  deterministic edges cannot be rederived/overwritten.
- **INT-052 C08↔C12:** immutable packages/facts/cache keys, duplicate/conflict,
  retention, access, replication, and rebuild preserve authority/checksum.
- **INT-053 C08↔C13:** provable edges and holes pass G1/G2/G4 semantics;
  verification drops return the stable hole and coverage counts reconcile.
- **INT-054 C08↔C14/C15/C17:** drift, before/after review, evidence/holes/
  determinants/coverage, and correction labels are visible and versioned.
- **INT-055 C08↔C18:** sandbox/privacy/determinism/load/failure/reconciliation/
  DR dashboards and runbooks pass.

## 17. Definition of Done

- Analyzer framework, Spring/FastAPI P0 plugins, contracts, golden fixtures,
  deterministic package/facts/hole/determinant generation, cache, and sandboxed
  Batch images are implemented.
- C08 P0 requirements and C08-CT-001 through C08-CT-012 pass.
- INT-049 through INT-055 pass against production-shaped components.
- The fixture corpus proves every expected sink is candidate or named gap and
  determinism has zero checksum divergence.
- Config-only/determinant/full-scan cases prove incremental soundness boundaries.
- Load/security/recovery reports meet NFRs and prove tenant/workspace isolation,
  controlled egress, secret/payload absence, exact reconciliation, and cleanup.
- Analyzer defect/resource/cache/determinism/security runbooks and dashboards
  are exercised with real evidence IDs.

## 18. Implementation Notes

```text
contracts/schemas/analysis/
workers/analyzer/framework/
workers/analyzer/plugins/spring-kafka/
workers/analyzer/plugins/fastapi-pydantic/
workers/analyzer/plugins/dask/
workers/analyzer/tools/
infra/lib/constructs/analyzer-batch.ts
tests/fixtures/analyzers/{spring,fastapi,dask}/
tests/contract/analyzers/
tests/integration/analyzers/
tests/load/analyzers/
tests/security/analyzers/
```

Use Python 3.12 for framework/plugins and language-appropriate deterministic
parsers (for example compiler AST/symbol APIs or pinned parser libraries), all
pinned in container digests. Canonical serialization must not depend on Python
set/dict/hash/random/wall-clock behavior. Source span evidence uses immutable
commit paths/lines and quote hashes under ABAC.

Build order: common facts/contracts/goldens; Spring; FastAPI; determinism/
determinants/cache; fact tools; C09/C13; load/security/DR. Dask activates only
after measured correction/coverage justifies priority and all gates pass.

## 19. Traceability

| Source decision | C08 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Deterministic floor and named holes | C08-FR-001 through C08-FR-007/011 | C08-CT-001/002/003/010 | INT-049/053; Lane A parser gate |
| Byte-identical and content-addressed | C08-FR-008/012; C08-NFR-003 | C08-CT-004/007 | INT-050/052 |
| Determinant incremental soundness | C08-FR-009/010 | C08-CT-005/006 | INT-049/054; incremental gate |
| Bounded failure/security/scale | C08-FR-014/015; C08-NFR-001-004; C08-SEC-001-005 | C08-CT-008/009/012 | INT-050/055; enterprise/security gates |
| Agent receives holes/tools only | C08-FR-013 | C08-CT-011 | INT-051 |
