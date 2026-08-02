# Lineage Collection Component PRD Package Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create and mechanically validate an implementation-ready PRD for each component of the approved end-to-end AWS lineage collection platform, plus the contracts, integration tests, traceability, and handoff material a coding agent needs to build it.

**Architecture:** Organize requirements around 18 capability-bounded components rather than AWS services. Put shared identity, contracts, state/error semantics, fixtures, integration boundaries, end-to-end gates, and build sequencing in common specifications; require every P0 requirement to trace to component and integration evidence.

**Tech Stack:** Markdown specifications, Mermaid diagrams, Python 3.12 documentation validators, pytest, JSON/JSON Schema and OpenAPI design conventions, AWS EventBridge/SQS/Step Functions/Batch/Bedrock/AppConfig/CloudWatch/Kinesis/S3/DynamoDB/Neptune/OpenSearch architecture.

---

## Execution Rules

- Read `docs/plans/2026-08-02-lineage-component-prd-package-design.md` first.
- Preserve untracked `docs/lineage-approach/` files; treat them as source material.
- Use stable IDs: `Cnn-FR-nnn`, `Cnn-NFR-nnn`, `Cnn-SEC-nnn`, `Cnn-OBS-nnn`, `Cnn-AC-nnn`, `Cnn-CT-nnn`, and `INT-nnn`.
- Do not introduce unresolved `TBD`, `TODO`, or `FIXME` placeholders.
- Every component PRD includes all 19 sections required by the approved design.
- Every component test names fixture, precondition, action, expected result, and retained evidence.
- Every integration test names participating components, injected condition, pass rule, and retained evidence.
- Run documentation validation after every component group and `git diff --check` before each commit.
- Stage only files created by this plan.

## Task 1: Create the Documentation Validator and Failing Skeleton Test

**Files:**
- Create: `tests/test_component_prds.py`
- Create: `docs/component-prds/README.md`

**Step 1: Write the failing package-completeness test**

Define `EXPECTED_COMPONENTS` for component IDs C01-C18 and their exact file
names. Define `EXPECTED_SHARED` for the eight shared documents. Add tests that
assert:

- All expected files exist.
- Each PRD title contains its component ID and name.
- Every PRD includes Purpose, Scope and Non-Goals, Actors and Use Cases,
  Boundary, Functional Requirements, Data and State, Interfaces, Processing,
  Failure Semantics, Security and Privacy, Scale and Performance,
  Observability, Acceptance Criteria, Component Tests, Integration
  Obligations, Definition of Done, Implementation Notes, and Traceability.
- No package file contains `TBD`, `TODO`, or `FIXME`.
- Requirement and test IDs are globally unique.
- Every P0 requirement appears in the traceability matrix.
- README links resolve to real files.

Use this core structure:

```python
from pathlib import Path
import re

ROOT = Path(__file__).parents[1]
PRD_ROOT = ROOT / "docs" / "component-prds"

ID_RE = re.compile(r"\b(?:C\d{2}-(?:FR|NFR|SEC|OBS|AC|CT)-\d{3}|INT-\d{3}|E2E-\d{3})\b")
PLACEHOLDER_RE = re.compile(r"\b(?:TBD|TODO|FIXME)\b", re.IGNORECASE)
```

**Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_component_prds.py -v`

Expected: FAIL because component and shared documents do not exist.

**Step 3: Add the package index**

Write README purpose, authority order, package map, reading paths for product,
implementation, QA, security, and operations, global conventions, completion
definition, and links to all planned files.

**Step 4: Run focused index tests**

Run: `python -m pytest tests/test_component_prds.py -v -k readme`

Expected: PASS for index syntax/link cases; package-completeness remains FAIL.

**Step 5: Commit**

```bash
git add tests/test_component_prds.py docs/component-prds/README.md
git commit -m "test: define component PRD package contract"
```

## Task 2: Define System Context, Shared State, and Contract Catalog

**Files:**
- Create: `docs/component-prds/00-system-context-and-architecture.md`
- Create: `docs/component-prds/shared/contract-catalog.md`
- Create: `docs/component-prds/shared/state-and-error-model.md`

**Step 1: Add failing assertions**

Assert the documents name all 18 components, all canonical artifacts, the
baseline/incremental/runtime flows, authority boundaries, compatibility rules,
the five error classes, and platform invariants.

**Step 2: Verify failure**

Run: `python -m pytest tests/test_component_prds.py -v -k 'system_context or contract_catalog or state_error'`

Expected: FAIL because the files are absent.

**Step 3: Write the shared specifications**

Specify canonical URNs, environments and effective versions; every event and
artifact in the approved design; schema/version/checksum rules; producer and
consumer ownership; state transitions; transient/deterministic/incomplete/
conflict/poison behavior; retry, quarantine, DLQ, redrive, replay, and audit.

**Step 4: Verify**

Run: `python -m pytest tests/test_component_prds.py -v -k 'system_context or contract_catalog or state_error'`

Expected: PASS.

**Step 5: Commit**

```bash
git add docs/component-prds/00-system-context-and-architecture.md docs/component-prds/shared/contract-catalog.md docs/component-prds/shared/state-and-error-model.md tests/test_component_prds.py
git commit -m "docs: define lineage system contracts and state model"
```

## Task 3: Author C01 Canonical Contracts, URNs, and Identity Resolution

**Files:**
- Create: `docs/component-prds/01-canonical-contracts-and-identity.md`
- Modify: `docs/component-prds/shared/contract-catalog.md`

**Steps:**

1. Add a failing C01 completeness/traceability assertion.
2. Run `python -m pytest tests/test_component_prds.py -v -k c01`; expect FAIL.
3. Specify canonical URN syntax, aliases, environment/version identity,
   resolution precedence, ambiguous/conflict behavior, schema registry,
   compatibility, and identity test fixtures. Include component, property,
   collision, compatibility, idempotency, security, load, and C01↔C02/C07/
   C08/C11/C13/C16 integration tests.
4. Re-run the focused test; expect PASS.
5. Commit C01 and its test changes with `docs: specify canonical lineage identity`.

## Task 4: Author C02 Source Adapters and Repository Inventory

**Files:**
- Create: `docs/component-prds/02-source-adapters-and-inventory.md`

**Steps:**

1. Add a failing C02 completeness/traceability assertion.
2. Run the focused test; expect FAIL.
3. Specify SCM, Test Automation, deployment, schema/catalog, native-lineage,
   CloudWatch-context, and catalog adapters; pagination, rate limits,
   watermarking, immutable snapshots, reconciliation, missing sources, and the
   10,000-repository inventory target. Include contract, partial-inventory,
   duplicate, throttling, permission, reconciliation, and scale tests.
4. Re-run; expect PASS.
5. Commit with `docs: specify source adapters and inventory`.

## Task 5: Author C03 Event Intake, Normalization, and Priority Queues

**Files:**
- Create: `docs/component-prds/03-event-intake-and-queues.md`

**Steps:**

1. Add and run a failing C03 assertion.
2. Specify authentication, normalized envelopes, SCM/deployment idempotency
   identities, missing-identity quarantine, EventBridge routing/archive,
   priority SQS/DLQs, coalescing versus deduplication, admission control, replay,
   and 10,000-event burst/100 events-per-second targets.
3. Include duplicates, out-of-order, malformed, poison, replay, queue fairness,
   observability, and load tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify event intake and priority queues`.

## Task 6: Author C04 Eligibility and Substrate Routing

**Files:**
- Create: `docs/component-prds/04-eligibility-and-substrate-routing.md`

**Steps:**

1. Add and run a failing C04 assertion.
2. Specify all repository classes, evidence precedence, path-level monorepo
   classification, Lane A/B/C assignment as data, override expiry,
   reclassification transitions, UNKNOWN quarantine, and never-silent
   exclusion.
3. Include table-driven class/lane tests, ambiguity tests, override expiry,
   reclassification, no-auto-delete, and C02/C03/C05/C06 integrations.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify eligibility and substrate routing`.

## Task 7: Author C05 Context, Dependency, and Determinant Indexes

**Files:**
- Create: `docs/component-prds/05-context-dependency-and-determinants.md`

**Steps:**

1. Add and run a failing C05 assertion.
2. Specify application-context snapshots, association precedence, library
   consumers, infrastructure bindings, contracts, test mappings, files,
   symbols, schemas, configuration keys, dependency versions, reverse indexes,
   versioning, staleness, and invalidation algorithms.
3. Include configuration-only changes, library/interface changes, capacity-only
   infrastructure no-impact, contract-source, mixed-path, and full-scan
   divergence tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify context dependencies and determinants`.

## Task 8: Author C06 Orchestration and Scheduling

**Files:**
- Create: `docs/component-prds/06-orchestration-and-scheduling.md`

**Steps:**

1. Add and run a failing C06 assertion.
2. Specify baseline, incremental, runtime, verification, review/publication,
   reconciliation, and projection-rebuild workflows; Step Functions states;
   S3-reference payloads; Batch/Lambda boundaries; retry/catch/finally/redrive;
   concurrency and per-domain fairness; and run-timeline events.
