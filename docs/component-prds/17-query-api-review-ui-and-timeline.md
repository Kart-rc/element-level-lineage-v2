# C17 Query APIs, Review UI, and Run Timeline PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C17 |
| Status | Approved for implementation |
| Launch phase | Required for pilot review, publication validation, and production query |
| Criticality | P0; the governed user and machine access boundary |
| Primary owner | Lineage experience and API team |
| Required approvers | Product, architecture, governance, application owners, security, accessibility, operations |
| Upstream dependencies | C01, C06, C12-C16, enterprise identity/ownership |
| Downstream dependencies | Users, incident response, automation clients, C18 operations |
| Authoritative sources | AWS architecture §§6.12-6.13, 12, 14, 16-18; component package design |

## 2. Purpose and Outcomes

C17 provides the only supported user and application access to approved lineage,
evidence, proposal review, coverage, and collection status. It resolves one
active graph version per request, performs bounded traversal in Neptune, uses
OpenSearch for discovery with an explicit projection watermark, applies
evidence-level authorization, and renders review and run timeline experiences
without hiding stale, incomplete, conflicting, or unresolved state.

Measurable outcomes:

- A permitted user can find an asset, inspect upstream/downstream lineage,
  evidence, two independent confidence axes, coverage, and the exact active
  version without observing a mixed-version response.
- One-hop graph requests return within two seconds p95 at target graph size,
  and every traversal has deterministic depth/result/time/cost bounds.
- A reviewer can understand a before/after proposal, correct or decide it
  through C15 optimistic concurrency, and never overwrite a newer version.
- Every collection run exposes intake through publication and projection as a
  correlated run timeline including retry, redrive, incomplete, and stale states.
- Primary user journeys meet WCAG 2.2 AA and are exercised by automated and
  manual assistive-technology tests.

## 3. Scope and Non-Goals

### In scope

- Versioned OpenAPI 3.1 read/review/timeline/export interfaces and generated
  client compatibility.
- Active-version graph traversal, asset/field discovery, autocomplete, filters,
  evidence/coverage/conflict/hole views, proposal before/after review, and
  collection/publication timeline.
- Web application shell, routes, accessibility, responsive layout, visual
  empty/loading/error/stale/partial states, and deep links.
- Enterprise authentication, domain RBAC, sensitive-metadata ABAC, purpose-
  bound evidence access, audit and export controls.

### Non-goals

- Accepting arbitrary Gremlin, openCypher, Lucene, or OpenSearch DSL from users.
- Mutating graph/search projections, evidence, confidence, proposals, or
  workflow history directly.
- Combining structural confidence and derivational confidence into one score.
- Treating an OpenSearch result as current when its projection watermark lags
  the active graph version.
- Hiding missing, stale, excluded, conflicting, unknown, unresolved, redacted,
  or incomplete data behind a generic success state.
- Replacing C15 decision policy, C16 publication authority, or C18 operations.

## 4. Actors and Use Cases

| Actor | Primary use case |
|---|---|
| Application owner/reviewer | Review before/after lineage, evidence, holes and approve/correct/reject |
| Data engineer/steward | Find fields, traverse dependencies, inspect provenance and conflicts |
| Incident responder | Perform bounded blast-radius traversal on approved state |
| Developer | Inspect why a CI/deployment lineage decision occurred |
| Auditor/governance user | Export an authorized, versioned evidence/decision report |
| Platform operator | Diagnose a run timeline, redrive link, projection lag or partial state |
| Automation client | Query version-pinned lineage through stable OpenAPI contracts |

## 5. Component Boundary

### Owned behavior

- API composition, query validation/bounds, active-version pinning, pagination,
  search/graph consistency metadata, response redaction, and export audit.
- UI navigation, discovery, graph/detail/review/timeline rendering, accessible
  interaction, optimistic edit presentation and user-visible failure states.

### Inputs

- C16 active pointer and projection watermark; Neptune/OpenSearch projections.
- C12 evidence references; C13 gates/confidence/coverage/conflicts/holes.
- C15 proposal/version/diff/decision APIs; C06/C03/C14/C16 stage histories.
- C01 URNs/schema versions; C18 identity, ownership, policy, audit and telemetry.

### Outputs

- Authorized version-pinned query/search/evidence responses, review commands to
  C15, timeline views, audited exports and user-experience telemetry.

### Forbidden behavior

- Querying Neptune or OpenSearch without resolving and pinning the permitted
  application/environment active graph version.
