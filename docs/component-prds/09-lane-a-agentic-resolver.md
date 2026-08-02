# C09 Lane A Agentic Residual Resolver PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C09 |
| Status | Approved for implementation after C07 oracle and C15 corpus instrumentation |
| Launch phase | Pilot weeks 10-20; observation before enforcement |
| Criticality | P0 for declared Lane A residual scope; probabilistic output is always bounded and verified downstream |
| Primary owner | Lineage inference and tools team |
| Required approvers | Architecture, AI governance, security/privacy, analyzer/trust-engine owners |
| Upstream dependencies | C01, C05, C06, C08 open holes/facts, C12 cache, approved enterprise model gateway |
| Downstream dependencies | C13-C15, C17-C18 |
| Authoritative sources | Element-level v2 R4-R7; AWS architecture §§6.6, 11, 14, 16 |

## 2. Purpose and Outcomes

C09 resolves only named residual holes that deterministic analysis could not
prove. It uses a fixed set of bounded, read-only analysis tools and one guarded
`emit_edge` operation. Every proposed edge cites immutable file:line spans and
remains probabilistic until C13 applies G1-G5. A shared content-addressed result
turns the first governed resolution into a reproducible estate-wide artifact.

Measurable outcomes:

- 100% of C09 executions reference an open C08/C13 hole; zero whole-repository
  or already-resolved-edge tasks.
- 100% of proposed edges include file:line evidence, quote hashes, tool/fact
  provenance, artifact/context identity, and budget/model/prompt versions.
- Budget exhaustion, tool failure, insufficient evidence, or ambiguity returns
  unresolved. Never a guess on timeout.
- Identical cache identity returns the same immutable accepted resolution across
  CI runners, applications, and retries.

## 3. Scope and Non-Goals

### In scope

- Hole eligibility/policy, bounded task construction, enterprise gateway call,
  tool authorization/execution, `emit_edge` prevalidation, budgets, result
  canonicalization, content-addressed cache, telemetry, and audit.
- Initial residual types for supported Spring/FastAPI analyzers, expanding only
  with measured correction/benefit.

### Non-goals

- Reading an entire repository into a model context.
- Re-deriving or modifying deterministic edges.
- Executing on developer machines or in production.
- Assigning final confidence or publishing graph state.
- Returning an edge merely to meet a coverage target.
- Using a model-family self-judge as correctness evidence.

## 4. Actors and Use Cases

| Actor/component | Use case |
|---|---|
| C08 | Submit stable open hole plus bounded facts/tools |
| C06 | Enforce CI-only job, quota, timeout, priority, and cost budget |
| Model agent | Investigate one hole through approved structured tools |
| C13 | Re-read citations, check reachability/type/oracle, drop/downgrade/accept candidate |
| Reviewer/C15 | Correct material proposals and generate provenance/archetype labels |
| AI/security operator | Approve model/prompt/tool policy and audit usage/failures |

## 5. Component Boundary

### Owned behavior

- Hole-only admission and task envelope.
- Tool gateway for `search`, `read_span`, `resolve_symbol`, `call_graph`,
  `schema_lookup`, and `emit_edge`.
- Budget/model/prompt policy, immutable `AgentResolution`, shared cache, and
  unresolved reasons.

### Inputs

- Open `Hole`, C08 package/fact index, C01/context/schema versions, artifact
  digest/environment, policy and resource budget.

### Outputs

- `AgentResolution`: verified-as-well-formed candidate proposals or unresolved,
  citations/tool transcript references, cache identity, budgets, versions.

### Forbidden behavior

- Accepting a free-form repository archive or arbitrary tool/plugin.
- Calling `emit_edge` without citations/evidence or outside the hole's affected
  sink/scope.
