# 06 — Delivery Roadmap: AWS Build-Out on the Phase 0–5 Gates

| | |
|---|---|
| **Status** | Draft — for review |
| **Role** | Maps the AWS build ([02](02-aws-architecture.md)) onto the existing six-month Phase 0–5 roadmap and exit gates in [../platform-10-de-review/README.md](../platform-10-de-review/README.md) §5. The gates are not restated — each phase below lists its AWS deliverables and names the existing gate it must pass. Team split (A: Collection & Trust, B: CI/CD & Pilot Operations) and the "collection plus evergreen change loop" reframing are inherited unchanged. |

## Phase 0 — Weeks 1–4: contracts, landing zone, and go/no-go foundations

**AWS deliverables**
- Landing zone: accounts, VPC-less serverless baseline, CDK skeleton with the plane-boundary module split (ADR-021); quota inventory + initial raise requests ([08](08-scale-resilience-observability.md) §2).
- GitHub App (org install on the pilot slice) + webhook receiver + dedup table + `throughline-collection` bus + Firehose envelope archive (components 1, 12).
- Business App registry (DynamoDB + `POST /v1/apps`) seeded with the vertical-slice app; test-automation inventory adapter's first sync (ADR-025).
- Canonical-schema registry v1: envelope + payload JSON Schemas + assertion-constraint table published (ADR-027); ingest-gateway validator skeleton; manifest schema includes the `kind:` classification field (ADR-029).
- Aurora DDL from HLD §2; URN library; identity ground-truth labeling for the slice.

**Gate (unchanged):** Phase 0 exit — identity spike ≥ 95 % precision / ≥ 90 % recall on labeled slice entities; 100 % in-scope systems classified with owner and collection posture; duplicate/out-of-order/rename/rollback contract tests exist; security threat model and metadata-only boundary approved. **PIVOT/STOP branches apply as written.**

## Phase 1 — Weeks 5–8: deterministic baseline and lineage artifacts

**AWS deliverables**
- BaselineCollection Step Function with Distributed Map fan-out (backfill lane); repo-classification step with detection rules v1 and per-class routing (ADR-029, [04](04-collection-workflow-spec.md) §8); Fargate extractor image (tree-sitter + sqlglot + manifest resolver; the scout-agent scripts adapted to the extractor contract in [04](04-collection-workflow-spec.md) §4).
- Artifact registry live (S3 + Iceberg + DynamoDB pointers, component 4); determinant sets recorded per edge (F-03).
- Advisory publication end-to-end: extraction → canonical envelopes → gateway → graph facts; zero-touch proof — registering the slice app triggers baseline with no human action (trigger rows 1–2).
- First approval-UI increment: review inbox + edge review (screens 2 and 4), Cognito/OIDC wiring, endpoints 23–25.
- Nightly full-rescan scheduler live; incremental-vs-full divergence metric published from day one.
- Bedrock Tier-3 behind the shared content-addressed cache (F-04), golden-set gated.

**Gate (unchanged):** Phase 1 exit — identical artifact hash on re-run; incremental and full scans converge for the same head SHA; deterministic parser accuracy measured; LLM-only edges ≥ 90 % precision / ≥ 70 % recall **or remain suggestion-only**; no source/secret leakage.

## Phase 2 — Weeks 9–12: runtime ingestion, reconciliation, and coverage truth

**AWS deliverables**
- CloudWatch interaction pipeline (subscription filters → Firehose → S3/Iceberg → Glue/Athena aggregation → gateway) for the slice app (ADR-025).
- **Sidecar runtime collection (ADR-028):** sidecar image + conformance library; feature-flag wiring (AppConfig) asserted by the test-automation service; `test.run.completed` ingestion (trigger row 17); digest-level execution-confirmed facets flowing to the graph. This realizes the Phase-2 milestone "pilot the governed structured OTel lineage record on two or three high-impact paths" in sidecar form, with the same contract gates.
- Lane B ingestion: Spark OpenLineage and/or one warehouse-native source for the slice; Airflow/dbt topology if used.
- Full reconciliation path: identity resolution, per-attribute precedence, conflict recording, DLQ/replay, coverage SLIs by asset/edge/granularity/signal/environment.
- Steward queue v1 (identity merges) + coverage dashboard (screens 5 and 1).

**Gate (unchanged):** Phase 2 exit — replay converges; duplicates change no state; runtime evidence cannot corroborate the wrong environment (now tested against sidecar evidence explicitly); column-facet coverage measured per operation; freshness p95 ≤ 60 s stream / ≤ 10 min batch; unresolved entities, conflicts, DLQ age, stale collectors visible and alertable.

## Phase 3 — Weeks 13–16: evergreen CI/CD loop

