# C14 CI Drift, Artifact Binding, and Freshness PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C14 |
| Status | Approved for implementation |
| Launch phase | Observation with Lane A; binding/freshness required before enforcement |
| Criticality | P0; every deployed artifact must have a visible lineage decision |
| Primary owner | Lineage CI/CD and release-integrations team |
| Required approvers | Architecture, release engineering, application security, trust/review owners |
| Upstream dependencies | C03-C06, C08-C13, enterprise CI/build/deployment systems, signing service |
| Downstream dependencies | C15-C18 and external deployment policy |
| Authoritative sources | Element-level v2 R8-R10; AWS architecture §§9, 14, 17-19 |

## 2. Purpose and Outcomes

C14 keeps lineage synchronized with code and immutable deployed artifacts while
stating CI's limits honestly. Lane A CI re-derivation is a drift check, not
semantic validation. An unskippable release step binds the reviewed LineageSpec
package to the exact artifact digest, including an already-built image and every
hotfix/emergency path. Deployment reconciliation exposes missing/stale lineage
and suppresses lineage more than two deploys behind from blast-radius claims.

Measurable outcomes:

- 100% of PR checks use only `Lineage drift: none` or `Lineage drift detected`
  status language; no CI output claims semantic validation.
- 100% of deployed artifacts have a current/approved lineage binding or an
  explicit missing/stale/blocked/exception decision and alert.
- LLM/opaque provenance is structurally absent from blocking policy inputs.
- Scheduled full analysis produces zero unexplained full-scan divergence from
  incremental state; non-zero is an owned defect.

## 3. Scope and Non-Goals

### In scope

- Lane A pull-request deterministic lineage re-derivation/diff, checks,
  comments, patch/proposal artifact, observe/acknowledge/block phases.
- Signed `ArtifactLineageBinding` for existing artifact digest without rebuild.
- Deployment event/binding/freshness reconciliation, hotfix/emergency coverage,
  missing alert, staleness/suppression, full-scan divergence, policy/audit.

### Non-goals

- Claiming CI proves lineage correctness; generator and checker share machinery.
- Running Lane B's authoritative per-run lineage through Lane A PR drift.
- Letting an LLM-provenance edge block CI/deployment.
- Silently committing generated lineage to a branch.
- Rebuilding an image merely to attach lineage or allowing image tag as identity.
- Production SCA/LLM; production emits digest/schema/boundary confirmation only.

## 4. Actors and Use Cases

| Actor/system | Use case |
|---|---|
| Developer/PR author | See deterministic lineage drift and apply an explicit patch |
| Reviewer | Compare proposed deterministic changes/evidence before merge |
| Release pipeline | Bind signed approved LineageSpec to exact already-built digest |
| Deployment controller | Evaluate binding/freshness policy for normal/hotfix deploy |
| Incident responder | Know whether an edge matches the running artifact or is suppressed |
| Operator | Reconcile deployments/bindings, full-vs-incremental divergence, exceptions |

## 5. Component Boundary

### Owned behavior

- CI drift result/patch artifact and deterministic-only policy input.
- Artifact-lineage signing/attestation registry, deployment freshness decision,
  reconciliation, stale suppression and enforcement phase policy.

### Inputs

- PR commit/base and C08/C13 deterministic results/determinants.
- C15 approved proposal/LineageSpec package and C12 reference/checksum.
- Immutable build artifact digest/signature/SBOM/provenance and deployment event.
- Active/previous bindings, policy/phase, full scan/incremental manifests.

### Outputs

- CI status/comment/patch artifact, `ArtifactLineageBinding`, deployment lineage
  decision, freshness/suppression, alerts/exceptions/divergence/audit.

### Forbidden behavior

