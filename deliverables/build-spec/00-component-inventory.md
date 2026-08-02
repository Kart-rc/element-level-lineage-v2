# 00 — Component Inventory and Step↔Component Matrix

| | |
|---|---|
| **Status** | Draft — for review (normative once approved) |
| **Role** | The canonical component registry for the build-spec package: every buildable component gets one ID, one PRD home, and one row in the step↔component matrix. Step docs [01](01-onboard.md)–[08](08-scale-and-visibility.md) cite these IDs; nothing else in the package may invent a component name. Also carries the package's terminology normalization. |
| **Builds on** | [../platform-10-de-review/README.md](../platform-10-de-review/README.md) §6.2 (the twelve required pipeline components) · [../aws-lineage-collection-plan/02-aws-architecture.md](../aws-lineage-collection-plan/02-aws-architecture.md) §2–§3 (AWS realizations) |

## 1. Why an inventory

The de-review names twelve required pipeline components; the AWS architecture realizes them and adds a "beyond the twelve" set; the trigger matrix and workflow spec reference several more by role (scope reconciler, change classifier, trust promotion, coverage reporter) without ever naming them as components. A coding agent needs one closed registry with stable IDs. This document is that registry. Rules:

1. **Every component has exactly one ID and exactly one PRD home** (the step doc that carries its PRD, HLD, and LLD). Other step docs reference the home; they never re-specify.
2. **The C-numbering is 1:1 with de-review §6.2** — verified in [10-verification-and-traceability.md](10-verification-and-traceability.md).
3. **Workflows are components too** (W1–W5): a Step Functions definition is buildable, testable code with its own contract surface.

## 2. Component registry

### 2.1 C1–C12 — the de-review's twelve pipeline components

