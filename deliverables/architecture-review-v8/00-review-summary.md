# 00 — Review Summary

| | |
|---|---|
| **Status** | Final — for review board |
| **Reviews** | Throughline v8 (`deliverables/latest_source/Data Lineage Impact Platform-8/`) |
| **Reviewer stance** | Distinguished-engineer architecture review: identify what blocks implementability, resolve it by design, keep what works |

## §1 Verdict

**The product thesis is right and worth building. The v8 architecture is not implementable as written.**

The wedge is real: fusing static + LLM baseline signals with Spark/Dask/OTel runtime signals into a *confidence-scored, path-qualified, column-level* graph — and enforcing it in CI/CD — is genuinely beyond what table-level catalogs do, and v8's own build-vs-buy position ("integrate where off-the-shelf fits, build the wedge") is correct.

But v8 stops at the pitch layer on every load-bearing wall: no temporal model (gate decisions cannot be reproduced), no identity specification (the join key for every signal is an example, not a grammar), no named technology, no NFR numbers, no security model for a graph that maps PII flows, a gate with no waiver/policy machinery, and collection coverage that ends at four collectors with no escape hatch. Its own Critical Review found 20 issues and its Remediation Plan honestly closed the program-shaped ones — but punted five architecture-shaped ones that never landed.

This package identifies **28 gaps** ([01-gap-register.md](01-gap-register.md)): 26 resolved by design in this package (19 ADRs + normative HLD), 2 recorded as out of charter scope (both delivery-plan findings). Result: an implementable target architecture on a 2,000-service design point with a validated 10,000-service ceiling.

## §2 What v8 gets right (keep, do not relitigate)

Carried unchanged from v8's own review, and endorsed here: (1) the multi-signal + confidence fusion wedge; (2) code-path-level impact (branch-qualified edges with guards and codeRefs — this package's logic-change detection is built *on* it); (3) CI/CD gating that closes the loop; (4) the altitude model for UI scale; (5) a working prototype that de-risks the vision; (6) staged funding with gates; (7) the observe→warn→block adoption ramp; (8) the identity-resolution P0 spike with numeric GO/PIVOT/STOP gates (retained as the acceptance bar for ADR-006).

## §3 Six findings that change the architecture