- Outputting "validated" or equivalent correctness claim for the drift check.
- Including LLM/Lane C/unreviewed evidence in blocking input.
- Pushing/committing a generated contract automatically.
- Binding a mutable tag, branch, missing digest, or package from another digest.
- Skipping binding for hotfix/emergency/already-built artifacts.
- Using stale-suppressed lineage in automated blast radius while hiding reason.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C14-FR-001 | Lane A PR check must deterministically regenerate the scoped LineageSpec/candidate set from the PR commit and compare it with the repository's declared/base lineage using pinned analyzer/policy versions. | P0 |
| C14-FR-002 | The only success/failure summary strings must be `Lineage drift: none` and `Lineage drift detected`; the word `validated` and semantic-correctness claims are prohibited in status/comment text. | P0 |
| C14-FR-003 | CI drift output must separate added/removed/modified deterministic edges, determinants, holes/coverage, unsupported/incomplete and artifact/policy versions with evidence references. | P0 |
| C14-FR-004 | Only deterministic-provenance edges may enter blocking policy; LLM, Lane C, runtime-only, conflict, uncalibrated, and bulk-unreviewed inputs must be structurally excluded before policy evaluation. | P0 |
| C14-FR-005 | CI must never silently commit generated lineage; it must publish a checksummed patch/proposal artifact and PR comment/status with explicit developer/reviewer action. | P0 |
| C14-FR-006 | Lane B native workloads must not use Lane A PR drift as their authoritative lineage gate; their per-run native evidence/freshness is reconciled separately. | P0 |
| C14-FR-007 | Enforcement phases must be versioned `OBSERVE`, `ACKNOWLEDGE_CRITICAL`, `BLOCK_MISSING_CRITICAL_MAPPING`, and `BLOCK_HIGH_CONFIDENCE_BREAKING_IMPACT`; transition requires approved measured false-positive/correction/SLO/security evidence. | P0 |
| C14-FR-008 | Advancement beyond observation must require false-positive rate below 20% for four consecutive weeks for the gated scope, calibrated bands, sufficient material labelled corpus, no unexplained full-scan divergence, and approved rollback. | P0 |
| C14-FR-009 | Release binding must take an immutable already-built image/artifact digest and approved LineageSpec package/reference/checksum, verify application/repository/commit/environment/policy compatibility, and produce a signed immutable `ArtifactLineageBinding`. | P0 |
| C14-FR-010 | Binding must be unskippable for normal, hotfix, emergency, rollback, promotion, and manual deployment paths and must run against an already-built image without rebuild or tag mutation. | P0 |
| C14-FR-011 | Signature/attestation must cover artifact digest, lineage package checksum/version, proposal/accepted manifest/base graph, application/repository/commit, environment scope, signer, policy, and creation/expiry/revocation. | P0 |
| C14-FR-012 | Every deployment event must reconcile by immutable digest/environment to a valid binding or explicit `MISSING`, `MISMATCHED`, `STALE`, `REVOKED`, `BLOCKED`, or governed time-bounded exception; absence is never silent. | P0 |
| C14-FR-013 | An artifact observed in production without valid lineage package must raise an owned alert and follow policy (observe/warn/block) while preserving the deployment decision and hotfix identity. | P0 |
| C14-FR-014 | Freshness must compare the active approved package with deployed digest/version sequence; more than two deploys behind must be `STALE_SUPPRESSED` and excluded from blast-radius automation with reason visible. | P0 |
| C14-FR-015 | Freshness/invalidation must use C05 determinants and all deploys, not changed-file proximity; configuration-only, dependency, schema, contract, infrastructure, and analyzer/policy changes must trigger correct decisions. | P0 |
| C14-FR-016 | Scheduled full rescan must diff against accumulated incremental result; any unexplained full-scan divergence must create a defect/alert and block enforcement advancement rather than be accepted as tolerance. | P0 |
| C14-FR-017 | Production collection for freshness must be limited to artifact digest, schema/version, deployment and boundary metadata; production SCA/LLM/raw field payload capture is prohibited. | P0 |
| C14-FR-018 | Exceptions must be scope/digest/environment/policy/reason/owner/approver/effective/expiry constrained, nonrenewing without review, visible in CI/deployment/UI, and reconciled on expiry. | P0 |
| C14-FR-019 | CI/binding/deployment/full-scan decisions must be immutable, idempotent by exact business identity, correlated, queryable, and auditable. | P0 |
| C14-FR-020 | C14 should support policy preview against historical PR/deployment/label data and current estate without changing active checks/gates. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C14-NFR-001 | Incremental PR drift must finish within 10 minutes p95 and artifact binding within two minutes p95 excluding required human review. | P0 |
| C14-NFR-002 | Deployment binding/freshness decision must be available within 60 seconds p95 of deployment event; Tier-1 within 30 seconds p95. | P0 |
| C14-NFR-003 | C14 must process at least 10,000 deployment decisions/day and 100 events/second bursts without losing hotfix or exception-expiry decisions. | P0 |
| C14-NFR-004 | CI/binding/freshness service must be 99.95% available monthly; policy defines fail-open/closed per phase while preserving visible decision and recovery within C18 RPO/RTO. | P0 |

## 7. Data and Durable State

`CiDriftResult` contains repository/base/head/analyzer/policy, deterministic input
manifest/checksum, added/removed/modified edges, holes/coverage, exclusions by
provenance/reason, summary string, status, patch/comment refs, and audit.

