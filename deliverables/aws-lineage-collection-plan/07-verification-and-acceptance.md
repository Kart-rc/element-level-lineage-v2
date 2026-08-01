# 07 — Verification and Acceptance

| | |
|---|---|
| **Status** | Draft — for review |
| **Role** | The acceptance criteria for the AWS lineage-collection service, the SLO subset it is measured against, the scale-acceptance additions, and the traceability appendix proving this package covers everything it claims to cover. |

## 1. Pilot acceptance criteria

The pilot acceptance table in [../lineage-collection-assessment.md](../lineage-collection-assessment.md) §"Pilot acceptance criteria" applies **verbatim** (identity ≥ 95 % precision / ≥ 90 % recall with zero cross-environment auto-merges; reproducible artifacts and replayable decisions; convergent ingestion; explicit unsupported constructs; measured coverage; freshness; CI budgets; deployment authority; no false "no impact"; exercised operations). This package adds the following rows:

| Area | Required evidence |
|---|---|
| Zero-touch | From app registration to published baseline with **zero human actions**; audit shows every collection flow originated from a [trigger-matrix](03-trigger-matrix.md) row; no manual invoke path exists in the deployed IaC (checked by policy scan of API routes and console-visible entry points) |
| Repo classification | Every in-scope repo carries a class; `documentation`/`tooling` pushes cost zero extraction compute; library releases recorded and consumer re-derivation observed on a dependency bump; an infrastructure repo contributes entity declarations and no transform edges; every exclusion visible as `excluded:<class>` in coverage; a steward reclassification re-enters the repo through baseline |
| Two-process split | Baseline runs app-scoped (membership from catalog ∩ active inventory); incremental runs repo-scoped; classifier fast-path verdicts recorded with evidence; **nightly incremental-vs-full divergence rate within agreed target and trending flat** (the F-03 detector) |
| Canonical schema | 100 % of ingested events validate against the registry `(schemaVersion, signal)`; assertion-violation DLQ empty in steady state; a deliberate violation test per signal is rejected with the correct reason |
| Approval loop | ≥ 1 full cycle delta → per-edge decisions → finalize → immutable record (hash chain verifies) → trust promotion; before/after captured on every correction; material edges show explicit acknowledgement; bulk-accept of material edges is impossible by construction |
| Sidecar evidence (ADR-028) | Sidecar evidence arrives only from test environments (a prod-tagged event raises the misconfiguration alarm); digest-level facets appear on deployed artifacts; **no test-environment evidence produces prod Verified** |
| Flow visibility | Every sampled flow answerable via `GET /v1/flows/{correlationId}/status`; trace coverage of flows ≥ 99 %; "where is my run?" resolves in one lookup |

## 2. SLO conformance subset (from HLD §11, unchanged targets)

| SLI | Target |
|---|---|
| CI gate end-to-end (webhook → status check) | p95 < 30 s · hard timeout 120 s → fail-open + warn |
| Ingestion freshness (`observedAt` → queryable) | p95 < 60 s stream · < 10 min batch/registry |
| UI scoped fetch | p95 < 500 ms |
| Fail-open rate | < 0.5 % of decisions / 30 d |
| Waiver rate per rule | < 10 % / 30 d (circuit breaker) |
| DLQ | alert > 100 · drain < 24 h |
| Identity resolution precision (sampled) | ≥ 95 % |
| Verified-band observed precision | ≥ 95 % (Probable ≥ 80 %) |

## 3. Scale acceptance (the ADR-026 additions, measured in the Phase 5 rehearsal)

| Criterion | Target |
|---|---|
| Baseline wave, 10k-repo synthetic fleet | Completes < 8 h at the planned concurrency; stragglers/retries inside the window; per-repo failures land as `error` coverage states, never wave aborts |
| Spike day (release-train profile per [08](08-scale-resilience-observability.md) §1) | pr-gate lane p95 holds < 30 s throughout; backfill sheds first and resumes from checkpoint; no quota alarm fires unrequested |
| Replay | A 24 h archive window replays to identical graph state (hash-compared projections) |
| Cost | Measured cost per baseline wave and per 1k incremental flows published; no standing idle-fleet cost line |

