# C04 Repository Eligibility and Substrate Routing PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C04 |
| Status | Approved for implementation |
| Launch phase | Foundation and baseline |
| Criticality | P0; prevents silent exclusion and routes analysis to the cheapest trustworthy lane |
| Primary owner | Lineage policy and onboarding team |
| Required approvers | Architecture, product, application governance, analyzer owners |
| Upstream dependencies | C01 identity, C02 inventory, C03 normalized triggers, governed service catalog/policy |
| Downstream dependencies | C05-C11, C14-C15, C17-C18 |
| Authoritative sources | AWS architecture §7 and §9.3; element-level v2 R1/R11/R12; component design §6 |

## 2. Purpose and Outcomes

C04 inventories the meaning of each repository or workload path before costly
analysis. It decides whether the unit produces standalone lineage, acts as a
dependency/trigger, represents contracts or tests, or requires classification
review. For eligible producers it assigns exactly one Lane A, Lane B, or Lane C
as governed data rather than hard-coded control flow.

Measurable outcomes:

- 100% of discovered repository/path units receive an effective classification
  decision or visible `UNKNOWN` review record; zero silent exclusions.
- 100% of eligible producers have exactly one effective lane assignment; a
  missing assignment is an explicit coverage gap.
- Reclassification and override expiry cause the specified downstream action
  without deleting accepted lineage automatically.
- Classification/routing replay with the same evidence/policy version is byte-
  identical.

## 3. Scope and Non-Goals

### In scope

- Repository/workload classification and standalone baseline eligibility.
- Path-level boundaries for `MIXED_MONOREPO`.
- Evidence precedence, rules, reason codes, policy version, expiry, manual
  override, review, and effective decision registry.
- Lane A/B/C substrate assignment per eligible producer/workload.
- Change-transition actions and trigger hints for downstream context/workflows.

### Non-goals

- Discovering inventory evidence (C02).
- Building dependency/consumer/determinant indexes (C05).
- Executing any collector/analyzer (C07-C11).
- Using an LLM to automatically exclude a repository.
- Deleting or deactivating accepted graph state solely because a new decision
  says excluded.
- Treating eligibility as a capacity/sizing shortcut; design capacity remains
  10,000 repositories.

## 4. Actors and Use Cases

| Actor | Use case |
|---|---|
| Application owner | Review unknown/conflicting classification and provide governed evidence |
| Governance administrator | Define policy/routing table and time-bounded override |
| C05 context builder | Know whether to analyze, index consumers/bindings/contracts/tests, or wait for review |
| C06 orchestrator | Route eligible units to Lane A/B/C and trigger transition actions |
| Analyzer owner | Add an archetype/lane only after capability and contract readiness |
| Auditor/operator | Reproduce a decision and understand excluded/unknown/stale counts |

Primary cases:

1. Spring Boot Kafka service -> `APPLICATION_RUNTIME`, Lane A.
2. Spark SQL or dbt project -> `DATA_PIPELINE`, Lane B.
3. Vendor binary without readable source/native plan -> eligible workload,
   Lane C advisory.
4. Shared library -> no standalone baseline, but index consumers and selectively
   reanalyze them on relevant change.
5. Documentation repository with Avro/OpenAPI ->
   `CONTRACT_SCHEMA_SOURCE`, not pure documentation.
6. Monorepo -> path-level application, infrastructure, library, and docs units.

## 5. Component Boundary

### Owned behavior

- `RepositoryEligibilityDecision` generation, review, registry, and transitions.
- Versioned classification policy, evidence precedence, and lane routing table.
- Explanation/reason/evidence and explicit coverage gaps.

### Inputs

- C02 repository/path/manifests/deployment/schema/test/context observations.
- C01 canonical identities and registry version.
- Governed catalog metadata and manual decision/override.
- Prior effective decision and current policy version.

### Outputs

- Immutable eligibility decision plus effective DynamoDB registry entry.
- Class/lane/transition action event for C05/C06/C14.
- UNKNOWN/conflict/expired-override review item.

### Forbidden behavior

- Defaulting `UNKNOWN` to documentation/excluded or inferring exclusion from no
  recent deployment.