`ArtifactLineageBinding` contains artifact digest/type/signature/build provenance,
application/repository/commit/environment, LineageSpec/accepted proposal/base
graph reference/checksum/version, analyzer/policy/contract versions, signer/
signature/key, effective/expiry/revocation, and immutable checksum.

`DeploymentLineageDecision` contains deployment/digest/environment/time/tier,
binding/freshness, deploy sequence/behind count, suppression, policy/phase,
action/exception/alert, run/proposal/graph refs and checksum.

`DivergenceReport` contains full/incremental refs/checksums, missing/extra/
modified edges/holes/determinants by archetype/provenance, explanation/status,
defect/owner and enforcement-gate effect.

C12 stores immutable results/bindings/decisions/reports; DynamoDB holds current
binding/freshness/exception/deployment indexes and idempotency.

## 8. Interfaces and Contracts

- CI command/API `lineage drift --base <sha> --head <sha> --output <dir>` emits
  machine JSON, LineageSpec patch, human summary and process status; server API
  uses S3 references for analysis.
- `POST /v1/artifact-lineage-bindings` accepts artifact provenance/digest and
  approved lineage ref/checksum/compatibility; signing service returns immutable
  binding/attestation.
- `POST /v1/deployment-lineage-decisions` normally consumes C03 normalized
  deployment event and binding registry.
- `GET /v1/artifacts/{digest}/lineage` and deployment/freshness endpoints return
  decision/history with authorization.
- Events: `lineage.drift.detected|none`, `artifact.lineage.bound|missing|revoked`,
  `deployment.lineage.current|stale|suppressed|blocked`,
  `incremental.full-scan.diverged`, `lineage.exception.expiring|expired`.

## 9. Processing and State Model

### CI drift

```text
REQUESTED -> INPUT_PINNED -> DETERMINISTIC_REDERIVE -> DIFF
          -> POLICY_FILTER -> ARTIFACTS_PUBLISHED -> REPORTED
```

### Artifact/deployment freshness

```text
BUILT -> LINEAGE_APPROVED -> BOUND_SIGNED -> DEPLOY_OBSERVED
      -> CURRENT | BEHIND_ONE | BEHIND_TWO | STALE_SUPPRESSED
      -> REBOUND/CURRENT
```

Alternative: `MISSING`, `MISMATCHED`, `REVOKED`, `BLOCKED`, `EXCEPTION_ACTIVE`,
`EXCEPTION_EXPIRED`.

1. Verify exact commit/digest/approved package/policy and sign binding without
   rebuilding artifact.
2. On every deploy, fetch/verify binding/signature/revocation/environment and
   active package/graph sequence.
3. Compute behind count/freshness and policy action; persist decision before
   acknowledge.
4. Reconcile deployment inventory to decisions/bindings and exceptions.
5. Scheduled full result compares incremental state and gates enforcement.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `DRIFT_INPUT_OR_ANALYSIS_INCOMPLETE` | `INCOMPLETE` | Non-success check with gap; no semantic claim |
| `NONDETERMINISTIC_PROVENANCE_IN_BLOCK_INPUT` | `DETERMINISTIC_INVALID` policy | Reject policy input/alert; no block decision from it |
| `ARTIFACT_DIGEST_MISSING_OR_MISMATCH` | `DETERMINISTIC_INVALID`/`CONFLICT` | No binding; exact defect/decision |
| `LINEAGE_PACKAGE_NOT_APPROVED_OR_MISMATCHED` | `DETERMINISTIC_INVALID` | No signature/binding |
| `SIGNING_SERVICE_UNAVAILABLE` | `TRANSIENT` | Bounded retry; phase policy fail behavior, visible decision |
| `BINDING_MISSING_REVOKED_EXPIRED` | `INCOMPLETE` | Alert/warn/block by phase; never assume current |
| `STALE_OVER_TWO_DEPLOYS` | deterministic freshness | Suppress blast-radius use and display reason |
| `FULL_SCAN_DIVERGENCE` | correctness defect | Alert/block phase advancement; preserve exact diff |
| `EXCEPTION_EXPIRED` | deterministic policy | Re-evaluate immediately; no silent renewal |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C14-SEC-001 | CI/release/deployment callers must use workload/repository/environment-scoped identities; signer keys/roles are separate from build/analyzer/reviewer/deployer roles and require exact digest/package conditions. | P0 |
| C14-SEC-002 | Artifact/lineage signatures and attestations must use approved KMS/signing profile, key rotation/revocation, immutable transparency/audit, and verification in deployment decisions. | P0 |
| C14-SEC-003 | CI logs/comments/status/patches must not include source secrets, payloads, sensitive evidence bodies, model prompts, or signing material; references enforce ABAC. | P0 |
| C14-SEC-004 | Policy/phase/exception/signing/revocation changes require scoped role separation, expected version, evidence/rationale/expiry, approval, and CloudTrail/audit. | P0 |
| C14-SEC-005 | Production roles must have no SCA/LLM/runtime-field ingestion permission; allowed digest/schema/boundary metadata contracts are closed and audited. | P0 |

