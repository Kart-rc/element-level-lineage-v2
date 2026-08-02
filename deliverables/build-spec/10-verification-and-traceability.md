# 10 — Verification and Traceability

| | |
|---|---|
| **Status** | Draft — for review (normative once approved) |
| **Role** | The package's acceptance roll-up and its self-verification checklist: the counts, numbers, and invariants that must hold across [00](00-component-inventory.md)–[09](09-end-user-testing.md) and [contracts/](contracts/README.md), in the style of [../aws-lineage-collection-plan/07-verification-and-acceptance.md](../aws-lineage-collection-plan/07-verification-and-acceptance.md) §5. |

## 1. What "done" means for a build from this package

A coding agent has built the platform this package specifies when:

1. Every component C1–C12, B1–B9, X1–X4, W1–W5 exists, passes its REQ list, its contract tests (§9 of its home doc), and its live-dependency tests (§10).
2. Every step doc's acceptance checklist (§12) is green on the pilot slice.
3. All seven E2E journeys pass with V1/V2 held throughout.
4. The externally inherited gates hold: identity ≥ 95% precision / ≥ 90% recall with zero cross-environment auto-merges; deterministic artifact reproducibility 100%; gate p95 < 30 s with fail-open tested; deployed lineage queryable ≤ 10 min; replay proves no effective event loss (the de-review month-6 table remains the master list).

## 2. Package traceability counts

| Claim | Count | Where verified |
|---|---|---|
| Components in the registry, each with exactly one PRD home | 30 (12 C + 9 B + 4 X + 5 W) | [00 §3](00-component-inventory.md) matrix; homes per step: 01→3, 02→6, 03→8, 04→4, 05→3, 06→3, 07→2, 08→1 |
| De-review §6.2 components mapped 1:1, order-preserving | 12/12 | [00 §2.1](00-component-inventory.md) |
| Trigger rows, each owned by exactly one step doc | 17/17 — 01: rows 1–3 · 03: 4–7, 15 · 04: 11, 13, 17 · 05: 8–9 · 06: 14, 16 · 07: 10, 12 · 08: none (by design) | [00 §4](00-component-inventory.md); [event-catalog](contracts/events/event-catalog.md) |
| Machine-readable contract files, each carrying `x-source` (or a source table) and cited by ≥ 1 step doc | 12 (8 schemas + 3 OpenAPI + event catalog) | [contracts/README.md](contracts/README.md) inventory |
| Endpoints 21–29 defined exactly once in OpenAPI (21–22 registry, 23–29 approval), referenced elsewhere | 9/9 | [`registry-api`](contracts/openapi/registry-api.openapi.yaml), [`approval-api`](contracts/openapi/approval-api.openapi.yaml) |
| Signals in the closed set, used consistently | 10 | [00 §5](00-component-inventory.md); envelope schema enum |
| Consumer states rendered | 7/7 | [06 §5.1](06-approval.md) REQ-B8-03 |
| E2E journeys, each composing ≥ 1 UC; every persona and interface covered | 7 | [09 §3, §5](09-end-user-testing.md) |
| ADR-020…029 each in ≥ 1 step-doc traceability section | 10/10 — 020: 01/02/03/05 · 021: 02 · 022: 04/08 · 023: 01/03/07/08 · 024: 06 · 025: 01/02/04/07 · 026: 03/05/07/08 · 027: 03/04 · 028: 04 · 029: 01/02/03/07 | step docs §13 |
| F-01…F-07 each in ≥ 1 traceability section | 7/7 — F-01: 03/04/05/06/08 · F-02: 01/04/07 · F-03: 02/03/07/08 · F-04: 02/03/04 · F-05: 01/02/06 · F-06: 03/05/07 · F-07: 03/08 | step docs §13 |
| Every step doc follows the fixed 13-section template | 8/8 | structural review |
| Flow-status acceptance ("record exists for every run") present in every step's §12 | 8/8 | step docs §12 |

## 3. Numbers that must match their sources exactly

Checked against [../architecture-review-v8/04-high-level-design.md](../architecture-review-v8/04-high-level-design.md), [../aws-lineage-collection-plan/](../aws-lineage-collection-plan/README.md), [../platform-10-de-review/README.md](../platform-10-de-review/README.md), [../lineage-collection-assessment.md](../lineage-collection-assessment.md):

