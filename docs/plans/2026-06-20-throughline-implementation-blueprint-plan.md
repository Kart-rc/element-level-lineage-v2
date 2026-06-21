# Throughline Implementation Blueprint Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build and verify a self-contained HTML implementation blueprint connecting the three Throughline PRDs and prototype to production APIs, architecture, process flows, capacity estimates, and full-scope delivery estimates.

**Architecture:** A standard-library Python builder owns the capacity formulas, delivery math, document data, and deterministic HTML generation. The generated artifact uses semantic HTML, inline CSS, and small framework-free JavaScript enhancements so it opens independently and remains printable. Unit tests verify formulas, required content, traceability, and self-containment; browser QA verifies responsive layout and interactions.

**Tech Stack:** Python 3 standard library, `unittest`, semantic HTML5, CSS Grid/Flexbox, vanilla JavaScript, in-app browser verification.

---

### Task 1: Establish deterministic capacity and delivery calculations

**Files:**
- Create: `tests/test_build_implementation_blueprint.py`
- Create: `scripts/build_implementation_blueprint.py`

**Step 1: Write failing calculation tests**

Add tests for a `ScaleAssumptions` dataclass and `calculate_scale()` using the approved defaults. Assert exact relationships rather than formatted strings:

```python
def test_scale_model_counts_dataset_and_api_schema_fields():
    result = builder.calculate_scale(builder.ScaleAssumptions(services=10_000))
    self.assertEqual(result["datasets"], 50_000)
    self.assertEqual(result["dataset_fields"], 1_000_000)
    self.assertGreater(result["api_payload_fields"], result["dataset_fields"])
    self.assertEqual(result["openlineage_events_per_day"], 480_000)

def test_delivery_months_use_effective_engineering_capacity():
    low, high = builder.delivery_month_range(325, 535, engineers=8, utilization=0.65)
    self.assertEqual((low, high), (16, 24))
```

Also test the 25k and 50k scenarios, physical storage multipliers, retention, peak throughput, and invalid zero/negative assumptions.

**Step 2: Run tests to verify failure**

Run: `python3 -m unittest tests.test_build_implementation_blueprint -v`  
Expected: FAIL because the builder module does not exist.

**Step 3: Implement minimal calculation functions**

Create immutable dataclasses for scale and delivery assumptions. Implement:

- `calculate_scale(assumptions) -> dict[str, int | float]`
- `delivery_month_range(low_weeks, high_weeks, engineers, utilization) -> tuple[int, int]`
- `format_bytes(value) -> str`
- input validation with actionable `ValueError` messages

The model must separately calculate dataset fields, API payload fields, canonical edges, evidence assertions, OpenLineage history, and OTel-derived telemetry. Do not append units to values that already contain units.

**Step 4: Run tests to verify passing calculations**

Run: `python3 -m unittest tests.test_build_implementation_blueprint -v`  
Expected: all calculation tests PASS.

**Step 5: Commit calculation foundation**

```bash
git add scripts/build_implementation_blueprint.py tests/test_build_implementation_blueprint.py
git commit -m "test: define Throughline blueprint capacity model"
```

### Task 2: Define the document contract and traceability data

**Files:**
- Modify: `scripts/build_implementation_blueprint.py`
- Modify: `tests/test_build_implementation_blueprint.py`

**Step 1: Write failing document-contract tests**

Test that generated HTML contains:

- all three PRD labels and P0/P1/P2 scope
- the four lenses: Lineage, Interactions, Impact, Provenance
- `INTERACTS_WITH` and `FIELD_FLOWS_TO` with text explicitly preventing automatic conversion
- platform endpoint groups for collection, query, impact, interactions/contracts, and operations
- application endpoint, operation, request/response schema version, and payload-field semantics
- `PRD states`, `Blueprint assumes`, and `Recommended decision` labels
- 10k, 25k, and 50k scenarios
- MVP and full-scope effort ranges
- no `support.js`, React, unpkg, or framework runtime references

Use `html.parser.HTMLParser` to assert a single `main`, unique section IDs, valid internal TOC targets, buttons with accessible names, and all inputs with labels.

**Step 2: Run tests to verify failure**

Run: `python3 -m unittest tests.test_build_implementation_blueprint -v`  
Expected: FAIL because `render_html()` and the content model are incomplete.

**Step 3: Add explicit content data**

Define immutable data for:

- cross-PRD contract and contradiction resolutions
- logical components and deployable groups
- canonical entities and relationship types
- four process flows
- API groups with method, path, purpose, auth scope, sync/async behavior, and proposed SLO
- scale assumptions and scenario presets
- workstreams, MVP/full effort ranges, staffing scenarios, and adapter multipliers
- proposed SLOs, failure modes, risks, and open decisions

