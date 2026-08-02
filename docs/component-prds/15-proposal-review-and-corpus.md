# C15 Proposal, Human Review, and Calibration Corpus PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C15 |
| Status | Approved for implementation |
| Launch phase | Required before first canonical publication |
| Criticality | P0; all material launch proposals require explicit human approval |
| Primary owner | Lineage governance and review team |
| Required approvers | Product, architecture, data governance, application ownership, security |
| Upstream dependencies | C01, C06, C12-C14, enterprise SSO/SCIM/ownership |
| Downstream dependencies | C13 calibration, C14 enforcement policy, C16-C18 |
| Authoritative sources | AWS architecture §12 and rollout/launch gates; element-level v2 R7/R10 |

## 2. Purpose and Outcomes

C15 turns a verified candidate set into an immutable before/after proposal,
supports evidence-aware human correction/approval/rejection, and records the
material per-edge labels needed to measure and calibrate trust. Review is a
governance boundary, not a checkbox: corrections create a new immutable proposal
version, approvals bind the exact checksum, and bulk accept is `unreviewed` for
calibration.

Measurable outcomes:

- Every material launch proposal is explicitly approved/rejected/corrected by
  an authorized reviewer; no production auto-publication.
- Every decision binds exact proposal version/checksum, base graph, reviewer,
  rationale, time, policy and audit; no stale browser overwrite.
- A material per-edge acknowledgement emits `diff(engineProposal,
  acceptedProposal)` as immutable `ReviewLabel`; bulk accept creates zero false
  correctness labels.
- Before enforcement beyond observation, corpus contains at least 200 labelled
  edges across all six archetypes including dynamic SQL, opaque UDF and multi-
  producer cases, with correction rate published by provenance and archetype.

The normative corpus shorthand used by gates is **200 labelled edges across six
archetypes**, subject to the materiality and hard-case rules below.

## 3. Scope and Non-Goals

### In scope

- `LineageProposal` construction/version/state, before/after diff, review
  assignment/authorization, correction/comment/rationale, approve/reject/
  supersede/rebase/expiry, decision/manifest handoff.
- Material-edge acknowledgement and immutable label corpus/metrics/quality gate.
- Review backlog/SLO, notification/escalation, audit and read/write APIs used by
  C17.

### Non-goals

- Rendering UI details (C17) or publishing graph state (C16).
- Treating bulk acceptance, a human decision, or a model self-score as runtime
  execution/derivational oracle.
- Mutating a prior proposal/label/decision.
- Automatically resolving critical UNKNOWN, identity ambiguity, or policy-
  blocking incomplete evidence.
- Training a model or selecting a model from labels without separate governed
  evaluation/AI process.

## 4. Actors and Use Cases

| Actor | Use case |
|---|---|
| Application/domain owner | Review baseline/incremental changes and evidence |
| Data steward | Correct canonical field/transform/metadata and classify conflict |
| Proposer | Submit verified proposal; cannot self-approve when separation required |
| Approver | Approve/reject exact immutable version with rationale |
| Calibration analyst | Build quality-controlled material-edge corpus/metrics |
| Operator | Reassign/escalate backlog, supersede stale proposal, redrive publication |

## 5. Component Boundary

### Owned behavior

- Proposal/decision/correction/comment/label contracts and immutable lifecycle.
- Reviewer assignment/authorization/separation, optimistic concurrency,
  materiality/acknowledgement and corpus calculations.

### Inputs

- C13 verified set/gates/confidence/holes/conflicts/coverage, base/active graph,
  C14 artifact/freshness, identity/context, reviewer ownership/role/policy.

### Outputs

- Immutable proposal versions, decisions/corrections/comments/labels, approved
  manifest request to C16, corpus/calibration/enforcement metrics.

### Forbidden behavior

- Updating a proposal version after publication to reviewers.
- Approval that does not name exact checksum/base/versions.
- Last-write-wins for concurrent review.
- Producing a correctness label from bulk accept or material edge not actually
  acknowledged.
