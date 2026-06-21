# Throughline Implementation Blueprint Design

**Date:** June 20, 2026  
**Status:** Approved  
**Audience:** Product leadership, enterprise architecture, data platform, application engineering, security, and delivery teams  
**Deliverable:** A new self-contained HTML companion; all source PRDs and prototype pages remain unchanged

## Purpose

Create an implementation-ready companion to the three Throughline PRDs and prototype. The document must connect product expectations to a production architecture, distinguish platform APIs from application endpoints modeled by lineage, expose end-to-end process flows, and provide defensible scale and delivery estimates for tens of thousands of services across domains and schemas.

The companion is additive. It does not replace `Architecture & Scale.dc.html` or `Roadmap & LOE.dc.html`; it corrects their gaps and makes their assumptions explicit.

## Chosen Approach

Use a decision-ready implementation blueprint rather than an API-only reference or diagram-only architecture dossier. Begin with a concise decision summary, then progressively disclose technical contracts, topology, flows, endpoints, capacity math, reliability, and delivery estimates.

The artifact will be a self-contained HTML file with inline CSS and JavaScript. It will retain the prototype's restrained IBM Plex-inspired typography, blue/orange/purple/teal semantic palette, progressive disclosure, and evidence-oriented detail without pretending to be a live product screen.

## Content Architecture

1. Scope, product promise, decisions, and explicit assumptions
2. Cross-PRD contract and unresolved requirement contradictions
3. Canonical entity, schema-version, assertion, and edge model
4. Logical architecture and initial deployment topology
5. Collection, reconciliation, impact/gate, and progressive UI query flows
6. Platform API endpoint catalog and application endpoint/payload lineage
7. Cross-domain partitioning, indexing, caching, retention, replay, security, and operations
8. Interactive capacity model for 10k, 25k, and 50k services
9. Full P0/P1/P2 estimate with P0 MVP breakout, staffing scenarios, critical path, and uncertainty drivers
10. Recommended SLOs, risks, open decisions, and acceptance checklist

Every substantive assumption must be labeled as one of:

- **PRD states:** directly traceable to the source PRDs or prototype.
- **Blueprint assumes:** necessary planning assumption where the sources are silent.
- **Recommended decision:** proposed resolution to a contradiction or production gap.

## Technical Model

Start with four to six deployables even though the logical model contains more components:

1. **Ingestion Gateway:** accepts OpenLineage and adapters for OTel, schema registries, API specifications, static analysis, and CI evidence.
2. **Lineage Core:** validates events, resolves canonical identity, stores immutable assertions, reconciles evidence, scores confidence, versions the graph, and publishes projections.
3. **Query and Impact Service:** provides scoped graph traversal, search, compatibility rules, impact reports, and CI decisions.
4. **Integration Workers:** run replay, backfill, catalog synchronization, notifications, and webhook delivery.
5. **Web Experience:** implements the four prototype lenses using bounded, progressive APIs.
6. **Control Plane:** manages collectors, policies, ownership, authorization, audit, and health; it may begin in the same deployment as the gateway or workers.

Backing services include a durable event log, raw object archive, graph projection, relational metadata store, search index, cache/rollups, and observability stack.

## Canonical Data Semantics

The model includes organization/tenant, domain, business application, team, service, endpoint/operation, request or response schema, job/run, dataset, schema version, field, evidence assertion, canonical relationship, graph snapshot, proposed change, compatibility policy, and immutable impact report.

Important relationship types are deliberately distinct:

- `INTERACTS_WITH` represents runtime service or endpoint traffic and does not become lineage automatically.
- `FIELD_FLOWS_TO` represents evidence-backed movement between dataset or API payload fields.
- `PRODUCES`, `CONSUMES`, and `CONTAINS` express ownership and hierarchy.
- Transformation relationships retain expression or semantic class, path, code reference, channel, observation interval, and evidence.

Canonical identity includes organization/tenant, environment, asset kind, namespace, source identity, schema or contract version, and path where applicable. Immutable source assertions are retained separately from reconciled graph edges so alternate paths and conflicting evidence are not collapsed.

OpenLineage remains canonical for job and dataset lineage ingestion and export. OTel, API specifications, schema events, and static analysis retain source-specific contracts before normalization into a versioned internal assertion model.

## Process Flows

### Ingestion and Reconciliation

`authenticate -> validate/version -> durable raw log -> normalize -> quarantine if invalid -> resolve identity -> upsert assertion -> reconcile/score -> update graph/search/rollups -> invalidate caches`

