# 08 — Scale, Resilience, and End-to-End Flow Visibility

| | |
|---|---|
| **Status** | Draft — for review (normative once approved) |
| **Role** | Expands ADR-026: capacity math for the 10,000-repo target, fan-out and quota design, priority lanes and backpressure, failure modes, and the end-to-end observability spec. Convention inherited from the v8 package: every derived number shows its formula; no naked numbers. |

## 1. Capacity math

Stated assumptions (calibrate in the Phase 5 scale rehearsal; every downstream number recomputes from these):

| Symbol | Meaning | Planning value |
|---|---|---|
| `R` | Registered repos | 10,000 |
| `a` | Active fraction (test-automation inventory, ADR-025) | 0.7 → `A = a·R = 7,000` active repos |
| `d` | Deployments per active repo per day | 1 (floor; the requirement) |
| `p` | Pushes per active repo per day | 3 |
| `q` | PR events (open+sync) per active repo per day | 3 |
| `t̄_base` | Mean full-extraction task time | 6 min = 0.1 h |
| `t̄_incr` | Mean selective re-derivation time | 2 min |
| `f` | Fraction of pushes with lineage-relevant impact (classifier pass-through) | 0.4 |

**Control-plane event volume.** `E = A·(d + p + q) = 7,000 × 7 = 49,000 events/day ≈ 0.57 events/s` sustained. A release-train spike of 20% of daily deploys inside one hour is `0.2 × 7,000 / 3,600 ≈ 0.39 events/s` added — even a 100× spike (~57 events/s) is three orders of magnitude below EventBridge/SQS limits. **Conclusion (backs ADR-022): the backbone is never the bottleneck; extraction compute is.**

**Baseline wave compute.** `W = A × t̄_base = 7,000 × 0.1 h = 700 task-hours`. Wall-clock = `W / C` for concurrency `C`: C = 250 → 2.8 h; C = 500 → 1.4 h. Target: **an org-wide baseline wave completes overnight (< 8 h) at C ≥ 100**, comfortably true with margin for retries and stragglers.

**Daily incremental compute.** Classifier runs are Lambda-milliseconds (`A·p = 21,000/day` — negligible). Re-derivations: `A·p·f × t̄_incr = 8,400 × 2 min = 280 task-hours/day ≈ 11.7 task-hours/hour`, i.e. **~12 concurrent tasks on average**; a 10× spike needs ~120 concurrent — inside a modest Fargate budget without touching the baseline reservation.

**LLM residue.** Bounded by cache misses, not pushes: the content-addressed key `(codeSliceHash, schemaHash, modelVersion, promptVersion)` (F-04) means steady-state daily misses ≈ slices whose content actually changed. Model/prompt bumps invalidate the whole cache by design — which is why trigger row 15 routes them to nightly Bedrock **batch** waves, never the interactive path.

## 2. Fan-out and quota design

- **Distributed Map** (BaselineCollection, NightlyReconciliation): native ceiling of 10,000 concurrent child executions per map run. Estates beyond 10k repos batch into **waves** (`⌈R_scope / 10,000⌉` map runs, sequential or capacity-interleaved); the wave planner also orders by app criticality so Tier-1 apps baseline first.
- **Per-wave concurrency cap** set from the account budget, not the ceiling: `C_wave = min(mapMaxConcurrency, ⌊vCPU_quota × reserveFraction / vCPU_task⌋, RunTask_rate_headroom)`. Planning point: 4 vCPU/task, backfill reserve fraction 0.5 → with the default adjustable Fargate quota this yields C in the hundreds; exact account values are measured in the Phase 0 landing zone and re-verified in the Phase 5 rehearsal (quotas are adjustable — the design treats them as **inputs, requested ahead of need**, not discovered limits).
- Quota watch-list (alarmed as consumables): Fargate on-demand + Spot vCPUs, ECS `RunTask` call rate, Step Functions state transitions/s and open executions, Lambda concurrent executions, Bedrock model TPS/TPM, EventBridge PutEvents.
- **Spot with dignity:** nightly/backfill tasks run Fargate Spot with automatic on-demand retry on interruption (map-state retry policy); interactive lanes never use Spot.

## 3. Priority lanes and backpressure

Three physically separate SQS lanes with separate concurrency reservations (ADR-026):

| Lane | Traffic | Latency objective | Reservation behavior |
|---|---|---|---|
| **pr-gate** (FIFO by repo) | trigger rows 5–6 | p95 < 30 s end-to-end (HLD §6.1) | Fixed reserved concurrency; never borrowed against |
| **deploy** | rows 8–9 | minutes | Reserved; may borrow idle backfill capacity |
| **baseline/backfill** | rows 1–3, 10, 15 | hours (overnight window) | Gets the remainder; **first to shed under pressure** |

Backpressure rules: queue-age alarms per lane; when the account budget saturates, the wave planner pauses backfill map runs (they checkpoint at item granularity — Distributed Map resumes where it stopped); the pr-gate lane's reservation guarantees a deploy-train spike can delay tonight's baseline wave but never a PR check. If the pr-gate lane itself breaches its budget, the gate's own documented posture applies: 120 s hard timeout → **fail-open + warn** — degraded honestly, never silently green.