- Auto-approving on confidence or allowing unreviewed LLM/Lane C evidence to
  bypass human review.
- Publishing directly to Neptune/OpenSearch.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C15-FR-001 | C15 must create an immutable `LineageProposal` version bound to application/environment, base graph version, C13 set/checksum/policies, context/artifact, creator and prior proposal version. | P0 |
| C15-FR-002 | Proposal must present before/after nodes/edges and separate added, removed, transformation/path, structural confidence, derivational confidence, evidence, coverage, holes, conflicts, freshness, and no-impact changes. | P0 |
| C15-FR-003 | Every proposed edge must expose canonical endpoints, environment/effective artifact, both confidence axes/caps/calibration, provenance/evidence, G1-G5, determinants, holes/conflicts and review materiality. | P0 |
| C15-FR-004 | The lifecycle must support `DRAFT -> AWAITING_REVIEW -> APPROVED -> PUBLISHING -> ACTIVE`, plus `REJECTED`, `SUPERSEDED`, and `FAILED` publication redrive; transitions are expected-state/version conditional. | P0 |
| C15-FR-005 | Reviewer correction must create a new immutable proposal version linked to the prior, recompute/verify affected diff and checksum, and return to `DRAFT`/`AWAITING_REVIEW`; prior version remains read-only. | P0 |
| C15-FR-006 | Approval/rejection must record exact proposal version/checksum/base graph, reviewer identity/role, decision/rationale, policy, time, evidence acknowledgements, and immutable audit. | P0 |
| C15-FR-007 | Stale/concurrent edit or decision must fail with current version/checksum/state and require deliberate rebase/review; it must not overwrite a newer change. | P0 |
| C15-FR-008 | Reviewer authorization must derive from enterprise SSO/SCIM, application/domain ownership, RBAC/ABAC and optional separation of proposer/approver; access is rechecked at every write. | P0 |
| C15-FR-009 | Critical UNKNOWN repository, unresolved identity/version conflict, blocking incomplete evidence, stale base graph, or expired artifact/policy must prevent approval until corrected, explicitly waived where permitted, rebased or superseded. | P0 |
| C15-FR-010 | At launch, every material baseline/incremental proposal must require explicit human approval; no production auto-approval/auto-publication policy exists. | P0 |
| C15-FR-011 | Proposal assignment must support owner queue, due/SLO, notifications/escalation, delegation with expiry, and absence/conflict handling without changing decision authority silently. | P0 |
| C15-FR-012 | A material edge acknowledgement must record `engineSaid`, `humanSaid`, edge, provenance, archetype, repository, commit, reviewer, timestamp, proposal versions and acknowledgement mode in immutable `ReviewLabel`. | P0 |
| C15-FR-013 | Bulk accept must mark material edges `unreviewed` and must not produce correctness/correction labels; a reviewer must explicitly acknowledge each material mapping used for calibration. | P0 |
| C15-FR-014 | `diff(engineProposal, acceptedProposal)` must classify unchanged-confirmed, corrected source/target/transform/path, added missing edge, removed false edge, confidence/evidence/metadata correction, unresolved/waived and unreviewed. | P0 |
| C15-FR-015 | Corpus gate must require at least 200 material labelled edges spanning Spring, FastAPI, Dask, Spark, dbt and Airflow/SQL archetypes and deliberately hard dynamic SQL, opaque UDF and multi-producer cases before enforcement beyond observation. | P0 |
| C15-FR-016 | C15 must publish correction rate by provenance (deterministic versus LLM/native/opaque as applicable) and by archetype, plus confirmed/added/removed/changed/unreviewed distribution and labelled sample counts/uncertainty. | P0 |
| C15-FR-017 | Label/corpus quality must detect duplicates/leakage, invalid reviewer scope, nonmaterial/bulk labels, superseded artifacts, missing evidence and imbalanced archetype/case coverage before calibration use. | P0 |
| C15-FR-018 | Proposal staleness must compare active graph/context/artifact/policy/evidence versions; stale proposals are rebased or superseded, never published against a changed expected base. | P0 |
| C15-FR-019 | Rejection/supersession/expiry/publication failure must retain all proposal/evidence/comment/decision/label history and expose governed retry/rebase/closure action. | P0 |
| C15-FR-020 | Post-launch auto-approval research may be evaluated only in shadow mode and requires a separate approved policy/change after measured gates; it is not initial scope. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C15-NFR-001 | Proposal creation/diff for 100,000 changed edges must complete within five minutes p95; standard proposal API writes within two seconds p95. | P0 |
| C15-NFR-002 | Review APIs/queues must be 99.95% available monthly and preserve read/write consistency/optimistic concurrency across Multi-AZ failure. | P0 |
| C15-NFR-003 | 95% of Tier-1 material proposals must be assigned/notified within one minute and reviewed within the governed Tier-1 SLO or escalated. | P0 |
| C15-NFR-004 | Proposal/decision/label history must recover within C18 RPO/RTO with no duplicate/lost decision or publication from stale state. | P0 |