- Model/network access from developer or production environments.
- Retrying until a preferred answer changes under the same cache key.
- Letting repository text/instructions modify system/tool/security policy.
- Claiming top-band confidence or correctness before C13/human evidence.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C09-FR-001 | C09 must admit only a valid open `Hole` from an immutable C08/C13 package and reject a deterministic-resolved, closed, stale-version, or arbitrary task. | P0 |
| C09-FR-002 | The task must be hole-only: hole ID/reason/location/affected sink, bounded candidate facts, pinned artifact/context/schema/analyzer/policy versions, approved tools, and budgets; it must not include the repository as context. | P0 |
| C09-FR-003 | The only model-visible tools must be `search`, `read_span`, `resolve_symbol`, `call_graph`, `schema_lookup`, and `emit_edge`, each with strict typed input/output and per-hole authorization. | P0 |
| C09-FR-004 | `search` must return bounded paths/symbols/spans from the immutable snapshot; it must not return unbounded files, binary content, secrets, or ignored/unauthorized paths. | P0 |
| C09-FR-005 | `read_span` must require exact file/range limits and return normalized text plus commit/path/line and quote hash; `resolve_symbol`, `call_graph`, and `schema_lookup` must return C08/C01/C05 facts with versions. | P0 |
| C09-FR-006 | `emit_edge` must reject an edge outside the hole sink/scope or missing canonical endpoints, typed transformation/path, determinants, and at least one immutable file:line citation with quote hash. | P0 |
| C09-FR-007 | C09 must enforce per-hole limits for turns, tool calls, input/output tokens, cited bytes, wall time, and estimated cost; every call/result records remaining budget. | P0 |
| C09-FR-008 | Budget exhaustion, ambiguity, unsupported evidence, tool/gateway failure after bounded retry, or no defensible mapping must return unresolved with a typed reason and must never emit a guess. | P0 |
| C09-FR-009 | C09 must operate only through the approved enterprise gateway in registered CI analysis accounts; developer-machine and production execution must be technically denied and audited. | P0 |
| C09-FR-010 | Resolution/cache identity must be `codeSliceHash + schemaHash + modelVersion + promptVersion + toolPolicyVersion` plus semantic hole/analyzer major version where needed to prevent collisions. | P0 |
| C09-FR-011 | The first conditionally accepted complete result for a cache identity must be immutable/shared; repeated/racing execution returns it and conflicting content enters cache conflict rather than overwriting or rerunning for a different answer. | P0 |
| C09-FR-012 | Any source/schema/model/prompt/tool policy/hole semantic change must create a new cache identity; invalidation/deprecation must preserve prior result/audit and require governed policy. | P0 |
| C09-FR-013 | `AgentResolution` must record hole, candidates/unresolved, every cited evidence/tool fact reference, minimal transcript metadata, model/prompt/tool versions, budgets, gateway request ID, input/output checksum, and policy decision. | P0 |
| C09-FR-014 | C09 must treat repository/schema text as untrusted data, isolate it from system/tool instructions, and deny prompt-injected requests to exfiltrate, change policy, call unregistered tools, or broaden scope. | P0 |
| C09-FR-015 | C09 must not set final confidence; it must label all candidates sole-LLM provenance pending C13 verification/oracle/human outcomes. | P0 |
| C09-FR-016 | Metrics must reconcile holes submitted, cache hits, resolved, unresolved by reason, candidate emissions/rejections, verification outcomes, corrections, cost, and latency by archetype/model/prompt. | P0 |
| C09-FR-017 | Model/prompt/tool policy rollout must use a labelled offline eval, canary, correction-rate monitoring, version pinning, rollback, and no automatic enforcement expansion. | P0 |
| C09-FR-018 | Additional tools or autonomous multi-hole/repository tasks require a new major policy/security review and are outside initial scope. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C09-NFR-001 | A cache hit must return within 500 ms p95; an uncached resolution must finish or return typed unresolved within the configured maximum 10 minutes. | P0 |
| C09-NFR-002 | C09 must enforce organization/domain/priority concurrency, daily token/cost budgets, and Bedrock quota without delaying Tier-1 deterministic work. | P0 |
| C09-NFR-003 | Cache/content/result availability must be 99.9% monthly; gateway unavailability degrades to unresolved/deferred, never blocks deterministic package completion or invents edges. | P0 |
| C09-NFR-004 | No sensitive/unauthorized source content may cross the gateway boundary or appear in telemetry/transcripts; test corpus exfiltration rate must be zero. | P0 |

## 7. Data and Durable State

`AgentTask` contains hole/package/fact refs and checksums, allowed repository
paths/symbols/schemas/sink, C01/context/artifact/environment/analyzer/policy,
model/prompt/tool versions, CI environment attestation, per-dimension budgets,
cache identity, and correlation.

`ToolCallRecord` contains task/hole/turn/tool, typed sanitized arguments/result
reference/checksum, authorization decision, start/end, bytes/tokens/cost, error,
and remaining budget. Source content remains in restricted evidence; broad
operational records store paths/hashes only.

`AgentResolution` contains:

- status `RESOLVED_CANDIDATE`, `UNRESOLVED`, `REJECTED`, or `CONFLICT`.
- candidate source/target/typed transform/path/determinants.
- file:line citations and quote hashes plus C08 fact/tool references.
- unresolved/rejected reasons.
- cache identity, immutable input/result checksums, model/prompt/tool/gateway
  versions/IDs, budgets used, provenance `LLM_RESIDUAL`, created time.

