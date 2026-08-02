# Build Specification — Component Breakdowns for the 8-Step Collection Lifecycle

| | |
|---|---|
| **Status** | Draft — for review (normative once approved) |
| **Version** | 1.0 |
| **Date** | 2026-08-02 |
| **Builds on** | [../aws-lineage-collection-plan/](../aws-lineage-collection-plan/README.md) (ADR-020…029, trigger matrix, workflow spec, approval spec, scale spec) · [../architecture-review-v8/](../architecture-review-v8/README.md) (ADR-001…019, HLD) · [../platform-10-de-review/README.md](../platform-10-de-review/README.md) (component list, state machine, CI suite) · [../lineage-collection-assessment.md](../lineage-collection-assessment.md) (contracts) |
| **Audience** | The engineers (or coding agents) building the collection platform; reviewers verifying build-readiness |
| **Scale anchor** | 10,000 registered repos, a = 0.7 active; pilot = one Business App (3–5 repos). 2k design point and 10k ceiling always shown together |

## 1. What this package is

The layers above this one decide and specify: ADRs decide, the workflow/approval/scale specs specify, the roadmap sequences. What none of them contain is **per-component build depth** — module layouts, error taxonomies, idempotency keys, testable requirements, contract tests, live-dependency tests, and end-user acceptance. This package adds exactly that, organized around the eight logical lifecycle steps:

1. **Onboard** (once per Business App): register → resolve members (catalog ∩ active inventory) → classify each repo.
2. **Baseline collection**: app-scoped fan-out → extract (SCA → LLM residue) → app-level reconcile with CloudWatch evidence → publish at Advisory → coverage report.
3. **Incremental collection**: push/PR → class gate → rule-based change classifier → determinant-scoped re-derivation → highlighted delta (+ the PR gate).
4. **Runtime corroboration**: feature-flagged sidecars in integration tests; CloudWatch/OpenLineage evidence from prod — confidence lifts asynchronously.
5. **Deployment promotion**: deploy success promotes the exact artifact digest to environment-authoritative; rollback reactivates the prior version.
6. **Approval**: per-edge accept/correct/reject with before/after → immutable review record → trust promotion.
7. **Nightly reconciliation**: full rescan diffed against incremental state — the standing bug detector and missed-event repair.
8. **Scale + visibility**: priority lanes, 10k-repo wave math, per-flow tracing.

It also ships the platform's first **machine-readable contracts** ([contracts/](contracts/README.md)): 8 JSON Schemas, 3 OpenAPI stubs, and the 17-trigger event catalog — the files the contract-testing sections test against.

## 2. Document map

| Doc | Contents | Read it if you are |
|---|---|---|
| [00-component-inventory.md](00-component-inventory.md) | Component registry (C1–C12, B1–B9, X1–X4, W1–W5), step↔component matrix, PRD homes, trigger-row ownership, terminology normalization | anyone — read first |
| [01-onboard.md](01-onboard.md) | Step 1: B1 registry, B2 inventory adapter, X1 scope reconciler | building onboarding |
| [02-baseline-collection.md](02-baseline-collection.md) | Step 2: C2 manifests, C3 extractor, C4 artifact registry, B4 LLM cache, X4 coverage, W1 | building extraction |
| [03-incremental-collection.md](03-incremental-collection.md) | Step 3 (largest): C1 receiver, X2 classifier, C6 diff, C7 impact, C8 policy, C9 renderer, W2, W3 | building the change loop / PR gate |
| [04-runtime-corroboration.md](04-runtime-corroboration.md) | Step 4: B3 CloudWatch pipeline, B5 sidecar, B6 schema registry, B7 ingest gateway | building evidence paths |
| [05-deployment-promotion.md](05-deployment-promotion.md) | Step 5: C5 baseline resolver, C10 deploy adapter, W4 | building promotion |
| [06-approval.md](06-approval.md) | Step 6: B8 UI+API, B9 review records, X3 trust promotion | building the approval experience |
| [07-nightly-reconciliation.md](07-nightly-reconciliation.md) | Step 7: C11 scheduler, W5, drift findings | building the safety net |
| [08-scale-and-visibility.md](08-scale-and-visibility.md) | Step 8: C12 — lanes, DLQ/replay, tracing, flow status, dashboards | operating the fleet |
| [09-end-user-testing.md](09-end-user-testing.md) | Personas, interface inventory, journeys E2E-01…07 | acceptance testing |
| [10-verification-and-traceability.md](10-verification-and-traceability.md) | Done-criteria, traceability counts, exact-number list, structural invariants, self-verification checklist | reviewing this package |
| [contracts/](contracts/README.md) | JSON Schemas, OpenAPI, event catalog — with `x-source` provenance | implementing any interface |

