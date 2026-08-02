# Lineage Collection Component PRD Package Design

**Status:** Approved scope
**Date:** 2026-08-02
**Audience:** Product, architecture, platform engineering, coding agents, QA, security, and operations
**Parent architecture:** `docs/plans/2026-08-01-aws-lineage-collection-architecture-design.md`

## 1. Decision

Break the approved end-to-end AWS lineage collection platform into capability-
bounded components. Give each component its own implementation-ready product
requirements document (PRD), while keeping shared identities, contracts,
failure semantics, test fixtures, and end-to-end gates in a small set of
cross-component specifications.

The package must let a coding agent implement the application without having to
infer product behavior from AWS service descriptions or reconstruct interfaces
from diagrams.

## 2. Authoritative Scope and Source Precedence

The package covers the complete platform:

1. Intake and inventory.
2. Classification and substrate routing.
3. Static, native, agentic, opaque, and integration-runtime evidence.
4. Verification, reconciliation, and two-axis confidence.
5. CI drift detection, artifact binding, and freshness.
6. Proposal, human review, correction, and approval.
7. Fenced publication to graph and search projections.
8. Query APIs, review UI, search, and run timeline.
9. Security, privacy, observability, operations, reconciliation, and disaster
   recovery.

When source documents disagree, use this precedence:

1. This approved component-package design.
2. `2026-08-01-aws-lineage-collection-architecture-design.md` for platform
   topology, AWS service selection, scale, security, publication, and
   operational behavior.
3. `docs/lineage-approach/PRD_Element_Level_Lineage_v2.md` for Lane A/B/C
   analyzer behavior, holes, verification, corpus, CI semantics, and the
   distinction between structural and derivational confidence.
4. `deliverables/Throughline-OpenLineage-Platform-PRD.md` for product language,
   user journeys, and OpenLineage compatibility.
5. Earlier source material for context only.

The 70-repository estate described by the element-level v2 PRD is the pilot
cohort. The platform remains designed and tested for the approved capacity of
10,000 repositories and at least 10,000 deployed-artifact decisions per day.

AWS EventBridge, SQS, Step Functions, Batch, Kinesis, S3, DynamoDB, Neptune, and
OpenSearch remain the selected initial architecture. References to a generic
Kafka evidence bus in earlier material describe semantics, not a replacement
for the approved AWS transport.

## 3. Goals

The PRD package must:

- Define one primary responsibility and an explicit boundary for every
  component.
- Define every input, output, durable record, event, API, idempotency identity,
  state transition, and error class used between components.
- Convert architectural principles into numbered, testable requirements.
- Define functional, privacy, security, resilience, scale, latency,
  observability, and operability acceptance criteria.
- Give each component a component-test matrix with fixtures, actions, expected
  outputs, and failure assertions.
- Define pairwise integration tests at every interface and end-to-end steel
  threads across the complete application.
- Make requirement-to-test-to-gate traceability machine-checkable.
- State build order, dependency gates, and the evidence required before a
  component is considered implemented.
- Preserve the approved rule that missing, stale, conflicting, excluded, or
  unresolved work is visible and never silently discarded.

## 4. Non-Goals

- Replacing the approved AWS architecture.
- Writing production implementation code in the PRD package.
- Treating a cloud service as a product component merely because it appears in
  the deployment topology.
- Making Lane C, production auto-publication, raw payload capture, or arbitrary
  LLM repository analysis part of the launch-critical minimum.
- Collapsing structural and derivational confidence into one score.
- Treating runtime interactions as lineage assertions without independent
  derivational evidence.

## 5. Decomposition Approaches Considered

| Approach | Strength | Weakness | Decision |
|---|---|---|---|
| One PRD per AWS service | Direct infrastructure ownership | Product behavior spans services; interfaces and user outcomes become fragmented | Rejected |
| One PRD per pipeline stage | Easy to visualize sequentially | Shared state, replay, review, and cross-cutting guarantees become ambiguous | Rejected |
| Capability-bounded components with shared contracts | Stable responsibility boundaries, independently testable behavior, explicit contracts | Requires disciplined shared specifications and traceability | **Selected** |