S3 stores immutable task/results/restricted evidence. DynamoDB conditionally
indexes cache identity/status and budgets/leases. Bedrock/gateway logs follow
enterprise no-training/retention settings and must not become product authority.

## 8. Interfaces and Contracts

### Submit/lookup

- `POST /v1/agent-resolutions` accepts `AgentTask` S3 reference/checksum and
  idempotency. It verifies CI/account/hole/cache/policy before queue/admission.
- `GET /v1/agent-resolutions/by-cache-key/{hash}` returns authorized immutable
  result reference/status, never another tenant's restricted evidence.

### Tool contracts

- `search(query, pathAllowlist, resultLimit<=50)` -> file/symbol/span metadata.
- `read_span(path, startLine, endLine<=start+200)` -> text/ref/quote hash.
- `resolve_symbol(symbolOrLocation, depth<=policy)` -> canonical fact/ambiguity.
- `call_graph(symbol, direction, depth<=policy, nodeLimit)` -> bounded fact graph.
- `schema_lookup(schemaOrField, version)` -> canonical schema facts/ambiguity.
- `emit_edge(holeId, source, target, transform, path, citations,
  determinants)` -> accepted-as-well-formed or exact rejection.

Tools require task token/hole scope and record every decision. `emit_edge`
writes only attempt-scoped candidate output, never C13/proposal/graph.

## 9. Processing and State Model

```text
SUBMITTED -> VALIDATING_HOLE -> CACHE_LOOKUP
          -> ADMITTED -> INVESTIGATING -> EMIT_OR_UNRESOLVED
          -> CANONICALIZE -> CONDITIONAL_CACHE_WRITE -> COMPLETE
```

Alternative: `CACHE_HIT`, `DEFERRED_QUOTA`, `REJECTED`, `UNRESOLVED`,
`CACHE_CONFLICT`, `FAILED_TRANSIENT`.

1. Verify task/source/checksum, open hole/current versions, CI attestation,
   policy, path/tool scope, and budgets.
2. Look up exact cache key. Return authorized immutable result when present.
3. Acquire per-key lease/admission and call enterprise gateway with fixed system
   policy and hole envelope; repository text is explicitly untrusted data.
4. Validate/authorize each typed tool call and decrement budgets before result.
5. `emit_edge` performs scope/contract/citation/determinant prechecks; agent may
   instead conclude unresolved.
6. At any exhausted/uncertain state, stop and create typed unresolved.
7. Canonicalize/checksum and conditionally create shared cache result. A racing
   prior result wins; conflicting bytes become conflict for investigation.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `HOLE_NOT_OPEN_OR_STALE` | `DETERMINISTIC_INVALID` | Reject task; do not call model |
| `ENVIRONMENT_NOT_CI` | `DETERMINISTIC_INVALID` security | Deny/audit/alert; no gateway call |
| `TOOL_SCOPE_DENIED` | `DETERMINISTIC_INVALID` security | Reject call; count; terminate task by policy |
| `CITATION_REQUIRED_OR_STALE` | `DETERMINISTIC_INVALID` candidate | Reject emission; allow bounded correction or unresolved |
| `BUDGET_EXHAUSTED` | `INCOMPLETE` | `UNRESOLVED`; no guess/retry under same task |
| `INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE` | `INCOMPLETE` | `UNRESOLVED` with evidence/reason |
| `GATEWAY_THROTTLED_UNAVAILABLE` | `TRANSIENT` | Bounded retry/defer, then unresolved; deterministic work unaffected |
| `CACHE_CONTENT_CONFLICT` | `CONFLICT` | Preserve results/checksums; quarantine model/prompt/key; no overwrite |
| `PROMPT_INJECTION_ATTEMPT` | `DETERMINISTIC_INVALID` security | Deny requested scope/tool, sanitize audit, task unresolved/rejected |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C09-SEC-001 | IAM/SCP/network policy must allow gateway invocation only from approved CI analysis roles/accounts and explicitly deny production/developer identities. | P0 |
| C09-SEC-002 | The task builder must minimize context to hole facts/cited spans and scan/redact credentials, secrets, payload values, personal data beyond allowed metadata, and ignored/restricted paths before gateway exposure. | P0 |
| C09-SEC-003 | Tool service must enforce per-task capability tokens, path/symbol/schema allowlists, byte/depth/result limits, read-only operation except attempt-scoped `emit_edge`, and complete audit. | P0 |
| C09-SEC-004 | Repository content is untrusted; system/tool policy is out-of-band and immutable for a task; prompt-injected instructions cannot alter tool schema, permissions, budgets, model, or destination. | P0 |
| C09-SEC-005 | S3/cache/budget state must use KMS/private access, domain ABAC, immutable/versioned results, strict retention, and separate task-builder/tool/model/cache roles. | P0 |
| C09-SEC-006 | Enterprise gateway settings must prohibit model training on inputs, use approved Region/model, enforce retention policy, and expose auditable request IDs without broad prompt logging. | P0 |

