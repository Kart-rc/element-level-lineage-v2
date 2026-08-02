# C10 Lane C Opaque-Substrate Collector PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C10 |
| Status | Approved design; activation follows measured Lane A/B pilot |
| Launch phase | P1/Q3+ advisory only |
| Criticality | Nonblocking for initial launch; P0 controls apply whenever enabled |
| Primary owner | Opaque lineage and privacy engineering team |
| Required approvers | Architecture, privacy/security/legal, data owners, trust-engine owner |
| Upstream dependencies | C01, C04 Lane C route, C05 context/schema/bindings, C06 schedule, approved source-local observation mechanism |
| Downstream dependencies | C12-C13, C15, C17-C18 |
| Authoritative sources | Element-level v2 R5/R6/R11; AWS architecture principles 5-7 and security/privacy controls |

## 2. Purpose and Outcomes

C10 provides privacy-preserving, statistical lineage evidence for vendor,
legacy binary, and other opaque systems with neither readable source nor an
authoritative native plan. It compares source-local irreversible fingerprints
and timing/schema evidence under a governed observation window. Its output is
advisory, never sole proof, and always subject to a confidence cap and C13
verification/human review.

Measurable outcomes:

- Zero raw values, reversible tokens, credentials, or payload bodies leave the
  source-local trust boundary or enter platform storage/logs.
- 100% of emitted relationships include environment/artifact/system/schema/
  window, minimum observation and entropy evidence, ambiguity/collision
  analysis, precision-policy version, and advisory confidence cap.
- Insufficient, low-cardinality, sensitive, ambiguous, collision-prone, stale,
  or cross-environment evidence returns no candidate and an explicit gap.
- Precision/false-positive/false-negative and abstention are measured against a
  labelled sample before any production use or policy expansion.

## 3. Scope and Non-Goals

### In scope

- Lane C onboarding consent/policy, source-local observation job, allowlisted
  schema/field metadata, window-scoped keyed fingerprint aggregation,
  statistical match/ambiguity analysis, privacy checks, advisory candidate
  package, scheduled refresh/expiry, evaluation and audit.

### Non-goals

- Capturing/storing/transmitting raw values or reversible encodings.
- Setting `VERIFIED`, blocking CI/deployment, or auto-publishing an opaque edge.
- Inferring an exact transform expression from correlation.
- Using low-cardinality/sensitive identifiers even if technically hashable.
- Correlating across organizations/environments/windows without an explicitly
  approved scoped policy/key and documented purpose.
- Replacing source remediation/native instrumentation when feasible.

## 4. Actors and Use Cases

| Actor/component | Use case |
|---|---|
| Data/system owner | Enroll an opaque source/sink and approve fields/window/purpose |
| Privacy/security | Review field eligibility, fingerprint/key/retention policy, and evaluation |
| Source-local collector | Compute aggregates without exporting raw values |
| C13 | Use qualified Lane C agreement only as advisory G5 evidence/candidate |
| Reviewer | Inspect support/ambiguity/cap and accept/correct/reject |
| Operator | Detect stale/insufficient/collision/privacy/key failure and revoke collection |

## 5. Component Boundary

### Owned behavior

- Opaque enrollment/capability/consent, source-local compute package, key/window
  policy, match analysis, abstention, expiry, and `OpaqueEvidencePackage`.

### Inputs

- C04 Lane C decision and C05 bindings/schema/field candidates.
- System/environment/artifact/version and authorized observation endpoints.
- Approved field eligibility/classification, key/window/minimum observation,
  precision/ambiguity/retention policy.

### Outputs

- Aggregated nonreversible evidence, advisory candidate(s) or abstention/gap,
  evaluation metrics, immutable package/checksum.

### Forbidden behavior