3. Include successful, resumed, cancelled, expired, duplicate, partial, quota,
   starvation, and baseline-under-incremental-load tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify lineage workflow orchestration`.

## Task 9: Author C07 Lane B Native Collectors

**Files:**
- Create: `docs/component-prds/07-lane-b-native-collectors.md`

**Steps:**

1. Add and run a failing C07 assertion.
2. Specify Spark OpenLineage column facets, dbt manifest/catalog parsing,
   Airflow-orchestrated SQL attribution, per-run/digest binding, `select *`
   catalog expansion, unresolved reason codes, oracle rules, duplicates, and
   run completeness.
3. Include exact mapping, UDF unresolved, raw-Jinja prohibition, missing
   catalog, duplicate run, digest mismatch, compatibility, and oracle
   integration tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify lane B native collectors`.

## Task 10: Author C08 Lane A Deterministic Analyzers

**Files:**
- Create: `docs/component-prds/08-lane-a-deterministic-analyzers.md`

**Steps:**

1. Add and run a failing C08 assertion.
2. Specify analyzer package input/output, checkout isolation, supported Spring
   Boot/Kafka and FastAPI/Pydantic archetypes, provable-edge rule, named holes,
   determinant capture, byte-identical output, budgets, unsupported syntax,
   Dask extension point, and content-addressed package reuse.
3. Include golden fixtures, repeatability, hole counting, config-only
   determinants, cross-file reachability, unsupported-language, resource-limit,
   security, and C05/C09/C13 integration tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify deterministic lineage analyzers`.

## Task 11: Author C09 Lane A Agentic Residual Resolver

**Files:**
- Create: `docs/component-prds/09-lane-a-agentic-resolver.md`

**Steps:**

1. Add and run a failing C09 assertion.
2. Specify hole-only operation, approved tools, file:line citations, enterprise
   gateway/CI-only execution, token/turn/time budgets, no-guess timeout,
   content-addressed cache key, deterministic reuse, model/prompt versioning,
   sensitive-context boundaries, and evidence emission.
3. Include tool authorization, attempt to rederive resolved work, uncited edge,
   stale quote, timeout, cache hit/miss, model-version change, prompt injection,
   gateway failure, rate-limit, and C08/C13 tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify agentic residual resolution`.

## Task 12: Author C10 Lane C Opaque-Substrate Collector

**Files:**
- Create: `docs/component-prds/10-lane-c-opaque-collector.md`

**Steps:**

1. Add and run a failing C10 assertion.
2. Specify advisory-only fingerprint/statistical inference, schedule,
   privacy-preserving samples, minimum observations, collision/ambiguity,
   labelled precision measurement, environment/digest binding, opt-out, and
   permanent confidence caps.
3. Include true/false match, low-cardinality deny, insufficient sample,
   collision, drift, retention, cross-environment, privacy, and G5 integration
   tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify opaque-substrate advisory collection`.

## Task 13: Author C11 Runtime Session Controller and Sidecar

**Files:**
- Create: `docs/component-prds/11-runtime-session-and-sidecar.md`

**Steps:**

1. Add and run a failing C11 assertion.
2. Specify the full runtime state machine, signed sessions, AppConfig
   validation, READY barrier, schema allowlist, sequence/checksum/manifests,
   CloudWatch-to-validator-to-Kinesis flow, per-sidecar ordering, HMAC lifecycle,
   fail-open application behavior, disable-in-finally, expiry kill switch, and
   production hard-deny.
3. Include lifecycle, forbidden keys, encoded-payload attempts, missing
   sequence/manifest, truncation, sidecar crash, flag-disable failure, expired
   session, cross-account denial, production denial, 10x storm, and no-confidence-
   promotion integration tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify integration runtime evidence`.

## Task 14: Author C12 Immutable Evidence Store and Cache

**Files:**
- Create: `docs/component-prds/12-evidence-store-and-cache.md`

**Steps:**

1. Add and run a failing C12 assertion.
2. Specify S3 prefixes/roles, Object Lock/versioning/checksums, immutable-write
   semantics, content-addressed cache keys, DynamoDB operational indexes,
   retention/legal hold, replication, corruption detection, large-payload
   references, access audit, and cache invalidation by versioned inputs.