- Assigning multiple effective lanes to one producer/workload.
- Hard-coding routing in analyzer/orchestrator deployment code.
- Letting heuristic/LLM evidence outrank governed metadata or auto-exclude.
- Deleting current lineage when included becomes excluded.
- Using interaction context alone to classify a field-level lineage producer.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C04-FR-001 | C04 must assign exactly one repository/path classification: `APPLICATION_RUNTIME`, `DATA_PIPELINE`, `CONTRACT_SCHEMA_SOURCE`, `SHARED_LIBRARY`, `INFRASTRUCTURE`, `DOCUMENTATION`, `TEST_AUTOMATION`, `MIXED_MONOREPO`, or `UNKNOWN`. | P0 |
| C04-FR-002 | Every C02 repository must receive an immutable decision/evidence/reason or explicit `UNKNOWN`; no repository may be silently omitted from the eligibility registry. | P0 |
| C04-FR-003 | Classification must apply evidence precedence: governed catalog/repository metadata, Test Automation association, CI/CD deployable artifact, deterministic manifests/structure, SBOM/dependency evidence, CloudWatch association, then heuristics requiring review. | P0 |
| C04-FR-004 | An LLM may propose a classification but must not automatically exclude, override higher-precedence evidence, or activate a decision. | P0 |
| C04-FR-005 | `APPLICATION_RUNTIME` and `DATA_PIPELINE` must be eligible for standalone baseline/incremental analysis; `CONTRACT_SCHEMA_SOURCE` must receive metadata-only treatment and trigger connected producers/consumers. | P0 |
| C04-FR-006 | `SHARED_LIBRARY`, `INFRASTRUCTURE`, `DOCUMENTATION`, and `TEST_AUTOMATION` must not run standalone lineage, but must emit the specified consumer/binding/no-impact/test-coverage action for C05/C06. | P0 |
| C04-FR-007 | A repository containing authoritative OpenAPI, AsyncAPI, Avro, Protobuf, JSON Schema, or equivalent governed contract must not be classified as pure `DOCUMENTATION` for those paths. | P0 |
| C04-FR-008 | A repository containing independently deployable and excluded units must be `MIXED_MONOREPO` with nonoverlapping governed path units and a catch-all/unknown rule. | P0 |
| C04-FR-009 | Every eligible producer/workload must have exactly one effective Lane A, Lane B, or Lane C assignment; no assignment must be surfaced as a blocking coverage gap. | P0 |
| C04-FR-010 | The baseline lane table must route Spark SQL, dbt, and Airflow-orchestrated SQL to Lane B; Spring Boot, FastAPI, and Dask custom code to Lane A; and workloads with neither readable source nor authoritative native plan to Lane C. | P0 |
| C04-FR-011 | Lane assignment and classification policy must be versioned data; reassigning an archetype/producer must not require a platform deployment. | P0 |
| C04-FR-012 | Manual overrides must name decision, scope, evidence, reviewer, rationale, effective/expiry, and prior policy; expiry must automatically re-evaluate rather than silently extend. | P0 |
| C04-FR-013 | An excluded-to-included transition must request baseline; included-to-excluded must require review/undeployment confirmation and keep current graph marked stale until governed change. | P0 |
| C04-FR-014 | Documentation-to-contract, library-to-deployable, and known-to-unknown/conflicting transitions must emit the specified re-evaluation/ownership/stale actions and preserve history. | P0 |
| C04-FR-015 | Decisions must be deterministic for identical inventory/evidence, policy, C01 registry, and prior-decision versions and must expose all rules/evidence used. | P0 |
| C04-FR-016 | C04 must support preview mode showing decision/transition deltas before policy activation across a representative estate snapshot. | P1 |

### Classification behavior

| Classification | Standalone baseline | Change behavior |
|---|---:|---|
| `APPLICATION_RUNTIME` | Yes | Incremental lineage |
| `DATA_PIPELINE` | Yes | Incremental plus native lineage |
| `CONTRACT_SCHEMA_SOURCE` | Metadata only | Re-evaluate connected producers/consumers |
| `SHARED_LIBRARY` | No | Resolve consumers and selectively reanalyze |
| `INFRASTRUCTURE` | No | Evaluate lineage-relevant bindings/routes/config |
| `DOCUMENTATION` | No | Record `NO_LINEAGE_IMPACT` unless machine contract path |
| `TEST_AUTOMATION` | No | Update coverage/test mapping and runtime freshness |
| `MIXED_MONOREPO` | Per path | Route each path unit |
| `UNKNOWN` | Never silently excluded | Quarantine/review, then replay |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C04-NFR-001 | Classifying a standard repository decision must complete within 500 ms p95 excluding human review; 10,000 decisions must complete within 15 minutes at planned concurrency. | P0 |
| C04-NFR-002 | Policy evaluation must be deterministic and byte-identical across repeated runs; rules may not depend on wall-clock time except explicit effective/expiry input. | P0 |
| C04-NFR-003 | The effective registry must be 99.95% available monthly with immutable history and PITR; C06 may use a pinned last-good decision only when marked stale and policy permits. | P0 |
| C04-NFR-004 | Policy preview must enumerate 100% of decision/lane/transition changes for the evaluated snapshot and produce no active side effect. | P1 |