- Exporting raw values or per-record fingerprints that enable linkage/recovery.
- Hashing without a secret scoped key, or retaining key after the window.
- Fingerprinting low-cardinality or prohibited sensitive fields.
- Selecting one producer/field when support is tied/ambiguous.
- Treating absence of match as proof no path exists.
- Raising either confidence axis to top band from Lane C alone.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C10-FR-001 | C10 must operate only for an effective C04 Lane C workload and an approved enrollment naming owner, purpose, systems/environments/artifacts, fields/schema versions, observation window, and privacy policy. | P0 |
| C10-FR-002 | Field eligibility must deny raw payload/body, credentials/tokens, direct identifiers, prohibited sensitive classifications, low-cardinality values, free text, and any field failing configured entropy/uniqueness/minimum-population thresholds. | P0 |
| C10-FR-003 | Eligible values must be transformed only inside the source-local trust boundary using a window/environment/purpose-scoped keyed HMAC or approved nonreversible primitive; raw values and unscoped hashes must never leave that boundary. | P0 |
| C10-FR-004 | The platform must receive only aggregate sketches/counts and metadata sufficient for governed comparison; per-record fingerprints and key material are prohibited in central evidence. | P0 |
| C10-FR-005 | Fingerprint keys must be issued through KMS/Secrets controls to authorized source-local jobs, never logged/exported, inaccessible after window close/expiry, and nonreusable across unapproved environments/purposes. | P0 |
| C10-FR-006 | Every comparison must require matching organization, approved environment/window/purpose/key-policy, canonical schema/field identity or candidates, artifact/system version, and sufficient overlapping observation interval. | P0 |
| C10-FR-007 | C10 must enforce minimum observation count, field presence, entropy/uniqueness, support, collision probability, temporal alignment, and ambiguity thresholds before emitting an advisory candidate. | P0 |
| C10-FR-008 | Multiple equal/near support candidates, multi-producer ambiguity, collision risk above policy, insufficient sample, stale window, or identity/schema conflict must yield explicit abstention/unresolved and no selected edge. | P0 |
| C10-FR-009 | `OpaqueEvidencePackage` must contain no raw values and must record aggregate support/count/range, ambiguity/collision statistics, field eligibility outcome, policy/key identifier (not key), system/environment/artifact/schema/window, provenance, expiry, and checksum. | P0 |
| C10-FR-010 | Every C10 relationship must be labelled `ADVISORY_OPAQUE`, carry a permanent policy confidence cap below `VERIFIED`, require C13 checks/human review, and be structurally excluded from automated enforcement/blocking inputs. | P0 |
| C10-FR-011 | Fingerprint agreement may contribute bounded derivational/structural evidence under calibrated C13 policy but must not assert an exact transformation or top-band confidence by itself. | P0 |
| C10-FR-012 | Absence/nonmatch must be reported as inconclusive with observation/coverage, never as proof an edge/path does not exist. | P0 |
| C10-FR-013 | C10 must run on a governed schedule/window, expire stale packages, and request recollection when schema, environment, artifact/system, field policy, or binding determinants change. | P0 |
| C10-FR-014 | Precision, false-positive, false-negative, abstention, ambiguous, collision, and privacy-denial rates must be measured on a labelled sample by archetype/system before activation and quarterly thereafter. | P0 |
| C10-FR-015 | A kill switch must revoke active jobs/keys, stop new collection, expire pending evidence, and retain sanitized immutable audit without requiring a platform deployment. | P0 |
| C10-FR-016 | New fingerprint/statistical methods or cross-environment correlation require a new versioned privacy threat model, labelled evaluation, and explicit approval. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C10-NFR-001 | Source-local collection CPU/memory/network overhead must remain below approved per-system budgets and must fail open for the observed application/data job. | P0 |
| C10-NFR-002 | Central analysis must process one million aggregate field-pair candidates within two hours in the production-like batch environment while enforcing abstention/privacy rules. | P0 |
| C10-NFR-003 | Source-local/key/central failures must never expose raw values or interrupt the observed system; they produce incomplete/abstention with audit. | P0 |
| C10-NFR-004 | Immutable approved aggregate evidence must recover within C18 RPO/RTO; destroyed scoped keys must not be restored to make old fingerprints newly linkable. | P0 |

## 7. Data and Durable State

`OpaqueEnrollment` includes organization/domain/owner, source/sink systems,
environment/artifact/schema/fields, purpose/legal/privacy approval, field
classifications, observation/minimum observation/entropy/uniqueness/support/
ambiguity/collision thresholds, key/retention policy, schedule/expiry, collector
version, kill-switch state, and checksum.

`AggregateFingerprintSketch` includes window/system/field canonical/native ID,
schema/artifact/environment, observation/presence/distinct estimates, approved
nonreversible sketch, sketch algorithm/key-policy ID, privacy eligibility, and
checksum. It must be impossible to enumerate individual records from the
contracted representation within the approved threat model.

`OpaqueEvidencePackage` includes compared sketches, overlap/support statistics,
candidate/abstention reasons, ambiguity/collision estimates, coverage,
`ADVISORY_OPAQUE` provenance, confidence cap policy, expiry, evaluation version,
and immutable checksum/reference.