- Mixing active graph version, proposal version, evidence version, or search
  watermark without labeling and enforcing the allowed consistency policy.
- Returning data outside caller domain/sensitivity scope through counts,
  autocomplete, graph topology, errors, exports, logs, traces or caches.
- Executing unbounded traversal/search or client-selected backend queries.
- Retrying a non-idempotent review write after an ambiguous response without
  reading its operation/result identity.
- Making a stale or partial page appear current or complete.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C17-FR-001 | C17 must publish a versioned OpenAPI 3.1 contract for applications, assets, fields, lineage, search, evidence, proposals/review, coverage, conflicts, holes, runs, stages, projection status and exports, with valid/invalid examples and generated-client tests. | P0 |
| C17-FR-002 | Every graph/search/evidence request must resolve one application/environment active graph version and return it with accepted-manifest checksum, projection watermark, generated-at time and consistency status. | P0 |
| C17-FR-003 | Graph APIs must implement bounded traversal with allowlisted directions/relationships, default one hop, maximum two hops, maximum 10,000 returned vertices/edges, server timeout, response-size cap and continuation rather than arbitrary graph language. | P0 |
| C17-FR-004 | A continuation cursor must be opaque, signed, expiring and bound to caller authorization, query/filter/order, application/environment, active graph version and projection version; a changed version returns a restart conflict rather than mixed results. | P0 |
| C17-FR-005 | Search must support asset/field text, exact canonical URN, owner/domain/application/environment/type filters, autocomplete and stable relevance/order, while disclosing OpenSearch index version and projection lag. | P0 |
| C17-FR-006 | When OpenSearch lags the active graph version, C17 must show a stale banner/status, return graph-version-qualified results, disable any unsafe completeness claim, and either use an approved graph fallback for exact lookup or return retry guidance. | P0 |
| C17-FR-007 | Lineage responses must expose canonical endpoints, direction/path, effective versions/artifacts, transformation/path semantics, evidence provenance, G1-G5 results, structural confidence, derivational confidence, calibration/caps, freshness and accepted proposal/version. | P0 |
| C17-FR-008 | Evidence detail must authorize each reference at request time, return metadata/redacted preview or short-lived download only within purpose/sensitivity policy, and distinguish unavailable, redacted, expired and unauthorized without leaking existence. | P0 |
| C17-FR-009 | Coverage views must show included/excluded/mixed/unknown inventory, analyzed/native/opaque/runtime counts, holes, dropped edges, conflicts, incomplete stages, stale inputs and coverage denominator/version; no empty collection may display as 100 percent. | P0 |
| C17-FR-010 | Review UI must render immutable before/after nodes/edges and added/removed/modified/no-impact changes with side-by-side evidence, two confidence axes, coverage, freshness, holes, conflicts, blockers, materiality and reviewer assignment/SLO. | P0 |
| C17-FR-011 | Correction, comment, assignment, approve and reject actions must call C15 with exact proposal/version/checksum/base/expected state and idempotency identity; a concurrent edit returns the new version and requires explicit reload/rebase. | P0 |
| C17-FR-012 | Bulk acceptance must state that material edges remain unreviewed for calibration, require explicit confirmation, and never imply correctness labels were created. | P0 |
| C17-FR-013 | The run timeline must correlate intake, inventory, classification, context, scheduling, lane collection, evidence, verification, CI/freshness, proposal/review, publication and projection stages by tenant/domain/application/run/correlation and show attempts, durations, retry/redrive, warnings, errors and artifact refs. | P0 |
| C17-FR-014 | Timeline stage state must distinguish queued, running, succeeded, incomplete, failed, quarantined, cancelled, superseded, retrying, awaiting review, publishing, active and projection lag, with reason/error class and permitted next action. | P0 |
| C17-FR-015 | Deep links must encode stable resource IDs and version/context but never credentials or sensitive raw data; historical links must render read-only historical state clearly separated from active state. | P0 |
| C17-FR-016 | Exports must be asynchronous for large results, bound to exact query/version/authorization/purpose, encrypted, checksummed, expiring, redacted, audited and downloadable by the requesting identity or approved delegate only. | P0 |
| C17-FR-017 | The UI must implement keyboard-complete operation, semantic landmarks/headings/tables, visible focus, skip links, accessible names, non-color-only states, graph textual equivalent, zoom/reflow, reduced motion, screen-reader announcements and WCAG 2.2 AA contrast. | P0 |
| C17-FR-018 | Loading, empty, no-access, redacted, partial, stale, conflict, dependency-error, rate-limit and timeout states must state what is known, exact version/time and safe retry/help action without losing user filters/context. | P0 |
| C17-FR-019 | API and UI caches must be private and authorization/version keyed, invalidate or expire on active-pointer/ownership/policy change, and never serve a response to a caller with different effective access. | P0 |
| C17-FR-020 | C17 must provide stable machine-readable problem details with correlation ID, safe error code, retryability and field violations; internal identifiers, queries, policy details and sensitive existence must not leak. | P0 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C17-NFR-001 | Bounded one-hop traversal must complete within two seconds p95 and five seconds p99 at representative target graph size; search/autocomplete must complete within one second p95. | P0 |
| C17-NFR-002 | Read APIs and the web shell must be 99.95 percent available monthly; review writes must preserve C15 consistency and never acknowledge an uncommitted decision. | P0 |
| C17-NFR-003 | APIs must sustain 500 read requests/second and 50 concurrent complex traversals per domain test profile while enforcing per-user/domain quotas and fair degradation. | P0 |
| C17-NFR-004 | Standard pages must meet agreed web performance budgets on enterprise desktop/mobile profiles and primary journeys must have zero critical accessibility violations. | P0 |
| C17-NFR-005 | Active-pointer change must be visible to uncached exact graph reads within five seconds and search status must expose lag until its C16 watermark catches up. | P0 |