Keep source-grounded statements separate from assumptions and recommendations.

**Step 4: Implement the minimal semantic HTML skeleton**

Add `render_html()` and `build(output_path)`. The skeleton must include metadata, skip link, sticky TOC, header, ten approved sections, footer, and no remote runtime dependency.

**Step 5: Run contract tests**

Run: `python3 -m unittest tests.test_build_implementation_blueprint -v`  
Expected: all document-contract tests PASS.

**Step 6: Commit content contract**

```bash
git add scripts/build_implementation_blueprint.py tests/test_build_implementation_blueprint.py
git commit -m "feat: define Throughline blueprint content contract"
```

### Task 3: Build the visual architecture and process-flow sections

**Files:**
- Modify: `scripts/build_implementation_blueprint.py`
- Modify: `tests/test_build_implementation_blueprint.py`

**Step 1: Add failing structural assertions**

Assert that the architecture section includes ingestion, lineage core, query/impact, integrations, experience, and control plane; that every backing store has an ownership/use label; and that each process flow has trigger, ordered stages, failure behavior, and output.

**Step 2: Run the targeted tests**

Run: `python3 -m unittest tests.test_build_implementation_blueprint.BlueprintContentTests -v`  
Expected: FAIL on missing architecture/flow detail.

**Step 3: Implement diagrams with semantic HTML/CSS**

Build:

- a C4-style logical component/deployable diagram
- an assertion-to-projection entity model
- a domain partition and cross-domain boundary-index diagram
- sequence lanes for onboarding/backfill, runtime reconciliation, impact/CI gate, and progressive UI query

Use text labels and ordered structure so diagrams remain meaningful when printed or read by assistive technology.

**Step 4: Add production gap callouts**

Include paired `Prototype shows` / `Production contract adds` callouts for interaction-versus-lineage semantics, endpoint fields, hard-coded impact behavior, scoped graph loading, and evidence/confidence.

**Step 5: Run structural tests**

Run: `python3 -m unittest tests.test_build_implementation_blueprint.BlueprintContentTests -v`  
Expected: PASS.

**Step 6: Commit architecture and flows**

```bash
git add scripts/build_implementation_blueprint.py tests/test_build_implementation_blueprint.py
git commit -m "feat: add Throughline architecture and process flows"
```

### Task 4: Build endpoint, schema, reliability, and operations references

**Files:**
- Modify: `scripts/build_implementation_blueprint.py`
- Modify: `tests/test_build_implementation_blueprint.py`

**Step 1: Add failing endpoint-coverage tests**

Assert presence of representative endpoints and behaviors:

```text
POST /v1/lineage/events
POST /v1/assertions/batches
GET  /v1/entities/{entityId}
GET  /v1/entities/{entityId}/lineage
GET  /v1/interactions/matrix
POST /v1/impact-analyses
GET  /v1/impact-analyses/{analysisId}
POST /v1/impact-analyses/{analysisId}/waivers
POST /v1/replays
GET  /v1/audit-events
```

Test for `Idempotency-Key`, tenant/environment scope, cursor pagination, ETag, `202 Accepted`, problem-details errors, rate limits, policy version, graph snapshot, coverage/truncation, and callback retries.

**Step 2: Run tests to verify failure**

Run: `python3 -m unittest tests.test_build_implementation_blueprint.BlueprintEndpointTests -v`  
Expected: FAIL on incomplete endpoint and reliability coverage.

**Step 3: Implement endpoint cards and payload tabs**

Render filterable endpoint cards grouped by collection, graph/query, impact/review, interactions/contracts, and administration/operations. Add concise JSON examples for an internal assertion, canonical edge, application endpoint schema identity, and asynchronous impact request/result.

**Step 4: Implement reliability and security sections**

Cover workload identity, SSO, RBAC/ABAC, domain/environment/classification scope, encryption, code/LLM safeguards, audit, retention/deletion, data residency, DLQ/quarantine, replay, late data, partial results, backup/restore, RPO/RTO, and explicit CI fail-open/fail-closed policy.

**Step 5: Run endpoint tests**

Run: `python3 -m unittest tests.test_build_implementation_blueprint.BlueprintEndpointTests -v`  
Expected: PASS.

**Step 6: Commit endpoint and operations reference**

```bash
git add scripts/build_implementation_blueprint.py tests/test_build_implementation_blueprint.py
git commit -m "feat: document Throughline APIs and operations"
```

### Task 5: Add interactive scale and delivery planning

**Files:**
- Modify: `scripts/build_implementation_blueprint.py`
- Modify: `tests/test_build_implementation_blueprint.py`

**Step 1: Add failing interaction/static-fallback tests**