KMS/Secrets holds short-lived key material under source-local job roles. C12 S3
holds only approved aggregates/packages; DynamoDB holds enrollment/job/window/
idempotency/expiry/evaluation indexes.

## 8. Interfaces and Contracts

- `POST /v1/opaque-enrollments` creates reviewed versioned enrollment; activation
  requires privacy/security/data-owner approvals and expected policy version.
- C06 starts `OpaqueCollectionJob` by immutable enrollment/context references.
- Source-local collector returns signed `AggregateFingerprintSketch` by direct
  restricted C12 path or governed cross-account transfer; contract validator
  rejects per-record/generic/raw content.
- `POST /v1/opaque-analysis` accepts source/sink sketch manifests/checksums and
  produces package/abstention by S3 reference.
- `POST /v1/opaque-enrollments/{id}:kill` is idempotent, audited, disables jobs,
  revokes grants/keys, and emits expiry/reconciliation events.
- Events: `opaque.window.started|closed|incomplete`,
  `opaque.evidence.created|abstained|expired`, `opaque.kill-switch.activated`.

## 9. Processing and State Model

```text
DRAFT -> PRIVACY_REVIEW -> APPROVED -> SCHEDULED -> COLLECTING
      -> WINDOW_CLOSED -> ANALYZING -> ADVISORY_READY -> EXPIRED
```

Alternatives: `DENIED`, `INCOMPLETE`, `ABSTAINED`, `FAILED`, `KILLED`.

1. Validate effective Lane C/enrollment/context and source-local attestation.
2. Apply field classification/cardinality/entropy/minimum-population denial
   before fingerprinting; record aggregate denial reason only.
3. Issue window-scoped job grant/key; compute allowed aggregates locally.
4. Validate signed sketch contract/privacy/budgets and persist; close/revoke key
   in finally/expiry.
5. Compare only compatible scoped sketches; calculate support/ambiguity/collision
   and apply conservative thresholds.
6. Emit advisory candidate or explicit abstention, never forced coverage.
7. C13 verifies identity/type/reachability where available and applies cap;
   C15 review/label is required before accepted use.
8. Expire package/recollect on schedule or determinant change.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `FIELD_PRIVACY_INELIGIBLE` | `DETERMINISTIC_INVALID` | Do not fingerprint; aggregate denial reason/audit only |
| `LOW_CARDINALITY_OR_ENTROPY` | `DETERMINISTIC_INVALID` privacy | Deny field; no sketch/raw log |
| `MINIMUM_OBSERVATION_NOT_MET` | `INCOMPLETE` | Abstain; report counts/window |
| `FINGERPRINT_SCOPE_MISMATCH` | `CONFLICT` | Do not compare; identify policy/environment/window mismatch |
| `AMBIGUOUS_OR_COLLISION_RISK` | `CONFLICT`/`INCOMPLETE` | Abstain; preserve aggregate statistics |
| `KEY_EXPIRED_OR_REVOKED` | `DETERMINISTIC_INVALID` | Stop/close incomplete; no reissue under same window identity |
| `SOURCE_LOCAL_COLLECTOR_FAILED` | `INCOMPLETE` | Fail open observed system; audit/alert/recollect if allowed |
| `RAW_OR_PER_RECORD_CONTENT_DETECTED` | `DETERMINISTIC_INVALID` security | Reject before central persistence; revoke/alert/investigate |
| `CENTRAL_STORE_OR_CAPACITY_FAILURE` | `TRANSIENT` | Bounded retry of aggregate package; never request raw fallback |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C10-SEC-001 | Enrollment requires data-owner, privacy, and security approval with purpose limitation, fields/classification, environments, window, retention, threat model, and kill-switch owner. | P0 |
| C10-SEC-002 | Technical controls must prevent raw values, per-record fingerprints, unkeyed/reusable hashes, low-cardinality/sensitive fields, key material, and arbitrary attributes from entering central transport/storage/logs. | P0 |
| C10-SEC-003 | Key grants must be source-local/job/window/purpose/environment scoped, short-lived, nonexportable where supported, audited, and revoked/destroyed on close/expiry/kill. | P0 |
| C10-SEC-004 | Collector/transfer/storage/analysis roles must be separate, least privilege, private/TLS/KMS protected, domain ABAC, and denied access to unrelated enrollment/windows. | P0 |
| C10-SEC-005 | Privacy-contract scanning must inspect schema and aggregate statistical properties without logging prohibited content; violation triggers revoke/quarantine/incident runbook. | P0 |
| C10-SEC-006 | Retention/deletion/legal-hold policy applies to approved aggregates/audit; raw source values remain governed solely by the source system and are never copied for C10. | P0 |