The flow covers idempotency, ordering, retries, late events, tombstones, replay, backfill, and stale-edge decay.

### Change Impact and CI Gate

`resolve versioned change -> choose graph snapshot and policy version -> bounded cycle-safe field traversal -> apply compatibility and transform rules -> resolve owners -> persist impact report -> notify owners -> return or callback CI decision`

Large traversals use asynchronous jobs with status and cancellation. Gate behavior is policy-controlled and explicitly fail-open or fail-closed.

### Progressive UI Query

`search or select scope -> fetch aggregate rollup -> request bounded neighborhood -> select entity/field -> fetch evidence or impact detail -> preserve scope, snapshot, filters, and selection across lenses`

No normal UI journey loads or renders the global graph.

## Endpoint Design

The platform API catalog is grouped into collection, graph/query, impact/review, interactions/contracts, and administration/operations. It specifies authentication and authorization scope, tenant/environment scoping, idempotency, version headers, pagination/cursors, ETags, asynchronous semantics, errors, rate limits, audit behavior, and proposed SLOs.

Application endpoint lineage is modeled separately: service -> endpoint/operation -> request/response schema version -> nested payload field. Runtime `INTERACTS_WITH` edges may reference these identities, while `FIELD_FLOWS_TO` requires explicit evidence linking payload fields to other payload or dataset fields.

## Capacity Model

The page provides transparent, editable assumptions for:

- services, domains, environments, and growth
- datasets per service and fields per schema
- API endpoints, message schemas, and payload fields per service
- lineage path multiplicity and evidence assertions
- job runs, average/p95 event sizes, and peak factors
- retention, index/replica overhead, backups, and search projections
- query, search, impact, and CI concurrency

Results compare 10k, 25k, and 50k services and show formulas for logical nodes/edges, physical graph footprint, daily ingest, raw annual retention, peak throughput, and major omitted multipliers. Telemetry volume is modeled separately from OpenLineage events because raw OTel spans may dominate capacity.

## Delivery Estimate

Display planning ranges, not false precision:

- **P0 MVP:** approximately 110-175 engineer-weeks
- **Full P0/P1/P2 production scope:** approximately 325-535 engineer-weeks
- **Five engineers at 65% effective capacity:** approximately 25-39 months
- **Eight engineers at 65% effective capacity:** approximately 16-24 months
- **Ten engineers at 65% effective capacity:** approximately 12-20 months

Show incremental effort ranges for additional parser or SQL families, execution engines, CI providers, catalogs, and schema registries. Explain the critical path through canonical identity, evidence reconciliation, confidence calibration, impact correctness, and production hardening. Keep product/design/PM and security participation visible rather than hiding them inside engineering totals.

## Reliability and Failure Behavior

Proposed SLOs are recommendations, not PRD commitments. The document will include availability, ingest acknowledgement, projection freshness, scoped query/search latency, synchronous and asynchronous impact latency, CI response, RPO, and RTO targets.

Failure behavior covers malformed events, unauthorized domains, duplicate and out-of-order assertions, identity conflicts, stale evidence, partial or truncated traversals, policy-version mismatch, notification retries, callback failures, replay, and degraded reads. Every partial result must expose coverage and uncertainty instead of appearing complete.

## Visual Design

- Professional technical-report layout with sticky table of contents on wide screens and compact navigation on small screens
- IBM Plex-style sans and mono typography with system fallbacks
- Restrained semantic color: collection blue, graph purple, impact orange, experience teal, operations green
- C4-style container view, sequence-flow lanes, an entity/assertion model, partition routing diagram, endpoint cards, formula panels, and delivery ranges
- Interactive controls limited to useful comprehension: scenario presets, scale inputs, endpoint category filters, schema tabs, and collapsible evidence
- Responsive at desktop, tablet, and mobile sizes; usable print layout; no remote runtime dependency

## Verification And Acceptance

1. Every PRD is represented in the cross-PRD contract and traceability view.
2. Runtime interactions and payload-field lineage remain semantically distinct throughout diagrams, endpoints, and examples.
3. Capacity calculations are covered by deterministic tests at 10k, 25k, and 50k services.
4. Delivery ranges reconcile mathematically with staffing and effective-capacity assumptions.
5. Endpoint groups include production concerns: auth, idempotency, pagination, async jobs, errors, versioning, rate limits, audit, replay, and health.
6. The HTML works without `support.js` or a framework runtime.
7. Browser verification covers interactions, console errors, desktop/tablet/mobile widths, and print styling.
8. The final file is additive; no source PRD, prototype, architecture, or roadmap file is modified.

