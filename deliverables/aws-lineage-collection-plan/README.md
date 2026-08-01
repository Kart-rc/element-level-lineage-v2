# Throughline — AWS Lineage Collection Service Plan

| | |
|---|---|
| **Status** | Draft — for review |
| **Version** | 1.0 |
| **Date** | 2026-08-01 |
| **Builds on** | [architecture-review-v8](../architecture-review-v8/README.md) (ADR-001..019, HLD) · [platform-10-de-review](../platform-10-de-review/README.md) (Phase 0–5 roadmap, pipeline components, deployment authority) · [lineage-collection-assessment.md](../lineage-collection-assessment.md) (contracts) · [execution_model_assessment](../../docs/execution_model_assessment.html) (findings F-01..F-07) · [PRD 1 — Lineage Collection](<../latest_source/Data Lineage Impact Platform-10/PRD 1 - Lineage Collection.dc.html>) |
| **Audience** | Review board, data platform engineering, AWS platform team, product |
| **Scale anchor** | 10,000 repos · ≥ 1 deployment/repo/day with significant spikes · pilot = one Business Application |

## 1. What this package is

The implementation plan for lineage collection as a **repeatable, zero-touch service on AWS** with an **approval experience**. It answers four questions the existing documents left open:

1. **Repo level or Business Application level?** Both, deliberately: baseline collection scopes to the **Business Application** (context-rich: service catalog + test-automation active-repo inventory + CloudWatch interaction evidence); incremental collection executes per **repo** (lightweight: rule-based fast path, determinant-driven re-derivation); trust binds to the **artifact digest** (ADR-020).
2. **How does collection run with no manual invoke point?** A closed trigger matrix of 17 event rows — onboarding, push, PR, deploy, rollback, schedules, test runs, approvals — with a normative invariant: *there is no row for manual invocation* (ADR-023, [03](03-trigger-matrix.md)).
3. **How do the three mechanisms (SCA, LLM, runtime) stay consistent?** One canonical OpenLineage-aligned schema for every signal — uniform structure, **signal-constrained assertions**, registry-validated at the gateway (ADR-027). The pushback is recorded: uniform payloads would launder authority; the constraint table prevents it.
4. **How do users see and approve results?** An approval UI where deltas surface with before/after side-by-side, decisions are per-edge (material mappings require explicit acknowledgement), every finalize writes an immutable hash-chained review record, and approval promotes trust Advisory → Producer-attested (ADR-024, [05](05-approval-ui-spec.md)).

Two further sponsor requirements shape the whole design: **scale** (10,000-repo baseline waves, daily deploy traffic with spikes, priority lanes so the PR gate never starves — ADR-026, [08](08-scale-resilience-observability.md)) and **runtime evidence without production cost** (feature-flagged sidecars collect lineage during integration tests and are off in production; evidence corroborates at artifact-digest level with the cross-environment rule preserved — ADR-028).

## 2. Document map and reading order

| Doc | Contents | Read it if you are |
|---|---|---|
| [01-decision-records.md](01-decision-records.md) | ADR-020..028: scoping, serverless plane, backbone, zero-touch authority, approval, context sources, scale/visibility, canonical schema, sidecar runtime | Review board; anyone wanting the "why" |
| [02-aws-architecture.md](02-aws-architecture.md) | The 12 pipeline components → named AWS services, integration adapters, plane boundary, diagrams | AWS platform team, implementers (start here to build) |
| [03-trigger-matrix.md](03-trigger-matrix.md) | The closed set of 17 triggers: event → what fires → what runs → what it produces, with lane tags | Everyone — this is the zero-touch contract |
| [04-collection-workflow-spec.md](04-collection-workflow-spec.md) | The two processes (baseline, incremental), gate/promotion/nightly workflows, canonical schema + assertion constraints, artifact/delta/determinant contracts | Implementers |
| [05-approval-ui-spec.md](05-approval-ui-spec.md) | Screens, trust ladder, seven-state rendering, endpoints 21–29, roles, review-record immutability | Product, frontend, stewards |
| [06-delivery-roadmap.md](06-delivery-roadmap.md) | AWS deliverables per existing Phase 0–5 gate; what the vertical slice proves; MSK checkpoint | Sponsors, leads |
| [07-verification-and-acceptance.md](07-verification-and-acceptance.md) | Acceptance criteria, SLO subset, scale acceptance, traceability appendix | Review board, QA |
| [08-scale-resilience-observability.md](08-scale-resilience-observability.md) | Capacity math with formulas, fan-out/quotas, priority lanes, failure modes, end-to-end flow visibility | Operators, SREs |

