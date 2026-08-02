# C13 Reconciliation, Verification, and Two-Axis Confidence PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C13 |
| Status | Approved for implementation |
| Launch phase | Trust gate before proposal/review |
| Criticality | P0; no collector candidate may reach proposal/publication without C13 outcome |
| Primary owner | Lineage trust and reconciliation team |
| Required approvers | Architecture, analyzer/native/runtime owners, data governance, product/review |
| Upstream dependencies | C01, C05, C07-C12, C15 calibration policy/labels |
| Downstream dependencies | C14-C17, C18 |
| Authoritative sources | Element-level v2 R5-R7 and residual risks; AWS architecture §§11-12, 17-18 |

## 2. Purpose and Outcomes

C13 resolves cross-lane identity, deduplicates candidates without erasing
conflict, applies verification gates G1-G5, returns dropped candidates to named
holes, calculates coverage, and assigns independent structural confidence and
derivational confidence under a calibrated versioned policy. It produces a
deterministic, evidence-complete candidate set for human proposal/review.

Measurable outcomes:

- Every input candidate has a terminal accept/drop/downgrade/conflict/unresolved
  outcome with gate/evidence/reason; zero silent disappearance.
- G1, G2, or G4 failure drops the candidate and opens/returns a hole; G3 or G5
  failure downgrades/flags but does not erase an otherwise real relationship.
- Runtime/OTel evidence never raises derivational confidence; sole-LLM evidence
  never reaches the top band; incomplete runtime never promotes either axis.
- Until labelled calibration exists, both axes render `UNCALIBRATED`; no
  collapsed confidence number is emitted or displayed.

## 3. Scope and Non-Goals

### In scope

- Candidate/evidence normalization and canonical identity/version reconciliation.
- Exact duplicate merge, provenance union, conflict/coverage/hole accounting.
- G1 existence, G2 evidence anchoring, G3 type compatibility, G4 reachability,
  G5 native/opaque oracle agreement with applicability/reason.
- Drop/downgrade/review-routing rules and deterministic output.
- Independent confidence policies, caps, calibration, reason/evidence and
  correction feedback aggregation.

### Non-goals

- Generating missing candidates; verification gate recall is zero by
  construction because a gate cannot test an edge that was never proposed.
- Using one model to judge another model's transform prose as correctness.
- Approving/correcting proposals (C15) or publishing graph (C16).
- Treating human acceptance as execution evidence; it is governed accepted state
  and a calibration label.
- Averaging conflicting evidence or confidence into one float.

## 4. Actors and Use Cases

| Actor/component | Use case |
|---|---|
| C07-C11 | Submit versioned candidate/evidence packages and explicit gaps |
| C08/C09 | Receive gate-dropped candidate as same/open hole with reason |
| C15 reviewer | Inspect gates/evidence/conflicts/coverage and correct proposal |
| Confidence policy owner | Calibrate bands from labels and activate versioned policy |
| C14 | Select deterministic-only/blocking-eligible inputs and freshness behavior |
| Operator | Reconcile input/outcome counts, investigate gate/confidence drift |

## 5. Component Boundary

### Owned behavior

- `VerifiedLineageCandidateSet`, verification policy/gate results, normalized
  conflicts, coverage, returned holes, confidence-axis objects and calibration.

### Inputs

- Immutable C07 native, C08 deterministic, C09 agent, C10 opaque, C11 runtime
  packages; C01 registry, C05 context/determinants, schemas/catalog, accepted
  graph/base version; C15 label/calibration manifests.

### Outputs

- Accepted/downgraded candidates, dropped candidates/returned holes, conflicts,
  unresolved/coverage, gate details, structural/derivational confidence,
  proposal-input manifest/checksum and metrics.

### Forbidden behavior

- Selecting a canonical endpoint when C01 remains ambiguous.
- Keeping a candidate that fails G1, G2, or applicable G4 at low confidence.
- Dropping solely for G3/G5 mismatch without preserving the structurally real
  candidate and conflict/downgrade.
- Promoting from incomplete/stale/mismatched runtime evidence.
- Allowing an LLM self-score, OTel execution, or bulk acceptance to set
  derivational `VERIFIED`.