1. **No temporal model → non-reproducible gate decisions** (GAP-A1, Critical). The graph mutates continuously under its readers; a blocked PR appealed an hour later can evaluate differently, and nobody can prove why. *Resolved:* append-only bitemporal facts, logical snapshots, every decision pins `{snapshotId, policyVersion, confidenceModelVersion}` (ADR-004).
2. **Identity is hand-waved at the exact layer everything joins on** (GAP-A2, Critical — extends v8's own finding). No URN grammar, no environment axis (staging corroborates prod!), no rename continuity. *Resolved:* normative `urn:tl:` grammar + stable entityId with aliases; deterministic resolution chain, human-confirmed merges, never probabilistic auto-merge (ADR-005/006).
3. **Coverage stops at four collectors and dark zones are invisible** (GAP-S1, Critical — v8 self-identified, never landed). Every uncovered system makes the gate silently wrong. *Resolved:* tiered connector roadmap (Snowflake/dbt/Airflow first), declarative `lineage.yaml` contracts as a first-class capped-confidence signal, coverage as a rendered product state (ADR-012).
4. **The gate has no survival machinery** (GAP-C1..C5). Schema-diff-only detection, no waivers, no policy framework, no latency budget, no failure posture — v8's own review predicted engineers would route around it. *Resolved:* OPA policy-as-code owned by stewards, waiver objects with expiry + FP circuit-breaker, p95 <30s / fail-open+warn, codeRef-based logic-change detection, `throughline.yaml` repo manifests (ADR-011).
5. **No named technology, no NFRs, and scale math that omits the dominant volume** (GAP-D1, D5, D6). *Resolved:* full named stack (headline: PostgreSQL 16 + in-process CSR projection — no graph database for a 4 GB graph); corrected capacity model showing OTel observations outnumber OpenLineage events ~7.6:1 *after* mandatory collector-side aggregation; complete NFR/SLO table (ADR-001..003, HLD §10–11).
6. **A PII-flow map with no security model** (GAP-D3, Critical). The lineage graph is reconnaissance gold. *Resolved:* OIDC + RBAC, metadata-only *enforced* at the ingestion schema, audited PII-lineage reads, GDPR-capable retention (ADR-016).

## §4 Delta table — v8 said → this package decides

The full 16-row version is in [02-target-architecture.md §6](02-target-architecture.md#6-key-changes-vs-v8); headlines:

| v8 said | Decided here | ADR |
|---|---|---|
| "graph DB + partitions" | PostgreSQL 16 + CSR projection; no graph DB in v1 | 001 |
| continuous upsert, no time axis | bitemporal facts + pinned snapshots | 004 |
| URNs by example | normative grammar + entityId/alias identity | 005/006 |
| "who wins?" open | per-attribute conflict matrix + cold-path invariant | 007 |
| 0.94-style confidence | bands-first, quarterly-calibrated, versioned | 008 |
| decay only | active/stale/retired lifecycle + tombstones | 009 |
| unbounded BFS | cycle-safe, budgeted, snapshot-pinned traversal | 010 |
| gate happy path | OPA + waivers + circuit-breaker + fail-open | 011 |
| four collectors | tiers + declared contracts + coverage surface | 012 |
| OL-only sizing | corrected 2k/10k model incl. OTel + payload fields | HLD §10 |

## §5 Scale anchor summary

Design point 2,000 services, ceiling 10,000 (full formulas HLD §10):

| Metric | @2k | @10k |
|---|---|---|
| Nodes (corrected basis, incl. endpoints/payload fields/jobs) | 346,000 | 1,730,000 |
| Edges (lineage + interaction + payload) | 740,000 | 3,700,000 |
| Graph store incl. indexes/versions | 2.6 GB | 13.2 GB |
| CSR traversal projection | 22 MB | 111 MB |
| Events/day (OL + aggregated OTel) | 828,000 | 4,140,000 |
| Peak ingest | ~38 events/s | ~192 events/s |

Two lessons the numbers teach: v8's sizing omitted OTel entirely (the dominant stream, even after mandatory collector-side aggregation — raw spans would be ~8.6 **billion**/day at 2k), and the graph is small — **capacity is not this system's risk; correctness under identity, conflict, and time is.** That is why the headline storage decision is a boring relational database and the engineering attention goes to fusion semantics.

## §6 Scope exclusions

- **GAP-R1** (High, recorded): five unreconciled effort envelopes across the v8 set (~134–193, 145–205, 325–535, ~605–780 eng-weeks, ~240 person-months) and an 18-vs-24-month timeline conflict between the Roadmap and the Remediation Plan/Executive Narrative. Remediation is the program team's, per charter — but the board should not fund against these documents until one envelope is designated authoritative (evidence table in [01 §R](01-gap-register.md#r--delivery-plan-recorded-remediation-out-of-charter)).
- **GAP-S3** (AI-uplift re-baseline): same disposition, same owner.
- Org staffing and delivery re-planning: out of charter.

## §7 How to read this package

| You are | Read |
|---|---|
| Exec / sponsor | This document §1–§5 |
| Review board | 00 → [01 gaps](01-gap-register.md) → [02 architecture](02-target-architecture.md) → [03 ADRs](03-decision-records.md) → [04 HLD](04-high-level-design.md); confirm the five items in [README §6](README.md#6-open-items-for-the-review-board) |
| Implementer | [02](02-target-architecture.md) → [04](04-high-level-design.md) → [03](03-decision-records.md), with [05 deep-dive](05-subsystem-deep-dive.md) / [deep-dive.html](deep-dive.html) as the guided tour of collection, fusion, impact, and the PR flow |
| Anyone, hands-on | [architecture-explorer.html](architecture-explorer.html) — the interactive version: step through the flows, browse every API with examples, build a URN, score an edge, drag the capacity slider |

Status legend and conventions: [README §3](README.md#3-conventions).
