# AWS Lineage Collection Component PRDs

**Package status:** Implementation specification in progress  
**Scope:** Approved end-to-end AWS lineage collection platform  
**Design date:** 2026-08-02

This package converts the approved lineage architecture into product and test
contracts that a coding agent can implement without reconstructing behavior
from service diagrams. The component boundary is a product capability, not an
AWS service. Shared contracts define how independently implemented components
compose into one governed application.

## Authoritative Sources

Use this order when requirements appear to disagree:

1. [Component package design](../plans/2026-08-02-lineage-component-prd-package-design.md).
2. [Approved AWS architecture](../plans/2026-08-01-aws-lineage-collection-architecture-design.md).
3. Element-level lineage v2 for Lane A/B/C analysis semantics.
4. [Throughline platform PRD](../../deliverables/Throughline-OpenLineage-Platform-PRD.md) for user journeys and OpenLineage product language.

The element-level document's 70-repository estate is the pilot cohort. The
platform capacity and launch tests remain sized for 10,000 repositories and at
least 10,000 deployed-artifact decisions per day. AWS EventBridge, SQS, Step
Functions, Batch, Kinesis, S3, DynamoDB, Neptune, and OpenSearch remain the
selected initial architecture.

## How to Use This Package

- A coding agent starts with [system context](00-system-context-and-architecture.md), [contracts](shared/contract-catalog.md), [state and errors](shared/state-and-error-model.md), and the [implementation sequence](shared/implementation-sequence.md).
- An owner implementing one component reads its PRD, then follows every linked
  interface and integration test before writing code.
- QA starts with [test strategy and fixtures](shared/test-strategy-and-fixtures.md), [dependency tests](shared/dependency-and-integration-matrix.md), and [end-to-end acceptance](shared/end-to-end-acceptance-tests.md).
- Product and architecture use [traceability](shared/requirements-traceability-matrix.md) to audit scope and launch evidence.
- Security and operations read every component's local controls plus C18; C18
  does not replace local least-privilege, telemetry, or recovery requirements.

## Component PRDs

| ID | Component | PRD |
|---|---|---|
| C01 | Canonical contracts, URNs, and identity resolution | [C01](01-canonical-contracts-and-identity.md) |
| C02 | Source adapters and repository inventory | [C02](02-source-adapters-and-inventory.md) |
| C03 | Event intake, normalization, and priority queues | [C03](03-event-intake-and-queues.md) |
| C04 | Repository eligibility and substrate routing | [C04](04-eligibility-and-substrate-routing.md) |
| C05 | Application context, dependency, and determinant indexes | [C05](05-context-dependency-and-determinants.md) |
| C06 | Workflow orchestration and workload scheduling | [C06](06-orchestration-and-scheduling.md) |
| C07 | Lane B native lineage collectors | [C07](07-lane-b-native-collectors.md) |
| C08 | Lane A deterministic analyzers | [C08](08-lane-a-deterministic-analyzers.md) |
| C09 | Lane A agentic residual resolver | [C09](09-lane-a-agentic-resolver.md) |
| C10 | Lane C opaque-substrate collector | [C10](10-lane-c-opaque-collector.md) |
| C11 | Integration runtime session controller and sidecar | [C11](11-runtime-session-and-sidecar.md) |
| C12 | Immutable evidence store and analysis cache | [C12](12-evidence-store-and-cache.md) |
| C13 | Reconciliation, verification, and two-axis confidence | [C13](13-reconciliation-verification-confidence.md) |
| C14 | CI drift, artifact binding, and freshness | [C14](14-ci-artifact-binding-and-freshness.md) |
| C15 | Proposal, human review, and calibration corpus | [C15](15-proposal-review-and-corpus.md) |
| C16 | Fenced publication and graph/search projections | [C16](16-publication-and-projections.md) |
| C17 | Query APIs, discovery, review UI, and run timeline | [C17](17-query-api-review-ui-and-timeline.md) |
| C18 | Security, observability, operations, and disaster recovery | [C18](18-security-observability-operations-dr.md) |

## Shared Specifications

- [Contract catalog](shared/contract-catalog.md)
- [State and error model](shared/state-and-error-model.md)
- [Dependency and integration matrix](shared/dependency-and-integration-matrix.md)
- [Test strategy and canonical fixtures](shared/test-strategy-and-fixtures.md)
- [End-to-end acceptance tests](shared/end-to-end-acceptance-tests.md)
- [Requirements traceability](shared/requirements-traceability-matrix.md)
- [Implementation sequence](shared/implementation-sequence.md)
- [Coding-agent handoff](shared/coding-agent-handoff.md)

## Global Conventions

- `must` and `must not` are normative; `may` identifies optional behavior.
- P0 is required for launch. P1 is a planned post-launch capability with an
  explicit safe launch behavior. P2 is an optimization or research item.
- All asynchronous deliveries are duplicateable. Business effects are
  idempotent by immutable, event-type-specific identity.
- Large payloads move by immutable S3 URI plus checksum, never through workflow
  state.
- Structural and derivational confidence are independent. Runtime execution
  cannot prove a transformation, and a single numeric confidence is prohibited.
- Evidence, proposals, accepted manifests, reviewer labels, and audit records
  are immutable. Corrections produce new versions.
- Neptune and OpenSearch are rebuildable projections. Accepted S3 manifests
  and the fenced active pointer define approved state.
- Missing, stale, conflicting, incomplete, excluded, or unresolved work is
  visible and attributable; no component may silently discard it.

## Package Completion Rule

The package is complete only when all 18 PRDs and shared specifications exist;
every P0 requirement maps to a component test, an integration test, a phase
gate, and retained evidence; all producer-consumer boundaries have positive and
failure-path tests; all mandatory steel threads have exact pass rules; and the
documentation validator plus the existing repository tests pass.