## 7. Data and Durable State

`RepositoryEligibilityDecision` fields:

- decision ID/version, organization, repository canonical/native ID.
- workload/path unit ID, root/include/exclude patterns, build/deploy descriptor.
- classification and standalone behavior.
- eligible producer/archetype and lane (`A`, `B`, `C`, or absent coverage gap).
- reason codes and ranked evidence references.
- application/domain/owner and dependency action hints.
- policy/C01/inventory/prior decision versions.
- effective/expiry, manual override/reviewer/rationale.
- status: `PROPOSED`, `REVIEW_REQUIRED`, `ACTIVE`, `STALE`, `SUPERSEDED`, or
  `EXPIRED`.
- deterministic input/output checksums and reconciliation time.

`EligibilityPolicy` contains typed rules, source/evidence precedence, class and
lane tables, path matching rules, ambiguity thresholds, required review cases,
transition actions, owner, semantic version, effective time, and checksum.

S3 keeps immutable decisions/policies/previews. DynamoDB provides the effective
repository/path registry and application/class/lane/review indexes.

## 8. Interfaces and Contracts

### Evaluate one repository

`POST /v1/eligibility:evaluate` accepts inventory snapshot reference/checksum,
repository ID, optional prior decision, policy/C01 versions, and dry-run. It
returns a decision proposal plus transition actions. It never activates a
review-required decision.

### Batch evaluation/preview

`POST /v1/eligibility:evaluateBatch` accepts an S3 manifest of repositories and
returns an S3 result manifest/counts/deltas. Step Functions Distributed Map
controls concurrency; no 10,000-item body enters API/workflow state.

### Review/activate

- `POST /v1/eligibility-decisions/{id}/review` records approve/correct/reject
  under expected decision version.
- `POST /v1/eligibility-policies/{version}:activate` requires preview summary,
  compatibility/contract tests, approval, and expected active policy.
- Events: `eligibility.decision.activated`, `eligibility.review.requested`,
  `eligibility.override.expiring`, `eligibility.transition.required`.

## 9. Processing and State Model

```text
EVIDENCE_READY -> EVALUATING -> PROPOSED
                              -> REVIEW_REQUIRED
PROPOSED/REVIEW_REQUIRED -> ACTIVE -> STALE -> SUPERSEDED
                                  \-> EXPIRED -> EVALUATING
```

Algorithm:

1. Pin inventory/C01/policy/prior versions and validate source completeness.
2. Identify deterministic workload boundaries from build manifests, deployment
   descriptors, container definitions, project boundaries, and path policy.
3. Evaluate all evidence by precedence. A lower tier cannot overturn a decided
   higher tier; contradictory highest-tier evidence requires review.
4. Select class and reason. For mixed repository, validate nonoverlap and
   catch-all behavior, then evaluate path units.
5. For eligible producers, apply lane routing data. Multiple matching lanes or
   no match yields review/coverage gap, not arbitrary selection.
6. Compare prior effective decision and produce transition actions.
7. Canonically serialize/checksum; auto-activate only deterministic policies
   explicitly allowed by governance. Preserve every proposal/history.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `INSUFFICIENT_EVIDENCE` | `INCOMPLETE` | Return `UNKNOWN`; request owner/review; never exclude |
| `CLASSIFICATION_CONFLICT` | `CONFLICT` | Preserve top evidence claims; review required |
| `LANE_UNASSIGNED` | `INCOMPLETE` | Explicit coverage gap; block eligible workload completion |
| `LANE_MULTIPLE_MATCH` | `CONFLICT` | No route; policy review with matching rules |
| `MONOREPO_PATH_OVERLAP` | `DETERMINISTIC_INVALID` | Reject decision/policy; identify overlapping units |
| `POLICY_VERSION_INVALID` | `DETERMINISTIC_INVALID` | Quarantine request; do not use implicit latest |
| `OVERRIDE_EXPIRED` | `INCOMPLETE` transition | Mark stale, re-evaluate, notify owner |
| `REGISTRY_WRITE_CONFLICT` | `TRANSIENT` or `CONFLICT` | Retry same expected version or recompute against new prior |
| `POLICY_ENGINE_UNAVAILABLE` | `TRANSIENT` | Bounded retry; optional pinned last-good stale behavior by policy |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C04-SEC-001 | Policy activation, manual override, included-to-excluded approval, and decision correction must require enterprise identity, scoped governance role, rationale, evidence, and audit. | P0 |
| C04-SEC-002 | Decision/evidence reads must enforce organization/domain RBAC and sensitive metadata ABAC; heuristic/LLM evidence must not contain repository secrets or payloads. | P0 |
| C04-SEC-003 | Policy/decision artifacts and effective registry must use KMS, TLS/private access, immutable history/PITR, and separate evaluator/reviewer/activator permissions. | P0 |
| C04-SEC-004 | Policy evaluation must use signed/versioned bundles and reject unregistered code/plugins or arbitrary executable rules. | P0 |
| C04-SEC-005 | Audit must record source evidence IDs/checksums and decisions without copying sensitive evidence bodies. | P0 |