- Emitting `confidence`, `score`, or a collapsed float in the edge contract.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C13-FR-001 | C13 must validate every input package/reference/schema/checksum and pin C01/context/base graph/verification/confidence/calibration versions before processing. | P0 |
| C13-FR-002 | C13 must resolve source/target/environment/effective version and preserve `IDENTITY_AMBIGUITY`, `VERSION_MISMATCH`, and `SCHEMA_MISMATCH` as conflicts rather than forced merges. | P0 |
| C13-FR-003 | Exact candidates may deduplicate only when canonical source/target, level, environment/effective version, path guard, and transformation identity are compatible; provenance/evidence/determinants/gates are unioned without loss. | P0 |
| C13-FR-004 | Structurally or derivationally disagreeing candidates must remain linked conflict claims; C13 must not average them or discard lower-precedence evidence silently. | P0 |
| C13-FR-005 | G1 existence must verify both endpoint URNs and effective schema/catalog versions resolve; G1 failure must drop the candidate and open/return a hole. | P0 |
| C13-FR-006 | G2 evidence anchoring must re-read every cited immutable file:line/span/fact, verify version/path/range/quote hash and that cited symbols support the asserted mapping; missing/stale/mismatched required citation must drop and return a hole. | P0 |
| C13-FR-007 | G3 type compatibility must apply versioned logical-type/nullability/shape/allowed-conversion policy; failure must retain relationship only as downgraded/type conflict requiring review, not silently drop. | P0 |
| C13-FR-008 | G4 reachability must verify applicable deterministic/agent candidates against C08's pinned call/data-flow/path facts; applicable failure must drop and return a hole. | P0 |
| C13-FR-009 | G5 oracle agreement must compare overlapping candidate claims with C07 exact native or qualified C10 advisory evidence by matching artifact/environment/schema/window; disagreement/absence must downgrade/flag, not drop solely. | P0 |
| C13-FR-010 | Gate applicability must be typed by provenance/candidate class; `NOT_APPLICABLE`, `NOT_OBSERVED`, `PASS`, `FAIL_DROP`, and `FAIL_DOWNGRADE` require a reason/evidence and cannot be used to bypass a required gate. | P0 |
| C13-FR-011 | G1/G2/applicable G4 failure must create a `DroppedCandidate` and restore/open the stable hole with verification reason; counts must reconcile and dropping must never be silent. | P0 |
| C13-FR-012 | G3/G5 failures and governed cheap unsound heuristics (argument/input mismatch, near-identical sibling field) must route downgrade/conflict/human review with explicit risk. | P0 |
| C13-FR-013 | C13 must publish that gate recall is zero by construction and report candidate-conditional gate precision/outcomes separately from lineage recall/coverage. | P0 |
| C13-FR-014 | Every retained edge must carry separate structural confidence and derivational confidence objects with band, reasons, evidence, policy/calibration versions, and calibrated flag; a shared numeric score is prohibited. | P0 |
| C13-FR-015 | Structural confidence may be influenced only by version-matched deterministic reachability, native execution/plan, complete integration runtime execution, deployment binding, and qualified boundary fingerprint agreement under policy. | P0 |
| C13-FR-016 | Derivational confidence may be influenced only by exact C07 native plan/dbt compiled mapping, deterministic transform proof, governed contract test, qualified C10 agreement, and calibrated review labels; OTel/runtime execution must not raise it. | P0 |
| C13-FR-017 | Sole-LLM provenance must remain below the top band on both axes; only independent qualifying oracle/multi-source evidence under calibrated policy may remove the sole-source cap. | P0 |
| C13-FR-018 | Incomplete, truncated, stale, mismatched-artifact/environment, or expired evidence must not promote confidence; it must appear in coverage/gaps. | P0 |
| C13-FR-019 | Until a confidence policy is calibrated against material per-edge C15 labels, all bands must be `UNCALIBRATED`; activation requires corpus/gate metrics, approval, versioning, canary, rollback, and quarterly distribution publication. | P0 |
| C13-FR-020 | C13 must reconcile input candidates, exact duplicates, retained/downgraded/dropped/conflict edges, open/closed/reopened holes, evidence sources, and coverage by application/archetype/provenance. | P0 |
| C13-FR-021 | Identical immutable inputs/policies must produce byte-identical candidate sets/gate/confidence/coverage/checksum; policy change creates a new version and preserves prior result. | P0 |
| C13-FR-022 | C13 should support counterfactual confidence-policy preview against the labelled corpus and current proposals without changing active proposal/graph state. | P1 |