- Confidence: weights `30/18/30/26/22`, declared 25, runtime-less cap `64`, declared+attested cap 75, conflict −10, bands `85/65` — integer + band, never decimals.
- Gate: p95 `< 30 s`, hard timeout `120 s` → fail-open + warn; fail-open rate `< 0.5%/30 d`; breaking precision ≥ 98% before block.
- Waivers ≤ `90 d`; declared-contract TTL `180 d` (decay to Inferred); circuit breaker `> 10%/30 d`; self-approval rejected.
- Identity: precision ≥ `95%`, recall ≥ `90%`, zero cross-environment auto-merges.
- Scale: `R = 10,000`, `a = 0.7 → A = 7,000`, `E = A·(d+p+q) = 49,000/day ≈ 0.57 ev/s`; `W = A × t̄_base = 700 task-hours` → < 8 h at C ≥ 100; incremental `280 task-hours/day ≈ 12` concurrent average; classifier pass-through `f = 0.4`; flow-status ≈ `343k` writes/day; Distributed Map ceiling 10,000; 2k design point and 10k ceiling reported together.
- Freshness: streaming evidence p95 ≤ `60 s`, batch/registry ≤ `10 min`; deployed lineage queryable ≤ `10 min`; DLQ alert depth > `100`, drain < `24 h`; flow-status TTL ~`90 d`; webhook dedup TTL `7 d`.
- Availability (inherited): query 99.9% (graph core), queue-buffered ingest 99.5%.

## 4. Structural invariants (the anti-drift checks)

1. **Single normative source.** For every shape, exactly one normative definition: the contracts file (Tier 2) or the cited prose (Tier 1). Step docs restate neither; Tier-3 recaps are marked informative with their source.
2. **Assertion-constraint table = validator.** The envelope schema's `allOf` branches are generated-from/checked-against workflow-spec §5.2; the 20-case MAY/MUST-NOT fixture matrix ([04 §9](04-runtime-corroboration.md)) is the executable proof.
3. **No manual invoke point.** No API path, event, or tool in this package means "run collection now"; replay replays past events only. (Grep-level check: the only human-shaped entries are registration, manifest merges, decisions — all trigger-matrix rows.)
4. **Single writer per store.** `deployment-state` ← W4 only; review records ← finalize only; `llm-cache` ← B4 only; `business-apps` ← B1 only. IAM-tested per the owning docs.
5. **Workflow ASL ↔ spec diagrams.** W1–W5 each carry a structural match test against workflow-spec §1–§4.
6. **Reuse invariant.** W5's rescan invokes W1/C3's machinery — no second extractor.
7. **Error vocabulary.** Every `flow-status.errorClass` value comes from the shared registry ([08 §7](08-scale-and-visibility.md)).
8. **Orthogonal axes.** Nothing in steps 4/5 moves trust; nothing in step 6 moves confidence; step 5's "authoritative" is never rendered as a trust rung.

## 5. Self-verification checklist for this document set

Run before declaring the package reviewable (and after any edit):

- [ ] All relative links resolve (docs ↔ docs, docs ↔ contracts, docs ↔ ../ sources).
- [ ] All Mermaid blocks render.
- [ ] JSON schemas parse as JSON and validate against draft 2020-12; OpenAPI files parse as YAML.
- [ ] §2 counts recomputed and matching; §3 numbers grepped against their sources.
- [ ] Every REQ ID unique package-wide (`REQ-<comp>-NN`); every UC ID unique (`UC-<step>-NN`); every UC maps to ≥ 1 REQ via its step's components; every E2E → ≥ 1 UC.
- [ ] Terminology: signal names only from the 10-value set; coverage states only from the closed set; "Authoritative" only as an environment property.
- [ ] Tier-1 duplication spot-check: no scoring weights, waiver rules, or AWS mappings restated as normative text in step docs.

## 6. Deliberate scope boundaries (honest constraints)

- **Graph core internals** (Aurora DDL, scoring implementation, endpoints 1–20, CSR projection) remain governed by the v8 HLD — this package builds the collection plane against them.
- **`throughline.yaml` JSON Schema** is named as a Phase-0 implementation task ([01](01-onboard.md)); its prose spec is HLD §6.2 + ADR-029's `kind:`.
- **The confidence-model calibration pipeline** consumes the corpus this package produces ([06](06-approval.md)) but is not specified here.
- **Dask lineage, production sidecars, MSK migration** stay behind their named revisit triggers; nothing here forecloses them.
- The de-review's month-6 exit table and funding gates remain the program-level master; this package's acceptance criteria are the build-level decomposition, not a replacement.