## 4. Resilience: failure modes, DLQ, replay

Idempotency is the foundation: every envelope carries `idempotencyKey`; consumers converge under replay; duplicate application changes no state (assessment reconciliation rules). On top of that:

| Component | Failure | Detection | Degradation | Recovery |
|---|---|---|---|---|
| Webhook receiver | Down / erroring | APIGW 5xx alarms | GitHub retries deliveries; missed ones caught by nightly sweep (row 10, "repair missed incremental events") | Redeploy; replay window covers the gap |
| EventBridge → SQS | Delivery failure | Rule DLQ depth | Events land in rule DLQ, not lost | Redrive from DLQ |
| Fargate capacity | Spot interruption / quota hit | Task-failure metrics, quota alarms | Map retry (Spot→on-demand); backfill sheds first (§3) | Quota raise; wave resumes from checkpoint |
| Bedrock | Throttle / outage | Error-rate alarms | Cache hits still serve; misses queue for the nightly wave; **deterministic extraction unaffected — and only deterministic edges gate (F-04)** | Queue drains when service recovers |
| Ingest gateway | Down | Health checks, queue age | Producers buffer in SQS; Firehose archive continues independently | Consumers drain; replay verifies convergence |
| Aurora (graph core) | Failover | RDS events | Read serving continues from projections (ADR-018 posture); gateway buffers writes | Multi-AZ failover; buffered writes drain |
| Schema registry (S3-published) | Unavailable | Validator fetch errors | Validators pin last-known versions (fail-static, not fail-open) | Republish; no event loss |
| Collector silence (Lane B) | Heartbeat loss | Freshness SLIs | Edges → `stale`; **absence is never inferred** (row 13) | Backfill on listener recovery |
| Poison events | Repeated consumer failure | Per-consumer DLQ depth | Quarantined with reason; alert at depth > 100, drain < 24 h (HLD SLO) | Triage; fix; redrive |

**Replay** is a standing Step Function reading the S3/Iceberg envelope archive by time/source/repo filter and re-feeding the gateway. It re-processes *past* envelopes only — it cannot mint new work (the ADR-023 invariant) — and its acceptance test is "replayed events converge to identical graph state."

## 5. End-to-end flow visibility

Requirement: any user or operator answers "where is my lineage run?" in one lookup; every flow is traceable hop-by-hop.

1. **Correlation ID.** The receiver mints `correlationId` (= envelope `eventId` of the originating trigger); every subsequent envelope, workflow input, task environment, log line, and graph write carries it, joined to `commitSha` and (post-build) `artifactDigest`. Propagation is library-enforced (the same conformance library that builds envelopes, ADR-027).
2. **Tracing.** OTel instrumentation (ADR-017 stack) via ADOT on Lambda and Fargate; Step Functions native tracing; X-Ray as the pilot backend. One trace = one flow: webhook → bus → workflow → tasks → gateway → graph write. Trace coverage of flows is itself a measured SLI (target in [07](07-verification-and-acceptance.md)).
3. **Flow-status record** (DynamoDB, TTL ~90 d), written at each stage transition:

```json
{
  "correlationId": "01J…",
  "trigger": "repo.push", "lane": "incremental",
  "app": "order-management", "repo": "orders-svc", "sha": "…",
  "stages": [
    {"stage": "received",   "at": "…"},
    {"stage": "classified", "at": "…", "verdict": "impact-possible"},
    {"stage": "extracted",  "at": "…", "artifact": "sha256:…"},
    {"stage": "published",  "at": "…", "edges": 41, "trust": "advisory"}
  ],
  "outcome": "succeeded | no-impact | failed | fail-open",
  "errorClass": null
}
```

   Powers `GET /v1/flows/{correlationId}/status` and the Admin "where is my run?" screen ([05](05-approval-ui-spec.md)). ~5–7 writes/flow ≈ `49,000 × 7 = 343k` DynamoDB writes/day — negligible on on-demand capacity.
4. **Dashboards and alarms** (CloudWatch): per-lane throughput and queue age; DLQ depth (alert > 100); fail-open rate (< 0.5 % of decisions/30 d); freshness SLIs (streaming evidence p95 ≤ 60 s, batch/registry ≤ 10 min); baseline-wave wall clock vs the 8 h window; incremental-vs-full divergence rate (the F-03 detector — alert on trend, not just threshold); classifier no-impact ratio (a sudden jump means a broken rule pack); Bedrock spend and cache hit rate; approval funnel (time-to-first-review, ack coverage).

## 6. Cost posture (shape, not budget)

Serverless pricing tracks the duty cycle: the dominant costs are Fargate task-hours (`≈ 700` per full baseline wave + `≈ 280`/day incremental, §1) and Bedrock inference (bounded by cache misses). Standing costs are small: DynamoDB on-demand, S3/Iceberg storage, CloudFront, Cognito, the Aurora core (owned by the graph-core budget). There is no idle worker fleet and no 24×7 broker fleet until an ADR-022 trigger fires — that is the financial expression of ADR-021/022. A monthly cost report per lane is part of the operator dashboard set.
