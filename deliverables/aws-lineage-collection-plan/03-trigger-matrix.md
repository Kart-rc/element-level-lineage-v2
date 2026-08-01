# 03 — Zero-Touch Trigger Matrix

| | |
|---|---|
| **Status** | Draft — for review (normative once approved) |
| **Role** | The closed set of ways lineage-collection work starts. Every row is an event; there is no other entry point. Workflows referenced here are specified in [04-collection-workflow-spec.md](04-collection-workflow-spec.md); the deployment-authority semantics come verbatim from [../platform-10-de-review/README.md](../platform-10-de-review/README.md) §6.1. |
| **Lanes** | A = custom application code (release-pipeline authoritative) · B = plan-based Spark/dbt/Airflow (execution authoritative) · C = opaque/no-repo (scheduled, advisory forever) — per the execution-model assessment's three-lane model (F-02). |

## 1. The matrix

| # | Trigger (event) | What fires | What runs | What it produces | Lane |
|---|---|---|---|---|---|
| 1 | **Business App registered** (`POST /v1/apps` or catalog sync) → `onboarding.registered` | BaselineCollection | Inventory pull (test-automation service, ADR-025) → member-repo resolution → Distributed Map fan-out per repo → app-level reconciliation with CloudWatch interaction evidence | Per-repo candidate artifacts; app-scoped graph at **Advisory** trust; coverage report (`automated` / `declared` / `uncovered` / `dormant` per system); seeded review queue | A+B+C |
| 2 | **Repo added to GitHub App installation** → `repo.onboarded` | BaselineCollection (single repo) | Immediate baseline extraction (F-05: publication is not merge-gated). If `throughline.yaml` is absent: open a scaffold PR (archetype detection informs it) and proceed without waiting | Candidate artifact; Advisory publication; scaffold PR when needed; coverage entry | A |
| 3 | **Repo-inventory sync delta** (`repo.inventory.delta`, scheduled + on-demand) | Scope reconciler | Diff active set vs collection scope; enqueue baselines for newly active repos; mark newly dormant repos | Scope changes; `dormant` coverage states (visible, never silently dropped) | A+B |
| 4 | **Push to default branch** → `repo.push` | IncrementalCollection | **Rule-based change classifier first** (changed paths ∩ manifest globs ∩ determinant sets; rule packs per file type): no-impact → fast exit with a recorded verdict. Impact possible → determinant-set-driven re-derivation (F-03), SCA first, LLM residue only on cache miss | New candidate artifact keyed `(repo, sha, toolchainHash)`; delta vs prior default-branch artifact; Advisory publication; flow-status record either way | A |
| 5 | **PR opened / synchronize** → `repo.pr.updated` | PRGate (priority lane) | Head-SHA candidate artifact → diff vs **environment baseline** (last successful deployment, never default-branch HEAD) → snapshot-pinned impact → OPA decision | `{added, changed, removed}` delta; status check + single updated PR comment; decision tuple `{snapshotId, policyVersion, confidenceModelVersion}`; p95 < 30 s, hard timeout 120 s → **fail-open + warn** | A |
| 6 | **PR rebased / force-pushed** | PRGate | Invalidate prior candidate by head SHA; recompute against new base | Superseded (not deleted) prior decision; replacement check | A |
| 7 | **Merge** → `repo.pr.merged` | Candidate recorder | Record merged candidate; **still not environment-authoritative** | Retained candidate awaiting deployment; trust-upgrade eligibility if the PR carried manifest/contract acceptance | A |
| 8 | **Deployment succeeded** (CD/ECR events) → `deploy.succeeded` | DeploymentPromotion | Resolve artifact digest → promote the **exact** artifact's lineage to authoritative for that environment; reconcile expected vs runtime. **If no lineage package exists for the digest (hotfix path): first-class alert, unskippable** (F-06) | New active version (previous queryable); updated `deployment-state`; alert on missing package | A |
| 9 | **Deployment failed / Rollback** → `deploy.failed` / `deploy.rolledback` | DeploymentPromotion | Failed: mark candidate failed, no promotion. Rollback: reactivate the prior deployed artifact/version | Bitemporal record of the event; no history deleted; drift re-evaluation on rollback | A |
| 10 | **Nightly schedule** (EventBridge Scheduler) | NightlyReconciliation | Full rescan (Fargate Spot wave) diffed against incremental state → **divergence rate = the F-03 bug detector**; Lane B OpenLineage/warehouse reconciliation; Lane C scheduled scanner sweep; repair missed webhooks | Drift findings (issue/alert, never silent overwrite); incremental-vs-full divergence metric; Lane B corroboration joins; Lane C advisory refresh | A+B+C |
| 11 | **CloudWatch interaction aggregation** (scheduled, ADR-025) | Interaction refresh | Glue/Athena aggregation over log evidence → `CloudWatchInteractionAggregate` observations through the ingest gateway | Interaction-edge confirmation + recency (never column lineage); confidence runtime term updates | A+B |
| 12 | **Schema-registry subject change** → `registry.changed` | Registry adapter | Re-derive affected edges; type-truth reconciliation (registry overrides all); tombstone on subject deletion | Schema-delta events; drift findings surfaced to owners | A+B |
| 13 | **Collector heartbeat loss** (Lane B listener / aggregation silence beyond the channel window) | Coverage lifecycle | Mark affected edges/regions `stale`; **do not infer absence** | `stale` coverage states; alert; gate degrades per policy (fail-open + warn) | B |
| 14 | **Waiver / attestation expiry approaching** (TTL sweep) | Steward notifier | Queue item + owner notification (waivers ≤ 90 d; declared contracts default TTL 180 d, decay to Inferred on expiry) | Steward-queue entries; decay events on true expiry | A+B+C |
| 15 | **Prompt/model version bump** (config merge) → `toolchain.updated` | Planned re-extraction wave | Nightly Bedrock batch wave through the content-addressed cache (F-04) — **never in the PR path** | Re-derived LLM-residue edges under new `(modelVersion, promptVersion)` keys; comparison report old-vs-new | A |
| 16 | **User approval decision finalized** (`proposal.finalized` from the UI) | Trust promotion | Apply per-edge decisions; promote Advisory → **Producer-attested**; write the immutable review record | Trust-band changes; review record; calibration-corpus events (proposal-vs-accepted diff) | A+B+C |

## 2. The invariant

**There is no row for manual invocation.** No CLI command, console button, or API endpoint exists whose purpose is "run collection now." The human-shaped inputs — registering an app (row 1), merging a manifest or toolchain config (rows 2, 15), deciding an approval (row 16) — are themselves events in the matrix. Operational **replay** ([08-scale-resilience-observability.md](08-scale-resilience-observability.md) §4) re-processes *past* envelopes from the archive; it cannot mint new work. Any future need that appears to require a manual trigger must instead be expressed as a new event row and reviewed as a change to this document.

## 3. Ordering, dedup, and spike notes

- Rows 4–7 for one repo serialize on `orderingKey = repo` (FIFO lane); cross-repo ordering is explicitly not guaranteed and nothing may depend on it (ADR-003 inheritance).
- Every trigger passes the receiver's dedup (row-source GUIDs; envelope `idempotencyKey` downstream), so at-least-once delivery converges.
- Spike behavior per lane (PR-gate > deploy > baseline/backfill) is specified in [08](08-scale-resilience-observability.md) §3; a deploy-train spike may delay row-10-class work by design, never row 5.