## 12. Scale, Performance, and Availability

- Evaluate up to 10,000 repositories and path-level monorepo units; sizing does
  not assume exclusions.
- Policy evaluation is a pure bounded function over normalized metadata; source
  checkout/SCA is forbidden.
- Batch manifests shard by organization/domain/repository hash and reserve
  capacity for event-driven reclassification.
- Cache key includes inventory content signature, repository/path ID, C01,
  policy, and prior-decision versions. Cache results are invalidated by any
  determinant change.
- Registry history is durable; effective reads are Multi-AZ and restored within
  C18 RPO/RTO.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C04-OBS-001 | Decision counts | class, lane, application/domain, policy version | P0 |
| C04-OBS-002 | Unknown/conflict/lane-gap counts and age | owner, reason, criticality; alert critical active gap | P0 |
| C04-OBS-003 | Override count/expiry | class/lane/owner/reviewer; notify before expiry | P0 |
| C04-OBS-004 | Transition actions | old/new class/lane, action status, affected applications | P0 |
| C04-OBS-005 | Policy preview/activation deltas | changed class/lane/unknown/exclusion counts; audit | P0 |
| C04-OBS-006 | Evaluation latency/cache/error | policy version, archetype, batch/online | P1 |

C17 shows reason/evidence/override/expiry and distinguishes excluded from unknown.
Counts reconcile to the C02 inventory; any missing decision is a P0 alert.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C04-AC-001 | Given one fixture for every class, C04 emits the exact class, standalone behavior, reason/evidence, and transition hint under the baseline policy. |
| C04-AC-002 | Given Spring/FastAPI/Dask, Spark/dbt/Airflow SQL, and opaque vendor workloads, exactly one Lane A, Lane B, and Lane C route respectively is selected as policy data. |
| C04-AC-003 | Given insufficient or conflicting top evidence, C04 returns `UNKNOWN`/review and does not exclude or schedule arbitrary analysis. |
| C04-AC-004 | Given a documentation repository with an authoritative schema path, that path is `CONTRACT_SCHEMA_SOURCE` and connected producer/consumer re-evaluation is requested. |
| C04-AC-005 | Given a mixed monorepo, every changed path maps to exactly one governed workload unit or catch-all unknown; overlaps fail activation. |
| C04-AC-006 | Given an override expiry, C04 marks the decision stale, re-evaluates, notifies/reviews, and never silently extends or deletes active graph state. |
| C04-AC-007 | Given included-to-excluded and library-to-deployable transitions, the required review/undeployment confirmation and ownership/baseline actions are emitted and history is preserved. |
| C04-AC-008 | Given the 10,000-repository fixture, evaluation meets C04-NFR-001 with exact inventory-to-decision reconciliation and deterministic checksums. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C04-CT-001 | Table/unit | One clear fixture per classification | Evaluate | Exact class/behavior/reason | Golden decisions |
| C04-CT-002 | Precedence | Conflicting evidence at different tiers | Evaluate | Highest tier wins; all evidence retained | Rule trace |
| C04-CT-003 | Conflict | Conflicting governed evidence same tier | Evaluate | `CLASSIFICATION_CONFLICT`/review; no active exclusion | Conflict record |
| C04-CT-004 | Lane table | Six baseline archetypes plus opaque source | Route | Exactly expected Lane A/B/C assignment | Routing golden |
| C04-CT-005 | Lane gaps | No lane and multiple matching rules | Route | Explicit gap/conflict; no arbitrary schedule | Gap records |
| C04-CT-006 | Monorepo | Deployable/library/infra/docs paths plus unowned path | Classify paths | Nonoverlapping units; catch-all unknown | Path manifest |
| C04-CT-007 | Contract boundary | Documentation repo with OpenAPI/Avro | Classify | Contract source action, not pure docs | Decision/action |
| C04-CT-008 | Override | Active override reaches expiry | Reconcile | Stale/re-evaluate/notify; no extension/delete | State/audit timeline |
| C04-CT-009 | Transition | All material old->new class transitions | Activate | Exact downstream action table | Transition event set |
| C04-CT-010 | Security | LLM proposes exclude; unauthorized override/policy | Evaluate/apply | Proposal cannot activate; access denied/audited | Policy/audit evidence |
| C04-CT-011 | Determinism/preview | Same snapshot/policy repeated; candidate new policy | Evaluate/preview | Same bytes; exact delta; no active effect | Checksums/registry before-after |
| C04-CT-012 | Load/recovery | 10,000 repositories, monorepo skew, worker restart | Batch evaluate | SLO/reconciliation met; no missing/duplicate decision | Load report/manifests |