| ID | Component | AWS realization (per [02-aws-architecture](../aws-lineage-collection-plan/02-aws-architecture.md) §2) | PRD home |
|---|---|---|---|
| C1 | SCM App / webhook receiver (dedup, installation-scoped credentials) | API Gateway (HTTP API) → Lambda; DynamoDB dedup on `X-GitHub-Delivery` (TTL 7 d); emits to EventBridge bus | [03-incremental-collection.md](03-incremental-collection.md) |
| C2 | Manifest resolver (repo/monorepo path → service/environment) | Lambda workflow step; Contents API fetch; JSON Schema validation | [02-baseline-collection.md](02-baseline-collection.md) |
| C3 | Incremental extractor runner (isolated, least-privilege source access) | ECS Fargate task (Graviton; Spot for nightly/backfill); tree-sitter + sqlglot image | [02-baseline-collection.md](02-baseline-collection.md) |
| C4 | Immutable artifact registry (repo, SHA, toolchain version, content hash) | S3 content-addressed + Iceberg index (Glue Catalog) + DynamoDB pointer table | [02-baseline-collection.md](02-baseline-collection.md) |
| C5 | Baseline resolver (environment's last successful deployment) | Lambda + DynamoDB `deployment-state` table | [05-deployment-promotion.md](05-deployment-promotion.md) |
| C6 | Versioned diff engine (entities, edges, transforms, schemas, codeRefs) | Lambda (Fargate fallback above size threshold) | [03-incremental-collection.md](03-incremental-collection.md) |
| C7 | Snapshot-pinned impact service (bounded traversal) | Pilot: Lambda + Aurora recursive CTE; Phase 3+: ECS/CSR in the graph core | [03-incremental-collection.md](03-incremental-collection.md) |
| C8 | Policy decision service + waiver store | OPA/WASM in Lambda; policy bundles S3; waivers in Aurora (HLD §6.5 semantics) | [03-incremental-collection.md](03-incremental-collection.md) |
| C9 | SCM check/comment renderer (stable annotation IDs) | Lambda → Checks API + single updated PR comment | [03-incremental-collection.md](03-incremental-collection.md) |
| C10 | Deployment and rollback event adapter | EventBridge ECR events + CD adapter Lambda → promotion Lambda | [05-deployment-promotion.md](05-deployment-promotion.md) |
| C11 | Nightly reconciliation scheduler | EventBridge Scheduler → NightlyReconciliation SFN | [07-nightly-reconciliation.md](07-nightly-reconciliation.md) |
| C12 | Metrics, audit, DLQ/replay, operator tooling | CloudWatch + per-consumer SQS DLQs + Firehose→S3/Iceberg archive + replay SFN + append-only Aurora audit | [08-scale-and-visibility.md](08-scale-and-visibility.md) |

### 2.2 B1–B9 — beyond the twelve (from [02-aws-architecture](../aws-lineage-collection-plan/02-aws-architecture.md) §3)

| ID | Component | AWS realization | PRD home |
|---|---|---|---|
| B1 | Business App registry | DynamoDB + registration API (`POST /v1/apps`), per-member-repo classification (ADR-029) | [01-onboard.md](01-onboard.md) |
| B2 | Test-automation inventory adapter | Lambda (scheduled + onboarding-triggered) → `repo.inventory.delta` | [01-onboard.md](01-onboard.md) |
| B3 | CloudWatch interaction pipeline | Logs subscription filters → Firehose → S3/Iceberg; Glue/Athena aggregation → gateway | [04-runtime-corroboration.md](04-runtime-corroboration.md) |
| B4 | Tier-3 LLM extraction + content-addressed cache | Bedrock (pinned models, temperature 0) + DynamoDB/S3 cache keyed `(codeSliceHash, schemaHash, modelVersion, promptVersion)` | [02-baseline-collection.md](02-baseline-collection.md) |
| B5 | Sidecar evidence path | Sidecar container + conformance library; AppConfig feature flag; `sidecar-test` envelopes | [04-runtime-corroboration.md](04-runtime-corroboration.md) |
| B6 | Schema registry (canonical schema) | Git-versioned JSON Schema → S3, version-pinned validators | [04-runtime-corroboration.md](04-runtime-corroboration.md) |
| B7 | Ingest gateway | API Gateway + Lambda; envelope/payload/assertion validation; Firehose archive + graph-core handoff | [04-runtime-corroboration.md](04-runtime-corroboration.md) |
| B8 | Approval UI + API | S3+CloudFront SPA; API GW + Lambda; Cognito→OIDC | [06-approval.md](06-approval.md) |
| B9 | Review-record store | Append-only Aurora + hash-chained S3 objects under Object Lock | [06-approval.md](06-approval.md) |

(IaC — CDK TypeScript with module boundaries mirroring the plane split — is a delivery vehicle, not a runtime component; it carries no ID and no PRD. Its expectations appear inside each component's LLD as deployment notes.)

### 2.3 X1–X4 — named here for the first time

These exist in the trigger matrix and workflow spec as roles without component names. This package names them; their behavior is unchanged from the sources cited.

| ID | Component | Source of its behavior | PRD home |
|---|---|---|---|
| X1 | Scope reconciler | Trigger row 3 ([03-trigger-matrix](../aws-lineage-collection-plan/03-trigger-matrix.md)): diff active set vs collection scope; enqueue/dormant/reclassify | [01-onboard.md](01-onboard.md) |
| X2 | Change classifier (rule-based) | Workflow spec §2: changed paths ∩ manifest globs ∩ determinant sets ∩ rule packs | [03-incremental-collection.md](03-incremental-collection.md) |
| X3 | Trust-promotion service | Trigger row 16 + approval spec §7: apply per-edge decisions, Advisory → Producer-attested | [06-approval.md](06-approval.md) |
| X4 | Coverage reporter | Workflow spec §1 Coverage stage + approval spec screen 1 states | [02-baseline-collection.md](02-baseline-collection.md) |

### 2.4 W1–W5 — the five Step Functions workflows ([02-aws-architecture](../aws-lineage-collection-plan/02-aws-architecture.md) §4)

| ID | Workflow | Trigger rows | PRD home |
|---|---|---|---|
| W1 | BaselineCollection (Distributed Map over member repos) | 1–3 | [02-baseline-collection.md](02-baseline-collection.md) |
| W2 | IncrementalCollection | 4 | [03-incremental-collection.md](03-incremental-collection.md) |
| W3 | PRGate | 5–6 | [03-incremental-collection.md](03-incremental-collection.md) |
| W4 | DeploymentPromotion | 8–9 | [05-deployment-promotion.md](05-deployment-promotion.md) |
| W5 | NightlyReconciliation | 10 | [07-nightly-reconciliation.md](07-nightly-reconciliation.md) |

## 3. Step↔component matrix

**P** = PRD home (the step doc carries the component's PRD/HLD/LLD) · **x** = participates by reference. Every component has exactly one P (checked in [10](10-verification-and-traceability.md)).

| Component | 1 Onboard | 2 Baseline | 3 Incremental | 4 Runtime | 5 Promotion | 6 Approval | 7 Nightly | 8 Scale |
|---|---|---|---|---|---|---|---|---|
| C1 webhook receiver | x | | **P** | | x | | | x |
| C2 manifest resolver | x | **P** | x | | | | x | |
| C3 extractor runner | | **P** | x | | | | x | x |
| C4 artifact registry | | **P** | x | | x | | x | |
| C5 baseline resolver | | | x | | **P** | | | |
| C6 diff engine | | x | **P** | | | | x | |
| C7 impact service | | | **P** | | | | | |
| C8 policy/waiver service | | | **P** | | | x | | |
| C9 check/comment renderer | | | **P** | | | x | | |
| C10 deploy/rollback adapter | | | | | **P** | | | |
| C11 nightly scheduler | | | | | | | **P** | x |
| C12 metrics/audit/DLQ/replay | x | x | x | x | x | x | x | **P** |
| B1 Business App registry | **P** | x | | | | | | |
| B2 inventory adapter | **P** | x | | x | | | x | |
| B3 CloudWatch interaction pipeline | | x | | **P** | | | x | |
| B4 LLM extraction + cache | | **P** | x | | | | x | |
| B5 sidecar evidence path | | | x | **P** | | | | |
| B6 schema registry | | x | | **P** | | | x | |
| B7 ingest gateway | | x | x | **P** | | | x | x |
| B8 approval UI + API | x | x | | | | **P** | | x |
| B9 review-record store | | | | | | **P** | | |
| X1 scope reconciler | **P** | x | | | | | x | |
| X2 change classifier | | | **P** | | | | x | |
| X3 trust-promotion service | | | | x | x | **P** | | |
| X4 coverage reporter | x | **P** | | x | | | x | |
| W1 BaselineCollection | x | **P** | | | | | | x |
| W2 IncrementalCollection | | | **P** | | | | | x |
| W3 PRGate | | | **P** | | | | | x |
| W4 DeploymentPromotion | | | | | **P** | | | |
| W5 NightlyReconciliation | | | | | | | **P** | x |

30 components; PRD homes per step doc: 01 → 3 (B1, B2, X1) · 02 → 6 (C2, C3, C4, B4, X4, W1) · 03 → 8 (C1, C6, C7, C8, C9, X2, W2, W3) · 04 → 4 (B3, B5, B6, B7) · 05 → 3 (C5, C10, W4) · 06 → 3 (B8, B9, X3) · 07 → 2 (C11, W5) · 08 → 1 (C12) — total 30. Doc 03 is deliberately the largest: push and PR share the classifier → diff → impact → policy chain, and splitting that chain would sever the flow the reader needs whole.

Two home placements that would otherwise surprise:

- **C5 (baseline resolver) homes in 05, not 03.** The `deployment-state` table is *written* by deployment promotion and only *read* by the PR gate. The de-review's most-cited correctness rule ("baseline = environment's last successful deployment, never default-branch HEAD") lives with its writer.
- **B6/B7 (schema registry, ingest gateway) home in 04, not 02.** Every signal passes through them, but their defining behavior — per-signal assertion constraints, evidence validation, metadata-only boundary — is exercised hardest by the runtime-corroboration signals, and step 4 is where all ten signal types are on the table at once.

## 4. Trigger-row ownership

Each of the 17 [trigger-matrix](../aws-lineage-collection-plan/03-trigger-matrix.md) rows is *owned* by exactly one step doc (the doc that specifies the handling end-to-end); other docs may reference a row.

| Rows | Owner | Note |
|---|---|---|
| 1, 2, 3 | [01-onboard.md](01-onboard.md) | Row 1's onboarding half (registration → membership resolution → classification). The collection run it launches is specified in [02](02-baseline-collection.md), which row 1 cross-references |
| 4, 5, 6, 7, 15 | [03-incremental-collection.md](03-incremental-collection.md) | 15 (prompt/model bump) owns here because its consequence is a re-extraction wave through the incremental machinery; the wave *executes* in the nightly window ([07](07-nightly-reconciliation.md) schedules it) |
| 8, 9 | [05-deployment-promotion.md](05-deployment-promotion.md) | |
| 10, 12 | [07-nightly-reconciliation.md](07-nightly-reconciliation.md) | 12 (registry change) reconciles type truth; nightly is its full-coverage backstop |
| 11, 13, 17 | [04-runtime-corroboration.md](04-runtime-corroboration.md) | |
| 14, 16 | [06-approval.md](06-approval.md) | |
| — | [08-scale-and-visibility.md](08-scale-and-visibility.md) | Owns no rows by design: 08 specifies lanes, waves, and visibility *across* all rows |

## 5. Terminology normalization

The package inherits vocabulary drift between the v8 layer and the AWS plan. This package always uses the right-hand column; the mapping is informative.

| Older term (v8 HLD / PRD) | This package (AWS-plan vocabulary) |
|---|---|
| signal `static` | `sca` |
| signal `spark` | `spark-ol` |
| signal `dask` | (deferred — no signal emitted; Dask collector is R&D per the assessment) |
| signal `otel` | `otel-agg` (interaction aggregates) — plus `cloudwatch-agg` (log-derived) and `sidecar-test` (ADR-028), which the v8 layer predates |
| "authoritative" (trust rung) | Not a trust rung. **Authoritative** is a deployment/environment property of an artifact digest ([05](05-deployment-promotion.md)); the human trust ladder is `Proposed → Advisory → UnderReview → ProducerAttested | Rejected | Remediation` ([06](06-approval.md)) |
| "confidence" as decimal | Always integer score + band (`Verified`/`Probable`/`Inferred`), never decimals (ADR-008) |

The closed signal set used everywhere in this package: `sca` · `llm` · `spark-ol` · `airflow-ol` · `warehouse` · `cloudwatch-agg` · `otel-agg` · `sidecar-test` · `registry` · `declared`.

The closed coverage-state set: `automated` · `automated:declarations` · `declared` · `uncovered` · `dormant` · `error` · `excluded:documentation` · `excluded:tooling` · `library` · `unclassified` · `stale`.

## 6. Traceability

- C1–C12 ↔ de-review §6.2 items 1–12, order-preserving.
- B1–B9 ↔ [02-aws-architecture](../aws-lineage-collection-plan/02-aws-architecture.md) §3 rows (IaC row excluded as non-runtime).
- X1–X4 sourced from trigger rows 3, 4, 16 and workflow-spec §1 respectively.
- W1–W5 ↔ [02-aws-architecture](../aws-lineage-collection-plan/02-aws-architecture.md) §4.
