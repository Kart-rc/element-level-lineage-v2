# 03 — Architecture Decision Records

| | |
|---|---|
| **Status** | Final — for review board |
| **Role** | The 19 decisions that turn v8 into an implementable architecture. ADRs decide and justify; normative specifications live in [04-high-level-design.md](04-high-level-design.md) and are referenced, not duplicated. |
| **Statuses** | `Decided` = implement unless the board objects · `Default — board confirmation requested` = defensible default, explicit confirmation wanted |

Bias declared up front: proven, boring, operable technology; the smallest number of stateful systems; every choice carries a revisit trigger so "boring for v1" never hardens into "wrong forever."

---

## ADR-001: Graph storage

**Status:** Decided · **Resolves:** GAP-D1 (headline decision)

**Context.** v8 says "graph DB + partitions" and never names a product. The workload: a graph of ~212k nodes / ~600k edges at the 2k design point and ~1.06M nodes / ~3M edges at the 10k ceiling (formulas in HLD §10); heavy point-reads and scoped neighborhoods; bounded BFS traversals; bitemporal versioning (ADR-004); joins to waivers, policies, schema versions, audit; strong consistency for gate decisions.

**Decision.** **PostgreSQL 16 is the system of record.** All nodes, edges, observations, versions, snapshots, and operational tables live in one relational schema (DDL in HLD §2). Traversal is served by an **in-process CSR (compressed sparse row) projection** — a compact adjacency structure built from PostgreSQL change-data-capture, held in memory by the impact-engine replicas, rebuilt from scratch in minutes and patched incrementally from CDC deltas. No graph database ships in v1.

**Why.** The graph is small. At the 10k ceiling it is ~4 GB pre-index (1.06M nodes × 1.5 KB + 3M edges × 0.8 KB); the projection form is smaller still (adjacency + a few attributes per edge ≈ low hundreds of MB). It fits in the RAM of one modest node with an order of magnitude to spare. What is genuinely hard in this system — bitemporal versioning, snapshot pinning, joins across operational tables, transactional writes, backup/restore, hiring — is exactly what a 30-year-old relational database is best at and what graph databases are weakest at. The only thing a graph database would win — multi-hop traversal — is served faster by an in-memory projection than by any out-of-process graph engine, because a bounded BFS over CSR arrays is a cache-friendly loop, not a network round-trip per hop.

**Alternatives considered.**
- **Neo4j** — mature, Cypher is pleasant, and it is the default answer to "lineage graph." Rejected: adds a second stateful system with its own HA/backup/upgrade story; bitemporal modeling is DIY; enterprise clustering is a licensing conversation; and at 4 GB the scale that justifies it never arrives.
- **JanusGraph / Amazon Neptune** — distributed graph stores for graphs that don't fit on one machine. This graph fits on one machine ~250× over. Rejected as category error.
- **Dual-store (PostgreSQL SoR + graph DB serving layer)** — the "best of both" option that actually buys the consistency problems of both. The CSR projection *is* the serving layer, minus the second database.
- **Recursive CTEs in PostgreSQL for traversal** — retained as the cold-start and ad-hoc fallback path; too slow at p99 for depth-10 hub traversals under the gate budget (measured plans in HLD §5).

**Consequences.** One database to operate, back up, and reason about. Impact-engine replicas carry state (the projection) and need a warm-up path (HLD §5). SQL, not Cypher, is the query surface — fine, since traversal is code, not ad-hoc queries.
**Managed option:** RDS/Aurora PostgreSQL.
**Revisit trigger:** graph exceeds ~50M edges, or scoped-traversal p99 breaches budget with the projection in place.

---

## ADR-002: Event backbone

**Status:** Decided · **Resolves:** GAP-D1 (component)

**Context.** All collectors emit events; the ingestion pipeline needs buffering, back-pressure, replayable consumption, and per-entity ordering. v8 already assumes Kafka in its backbone sketch.

**Decision.** **Apache Kafka**, partitioned by `hash(canonical entity URN)` so all events touching an entity arrive in order at one consumer. Topic map, partition counts, and retention in HLD §3.

**Why.** It is the assumed choice in v8, the org-standard streaming substrate in most estates of this shape, and every property the ingestion contract (ADR-003) needs — ordered partitions, consumer offsets as replay cursors, back-pressure by lag — is native.

**Alternatives considered.** **Redpanda** — Kafka-API-compatible, lighter operationally; an acceptable drop-in if the org prefers it (no design change). **Pulsar** — capable, but no requirement here that Kafka lacks, and it adds an unfamiliar operational surface. Rejected.
**Managed option:** AWS MSK or Confluent Cloud.
**Revisit trigger:** none expected; this decision is deliberately unexciting.

---

## ADR-003: Raw event store and ingestion contract

**Status:** Decided · **Resolves:** GAP-B1

**Context.** v8 asserts "async, idempotent collectors" without a contract, and mentions backfill in one phrase. Whether the graph converges to truth under retries, delays, and bugs is decided here.

**Decision.** Every accepted event lands **append-only in S3 as Parquet, managed as Apache Iceberg tables** (partitioned by event-date and source), *before* graph processing. The normative ingestion contract (full rules in HLD §3):