3. Include write-once, duplicate-write-same-content, collision, checksum
   mismatch, unauthorized prefix, legal hold, restore, replication lag, cache
   hit/miss, and high-volume tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify immutable evidence and cache`.

## Task 15: Author C13 Reconciliation, Verification, and Confidence

**Files:**
- Create: `docs/component-prds/13-reconciliation-verification-confidence.md`

**Steps:**

1. Add and run a failing C13 assertion.
2. Specify canonical identity merge, deduplication, evidence precedence,
   conflicts, holes/coverage, gates G1-G5, drop versus downgrade rules,
   returned-hole reasons, gate recall limitation, structural/derivational
   drivers and caps, UNCALIBRATED state, policy versioning, and deterministic
   proposal inputs.
3. Include one test per gate and gate combination; exact duplicate/conflict;
   Lane B oracle asymmetry; OTel structural-only; incomplete runtime no-
   promotion; sole-LLM caps; calibration change; and scale tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify reconciliation verification and confidence`.

## Task 16: Author C14 CI Drift, Artifact Binding, and Freshness

**Files:**
- Create: `docs/component-prds/14-ci-artifact-binding-and-freshness.md`

**Steps:**

1. Add and run a failing C14 assertion.
2. Specify PR drift output strings, deterministic-only blocking inputs,
   proposal-artifact behavior, no silent commits, signed digest binding,
   already-built/hotfix support, deployment reconciliation, missing-package
   alerts, two-deploy staleness suppression, determinant incremental checks,
   scheduled full scans, and zero-divergence policy.
3. Include drift/no-drift, prohibited "validated" wording, LLM exclusion,
   emergency deployment, digest mismatch, missing package, stale suppression,
   config-only invalidation, divergence defect, and enforcement-phase tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify CI artifact binding and freshness`.

## Task 17: Author C15 Proposal, Review, and Corpus

**Files:**
- Create: `docs/component-prds/15-proposal-review-and-corpus.md`

**Steps:**

1. Add and run a failing C15 assertion.
2. Specify proposal state machine, before/after diff categories, immutable
   corrections, optimistic concurrency, reviewer authorization, rationale,
   separation of duties, material-edge acknowledgement, bulk-accept
   `unreviewed`, label event schema, correction metrics, 200-edge/six-archetype
   corpus gate, supersession, rejection, and audit.
3. Include state transitions, stale reviewer edit, unauthorized approval,
   correction version, bulk accept, label immutability, metric aggregation,
   corpus gate, backlog SLO, and C13/C16/C17 integrations.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify proposal review and corpus`.

## Task 18: Author C16 Publication and Projections

**Files:**
- Create: `docs/component-prds/16-publication-and-projections.md`

**Steps:**

1. Add and run a failing C16 assertion.
2. Specify accepted-manifest validation, expected-prior-version condition,
   application-scoped reservation, lease/fencing token, immutable target
   namespace, counts/checksums, atomic active-pointer advance, OpenSearch
   watermark, stale-worker denial, rebase/supersede, idempotent redrive,
   projection rebuild, and RPO/RTO.
3. Include normal publish, concurrent proposal, expired lease, stale worker,
   partial Neptune write, checksum failure, OpenSearch lag, redrive, full
   rebuild, and regional restore tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify fenced lineage publication`.

## Task 19: Author C17 Query APIs, Review UI, and Timeline

**Files:**
- Create: `docs/component-prds/17-query-api-review-ui-and-timeline.md`

**Steps:**

1. Add and run a failing C17 assertion.
2. Specify OpenAPI resources, pagination/filtering, bounded traversal, search,
   active-version reads, evidence authorization, before/after review, two-axis
   confidence, provenance, holes/conflicts/coverage, correction interactions,
   run timeline, projection watermark, accessibility, empty/error/stale states,
   and export audit.
3. Include API contract, authz, one-hop p95, query bound, stale projection,
   sensitive metadata, visual states, keyboard/accessibility, concurrent edit,
   timeline retry/redrive, and Playwright steel-thread tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify lineage APIs and review experience`.

## Task 20: Author C18 Security, Observability, Operations, and DR

**Files:**
- Create: `docs/component-prds/18-security-observability-operations-dr.md`

**Steps:**

1. Add and run a failing C18 assertion.
2. Specify account boundaries, IAM/ABAC/RBAC, encryption, private networking,
   secrets/egress, CloudTrail/S3 data audit, retention, no-payload controls,
   common correlation contract, metrics/alarms/dashboards/SLOs, runbooks,
   inventory/deployment/full-scan reconciliation, backup, rebuild, warm standby,
   15-minute RPO/four-hour RTO, chaos, cost allocation, and waiver expiry.
3. Include policy-as-code, cross-account denial, data exfiltration attempts,
   audit completeness, alarm/runbook links, reconciliation drift, DLQ redrive,
   dependency outage, Region failure, projection rebuild, and security/load/
   chaos tests.
4. Run focused validation; expect PASS.
5. Commit with `docs: specify platform security operations and DR`.