## 7. Data and Durable State

C17 owns no canonical lineage state. It stores only versioned API specifications,
UI configuration, private short-lived response caches, export jobs, user
preferences that do not affect approval, and audit/telemetry.

Query context contains caller/tenant/domain/roles/attributes/purpose,
application/environment, active graph version, accepted-manifest checksum,
projection watermark, query hash, limits, cursor, request/correlation ID and
policy version. Cache keys include every field that can alter authorization or
content.

ExportJob contains request/query hash, exact graph/search/proposal versions,
authorization/purpose snapshot, redaction policy, state, output C12 reference/
checksum, expiry, requester/delegate and audit reference. Export content is
immutable and never becomes graph authority.

UI routes use canonical URNs and immutable IDs. Browser storage may retain
non-sensitive presentation preferences only; tokens, evidence, proposal content,
exports and graph results must not be persisted in local storage.

## 8. Interfaces and Contracts

- GET /v1/applications and /v1/applications/{application}/environments returns
  authorized scope, active graph version and coverage summary.
- GET /v1/assets and /v1/search provide discovery/filter/autocomplete with
  signed cursor and search projection watermark.
- GET /v1/lineage/{urn}?direction=upstream|downstream&depth=1..2 returns bounded
  version-pinned nodes/edges/continuation and truncation reason.
- GET /v1/assets/{urn}, /fields/{urn}, /edges/{edgeId}, /evidence/{evidenceId},
  /coverage, /conflicts and /holes return authorized detail.
- GET /v1/proposals and proposal diff/material edges delegate reads to C15;
  POST review actions are conditional C15 commands, not C17 state changes.
- GET /v1/runs/{runId}/timeline and /stages compose immutable stage events and
  C16 projection status in monotonic event/attempt order.
- POST /v1/exports and GET /v1/exports/{id} implement asynchronous governed
  export. DELETE cancels only a not-yet-complete job and preserves audit.
- All responses use schema/content version, request/correlation ID, ETag,
  Cache-Control, RFC-style problem details and rate-limit metadata. Writes use
  Idempotency-Key and If-Match/expected version.

Compatibility is additive within a major version. Removing/renaming a field,
changing confidence meaning, pagination order, bounds, redaction or default
version requires a new major contract and overlapping deprecation window.

## 9. Processing and State Model

Read request:

1. Authenticate, authorize application/domain/purpose and assign correlation.
2. Validate allowlisted query and hard bounds before backend access.
3. Resolve and pin C16 active graph version plus projection watermark.
4. Query version namespace/index, apply row/field/evidence authorization and
   redaction, then verify returned version/count/truncation metadata.
5. Emit safe response/audit/telemetry; cursor binds the exact context.

Review write:

1. Read authorized immutable proposal/version and current ETag.
2. Collect explicit action/rationale/material acknowledgements.
3. Send idempotent expected-state/version/checksum command to C15.
4. On success, render returned new version/state; on conflict, preserve local
   draft separately, display differences and require deliberate reload/reapply.