Every step doc follows the same 13-section template (overview/boundaries · normative inputs · process flow · components · component PRDs · HLD · LLD · use cases with success criteria · contract tests · live-dependency tests · end-user hooks · acceptance criteria · traceability), so any doc can be navigated blind.

## 3. Reading orders

- **Coding agent building a component:** [00](00-component-inventory.md) → the component's PRD-home doc (§5/§7 for its PRD+LLD, §9/§10 for its tests) → the contracts files its interfaces cite → [10](10-verification-and-traceability.md) §1.
- **Tech lead sequencing the build:** [00](00-component-inventory.md) → [01](01-onboard.md)–[08](08-scale-and-visibility.md) overviews (§1 of each) → the AWS plan's [delivery roadmap](../aws-lineage-collection-plan/06-delivery-roadmap.md).
- **Reviewer:** [10](10-verification-and-traceability.md) → spot-check step docs against it → [09](09-end-user-testing.md).
- **Steward/product:** [09](09-end-user-testing.md) → [06](06-approval.md) → [01](01-onboard.md).

## 4. Conventions (inherited, binding)

- **Three-tier anti-duplication rule.** Tier 1: anything normative elsewhere (scoring weights, waiver semantics, AWS mappings) appears only in each doc's §2 "Normative inputs" table with a one-line gloss — never restated. Tier 2: contracts new in this package are defined once — machine-readable file + prose PRD in the home doc. Tier 3: recap tables are marked informative with their source. [10 §4](10-verification-and-traceability.md) polices this.
- Confidence is always integer score + band (Verified/Probable/Inferred) — never decimals. Trust (human ladder) and confidence (evidence) are orthogonal; "authoritative" is an environment property, not a trust rung.
- Every derived capacity number shows its formula; 2k design point and 10k ceiling travel together.
- Signal vocabulary is the closed 10-value set (`sca` · `llm` · `spark-ol` · `airflow-ol` · `warehouse` · `cloudwatch-agg` · `otel-agg` · `sidecar-test` · `registry` · `declared`); drift mapping from older layers in [00 §5](00-component-inventory.md).
- No manual invoke point exists anywhere (ADR-023); diagrams are Mermaid.

## 5. Decision summary consumed by this package

| ADR | One line | Where it lands here |
|---|---|---|
| 020 | App / repo / digest are three scoping units | 01, 02, 03, 05 |
| 021 | Serverless collection plane | 02 (Fargate), all HLDs |
| 022 | EventBridge+SQS now, Kafka by trigger | 04 (bus bypass), 08 (replay/archive) |
| 023 | One GitHub App, zero-touch, no manual invoke | 01, 03, 07, 08 |
| 024 | Per-edge approval, immutable records | 06 |
| 025 | Inventory authority + CloudWatch evidence | 01, 02, 04, 07 |
| 026 | Lanes, waves, DLQ/replay, flow visibility | 03, 05, 07, 08 |
| 027 | One canonical schema, signal-constrained | 04, contracts |
| 028 | Sidecar in tests, off in prod | 04 |
| 029 | Repo classification, per-class treatment | 01, 02, 03, 07 |

## 6. Honest constraints carried forward

- The graph core (Aurora, scoring, endpoints 1–20, CSR) is consumed, not specified — its authority remains the v8 HLD.
- Confidence weights and the sidecar posture are priors to calibrate on the pilot, not truths; the calibration corpus this package's approval step produces is the input.
- Live-dependency tests assume a sandbox GitHub org, a test AWS account, and test-automation-service sandbox access — provisioning them is a Phase-0 dependency.
- The `throughline.yaml` JSON Schema and the CDK IaC are named build tasks, not shipped artifacts of this package.
- The de-review's month-6 gates and funding gates remain the program master; this package decomposes them for builders, it does not renegotiate them.