## Task 21: Define Dependency Matrix, Test Strategy, and Canonical Fixtures

**Files:**
- Create: `docs/component-prds/shared/dependency-and-integration-matrix.md`
- Create: `docs/component-prds/shared/test-strategy-and-fixtures.md`

**Steps:**

1. Add failing assertions that every component has upstream/downstream rows and
   every boundary has positive, negative, duplicate, compatibility,
   timeout/recovery, and observability tests.
2. Run focused tests; expect FAIL.
3. Define INT-001 onward, canonical pilot/mixed-monorepo/library/
   infrastructure/contract/runtime fixtures, local emulator versus deployed
   test layers, data cleanup, clocks/IDs, fault injection, load profiles,
   production-like environment requirements, evidence retention, and flaky-test
   policy.
4. Run focused tests; expect PASS.
5. Commit with `docs: define lineage integration test matrix`.

## Task 22: Define End-to-End Acceptance Tests

**Files:**
- Create: `docs/component-prds/shared/end-to-end-acceptance-tests.md`

**Steps:**

1. Add failing assertions for the 14 mandatory steel threads in the design.
2. Run focused tests; expect FAIL.
3. Specify each `E2E-nnn` with purpose, components, environment, fixtures,
   preconditions, exact steps, injected failures, pass/fail rules, SLO, security
   assertion, cleanup, and retained evidence. Include the complete mixed-
   application baseline-to-query path and all required negative/recovery/load
   paths.
4. Run focused tests; expect PASS.
5. Commit with `docs: define lineage end-to-end acceptance tests`.

## Task 23: Complete Traceability, Build Sequence, and Coding-Agent Handoff

**Files:**
- Create: `docs/component-prds/shared/requirements-traceability-matrix.md`
- Create: `docs/component-prds/shared/implementation-sequence.md`
- Create: `docs/component-prds/shared/coding-agent-handoff.md`

**Steps:**

1. Add failing assertions that every P0 requirement maps to component test,
   integration test, phase gate, and expected evidence; and that all build
   phases name entry/exit criteria and exact repository targets.
2. Run focused tests; expect FAIL.
3. Populate the matrix, dependency DAG, phase gates, repository layout,
   approved language/runtime choices, contract-first/TDD rules, feature flags,
   local and deployed test commands, environment assumptions, commit cadence,
   non-negotiable invariants, stop/escalate conditions, and final evidence
   checklist.
4. Run focused tests; expect PASS.
5. Commit with `docs: add lineage implementation handoff and traceability`.

## Task 24: Audit and Verify the Complete PRD Package

**Files:**
- Modify as required: `docs/component-prds/**/*.md`
- Modify as required: `tests/test_component_prds.py`

**Step 1: Run structural validation**

Run:

```bash
python -m pytest tests/test_component_prds.py -v
```

Expected: all package, section, ID, placeholder, link, boundary, and
traceability tests PASS.

**Step 2: Run the repository test suite**

Run:

```bash
python -m pytest -v
```

Expected: all existing and new tests PASS.

**Step 3: Run consistency searches**

Run:

```bash
rg -n '\b(TBD|TODO|FIXME)\b' docs/component-prds
rg -n 'single confidence|confidence score|OTel.*derivation|runtime.*proves.*transform' docs/component-prds
git diff --check
```

Expected: placeholder search returns no matches; semantic search returns only
explicit prohibitions/explanations; diff check returns no errors.

**Step 4: Perform requirement-by-requirement audit**

Confirm all explicit source requirements, 18 components, mandatory PRD
sections, component tests, interface tests, 14 steel threads, scale/security/
privacy/resilience gates, implementation sequence, and handoff evidence are
present and mutually consistent. Record any intentional deferral as a scoped
P1/P2 item with observable launch behavior, never as a placeholder.

**Step 5: Commit**

```bash
git add docs/component-prds tests/test_component_prds.py
git commit -m "docs: complete lineage component PRD package"
```

## Completion Evidence

The documentation work is complete only when:

- The index, system context, 18 component PRDs, and eight shared specifications
  exist and link correctly.
- Each component PRD contains all mandatory sections and explicit test criteria.
- Every P0 requirement maps to component, integration, and launch evidence.
- Every producer-consumer boundary has positive and failure-path integration
  coverage.
- The end-to-end suite specifies all mandatory steel threads, including
  production hard-deny, fenced publication, projection rebuild, and enterprise
  load/fairness.
- The coding-agent handoff defines exact build order, repository layout,
  technology choices, commands, invariants, and stop conditions.
- `python -m pytest -v` and `git diff --check` pass.
- The completion audit finds no missing or weakly supported requirement.