## 7. Data and Durable State

`LineageProposal` contains ID/version/state/application/environment/base/target
intent, immutable C13 before/after/diff refs, context/artifact/digest/freshness,
confidence/gates/coverage/conflicts/holes summaries, creator/assignment/material
edge manifest, policy/schema versions, prior/supersedes, checksum/timestamps.

`ReviewCorrection` contains proposal/version/checksum, material edge/object,
operation, engine value, human value, evidence/rationale, reviewer, expected
state/version, time and new proposal ref/checksum.

`ProposalDecision` contains exact reviewed checksum/base, approve/reject,
reviewer/role, separation result, rationale, material acknowledgement manifest,
waivers, policy and signature/audit.

`ReviewLabel` contains edge/engineSaid/humanSaid/change class/provenance/
archetype/repository/commit/artifact/reviewer/time/ack mode/evidence/policy and
immutable checksum. Acknowledgement mode is `MATERIAL_EDGE_REVIEWED` or
`UNREVIEWED_BULK`; only the first enters labelled accuracy corpus.

C12 S3 Object Lock stores proposal versions, corrections, decisions, labels and
accepted manifest input. DynamoDB holds lifecycle/assignment/concurrency/
notification/publication status; analytics catalog reads immutable labels.

## 8. Interfaces and Contracts

- `POST /v1/proposals` accepts C13 set/base/context/artifact refs/checksums and
  idempotency; returns draft ref/version.
- `POST /v1/proposals/{id}/versions/{v}:submit|correct|approve|reject|supersede|
  rebase` requires expected state/version/checksum, role, rationale/input.
- `POST /v1/proposals/{id}:assign|delegate|escalate` uses owner policy/expiry.
- `GET /v1/proposals`, `/versions`, `/diff`, `/edges`, `/evidence`, `/comments`,
  `/labels` paginate and ABAC filter.
- `POST /v1/review-labels:validateCorpus` and metrics endpoints produce immutable
  manifests/reports for C13/C14.
- Events: `proposal.created|submitted|corrected|approved|rejected|superseded|
  stale|publishing|active|failed`, `review.label.created`,
  `review.corpus.gate.passed|failed`, assignment/SLO events.

## 9. Processing and State Model

```text
DRAFT -> AWAITING_REVIEW -> APPROVED -> PUBLISHING -> ACTIVE
                         -> REJECTED
                         -> SUPERSEDED
AWAITING_REVIEW -> DRAFT  (correction creates new immutable proposal version)
PUBLISHING -> FAILED -> PUBLISHING  (governed redrive)
```

1. Validate C13/base/context/artifact/policy and create deterministic immutable
   before/after/diff/materiality manifest.