Run timeline:

1. Load normalized stage events by run/correlation and stable event sequence.
2. Join attempts/artifact refs without rewriting source events.
3. Add current proposal/publication/projection status as labeled observations.
4. Mark delayed/missing/out-of-order stages; never infer success from absence.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| QUERY_INVALID_OR_UNBOUNDED | DETERMINISTIC_INVALID | Reject before backend query; safe field/bound guidance |
| ACTIVE_VERSION_CHANGED | CONFLICT | Abort cursor/request and require restart on new version |
| SEARCH_PROJECTION_LAGGING | INCOMPLETE | Return explicit watermark/lag and safe fallback/retry |
| GRAPH_OR_SEARCH_UNAVAILABLE | TRANSIENT | Bounded retry/circuit break; status and correlation ID |
| EVIDENCE_UNAVAILABLE_OR_REDACTED | INCOMPLETE/security | No existence leak; show permitted state/action |
| REVIEW_VERSION_CONFLICT | CONFLICT | No overwrite; return current C15 version/ETag and reload path |
| REVIEW_DEPENDENCY_FAILED | TRANSIENT | Resolve idempotency result before user retry |
| TIMELINE_GAP_OR_DELAY | INCOMPLETE | Render known events and missing-stage diagnostic |
| EXPORT_TOO_LARGE_OR_POLICY_DENIED | DETERMINISTIC_INVALID/security | Deny/audit; smaller query or policy path |
| RATE_LIMITED | TRANSIENT/capacity | Retry-After and fair quota; no silent partial result |

Dependency retries are read-only or idempotency-resolved. C17 never fabricates
success during backend failure, never falls back to an unauthorized source, and
never converts a partial query into a complete status.

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C17-SEC-001 | Users must authenticate through enterprise federation/IAM Identity Center path; API authorization must enforce tenant/domain/application RBAC and sensitive-metadata ABAC on every resource, relationship, count, search suggestion, evidence item and export. | P0 |
| C17-SEC-002 | API/UI compute must use private networking to Neptune/OpenSearch/internal services, TLS, managed WAF/rate limits, short-lived credentials, encrypted stores and no public projection endpoint. | P0 |
| C17-SEC-003 | Browser protections must include secure HttpOnly SameSite cookies or approved token pattern, CSRF protection, strict CSP, output encoding, dependency integrity, clickjacking defense and no tokens/sensitive metadata in URLs/logs/analytics/storage. | P0 |
| C17-SEC-004 | Review/decision/export/evidence access and privileged searches must emit immutable CloudTrail/application audit with actor, purpose, scope, versions, outcome and correlation, while audit itself excludes payload values. | P0 |
| C17-SEC-005 | Backend queries must be parameterized/allowlisted; arbitrary graph/search language, SSRF destinations, user-selected S3 URIs and cross-tenant identifiers must be rejected before dependency access. | P0 |
| C17-SEC-006 | C17 roles must be read-only for Neptune/OpenSearch/C12 evidence and have only C15 command permissions; no UI or API identity may advance the C16 active pointer. | P0 |

## 12. Scale, Performance, and Availability

- Benchmark with the target node/edge distribution, high-degree hubs, 10,000
  repositories, cold/warm caches, permitted/redacted mixes and concurrent users.
- Query guards apply before and during traversal: depth, fan-out, vertices,
  edges, time, bytes, concurrency and per-domain cost. Truncation is explicit.
- Neptune read replicas serve pinned read traffic; circuit breakers/bulkheads
  isolate search, graph, evidence, review, timeline and export dependencies.
- OpenSearch is discovery only. Exact graph detail uses the active Neptune
  namespace; search lag cannot make an older projection appear current.
- Multi-AZ stateless API/UI deploys retain prior version during rollout.
  Contracts and UI remain backward-compatible across rolling deployment.
- Large exports run asynchronously with bounded concurrency and never consume
  interactive query capacity.

## 13. Observability