**AWS deliverables**
- IncrementalCollection with the rule-based change classifier (rule packs v1) and determinant-driven selective re-derivation ([04](04-collection-workflow-spec.md) §2).
- PRGate in **observe mode** on the pr-gate lane: environment-baseline resolver (component 5), versioned diff engine, snapshot-pinned impact (Lambda + CTE pilot form), OPA/WASM decisions, Checks renderer with stable annotation IDs (components 6–9); warm-path work if p95 demands it.
- Deployment authority wired: CD/ECR adapter, promotion Lambda, `deployment-state`, rollback reactivation, **F-06 hotfix alert live** (component 10, trigger rows 8–9).
- Delta review screen (screen 3) with before/after side-by-side, linked from the PR comment; flow-status records + `GET /v1/flows/{id}/status` (ADR-026).

**Gate (unchanged):** Phase 3 exit — CI check p95 < 30 s incremental / hard timeout 120 s fail-open with auditable decision; same inputs reproduce the same decision; failed deployments never alter authoritative lineage; rollback restores prior version without deleting history; test matrix covers stale base, rebase, force-push, concurrent PRs, merge queue, monorepo subtree mapping.

## Phase 4 — Weeks 17–20: impact calibration and warn-mode adoption

**AWS deliverables**
- Warn mode on the pilot repos; waiver store + approval flow in the UI (HLD §6.5 semantics; circuit-breaker board on screen 7).
- Trust promotion live end-to-end: finalize → immutable review record (Aurora + Object Lock hash chain) → Advisory → Producer-attested (trigger row 16); calibration-corpus events accumulating with per-edge `acknowledged` flags.
- Confidence calibration against the corpus + sidecar/runtime corroboration outcomes; severity rules versioned; gate-quality dashboards (latency, fail-open, FP/FN from adjudicated samples, waiver rate, coverage at decision time).

**Gate (unchanged):** Phase 4 exit — Verified-band observed precision ≥ 95 %; Probable ≥ 80 %; breaking-classification precision ≥ 98 % before any block experiment; no "no impact" verdict under truncation/unknown coverage/stale collector; waivers carry actor, reason, scope, expiry, immutable audit.

## Phase 5 — Weeks 21–26: production pilot, scale rehearsal, and block-readiness

**AWS deliverables**
- The full loop in production for the slice app: PR → merge → deploy promotion → runtime reconciliation → nightly drift → approval funnel, continuously, zero-touch.
- **10k-repo scale rehearsal:** synthetic fleet (generated repos + replayed event traffic) driving a full baseline wave and a spike day at the [08](08-scale-resilience-observability.md) §1 planning values; measure wave wall-clock vs the 8 h window, lane isolation under spike (PR p95 held while backfill sheds), quota headroom, cost per wave.
- Resilience exercises: replay, store failover, queue backlog, collector loss, deployment rollback (the de-review's exercise list) plus Spot-interruption storms.
- **ADR-022 MSK checkpoint:** evaluate the three named triggers against measured volumes; decide stay/migrate with evidence.
- Runbooks, on-call alerts, collector onboarding docs, DR exercise.

**Gate (unchanged):** the Month-6 exit criteria table in [../platform-10-de-review/README.md](../platform-10-de-review/README.md) §5 applies verbatim, **plus** the scale-acceptance additions defined in [07-verification-and-acceptance.md](07-verification-and-acceptance.md) §3. Block mode only after ≥ 4 stable warn-mode weeks and all gates pass.

## What the vertical slice proves

By month 6, for one Business Application, the pilot demonstrates the full sponsor ask:

1. **Zero-touch, end-to-end:** the app was registered once (row 1); everything since — baseline, every push, every PR, every deploy, every night — ran from events. No manual invoke exists to point at.
2. **Two processes, correctly scoped:** baseline ran app-scoped with inventory + CloudWatch context; incremental ran repo-scoped with the classifier fast path; the nightly divergence metric stayed within target, proving the fast path sound in practice.
3. **The approval loop closes:** at least one full cycle of delta → per-edge review with before/after capture → immutable record → Advisory → Producer-attested promotion, with the calibration corpus visibly accumulating.
4. **Runtime evidence without production cost:** sidecar corroboration inside the change loop (ADR-028), CloudWatch interaction evidence at baseline, Lane B execution evidence on schedule — and the static-only confidence cap (64) observably lifting where corroboration landed.
5. **Scale credibility:** the rehearsal numbers — not projections — say what a 10,000-repo estate costs and how long a wave takes.

## Funding-gate alignment

The existing funding-gate cadence (week 4 / 8 / 12 / 16 / 20 / month 6 — "do not expand because the calendar says so") applies to this build unchanged; each phase's gate above is the evidence for its corresponding funding decision.