2. Assign owner/reviewer; submit conditionally and notify/escalate.
3. Review writes require current state/version/checksum/authorization.
4. Correction creates a new version, triggers affected C13 verification as
   needed, recalculates diff/materiality and resubmits.
5. Decision validates blockers/separation/material acknowledgements, persists
   immutable decision/labels, then conditionally transitions.
6. Approval creates exact accepted-manifest input and requests C16. Publication
   callback uses expected proposal/version/graph/token result.
7. Corpus validates labels and publishes metrics/gate to C13/C14.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `PROPOSAL_INPUT_INVALID_OR_INCOMPLETE` | `DETERMINISTIC_INVALID`/`INCOMPLETE` | No reviewable proposal; exact gaps |
| `PROPOSAL_VERSION_OR_STATE_CONFLICT` | `CONFLICT` | Reject stale write; return current version/state |
| `REVIEWER_UNAUTHORIZED_OR_SEPARATION_FAILED` | `DETERMINISTIC_INVALID` security | Deny/audit; no decision |
| `APPROVAL_BLOCKER_PRESENT` | `INCOMPLETE` | Deny approval; list UNKNOWN/conflict/stale/policy/evidence blocker |
| `BASE_GRAPH_CHANGED` | `CONFLICT` | Rebase/supersede; do not publish stale proposal |
| `LABEL_NOT_MATERIAL_OR_ACKNOWLEDGED` | `DETERMINISTIC_INVALID` corpus | Store unreviewed/audit but exclude accuracy corpus |
| `CORPUS_GATE_INSUFFICIENT_OR_INVALID` | `INCOMPLETE` calibration | No enforcement advancement/confidence calibration use |
| `PUBLICATION_FAILED` | `TRANSIENT`/`CONFLICT` | Preserve approved state, redrive or rebase/supersede |
| `NOTIFICATION_DEPENDENCY_FAILED` | `TRANSIENT` | Retry/escalate; proposal remains durable/queryable |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C15-SEC-001 | Enterprise SSO/SCIM, domain RBAC, sensitive-metadata ABAC, owner mapping and optional proposer/approver separation must be enforced on every read/write/decision/export. | P0 |
| C15-SEC-002 | Proposal services must have no direct Neptune/OpenSearch mutation; approved handoff is an immutable C12 manifest to a separate C16 publication role. | P0 |
| C15-SEC-003 | Proposal/evidence/comments/labels must not contain payload values, credentials, broad source/model transcript content, or unauthorized sensitive field details; references and redaction apply. | P0 |
| C15-SEC-004 | Decisions/corrections/labels/comments/assignments/delegations/exports/policy changes must be immutable/audited with actor/purpose/version/checksum and S3 data events where required. | P0 |
| C15-SEC-005 | Reviewer/admin/publication/analytics roles and KMS/prefix access must be least privilege/separated; bulk data export requires explicit purpose/approval/watermark. | P0 |

## 12. Scale, Performance, and Availability

- Large proposals store before/after/diff/material-edge pages in C12 S3 and
  indexed DynamoDB/OpenSearch review read models; APIs paginate/filter and never
  load an unbounded graph in one request.
- Proposal creation/diff uses Batch for millions of edges, conditional state for
  lifecycle, and deterministic content addressing for retries.
- Review queue partitions by domain/application/priority; Tier-1 assignment/
  notification/escalation remains isolated from baseline bulk review.
- Labels are append-only, deduplicated by proposal edge/decision/reviewer and
  partitioned for analytics by archetype/provenance/time without mutating source.
- Replication/backups restore proposal/decision/label authority before read
  models; stale workers/notifications cannot decide/publish after recovery.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C15-OBS-001 | Proposal state/count/age/latency | type/priority/app/domain/owner | P0 |