## 4. Traceability appendix

### 4.1 De-review §6.2 pipeline components → this package

All 12 components map to [02-aws-architecture.md](02-aws-architecture.md) §2 rows 1–12, 1:1 by number. (Mechanically checkable: the table carries the de-review numbering.)

### 4.2 Execution-model findings → resolving sections

| Finding | Resolved where |
|---|---|
| F-01 self-validation loop | Drift language + Lane B reconciliation as the external oracle — [04](04-collection-workflow-spec.md) §4 (nightly), ADR-025/028 corroboration framing |
| F-02 three-lane model | Lane column on every [trigger row](03-trigger-matrix.md); Lane B/C sweeps in NightlyReconciliation |
| F-03 determinant-set invalidation | [04](04-collection-workflow-spec.md) §7 contract; classifier soundness §2; divergence metric §4 + [08](08-scale-resilience-observability.md) §5 |
| F-04 content-addressed shared LLM cache; only deterministic edges fail builds | [02](02-aws-architecture.md) §3 (Bedrock row); [04](04-collection-workflow-spec.md) §3; ADR-021/027 |
| F-05 publication decoupled from merge | ADR-023/024; trigger rows 1–2; trust ladder in [05](05-approval-ui-spec.md) §2 |
| F-06 hotfix digest binding + per-edge acknowledgement | Trigger row 8 alert; ADR-024; delta `materiality` in [04](04-collection-workflow-spec.md) §6 |

### 4.3 New ADRs → existing decisions they scope or build on

| New | Relationship |
|---|---|
| ADR-020 | Builds on ADR-011.5 (manifest), resolves GAP-C5's app-level remainder |
| ADR-021 | Scopes ADR-018 (collection plane only; core unchanged) |
| ADR-022 | Scopes ADR-002 (backbone deferral with named triggers; topic map preserved) |
| ADR-023 | Realizes de-review component 1; applies F-05 |
| ADR-024 | Realizes HLD §6.5 waivers + IMP-009/011/012; applies ADR-006 |
| ADR-025 | Extends the assessment's signal responsibility matrix (two new evidence sources) |
| ADR-026 | Applies ADR-017 observability posture to the collection plane |
| ADR-027 | Executable form of the responsibility matrix + envelope; aligns with ADR-007 conflict preservation |
| ADR-028 | Deployment vehicle for the assessment's `RuntimeLineageObservation` contract; preserves the cross-environment rule |
| ADR-029 | Applies ADR-011.5 declaration-over-guessing and the coverage-truth invariant to repo scope itself |

### 4.4 Coverage checklists (audited before each release of this package)

- **12/12** pipeline components mapped ([02](02-aws-architecture.md) §2).
- **17/17** trigger rows present, each with lane tag; the no-manual-invoke closing statement intact ([03](03-trigger-matrix.md) §2).
- **7/7** consumer-contract states rendered ([05](05-approval-ui-spec.md) §4).
- **7/7** signals in the assertion-constraint table ([04](04-collection-workflow-spec.md) §5.2).
- Sponsor-revision checklist: two-process split ✓ (04 §1–2) · test-automation + CloudWatch context sources ✓ (ADR-025) · rule-based fast path ✓ (04 §2) · before/after capture ✓ (ADR-024, 05 §7) · 10k-repo scale + spikes + E2E visibility ✓ (ADR-026, 08) · consistent schema across SCA/LLM/runtime with stated pushback ✓ (ADR-027) · feature-flagged sidecar runtime in integration tests, off in prod ✓ (ADR-028) · infrastructure/library/documentation repo handling in both flows ✓ (ADR-029, 04 §8).

## 5. Verifying this document set itself

Before merge: every relative link resolves; every quoted number matches its source file exactly (weights 30/18/30/26/22, cap 64, bands 85/65, waiver ≤ 90 d, circuit breaker 10 %/30 d, gate p95 < 30 s / timeout 120 s, identity ≥ 95 %/≥ 90 %, LLM residual ≥ 90 %/≥ 70 %, freshness 60 s/10 min, breaking precision ≥ 98 %); all Mermaid diagrams render; README status table matches the v8 package format; no normative text is duplicated from the HLD or the assessment — referenced only.