## 12. Scale, Performance, and Availability

- Collection is scheduled/admission-controlled and lower priority than Tier-1
  incremental/native/deterministic work. Per-source budgets protect observed
  systems; backpressure skips/defer windows visibly rather than increasing load.
- Aggregate sketches are bounded by field/window, never record count. Central
  comparison shards by organization/environment/schema candidate partitions and
  uses Batch/S3 manifests.
- Candidate explosion uses conservative prefilters from C05 bindings/schemas;
  an unbounded all-to-all comparison is rejected.
- Kill/revocation path is independent of central analyzer health.
- Cross-Region restores exclude destroyed key material; restored aggregates
  retain original scope/expiry and cannot be linked outside it.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C10-OBS-001 | Enrollment/window/job status | system/domain/environment/owner/policy | P0 |
| C10-OBS-002 | Field eligibility/denial | classification/reason/collector policy; privacy alert | P0 |
| C10-OBS-003 | Observation/support/abstention | system/archetype/reason/window | P0 |
| C10-OBS-004 | Ambiguity/collision/expiry | policy/system/schema/owner | P0 |
| C10-OBS-005 | Raw/per-record/key/scope violation | source/account/job; immediate security alert | P0 |
| C10-OBS-006 | Labelled precision/FP/FN/abstention | system/archetype/policy/evaluation version | P0 |
| C10-OBS-007 | Source overhead/central cost | CPU/memory/network/job/field pairs | P1 |

Metrics never publish fingerprint/sketch content. C17 displays advisory status,
scope/window/support/ambiguity/expiry/evidence and cap, not a misleading exact
probability unless calibrated policy explicitly defines a user-safe statistic.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C10-AC-001 | Given an approved high-cardinality field/window with known match, source-local jobs emit only bounded aggregate sketches and C10 produces an advisory candidate with scope/support/ambiguity/cap. |
| C10-AC-002 | Given raw/per-record content, low-cardinality/sensitive field, unkeyed hash, or key material, validation denies before central persistence and triggers sanitized security evidence. |
| C10-AC-003 | Given insufficient observations, stale window, scope mismatch, tied candidates, multi-producer ambiguity, or collision risk, C10 abstains and emits no selected edge. |
| C10-AC-004 | Given no fingerprint match, C10 reports inconclusive coverage rather than a negative lineage assertion. |
| C10-AC-005 | Given a valid advisory candidate, C13/C15 integration cannot set top band or automated enforcement and requires verification/review. |
| C10-AC-006 | Given kill/expiry/source collector failure, keys/grants stop, observed system continues, pending evidence is incomplete/expired, and no raw fallback occurs. |
| C10-AC-007 | Given labelled positive/negative/ambiguous sample, published precision/FP/FN/abstention exactly match the fixture and gate activation. |
| C10-AC-008 | Scale/recovery meet C10 NFRs and prove restored evidence cannot be linked with destroyed keys or across scope. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C10-CT-001 | Privacy contract | Raw values, per-record hashes, key, arbitrary maps, valid aggregate | Validate transfer | Prohibited rejected before persistence; aggregate accepted | Validator/store scan |
| C10-CT-002 | Field eligibility | Sensitive, free-text, low/high-cardinality fields | Evaluate | Exact denial/eligible outcomes without values in logs | Policy/audit report |
| C10-CT-003 | Positive/negative | Labelled matching/nonmatching high-cardinality aggregate fixtures | Compare | Advisory match or inconclusive nonmatch | Package goldens |
| C10-CT-004 | Minimum observation | Below/at/above count/entropy/uniqueness thresholds | Compare | Abstain or evaluate exactly at boundary | Threshold matrix |
| C10-CT-005 | Ambiguity/collision | Tied, multi-producer, collision-prone sketches | Compare | Abstain; all aggregate candidates/reason retained | Ambiguity report |
| C10-CT-006 | Scope isolation | Different environment/window/purpose/key policy | Compare | `FINGERPRINT_SCOPE_MISMATCH`; no link | Conflict/audit |
| C10-CT-007 | Key lifecycle | Normal close, expiry, kill, attempted reuse/export | Operate | Grant revoked/destroyed, reuse/export denied/audited | KMS/job evidence |
| C10-CT-008 | Fail-open | Collector/transfer/central analysis failure | Execute | Source system succeeds; incomplete/abstain; no raw fallback | Source/job timeline |
| C10-CT-009 | Confidence/enforcement | Advisory candidate alone and with other evidence | Reconcile/policy | Cap enforced; no top band/blocking input | C13/C14 result |
| C10-CT-010 | Evaluation | Labelled true/false/ambiguous/denied corpus | Calculate | Exact precision/FP/FN/abstention with version | Evaluation report |
| C10-CT-011 | Security | Cross-domain role, tampered collector/sketch, privacy violation | Execute | Deny/quarantine/revoke/alert/audit | Security exercise |
| C10-CT-012 | Load/recovery | 1M field-pair candidates, source budgets, restart/Region restore | Collect/analyze/recover | NFRs/overhead/exact counts; scope/expiry intact; key absent | Load/DR report |