| C15-OBS-002 | Assignment/review/SLO/escalation | team/reviewer/tier/state | P0 |
| C15-OBS-003 | Correction/approve/reject/supersede/rebase | provenance/archetype/diff/materiality | P0 |
| C15-OBS-004 | Concurrent/stale/unauthorized/blocker decisions | reason/app/reviewer | P0 |
| C15-OBS-005 | Material labels/unreviewed/corpus coverage | archetype/provenance/hard case/reviewer | P0 |
| C15-OBS-006 | Correction rate/distribution | provenance/archetype/model/analyzer/policy/sample count | P0 |
| C15-OBS-007 | Publication handoff/failure/redrive | proposal/base/target/reason | P0 |

Metrics distinguish accepted proposal from reviewed material edge. Bulk accept
increases adoption/review throughput but not labelled correctness denominator.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C15-AC-001 | Given C13 verified baseline/incremental set, C15 creates deterministic immutable before/after proposal with all diff, confidence, gates, evidence, holes, conflicts, coverage and versions. |
| C15-AC-002 | Given two concurrent reviewers, only the expected current version writes; stale correction/decision receives conflict and cannot overwrite. |
| C15-AC-003 | Given correction, prior proposal remains immutable, new version is reverified/diffed, and approval applies only to new exact checksum. |
| C15-AC-004 | Given unauthorized/self-approval under separation or critical blocker/stale base, approval is denied/audited with exact remediation. |
| C15-AC-005 | Given per-edge material acknowledgement, correct label diff is emitted; given bulk accept, edge is `unreviewed` and excluded from corpus metrics. |
| C15-AC-006 | Given fewer/imbalanced/invalid labels or missing hard cases, corpus gate fails; given 200 valid labelled edges across six archetypes/hard cases, exact metrics/gate publish. |
| C15-AC-007 | Given base graph changes before publication, proposal rebases/supersedes and cannot activate against stale expected version. |
| C15-AC-008 | Load/outage/DR meet NFRs with no lost/duplicate decision/label/publication, exact lifecycle and Tier-1 review escalation. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C15-CT-001 | Golden proposal | Baseline/incremental C13 set with all diff types | Create | Exact immutable proposal/diff/materiality/checksum | Proposal goldens |
| C15-CT-002 | State matrix | Every valid/invalid transition and redrive | Transition | Exact allowed/denied conditional state | State report |
| C15-CT-003 | Concurrent/stale | Two corrections/decisions same expected version | Write | One wins; stale conflict/current returned; history intact | State/audit history |
| C15-CT-004 | Correction | Source/target/transform/path/confidence/evidence changes | Correct/resubmit | New immutable version/reverification/diff/labels | Version chain |
| C15-CT-005 | Authorization | Domain/ABAC/self-approval/delegation expiry | Read/write/approve | Exact allow/deny/separation/audit | IAM/API report |
| C15-CT-006 | Approval blockers | UNKNOWN/identity conflict/incomplete/stale base/digest/policy | Approve | Denied with exact blocker/rebase/waiver path | Decision responses |
| C15-CT-007 | Label materiality | Explicit per-edge, bulk accept, nonmaterial, superseded | Decide/validate | Valid labels or `unreviewed`/excluded | Label/corpus rows |
| C15-CT-008 | Corpus metrics | 200+ labelled six archetypes/hard cases plus duplicates/imbalance | Calculate | Exact counts/correction rates/gate/invalid exclusions | Corpus report |
| C15-CT-009 | Publication conflict | Active graph changes after approval | Publish callback/rebase | No stale active; rebase/supersede history | Proposal/publication history |
| C15-CT-010 | Privacy/export | Sensitive evidence/comments and bulk export | Read/comment/export | ABAC/redaction/purpose/watermark/audit | Security/export scan |
| C15-CT-011 | SLO/notification | Tier-1/standard queues, owner absent, dependency outage | Assign/escalate | Exact notification/escalation; durable proposal | Timeline/metrics |
| C15-CT-012 | Load/DR | 100k diff, concurrent review, failure/Region restore | Create/review/recover | NFR/RPO/RTO, no duplicate/lost decision/label | Load/DR report |