## 6. Component Model

### 6.1 Foundation and Control Plane

| ID | Component | Primary responsibility | Explicitly does not own |
|---|---|---|---|
| C01 | Canonical Contracts, URNs, and Identity Resolution | Version schemas; resolve stable entity identities across sources, lanes, environments, and versions | Collection, analysis, graph publication |
| C02 | Source Adapters and Repository Inventory | Discover repositories, deployments, applications, schemas, native sources, and test associations; create immutable inventory snapshots | Eligibility decisions and lineage inference |
| C03 | Event Intake, Normalization, and Priority Queues | Authenticate, normalize, validate, deduplicate, route, archive, quarantine, and buffer triggers | Long-running orchestration and analysis |
| C04 | Repository Eligibility and Substrate Routing | Classify repositories/workload paths and assign Lane A, B, or C as governed data | Running analyzers or silently excluding unknowns |
| C05 | Application Context, Dependency, and Determinant Indexes | Build versioned application context and resolve library, infrastructure, contract, test, and analysis determinants | Executing analysis or approving lineage |
| C06 | Workflow Orchestration and Workload Scheduling | Coordinate baseline, incremental, runtime, verification, publication, reconciliation, retry, and redrive flows with priority fairness | Heavy analysis and authoritative evidence storage |

### 6.2 Collection and Analysis Plane

| ID | Component | Primary responsibility | Explicitly does not own |
|---|---|---|---|
| C07 | Lane B Native Lineage Collectors | Capture exact engine-native/dbt column lineage per run and bind it to an artifact digest | Guessing unresolved native mappings |
| C08 | Lane A Deterministic Analyzers | Emit byte-stable provable edges, determinants, and explicit holes for supported code archetypes | Resolving holes with probabilistic inference |
| C09 | Lane A Agentic Residual Resolver | Resolve named holes through bounded tools, cited evidence, budgets, and a content-addressed result cache | Reanalyzing whole repositories or uncited edge emission |
| C10 | Lane C Opaque-Substrate Collector | Produce advisory statistical/fingerprint evidence for systems without readable source | Verified derivation or launch-critical enforcement |
| C11 | Integration Runtime Session Controller and Sidecar | Collect metadata-only integration-test execution evidence under signed, expiring sessions with production hard-deny | Raw/reversible values or proof of internal transformation |
| C12 | Immutable Evidence Store and Analysis Cache | Preserve evidence, packages, proposals, manifests, labels, checksums, and reusable content-addressed results | Mutable graph/query projection state |

### 6.3 Trust, Governance, and Publication Plane

| ID | Component | Primary responsibility | Explicitly does not own |
|---|---|---|---|
| C13 | Reconciliation, Verification, and Two-Axis Confidence | Merge identities/evidence, apply gates G1-G5, surface conflicts/holes/coverage, and assign calibrated independent confidence bands | Human approval or projection mutation |
| C14 | CI Drift, Artifact Binding, and Freshness | Detect LineageSpec drift, bind signed lineage packages to artifacts, enforce deploy freshness, and run full-vs-incremental divergence checks | Claiming CI proves semantic correctness |
| C15 | Proposal, Human Review, and Calibration Corpus | Version before/after proposals, capture corrections/decisions, and emit per-edge labels for calibration | Publishing unapproved state |
| C16 | Fenced Publication and Graph/Search Projections | Atomically advance approved graph versions and build/rebuild Neptune/OpenSearch projections from accepted manifests | Acting as the authoritative evidence store |

### 6.4 Experience and Operations Plane