### Gate matrix

| Gate | Claim tested | Fail effect | Not applicable example |
|---|---|---|---|
| G1 | Both canonical versioned endpoints exist | drop/open hole | none for an edge candidate |
| G2 | Required evidence is immutable, current, quote/fact anchored | drop/open hole | Native engine facet uses facet/checksum validation rather than source lines |
| G3 | Source/target logical types/shapes are compatible | downgrade/conflict | Type unknown is `NOT_OBSERVED`, never pass |
| G4 | Applicable source-code path reaches the sink | drop/open hole | Exact native engine plan has native plan proof, not C08 call graph |
| G5 | Independent oracle/opaque overlap agrees | downgrade/conflict | No eligible overlap is `NOT_OBSERVED`, not failure/pass |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C13-NFR-001 | A standard repository candidate package (up to 100k candidates) must reconcile/verify within five minutes p95; a 10M-edge application baseline within two hours at approved Batch scale. | P0 |
| C13-NFR-002 | C13 must scale horizontally without non-deterministic merge ordering and support 500 concurrent repository verification jobs under C06 quotas. | P0 |
| C13-NFR-003 | Trust output/policy service must be 99.9% available monthly; failure leaves immutable inputs/base graph unchanged and does not create a proposal. | P0 |
| C13-NFR-004 | 100 repeated/parallel/cross-Region runs of identical inputs/policy must have zero checksum divergence. | P0 |

## 7. Data and Durable State

`VerificationGateResult` contains gate/version/applicability/status, claim/input,
evidence refs/checksums, observed values, reason, effect, time, verifier version.

`ConfidenceAxis` contains `axis`, band (`UNCALIBRATED` or calibrated enum),
calibrated flag, policy/calibration version, evidence refs, positive/negative/
missing/stale reasons and applicable caps. It has no generic float.

`LineageConflict` typed variants: identity, structure, derivation, type, version,
schema, evidence, oracle. It records all claims/provenance/evidence and
resolution status/rule/reviewer if later resolved.

`CoverageReport` contains expected/analyzed/source/sink/field/candidate counts,
package/evidence completeness, exact duplicates, gates, retained/downgraded/
dropped/conflicts, holes opened/closed/reopened, unsupported/unobserved/stale,
and denominators by provenance/archetype/application/domain.

`VerifiedLineageCandidateSet` contains base graph/context versions, canonical
retained candidates with axes/gates, dropped/returned holes, conflicts,
unresolved/coverage, policy/calibration, immutable input refs and checksum.
C12 stores immutable sets/policies/calibration manifests; DynamoDB indexes run/
cache/status. C15 owns proposal/review labels.

## 8. Interfaces and Contracts

- `POST /v1/verification-runs` accepts checksummed input manifest, base graph/
  C01/context/verification/confidence/calibration versions and idempotency;
  returns run/reference.
- C06 invokes Batch shards over S3 manifest and deterministic reduce/merge.
- `GET /v1/verification-runs/{id}` returns status/counts/references.
- `POST /v1/confidence-policies/{version}:preview|activate|rollback` requires
  labelled corpus/eval/distribution, expected active policy, approval/audit.
- Events: `verification.completed|incomplete|conflict`,
  `verification.candidate.dropped`, `lineage.hole.reopened`,
  `confidence.policy.activated`, `coverage.report.created`.

Outputs to C15 are immutable S3 references/checksums plus summary counts; no
candidate body is placed on EventBridge/Step Functions.

## 9. Processing and State Model