| ID | Signal | Dimensions / alarm |
|---|---|---|
| C17-OBS-001 | API rate/latency/error and backend time | route/domain/status/version; SLO burn |
| C17-OBS-002 | Traversal vertices/edges/depth/truncation/cost | route/domain/bound; abuse/capacity alarm |
| C17-OBS-003 | Search active-version versus projection watermark lag | application/environment/index; lag alarm |
| C17-OBS-004 | Authorization deny/redaction/evidence/export events | policy/domain/action; anomaly alarm |
| C17-OBS-005 | Review submit/conflict/retry/result latency | action/proposal/domain; conflict/error alarm |
| C17-OBS-006 | Timeline gap/out-of-order/stage delay | run/stage/error class; completeness alarm |
| C17-OBS-007 | UI route/Web Vitals/client error/accessibility checks | build/route/browser; regression gate |
| C17-OBS-008 | Cache hit/invalidation/version/access-key isolation | cache/route/policy; leakage invariant |

Logs/traces use the common correlation contract and safe resource hashes. The
user can copy request/correlation ID. Dashboards show query SLO, projection lag,
review experience, timeline completeness, export backlog, access denials and
dependency saturation without sensitive payloads.

## 14. Acceptance Criteria

| ID | Given / When / Then |
|---|---|
| C17-AC-001 | Given an authorized active application, when a user searches and opens a field, then discovery, one-hop lineage, evidence, confidence, coverage and versions are consistent and within SLO. |
| C17-AC-002 | Given high-degree/cyclic lineage, when depth/result/time bounds are reached, then traversal terminates, labels truncation and supplies a version-bound cursor without backend language exposure. |
| C17-AC-003 | Given OpenSearch watermark behind active Neptune, when search/detail load, then stale state and exact versions are visible and no completeness/currentness claim is made. |
| C17-AC-004 | Given sensitive/cross-domain evidence, when an unauthorized caller searches, traverses, opens or exports it, then content/existence/count leakage is denied and audited. |
| C17-AC-005 | Given a proposal, when reviewer compares before/after and corrects/approves, then the exact C15 version/checksum is updated; concurrent stale action cannot overwrite. |
| C17-AC-006 | Given failed/retried/redriven collection, when timeline opens, then every attempt, gap, artifact, reason, next action, publication and projection status is ordered and correlated. |
| C17-AC-007 | Given keyboard/screen-reader/reflow/reduced-motion use, when primary journeys execute, then WCAG 2.2 AA behavior and textual graph equivalence pass. |
| C17-AC-008 | Given active pointer/ownership/policy change, when cached or cursor request repeats, then stale/cross-authority data is not served and restart/re-authorization is explicit. |

## 15. Component Test Matrix

| ID | Type | Fixture / fault | Action | Expected result | Evidence |
|---|---|---|---|---|---|
| C17-CT-001 | Contract | OpenAPI valid/invalid/golden and previous client | Generate/validate/call | Schemas/examples/problem details compatible | Contract report |
| C17-CT-002 | Graph happy/bounds | Pilot, cycle, high-degree, 10k-result graph | One/two-hop queries | Correct version/path; hard bounds/truncation/cursor | Query golden/plan |
| C17-CT-003 | Version consistency | Pointer changes between resolve/query/page | Query/page | One pinned version or restart conflict; never mixed | Version trace |
| C17-CT-004 | Search lag | OpenSearch old/missing/partial watermark | Search/open detail | Stale state/fallback/retry; no false completeness | UI/API capture |
| C17-CT-005 | Confidence/coverage | Two axes, caps, unknowns, holes/conflicts | Render/API | Separate axes/provenance/G1-G5/denominator/states | Snapshot/schema |
| C17-CT-006 | Review concurrency | Before/after proposal; two browser versions | Correct/approve concurrently | Exact C15 write; stale loses without overwrite | C15/audit record |
| C17-CT-007 | Authorization/privacy | Cross-domain/sensitive/hidden evidence and counts | Search/query/export/direct ID | Denied/redacted/no existence leak; audited | IAM/ABAC report |
| C17-CT-008 | Timeline/recovery | Retry, redrive, cancel, quarantine, delayed event | Open timeline | Ordered attempts/gaps/reasons/actions/watermark | Timeline golden |
| C17-CT-009 | Accessibility | Keyboard, screen reader, 200% zoom, contrast, reduced motion | Complete primary journeys | WCAG 2.2 AA; textual graph equivalent | axe/manual report |
| C17-CT-010 | Browser steel thread | Mixed application baseline through active graph | Search/review/traverse/timeline | Complete usable journey with exact versions | Playwright trace |
| C17-CT-011 | Cache/security | Ownership/policy/pointer change and poisoned cursor | Repeat requests | Reauthorize/invalidate/reject; no cross-user content | Cache/security log |
| C17-CT-012 | Load/availability | Target graph, 500 rps, hot hubs, dependency throttles | Query/search/export | NFR p95/p99, fair limits, graceful errors | Load/chaos report |

