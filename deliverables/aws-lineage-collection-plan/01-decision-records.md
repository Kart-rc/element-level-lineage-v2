# 01 — Decision Records (ADR-020 … ADR-027)

| | |
|---|---|
| **Status** | Draft — for review |
| **Role** | The ten decisions that turn lineage collection into a repeatable, zero-touch AWS service with an approval experience. ADRs decide and justify; normative specifications live in [02-aws-architecture.md](02-aws-architecture.md), [03-trigger-matrix.md](03-trigger-matrix.md), [04-collection-workflow-spec.md](04-collection-workflow-spec.md), [05-approval-ui-spec.md](05-approval-ui-spec.md), and [08-scale-resilience-observability.md](08-scale-resilience-observability.md), and are referenced, not duplicated. |
| **Numbering** | Continues the global sequence from [../architecture-review-v8/03-decision-records.md](../architecture-review-v8/03-decision-records.md) (ends at ADR-019). |
| **Statuses** | `Decided` = implement unless the board objects · `Default — board confirmation requested` = defensible default, explicit confirmation wanted |

Bias declared up front, inherited from the v8 review: proven, boring, operable technology; the smallest number of stateful systems; every choice carries a revisit trigger. Two additions for this package: **no manual invoke point anywhere in the collection design**, and **honest infeasibility statements over silent promises** (the sponsor explicitly asked for pushback where an approach does not hold).

---

## ADR-020: Collection scoping — Business Application for baseline, repo for incremental, artifact digest for binding

**Status:** Decided · **Resolves:** the open "repo level vs Business Application level" scoping debate · **Builds on:** ADR-011 sub-decision 5 (`throughline.yaml`), GAP-C5