## 16. Integration Obligations

- **INT-020 C02↔C04:** all inventory repositories/path evidence produce a
  decision/UNKNOWN and counts reconcile exactly.
- **INT-021 C03↔C04:** duplicate/out-of-order triggers reuse/recompute the
  correct versioned decision without duplicate transition effects.
- **INT-022 C04↔C05:** each class produces the correct application context,
  consumer/binding/contract/test/no-impact indexing instruction.
- **INT-023 C04↔C06/C07-C11:** eligible producers route to exactly one lane;
  excluded/unknown units never execute an incorrect standalone analyzer.
- **INT-024 C04↔C14:** class/lane/policy changes invalidate the correct artifact
  lineage decisions and stale bindings.
- **INT-025 C04↔C15/C17:** unknown/conflict/override/transition review and user
  explanation preserve immutable versions and do not auto-delete lineage.
- **INT-026 C04↔C18:** policy activation/rollback, expiry, reconciliation,
  security audit, load, and Region restore pass operations gates.

## 17. Definition of Done

- Typed eligibility/policy/transition contracts, baseline rule tables, reason
  codes, examples, and effective registry are implemented.
- C04 P0 requirements and C04-CT-001 through C04-CT-012 pass.
- INT-020 through INT-026 pass with production-shaped upstream/downstreams.
- Inventory-to-decision reconciliation proves zero silent exclusions and every
  eligible producer has exactly one lane or visible blocking gap.
- Policy preview/activation/rollback, override expiry, unknown/conflict review,
  and included-to-excluded runbooks are exercised.
- Security tests prove no LLM auto-exclusion, role separation, signed policies,
  evidence isolation, and complete audit.
- The 10,000-repository load report and dashboards/alarms meet SLO/gates.

## 18. Implementation Notes

```text
contracts/schemas/eligibility/
contracts/examples/eligibility/
services/eligibility/
services/eligibility/src/policy/
services/eligibility/src/monorepo/
services/eligibility/src/transitions/
infra/lib/constructs/eligibility-registry.ts
tests/contract/eligibility/
tests/integration/eligibility/
tests/load/eligibility/
```

Use TypeScript 5 for a pure policy evaluator on Lambda and DynamoDB for effective
lookup; S3 stores immutable policies/decisions/previews. Policy is declarative,
typed, signed, and side-effect-free during evaluation. Activation emits actions
through C03; it never invokes analyzers directly.

Implement the baseline class/lane table first, then monorepo paths, overrides/
transitions, preview/activation, and UI/reconciliation. New archetypes enter as
policy plus verified analyzer capability, not a catch-all heuristic.

## 19. Traceability

| Source decision | C04 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Inventory all; no silent exclusion | C04-FR-001 through C04-FR-004 | C04-CT-001/002/003/010 | INT-020/025; baseline gate |
| Class-specific behavior and monorepos | C04-FR-005 through C04-FR-008 | C04-CT-006/007/009 | INT-022/023 |
| Substrate-routed Lane A/B/C as data | C04-FR-009 through C04-FR-011 | C04-CT-004/005/011 | INT-023; analyzer gate |
| Overrides/transitions preserve approved graph | C04-FR-012 through C04-FR-015 | C04-CT-008/009 | INT-024/025/026 |
| Enterprise capacity/determinism | C04-NFR-001 through C04-NFR-004 | C04-CT-011/012 | Enterprise load gate |
| Governance/security | C04-SEC-001 through C04-SEC-005 | C04-CT-010 | INT-025/026; security gate |
