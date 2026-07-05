# 01 — Gap Register

| | |
|---|---|
| **Status** | Final — for review board |
| **Role** | Canonical register and traceability root. Nothing in this package may claim to resolve a gap that is not listed here; every gap here carries exactly one disposition. |
| **Severity scale** | Critical = blocks implementability or will derail buy-in · High = will draw hard questions / material rework risk · Medium = credibility and polish |
| **Sources** | `v8 self-identified` = raised by v8's own Critical Review but still open after its Remediation Plan · `net-new` = found by this review |

Evidence citations refer to the v8 documents in `deliverables/latest_source/Data Lineage Impact Platform-8/`. v8's Critical Review has no formal gap IDs, so citations use file + section heading.

---

## S — v8 self-identified gaps still open after its Remediation Plan

v8 deserves credit for its own adversarial review: 20 issues, honestly graded. Its Remediation Plan genuinely closes the program-shaped ones (staffing reconciliation, PI value cadence, identity spike, adoption workstream). The five below were acknowledged and then punted — dispositioned "TRACKED → Roadmap" or "TRACKED → PRD 1" — and never landed anywhere in the v8 document set.

### GAP-S1 — Collector coverage stops at four collectors; no declarative escape hatch

**Severity:** Critical · **Source:** v8 self-identified
**v8 evidence:** Critical Review §02 — "Four collectors will not cover a real enterprise stack… Snowflake, dbt, Airflow, Flink, Kafka Streams, stored procedures, and legacy ETL are not addressed… the UI will imply confidence where there is none." Remediation Plan dispositions this "TRACKED → Roadmap"; the Roadmap never publishes the promised coverage map — it lists only the same four collectors plus "streaming," and buries the rest in an unitemized "adoption & connector long-tail ~180 eng-weeks" bucket.
**Why it matters:** At a 2,000-service estate, the four collectors (static+LLM, Spark, Dask, OTel) plausibly cover less than half the systems that move data. Every uncovered system is an invisible edge, and invisible edges make the flagship capability — the CI gate — silently wrong: a "no breaking impact" verdict that really means "no impact *we can see*." Coverage is not an onboarding detail; it is the correctness boundary of the product.
**Options:**
1. Build connectors in priority order and accept dark zones until built (v8's implicit position).
2. Tiered connector roadmap **plus a declarative lineage-contract mechanism** (`lineage.yaml` in repos, schema-validated, owner-attributed, TTL-reviewed) so any team can assert lineage for uncovered systems today, at capped confidence.
3. Adopt an existing catalog's connector estate (DataHub / OpenMetadata ingestion) as a collector fleet feeding the Throughline graph.
**Recommendation:** Option 2 as core design; evaluate option 3 as a Tier-2 accelerator (board flag). Coverage itself becomes a product surface: per-domain coverage %, and "uncovered" rendered as a first-class state everywhere.
**Disposition:** Resolved-by-design → ADR-012, ADR-013, HLD §4

### GAP-S2 — Cold-path policy and signal conflict-resolution matrix never landed

**Severity:** High · **Source:** v8 self-identified
**v8 evidence:** Critical Review §02 — "Cold/never-run paths stay Inferred forever — exactly the risky tail" (High) and "Conflict resolution between signals is underspecified… who wins?" (Medium). Both dispositioned "TRACKED → PRD 1"; PRD 1 v8 contains neither the cold-path policy nor a conflict matrix.
**Why it matters:** The two unwritten rules sit at the heart of the fusion engine. Without a conflict matrix, merge behavior is implementation-defined — two engineers will build two different graphs from the same events. Without a cold-path policy, the quarter-end job that fires four times a year lives permanently in the lowest trust band, which is precisely backwards: rare paths are where breaking changes hide.
**Options:** (1) Leave to implementation and tune later. (2) Specify a normative per-attribute precedence matrix (existence, transform, type, path, ownership resolved differently) plus an explicit cold-path rule, versioned in git.
**Recommendation:** Option 2. "Low confidence ≠ low risk" must be a written invariant: static-only edges always surface in impact results as Possible, and are never silently dropped.
**Disposition:** Resolved-by-design → ADR-007, HLD §4

### GAP-S3 — AI-uplift re-baseline of estimates promised, never shown

**Severity:** Medium · **Source:** v8 self-identified
**v8 evidence:** Critical Review §03 — "AI productivity uplift is baked into the estimates… if the uplift under-delivers, every date moves" (High), fix: "re-baseline without uplift, present AI assist as upside." Dispositioned "TRACKED → Roadmap"; the Roadmap presents a flat ~240 person-month total with no with/without-uplift split or sensitivity band.
**Why it matters:** An estimate whose core assumption is invisible cannot be interrogated. This compounds GAP-R1.
**Options:** (1) Re-baseline the LOE without uplift. (2) Record as a delivery-plan finding.
**Recommendation:** Option 1 when the program team reconciles the plan — but estimate remediation is excluded by this review's charter.
**Disposition:** Out-of-scope (charter) — recorded; cross-reference GAP-R1

### GAP-S4 — Exec/governance personas unserved; two-decimal confidence contradiction

**Severity:** Medium · **Source:** v8 self-identified
**v8 evidence:** Critical Review §01 — "Cognitive load: a power-user tool, not a leadership dashboard" (High) and "Confidence score reads as false precision… never two decimals" (High). Remediation §A8 defines role landings for only two personas (analyst, platform engineer) out of the four audiences the Critical Review names; and the v8 Architecture & Scale document itself still displays two-decimal confidence (0.94, 0.91, 0.72) throughout its schemas and API examples, contradicting its own review.
**Why it matters:** The contradiction is small but diagnostic: a fix the proposal agreed to did not propagate into its own reference architecture, which is what happens without a normative spec. The unserved exec/governance persona matters because those are the audiences that fund and govern the platform.
**Options:** (1) Full UI redesign for four personas. (2) Fix the data contract now — bands-only display rule, and coverage/risk roll-up APIs that give exec/governance consumers their entry point — and defer visual design to the product team.
**Recommendation:** Option 2. Display rule: integer score + band, never decimals, enforced in the API serialization layer, not left to UI discipline.
**Disposition:** Resolved-by-design (API + display rule) → ADR-008, HLD §8 · full persona UI design **Deferred** — trigger: first governance-user onboarding wave

### GAP-S5 — Unknown/empty/error UI states and accessibility undesigned

**Severity:** Medium · **Source:** v8 self-identified
**v8 evidence:** Critical Review §01 — "No empty/unknown/error states shown… Absence of an edge could mean safe, or blind" (Medium) and the accessibility item (Medium); both rated "NICE," no design produced anywhere in v8.
**Why it matters:** "No edge" versus "no coverage" is not a UI nicety — it is the difference between *safe* and *blind*, and the API must be able to express it before any UI can render it. An impact result that cannot say "this region of the graph is unobserved" will be read as "nothing is affected."
**Options:** (1) Defer wholly to UI hardening. (2) Specify the distinction at the API layer now (`no-dependency` / `not-observed` / `stale` / `retired` / `error` as distinct response states), defer visual/a11y treatment.
**Recommendation:** Option 2 — the API contract is architectural; pixel design is not.
**Disposition:** Resolved-by-design (API states) → ADR-009, HLD §8 · visual & accessibility design **Deferred** — trigger: GA readiness review

---

## A — Data model and semantics (net-new)

### GAP-A1 — No temporal/versioned graph or snapshot semantics

**Severity:** Critical · **Source:** net-new
**v8 evidence:** Architecture & Scale entity schema carries only `firstSeenAt` / `lastObservedAt`; edges carry `lastObservedAt`. The impact API returns `computedAt` and a `stale` flag but nothing pins a result to a graph state. Nothing anywhere in v8 lets a reader ask for "the graph as of Tuesday 14:02."
**Why it matters:** Concrete failure: the CI gate blocks a PR at 14:02; the developer appeals; by 14:40 the graph has absorbed 300 new runtime events and the same query now returns *pass*. The decision can be neither reproduced nor audited — fatal for a system whose whole purpose is to block merges, and indefensible in the incident review that follows the first contested block. Continuous upsert (v8 scaling tactic 2: "stream, never batch-rebuild") makes this *worse*: the graph mutates constantly under the reader.
**Options:**
1. Full event-sourcing with rebuild-on-query — perfectly reproducible, far too slow for a 30-second gate budget.
2. Physical snapshot copies per decision — reproducible, ruinous storage duplication.
3. Append-only bitemporal-lite: immutable edge/node versions with `(validFrom, validTo]`, "current graph" as a view, snapshots as **logical watermarks** (offset vector + max transaction time), every gate/impact decision pinning `{snapshotId, policyVersion, confidenceModelVersion}`.
**Recommendation:** Option 3 — reproducibility at the cost of one design constraint (append-only writes) rather than storage or latency.
**Disposition:** Resolved-by-design → ADR-004, HLD §2

### GAP-A2 — No formal identity spec: URN grammar, environment, schema-version, rename continuity

**Severity:** Critical · **Source:** net-new (extends v8's own identity-resolution finding)
**v8 evidence:** URNs appear only as examples (`col:orders_raw.total_amount`, `svc:orders-svc`) with no grammar, no reserved-character rules, no namespace registry. The entity model has **no environment dimension** — a staging table and its prod twin collide on the same identifier. Schema versions are absent from identity. PRD 1 names identity resolution "on the critical path" and the Remediation Plan funds a spike — but a spike can only *measure* resolution against a spec, and there is no spec to measure against.
**Why it matters:** Identity is the load-bearing wall: every signal joins the graph through it. Without a deterministic grammar, each collector invents its own naming and the "merge & reconcile" engine becomes a heuristic soup. Without an environment axis, staging runs corroborate prod edges (false Verified). Without rename continuity, every refactor orphans history and resets confidence to zero.
**Options:** (1) Adopt DataHub URNs (proven, but verbose nested-paren syntax and imports DataHub semantics). (2) Adopt raw OpenLineage naming (standard, but no environment axis and no column fragment). (3) Own grammar — compact, environment-first, deterministic — with a documented bidirectional mapping to OpenLineage naming for interop.
**Recommendation:** Option 3, plus separation of *name* from *identity*: URNs are deterministic names; a stable `entityId` (ULID) with `sameAs` alias records carries history across renames.
**Disposition:** Resolved-by-design → ADR-005, ADR-006, HLD §1

### GAP-A3 — No tombstone/retirement lifecycle

**Severity:** High · **Source:** net-new
**v8 evidence:** PRD 1 FR-C9 offers only "stale-edge decay lowers confidence for edges not re-observed" (P2). No deletion events, no retirement state, no purge. A deleted pipeline and a quiet pipeline are indistinguishable — both just fade.
**Why it matters:** Impact analysis over a graph that cannot say "this consumer was decommissioned" reports blast radii that include ghosts, and — worse — "was connected until 2026-03-01" is exactly the information an incident review needs and decay destroys. Confidence decay conflates two orthogonal facts: *how sure are we* and *does it still exist*.
**Options:** (1) Decay only (v8). (2) Explicit lifecycle — `active → stale → retired` — with tombstones triggered by deletion events (OpenLineage lifecycle facets, CI file deletion, registry subject deletion, owner attestation), retired entities excluded from impact but queryable for 13 months.
**Recommendation:** Option 2. Lifecycle state is a fact; confidence is an assessment; the model must carry both.
**Disposition:** Resolved-by-design → ADR-009, HLD §2

### GAP-A4 — No cycle handling or hub caps in the impact traversal

**Severity:** High · **Source:** net-new
**v8 evidence:** PRD 2 specifies "downstream traversal — BFS over outbound lineage edges" with unbounded depth and no cycle mention. The Architecture bottleneck table acknowledges hub fan-out ("a shared key can dominate cost") but only as a mitigation note; nothing reaches the PRD's traversal semantics or the API contract.
**Why it matters:** Real column graphs cycle (feedback pipelines, reverse-ETL writing back to operational stores — reverse-ETL is explicitly in v8's own topology model). A naive BFS on a cyclic graph does not terminate. And hub columns (`customer_id`) will blow any latency budget and produce unreadable ten-thousand-node blast radii unless caps and truncation are part of the *contract*, not an afterthought.
**Options:** (1) Leave to implementation. (2) Contract-level traversal spec: visited-set cycle handling, SCC pre-collapse for roll-ups, per-query node/edge-visit budgets, truncation as an explicit response flag with cursor continuation — never a silent cut.
**Recommendation:** Option 2.
**Disposition:** Resolved-by-design → ADR-010, HLD §5

### GAP-A5 — No roll-up aggregation semantics for confidence and severity

**Severity:** Medium · **Source:** net-new
**v8 evidence:** PRD 1: "Column-level edges roll up to dataset and app edges for higher altitudes" — with no rule for how N child confidences and severities become one parent value. PRD 3 renders rolled-up edges with counts.
**Why it matters:** The obvious implementation — averaging — is wrong in both directions: averaging a Verified edge with an Inferred edge manufactures a "Probable" that no signal ever asserted, and averaging severities lets one Breaking drown in twenty Safes. Executives read the rolled-up view; getting this wrong misinforms exactly the audience with the least ability to drill down and notice.
**Options:** (1) Implementation-defined. (2) Normative rules: severity rolls up as **max of children**; confidence rolls up as a **coverage-weighted band distribution** ("62% verified · 30% probable · 8% inferred"), displayed as a distribution, never blended into one number.
**Recommendation:** Option 2.
**Disposition:** Resolved-by-design → ADR-010, HLD §5

---

## B — Collection and maintenance (net-new)

### GAP-B1 — Ingestion contract lacks idempotency, ordering, late events, replay, backfill, and dead-lettering

**Severity:** Critical · **Source:** net-new
**v8 evidence:** Architecture scaling tactic 6 asserts "async, idempotent collectors… back-pressure via event bus" but no contract exists: no idempotency key, no ordering rule, no late-event semantics, no DLQ, no replay design. Backfill appears once, as the phrase "historical backfill" in PRD 1's Phase 2.
**Why it matters:** These are the mechanics that decide whether the graph converges to truth or accumulates noise. Without an idempotency key, every collector retry double-counts an observation and inflates confidence. Without per-entity ordering and a late-event rule, a delayed Tuesday event overwrites Thursday state. Without replay, every scorer bug becomes unfixable history.
**Options:** (1) Leave to implementation. (2) Normative contract: idempotency key `(source, runId, eventId)`; per-entity ordering via partition key; late events merged by `observedAt` (never arrival time); malformed events to DLQ with a triage SLI; replay/backfill = reprocess a raw-store time range into a shadow graph build, then atomic snapshot swap.
**Recommendation:** Option 2 — and the raw store must be a queryable table format (Iceberg), not loose JSON, or replay at year-two volumes is impractical.
**Disposition:** Resolved-by-design → ADR-003, HLD §3

### GAP-B2 — Schema-registry integration asserted, never designed

**Severity:** High · **Source:** net-new
**v8 evidence:** The Column entity lists "schema registry" as a source; FR-C8 references "registry subject+version"; the Worked Example leans on Avro subjects. No sync mechanism, no conflict rule between registry-declared and runtime-observed types, no non-stream story (warehouse schemas, API schemas).
**Why it matters:** The registry is the only *authoritative* type source in the entire signal set — everything else is inference. The severity matrix (type widen/narrow/nullability) is only as good as the type information beneath it; leaving type truth to LLM inference undermines the gate's core judgment. Registry-vs-runtime drift is itself a valuable finding the design should surface, not average away.
**Options:** (1) Types from static/LLM inference only. (2) Registry sync jobs as first-class collectors: Confluent SR for streams, warehouse `INFORMATION_SCHEMA` snapshots, repo-sourced OpenAPI/protobuf for services; registry wins type conflicts; schema versions land in the version registry axis of the identity model.
**Recommendation:** Option 2.
**Disposition:** Resolved-by-design → ADR-014, HLD §3

### GAP-B3 — LLM extraction has no eval harness, cost model, or determinism handling

**Severity:** High · **Source:** net-new (extends v8's own LLM finding)
**v8 evidence:** Critical Review §02 flags "LLM extraction: accuracy, cost, drift, and non-determinism… validation rate and spend unquantified" (High). The Remediation Plan's numeric precision/recall gates apply **only to identity resolution**, not edge extraction. FR-C2 relies on "self-reported confidence" — the model grading its own homework.
**Why it matters:** LLM-derived edges are the largest single input to the baseline graph and the least trustworthy. Without a labeled golden set there is no way to know whether LLM precision is 95% or 60%; without pinned versions, a silent model upgrade re-shapes the graph overnight; without content-hash caching, cost scales with codebase size instead of change rate.
**Options:** (1) Trust self-reported confidence and calibrate someday. (2) Golden-set eval harness (≥500 labeled file→edge examples) with hard gates — below-target precision hard-caps LLM-only edges at Inferred; temperature 0, pinned model versions, golden-set re-run gating any upgrade; content-hash caching; explicit cost model.
**Recommendation:** Option 2.
**Disposition:** Resolved-by-design → ADR-015, HLD §4

### GAP-B4 — No static-analysis feasibility inventory per language/dialect

**Severity:** Medium · **Source:** net-new
**v8 evidence:** FR-C1: "static analyzer parses repo code, SQL, orchestration DAGs" — no parser named, no per-language feasibility assessment. The Onboarding Estimator prices "SCA+LLM" identically for a 5-line service and a legacy monolith (modulated only by a coarse ×1.0–1.45 code-health factor).
**Why it matters:** "Parse the code" hides a 10× spread in difficulty: SQL column lineage is a solved problem; PySpark DataFrame chains are partially tractable; arbitrary Java service code is a research project. Without an inventory, the roadmap cannot sequence collectors by tractability and the estimator's baselines are fiction.
**Options:** (1) Discover feasibility during build. (2) Publish a feasibility inventory now — per source type: feasible-static / LLM-assisted / declared-only — and name the parser stack.
**Recommendation:** Option 2, with sqlglot as the SQL backbone and an explicit v1 exclusion of deep app-code dataflow analysis.
**Disposition:** Resolved-by-design → ADR-013, HLD §4

---

## C — Impact analysis and CI/CD experience (net-new)

### GAP-C1 — The gate is schema-diff-only; logic-only changes never trigger impact

**Severity:** High · **Source:** net-new
**v8 evidence:** PRD 2's entire severity model is a schema-change-type matrix (widen, narrow, rename, drop, add, nullability); FR-I5 triggers the gate on "PR schema deltas." A PR that rewrites `net_amount = gross - tax` to `net_amount = gross - tax - fees` — same name, same type, different meaning — produces no schema delta and sails through the very gate built to catch breaking changes.
**Why it matters:** Semantic breakage is the harder and more common failure class; a "breaking-change gate" that only sees shape, not meaning, will let through incidents and then take the reputational hit for them.
**Options:** (1) Accept schema-only scope, documented. (2) v1: exploit the path-qualified edges v8 already has — every edge carries `codeRef`; map PR-changed files/functions to edges via codeRef and emit warn-tier "transform logic changed" impact for touched edges even with no schema delta. (3) v2: semantic SQL AST diff (sqlglot) to classify transform changes.
**Recommendation:** Option 2 now (it is nearly free — the data is already on the edge), option 3 as the v2 trigger-documented upgrade.
**Disposition:** Resolved-by-design (v1 codeRef mechanism; semantic diff Deferred to v2 — trigger: first quarter of gate operation) → ADR-011, HLD §6

### GAP-C2 — No waiver/override/suppression workflow

**Severity:** Critical · **Source:** net-new (v8 names the need, designs nothing)
**v8 evidence:** Critical Review §04 prescribes "easy audited override" and a "published false-positive budget"; Remediation §A4 repeats both as levers. No workflow, schema, permission model, expiry, or audit design exists anywhere in v8.
**Why it matters:** v8's own review states the failure mode: "a few wrong blocks and engineers route around the gate." The waiver workflow *is* the trust mechanism — who may override, with what justification, visible to whom, expiring when. An override that is a Slack message to an admin becomes either a rubber stamp (gate meaningless) or a bottleneck (gate ripped out). This is the single most operationally consequential unwritten design in v8.
**Options:** (1) Manual overrides via platform admins. (2) First-class waiver objects: `{gateDecisionId, scope, reason, approver, expiry ≤90d, auditRef}`, approver must be the downstream owner or domain steward, all waivers queryable, waiver-rate-per-rule as a published SLI feeding an automatic circuit-breaker (rule exceeding FP budget auto-demotes block→warn).
**Recommendation:** Option 2 — the circuit-breaker converts v8's "FP budget" from a slide-word into a mechanism.
**Disposition:** Resolved-by-design → ADR-011, HLD §6

### GAP-C3 — No policy framework: block vs warn by domain/criticality is an open question

**Severity:** High · **Source:** net-new (v8 lists it as an open question)
**v8 evidence:** PRD 2 open question — "Gate enforcement policy (block vs warn: by criticality tier, domain, or consumer SLA — needs a policy framework)." No framework follows. The observe→warn→block ramp in Remediation §A4 describes *stages* but not *who decides, where policy lives, or how it changes*.
**Why it matters:** Enforcement policy is where platform meets organization. Hard-coded policy means every domain exception is a code change; ad-hoc policy means nobody can answer "why did this block?" A gate whose rules cannot be inspected and diffed will not survive its first escalation.
**Options:** (1) Hard-coded thresholds with config flags. (2) Policy-as-code: OPA/Rego packages per domain, owned by domain stewards via pull request, versioned, with decision logs; ramp stage (observe/warn/block) is a policy input per domain.
**Recommendation:** Option 2 — boring, auditable, and the PR-based change flow gives stewards ownership without platform-team gatekeeping.
**Disposition:** Resolved-by-design → ADR-011, HLD §6

### GAP-C4 — No gate latency SLO or failure posture

**Severity:** High · **Source:** net-new
**v8 evidence:** PRD 2's latency metric: "within a single review/pipeline cycle" — no number. The Architecture flow says "sub-second p50" for the impact *query*, which is not the gate's end-to-end webhook→status-check path. Nothing anywhere states what happens when the platform is down while a developer waits on a required status check.
**Why it matters:** Two unwritten numbers decide the gate's survival. A gate that adds minutes to every PR gets ripped out by the first frustrated staff engineer. And the failure posture is existential: if Throughline's outage blocks all merges org-wide, the platform dies in its first bad week.
**Options:** (1) Best-effort latency, fail-closed (safe-looking, org-hostile). (2) Hard budget — p95 < 30s webhook→status-check, 120s timeout — and **fail-open with a warn annotation** on platform error, with Tier-0 domains able to opt into fail-closed.
**Recommendation:** Option 2. A lineage gate's authority must be earned by availability, not imposed by default-deny.
**Disposition:** Resolved-by-design → ADR-011, HLD §11

### GAP-C5 — No monorepo/multi-repo PR→service mapping

**Severity:** Medium · **Source:** net-new
**v8 evidence:** FR-C7 says the CI hook "regenerates lineage for changed code per PR"; every example assumes one repo = one service. Nothing maps a PR's changed paths to the services/datasets whose lineage should be re-derived — untenable in a monorepo and ambiguous even in polyrepo estates with shared libraries.
**Why it matters:** Wrong mapping in a monorepo means either re-analyzing the world on every PR (gate latency explodes) or missing the affected service entirely (gate silently skips).
**Options:** (1) Heuristic mapping from build files. (2) Explicit `throughline.yaml` manifest per repo/subtree declaring path→service-URN ownership, validated in CI.
**Recommendation:** Option 2 — one small file makes the mapping deterministic, reviewable, and self-serve.
**Disposition:** Resolved-by-design → ADR-011, HLD §6

---

## D — Platform and non-functional requirements (net-new)

### GAP-D1 — No named technology decisions

**Severity:** Critical · **Source:** net-new
**v8 evidence:** The graph store is "graph DB + partitions" in every diagram — no product. No parser, no policy engine, no search engine, no LLM serving choice, no orchestration platform. Across ~15 documents the only concrete technology commitments are OpenLineage, Kafka, and S3.
**Why it matters:** "Graph DB" vs "relational + projection" is not a detail — it changes the temporal model, the operational burden, the hiring profile, and the cost envelope. An architecture that defers every technology choice has not actually made its trade-offs; it has deferred them to whoever writes the first line of code.
**Options:** (1) Keep technology-agnostic and decide per-component during build. (2) Decide now with named recommendations, criteria, and alternatives, revisit-triggers attached.
**Recommendation:** Option 2 (charter requirement). Headline decision: PostgreSQL 16 as system of record with an in-process traversal projection — no graph database in v1 (the 10k-ceiling graph is ~4 GB; see ADR-001).
**Disposition:** Resolved-by-design → ADR-001, ADR-002, ADR-003, ADR-013, ADR-014, ADR-019; stack table in 02 §3

### GAP-D2 — No deployment topology, environments, HA/DR, or retention design

**Severity:** High · **Source:** net-new
**v8 evidence:** Architecture & Scale has no deployment section; storage sizing is labeled "pre-replication"; there is no dev/staging/prod story for the platform itself, no availability target, no RPO/RTO, no retention/GDPR treatment.
**Why it matters:** A platform that gates merges is production infrastructure from day one of block-mode; "we'll figure out HA later" is not compatible with sitting in the merge path. The environments question is doubly subtle here because the *platform's* environments are orthogonal to the *estate* environments the graph models — an unstated distinction that will confuse every new engineer.
**Options:** (1) Defer to the infra team. (2) Specify: Kubernetes, single region multi-AZ, managed PostgreSQL HA, DR by rebuild-from-log (raw events RPO≈0 on S3; graph is derived and rebuildable ≤8h), 13-month raw retention with Iceberg row-level deletes for purge.
**Recommendation:** Option 2.
**Disposition:** Resolved-by-design → ADR-018, HLD §12

### GAP-D3 — No security, authorization, or tenancy model — for a graph that maps PII flows

**Severity:** Critical · **Source:** net-new
**v8 evidence:** PII classification is a first-class column attribute in PRD 1; PRD 3 offers PII as a search facet. Yet no document defines authentication, authorization, roles, audit, or who may see what. (The June-2026 platform-design plan lists "SSO, scoped RBAC, audit" as bullet aspirations; v8 carries none of it into design.)
**Why it matters:** The lineage graph is itself a sensitive asset: it is literally a map of where PII flows, which systems touch payments data, and where the soft spots are — reconnaissance gold. A platform that renders "every PII flow in the company" behind a single shared login is a compliance finding waiting to be written.
**Options:** (1) Perimeter auth only, defer authz. (2) OIDC SSO; RBAC v1 (viewer / domain-steward / platform-admin / service-account); domain-scoped visibility in v1.5; **metadata-only enforced at ingest** (collection schemas structurally reject data values); audit events on gate decisions, waivers, identity merges, and reads of PII-tagged lineage.
**Recommendation:** Option 2. "We only store metadata" must be enforced by schema, not asserted in a slide.
**Disposition:** Resolved-by-design → ADR-016, HLD §9

### GAP-D4 — No platform self-observability or coverage SLIs

**Severity:** High · **Source:** net-new
**v8 evidence:** `GET /v1/collectors/health` exists with a single `coverage.runtimeBacked` example value. No SLI definitions, no freshness/lag measures, no alerting design, no answer to "is the lineage pipeline itself healthy?"
**Why it matters:** A trust product must be able to prove its own trustworthiness. If ingestion silently lags three days, every confidence score is quietly wrong and the gate is making decisions on stale truth — and nobody knows. Meta-observability is not ops hygiene here; it is part of the product's epistemics.
**Options:** (1) Standard infra dashboards. (2) A designed SLI family — ingestion lag, DLQ depth, collector heartbeats, coverage %, identity sampled precision, gate latency/fail-open/waiver rates, calibration drift — with targets, doubling as the platform's quantified success metrics.
**Recommendation:** Option 2.
**Disposition:** Resolved-by-design → ADR-017, HLD §11

### GAP-D5 — Scale math omits OTel volume and API-payload fields

**Severity:** High · **Source:** net-new
**v8 evidence:** Architecture & Scale counts only OpenLineage job events (~480K/day at 10k services) and prices ingest at ~1.9 GB/day. OTel — one of the four signals — contributes zero events in the model. (The repo's own June-2026 blueprint plan warned "raw OTel spans may dominate capacity"; v8's math dropped the warning.) Node counts include dataset columns but not API payload fields, though endpoint lineage is in scope.
**Why it matters:** Raw span volume at 2,000 instrumented services is measured in billions/day — three to four orders of magnitude above everything else in the pipeline. Whether OTel is aggregated at the collector or shipped raw is *the* capacity decision for the collection plane, and v8's sizing silently assumes it away.
**Options:** (1) Ship spans, filter centrally. (2) Aggregate at the collector edge: spans reduce to per-edge observation flushes (hot edges flush every 5 min, warm hourly, cold on-fire), bounding OTel-derived load to `active edges × flushes/day` — independent of request rate.
**Recommendation:** Option 2; the corrected capacity model (HLD §10) shows OTel observations still dominate OpenLineage events ~5× even after aggregation, which is exactly why the correction matters.
**Disposition:** Resolved-by-design → HLD §10

### GAP-D6 — No p99/QPS/availability targets; no cost model

**Severity:** Medium · **Source:** net-new
**v8 evidence:** The only latency number in v8 is "sub-second p50" on the impact flow. No p99 anywhere (hub-node traversals live in the tail), no QPS model, no availability target, no infra or LLM cost estimate — despite the Critical Review flagging LLM spend as unquantified.
**Why it matters:** p50 targets are how systems pass review and then fail in production; the gate and the hub-column blast radius are tail-latency problems by construction. And a platform asking for multi-year funding should be able to state its own run cost to one significant figure.
**Options:** (1) Set SLOs after launch from observed data. (2) Propose the full NFR/SLO table now (p50/p99, availability, freshness, gate budget) at the 2k design point, with a load-test plan targeting worst-case hubs, plus an LLM + infra cost model.
**Recommendation:** Option 2 — targets can be renegotiated later; designing without them cannot.
**Disposition:** Resolved-by-design → HLD §10, §11

---

## E — Operating model (net-new)

### GAP-E1 — Day-2 ownership of rules, thresholds, collectors, and contracts unspecified

**Severity:** High · **Source:** net-new
**v8 evidence:** PRD 2 open question: "Severity rule ownership (global vs per-domain… overridable)." Nothing anywhere assigns ownership of identity rules, the severity matrix, confidence thresholds, gate policies, connector maintenance, or lineage contracts after launch.
**Why it matters:** Every one of these artifacts *will* need changing in week one of real operation. If the platform team owns them all, it becomes the bottleneck for every domain exception; if nobody owns them, they rot. The severity matrix and gate policy are organizational contracts as much as technical ones.
**Options:** (1) Platform team owns everything initially, delegate later. (2) A day-2 ownership table now: each rule set lives in git with a named owning role and change mechanism (identity rules → platform team; severity matrix → architecture guild; gate policies → domain stewards via PR; confidence thresholds → quarterly calibration review; lineage contracts → asset owners with TTL re-attestation).
**Recommendation:** Option 2 — policy-as-code (GAP-C3) makes delegation safe from day one.
**Disposition:** Resolved-by-design → HLD §12

### GAP-E2 — Success metrics are all directional; none quantified

**Severity:** Medium · **Source:** net-new
**v8 evidence:** Every metric in PRDs 1–3 is directional ("growing share," "majority," "low false-positive," "within one cycle"). Remediation §A10's six "leading indicators with targets" have targets like "Majority" and "High" — labels, not numbers.
**Why it matters:** Unquantified metrics cannot fail, which means they cannot inform. The funding gates (v8's own staged-funding design) need pass/fail evidence.
**Options:** (1) Set numbers after the vertical slice. (2) Bind the SLI family (GAP-D4) with concrete targets now: e.g., ≥80% of Tier-1 assets with ≥1 signal within two quarters; sampled Verified precision ≥95%; waiver rate <10% per rule; gate p95 <30s.
**Recommendation:** Option 2 — the slice may recalibrate the numbers, but the *instrument* must exist before the slice runs.
**Disposition:** Resolved-by-design → ADR-017, HLD §11

---

## R — Delivery plan (recorded; remediation out of charter)

### GAP-R1 — Five unreconciled effort envelopes and an 18-vs-24-month timeline conflict

**Severity:** High · **Source:** net-new (extends v8's own estimate-consistency finding)
**v8 evidence** (per-document, all within the v8 set and its companion plans):

| Document | Effort figure | Timeline frame |
|---|---|---|
| Roadmap & LOE | ~240 person-months (≈ its own `capPm=240` constant) | **18 months**, 2→3 teams ("all 15 use cases live… 19-month target") |
| Critical Review | cites build estimate "~145–205 eng-weeks" | judges "the **24-month** plan" |
| Remediation Plan §A2 | ~780 net eng-weeks (10 eng × 104 wk − 25%) | **24 months** (PI 1–16, weeks 1–104) |
| Executive Narrative | "≈605–780 eng-weeks" | **24 months**, four phases |
| Implementation-blueprint plan (repo `docs/plans/`) | P0 MVP 110–175; full scope 325–535 eng-weeks | 12–39 months by staffing scenario |

The Remediation Plan — written specifically to answer "estimate vs. staffing looks inconsistent" — reconciles a 24-month plan while the Roadmap it ships beside presents an 18-month one. The "when is gating live" answer ranges from month 8 (Remediation PI 6) to month 9–12 (Roadmap) to month 18–24 (org-wide, Remediation PI 14–16) depending on which document is read. Note also: 780 eng-weeks ≈ 180 person-months, which is *less* than the Roadmap's 240 person-months — the two "totals" do not even order consistently.
**Why it matters:** v8's own Critical Review predicted that "a sharp CFO will ask why 10× the estimated effort is staffed"; the current document set would fail that meeting on internal consistency alone, taking the (sound) architecture down with it.
**Recommendation (recorded for the program team):** designate one authoritative envelope and timeline; restate every other document against it; publish the with/without-AI-uplift sensitivity (GAP-S3) in the same pass.
**Disposition:** Out-of-scope (charter) — recorded with evidence; owner: program/delivery team

---

## Appendix — Crosswalk to v8's Critical Review (20 items)

v8's Critical Review enumerates 20 issues (7 Critical, 7 High, 6 Medium) without IDs; numbering below follows its section order.

| # | v8 Critical Review item (severity) | Status in v8 after Remediation Plan | This package |
|---|---|---|---|
| 1 | §01 Cognitive load: power-user tool, not leadership dashboard (High) | Partially closed (§A8: two personas only) | GAP-S4 |
| 2 | §01 Browse-first landing at 10k assets (Critical) | Closed-in-v8 (§A8 search-first) — verified | Retained; UI states via GAP-S5 |
| 3 | §01 Confidence reads as false precision (High) | Agreed, not propagated (Architecture still shows 0.94) | GAP-S4 → ADR-008 |
| 4 | §01 No empty/unknown/error states (Medium) | Open (rated NICE) | GAP-S5 |
| 5 | §01 Accessibility (Medium) | Open (rated NICE) | GAP-S5 (deferred, trigger stated) |
| 6 | §02 Identity resolution hand-waved (Critical) | Closed-in-v8 (§A5 spike, GO ≥95%/≥90%) — verified; but spike lacks a spec to measure against | GAP-A2 supplies the spec → ADR-005/006 |
| 7 | §02 Four collectors won't cover the estate (Critical) | **Open** ("TRACKED → Roadmap"; map never published) | GAP-S1 → ADR-012 |
| 8 | §02 Cold paths stay Inferred forever (High) | **Open** ("TRACKED → PRD 1"; never landed) | GAP-S2 → ADR-007 |
| 9 | §02 LLM accuracy/cost/drift unquantified (High) | Open (no edge-extraction gates) | GAP-B3 → ADR-015 |
| 10 | §02 Signal conflict resolution underspecified (Medium) | **Open** ("TRACKED → PRD 1"; never landed) | GAP-S2 → ADR-007 |
| 11 | §02 Hot-node traversal fan-out (Medium) | Mitigation noted, no contract | GAP-A4 → ADR-010 |
| 12 | §03 Estimate vs staffing inconsistent (Critical) | Reconciled in §A2 — but against a different timeline than the Roadmap's | GAP-R1 (recorded) |
| 13 | §03 24 months to value, no early win (Critical) | Closed-in-v8 (PI cadence, 90-day win) — verified | Retained |
| 14 | §03 One fragile serial spine (High) | Closed-in-v8 (spike gate + fallback) — verified | Retained; ADR-006 keeps the gate |
| 15 | §03 AI uplift baked into estimates (High) | **Open** (re-baseline never shown) | GAP-S3 (out-of-scope, recorded) |
| 16 | §03 Success measured qualitatively (Medium) | Partially closed (§A10 targets are labels) | GAP-E2 → ADR-017 |
| 17 | §04 Build-vs-buy not pre-empted (Critical) | Closed-in-v8 ("integrate-don't-replace") — verified | Retained; ADR-012 buy-note re-opens it narrowly for connectors |
| 18 | §04 Adoption is an org-change program (Critical) | Closed-in-v8 (§A4 workstream + sponsor) — verified | Retained |
| 19 | §04 Gate false positives erode trust (High) | Ramp defined; override/budget mechanics missing | GAP-C2 → ADR-011 |
| 20 | §04 Vertical-slice representativeness criteria (Medium) | Fix stated, criteria still unpublished | Accepted-risk — owner: program team; criteria template in HLD §12 note |

**Register totals:** 28 gaps — 26 Resolved-by-design and 2 Out-of-scope (GAP-S3, GAP-R1). Three of the resolved gaps carry explicitly deferred sub-parts with named re-opening triggers (GAP-S4 persona UI, GAP-S5 visual/a11y, GAP-C1 semantic diff). One additional non-register item (crosswalk #20, vertical-slice representativeness criteria) is carried as Accepted-risk owned by the program team.