| ID | Component | Primary responsibility | Explicitly does not own |
|---|---|---|---|
| C17 | Query APIs, Discovery, Review UI, and Run Timeline | Expose bounded graph/search queries, evidence, review workflows, confidence, coverage, and stage status to users | Bypassing review/publish policies |
| C18 | Security, Observability, Reconciliation Operations, and DR | Provide account/IAM boundaries, privacy controls, audit, telemetry, alarms, runbooks, replay, rebuild, backup, and regional recovery | Redefining component business behavior |

Cross-cutting infrastructure in C18 does not erase local responsibility. Every
component PRD must still define its own least-privilege permissions, metrics,
alarms, and recovery behavior.

## 7. Shared Artifact Set

The package will live under `docs/component-prds/`:

```text
docs/component-prds/
  README.md
  00-system-context-and-architecture.md
  01-canonical-contracts-and-identity.md
  02-source-adapters-and-inventory.md
  03-event-intake-and-queues.md
  04-eligibility-and-substrate-routing.md
  05-context-dependency-and-determinants.md
  06-orchestration-and-scheduling.md
  07-lane-b-native-collectors.md
  08-lane-a-deterministic-analyzers.md
  09-lane-a-agentic-resolver.md
  10-lane-c-opaque-collector.md
  11-runtime-session-and-sidecar.md
  12-evidence-store-and-cache.md
  13-reconciliation-verification-confidence.md
  14-ci-artifact-binding-and-freshness.md
  15-proposal-review-and-corpus.md
  16-publication-and-projections.md
  17-query-api-review-ui-and-timeline.md
  18-security-observability-operations-dr.md
  shared/
    contract-catalog.md
    state-and-error-model.md
    dependency-and-integration-matrix.md
    test-strategy-and-fixtures.md
    end-to-end-acceptance-tests.md
    requirements-traceability-matrix.md
    implementation-sequence.md
    coding-agent-handoff.md
```

## 8. Required PRD Schema

Every component PRD must contain the following sections. A section may say
"not applicable" only with a reason.

1. Document control: component ID, status, launch phase, criticality, owners,
   dependencies, and source decisions.
2. Purpose and measurable outcome.
3. Scope and explicit non-goals.
4. Actors, jobs, and primary use cases.
5. Boundary: owned behavior, upstreams, downstreams, and forbidden behavior.
6. Functional requirements with stable IDs such as `C08-FR-001`.
7. Data model and durable state.
8. Input/output contract references, API/event semantics, compatibility, and
   idempotency.
9. Processing rules or state machine.
10. Failure semantics: transient, deterministic, incomplete, conflict,
    quarantine, retry, redrive, replay, and operator action.
11. Security, privacy, and compliance requirements.
12. Scale, performance, availability, and cost guardrails.
13. Observability: logs, metrics, traces, audit events, dashboards, and alarms.
14. Component acceptance criteria in Given/When/Then or equally testable form.
15. Component test matrix, including happy path, boundary, negative,
    idempotency, failure/recovery, privacy/security, contract, and load tests.
16. Integration obligations and integration-test references.
17. Definition of done and required completion evidence.
18. Implementation notes: approved technology, repository path, dependency
    order, feature flags, rollout/rollback, and unresolved decisions.
19. Traceability back to platform requirements and forward to tests/gates.

Requirements must use **must**, **must not**, or an explicit optional priority.
Words such as "support," "handle," "robust," and "appropriate" are invalid
unless followed by observable behavior.

## 9. Shared Contract Design

The contract catalog owns schemas and compatibility rules for at least:

- `CanonicalUrn` and identity aliases.
- `EventEnvelope` and typed trigger payloads.
- `RepositoryInventorySnapshot`.
- `RepositoryEligibilityDecision`.
- `ApplicationContextSnapshot`.
- `DependencyRecord` and `DeterminantSet`.
- `CollectionRun` and stage result.
- `NativeLineageRun`.
- `DeterministicAnalysisPackage`, `Hole`, and `AgentResolution`.
- `RuntimeEvidenceSession`, evidence envelope, heartbeat, and closing manifest.
- `EvidenceReference` and provenance.
- `LineageEdgeCandidate`, verification result, conflict, and coverage report.
- `LineageProposal`, review correction, and decision.
- `AcceptedLineageManifest`, publication reservation, fencing token, and graph
  pointer.