```text
REQUESTED -> INPUT_VERIFY -> IDENTITY_RECONCILE -> DEDUP_CONFLICT
          -> G1 -> G2 -> G3 -> G4 -> G5
          -> HOLE_COVERAGE_RECONCILE -> CONFIDENCE -> CANONICALIZE
          -> PACKAGE_VERIFY -> COMPLETE
```

1. Verify all exact input versions/checksums and reject mixed artifact/
   environment/base versions.
2. Canonicalize identity/path/transform; group exact-compatible candidates,
   preserve conflicts.
3. Apply gates under provenance applicability. Once drop gate fails, record
   remaining gates `NOT_EVALUATED_AFTER_DROP` and return hole; do not hide why.
4. Apply downgrade/review flags and evidence precedence without erasing claims.
5. Reconcile holes/coverage/input-output counts.
6. Calculate axes from allowed evidence and caps using pinned calibration; if
   uncalibrated, band is `UNCALIBRATED` while reasons still show evidence.
7. Canonical sort/serialize/write/read-back and emit one terminal output.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `INPUT_PACKAGE_INVALID_OR_MIXED` | `DETERMINISTIC_INVALID` | Quarantine run; no proposal output |
| `IDENTITY_OR_VERSION_CONFLICT` | `CONFLICT` | Preserve claims; no forced edge merge |
| `G1_ENDPOINT_MISSING` | correctness drop | Drop/reopen hole with endpoint evidence |
| `G2_EVIDENCE_STALE_OR_MISMATCHED` | correctness drop | Drop/reopen hole; no low-confidence edge |
| `G3_TYPE_INCOMPATIBLE` | downgrade/conflict | Retain relationship risk/review unless another drop applies |
| `G4_UNREACHABLE` | correctness drop | Drop/reopen hole with call/data-flow facts |
| `G5_ORACLE_DISAGREEMENT` | downgrade/conflict | Retain risk/review; preserve oracle claim |
| `CONFIDENCE_POLICY_UNCALIBRATED` | `INCOMPLETE` calibration | Emit `UNCALIBRATED`, never guessed bands |
| `NONDETERMINISTIC_OUTPUT` | `DETERMINISTIC_INVALID` defect | Block verifier/policy version; preserve diff |
| `STORE_OR_BATCH_FAILURE` | `TRANSIENT` | Bounded retry/idempotent shard/reduce; no partial proposal |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C13-SEC-001 | Verification workers must use tenant/run-scoped roles for exact C12 evidence/schema/fact/proposal-input prefixes and no graph publication permission. | P0 |
| C13-SEC-002 | Source citations/snippets, schemas, sensitive field metadata, runtime and opaque evidence must enforce domain ABAC/data class and never be copied into broad logs/events/metrics. | P0 |
| C13-SEC-003 | Verification/confidence/calibration policies and activations must be signed/versioned, separated from analyzer producers, reviewed, canaried, rollbackable, and audited. | P0 |
| C13-SEC-004 | Workers run in private encrypted Batch environments with controlled egress, signed images, ephemeral cleanup, and no direct mutable Neptune/OpenSearch access. | P0 |
| C13-SEC-005 | Gate/errors/audit must use allowlisted facts/checksums/reasons; payload values, credentials, sensitive source bodies, and model prompts/transcripts are prohibited. | P0 |

## 12. Scale, Performance, and Availability

- Shard verification by application/repository/artifact and candidate hash while
  keeping conflict/duplicate groups in one deterministic reducer partition.
- Gate fact/schema/oracle reads batch and cache immutable versions; cache key
  includes all input/policy/verifier versions. Integrity/authorization rechecks
  on lookup.
- Use Batch for G1-G5 and merge; Lambda only validates/dispatches small control.
  S3 manifests carry large input/output.
- One large application/domain cannot consume Tier-1 verification capacity;
  C06 admission applies.
- Immutable results/policies replicate; operational index/cache rebuild and
  rerun from C12 supports RPO/RTO. Current graph remains unchanged on failure.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C13-OBS-001 | Candidate input/dedup/retained/drop/downgrade/conflict | provenance/archetype/app/policy | P0 |