## 12. Scale, Performance, and Availability

- C06 routes residuals through a separate SQS/admission pool; deterministic and
  Tier-1 workflows cannot be starved by model quota.
- Cache is estate-wide by content but authorization is checked on every lookup;
  source snippets are not exposed cross-tenant even when a semantic result is
  safely reusable under policy.
- Budgets are configured by hole reason/archetype/priority and capped globally/
  per organization/domain/model. Exhaustion is a valid unresolved outcome.
- Rate-limit/circuit-breaker prevents a gateway/model defect from generating
  cost/retry storms. Deterministic proposals may proceed with open holes.
- Immutable cache/results replicate under C18 RPO; operational leases/budgets
  restore/rebuild. A model service is not in the graph query/publication path.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C09-OBS-001 | Hole submission/cache/result | archetype/reason/model/prompt/tool policy/status | P0 |
| C09-OBS-002 | Tool calls/rejections/budgets | tool/reason/turn/bytes/tokens/cost | P0 |
| C09-OBS-003 | Candidate/unresolved/rejection | reason/provenance/application/domain | P0 |
| C09-OBS-004 | Gateway latency/throttle/error | model/Region/account/request class | P0 |
| C09-OBS-005 | Verification/correction rate | G1-G5 outcome, archetype, model/prompt/tool version | P0 |
| C09-OBS-006 | Security/privacy | non-CI, prompt injection, scope deny, secret scan, egress | P0 |
| C09-OBS-007 | Cache conflict/hit/cost avoidance | key version/model/archetype | P1 |

No dashboard treats self-reported model confidence as accuracy. Advancement uses
C13 verification and C15 labelled correction rates by provenance/archetype.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C09-AC-001 | Given a valid open hole, C09 exposes only approved bounded tools/facts and any emitted candidate cites exact immutable file:line spans/quote hashes within the hole scope. |
| C09-AC-002 | Given a resolved/closed/stale hole or request to rederive a deterministic edge, C09 rejects before model invocation. |
| C09-AC-003 | Given token/turn/tool/time/cost exhaustion or ambiguous evidence, C09 returns typed unresolved and emits no edge. |
| C09-AC-004 | Given identical cache identity on two racing CI runners, one immutable result is accepted and both return it; different content becomes conflict, not overwrite/rerun selection. |
| C09-AC-005 | Given any cache key input/version change, stale result is not reused; prior immutable resolution remains auditable. |
| C09-AC-006 | Given developer/production invocation, unregistered tool, path escape, or prompt injection, technical controls deny/audit and no unauthorized content/gateway call occurs. |
| C09-AC-007 | Given candidate citation changed or cannot be re-read, C13 integration drops it/returns hole open; C09 cannot self-promote confidence. |
| C09-AC-008 | Load/quota/gateway-outage tests keep deterministic work within SLO, budgets bounded, and every hole reconciled to cache/resolved/unresolved/deferred. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C09-CT-001 | Admission | Open, closed, stale, and arbitrary tasks | Submit | Only current open hole invokes model | Decision/gateway counts |
| C09-CT-002 | Tool contract | Valid/invalid search/span/symbol/call/schema calls | Invoke | Typed bounded results or exact deny | Tool fixtures/audit |
| C09-CT-003 | Emit contract | Cited in-scope versus uncited/out-of-scope/stale evidence | `emit_edge` | Accept well-formed only; exact rejection reasons | Candidate/rejection set |
| C09-CT-004 | Budget | Exhaust each turn/tool/token/byte/time/cost dimension | Execute | `UNRESOLVED`; no post-limit call/edge | Budget ledger/transcript metadata |
| C09-CT-005 | Cache/idempotency | Same key sequential/concurrent/retry | Resolve | One immutable result/gateway invocation logically | Cache/attempt history |
| C09-CT-006 | Cache invalidation | Change each code/schema/model/prompt/tool/hole key part | Lookup | Required miss/new version; prior preserved | Key/result matrix |
| C09-CT-007 | Conflict | Racing same key returns differing bytes | Commit | `CACHE_CONTENT_CONFLICT`; neither overwrites active until governed resolution | Conflict artifacts |
| C09-CT-008 | Environment/security | Developer/prod identities and network paths | Submit/call gateway | Denied before exposure; audit/alert | IAM/SCP/network evidence |
| C09-CT-009 | Prompt injection/privacy | Repository asks for secrets/tool expansion/exfiltration; secret fixtures | Execute | Policy unchanged, deny/redact, unresolved/rejected | Security transcript scan |
| C09-CT-010 | Gateway failure | Throttle/timeout/model unavailable | Execute | Bounded retry/defer then unresolved; no cost storm | Attempt/metrics |
| C09-CT-011 | Verification feedback | Candidate passes/fails each G1-G5/correction | Process feedback | Metrics/labels keyed by exact model/prompt/tool/archetype | Feedback aggregates |
| C09-CT-012 | Load/quota/recovery | Residual spike, domains, cache mix, gateway outage/Region restart | Execute | Budgets/fairness/NFRs/exact reconciliation/cache recovery | Load/recovery report |