## 12. Scale, Performance, and Availability

- CI uses C08 content cache and C05 determinant scope; full reanalysis is
  scheduled separately and never omitted as soundness oracle.
- Binding is O(artifact/package) verification/signing, not repository analysis.
  Registry/index partitions by organization/digest/environment.
- Deployment events are Tier-1 through C03/C06; every hotfix identity remains
  independent. Backfill/full scan cannot consume reserved decision capacity.
- Signer/registry/decision services are Multi-AZ with queued retry and warm-
  Region keys/IaC/replicated immutable evidence. Phase policy defines whether
  dependency outage observes/warns/blocks without losing audit.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C14-OBS-001 | CI drift/status/latency | repo/archetype/deterministic count/policy | P0 |
| C14-OBS-002 | Blocking exclusions | provenance/conflict/calibration/coverage reason | P0 |
| C14-OBS-003 | Binding/sign/verify/revoke | digest/app/env/key/policy/status | P0 |
| C14-OBS-004 | Deployment current/missing/stale/suppressed/blocked/exception | tier/app/domain/owner; missing hotfix alert | P0 |
| C14-OBS-005 | Deploy-to-decision latency/backlog/reconciliation | priority/domain/system | P0 |
| C14-OBS-006 | Full-scan divergence | archetype/reason/missing/extra/modified; any unexplained alert | P0 |
| C14-OBS-007 | Phase metrics | false positive/correction/labelled corpus/SLO/security/rollback | P0 |

C17 displays digest/binding/freshness/behind count/suppression/exception and
LineageSpec/proposal/graph versions. Dashboard metrics reconcile all deployment
inventory to decisions.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C14-AC-001 | Given no/detected deterministic diff, CI emits exactly the approved summary string, full patch/evidence, and never uses `validated` as correctness language. |
| C14-AC-002 | Given LLM/Lane C/runtime-only/unreviewed candidates, they are absent from blocking input by schema/filter assertion, not merely ignored by convention. |
| C14-AC-003 | Given a PR drift, C14 publishes patch/comment/artifact but does not commit/push source automatically. |
| C14-AC-004 | Given an already-built normal or hotfix image, C14 binds the exact digest to compatible approved package without rebuild; mismatches fail. |
| C14-AC-005 | Given a deployed digest with missing/revoked/stale binding, an exact visible policy decision/alert occurs and more than two deploys behind is suppressed. |
| C14-AC-006 | Given configuration-only/dependency/schema/infrastructure/test changes, determinant-based freshness targets match C05; changed-file-only under-report is absent. |
| C14-AC-007 | Given non-zero full-scan divergence or unmet FP/corpus/calibration/SLO/security gate, enforcement phase cannot advance. |
| C14-AC-008 | Load/outage/recovery meet NFRs and every deployment/hotfix/exception reconciles to one immutable decision with no silent absence. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C14-CT-001 | CI golden | No drift and added/removed/modified deterministic drift | Run check | Exact strings/status/diff/versions | CI artifacts |
| C14-CT-002 | Semantics/negative | Scan all check text plus generator/validator same engine | Execute | No `validated` claim; docs/status state drift limitation | Output scan |
| C14-CT-003 | Provenance policy | Deterministic, LLM, runtime, opaque, conflict, unreviewed inputs | Build block set | Deterministic eligible only, exact exclusions | Policy input golden |
| C14-CT-004 | No silent commit | Repository/PR token with generated patch | Run CI | Comment/artifact only; git ref unchanged | SCM before/after/audit |
| C14-CT-005 | Binding | Correct/missing/mismatched digest/package; already-built image | Bind | Signed exact binding or deterministic failure; image digest unchanged | Attestation/image evidence |
| C14-CT-006 | Hotfix/emergency | All normal/manual/hotfix/rollback/promotion paths | Deploy | Every digest passes binding decision; none skipped/coalesced | Deployment decision set |
| C14-CT-007 | Freshness | Current, one/two/three deploys behind, revoked, exception | Decide/query | Exact states; >2 suppressed/visible | Freshness matrix |
| C14-CT-008 | Determinants | Config/library/infra/contract/test changes | Invalidate/decide | Exact impacted/no-impact, no file-only gap | Plan/decision report |
| C14-CT-009 | Divergence | Full result differs missing/extra/modified | Compare/advance phase | Defect/alert; advancement denied | Divergence/gate evidence |
| C14-CT-010 | Exception/security | Unauthorized/expired/overbroad exception, bad signature/key | Apply/verify | Denied or exact expiry/re-evaluation/audit | IAM/sign/audit report |
| C14-CT-011 | Phase | Historical four-week FP/corpus/calibration/SLO combinations | Preview/activate | Advance only all conditions/approval; rollback exact | Phase decision report |
| C14-CT-012 | Load/DR | 10k/day, 100/sec burst, signer outage, Region failover | Decide/recover | NFR/RPO/RTO and exact deployment reconciliation | Load/DR report |