## 16. Integration Obligations

- **INT-102 C13↔C15:** immutable verified set becomes deterministic proposal;
  corrections reverify affected claims and labels feed calibration without
  circular self-validation.
- **INT-103 C14↔C15:** artifact/freshness/phase/blocker/approved package and
  enforcement corpus metrics interoperate.
- **INT-104 C15↔C16:** exact approved checksum/base/manifest publishes with
  conditional callbacks; stale/version conflict rebase/supersede/redrive.
- **INT-105 C15↔C17:** assignment, diff, evidence, two axes, gates, holes,
  conflicts, correction/comments/decision/concurrency/accessibility flows pass.
- **INT-106 SSO/SCIM/catalog↔C15:** owner/domain/role/delegation/separation and
  access removal propagate before every decision.
- **INT-107 C15↔C12:** immutable proposal/correction/decision/label/Object Lock,
  exact references/access/audit/replication/restore pass.
- **INT-108 C15↔C18:** SLO/notification/escalation/audit/security/privacy/export/
  backlog/reconciliation/load/DR runbooks/gates pass.
- **INT-109 C15↔C13/C14 corpus:** 200-edge six-archetype/hard-case quality,
  correction metrics and unreviewed exclusion gate policy activation.

## 17. Definition of Done

- Proposal/diff/materiality/state/assignment/correction/comment/decision/label/
  corpus contracts/services/indexes/immutable writes and notifications exist.
- C15 P0 requirements and C15-CT-001 through C15-CT-012 pass.
- INT-102 through INT-109 pass with production-shaped C12-C17 and enterprise
  identity/ownership systems.
- No production auto-approval/publication exists; authorization/separation,
  concurrency/blockers, immutable history, exact checksum and stale-base tests
  pass.
- Corpus report proves or explicitly fails 200 labelled/six archetype/hard-case
  gate, exact correction metrics and bulk-unreviewed exclusion.
- Load/security/privacy/SLO/outage/DR reports meet NFRs with no lost/duplicate
  decision/label/publication.
- Review/backlog/identity/blocker/correction/rebase/publication/corpus/export/DR
  runbooks and alarms are exercised.

## 18. Implementation Notes

```text
contracts/schemas/proposals/
contracts/schemas/review-labels/
contracts/openapi/review-api.yaml
services/proposal-api/
services/review-assignment/
workers/proposal-diff/
workers/calibration-corpus/
infra/lib/constructs/proposal-review.ts
tests/contract/proposals/
tests/integration/proposal-review/
tests/security/proposal-review/
tests/load/proposal-review/
```

Use TypeScript 5 for APIs/control/IaC, Python 3.12 for large deterministic diff/
corpus jobs. C12 S3 holds immutable content, DynamoDB conditional state/queues,
and a rebuildable search/read model may support review. C15 never gets Neptune
write credentials.

Build order: contracts/state; proposal/diff/materiality; review/concurrency/auth;
correction/reverification; approval/labels; C16/C17; corpus/metrics; load/security/
DR. Launch feature policy requires explicit approval; shadow research cannot
change state.

## 19. Traceability

| Source decision | C15 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Immutable before/after human review | C15-FR-001-011/018-019 | C15-CT-001-006/009/011 | INT-102-106; publication gate |
| Per-edge labels; bulk unreviewed | C15-FR-012-014/017 | C15-CT-004/007/010 | INT-107/109 |
| 200 labels/six archetypes/correction metrics | C15-FR-015/016 | C15-CT-008 | INT-109; calibration/enforcement gate |
| Security/scale/recovery | C15-SEC-001-005; C15-NFR-001-004 | C15-CT-005/010-012 | INT-108; security/enterprise/DR gates |