## 16. Integration Obligations

- **INT-056 C08↔C09:** open hole/fact/tool scope round-trips; deterministic/
  closed/stale work is rejected and no whole repository enters context.
- **INT-057 C06↔C09:** residual queue/admission/budget/retry/defer/result prevents
  starvation and preserves one run/stage outcome.
- **INT-058 C09↔Enterprise gateway:** CI-only identity, approved model/Region,
  retention/no-training, rate/quota, audit ID, and outage cases pass.
- **INT-059 C09↔C12:** task/result/cache immutable writes, first-writer,
  conflict, auth, replication, and restore preserve reproducibility.
- **INT-060 C09↔C13:** citations/evidence/determinants undergo G1-G5; dropped edge
  reopens same hole, failures/downgrades and confidence caps are exact.
- **INT-061 C09↔C15/C17:** provenance/evidence/unresolved/budget/verification/
  correction are visible without unsafe source exposure and feed corpus metrics.
- **INT-062 C09↔C18:** IAM/SCP/privacy/prompt-injection/cost/load/outage/audit/DR
  gates and runbooks pass.

## 17. Definition of Done

- Hole admission/task builder, typed tools, budget ledger, enterprise gateway,
  `emit_edge`, immutable result/cache, feedback telemetry, and policy rollout
  are implemented.
- C09 P0 requirements and C09-CT-001 through C09-CT-012 pass.
- INT-056 through INT-062 pass in production-shaped CI/nonproduction accounts.
- Security evidence proves developer/production hard-deny, minimal context,
  capability/path limits, prompt-injection resistance, no secret/payload leak,
  approved model/Region/no-training, and audit.
- Cache race/invalidation/conflict and gateway outage tests prove reproducible
  behavior and no retry-for-preferred-answer.
- Labelled offline/canary report publishes verification/correction/unresolved/
  cost metrics by provenance/archetype before enforcement use.
- Quota/gateway/cache/security/rollback/DR runbooks and alarms are exercised.

## 18. Implementation Notes

```text
contracts/schemas/agent-resolution/
services/agent-task-builder/
services/agent-tools/
workers/agent-resolver/
workers/agent-resolver/prompts/
infra/lib/constructs/agent-gateway.ts
infra/lib/constructs/agent-cache.ts
tests/fixtures/agent-holes/
tests/contract/agent-tools/
tests/integration/agent-resolver/
tests/security/agent-resolver/
tests/load/agent-resolver/
```

Use Python 3.12 for task/agent/tool orchestration and typed JSON schemas for all
tool calls. Bedrock is accessed only through the enterprise gateway. Use a
model API that supports tool calling and explicit version pinning; model choice
is policy/config, not hard-coded product behavior. Store prompts as reviewed
versioned artifacts and results in C12.

Build order: contracts/hole admission; read-only tools; budgets/security; fixed
prompt/gateway; emit/result/cache; C13 feedback; canary/load/DR. Default feature
flag is observation-only; rollback disables new tasks while preserving cached
results/audit and open holes.

## 19. Traceability

| Source decision | C09 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Agent only on named holes/tools | C09-FR-001 through C09-FR-006 | C09-CT-001/002/003 | INT-056/060 |
| Bounded/no guess | C09-FR-007/008 | C09-CT-004/010 | INT-057/058 |
| Shared content-addressed reproducibility | C09-FR-010 through C09-FR-013 | C09-CT-005/006/007 | INT-059 |
| CI-only/security/privacy/prompt injection | C09-FR-009/014; C09-SEC-001-006 | C09-CT-008/009 | INT-058/062 |
| Verification/correction not self-confidence | C09-FR-015 through C09-FR-017 | C09-CT-011/012 | INT-060/061; calibration gate |