- `ReviewLabel`, calibration report, and policy version.

Every schema requires:

- A schema identifier and semantic version.
- `additionalProperties: false` at privacy-sensitive boundaries.
- Immutable identity fields.
- Producer and consumer ownership.
- Backward/forward compatibility policy.
- Valid and invalid examples.
- A checksum rule for large artifacts passed by S3 reference.

## 10. End-to-End Data Flow

### 10.1 Baseline

1. C02 creates a complete inventory snapshot for a business application.
2. C03 normalizes the baseline request and creates a durable idempotent trigger.
3. C04 classifies every repository/path and assigns its collection lane.
4. C05 builds application context, dependencies, test mappings, and initial
   determinants.
5. C06 schedules the appropriate C07-C11 collectors/analyzers.
6. C12 preserves all immutable evidence and analysis packages.
7. C13 resolves identities, merges candidates, verifies edges, records holes
   and conflicts, assigns confidence, and produces coverage.
8. C15 creates an immutable before/after proposal for human decision.
9. C16 publishes only the approved manifest using an application-scoped lease
   and fencing token.
10. C17 exposes the active graph, evidence, confidence, coverage, and full run
    timeline; C18 observes and audits every stage.

### 10.2 Incremental

1. C03 receives an SCM or deployment event with immutable commit/artifact
   identity.
2. C04 and C05 resolve repository class, consumers, bindings, and changed
   determinants.
3. C06 schedules only affected analysis while preserving a recorded decision
   for every deployment, including hotfixes.
4. C13 compares the result with the accepted baseline and C15 presents added,
   removed, modified, confidence, coverage, and unresolved differences.
5. C14 binds the approved lineage package to the artifact and detects stale or
   missing packages; C16 publishes the approved graph version.

### 10.3 Integration Runtime Evidence

1. C06 requests evidence for named tests and C11 creates a signed, expiring,
   integration-only session.
2. Tests start only after expected sidecars report `READY`.
3. Sidecars emit allowlisted metadata, sequence numbers, and session-scoped
   irreversible fingerprints through the validated runtime transport.
4. C12 persists validated evidence; C11 drains, disables, and closes in a
   finally path.
5. Missing sequences, manifests, sidecars, or checksums make the session
   `INCOMPLETE` or `TRUNCATED`; C13 must not promote confidence from it.

## 11. Error and Recovery Model

All components share five top-level outcomes:

| Class | Example | Required behavior |
|---|---|---|
| Transient | Throttle, timeout, capacity shortage | Bounded retry with jitter; preserve idempotency |
| Deterministic invalid | Invalid schema, forbidden evidence, unsupported syntax | Do not waste retry; quarantine with reason and owner action |
| Incomplete | Missing inventory source, sidecar manifest, dependency, or evidence | Surface coverage gap; prevent unwarranted completion/confidence |
| Conflict | Identity ambiguity, concurrent graph version, evidence disagreement | Preserve both claims; route to deterministic resolution or review |
| Poison/repeated | Repeated consumer failure | DLQ with governed redrive and replay audit |

Every consumed message may be delivered more than once. Success means the same
durable result is observable exactly once by business identity, not that the
transport delivers exactly once.

No failure path may:

- Drop a repository, deployment, hole, edge, evidence envelope, proposal, or
  approval silently.
- Infer an empty idempotency identity from a missing commit or digest.
- Promote incomplete runtime evidence.
- Mutate an accepted manifest or reviewer label.
- Allow an expired publication worker to advance the active graph pointer.

## 12. Testing Design

### 12.1 Component Tests

Each component must have deterministic local tests for:

- Contract validation and invalid examples.
- Happy path and every state transition.
- Boundary values, unsupported inputs, and explicit non-goals.
- Duplicate delivery and idempotent replay.
- Transient retry and deterministic quarantine.
- Incomplete/conflict behavior.
- Least-privilege and privacy invariants.
- Metrics/audit emission.
- Representative capacity and payload limits where locally testable.

A component is not implemented merely because unit tests pass. Its PRD
definition of done requires contract, integration, and operational evidence.

### 12.2 Pairwise Integration Tests

The dependency matrix assigns at least one positive, negative, duplicate,
compatibility, timeout/recovery, and observability test to every producer-
consumer boundary. Tests use shared canonical fixtures rather than independent
hand-built objects.

### 12.3 End-to-End Steel Threads

The package must specify, at minimum:

1. Approved baseline for a mixed business application.
2. Lane B Spark/dbt exact native lineage.
3. Lane A deterministic edge plus a named hole resolved by a cited agent edge.
4. Verification drop for G1/G2/G4 and downgrade for G3/G5.
5. Metadata-only runtime completion and an incomplete-session no-promotion case.
6. Application incremental determinant change.
7. Shared-library and infrastructure changes routed to affected consumers.
8. Documentation no-impact and contract-source reclassification.
9. Mixed-monorepo path routing and UNKNOWN quarantine/replay.
10. Hotfix artifact with missing lineage alert and unskippable binding.
11. Human correction, re-versioning, approval, fenced publication, and query.
12. Duplicate event storm, DLQ/redrive, projection rebuild, and regional
    recovery.
13. Production attempts to enable or submit runtime evidence are denied and
    audited.
14. 10,000-repository baseline, 10,000-event burst, priority fairness, and
    projection/query SLOs.

### 12.4 Completion Rule

The application is successfully implemented only when:

- All P0 component requirements have passing mapped tests.
- Every shared contract passes compatibility and privacy tests.
- Every dependency-matrix boundary has passing integration tests.
- All launch-phase steel threads pass in a production-like nonproduction
  environment.
- Security/privacy, performance, resilience, recovery, and rebuild gates have
  retained evidence.
- No critical repository is UNKNOWN and no time-bounded waiver has expired.
- The signed launch checklist links to actual run IDs, reports, manifests, and
  dashboards rather than assertions of completion.

## 13. Implementation Sequencing

1. Contracts and identity (C01).
2. Evidence/control-state foundation (C12 plus C18 foundations).
3. Inventory, intake, eligibility, context, and orchestration (C02-C06).
4. Lane B and deterministic Lane A (C07-C08).
5. Reconciliation, verification, proposal, and initial review (C13 and C15).
6. Artifact/freshness workflow and publication/query path (C14, C16, C17).
7. Runtime session/sidecar and agentic residuals (C11 and C09).
8. Lane C advisory collection (C10).
9. Enterprise security, scale, chaos, projection rebuild, and DR completion
   (C18 and all component gates).

The earliest meaningful vertical slice is C01-C08, C12-C13, and C15-C17 for one
Spark/dbt plus Spring/FastAPI application. It must still use production-shaped
contracts and immutable/fenced state; it is not a throwaway prototype.

## 14. Traceability and Document Validation

The traceability matrix records:

```text
source requirement
  -> component requirement
  -> contract/schema
  -> component test
  -> integration test
  -> steel-thread/launch gate
  -> retained completion evidence
```

Automated documentation checks must fail when:

- A component PRD or mandatory section is missing.
- A requirement ID is duplicated.
- A P0 requirement has no test mapping.
- A contract has no producer or consumer.
- An integration boundary has no test.
- A steel thread has no owner, environment, expected evidence, or pass rule.
- A requirement uses an unresolved placeholder such as TBD.
- A PRD contradicts the source-precedence decisions in this design.

## 15. Approval Consequence

Approval of this design authorizes creation of the complete component PRD
package and its documentation-validation tests. It does not authorize deploying
AWS resources or implementing the production application.