## 16. Integration Obligations

- **INT-063 C01/C04/C05↔C10:** only Lane C enrolled compatible
  systems/environment/schema/bindings are compared; identity/scope gaps abstain.
- **INT-064 C06↔C10:** scheduled/admission/budget/fail-open/kill/finally/result
  workflows preserve lower priority and exact status.
- **INT-065 Source-local collector↔C10/C12:** field eligibility, key lifecycle,
  aggregate-only contract, privacy denial, signed transfer, and immutable storage
  prove no raw/per-record/key content.
- **INT-066 C10↔C13:** G1/G3/G5, ambiguity/coverage/expiry, advisory confidence cap,
  nonmatch semantics, and multi-source behavior are exact.
- **INT-067 C10↔C14/C15:** opaque evidence never enters blocking policy;
  review/labels/evaluation gate any accepted advisory use.
- **INT-068 C10↔C17:** UI/API shows advisory/cap/scope/window/support/ambiguity/
  expiry/coverage and sensitive metadata authorization.
- **INT-069 C10↔C18:** privacy incident/kill/key/source failure/load/cost/audit/
  retention/restore runbooks and gates pass.

## 17. Definition of Done

- Enrollment/privacy policy, source-local collector, key lifecycle, aggregate
  contract/validator, comparison/abstention, expiry/kill, evaluation, immutable
  package, and observability are implemented for approved pilot systems.
- C10 P0 requirements and C10-CT-001 through C10-CT-012 pass.
- INT-063 through INT-069 pass in privacy-approved nonproduction environments.
- Independent privacy/security review confirms threat model and no raw/per-
  record/reversible/key content; violation/kill exercise IDs are retained.
- Labelled evaluation publishes precision/FP/FN/abstention/ambiguity and approves
  the cap; no automated enforcement use exists.
- Load/source-overhead/fail-open/recovery reports meet NFRs and prove scope/key
  semantics after restore.
- Owner/kill/privacy/source failure/expiry/rollback/DR runbooks and alarms are
  exercised.

## 18. Implementation Notes

```text
contracts/schemas/opaque-lineage/
sidecars/opaque-observer/
services/opaque-enrollment/
workers/opaque-analyzer/
infra/lib/constructs/opaque-collection.ts
docs/threat-models/opaque-lineage.md
tests/fixtures/opaque-lineage/
tests/contract/opaque-lineage/
tests/integration/opaque-lineage/
tests/security/opaque-lineage/
tests/load/opaque-lineage/
```

Use Go 1.24 for a minimal source-local collector when a sidecar/job is possible,
Python 3.12 for aggregate analysis, TypeScript 5 for control/IaC. Prefer mature
privacy-reviewed HMAC/sketch primitives; custom cryptography is prohibited.
Specific statistical thresholds are versioned policy derived from labelled
evaluation, not embedded as universal constants.

Build order: threat model/contracts; synthetic privacy fixtures; source-local
aggregate/key/kill; comparison/abstention; C13/C15 cap/evaluation; pilot;
load/DR. Default is disabled; rollout per system/environment/enrollment and
rollback activates kill/expiry without code deployment.

## 19. Traceability

| Source decision | C10 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Lane C opaque and advisory forever | C10-FR-001/006-012 | C10-CT-003-006/009 | INT-063/066/067/068 |
| No raw/reversible/low-cardinality evidence | C10-FR-002-005/009; C10-SEC-001-006 | C10-CT-001/002/007/011 | INT-065/069; privacy gate |
| Schedule/freshness/kill | C10-FR-013/015 | C10-CT-007/008 | INT-064/069 |
| Labelled precision before activation | C10-FR-014/016 | C10-CT-010 | INT-067; Lane C activation gate |
| Fail-open/scale/recovery | C10-NFR-001-004 | C10-CT-008/012 | INT-064/069 |