## 16. Integration Obligations

- **INT-094 C05/C08/C13↔C14:** determinant-scoped deterministic drift, holes/
  coverage, provenance block filtering, and full-scan comparison interoperate.
- **INT-095 C03/C06↔C14:** every deployment/hotfix/exception expiry creates one
  priority idempotent decision under duplicates/out-of-order/replay.
- **INT-096 CI/SCM↔C14:** exact strings/status/comment/patch/no-auto-commit,
  permissions, timeout and deterministic-only policy pass.
- **INT-097 Build/release/signing↔C14:** already-built digest, approved package,
  signature/attestation, mismatch/revoke/outage and all paths pass.
- **INT-098 C14↔C15/C16:** approved proposal/package binds to artifact and only
  matching approved graph version publishes/becomes current.
- **INT-099 Deployment↔C14/C17:** current/missing/stale/suppressed/blocked/
  exception decisions/alerts are visible and reconciled.
- **INT-100 C14↔C18:** policy/phase/signing/IAM/privacy/audit/alarms/runbooks/
  exceptions/reconciliation/load/DR gates pass.
- **INT-101 C14↔Incident queries:** stale-suppressed lineage is excluded from
  blast-radius automation with reason, while historical evidence remains.

## 17. Definition of Done

- CI command/service, deterministic policy filter, patch/comment/status,
  binding signer/registry/attestation, deployment decision/freshness/suppression,
  exception, full-scan/phase policy, reconciliation and telemetry are implemented.
- C14 P0 requirements and C14-CT-001 through C14-CT-012 pass.
- INT-094 through INT-101 pass with enterprise SCM/build/release/deployment and
  production-shaped platform components.
- Every deployment/hotfix in the acceptance window reconciles to one immutable
  decision; missing/stale alerts and >2 suppression are proven.
- Phase remains observation unless corpus/calibration/FP/SLO/security/divergence
  evidence meets the exact gate; activation/rollback report is retained.
- Signing/security/privacy/load/outage/DR reports meet NFRs and prove no rebuild,
  skipped path, nondeterministic block input, production SCA/LLM, or secret leak.
- CI/binding/missing/stale/exception/signing/phase/reconciliation/DR runbooks and
  alarms are exercised with real IDs.

## 18. Implementation Notes

```text
contracts/schemas/ci-drift/
contracts/schemas/artifact-binding/
services/ci-drift/
services/artifact-binder/
services/deployment-lineage-controller/
workers/full-scan-divergence/
infra/lib/constructs/artifact-binding.ts
docs/runbooks/artifact-freshness/
tests/contract/ci-binding/
tests/integration/ci-binding/
tests/security/ci-binding/
tests/load/ci-binding/
```

Use TypeScript 5 for CI/control/signing/IaC integration and Python 3.12 for
manifest diff/large reconciliation. Sign an attestation referencing existing
artifact digest and C12 package; never mutate/rebuild image. Prefer the
enterprise artifact-attestation standard and KMS keys rather than a new private
signature format.

Build order: drift schema/CLI/exact language; provenance filter/patch; binding/
sign/verify; deploy decisions/freshness/suppression; exceptions/reconciliation;
full-scan/phase; load/security/DR. Default phase is `OBSERVE` and policy rollback
is independent of application deployment.

## 19. Traceability

| Source decision | C14 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| CI is drift, deterministic blocking only, no auto-commit | C14-FR-001-008 | C14-CT-001-004/011 | INT-094/096; CI observation gate |
| Artifact digest binding unskippable incl hotfix | C14-FR-009-013/019 | C14-CT-005/006/010/012 | INT-095/097/098 |
| Freshness >2 suppressed/determinant/full divergence | C14-FR-014-018 | C14-CT-007-009 | INT-099/101; freshness gate |
| Security/scale/recovery | C14-SEC-001-005; C14-NFR-001-004 | C14-CT-010/012 | INT-100; security/enterprise/DR gates |
