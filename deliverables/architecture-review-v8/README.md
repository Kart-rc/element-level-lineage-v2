# Throughline v8 — Architecture Review & Target Architecture Package

| | |
|---|---|
| **Status** | Final — for review board |
| **Version** | 1.0 |
| **Date** | 2026-07-05 |
| **Reviews** | `deliverables/latest_source/Data Lineage Impact Platform-8/` (the v8 proposal, 15 documents) |
| **Audience** | Review board, enterprise architecture, data platform engineering, sponsor |
| **Author role** | Distinguished-engineer architecture review |

## 1. What this package is

Throughline v8 proposes an enterprise element-level (column/field) data lineage and impact-analysis platform: fuse static-analysis + LLM baseline signals with Spark/Dask/OTel runtime signals into one confidence-scored, path-qualified column-level graph, and enforce impact analysis in CI/CD. This package is the independent architecture review of that proposal, plus the target architecture and high-level design needed to make it implementable.

The review's verdict, in one line: **the product thesis is right and worth building; the v8 architecture is not implementable as written.** This package identifies 28 gaps, resolves 26 by design (three with explicitly deferred sub-parts and named re-opening triggers), and records 2 as out of charter scope (both delivery-plan findings).

**Charter constraints** (fixed by the sponsor):

- Deliverables are Markdown, in this directory.
- Technology recommendations are **concrete and named**, each with selection criteria and alternatives considered.
- Scale anchor: design point **2,000 services** (current estate per the v8 Executive Narrative), validated headroom to **10,000 services** (the v8 Architecture & Scale lower bound). Capacity math is redone at 2k with the 10k ceiling shown alongside.
- Scope is **architecture only**. The v8 delivery-plan inconsistencies (timeline and effort envelopes) are recorded as a finding (GAP-R1) but not remediated here.

## 2. Document map and reading order

| Doc | Contents | Read it if you are |
|---|---|---|
| [00-review-summary.md](00-review-summary.md) | Verdict, what v8 gets right, the six findings that change the architecture, delta table (v8 said → this package decides) | Everyone; execs can stop after §1–§4 |
| [01-gap-register.md](01-gap-register.md) | The canonical 28-gap register with evidence, options, recommendations, dispositions; crosswalk to v8's own Critical Review | Review board, architects |
| [02-target-architecture.md](02-target-architecture.md) | Target architecture narrative: principles, container view with named technologies, stack decision table, data-flow walkthroughs | Architects, implementers (start here to build) |
| [03-decision-records.md](03-decision-records.md) | 19 architecture decision records (ADR-001…ADR-019), full form | Review board (decisions), implementers (rationale) |
| [04-high-level-design.md](04-high-level-design.md) | Normative specifications: URN grammar, data model DDL, ingestion contract, conflict matrix, impact engine, CI gate, APIs, security, capacity math, NFR/SLO table, operations | Implementers; the board for §10–§11 |
| [05-subsystem-deep-dive.md](05-subsystem-deep-dive.md) | Deep-dive on the four core subsystems — collection mechanisms, fusion engine, impact-analysis flow, PR/gate flow — with diagrams and worked examples on the v8 Orders scenario | Anyone wanting the guided tour; pairs with the HTML below |
| [deep-dive.html](deep-dive.html) | Self-contained HTML rendering of the deep-dive with visual flows, record-evolution cards, the six-hop blast radius, and tabbed PR walkthroughs (no external dependencies; light/dark) | Non-Markdown readers; demos and reviews |
| [architecture-explorer.html](architecture-explorer.html) | **Interactive explorer for the whole package**: clickable four-plane architecture, step-through flows with real payloads, a 20-endpoint API explorer with examples, a URN builder, a live confidence calculator (the exact ADR-008 rules), a 2k→10k capacity slider, and filterable gap/ADR registers. Self-contained, light/dark, deep-linkable tabs | Everyone — the fastest way to *understand* the architecture |

Reading order:

- **Exec / sponsor:** this README → 00 (§1–§4).
- **Review board:** 00 → 01 → 02 → 03 → 04, with 05/deep-dive.html as the guided tour.
- **Implementers:** 02 → 04 → 03, with 01 as reference and 05 as the subsystem walkthrough.

Division of labor: **ADRs decide and justify; the HLD specifies; the deep-dive narrates and exemplifies.** An ADR states the decision and why the alternatives lost; the normative spec text (grammars, schemas, matrices, numbers) lives in 04 and is referenced, never duplicated; 05 and its HTML companion walk the four core subsystems with diagrams and worked examples.

## 3. Conventions

### 3.1 Gap IDs (minted in 01-gap-register.md, the traceability root)

| Prefix | Meaning | Count |
|---|---|---|
| `GAP-S1..S5` | v8 self-identified gaps (its own Critical Review) still open after its Remediation Plan | 5 |
| `GAP-A1..A5` | Net-new: data model & semantics | 5 |
| `GAP-B1..B4` | Net-new: collection & maintenance | 4 |
| `GAP-C1..C5` | Net-new: impact analysis & CI/CD | 5 |
| `GAP-D1..D6` | Net-new: platform & non-functional requirements | 6 |
| `GAP-E1..E2` | Net-new: operating model | 2 |
| `GAP-R1` | Delivery-plan inconsistency (recorded; remediation out of charter) | 1 |