## 16. Integration Obligations

- **INT-118 C16↔C17:** active pointer, immutable namespace, accepted checksum and
  projection watermark changes produce version-consistent graph/search reads.
- **INT-119 C15↔C17:** proposal/diff/materiality/assignment and conditional
  correction/decision preserve immutable version, auth and concurrency.
- **INT-120 C12↔C17:** evidence/export references enforce checksum, Object Lock,
  purpose/ABAC, short-lived access, redaction, expiry and audit.
- **INT-121 C13↔C17:** G1-G5, separate confidence axes, caps/calibration,
  coverage denominator, holes/conflicts/drop reasons render without collapse.
- **INT-122 C03/C06/C14/C16↔C17:** common correlation and stage events form an
  ordered run timeline with attempts, decisions, gaps and next action.
- **INT-123 C01↔C17:** canonical URNs, schema versions and compatibility generate
  valid OpenAPI/client/entity deep links and reject ambiguous identity.
- **INT-124 C18↔C17:** SSO/RBAC/ABAC/WAF/network/audit/SLO/alarms/runbooks/DR and
  no-payload telemetry controls pass for API, UI and export.
- **INT-125 Neptune/OpenSearch↔C17:** query bounds, replica/index versions,
  throttling, high-degree paths and lag behave per active-version policy.
- **INT-126 Browser↔C17:** supported browsers and assistive technologies pass
  search-to-lineage, review, timeline, error, stale and concurrent-edit flows.

## 17. Definition of Done

- OpenAPI 3.1 schemas, generated clients, API service, UI routes/components,
  query guards, auth/redaction, private cache, exports and telemetry are deployed.
- C17 P0 requirements and C17-CT-001 through C17-CT-012 pass in production-
  shaped graph/search/review/evidence/timeline infrastructure.
- INT-118 through INT-126 pass, including version races, dependency faults,
  authorization boundaries and browser/accessibility steel threads.
- Performance report proves two seconds p95 bounded one-hop traversal and search,
  quota, high-degree and degraded dependency behavior at approved scale.
- Threat model/security tests prove no arbitrary backend query, cross-domain
  leak, unsafe browser persistence, unauthorized export or projection mutation.
- Product/accessibility owners approve empty/error/stale/partial/conflict and
  confidence/coverage/review/timeline semantics.
- Dashboards, alerts, SLOs and runbooks are linked to release evidence; rollback
  preserves compatible API/UI and active approved graph access.

## 18. Implementation Notes

Approved repository targets:

    contracts/openapi/lineage-query-v1.yaml
    services/query-api/
    apps/lineage-web/
    packages/api-client/
    packages/ui-components/
    infra/lib/stacks/experience-stack.ts
    tests/contract/query-api/
    tests/integration/experience/
    tests/e2e/experience/
    tests/accessibility/
    tests/load/query/

Use TypeScript 5 for API composition, web application and IaC. Use a supported
React framework with server-side authorization and generated contract types.
Backend adapters expose typed bounded operations, never generic query strings.
Playwright covers browser steel threads; axe plus manual assistive-technology
evidence covers accessibility. Pin runtime/framework versions in the root
toolchain and software bill of materials.

Build order: OpenAPI/problem details; auth/version context; graph bounds; search
watermark; evidence/coverage; C15 review; timeline; exports; UI states and
accessibility; load/chaos/security. Feature flags may hide a UI route but must
not weaken API authorization, review policy, query bounds or version semantics.

## 19. Traceability

| Source decision | C17 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Approved graph traversal/discovery | C17-FR-001-007/015/019-020 | C17-CT-001-005/011-012 | INT-118/123/125; functional/performance gates |
| Evidence/confidence/coverage/review | C17-FR-007-012/016 | C17-CT-005-007/010 | INT-119-121; review/privacy/accuracy gates |
| End-to-end visibility and timeline | C17-FR-013-014/018 | C17-CT-008/010 | INT-122/124; operational gate |
| Security/privacy/accessibility | C17-SEC-001-006, C17-FR-017-020 | C17-CT-007/009-012 | INT-124/126; security/privacy/experience gates |
| Query SLO/availability/scale | C17-NFR-001-005 | C17-CT-002/004/011-012 | INT-118/125; performance/resilience gates |