| C13-OBS-002 | G1-G5 applicability/pass/fail/effect | gate/reason/provenance/verifier version | P0 |
| C13-OBS-003 | Holes opened/closed/reopened and coverage | reason/archetype/analyzer/app/owner | P0 |
| C13-OBS-004 | Structural/derivational band/cap/distribution | evidence/provenance/policy/calibration | P0 |
| C13-OBS-005 | Incomplete/stale/mismatched evidence | component/type/artifact/environment/owner | P0 |
| C13-OBS-006 | Verification versus human correction | provenance/archetype/gate/model/analyzer/policy | P0 |
| C13-OBS-007 | Determinism/latency/resource/cache/cost | shard/reducer/app/version | P0 |

Dashboards label gate metrics candidate-conditional and display the recall-zero
limitation. Correction rates use per-edge material labels; bulk unreviewed is
not accuracy evidence.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C13-AC-001 | Given exact duplicates from multiple collectors, C13 emits one compatible edge with all provenance/evidence/determinants and no lost claim. |
| C13-AC-002 | Given G1, G2, or applicable G4 failure, candidate is absent from retained set, a dropped record and same/open hole exist, and counts reconcile. |
| C13-AC-003 | Given only G3 or G5 failure, structurally supported candidate remains downgraded/conflicted for review with no top-band promotion. |
| C13-AC-004 | Given complete runtime/OTel evidence, structural may increase and derivational is unchanged; incomplete/stale/mismatched evidence changes neither axis and appears as gap. |
| C13-AC-005 | Given exact Lane B mapping, native edge may be derivational oracle; its observation of a Lane A-produced field corroborates producer structure only, not producer derivation. |
| C13-AC-006 | Given sole-LLM or Lane C-only candidate, policy caps top bands/enforcement; no self-score or runtime changes cap incorrectly. |
| C13-AC-007 | Given no approved calibration, both axes are `UNCALIBRATED`; given labelled policy activation, expected independent bands/reasons/distribution result and collapsed score remains absent. |
| C13-AC-008 | Load/determinism/recovery meet NFRs with exact input/outcome/hole/coverage reconciliation and zero checksum divergence. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C13-CT-001 | Dedup/conflict | Compatible duplicates plus structural/derivation/version conflicts | Reconcile | Exact merge or linked conflict, all claims retained | Candidate/conflict golden |
| C13-CT-002 | G1 | Existing/missing/ambiguous/versioned endpoints | Verify | Pass or drop/open hole; no forced identity | Gate/outcome |
| C13-CT-003 | G2 | Valid, moved/stale quote, wrong version/path/range, missing citation | Verify | Pass or drop/open hole | Reread/quote report |
| C13-CT-004 | G3 | Compatible cast, incompatible type/shape/nullability, unknown | Verify | Pass/downgrade/not observed exactly | Type matrix |
| C13-CT-005 | G4 | Reachable/unreachable/applicability native versus source | Verify | Pass/drop or typed not applicable | Graph/gate evidence |
| C13-CT-006 | G5 | Agree/disagree/no overlap/mismatched scope native/opaque | Verify | Pass/downgrade/not observed; no drop solely | Oracle matrix |
| C13-CT-007 | Gate combinations | Pairwise/all fail combinations | Verify | Drop precedence and remaining gate status exact; no lost reason | Combination matrix |
| C13-CT-008 | Confidence axes | Deterministic/native/LLM/runtime/opaque/human evidence combinations | Calculate | Independent allowed effects/caps; no shared float | Policy golden |
| C13-CT-009 | Runtime boundary | Complete/incomplete/truncated/stale/mismatched runtime | Calculate | Structural only for complete; derivational never; gaps exact | Confidence/coverage |
| C13-CT-010 | Calibration | No labels, material labels, bulk unreviewed, policy canary/rollback | Calculate/activate | Uncalibrated or expected bands; bulk excluded | Calibration report |
| C13-CT-011 | Determinism/security | Random input/shard order, sensitive citations, unauthorized domain | Verify repeatedly/access | Same bytes; ABAC deny/redacted logs | Checksums/security scan |
| C13-CT-012 | Load/recovery | 100k package, 10M app, 500 concurrency, failure/Region restart | Verify/recover | NFR/RPO/RTO/exact reconciliation/no partial proposal | Load/DR report |