1. **Idempotency:** key = `(source, runId, eventId)`; duplicates within the dedupe window are acknowledged and dropped. A collector retry can never double-count an observation.
2. **Ordering:** per-entity ordering via the Kafka partition key (ADR-002); cross-entity ordering is explicitly not guaranteed and nothing may depend on it.
3. **Late events:** merged by `observedAt` (event time), never by arrival time. A late Tuesday event never overwrites Thursday state; it back-fills the observation history.
4. **Malformed events:** rejected to a DLQ topic with a triage queue; DLQ depth is an alerting SLI (ADR-017).
5. **Replay / backfill:** reprocess an Iceberg time range through the (possibly fixed) pipeline into a **shadow graph build**, verify, then atomically swap via the snapshot mechanism (ADR-004). Scorer bugs are repairable history, not permanent scars.

**Why Iceberg, not loose JSON on S3:** schema evolution for event formats, efficient time-range scans for replay (the whole point of keeping raw events), and row-level deletes for retention/GDPR purges (ADR-016) — none of which a JSON prefix soup provides.

**Alternatives considered.** Raw JSON on S3 (v8's implicit answer) — rejected per above. **Delta Lake** — equivalent capability; Iceberg chosen for engine neutrality. **Keep raw events only in Kafka with long retention** — retention economics and ad-hoc scan ergonomics both worse.
**Managed option:** S3 + AWS Glue catalog.
**Revisit trigger:** none; append-only raw history is foundational.

---

## ADR-004: Temporal model

**Status:** Decided · **Resolves:** GAP-A1

**Context.** v8's graph mutates continuously under its readers ("stream, never batch-rebuild") and carries only `firstSeenAt`/`lastObservedAt`. A CI gate decision made at 14:02 cannot be reproduced at 14:40. For a system whose product is *blocking merges*, non-reproducibility is disqualifying.

**Decision.** **Append-only bitemporal-lite.** Node versions and edges are immutable facts carrying `(validFrom, validTo]` transaction time; updates close the old version and open a new one; the "current graph" is a view over open versions. A **snapshot is a logical watermark** — a Kafka offset vector plus max transaction time — minted cheaply (one row) at any moment; `AS OF snapshot` queries filter versions by the watermark. Every impact report and every gate decision **pins and stores `{snapshotId, policyVersion, confidenceModelVersion}`** and is therefore exactly reproducible and appealable forever (within retention).

Retention: full version history 13 months, then compaction to monthly snapshots (the raw event log in Iceberg remains the deep archive).

**Alternatives considered.** **Full event-sourcing with rebuild-on-query** — perfectly reproducible and hopeless against a 30-second gate budget. **Physical snapshot copies per decision** — at ~600k edges × dozens of gate runs per day, pure waste; append-only tables make logical snapshots free. **No temporal model, log decisions with their result payloads only** — makes the *decision* auditable but not *re-derivable*; an appeal cannot ask "what would it say now, and why the difference?"

**Consequences.** All writers must be append-only (the merge engine closes/opens versions, never UPDATEs facts). Storage grows with change rate, not graph size — bounded and cheap at this scale (HLD §10). Every read API takes an optional `snapshotId`.
**Revisit trigger:** version-history storage exceeding 5× the live graph — would prompt tighter compaction, not a model change.

---

## ADR-005: Canonical URN grammar

**Status:** Decided · **Resolves:** GAP-A2 (with ADR-006)

**Context.** v8 uses URNs in examples only (`col:orders_raw.total_amount`) — no grammar, no environment axis, no rename story. Identity is the join key for every signal; without a deterministic spec, "merge & reconcile" has nothing to merge on. v8's own remediation funds an identity *spike* but gives it no spec to measure against.

**Decision.** The canonical name grammar (normative ABNF, encoding rules, and eight worked examples in HLD §1):

```text
urn:tl:{env}:{type}:{authority}:{path}[#{fragment}]

env       ∈ registered vocabulary: prod | staging | dev | ...(estate environments)
type      ∈ org | domain | app | svc | ds | job | col | ep | topic | field
authority = system-of-record namespace: snowflake.acme1 | kafka.main | gh.acme/orders | k8s.main
path      = /-separated hierarchical name within the authority
fragment  = element within the parent: #total_amount | #GET:/v1/orders
```

Examples: `urn:tl:prod:col:snowflake.acme1:analytics/orders_raw#total_amount` · `urn:tl:prod:svc:k8s.main:payments/orders-svc`.

Three deliberate properties:

1. **Deterministic:** any collector can compute an entity's URN from local knowledge (system + name + environment) with zero lookups. Determinism is what makes cross-signal joins possible at all.
2. **Schema version is *not* in the URN.** It is a separate axis `(urn, schemaVersion)` in the version registry (ADR-014). Identity survives schema evolution; versions attach to it.
3. **Name ≠ identity.** Every entity carries a stable `entityId` (ULID). URNs are names that *resolve to* an entityId; renames create a new URN, the resolver links it (ADR-006), the old URN becomes a `sameAs` alias, and history — including confidence — survives the refactor.

Interop: a documented bidirectional mapping to OpenLineage naming conventions (HLD §1), since OpenLineage remains the ingest wire format.

**Alternatives considered.** **DataHub URNs** (`urn:li:dataset:(urn:li:dataPlatform:...,name,env)`) — proven at scale, but verbose, nested-paren parsing is unpleasant in every language, and adopting the grammar quietly imports DataHub's entity semantics. **Raw OpenLineage naming** — the right *wire* convention, but it has no environment axis and no sub-dataset fragment, which are exactly the two axes v8 is missing. Mapping to it beats adopting it.
**Revisit trigger:** adoption of a company-wide asset-naming standard — the grammar's `authority` segment is designed to absorb one.

---

## ADR-006: Identity resolution

**Status:** Decided · **Resolves:** GAP-A2 (with ADR-005)

**Context.** The same physical table arrives as `snowflake://acme1/ANALYTICS/ORDERS_RAW` from the Spark collector, `analytics.orders_raw` from dbt, and `SELECT ... FROM orders_raw` from static SQL. v8 names this the hardest problem and funds a spike (GO gate: ≥95% precision / ≥90% recall — retained here as the acceptance bar). What the spike lacks is the resolution *algorithm* to evaluate.

**Decision.** A **deterministic rule chain, with humans confirming anything the rules cannot decide — and no probabilistic auto-merge, ever:**

1. **Exact URN match** (after each collector applies the ADR-005 construction rules).
2. **Registered alias** lookup (`sameAs` records from prior confirmations and rename events).
3. **Normalization rules** — per-source canonicalization: case folding per dialect, quoting removal, default-schema/database expansion, connection-alias mapping. Versioned in git, owned by the platform team (HLD §12), testable as pure functions.
4. **Candidate suggestion** — anything unresolved gets similarity-scored candidates (name distance + LLM assist) queued for **steward confirmation**. Confirmed → new alias record (the system learns). Unconfirmed → the entity stands alone, visibly `unresolved`, and appears in the coverage SLIs.

Measured continuously, not just in the spike: sampled resolution precision is a standing SLI (ADR-017).

**Why no probabilistic auto-merge:** a wrong automatic merge silently splices two assets' lineage together and poisons every downstream impact answer — the single failure mode this product can least afford, and the hardest to detect once made. Fragmented identities (the failure mode of being too conservative) are visible and repairable; wrong merges are invisible and compounding.

**Alternatives considered.** **Probabilistic entity resolution (e.g. Splink)** — right tool for fuzzy customer records; wrong risk profile here, rejected for v1 (revisit only as a *suggester*, never an auto-merger). **Central asset registry that all teams must pre-register against** — deterministic but organizationally utopian as a prerequisite; the alias mechanism gets the same result incrementally.
**Consequences.** A steward-facing confirmation queue is a v1 product surface, not an afterthought. Resolution throughput depends on normalization-rule quality; the spike measures exactly that.
**Revisit trigger:** confirmation-queue depth persistently exceeding steward capacity — would prompt better suggesters, not auto-merge.

---

## ADR-007: Signal precedence and conflict resolution

**Status:** Decided · **Resolves:** GAP-S2

**Context.** Five signals (static, LLM, Spark, Dask, OTel) plus — new in this package — `declared` (lineage contracts, ADR-012) will disagree daily. v8 acknowledged "who wins?" as unanswered and punted it to a PRD revision that never happened. There is no single global answer because the right winner differs *per attribute*: runtime is authoritative about what happened; static is authoritative about what the code says; the registry is authoritative about types.

**Decision.** A **normative per-attribute precedence matrix** (full table with all cells and tie-breakers in HLD §4). The load-bearing rows:

| Attribute | Precedence | On conflict |
|---|---|---|
| Edge existence | runtime (spark/dask/otel) > declared > static > llm | Runtime-observed but static-absent → edge exists, flagged `unexplained` (parser-coverage triage). Static-asserted but never observed → **cold-path edge: stays visible**, surfaces in impact as Possible. Never silently dropped. |
| Transform semantics | static > llm > OL facets | Disagreement → static wins, edge flagged `conflict`, fixed confidence penalty, triage event emitted |
| Type / schema | schema registry > runtime-observed > static > llm | Registry always wins; registry-vs-runtime drift is itself surfaced to owners as a finding |
| Path guard / frequency | runtime only | Latest observation wins; static supplies the path superset |
| Ownership | declared > CODEOWNERS > inferred | Never LLM-only |

Two rules with teeth:

- **Cold-path rule (the "low confidence ≠ low risk" invariant):** a static-only edge — the quarter-end job, the error branch — is permanently visible and always included in impact output as Possible. Confidence describes trust in *existence*, and is never used to hide asserted-but-unobserved risk.
- **Declared-edge discipline:** `declared` edges cap at Probable (75) unless runtime-confirmed, and carry a mandatory review TTL (default 180 days). Expired attestation decays the edge to Inferred. Contracts rot; the model must price that in.

Inter-runtime disagreement (Spark and OTel disagree about the same hop): union the observations, flag `conflict`, fixed penalty, triage — the pipeline never guesses which runtime lied.

**Alternatives considered.** **Single global signal ranking** — simpler and wrong; it forces one of "runtime beats static about transforms" (false) or "static beats runtime about existence" (false). Per-attribute precedence is exactly the finding v8 punted. **Weighted vote across signals per attribute** — reintroduces false precision and makes conflicts invisible; flags + triage keep humans in the loop where signals genuinely disagree.
**Revisit trigger:** conflict-triage volume showing a systematically wrong precedence row — the matrix is a versioned artifact (HLD §12) and single rows can change under review.

---

## ADR-008: Confidence model

**Status:** Decided · **Resolves:** GAP-S4 (display + calibration); supports GAP-E2

**Context.** v8's scoring — per-signal weights (static 30, LLM 18, Spark 30, Dask 26, OTel 22), recency multipliers (×1.0 <1d, ×0.82 <7d, ×0 never), baseline-only cap at 64, bands Verified ≥85 / Probable 65–84 / Inferred <65 — is a reasonable prior with two defects its own Critical Review names: two-decimal display implies false precision, and the weights are uncalibrated guesses with no feedback loop.

**Decision.** Keep the v8 additive model **as the v1 prior**, and fix the epistemics around it:

1. **Bands are the product; the number is a debugging detail.** APIs serialize `{score: 87, band: "verified"}` — integer only, enforced in the serialization layer, never client discipline. UI leads with the band.
2. **Quarterly calibration loop:** sample N edges per band, steward-verify ground truth, compute *observed precision per band*, and adjust **band thresholds** (not weights) until observed precision meets target: Verified ≥95%, Probable ≥80%. Procedure in HLD §4.
3. **The model is versioned.** `confidenceModelVersion` is pinned in every snapshot and gate decision (ADR-004); a calibration change never silently re-grades history.
4. Structural rules stay: baseline-only cap (LLM/static alone can never reach Verified), and only Verified/Probable edges participate in blocking decisions (per v8's own FR-I6, retained).

**Alternatives considered.** **Bayesian noisy-OR over per-signal reliability estimates** — statistically superior and data-hungry; deferred to v2 with a concrete trigger: two completed calibration cycles (the calibration loop is precisely what produces the reliability data the Bayesian model needs). **Ship v8 weights and tune ad hoc** — no instrument, no learning; rejected.
**Consequences.** A steward-hours cost per quarter (bounded: N ≈ 100–200 samples); in exchange, "Verified" becomes a claim with a measured error rate — which is the entire trust proposition of the product.
**Revisit trigger:** two calibration cycles complete → evaluate the Bayesian upgrade.

---

## ADR-009: Entity lifecycle and tombstones

**Status:** Decided · **Resolves:** GAP-A3; supports GAP-S5

**Context.** In v8, a deleted pipeline and a quiet pipeline look identical — both decay. Impact analysis reports ghosts; incident reviews lose "was connected until March 1st"; and the UI cannot render "retired" because the model cannot say it.

**Decision.** Explicit lifecycle on nodes and edges: **`active → stale → retired`**.

- **active:** observed within the channel-class window — stream 7d, batch 35d (covering monthly jobs); static-only entities are exempt from staleness (they assert code shape, not runtime liveness).
- **stale:** window exceeded. Distinct from low confidence: staleness is a fact about observation, confidence is an assessment of truth.
- **retired:** explicit tombstone, triggered by any of: OpenLineage lifecycle/deletion events, CI-diff file deletion, schema-registry subject deletion, or owner attestation via API. Retired entities are **excluded from impact traversal**, remain queryable for 13 months ("was connected until X"), then purge.

State machine, transition table, and per-channel windows in HLD §2.

**Alternatives considered.** **Pure recency decay** (v8) — conflates "gone" with "quiet"; rejected as a correctness bug in impact analysis. **Hard delete on tombstone** — destroys the historical record precisely when it is most valuable (post-incident).
**Revisit trigger:** channel-class windows are config, not architecture; tune freely.

---

## ADR-010: Impact traversal

**Status:** Decided · **Resolves:** GAP-A4, GAP-A5

**Context.** v8 specifies "downstream BFS" with unbounded depth, no cycle handling, no fan-out control, and no aggregation rule for roll-ups. Real column graphs cycle (reverse-ETL is in v8's own topology); hub columns like `customer_id` fan out to thousands; and executives read the rolled-up view.

**Decision.** Traversal runs against the in-memory CSR projection (ADR-001), **always pinned to a snapshot** (ADR-004), under a contract:

1. **Cycle-safe:** visited-set per query; strongly-connected components pre-collapsed in the projection for roll-up metrics.
2. **Budgeted:** per-query defaults 5,000 nodes / 50,000 edge-visits / depth 10 (max 25). Exhaustion returns partial results with an explicit `truncated: true` and a continuation cursor — **truncation is always visible, never silent** (the same invariant as the cold-path rule: the system may be incomplete, but never quietly).
3. **Path-tiered:** a downstream node's tier derives from the best path to it — Confirmed requires an all-Verified/Probable path; any Inferred hop demotes the path to Possible. Severity does **not** attenuate with hops: a break six hops away is still a break (v8's Worked Example agrees — the money-type change ripples six hops).
4. **Roll-up semantics (normative):** severity aggregates as **max of children** — one Breaking makes the parent Breaking. Confidence aggregates as a **coverage-weighted band distribution** ("62% verified · 30% probable · 8% inferred"), displayed as a distribution and never blended into a single average — averaging Verified with Inferred manufactures a Probable that no signal asserted.
5. **Hot-asset precompute:** blast radii for the top-N hub columns are materialized on projection delta and served from cache; ad-hoc queries pay traversal cost.

**Alternatives considered.** **Graph-DB traversal** — see ADR-001. **Recursive CTEs** — retained as fallback; fails p99 budget on hubs. **Severity attenuation by distance** — tempting for readability, dangerous for truth; readability is handled by tiering and truncation UX instead.
**Revisit trigger:** budget defaults are policy config; the contract (visible truncation, snapshot pinning) is not revisitable.

---

## ADR-011: CI gate

**Status:** Decided (Tier-0 fail-closed opt-in flagged for board) · **Resolves:** GAP-C1, GAP-C2, GAP-C3, GAP-C4, GAP-C5

**Context.** The gate is the product's sharpest edge and its biggest political liability. v8 designs the happy path (status check, block on confirmed-breaking) and leaves unwritten everything that decides survival: policy ownership, overrides, latency, failure posture, logic-only changes, and repo mapping. v8's own review states the stakes: "a few wrong blocks and engineers route around the gate."

**Decision.** Five sub-decisions, specified in HLD §6:

1. **Policy is code: OPA/Rego.** Per-domain policy packages in git, owned by domain stewards, changed by pull request, versioned (`policyVersion` pinned per decision, ADR-004), with OPA decision logs retained. The observe→warn→block ramp stage is a policy input per domain — v8's adoption ramp becomes enforceable configuration instead of a slide.
2. **Waivers are first-class objects:** `{gateDecisionId, scope, reason, approver, expiry ≤ 90d, auditRef}` — approver must be the impacted downstream owner or the domain steward; all waivers queryable; RBAC-controlled (ADR-016). **The false-positive budget is a circuit-breaker, not a slogan:** a policy rule whose waiver rate exceeds 10% over 30 days auto-demotes from block to warn and pages the rule's owner. Trust erosion becomes a measured, self-correcting quantity.
3. **Latency and failure posture:** p95 < 30 seconds webhook→status-check (budget breakdown in HLD §6), hard timeout 120s. On timeout or platform error the gate **fails open with a warn annotation** — a lineage tool that blocks all merges when *it* is down dies in its first bad week. Tier-0 domains (payments-grade) may opt into fail-closed by policy. *(Board confirmation requested on the opt-in.)*
4. **Logic-only change detection (v1):** v8's path-qualified edges already carry `codeRef`. The diff service maps PR-changed files/functions to edges via codeRef; a PR touching an edge's transform code with **no schema delta** emits a warn-tier "transform logic changed" impact to downstream owners. Cheap, honest, and closes the blind spot where the severity matrix sees nothing. v2 (trigger: first quarter of gate operation): semantic SQL AST diff via sqlglot to classify the change.
5. **Repo mapping is declared, not guessed:** each repo (or monorepo subtree) carries a `throughline.yaml` manifest mapping paths → service URNs (spec in HLD §6), validated in CI. Deterministic, reviewable, self-serve.

**Alternatives considered.** **Bespoke policy DSL / config flags** — every domain exception becomes a platform ticket; rejected. **Fail-closed by default** — maximal apparent safety, guaranteed organizational rejection; rejected except as Tier-0 opt-in. **Hard-block from day one** — v8's own observe→warn→block ramp is correct; the gate must earn authority through measured precision. **Heuristic repo mapping from build files** — silently wrong in monorepos; rejected for one small explicit file.
**Consequences.** OPA is a new (stateless, well-understood) runtime dependency. Stewards own policy — which is the point (GAP-E1).
**Revisit trigger:** FP-budget threshold and latency budget are policy config; the fail-open default is revisitable only by the board.

---

## ADR-012: Collection coverage

**Status:** Decided — buy-note flagged for board · **Resolves:** GAP-S1

**Context.** v8's four collectors leave Snowflake-native SQL, dbt, Airflow, Flink, Kafka Streams, stored procedures, and legacy ETL dark — and dark zones make the gate silently wrong (a "no impact" verdict that means "no *visible* impact"). v8's own review called this Critical; the remediation never landed.

**Decision.** Three moves:

1. **Tiered connector roadmap, sequenced by estate share:**
   - **Tier 1 (build first):** Spark OpenLineage (exists in v8), **Airflow** OpenLineage provider, **dbt** (manifest/artifacts + sqlglot column lineage), **Snowflake** `ACCESS_HISTORY` (query-log-derived column lineage), Kafka via schema registry (ADR-014). These five cover the bulk of a modern data estate.
   - **Tier 2:** Flink OpenLineage, Kafka Streams interceptor, generic warehouse query-log parsing (Trino/BigQuery/Redshift patterns), Dask (demoted from v8's Tier 1 — see below).
   - **Tier 3 (never fully automated):** stored procedures, legacy ETL — best-effort sqlglot parsing plus the escape hatch.
2. **A declarative escape hatch as a first-class signal:** `lineage.yaml` **lineage contracts** in repos — schema-validated edge declarations with owner and review TTL, ingested as the `declared` signal with the ADR-007 confidence discipline (cap Probable, TTL decay). Plus a steward-only manual-edge API (mandatory owner + expiry). Any team can make any system visible *today*, at honestly-capped confidence, without waiting for a connector.
3. **Coverage is a product surface:** per-domain coverage % (assets with ≥1 signal; % of edges runtime-confirmed) as a standing SLI (ADR-017), and **"uncovered" as a first-class rendered state** — the UI must show blind spots as blind spots (GAP-S5).

Dask is demoted from v8's day-one set: it is the narrowest of the four original collectors, and estate share, not implementation order in a demo, should sequence connectors.

**Alternatives considered.** **Build connectors serially and accept dark zones** (v8's implicit plan) — leaves the gate's correctness boundary invisible for years. **Adopt DataHub/OpenMetadata ingestion as a collector fleet** feeding our graph — genuinely attractive: dozens of maintained connectors for free. Not chosen as v1 core because it imports a foreign identity model at the exact layer (identity) this architecture works hardest to control. **Flagged for the board as the Tier-2 accelerator option:** run selected catalog connectors → normalize to OpenLineage → ingest as a `catalog` signal, confidence-capped like `declared`.
**Revisit trigger:** connector-tier sequencing reviews quarterly against measured estate share.

---

## ADR-013: Parser and static-analysis stack

**Status:** Decided — v1 app-code exclusion flagged for board · **Resolves:** GAP-B4; supports GAP-S1

**Context.** "Static analyzer parses repo code, SQL, orchestration DAGs" (v8 FR-C1) hides a 10× tractability spread. Without naming parsers and drawing the feasibility line, the estimator and the roadmap are pricing fiction.

**Decision.** **sqlglot** is the SQL backbone — pure-Python parser/transpiler with 20+ dialect support and AST-level column-lineage extraction; embeddable in collectors, the CI diff service, and (v2) the semantic-diff engine. The **feasibility inventory** (full table in HLD §4) classifies every source type as `feasible-static` (warehouse SQL, dbt models, Avro/protobuf/OpenAPI schemas, Airflow DAG topology), `LLM-assisted` (PySpark/DataFrame chains, notebook SQL-in-strings, dynamic SQL, UDF bodies), or `declared-only` (stored-proc forests, closed-source ETL, anything Tier 3) — and the declared-only class is served by the ADR-012 escape hatch rather than over-promised.

**Deep application-code dataflow analysis (CodeQL-class interprocedural taint tracking through Java/Go services) is explicitly out of v1.** The cost/precision curve does not clear the bar, and the architecture already has a better instrument for that layer: runtime signals (OTel + OpenLineage) observe what services *actually* do. Static covers data-transform code; runtime covers application behavior. *(Board confirmation requested on this exclusion.)*

**Alternatives considered.** **Apache Calcite** — JVM-heavy, weaker dialect breadth, awkward embedding in Python-side collectors. **ZetaSQL** — BigQuery-centric. **sqllineage** — thinner than sqlglot's AST. **Buying CodeQL-class analysis for app code** — see exclusion above.
**Revisit trigger:** if LLM-assisted extraction (ADR-015) misses its precision gate on DataFrame-heavy estates, revisit dedicated PySpark static analysis (e.g., AST walkers) before reaching for deep dataflow tooling.

---

## ADR-014: Schema registry integration

**Status:** Decided · **Resolves:** GAP-B2

**Context.** The registry is the only *authoritative* type source in the signal set — everything else infers. v8 references "registry subject+version" and designs nothing. The severity matrix's judgments (widen/narrow/nullability) are only as good as the types underneath.

**Decision.** Registry synchronization is a **first-class collector family**, and the registry is **type truth** in the ADR-007 matrix:

- **Streams:** Confluent Schema Registry sync — subjects/versions polled and change-evented; Avro/protobuf/JSON-schema parsed into the field model.
- **Warehouses/lakes:** scheduled `INFORMATION_SCHEMA` (and Iceberg catalog) snapshots with diff-on-change.
- **Services:** OpenAPI/protobuf definitions harvested from repos by the static collector; payload fields enter the graph as `field`-type entities under endpoints.
- Every sync lands `(urn, schemaVersion)` records in the **version registry** — the identity axis deliberately kept out of the URN (ADR-005). The CI diff service diffs **registered** schema versions, not just PR file text.
- **Registry-vs-runtime drift** (observed type ≠ registered type) is never averaged away: it is surfaced to the asset owner as a finding — often the earliest signal of an unmanaged change.

**Alternatives considered.** **Types from static/LLM inference only** (v8's effective position) — builds the gate's core judgment on the least reliable signal; rejected. **AWS Glue Schema Registry** — fine substitution in an MSK-native shop; note, not a design change. **Buf Schema Registry** for protobuf-heavy estates — same.
**Revisit trigger:** none; "authoritative types where they exist" is foundational.

---

## ADR-015: LLM extraction hardening

**Status:** Decided · **Resolves:** GAP-B3

**Context.** LLM inference is v8's boldest bet and least-governed component: "self-reported confidence," no labeled evaluation, no version pinning, no cost model. v8's numeric quality gates exist only for identity resolution; the same rigor must reach edge extraction — the largest single input to the baseline graph.

**Decision.**

1. **Golden-set eval harness:** ≥500 hand-labeled file→edges examples spanning the estate's top languages and SQL dialects (sampled from the vertical slice and refreshed quarterly). Measured targets for LLM-only edges: **precision ≥90%, recall ≥70%**. Below the precision gate, LLM-only edges are hard-capped at Inferred band regardless of self-reported score — they surface but never influence gating (consistent with ADR-007/008 discipline).
2. **Determinism and drift control:** temperature 0; pinned model versions; **any model or prompt upgrade must re-pass the golden set before rollout** — the same gate a code change would face.
3. **Cost control:** extraction runs only on content-hash change (hash → result cache in PostgreSQL); batch scheduling off-peak; cost model with formulas in HLD §4 (at the 2k design point, order low-thousands USD/month — dominated by initial backfill, then change-rate-bounded).
4. **Provenance:** every LLM-derived edge stores model version, prompt version, and content hash — reproducible and re-derivable, per the package-wide epistemics.

**Alternatives considered.** **Trust self-reported confidence** (v8) — the model grading its own homework; rejected. **Fine-tuned local model** — premature before a golden set even exists to fine-tune against; the eval harness is the prerequisite either way. **Skip LLM, static-only baseline** — loses coverage of exactly the LLM-assisted class in ADR-013's inventory; the discipline above makes the bet governable instead of abandoning it.
**Revisit trigger:** golden-set metrics stable ≥2 quarters → consider raising LLM edge cap or fine-tuning; sustained miss → shrink LLM scope to suggestion-only (feeds ADR-006's candidate queue).

---

## ADR-016: Security and tenancy

**Status:** Decided · **Resolves:** GAP-D3

**Context.** The lineage graph is a map of where PII flows, which systems touch payment data, and where the soft spots are — reconnaissance gold. v8 makes PII classification a first-class attribute and a search facet, and defines no authentication, authorization, or audit. "We only store metadata" appears nowhere as an enforced property.

**Decision.**

1. **Single-tenant** deployment (one org). The URN grammar carries an org-capable `authority` structure, so multi-tenancy is a seam, not a rewrite — but it is explicitly out of v1.
2. **AuthN:** OIDC SSO against the corporate IdP; service accounts (collectors, CI) use short-lived workload identity, never shared secrets.
3. **AuthZ:** RBAC v1 — `viewer`, `domain-steward`, `platform-admin`, `service-account` — with permission matrix in HLD §9. **Domain-scoped visibility** (ABAC on domain tags, likely PostgreSQL row-level security) targeted v1.5; v1 access is org-internal with PII-lineage reads audited.
4. **Metadata-only, enforced:** ingestion schemas **structurally reject** value-bearing payloads (no sample values, no row data fields exist in the schema to fill). The property is enforced by schema validation at the gateway, not asserted in documentation.
5. **Audit events:** gate decisions, waivers, manual edges, identity merges, policy changes, and **reads of PII-tagged lineage** — append-only, queryable, retained per policy.
6. **Classification propagation:** PII/classification tags propagate downstream along Verified edges as *advisory* markings (a governance aid, never auto-enforcement).
7. **Retention/GDPR:** raw events 13 months (Iceberg row-level deletes make purge real, ADR-003); the graph stores no personal data by construction; audit records carry actor IDs under the corporate retention schedule.

**Alternatives considered.** **Perimeter auth only, authz later** — indefensible for a PII-flow map; rejected. **Full ABAC day one** — heavier than v1 adoption needs; RBAC-then-ABAC is the boring path. **Multi-tenant SaaS posture** — out of scope; seams noted.
**Revisit trigger:** first external-audit finding or first cross-org sharing requirement.

---

## ADR-017: Platform self-observability

**Status:** Decided · **Resolves:** GAP-D4, GAP-E2

**Context.** A trust product must prove its own trustworthiness. If ingestion lags three days, every confidence score is quietly stale and the gate is deciding on old truth. v8 offers one health endpoint and no SLI definitions. Separately, v8's success metrics are all directional ("majority," "growing") — unquantifiable and therefore unfalsifiable.

**Decision.** The platform is **OTel-instrumented end to end**, metrics in **Prometheus**, dashboards/alerts in **Grafana**, with a designed SLI family whose targets (numbers in HLD §11) **double as the platform's quantified success metrics** — one instrument serves both operations and the funding gates:

- **Pipeline health:** ingestion lag p95 (event `observedAt` → queryable), event acceptance rate, DLQ depth, collector heartbeat freshness.
- **Graph quality:** coverage % (assets with ≥1 signal, per domain), % of active edges runtime-confirmed, identity sampled precision, unresolved-entity count, conflict-triage backlog.
- **Gate quality:** gate p95 latency, fail-open rate, waiver rate per rule, calibration drift (observed band precision vs target).

**Alternatives considered.** **Datadog** — fine managed substitution, note only. **Standard infra dashboards without designed SLIs** — measures the machines, not the epistemics; rejected.
**Revisit trigger:** SLI target values are config reviewed quarterly with calibration (ADR-008); the SLI *family* is the architecture.

---

## ADR-018: Deployment topology

**Status:** Decided — single-region posture flagged for board · **Resolves:** GAP-D2

**Context.** A platform that gates merges is production infrastructure from block-mode day one. v8 has no deployment section, "pre-replication" storage numbers, and no HA/DR/RPO/RTO story.

**Decision.**

1. **Kubernetes, single region, multi-AZ.** All four planes are stateless deployments on HPA except the impact engine (stateful in-memory projection — replicas warm up from CDC in minutes and are disposable).
2. **PostgreSQL:** managed HA (RDS/Aurora multi-AZ failover; Patroni if self-hosted). **Kafka:** 3-AZ replication.
3. **DR by rebuild-from-log:** raw events on S3 are RPO≈0 (11-nines durability); the graph is *derived* state, rebuildable from Iceberg ≤8h at the 2k design point. Graph RPO 24h (worst case: replay yesterday), platform RTO 4h. Cross-region PostgreSQL replicas are deliberately *not* the v1 DR mechanism — for a rebuildable derived store, replay is cheaper and more honest than replica fleets. *(Board confirmation requested on the single-region posture.)*
4. **Platform environments (dev/staging/prod) are orthogonal to the URN `env` axis.** The platform's *staging* ingests events *about* the estate's prod and staging alike, tagged by URN. Stated here and in HLD §1 because it is the single most reliable confusion in systems of this shape.
5. Failure-mode table (HLD §12): Kafka down → collectors buffer locally, gate degrades per policy (fail-open); PostgreSQL failover → read-only serving continues from projections; LLM outage → baseline refresh pauses, zero runtime-signal impact.

**Alternatives considered.** **Cross-region active-passive** — doubles cost and operational surface to protect a derived store that rebuilds in hours; rejected for v1. **Serverless-first (Lambda/Fargate)** — poor fit for the stateful projection and long-lived consumers.
**Revisit trigger:** gate adoption reaching org-wide block-mode (the merge path's availability tolerance tightens) → revisit cross-region.

---

## ADR-019: API serving strategy

**Status:** **Default — board confirmation requested** · **Resolves:** part of GAP-D1; supports GAP-A4

**Context.** v8 exposes REST plus an open GraphQL endpoint for altitude-scoped UI queries. Open GraphQL against a graph with hub nodes is a standing invitation to accidental (or adversarial) unbounded traversal — the exact fan-out problem ADR-010 caps elsewhere.

**Decision (default).** **REST is the contract surface** for all programmatic consumers (collectors, CI, integrations) — versioned, paginated, budget-capped per ADR-010. **GraphQL survives only as persisted queries**: the UI's altitude-navigation query shapes (v8's own good idea) are registered server-side, cost-analyzed once at registration, and invoked by ID. Arbitrary client-composed GraphQL is not accepted.

**Alternatives considered.** **REST-only** — simplest, but forfeits the genuinely good fit between GraphQL selection sets and the altitude/lens UI (one round-trip per lens switch), forcing either chatty REST or bespoke aggregate endpoints that are persisted queries in worse clothing. **Open GraphQL with depth/complexity limiting** — workable and widely done, but cost estimation on a lineage graph with hubs is subtle, and a misestimated query is a production incident; a closed query set is the boring answer.
**Consequences.** UI query changes require registering a persisted query (a deploy-time step, not a blocker). Third parties integrate via REST.
**Revisit trigger:** mature cost-limiting in the chosen GraphQL server plus demonstrated demand for ad-hoc graph queries from power users.

---

## Summary table

| ADR | Decision | Status |
|---|---|---|
| 001 | PostgreSQL 16 SoR + in-process CSR projection; no graph DB in v1 | Decided |
| 002 | Kafka backbone, URN-hash partitioning | Decided |
| 003 | S3 + Iceberg raw store; idempotent/ordered/replayable ingestion contract | Decided |
| 004 | Bitemporal-lite, logical snapshots, pinned decision triples | Decided |
| 005 | `urn:tl:` grammar; entityId + aliases; schema version as separate axis | Decided |
| 006 | Deterministic identity chain; human-confirmed merges; no probabilistic auto-merge | Decided |
| 007 | Per-attribute precedence matrix; cold-path visibility invariant; `declared` signal | Decided |
| 008 | v8 scoring as prior; bands-only display; quarterly calibration; versioned model | Decided |
| 009 | active → stale → retired lifecycle with tombstones | Decided |
| 010 | Cycle-safe, budgeted, snapshot-pinned traversal; max/coverage-weighted roll-ups | Decided |
| 011 | OPA gate policy; waiver objects + FP circuit-breaker; fail-open; codeRef logic detection; repo manifests | Decided (Tier-0 opt-in flagged) |
| 012 | Tiered connectors + `lineage.yaml` declared contracts; coverage as product | Decided (buy-note flagged) |
| 013 | sqlglot; feasibility inventory; no deep app-code dataflow in v1 | Decided (exclusion flagged) |
| 014 | Registry sync as collector family; registry = type truth | Decided |
| 015 | LLM golden-set gates; pinned versions; content-hash caching; cost model | Decided |
| 016 | Single-tenant, OIDC, RBAC; metadata-only enforced; audited PII-lineage reads | Decided |
| 017 | OTel/Prometheus/Grafana; SLI family = success metrics | Decided |
| 018 | K8s single-region multi-AZ; managed PG HA; DR by rebuild | Decided (posture flagged) |
| 019 | REST contracts; GraphQL as persisted queries only | Default — board |