v8's Critical Review has no formal gap IDs; evidence citations therefore use file + section, e.g. `Critical Review §02 "Identity resolution is the real hard problem"`.

### 3.2 Dispositions (closed vocabulary)

- **Resolved-by-design** — closed by a decision/spec in this package (`→ ADR-xxx`, `HLD §y`).
- **Deferred** — intentionally not solved in v1; the entry states the trigger that re-opens it.
- **Accepted-risk** — acknowledged, not mitigated; owner and rationale stated.
- **Out-of-scope** — excluded by the review charter.
- **Closed-in-v8** — v8's Remediation Plan already addressed it; this package verified and retained the fix.

### 3.3 Decision statuses

- **Decided** — the recommendation of this review; implement unless the board objects.
- **Default — board confirmation requested** — a defensible default is set, but the board should explicitly confirm (all such items are listed in §6 below).

### 3.4 Writing rules used throughout

- Confidence is always displayed as an integer score plus band (Verified / Probable / Inferred) — never with decimals. (This package practices the fix it prescribes; see GAP-S4.)
- Every derived capacity number shows its formula inline. No naked numbers.
- 2k design-point and 10k ceiling numbers always appear together.
- Diagrams are Mermaid (render natively on GitHub).

## 4. Traceability matrix

One row per gap. This table is mechanically checked against 01-gap-register.md before commit; 01 is authoritative if they ever diverge.

| Gap | Title | Severity | Disposition | Resolved by |
|---|---|---|---|---|
| GAP-S1 | Collector coverage stops at four collectors; no declarative escape hatch | Critical | Resolved-by-design | ADR-012, ADR-013, HLD §4 |
| GAP-S2 | Cold-path policy and signal conflict-resolution matrix never landed | High | Resolved-by-design | ADR-007, HLD §4 |
| GAP-S3 | AI-uplift re-baseline of estimates promised, never shown | Medium | Out-of-scope | (cross-ref GAP-R1) |
| GAP-S4 | Exec/governance personas unserved; two-decimal confidence contradiction | Medium | Resolved-by-design (partial: API + display; UI redesign deferred) | ADR-008, HLD §8 |
| GAP-S5 | Unknown/empty/error UI states and accessibility undesigned | Medium | Resolved-by-design (API states); visual design Deferred | ADR-009, HLD §8 |
| GAP-A1 | No temporal/versioned graph or snapshot semantics | Critical | Resolved-by-design | ADR-004, HLD §2 |
| GAP-A2 | No formal URN grammar, environment, schema-version, or rename continuity | Critical | Resolved-by-design | ADR-005, ADR-006, HLD §1 |
| GAP-A3 | No tombstone/retirement lifecycle | High | Resolved-by-design | ADR-009, HLD §2 |
| GAP-A4 | No cycle handling or hub caps in impact traversal | High | Resolved-by-design | ADR-010, HLD §5 |
| GAP-A5 | No roll-up aggregation semantics for confidence/severity | Medium | Resolved-by-design | ADR-010, HLD §5 |
| GAP-B1 | Ingestion contract lacks idempotency/ordering/late-event/replay/backfill/DLQ | Critical | Resolved-by-design | ADR-003, HLD §3 |
| GAP-B2 | Schema-registry integration asserted, never designed | High | Resolved-by-design | ADR-014, HLD §3 |
| GAP-B3 | LLM extraction has no eval harness, cost model, or determinism handling | High | Resolved-by-design | ADR-015, HLD §4 |
| GAP-B4 | No static-analysis feasibility inventory per language/dialect | Medium | Resolved-by-design | ADR-013, HLD §4 |
| GAP-C1 | Gate is schema-diff-only; logic-only changes never trigger impact | High | Resolved-by-design (v1 mechanism; semantic diff deferred to v2) | ADR-011, HLD §6 |
| GAP-C2 | No waiver/override/suppression workflow | Critical | Resolved-by-design | ADR-011, HLD §6 |
| GAP-C3 | No policy framework (block vs warn by domain/criticality) | High | Resolved-by-design | ADR-011, HLD §6 |
| GAP-C4 | No gate latency SLO or failure posture | High | Resolved-by-design | ADR-011, HLD §11 |
| GAP-C5 | No monorepo/multi-repo PR→service mapping | Medium | Resolved-by-design | ADR-011, HLD §6 |
| GAP-D1 | No named technology decisions | Critical | Resolved-by-design | ADR-001..003, 013, 014, 019; 02 §3 |
| GAP-D2 | No deployment topology, environments, HA/DR, retention | High | Resolved-by-design | ADR-018, HLD §12 |
| GAP-D3 | No security/authz/tenancy model; lineage maps PII flows | Critical | Resolved-by-design | ADR-016, HLD §9 |
| GAP-D4 | No platform self-observability or coverage SLIs | High | Resolved-by-design | ADR-017, HLD §11 |
| GAP-D5 | Scale math omits OTel volume and API-payload fields | High | Resolved-by-design | HLD §10 |
| GAP-D6 | No p99/QPS targets; no cost model | Medium | Resolved-by-design | HLD §10–§11 |
| GAP-E1 | Day-2 ownership of rules/thresholds/collectors/contracts unspecified | High | Resolved-by-design | HLD §12 |
| GAP-E2 | Success metrics all directional, none quantified | Medium | Resolved-by-design | ADR-017, HLD §11 |
| GAP-R1 | Five unreconciled effort envelopes; 18-vs-24-month timeline conflict | High | Out-of-scope (charter) — recorded with full evidence | 01 §R |