Assert that the HTML includes preset buttons for 10k/25k/50k, labeled assumption inputs, formula explanations, a live results region, endpoint filter controls, schema tabs, reduced-motion behavior, and readable static default values when JavaScript is unavailable.

**Step 2: Run tests to verify failure**

Run: `python3 -m unittest tests.test_build_implementation_blueprint.BlueprintInteractionTests -v`  
Expected: FAIL on missing controls and fallback content.

**Step 3: Add framework-free JavaScript**

Implement:

- scenario preset and assumption input recalculation
- accessible live result updates
- endpoint-category filtering
- schema example tabs with keyboard semantics
- optional section disclosure without hiding print content
- active TOC highlighting with graceful fallback

Mirror Python formulas exactly and keep formulas named in one visible assumption block.

**Step 4: Add delivery visualizations**

Show the P0 MVP and full P0/P1/P2 ranges, workstream ranges, critical-path dependency chain, staffing-derived month ranges, and incremental adapter costs. Explain why the source `134-193` engineer-week sum is not the same as a production-ready 24-month plan.

**Step 5: Run interaction tests**

Run: `python3 -m unittest tests.test_build_implementation_blueprint.BlueprintInteractionTests -v`  
Expected: PASS.

**Step 6: Commit interactive planning**

```bash
git add scripts/build_implementation_blueprint.py tests/test_build_implementation_blueprint.py
git commit -m "feat: add interactive Throughline capacity planning"
```

### Task 6: Generate the deliverable and complete automated verification

**Files:**
- Create: `deliverables/Throughline-Implementation-Blueprint.html`
- Modify: `scripts/build_implementation_blueprint.py`
- Modify: `tests/test_build_implementation_blueprint.py`

**Step 1: Add output determinism test**

Build twice into temporary paths and assert byte-identical output. Assert UTF-8, a descriptive `<title>`, viewport metadata, print CSS, no local absolute paths, and no external script dependencies.

**Step 2: Run the test to verify failure if required**

Run: `python3 -m unittest tests.test_build_implementation_blueprint.BlueprintBuildTests -v`  
Expected: FAIL until deterministic metadata and output ordering are complete.

**Step 3: Finalize the builder CLI**

Support:

```bash
python3 scripts/build_implementation_blueprint.py \
  --output deliverables/Throughline-Implementation-Blueprint.html
```

Use a fixed document version/date supplied by the builder, create parent directories, and fail loudly on invalid assumptions.

**Step 4: Generate the final HTML**

Run: `python3 scripts/build_implementation_blueprint.py --output deliverables/Throughline-Implementation-Blueprint.html`  
Expected: the HTML file is created successfully.

**Step 5: Run all automated tests**

Run: `python3 -m unittest discover -s tests -v`  
Expected: all existing and new tests PASS.

**Step 6: Inspect generated-file statistics**

Run: `wc -c deliverables/Throughline-Implementation-Blueprint.html`  
Expected: a non-empty, reasonably sized standalone HTML document.

**Step 7: Commit the generated artifact**

```bash
git add scripts/build_implementation_blueprint.py tests/test_build_implementation_blueprint.py deliverables/Throughline-Implementation-Blueprint.html
git commit -m "docs: add Throughline implementation blueprint"
```

### Task 7: Browser, responsive, and print verification

**Files:**
- Modify if needed: `scripts/build_implementation_blueprint.py`
- Regenerate: `deliverables/Throughline-Implementation-Blueprint.html`

**Step 1: Open the generated file in the in-app browser**

Use the browser-control skill to navigate to the absolute `file://` path or a local HTTP server when browser restrictions require it.

**Step 2: Verify interactions and console state**

Exercise 10k/25k/50k presets, edit assumptions, filter endpoint groups, switch schema tabs, use TOC navigation, and confirm there are no console errors.

**Step 3: Verify responsive layouts**

Inspect at approximately 1440px, 1024px, 768px, and 390px widths. Confirm no horizontal page overflow, clipped diagrams, unreadable code, overlapping sticky navigation, or inaccessible controls.

**Step 4: Verify print presentation**

Use print emulation or print preview. Confirm navigation and controls are suppressed or simplified, all content remains visible, colors preserve contrast, and sections avoid destructive page breaks where practical.

**Step 5: Fix and regenerate as needed**

Apply minimal CSS/JS corrections in the builder, regenerate the artifact, rerun the full test suite, and repeat browser checks until clean.

**Step 6: Final verification**

Run: `python3 -m unittest discover -s tests -v`  
Expected: all tests PASS after the final generated output.

**Step 7: Commit QA fixes if any**

```bash
git add scripts/build_implementation_blueprint.py tests/test_build_implementation_blueprint.py deliverables/Throughline-Implementation-Blueprint.html
git commit -m "fix: polish Throughline blueprint presentation"
```