**Context.** A Business Application contains one or more services, typically spread across one or more repositories (the PRD models e.g. an Order Management app with dozens of services). The debate — should collection operate per repo or per Business Application — has been treated as a binary. The evidence says it is not: no static analyzer crosses the Kafka, S3, or service boundary (the Deep Dive's "decisive point"), so cross-repo edges are only recoverable above the repo; yet extraction must be deterministic and reproducible, which only a commit SHA provides, and Business Applications are not versioned as a unit. Meanwhile the execution-model assessment (F-02) shows ~20% of the estate (vendor systems, legacy binaries) has no repo at all, so repo-scoped onboarding structurally cannot reach whole-estate coverage.

**Decision.** Three units answer three different questions, and the design uses all three:

| Unit | Role | Question it answers | Anchor |
|---|---|---|---|
| **Business Application** | Baseline-collection scope; onboarding, approval, reconciliation, and reporting unit | "Who signs off, and is coverage complete?" | Service-catalog registry entry `{id, name, team, domain, repos[], services[]}` |
| **Repo / monorepo subtree** | Incremental execution unit | "What do we analyze, and when?" | `throughline.yaml` (ADR-011.5) + commit SHA + toolchain hash |
| **Artifact digest** | Trust-binding unit | "What do we trust in an environment?" | Per-artifact `lineage/<artifact>.yaml`; deployment-authority state machine |

Concretely: **baseline collection is scheduled per Business Application** — the orchestrator resolves the app's member repos (from the service catalog plus the test-automation-service inventory, ADR-025), fans out per-repo extraction, then reconciles at the app level where cross-repo interaction evidence (CloudWatch logs, ADR-025; OTel/OpenLineage later) joins the per-repo supersets into one app-scoped graph. **Incremental collection is triggered per repo** — a push or PR touches exactly one repo, and the baseline already carries the app context, so the incremental path re-derives only the changed repo's edges and re-reconciles them into the standing app graph. **Trust binds to the artifact digest** — a repo builds several artifacts, one artifact runs in several environments, and only a successful deployment promotes the exact digest's lineage to environment-authoritative.

**Why.** Each candidate "single level" fails on its own:
- *Pure repo scoping* — no accountable approval owner (teams own apps, not the union of repos they touch); coverage reporting per repo is meaningless to a change approver; multi-repo apps get fragmented graphs with no reconciliation point; Lane C systems are unrepresentable.
- *Pure Business-Application scoping* — non-deterministic (no app-level SHA), un-cacheable, and forces whole-app rescans when one repo changes; gate latency explodes exactly as GAP-C5 warned for monorepos.
The three-unit split keeps extraction deterministic, approval accountable, and trust environment-precise — and it is already latent in the existing specs (ADR-011.5 declares the repo→service mapping; the PRD's vertical slice is "one business application"; F-06 binds lineage to artifact digests). This ADR makes it explicit and load-bearing.

**Alternatives considered.**
- **Repo-level only** — rejected as above; also collapses when the same service is built from two repos (config split from code).
- **Business-Application-level only** — rejected as above.
- **Service-level scoping** (between the two) — the service is the graph's identity unit (URNs) but a poor collection unit: services share repos and build pipelines, so triggering per service duplicates work the repo trigger already covers.

**Consequences.** The Business App registry becomes a hard dependency of baseline collection (it did not previously exist as a machine-readable object — this package specifies it in [02-aws-architecture.md](02-aws-architecture.md) §4). Approval, coverage, and the UI aggregate by app; extraction caches key by `(repo, SHA, toolchainHash)`; promotion keys by `(artifactDigest, environment)`.
**Revisit trigger:** if the estate adopts a monorepo-per-app convention org-wide, the repo and app units converge and the fan-out layer can be simplified.

---

## ADR-021: Serverless collection plane on AWS — scoped supersession of ADR-018

**Status:** Decided · **Scopes:** ADR-018 (which stands for the graph core) · **Resolves:** the "robust service on AWS" platform question for collection

**Context.** ADR-018 chose Kubernetes and rejected "serverless-first (Lambda/Fargate)" as a "poor fit for the stateful projection and long-lived consumers." That reasoning is correct for the tier it examined — the impact engine's in-memory CSR projection and Kafka consumer groups — and does not examine the collection plane, which has neither property. Every collection step is a stateless function of `(commit SHA, toolchain hash, manifest)` producing immutable artifacts; traffic is bursty (deploy trains, release windows, nightly waves) with long idle valleys — the exact profile serverless prices and scales best.

**Decision.** The **collection plane** — webhook receipt, manifest resolution, extraction orchestration, artifact registry writes, diffing, policy evaluation, SCM check rendering, schedulers, and the approval API — runs serverless on AWS: **API Gateway + Lambda + Step Functions + ECS Fargate tasks + EventBridge + SQS + S3 + DynamoDB** (full mapping in [02-aws-architecture.md](02-aws-architecture.md)). Heavy extraction (git clone, tree-sitter, sqlglot over large repos) runs as Fargate tasks because it exceeds Lambda's duration/storage envelope, not because it is stateful. The **graph core** — Aurora PostgreSQL system of record, the CSR impact projection, and (when it arrives) long-lived Kafka consumers — keeps the ADR-018 posture unchanged. This ADR *scopes* ADR-018; it does not overturn it.

**Why.** At 10,000 repos the collection workload is thousands of short-to-medium independent jobs per day with 10–100× spikes ([08-scale-resilience-observability.md](08-scale-resilience-observability.md) §1). A K8s worker fleet sized for the spike idles most of the day; sized for the average, it queues the spike into SLO breaches. Serverless converts that sizing problem into a concurrency-budget problem, which Step Functions Distributed Map and SQS solve declaratively. Operationally it removes node patching, cluster upgrades, and capacity planning from a team whose hard problems are identity and reconciliation, not infrastructure.

**Alternatives considered.**
- **EKS for everything (ADR-018 as written)** — operable and consistent, but pays a standing cluster + node-fleet cost for a bursty stateless workload and adds K8s operational surface before the pilot has users. Rejected for the collection plane; remains the documented posture for the graph core.
- **EKS with Karpenter/KEDA autoscaling** — closes the elasticity gap but keeps the cluster-ops burden; a reasonable end-state if the org later standardizes on K8s. Noted as the migration path if the revisit trigger fires.
- **AWS Batch instead of Fargate-via-Step-Functions** — good for the nightly wave, weaker for per-PR latency-sensitive tasks (queue scheduling jitter vs. the 30 s gate budget). Rejected as the primary runner; acceptable for the nightly full-rescan wave if cost favors it.

**Consequences.** Two runtime postures exist (serverless collection, K8s-or-managed core) — the boundary is drawn in one diagram and enforced in IaC module structure. Fargate cold starts (~30–60 s with image pull) are inside the nightly budget but outside the PR-gate budget; the PR path therefore never waits on a cold clone ([04-collection-workflow-spec.md](04-collection-workflow-spec.md) §3: shallow fetch + cached layers + warm pool at P3+).
**Revisit trigger:** sustained (not spiky) extraction demand above ~50% duty cycle on the Fargate fleet, or org-wide K8s standardization — either makes a right-sized EKS pool cheaper.

---

## ADR-022: Event backbone at collection scale — EventBridge + SQS now, Kafka/MSK by named trigger

**Status:** Decided · **Scopes:** ADR-002 (Kafka remains the target backbone for the graph core's runtime-event firehose) · **Resolves:** backbone choice for the collection plane at pilot-through-10k-repo scale

**Context.** ADR-002 chose Kafka, with MSK as the managed option. The collection plane's control traffic is much smaller than the runtime-observation firehose ADR-002 was sized for: at 10,000 repos with ≥1 deployment/repo/day plus PR and push events, control-plane volume is ~30–60k events/day ≈ 0.4–0.7 events/s sustained ([08](08-scale-resilience-observability.md) §1 shows the formulas), with spikes that are absorption problems, not throughput problems. A 3-AZ MSK fleet is a standing cost and an operational surface that this volume cannot justify in Phases 0–2.

**Decision.** Collection-plane eventing runs on an **EventBridge custom bus (`throughline-collection`) → per-consumer SQS queues (FIFO where per-entity ordering matters, `MessageGroupId = orderingKey`)**, with **every accepted envelope archived to S3/Iceberg via Firehose** for replay. The **versioned ingestion envelope** ([../lineage-collection-assessment.md](../lineage-collection-assessment.md) §"Contracts to implement first") is transport-agnostic by design — that is the migration insurance. The HLD §3.1 Kafka topic map is preserved verbatim as the target topology; EventBridge rule names mirror topic names 1:1 (`tl.baseline.candidates` → rule `tl-baseline-candidates`) so the migration is a transport swap, not a redesign.

**Named migration triggers to Kafka/MSK (any one suffices):**
1. Lane B runtime OpenLineage volume sustained above ~500 events/s, or a consumer needing log compaction / consumer-group fan-out semantics.
2. The CDC feed to the CSR impact projection (ADR-001) going live — long-lived ordered consumption is Kafka's home turf and ADR-018's domain.
3. Replay-from-S3 windows exceeding the HLD §12 rebuild SLO (Kafka offset replay is faster than S3 scan-and-refeed at large windows).

**Alternatives considered.**
- **MSK from day one** — architecture-consistent with ADR-002 but ~3 brokers × 24/7 plus ops for <1 event/s of control traffic; rejected for Phases 0–2. It is not a rejection of ADR-002: the runtime-observation firehose that justifies Kafka arrives with Lane B scale, which is exactly trigger 1.
- **Kinesis Data Streams** — cheaper than MSK, ordered shards, but a third streaming idiom (neither the Kafka target nor the EventBridge start) with shard-management overhead; rejected to keep the migration path binary.
- **SQS only (no EventBridge)** — loses content-based routing and the 1:N fan-out that the trigger matrix needs (one deploy event feeds promotion, status, and audit consumers); rejected.

**Consequences.** EventBridge's at-least-once delivery makes consumer idempotency mandatory — already required by the envelope's `idempotencyKey` and the reconciliation contract, so no new burden. FIFO queue throughput caps (~300 msg/s/group without batching) are three orders of magnitude above control-plane need. CloudWatch log-derived interaction evidence (ADR-025) is the one high-volume flow, and it **bypasses the bus entirely** (subscription filter → Firehose → S3), so the bus never carries span-scale traffic.
**Revisit trigger:** the three named triggers above.

---

## ADR-023: Zero-touch trigger authority — one GitHub App, no manual invoke point

**Status:** Decided · **Resolves:** the "no invoke point" requirement; **Builds on:** de-review §6.2 component 1 (webhook receiver with dedup and installation-scoped credentials), F-05 (decouple publication from merge)

**Context.** The requirement is that baseline collection fires the first time with no human action, and re-fires on every code change, forever. That demands a single, reliable, org-wide integration authority with events for repo lifecycle and code change, credentials that scope to installations rather than people, and a write surface for gate results.

**Decision.** A single **org-level GitHub App** is the SCM integration point, supplying: webhooks (`installation_repositories`, `push`, `pull_request`, `pull_request_review`), the Checks API for gate output, the Contents API for manifest resolution, and short-lived installation tokens (no PATs, no deploy keys). **Repo added to the installation ⇒ collection begins** — the webhook receiver emits `repo.onboarded` and the baseline workflow starts immediately, publishing at **Advisory** trust per F-05; a merged `throughline.yaml` is a *trust upgrade*, never an entry requirement. If the manifest is missing, the platform opens a scaffold PR (informed by archetype detection) and proceeds without waiting for the merge.

**The no-manual-invoke invariant, stated normatively:** the trigger matrix ([03-trigger-matrix.md](03-trigger-matrix.md)) is the closed set of ways collection work starts. Every row is an event. The only human-shaped inputs in the system — registering a Business App, merging a manifest, deciding an approval — are themselves events that appear as rows. There is no CLI, console button, or API endpoint whose purpose is "run collection now"; operational replay exists ([08](08-scale-resilience-observability.md) §4) but replays past events rather than minting new work.

**Alternatives considered.**
- **EventBridge inbound webhooks (partner source / API destination)** — fewer moving parts, but the receiver must verify HMAC signatures, deduplicate on `X-GitHub-Delivery`, enrich with installation context, and rate-limit — the de-review's component 1 responsibilities — which the managed inbound path cannot host; rejected.
- **Per-repo webhooks or personal access tokens** — 10,000 repos of webhook config drift and token rotation; the exact failure F-05 warns about (coverage becomes a function of team cooperation); rejected.
- **CI-resident collection (a step teams add to their pipelines)** — inverts the zero-touch requirement into 10,000 PRs asking teams to adopt a step; merge-bound onboarding is the documented bottleneck (F-05: "merge throughput is the constraint"); rejected as the *trigger* mechanism. (CI remains where gate *results* surface.)

**Consequences.** The GitHub App's key is the platform's most sensitive credential (Secrets Manager, rotation, least-scope). GitHub webhook delivery is at-least-once and can lag; the nightly reconciliation sweep (trigger row 10) is the documented safety net for missed deliveries, per the de-review state machine's "repair missed incremental events."
**Revisit trigger:** a second SCM (GitLab/Bitbucket) entering the estate → the receiver grows an adapter per SCM behind the same normalized events; the invariant is unchanged.

---

## ADR-024: Approval experience — trust promotion through immutable review records

**Status:** Decided · **Resolves:** the approval-surface requirement · **Builds on:** HLD §6.5 (waivers), IMP-009/IMP-011/IMP-012, F-05 (trust ladder), F-06 (per-edge acknowledgement), ADR-006 (human-confirmed merges)

**Context.** Collection results — proposed nodes, edges, and per-change deltas — must surface to end users for review and approval. The specs already define the objects (waiver, attestation, review actions, identity-merge queue) but no screen exists anywhere, and the execution-model assessment adds two hard constraints: bulk-accept produces worthless labels (acknowledgement must be per-edge and only for material mappings), and the accept/correct diff is the calibration corpus the confidence model is waiting for.

**Decision.** Approval is a first-class subsystem with four rules:

1. **Per-edge decisions.** Users acknowledge, comment, accept, correct, reject, or request remediation per edge (IMP-009). Explicit acknowledgement is required **only for material mappings**; everything else in a proposal is recorded as unreviewed rather than silently blessed. Every user correction captures **before and after state**.
2. **Immutable review records.** Finalizing a review emits an append-only record — proposal, evidence, per-edge decisions, actors, timestamps (IMP-011) — stored in Aurora and exported as a content-addressed, hash-chained S3 object under Object Lock (governance mode). Records are never updated; corrections are new records referencing the old.
3. **Approval is trust promotion, not admission.** Lineage is already published at Advisory when review starts (F-05). An approval promotes edges Advisory → **Producer-attested**; a rejection demotes/flags; nothing in the approval path deletes evidence. No approval action modifies source schemas, pipelines, or deployments (IMP-012).
4. **Steward queues for the decisions users cannot make alone:** fuzzy identity merges (never auto-merged, per ADR-006), waivers (HLD §6.5 semantics verbatim — downstream-owner/steward approver, ≤90 days expiry, self-approval rejected, >10%/30d circuit breaker), and attestation renewals.

**UI stack:** React SPA on S3 + CloudFront; API Gateway (HTTP API) + Lambda for the approval API; Cognito federated to the corporate OIDC IdP (ADR-016), groups mapped to `viewer` / `domain-steward` / `platform-admin` (HLD §9.1). Screens, states, and endpoints in [05-approval-ui-spec.md](05-approval-ui-spec.md).

**Alternatives considered.**
- **PR-comment-only approval (no UI)** — keeps developers in-flow and is retained as a *surface* for the CI delta, but cannot host app-level coverage review, steward queues, or Lane C systems that have no PRs; rejected as the sole surface.
- **Amplify Hosting** — no benefit over S3+CloudFront for a plain SPA in an IaC-managed account; rejected.
- **ECS-hosted approval API** — unnecessary for a low-QPS CRUD API; deferred to the same trigger as ADR-022's migration (if the API grows long-lived subscriptions).
- **Mutable review state with audit log** — an audit log alongside mutable rows is weaker than append-only records and fails IMP-011's "immutable review record" verbatim; rejected.

**Consequences.** The review record store grows monotonically (cheap: text objects); the calibration corpus (proposal-vs-accepted diffs, keyed by provenance and archetype) accumulates as a free by-product and is explicitly a deliverable, not exhaust. Approval latency becomes a measured funnel (time-to-first-review, ack coverage) surfaced on the coverage dashboard.
**Revisit trigger:** if per-edge acknowledgement measurably stalls adoption, narrow the material-mapping definition — never widen to bulk-accept.

---

## ADR-025: Baseline context sources — test-automation-service inventory and CloudWatch log evidence

**Status:** Decided · **Resolves:** how baseline collection knows which repos are active and how apps/repos actually interact · **Extends:** the signal responsibility matrix in [../lineage-collection-assessment.md](../lineage-collection-assessment.md)

**Context.** Baseline collection at Business-Application scope (ADR-020) needs two facts the code cannot supply: *which member repos are alive* (10,000 registered repos include dormant forks and archived experiments; scanning them wastes the fleet and pollutes the graph), and *how the app's repos and neighbors actually interact at runtime* (the cross-repo edges no static analyzer can see). Two organizational capabilities already exist: the **test automation service** knows which repos are actively built and exercised, and **AWS CloudWatch** holds the estate's service logs.

**Decision.**

1. **The test-automation service is the authority for "active repo."** An inventory-sync adapter (Lambda) pulls the active-repo set on a schedule and on-demand at Business-App onboarding, writing `repo.inventory.delta` events. Baseline fan-out enumerates *catalog members ∩ active set*; members outside the active set are recorded as `dormant` in the coverage report — explicitly visible, never silently skipped (the "absence of evidence must never mean no dependency" invariant applies to dormancy too).
2. **CloudWatch logs are an interaction-evidence signal.** Subscription filters on in-scope log groups → Firehose → S3/Iceberg; a scheduled aggregation job (Glue/Athena at pilot scale) extracts caller→callee, topic, queue, and endpoint interactions with counts and recency, emitting `CloudWatchInteractionAggregate` observations through the standard ingest gateway. The signal is scoped exactly like ordinary OTel in the responsibility matrix: it **may assert** service/endpoint/topic interaction, frequency, and recency; it **must not assert** field/column mappings; posture **interaction-confirming only**, feeding the confidence model as a runtime term. Raw log lines never enter the lineage graph (metadata-only boundary: the aggregator emits identities and counts, not payloads).

**Why.** The active-repo set turns a 10,000-repo scan into the smaller real workload and gives baseline a defensible scope. CloudWatch evidence is the cheapest available runtime corroboration at baseline time — it exists today, before OTel adoption or OpenLineage listeners are rolled out, and it is precisely the cross-repo signal ADR-020's app-level reconciliation needs. Both are corroboration, not extraction: they adjust confidence and coverage, never invent column lineage.

**Alternatives considered.**
- **Treat catalog membership as "active"** — catalogs rot; scanning dormant repos wastes exactly the fleet capacity the 10k-repo budget needs; rejected as the sole source (the catalog remains the *membership* authority; the test-automation service is the *activity* authority).
- **Git-activity heuristics (recent commits) for activeness** — cheap but wrong in both directions (active-but-stable services, doc-only churn); retained only as a cross-check metric.
- **CloudWatch Logs Insights queries on demand** (no export) — interactive-scale, not fleet-scale, and leaves no replayable raw evidence; rejected.
- **Wait for OTel rollout instead of log mining** — leaves baseline with zero runtime corroboration for the entire adoption window; rejected. The log signal is explicitly the bridge; OTel/OpenLineage supersede it per-service as they arrive, and the aggregate schema is shaped so the OTel aggregate is a drop-in replacement.

**Consequences.** Two new integration adapters ([02](02-aws-architecture.md) §3) and one new signal row in the responsibility matrix. Log-format diversity means the interaction extractor is config-per-archetype (reviewed parsing rules, like URN normalizers — "code-reviewed config, not inference"). If log hygiene is poor for an app, its interaction evidence is simply sparse — the coverage report says so, and confidence stays capped at the runtime-less 64 for uncorroborated edges, which is the designed behavior.
**Revisit trigger:** OTel interaction aggregates covering ≥80% of an app's services → retire that app's CloudWatch subscription filters.

---

## ADR-026: Scale, resilience, and end-to-end flow visibility

**Status:** Decided · **Resolves:** the 10,000-repo / daily-deploy / spike requirement and the end-to-end visibility requirement · **Specified in:** [08-scale-resilience-observability.md](08-scale-resilience-observability.md)

**Context.** The service must baseline 10,000 repos, absorb ~10,000 deployments/day (≥1 per repo) plus PR/push traffic with significant spikes, degrade without losing work, and let any user or operator answer "where is my lineage run?" without grepping logs.

**Decision.**

1. **Fan-out:** baseline waves run as Step Functions **Distributed Map** over the repo list (native 10k-child concurrency ceiling, per-wave concurrency caps), executing Fargate extraction tasks (Spot for nightly/backfill waves, on-demand for interactive paths). Per-account quota budgets (Fargate vCPUs, `RunTask` rate, state transitions) are first-class capacity inputs with formulas in [08](08-scale-resilience-observability.md) §2.
2. **Priority lanes:** three queue lanes — **PR-gate** (interactive, p95 < 30 s budget) > **deploy promotion** (minutes) > **baseline/nightly backfill** (hours) — with separate SQS queues, separate concurrency reservations, and backpressure that sheds *backfill* first. A spike can never starve the PR lane.
3. **Resilience:** idempotent everything (envelope `idempotencyKey`; consumers converge under replay), per-consumer DLQs with alerting, replay from the S3 envelope archive as a standing workflow, and a per-component failure-mode table (failure → detection → degradation → recovery) in [08](08-scale-resilience-observability.md) §4. The gate inherits its documented posture: fail-open + warn, never silently green.
4. **End-to-end visibility:** every flow carries a **correlation ID** (the envelope `eventId`, joined to `commitSha`/`artifactDigest`) through webhook → bus → workflow → task → publish; OTel instrumentation (per ADR-017) across Lambda/Step Functions/Fargate with X-Ray as the pilot trace backend; and a **collection-status record** per flow (DynamoDB: trigger, stage, timestamps, outcome, error class) that powers the "where is my run?" view in the UI and `GET /v1/flows/{correlationId}/status`. Fleet dashboards: throughput, queue lag per lane, DLQ depth, fail-open rate, freshness SLIs.

**Alternatives considered.** **SQS-consumer fan-out instead of Distributed Map** — workable, but re-implements map-state bookkeeping (per-item retry, result aggregation, partial-failure semantics) that Step Functions provides; rejected. **One shared queue with priority field** — priority-in-band starves under spike exactly when it matters; rejected in favor of physically separate lanes. **Logs-as-visibility (CloudWatch Logs Insights on demand)** — answers operators slowly and users never; rejected as the primary mechanism; logs remain the forensic layer.

**Consequences.** The status record adds one small write per stage per flow (~5–7 writes/flow — negligible against DynamoDB on-demand). Distributed Map's 10k ceiling means a >10k-repo estate batches into waves; the wave planner is specified in [08](08-scale-resilience-observability.md) §2.
**Revisit trigger:** sustained fleet duty cycle >50% (see ADR-021's trigger); or trace volume outgrowing X-Ray → managed OTel backend per ADR-017's stack.

---

## ADR-027: Canonical lineage observation schema — one schema for all three mechanisms; uniform envelope, signal-constrained assertions

**Status:** Decided · **Resolves:** the requirement that SCA, LLM, and runtime collection produce a consistent schema · **Builds on:** the ingestion envelope and signal responsibility matrix ([../lineage-collection-assessment.md](../lineage-collection-assessment.md)), ADR-007 (conflict matrix), OpenLineage alignment noted in the Deep Dive

**Context.** The sponsor requires the three collection mechanisms — SCA, LLM, runtime — to produce a consistent schema, and asked for pushback if the approach is unsound. The pushback is a refinement, not a rejection: a schema that forces the three signals to emit *identical assertions* would be actively harmful. The signals observe different realities with different authority — runtime interaction evidence structurally cannot see column mappings; LLM output must not carry authoritative types; Spark column facets are silently absent for UDFs/RDDs. Uniform payloads would erase provenance and launder low-authority claims into high-authority fields, which is precisely what the conflict matrix (ADR-007) and responsibility matrix exist to prevent.

**Decision.** All three mechanisms emit **one versioned canonical schema** = the existing **ingestion envelope** wrapping an **OpenLineage-aligned observation payload** extended with namespaced custom facets for what the standard lacks — path/guard, codeRef, determinant set, provenance detail, extractor/parser/prompt/model versions (the Deep Dive already flags this as "a deliberate extension" relative to OpenLineage's open DetailedLineage discussion). Consistency is enforced at three layers:

1. **Uniform structure.** Same envelope, same payload grammar, same URN vocabulary, for every signal. A consumer parses one schema, ever.
2. **Signal-constrained assertions.** The schema carries a machine-enforced **assertion-constraint table** (normative form in [04-collection-workflow-spec.md](04-collection-workflow-spec.md) §5): per signal, the fields it MAY populate and MUST NOT populate, taken verbatim from the signal responsibility matrix. A SCA event asserting `runStats`, an LLM event asserting authoritative `type`, or an interaction aggregate asserting `columnMapping` fails validation — by construction, not by reviewer vigilance.
3. **Registry-validated at the gateway.** Schemas are JSON Schema documents, versioned in a schema registry (git-versioned, published to S3, served to validators; AWS Glue Schema Registry is the managed alternative if Avro/protobuf transport arrives with Kafka). The ingest gateway validates every event against `(schemaVersion, signal)` and routes mismatches to the DLQ. No signal bypasses validation, including the platform's own extractors.

Reconciliation then **preserves disagreements as conflicts** (the existing rule: "do not average them away") — consistent schema in, per-attribute authority applied after.

**Why.** This gives the sponsor's requirement its real value — one parser, one validator, one evolution process, cross-signal joins for free — without the false uniformity failure mode. It also keeps the OpenLineage door open: runtime events are already OL; static/LLM emitters producing OL-shaped events with custom facets remain consumable by any OL-aware tool, which protects the ADR-012 catalog-integration option.

**Alternatives considered.**
- **Strictly identical payloads for all signals** — rejected as above: erases authority, launders confidence, and contradicts ADR-007.
- **Pure OpenLineage with no extensions** — loses path/guard/codeRef/determinants, the fields that differentiate this platform's collection (path-qualified edges are load-bearing in the PRD); rejected.
- **Per-signal bespoke schemas + a normalization layer** — the status quo ante; pushes inconsistency into N×M consumer mappings and makes schema evolution N simultaneous migrations; rejected — normalization happens once, in the emitters, against one contract.
- **Schema-on-read (validate in consumers)** — turns every consumer into a validator with drifting copies of the rules; rejected. The gateway is the single enforcement point.

**Consequences.** Emitters carry a thin conformance library (envelope construction, facet vocabulary, constraint self-check) — one library, three mechanisms. Schema evolution is versioned and additive-first; breaking payload changes require a dual-publish window ([04](04-collection-workflow-spec.md) §5.4). The assertion-constraint table becomes the executable form of the responsibility matrix — the doc and the validator can no longer drift apart.
**Revisit trigger:** OpenLineage standardizing sub-transformation/element lineage (the open DetailedLineage facet work) → fold the custom facets into the standard forms and deprecate the namespaced ones.

---

## ADR-028: Feature-flagged sidecar runtime collection — on during integration tests, off in production

**Status:** Decided · **Resolves:** how the runtime path produces evidence without production overhead · **Builds on:** the `RuntimeLineageObservation` contract and its gates ([../lineage-collection-assessment.md](../lineage-collection-assessment.md) §5), ADR-025 (test-automation service), ADR-020 (artifact-digest binding), the identity contract's cross-environment rule

**Context.** The runtime leg of the three-path ladder needs execution evidence, but the estate-wide alternatives all pay somewhere: production instrumentation carries overhead and rollout friction (the de-review is blunt that no universal zero-overhead mechanism can prove in-process element mappings), and waiting for production traffic means runtime corroboration arrives days after a change ships. The org already runs integration tests through the test-automation service (ADR-025) — a controlled environment where overhead is acceptable and every run is tied to a commit SHA and artifact digest.

**Decision.** Runtime lineage collection ships as an **instrumented sidecar attached to applications, enabled by a feature flag only during integration-test runs, and off in production.**

1. **Mechanics.** The sidecar (container alongside the app in the test environment) observes boundary I/O — HTTP/gRPC calls, Kafka produce/consume, S3/database access — and, where teams opt in, receives explicitly instrumented in-process element-mapping events (the `RuntimeLineageObservation` contract, unchanged: emitted once per operation/path/schema version, never per row). It emits canonical envelopes (ADR-027) with `provenance.signal = sidecar-test`, stamped with `environment = <test env>`, the test-run ID, commit SHA, artifact digest, and the **flag state** — evidence is always attributable to the run that produced it.
2. **The flag.** Sidecar activation is deployment configuration (AWS AppConfig or the org's flag system), asserted on by the test-automation service for integration runs and **asserted off in production by policy** — the platform alarms if `sidecar-test` evidence ever arrives tagged with a production environment (that is a misconfiguration, not a signal).
3. **What the evidence means — the honest scoping.** The identity contract's rule stands: **cross-environment corroboration is rejected** — a test run never directly raises the confidence of a production edge. Sidecar evidence corroborates at two legitimate levels instead:
   - *Within the test-environment graph*: full runtime term — it confirms executed paths, interaction edges, and (where instrumented) element mappings for that environment.
   - *At the artifact-digest level* (ADR-020): the evidence attaches to the digest as an **execution-confirmed-in-test facet**. When that exact digest deploys to production, its edges carry "executed under integration test for this digest" — lifting them above the static-only posture in impact and UI treatment, with a **Probable ceiling**: production **Verified** still requires production-environment runtime evidence (OpenLineage, CloudWatch/OTel aggregates).
4. **Where it lands in the loop.** Integration tests run in the PR/merge window — so runtime corroboration becomes available **pre-deploy, inside the change loop**, rather than days later from production traffic. The PR surface can say "3 of 4 changed paths executed under integration tests" before anyone merges. Coverage truth applies as everywhere: paths the test suite never exercises stay `not-observed`; test coverage gaps become visible lineage-coverage gaps, which is a feature, not a flaw.

**Why.** Zero production overhead by construction (the strongest objection to runtime instrumentation disappears); evidence arrives at the moment the change loop needs it; the test-automation service already orchestrates the runs and carries the correlation identifiers; and the artifact-digest binding gives test evidence a sound bridge into production context without violating the environment rule.

**Alternatives considered.**
- **Production sidecars (always-on or sampled)** — real prod evidence, but pays latency/overhead on every hop of every service and requires an estate-wide rollout negotiation; rejected for this phase. Production evidence continues to arrive via the passive paths (CloudWatch aggregates now, OpenLineage/OTel as adopted).
- **eBPF/mesh-level capture in production** — lower overhead than in-process sidecars but sees bytes, not element semantics, and still needs prod rollout; noted in the de-review's alternatives table as a later layer; deferred.
- **Test-time evidence treated as production Verified** — rejected outright: it would launder test-environment observation into production trust, exactly what the cross-environment rule and the zero-cross-environment-auto-merge gate exist to prevent.
- **No runtime-in-test signal (wait for prod adoption)** — leaves the incremental loop's runtime path empty for the entire OTel/OpenLineage adoption window; rejected.

**Consequences.** A new signal row (`sidecar-test`) in the assertion-constraint table ([04](04-collection-workflow-spec.md) §5.2) and a new trigger row (integration-test run completed → evidence ingestion, [03](03-trigger-matrix.md)). The sidecar image and its conformance library become platform deliverables ([06](06-delivery-roadmap.md), Phase 2). Evidence volume is test-run-bounded, not prod-scale — negligible against the [08](08-scale-resilience-observability.md) §1 budgets. The confidence model gains one posture ("test-corroborated, Probable ceiling in prod context") whose exact weight is calibrated on the pilot slice like every other weight — priors, not truths.
**Revisit trigger:** production OTel/OpenLineage coverage ≥ 80% for an app → the digest-level facet stops adding information for that app and can be dropped from its impact rendering; or a future decision to run sampled sidecars in production supersedes the off-in-prod policy explicitly.

---

## ADR-029: Repo classification — application, library, infrastructure, documentation; declared-first, detected-fallback; exclusion is a recorded state, never silence

**Status:** Decided · **Resolves:** how non-application repos (infrastructure, libraries, documentation, tooling) are excluded from — or partially included in — collection, in both the baseline and update flows · **Builds on:** ADR-020 (scoping), ADR-025 (active-repo inventory), F-03 (determinants), the "absence of evidence must never mean no dependency" invariant

**Context.** A 10,000-repo estate is not 10,000 applications. A large fraction is infrastructure-as-code, shared libraries, documentation, and tooling. Treating them all as applications wastes the extraction fleet and pollutes the graph with junk candidates. But naive exclusion is worse than waste, three ways: **IaC repos declare the estate's datasets** — topics, buckets, queues, databases, ownership tags — and FR-C1 explicitly names IaC a signal source, so dropping them discards identity evidence; **library repos shape consumer lineage** — a serialization library's field mapping or a data-access helper changes what consumers emit, which is exactly the determinant problem F-03 exists for; and **silent exclusion is a coverage lie** — a repo nobody scanned must be distinguishable from a repo with no lineage.

**Decision.** Every repo (or monorepo subtree) in collection scope carries a **classification**: `application` · `library` · `infrastructure` · `documentation` · `tooling` · `unknown`.

1. **Declared-first.** `throughline.yaml` gains an optional `kind:` field per repo/subtree (monorepos mix kinds: a docs subtree inside an application repo classifies independently). A declaration always wins and is reviewed like any manifest change.
2. **Detected-fallback.** Absent a declaration, archetype detection classifies from evidence: build files and deployable-artifact definitions → `application`; published-package manifests without a deployable → `library`; dominant IaC file share → `infrastructure`; no code → `documentation`. Low-confidence detection yields `unknown`, which gets a **scan-light pass** (cheap Tier-1 sweep to check whether anything lineage-relevant exists) and a steward confirmation item — never a silent guess in either direction.
3. **Per-class treatment** (normative table in [04-collection-workflow-spec.md](04-collection-workflow-spec.md) §8):
   - `application` — full extraction in both flows.
   - `library` — **no direct edge extraction**; registered as a *determinant source*. A library release is recorded (name, version, digest) but triggers no extraction of its own: its lineage effect materializes through **consumers** — a dependency-manifest/lockfile bump in an application repo is a determinant change there (F-03), which drives the consumer's own incremental run. Unpinned/latest-tag consumption is the gap; the nightly rescan covers it, and the divergence metric would expose a systematic hole.
   - `infrastructure` — **resource-declaration extraction only**: Tier-1 parse of Terraform/CloudFormation/CDK for datasets, topics, queues, and ownership, emitted as entity candidates and identity evidence (`sca` signal, declaration facets). No transform edges — IaC declares that things exist, not how data flows through them.
   - `documentation` / `tooling` — excluded from extraction, zero compute.
4. **Exclusion is a recorded, reversible state.** Every classified-out repo appears in the app coverage report as `excluded:<class>` — visible, auditable, filterable — alongside `dormant` (ADR-025). Reclassification (declaration change, steward decision, or detection flip on new evidence) is an event that re-enters the repo through the baseline flow. Nothing ever just disappears from scope.

**Why.** This turns "exclude the noise" from an allow-list guess into a typed contract with per-class behavior: the fleet spends compute only where lineage can exist, IaC's identity evidence is kept, library influence flows through the determinant machinery that already exists instead of a bespoke library analyzer, and the coverage report stays honest about what was deliberately not scanned.

**Alternatives considered.**
- **Scan everything** — burns the [08](08-scale-resilience-observability.md) §1 budget on repos that cannot produce lineage and floods review inboxes with junk proposals; rejected.
- **Manual allow-list of application repos** — rots immediately at 10k scale and is merge-bound (the F-05 failure shape); rejected.
- **Name/path heuristics only** (`*-docs`, `terraform-*`) — wrong in both directions with no confidence signal and no override path; rejected as sole mechanism (patterns may inform detection, never decide it).
- **Extract libraries directly** (analyze library code for potential lineage) — produces edges with no deployable context that double-count once consumers are analyzed; rejected — libraries influence lineage through consumers, and determinants already model that.

**Consequences.** The Business App registry stores classification per member repo; baseline fan-out routes per class ([04](04-collection-workflow-spec.md) §1); the incremental classifier gains a class check as its first gate ([04](04-collection-workflow-spec.md) §2); the coverage dashboard shows the classification distribution and `excluded:*` states ([05](05-approval-ui-spec.md)); stewards can reclassify from the UI. Detection rules are code-reviewed configuration, versioned with the toolchain hash like the classifier rule packs.
**Revisit trigger:** evidence of systematic misclassification (e.g. divergence findings tracing to an `excluded` repo) → tighten detection or force scan-light on the affected class.

---

## Summary table

| ADR | Decision | Status |
|---|---|---|
| 020 | Baseline scopes to Business Application; incremental executes per repo; trust binds to artifact digest | Decided |
| 021 | Serverless collection plane (Lambda/Step Functions/Fargate/EventBridge); graph core keeps ADR-018 posture | Decided |
| 022 | EventBridge + SQS backbone now; Kafka/MSK by three named triggers; envelope is the migration insurance | Decided |
| 023 | One org-level GitHub App; repo-added ⇒ collection begins at Advisory; no manual invoke point exists | Decided |
| 024 | Per-edge approval with immutable review records; approval = trust promotion Advisory → Producer-attested | Decided |
| 025 | Test-automation service = active-repo authority; CloudWatch logs = interaction-confirming signal (never column lineage) | Decided |
| 026 | Distributed Map fan-out, priority lanes, DLQ/replay, correlation-ID tracing + per-flow status records | Decided |
| 027 | One canonical OpenLineage-aligned schema for SCA/LLM/runtime; uniform structure, signal-constrained assertions | Decided |
| 028 | Feature-flagged sidecar runtime collection in integration tests, off in production; digest-level corroboration, Probable ceiling in prod context | Decided |
| 029 | Repo classification (application/library/infrastructure/documentation): declared-first, detected-fallback; per-class treatment; exclusion is a recorded state | Decided |