## 5. Decision index

| ADR | Decision (one line) | Status |
|---|---|---|
| [ADR-001](03-decision-records.md#adr-001-graph-storage) | PostgreSQL 16 system of record + in-process CSR traversal projection; no graph database in v1 | Decided |
| [ADR-002](03-decision-records.md#adr-002-event-backbone) | Apache Kafka event backbone, partitioned by entity URN hash | Decided |
| [ADR-003](03-decision-records.md#adr-003-raw-event-store-and-ingestion-contract) | S3 + Apache Iceberg raw store; idempotent, ordered, replayable ingestion contract | Decided |
| [ADR-004](03-decision-records.md#adr-004-temporal-model) | Append-only bitemporal-lite graph; logical snapshots; every decision pins snapshot + policy + model versions | Decided |
| [ADR-005](03-decision-records.md#adr-005-canonical-urn-grammar) | Canonical URN grammar `urn:tl:{env}:{type}:{authority}:{path}[#fragment]`; stable entityId + aliases | Decided |
| [ADR-006](03-decision-records.md#adr-006-identity-resolution) | Deterministic identity-resolution rule chain; human-confirmed merges; no probabilistic auto-merge | Decided |
| [ADR-007](03-decision-records.md#adr-007-signal-precedence-and-conflict-resolution) | Per-attribute signal precedence matrix; cold-path edges always surface; `declared` signal added | Decided |
| [ADR-008](03-decision-records.md#adr-008-confidence-model) | Keep v8 scoring as priors; bands-only display; quarterly calibration; versioned model | Decided |
| [ADR-009](03-decision-records.md#adr-009-entity-lifecycle-and-tombstones) | Lifecycle active → stale → retired with explicit tombstones | Decided |
| [ADR-010](03-decision-records.md#adr-010-impact-traversal) | BFS on CSR projection: cycle-safe, budget-capped, snapshot-pinned; max-severity / coverage-weighted roll-ups | Decided |
| [ADR-011](03-decision-records.md#adr-011-ci-gate) | OPA/Rego gate policy; waivers with expiry + FP circuit-breaker; fail-open default; codeRef logic-change detection | Decided |
| [ADR-012](03-decision-records.md#adr-012-collection-coverage) | Three connector tiers + declarative `lineage.yaml` contracts as first-class signal; coverage map as product feature | Decided (buy-note flagged) |
| [ADR-013](03-decision-records.md#adr-013-parser-and-static-analysis-stack) | sqlglot SQL parsing; SQL-first static analysis; no deep app-code dataflow analysis in v1 | Decided |
| [ADR-014](03-decision-records.md#adr-014-schema-registry-integration) | Confluent Schema Registry + warehouse INFORMATION_SCHEMA + repo OpenAPI/protobuf as type truth | Decided |
| [ADR-015](03-decision-records.md#adr-015-llm-extraction-hardening) | LLM golden-set eval harness with precision/recall gates; pinned models; content-hash caching | Decided |
| [ADR-016](03-decision-records.md#adr-016-security-and-tenancy) | Single-tenant, OIDC SSO, RBAC; metadata-only enforced at ingest; lineage treated as sensitive | Decided |
| [ADR-017](03-decision-records.md#adr-017-platform-self-observability) | OTel-instrumented platform; coverage/precision/gate-quality SLIs double as success metrics | Decided |
| [ADR-018](03-decision-records.md#adr-018-deployment-topology) | Kubernetes, single region multi-AZ; managed PostgreSQL HA; DR by rebuild-from-log | Decided |
| [ADR-019](03-decision-records.md#adr-019-api-serving-strategy) | REST contract surface; GraphQL only as persisted queries for the altitude UI | Default — board confirmation |

## 6. Open items for the review board

Consolidated `Default` decisions and flags that need explicit board confirmation:

1. **ADR-019** — GraphQL restricted to persisted queries (vs. open GraphQL with cost limits, vs. REST-only).
2. **ADR-012 buy-note** — whether to adopt an open-source catalog's connector estate (DataHub/OpenMetadata ingestion framework) as a Tier-2 collector accelerator feeding our graph, versus building all connectors in-house.
3. **ADR-011** — confirmation that Tier-0 domains may opt into fail-closed gate behavior (default posture is fail-open with warn).
4. **ADR-013** — confirmation of the v1 exclusion of deep application-code dataflow analysis (runtime signals carry that burden).
5. **ADR-018** — single-region (multi-AZ) deployment posture with rebuild-based DR, versus cross-region replicas.