Reading order — **board:** this README → 01 → 03 → 06. **Implementers:** 02 → 04 → 03 → 08, with 01 as rationale. **Product/UX:** 05 → 03. Division of labor inherited from v8: **ADRs decide, the specs specify, the roadmap sequences**; normative text from the HLD and the collection assessment is referenced, never duplicated.

## 3. Decision summary

| ADR | Decision (one line) | Status |
|---|---|---|
| [ADR-020](01-decision-records.md#adr-020-collection-scoping--business-application-for-baseline-repo-for-incremental-artifact-digest-for-binding) | Baseline scopes to the Business App; incremental executes per repo; trust binds to artifact digest | Decided |
| [ADR-021](01-decision-records.md#adr-021-serverless-collection-plane-on-aws--scoped-supersession-of-adr-018) | Serverless collection plane; graph core keeps the ADR-018 posture | Decided |
| [ADR-022](01-decision-records.md#adr-022-event-backbone-at-collection-scale--eventbridge--sqs-now-kafkamsk-by-named-trigger) | EventBridge + SQS now; Kafka/MSK by three named triggers | Decided |
| [ADR-023](01-decision-records.md#adr-023-zero-touch-trigger-authority--one-github-app-no-manual-invoke-point) | One org GitHub App; repo-added ⇒ collection begins; no manual invoke point | Decided |
| [ADR-024](01-decision-records.md#adr-024-approval-experience--trust-promotion-through-immutable-review-records) | Per-edge approval, before/after capture, immutable records, trust promotion | Decided |
| [ADR-025](01-decision-records.md#adr-025-baseline-context-sources--test-automation-service-inventory-and-cloudwatch-log-evidence) | Test-automation service = active-repo authority; CloudWatch logs = interaction evidence | Decided |
| [ADR-026](01-decision-records.md#adr-026-scale-resilience-and-end-to-end-flow-visibility) | Distributed Map fan-out, priority lanes, DLQ/replay, per-flow status + tracing | Decided |
| [ADR-027](01-decision-records.md#adr-027-canonical-lineage-observation-schema--one-schema-for-all-three-mechanisms-uniform-envelope-signal-constrained-assertions) | One canonical schema for SCA/LLM/runtime; signal-constrained assertions | Decided |
| [ADR-028](01-decision-records.md#adr-028-feature-flagged-sidecar-runtime-collection--on-during-integration-tests-off-in-production) | Sidecar runtime collection in integration tests via feature flag; off in production | Decided |

## 4. Honest constraints carried forward (the pushback, kept visible)

- **Consistent schema ≠ identical payloads.** The three mechanisms have different authority; the assertion-constraint table is machine-enforced so low-authority claims can never occupy high-authority fields (ADR-027).
- **The three paths are a ladder, not a triple-run.** Deterministic SCA first; LLM only for cache-missed residue, never gating; runtime corroborates asynchronously. Prefer plan-based/warehouse-native lineage over LLM breadth wherever an engine can state its own lineage.
- **Test evidence is not production truth.** Sidecar corroboration from integration tests lifts confidence at the artifact-digest level with a Probable ceiling; production Verified requires production evidence — the cross-environment rule survives every convenience argument (ADR-028).
- **A Dask OpenLineage collector still does not exist.** Deferred R&D, not a silent promise.
- **ADR-018 is scoped, not overturned.** Serverless is right for the stateless collection plane; the stateful graph core keeps its documented posture, and the MSK migration path stays warm with named triggers (ADR-021/022).