## 16. Integration Obligations

- **INT-086 C01/C05↔C13:** canonical identity/environment/version/schema/
  determinants/base graph pin and ambiguity/conflict behavior pass.
- **INT-087 C07↔C13:** native exact oracle, unresolved/coverage, duplicate,
  artifact/environment, and Lane A producer asymmetry pass.
- **INT-088 C08/C09↔C13:** deterministic proof/hole/citation/tools undergo
  G1/G2/G4; drop reopens same hole and LLM caps/feedback are exact.
- **INT-089 C10↔C13:** advisory scope/abstention/G3/G5/cap/nonmatch/expiry never
  produces top band or blocking eligibility alone.
- **INT-090 C11↔C13:** complete versus incomplete runtime affects structural
  only and interaction alone is not lineage.
- **INT-091 C13↔C14/C15:** deterministic-only blocking selection, immutable
  proposal inputs, before/after gates/conflicts/coverage and review labels feed
  calibration without circular self-validation.
- **INT-092 C13↔C17:** UI/API render both axes, evidence/gates/caps/holes/conflicts/
  coverage and recall limitation; single score absent.
- **INT-093 C13↔C18:** policy security, deterministic/load/chaos, reconciliation,
  calibration drift, audit and DR runbooks/gates pass.

## 17. Definition of Done

- Candidate/group/conflict/coverage contracts, deterministic merge, G1-G5,
  drop/downgrade/hole reconciliation, two-axis policy/calibration, immutable
  output/cache, and telemetry are implemented.
- C13 P0 requirements and C13-CT-001 through C13-CT-012 pass.
- INT-086 through INT-093 pass with production-shaped C07-C12 and C14-C17.
- Gate combination/recall limitation and every confidence evidence combination
  have golden results; no schema/UI/API contains collapsed score.
- Labelled calibration/canary report proves bands/distributions or system remains
  visibly `UNCALIBRATED`; no unsupported enforcement advancement.
- Load/determinism/security/recovery reports meet NFRs, exact reconciliation,
  zero checksum divergence, ABAC/no-sensitive-log, and no partial proposal.
- Gate/policy/calibration/conflict/reconciliation/rollback/DR runbooks and alarms
  are exercised with real IDs.

## 18. Implementation Notes

```text
contracts/schemas/verification/
contracts/schemas/confidence/
workers/verifier/
workers/verifier/gates/
workers/verifier/confidence/
services/confidence-policy/
infra/lib/constructs/verification-jobs.ts
tests/fixtures/verification-microworld/
tests/contract/verification/
tests/integration/verification/
tests/load/verification/
tests/security/verification/
```

Use Python 3.12 for deterministic verification/confidence workers, TypeScript 5
for policy/control/IaC. Implement gates as pure versioned functions returning
typed results, not exceptions or side effects. Canonical merge/sort is stable
and uses exact rational/decimal or policy bands, never floating-point summation
over unordered inputs.

Build order: contracts/microworld; identity/dedup/conflict; G1-G5 one at a time;
hole/coverage reconciliation; uncalibrated axes/caps; C15 labels/calibration;
C14/C17; load/security/DR. Rollback activates prior immutable policy for new
runs; prior output/proposals retain their original policy/version.

## 19. Traceability

| Source decision | C13 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Five verification gates/drop versus downgrade | C13-FR-005 through C13-FR-013 | C13-CT-002 through C13-CT-007 | INT-087-091; verification gate |
| Cross-lane reconciliation/conflict | C13-FR-001 through C13-FR-004/020/021 | C13-CT-001/011/012 | INT-086-090 |
| Independent confidence/evidence/caps | C13-FR-014 through C13-FR-019 | C13-CT-008-010 | INT-087-092; calibration gate |
| Scale/determinism/security/recovery | C13-NFR-001-004; C13-SEC-001-005 | C13-CT-011/012 | INT-093; enterprise/security/DR gates |
