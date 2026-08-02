# Requirements Traceability Matrix

**Status:** Normative machine-validated coverage register  
**Scope:** All P0 functional, nonfunctional, security and observability
requirements in C01-C18

## 1. P0 Coverage Invariant

The **P0 coverage invariant** is:

    source decision -> Requirement set -> Component test -> Integration test
    -> E2E steel thread -> Phase gate -> Expected evidence

Every P0 requirement must appear in exactly one component requirement table and
be covered by a row below. Range notation is inclusive: for example,
C01-FR-001..C01-FR-015 expands to every numbered ID from 001 through 015.
The documentation validator expands ranges and fails on any uncovered P0 ID.

The component test column names the complete component suite because the
component PRD's Traceability section narrows each behavioral cluster to specific
cases. The integration column points to the authoritative INT matrix, where
every ID expands into positive, negative, duplicate, compatibility,
timeout/recovery and observability cases. Expected evidence conforms to the
TestEvidenceManifest in the shared test strategy.

## 2. Evidence Classes

| Class | Required contents |
|---|---|
| FUNC | Contract/golden, state transitions, immutable input/output checksums, idempotent/forbidden effects, integration report and applicable E2E manifest |
| NFR | Production-shaped configuration, raw latency/throughput/error/fairness/capacity/cost, fault/recovery timeline and SLO calculation |
| SEC | IAM/policy/network/KMS/egress/privacy/accessibility scan as applicable, deny/allow matrix, immutable CloudTrail/data/application audit and incident evidence |
| OBS | Correlation completeness, safe logs/metrics/traces/audit, dashboard/alarms/no-data behavior, tested runbook and timeline capture |

## 3. Foundation and Control Plane Traceability

| Component | Requirement set | Component test | Integration test | E2E steel thread | Phase gate | Expected evidence |
|---|---|---|---|---|---|---|
| C01 | C01-FR-001..C01-FR-015 | C01-CT-001..C01-CT-012 | INT-001..INT-006 | E2E-001/002/003/004/006/009/011/012/014 | Phase 1 contracts/identity | FUNC: schemas/examples, cross-language canonicalization, alias/ambiguity/state report |
| C01 | C01-NFR-001..C01-NFR-004 | C01-CT-001..C01-CT-012 | INT-001..INT-006 | E2E-012/014 | Phase 1 plus Phase 9 scale/DR | NFR: registry/resolve load, availability, backup/restore and checksum report |
| C01 | C01-SEC-001..C01-SEC-004 | C01-CT-001..C01-CT-012 | INT-004/006 | E2E-001/012/013 | Phase 1 security gate | SEC: registry/IAM/ABAC/KMS/tamper/cross-account deny and audit report |
| C01 | C01-OBS-001..C01-OBS-004 | C01-CT-001..C01-CT-012 | INT-006 | E2E-001/012/014 | Phase 1 operations gate | OBS: resolution/ambiguity/version/rollback signals, correlation and alarms |
| C02 | C02-FR-001..C02-FR-015 | C02-CT-001..C02-CT-012 | INT-007..INT-012 | E2E-001/007/009/014 | Phase 3 inventory | FUNC: source goldens/watermarks, snapshot cardinality/checksum, partial/reconcile report |
| C02 | C02-NFR-001..C02-NFR-004 | C02-CT-001..C02-CT-012 | INT-012 | E2E-012/014 | Phase 3 plus Phase 9 scale/DR | NFR: 10k inventory/quota/fairness/outage/recovery raw report |
| C02 | C02-SEC-001..C02-SEC-005 | C02-CT-001..C02-CT-012 | INT-007/012 | E2E-001/012/013 | Phase 3 security gate | SEC: scoped credentials/egress/KMS/secret scan/ABAC/audit evidence |
| C02 | C02-OBS-001..C02-OBS-005 | C02-CT-001..C02-CT-012 | INT-011/012 | E2E-001/012/014 | Phase 3 operations gate | OBS: source completeness/lag/error/reconcile dashboards and alerts |
| C03 | C03-FR-001..C03-FR-015 | C03-CT-001..C03-CT-012 | INT-013..INT-019 | E2E-001/005/006/009/010/012/013/014 | Phase 3 intake | FUNC: auth/normalize/idempotency/coalesce/route/archive/quarantine ledger |
| C03 | C03-NFR-001..C03-NFR-004 | C03-CT-001..C03-CT-012 | INT-018 | E2E-012/014 | Phase 3 plus Phase 9 scale | NFR: 10k burst/100 rps/priority/backpressure/DLQ recovery report |
| C03 | C03-SEC-001..C03-SEC-005 | C03-CT-001..C03-CT-012 | INT-014/018 | E2E-001/012/013 | Phase 3 security gate | SEC: source signature/replay/size/schema/payload/IAM/audit proof |
| C03 | C03-OBS-001..C03-OBS-005 | C03-CT-001..C03-CT-012 | INT-018/019 | E2E-001/012/014 | Phase 3 operations gate | OBS: queue age/depth/throughput/DLQ/route/idempotency timeline |
| C04 | C04-FR-001..C04-FR-015 | C04-CT-001..C04-CT-012 | INT-020..INT-026 | E2E-001/006/007/008/009/014 | Phase 3 classification | FUNC: inventory-decision cardinality, lane/path policy/unknown/override history |
| C04 | C04-NFR-001..C04-NFR-003 | C04-CT-001..C04-CT-012 | INT-026 | E2E-009/012/014 | Phase 3 plus Phase 9 scale | NFR: 10k decision p95/determinism/availability/restore report |
| C04 | C04-SEC-001..C04-SEC-005 | C04-CT-001..C04-CT-012 | INT-025/026 | E2E-001/009/012/013 | Phase 3 security gate | SEC: policy signing/role/ABAC/LLM-nonexclusion/expiry/audit evidence |
| C04 | C04-OBS-001..C04-OBS-005 | C04-CT-001..C04-CT-012 | INT-025/026 | E2E-001/009/014 | Phase 3 operations gate | OBS: class/lane/unknown/stale/override/reconcile dashboards and alerts |
| C05 | C05-FR-001..C05-FR-016 | C05-CT-001..C05-CT-012 | INT-027..INT-033 | E2E-001/003/006/007/008/010/014 | Phase 3 context/indexes | FUNC: snapshot/dependency/determinant/reverse-index/no-impact/divergence report |
| C05 | C05-NFR-001..C05-NFR-004 | C05-CT-001..C05-CT-012 | INT-033 | E2E-007/012/014 | Phase 3 plus Phase 9 scale | NFR: invalidation/fan-out/full-context/load/fairness/rebuild metrics |
| C05 | C05-SEC-001..C05-SEC-005 | C05-CT-001..C05-CT-012 | INT-032/033 | E2E-001/007/012/013 | Phase 3 security gate | SEC: source/context ABAC, secrets/egress, policy and audit report |
| C05 | C05-OBS-001..C05-OBS-006 | C05-CT-001..C05-CT-012 | INT-032/033 | E2E-001/007/012/014 | Phase 3 operations gate | OBS: context completeness/fan-out/divergence/rebuild correlation |
| C06 | C06-FR-001..C06-FR-018 | C06-CT-001..C06-CT-012 | INT-034..INT-041 | E2E-001/003/005/006/007/009/010/011/012/014 | Phase 3 orchestration | FUNC: workflow definitions, stage/idempotency/finally/redrive/fairness ledger |
| C06 | C06-NFR-001..C06-NFR-004 | C06-CT-001..C06-CT-012 | INT-041 | E2E-012/014 | Phase 3 plus Phase 9 scale/DR | NFR: 10k baseline/Tier-1 start/availability/concurrency/recovery report |
| C06 | C06-SEC-001..C06-SEC-005 | C06-CT-001..C06-CT-012 | INT-037/041 | E2E-001/005/012/013 | Phase 3 security gate | SEC: task/workflow roles, reference-only state, callback/auth/audit proof |
| C06 | C06-OBS-001..C06-OBS-006 | C06-CT-001..C06-CT-012 | INT-040/041 | E2E-001/012/014 | Phase 3 operations gate | OBS: stage latency/state/retry/incomplete/fairness/cost/timeline signals |

## 4. Collection and Analysis Plane Traceability

| Component | Requirement set | Component test | Integration test | E2E steel thread | Phase gate | Expected evidence |
|---|---|---|---|---|---|---|
| C07 | C07-FR-001..C07-FR-017 | C07-CT-001..C07-CT-012 | INT-042..INT-048 | E2E-001/002/004/006/014 | Phase 4 native collection | FUNC: Spark/dbt/Airflow exact/unresolved/artifact/duplicate package goldens |
| C07 | C07-NFR-001..C07-NFR-004 | C07-CT-001..C07-CT-012 | INT-048 | E2E-002/012/014 | Phase 4 plus Phase 9 scale/DR | NFR: native run/mapping load, freshness, availability and restore report |
| C07 | C07-SEC-001..C07-SEC-005 | C07-CT-001..C07-CT-012 | INT-044/048 | E2E-001/002/012/013 | Phase 4 security gate | SEC: engine/source/IAM/KMS/privacy/artifact/audit evidence |
| C07 | C07-OBS-001..C07-OBS-006 | C07-CT-001..C07-CT-012 | INT-047/048 | E2E-001/002/012/014 | Phase 4 operations gate | OBS: run/facet/mapping/unresolved/coverage/lag/cost signals |
| C08 | C08-FR-001..C08-FR-015 | C08-CT-001..C08-CT-012 | INT-049..INT-055 | E2E-001/003/004/006/007/008/014 | Phase 4 deterministic analysis | FUNC: pinned request, byte-identical edges/holes/determinants/cache goldens |
| C08 | C08-NFR-001..C08-NFR-004 | C08-CT-001..C08-CT-012 | INT-055 | E2E-003/012/014 | Phase 4 plus Phase 9 scale | NFR: repository/candidate throughput, resource budget, availability/recovery |
| C08 | C08-SEC-001..C08-SEC-005 | C08-CT-001..C08-CT-012 | INT-049/055 | E2E-001/003/012/013 | Phase 4 security gate | SEC: sandbox/read-only checkout/no-network/secret scan/evidence audit |
| C08 | C08-OBS-001..C08-OBS-006 | C08-CT-001..C08-CT-012 | INT-054/055 | E2E-001/003/014 | Phase 4 operations gate | OBS: edges/holes/balance/cache/determinism/resource/stage correlation |
| C09 | C09-FR-001..C09-FR-017 | C09-CT-001..C09-CT-012 | INT-056..INT-062 | E2E-001/003/004/014 | Phase 7 agentic residual | FUNC: hole/task/tool/citation/abstention/cache/budget immutable reports |
| C09 | C09-NFR-001..C09-NFR-004 | C09-CT-001..C09-CT-012 | INT-057/062 | E2E-003/012/014 | Phase 7 plus Phase 9 scale/DR | NFR: budget/latency/queue fairness/gateway outage/cost/recovery report |
| C09 | C09-SEC-001..C09-SEC-006 | C09-CT-001..C09-CT-012 | INT-058/062 | E2E-001/003/012/013 | Phase 7 security/AI gate | SEC: bounded context/tools/model/Region/IAM/egress/injection/privacy audit |
| C09 | C09-OBS-001..C09-OBS-006 | C09-CT-001..C09-CT-012 | INT-061/062 | E2E-003/012/014 | Phase 7 operations gate | OBS: admitted/resolved/abstained/dropped/tool/token/cache/cost signals |
| C10 | C10-FR-001..C10-FR-015 | C10-CT-001..C10-CT-012 | INT-063..INT-069 | E2E-001/004/014 | Phase 8 opaque advisory | FUNC: enrollment/window/fingerprint/support/ambiguity/expiry/abstention report |
| C10 | C10-NFR-001..C10-NFR-004 | C10-CT-001..C10-CT-012 | INT-064/069 | E2E-012/014 | Phase 8 plus Phase 9 scale/DR | NFR: optional capacity/latency/kill/fail-open/cost/recovery evidence |
| C10 | C10-SEC-001..C10-SEC-006 | C10-CT-001..C10-CT-012 | INT-065/069 | E2E-001/012/013 | Phase 8 privacy gate | SEC: source-local key, minimum support, sensitive suppression, no-raw scan |
| C10 | C10-OBS-001..C10-OBS-006 | C10-CT-001..C10-CT-012 | INT-068/069 | E2E-001/012/014 | Phase 8 operations gate | OBS: source/window/eligible/suppressed/ambiguous/kill/cost signals |
| C11 | C11-FR-001..C11-FR-017 | C11-CT-001..C11-CT-012 | INT-070..INT-077 | E2E-001/005/012/013/014 | Phase 7 runtime evidence | FUNC: signed session/readiness/sequence/manifest/finally/completeness ledger |
| C11 | C11-NFR-001..C11-NFR-004 | C11-CT-001..C11-CT-012 | INT-077 | E2E-005/012/014 | Phase 7 plus Phase 9 load/DR | NFR: overhead/10x storm/drain/availability/RPO-RTO report |
| C11 | C11-SEC-001..C11-SEC-006 | C11-CT-001..C11-CT-012 | INT-071/072/075/077 | E2E-005/012/013 | Phase 7 privacy/hard-deny gate | SEC: integration attestation/key/schema/prod multilayer deny/canary audit |
| C11 | C11-OBS-001..C11-OBS-007 | C11-CT-001..C11-CT-012 | INT-074/075/077 | E2E-001/005/012/014 | Phase 7 operations gate | OBS: state/readiness/sequence/gap/truncation/flag/overhead timeline |
| C12 | C12-FR-001..C12-FR-017 | C12-CT-001..C12-CT-012 | INT-078..INT-085 | E2E-001/002/003/004/005/006/011/012/013/014 | Phase 2 immutable evidence | FUNC: prefix/schema/checksum/Object Lock/content-cache/index/integrity report |
| C12 | C12-NFR-001..C12-NFR-004 | C12-CT-001..C12-CT-012 | INT-085 | E2E-012/014 | Phase 2 plus Phase 9 scale/DR | NFR: write/read/load/storage/cost/CRR/restore RPO-RTO evidence |
| C12 | C12-SEC-001..C12-SEC-005 | C12-CT-001..C12-CT-012 | INT-084 | E2E-001/005/012/013 | Phase 2 security/records gate | SEC: IAM/KMS/private/Object Lock/legal hold/data events/privacy scan |
| C12 | C12-OBS-001..C12-OBS-007 | C12-CT-001..C12-CT-012 | INT-084/085 | E2E-001/012/014 | Phase 2 operations gate | OBS: write/read/conflict/integrity/replication/cache/cost/audit signals |

## 5. Trust, Governance, Publication and Experience Traceability

| Component | Requirement set | Component test | Integration test | E2E steel thread | Phase gate | Expected evidence |
|---|---|---|---|---|---|---|
| C13 | C13-FR-001..C13-FR-021 | C13-CT-001..C13-CT-012 | INT-086..INT-093 | E2E-001/002/003/004/005/006/011/014 | Phase 5 trust engine | FUNC: identity/dedup/conflict/G1-G5/drop/hole/coverage/two-axis checksum |
| C13 | C13-NFR-001..C13-NFR-004 | C13-CT-001..C13-CT-012 | INT-093 | E2E-004/012/014 | Phase 5 plus Phase 9 scale/DR | NFR: 100k/10M/500-job determinism/availability/recovery report |
| C13 | C13-SEC-001..C13-SEC-005 | C13-CT-001..C13-CT-012 | INT-086/093 | E2E-001/004/012/013 | Phase 5 security gate | SEC: policy/ABAC/evidence/provenance/no-single-score/audit proof |
| C13 | C13-OBS-001..C13-OBS-007 | C13-CT-001..C13-CT-012 | INT-092/093 | E2E-001/004/012/014 | Phase 5 operations/accuracy gate | OBS: candidates/drops/gates/holes/conflicts/coverage/confidence distribution |
| C14 | C14-FR-001..C14-FR-019 | C14-CT-001..C14-CT-012 | INT-094..INT-101 | E2E-001/006/007/008/010/011/014 | Phase 6 CI/freshness | FUNC: exact drift strings/determinants/signature/binding/deployment decision |
| C14 | C14-NFR-001..C14-NFR-004 | C14-CT-001..C14-CT-012 | INT-100 | E2E-010/012/014 | Phase 6 plus Phase 9 scale/DR | NFR: CI/binding/deploy rate/availability/divergence/RPO-RTO report |
| C14 | C14-SEC-001..C14-SEC-005 | C14-CT-001..C14-CT-012 | INT-096/097/100 | E2E-001/010/012/013 | Phase 6 supply-chain/security gate | SEC: scoped identities/signer separation/provenance/waiver/audit evidence |
| C14 | C14-OBS-001..C14-OBS-007 | C14-CT-001..C14-CT-012 | INT-099/100 | E2E-001/010/012/014 | Phase 6 operations gate | OBS: drift/binding/deploy decision/stale/hotfix/divergence/waiver signals |
| C15 | C15-FR-001..C15-FR-019 | C15-CT-001..C15-CT-012 | INT-102..INT-109 | E2E-001/002/003/004/005/006/011/014 | Phase 5 proposal/review | FUNC: immutable versions/diff/correction/decision/labels/corpus/checksums |
| C15 | C15-NFR-001..C15-NFR-004 | C15-CT-001..C15-CT-012 | INT-108/109 | E2E-011/012/014 | Phase 5 plus Phase 9 scale/DR | NFR: 100k diff/API/backlog/SLO/availability/recovery report |
| C15 | C15-SEC-001..C15-SEC-005 | C15-CT-001..C15-CT-012 | INT-105..INT-108 | E2E-001/011/012/013 | Phase 5 governance/security gate | SEC: SSO/SCIM/RBAC/ABAC/separation/no-direct-publish/privacy/audit |
| C15 | C15-OBS-001..C15-OBS-007 | C15-CT-001..C15-CT-012 | INT-108/109 | E2E-001/011/012/014 | Phase 5 operations/calibration gate | OBS: state/backlog/conflict/correction/labels/corpus/rates/publication signals |
| C16 | C16-FR-001..C16-FR-018 | C16-CT-001..C16-CT-012 | INT-110..INT-117 | E2E-001/006/011/012/014 | Phase 6 publication | FUNC: manifest/reservation/lease/fence/stage/verify/pointer/watermark/rebuild |
| C16 | C16-NFR-001..C16-NFR-004 | C16-CT-001..C16-CT-012 | INT-112/113/117 | E2E-011/012/014 | Phase 6 plus Phase 9 scale/DR | NFR: publication latency/concurrency/availability/rebuild RPO-RTO report |
| C16 | C16-SEC-001..C16-SEC-005 | C16-CT-001..C16-CT-012 | INT-110/112/116/117 | E2E-001/011/012/013 | Phase 6 publication-security gate | SEC: C16-only mutation/stage-commit separation/KMS/private/audit proof |
| C16 | C16-OBS-001..C16-OBS-006, C16-OBS-008 | C16-CT-001..C16-CT-012 | INT-113..INT-117 | E2E-001/011/012/014 | Phase 6 operations gate | OBS: attempt/lease/fence/stage/pointer/lag/reconcile/rebuild alarms |
| C17 | C17-FR-001..C17-FR-020 | C17-CT-001..C17-CT-012 | INT-118..INT-126 | E2E-001/002/003/004/005/009/010/011/012/014 | Phase 6 API/UI | FUNC: OpenAPI/client/query/search/evidence/review/timeline/export/UI result |
| C17 | C17-NFR-001..C17-NFR-005 | C17-CT-001..C17-CT-012 | INT-124..INT-126 | E2E-001/011/012/014 | Phase 6 plus Phase 9 scale/DR | NFR: one-hop/search/Web Vitals/500-rps/availability/version-lag report |
| C17 | C17-SEC-001..C17-SEC-006 | C17-CT-001..C17-CT-012 | INT-120/124/126 | E2E-001/011/012/013 | Phase 6 experience-security gate | SEC: SSO/RBAC/ABAC/WAF/browser/query injection/export/audit evidence |
| C18 | C18-FR-001..C18-FR-030 | C18-CT-001..C18-CT-012 | INT-127..INT-138 | E2E-001/005/007/009/010/011/012/013/014 | Phase 0 foundation and Phase 9 launch | FUNC: conformance/telemetry/reconcile/redrive/backup/rebuild/recovery/cost |
| C18 | C18-NFR-001..C18-NFR-005 | C18-CT-001..C18-CT-012 | INT-127..INT-138 | E2E-012/014 | Phase 9 enterprise scale/DR | NFR: audit latency/reconcile coverage/headroom/SLO/RPO-RTO/availability |
| C18 | C18-SEC-001..C18-SEC-008 | C18-CT-001..C18-CT-012 | INT-127..INT-138 | E2E-001/005/012/013/014 | Phase 0 and Phase 9 security/privacy | SEC: SCP/IAM/ABAC/KMS/network/egress/audit/no-payload/supply-chain proof |

## 6. Matrix Maintenance

- Adding a P0 requirement requires updating its component test matrix, affected
  INT rows, an E2E/phase gate and this register in the same change.
- Moving a requirement to P1/P2 requires product/architecture approval and a
  safe observable launch behavior; it is not a way to make a failed test pass.
- A test ID alone is not evidence. The linked immutable TestEvidenceManifest
  must name the requirement/range, expected/observed effects and cleanup.
- Traceability is evaluated on the exact release candidate. Evidence from
  incompatible contracts, policies, IaC, images or fixture versions is stale.
- Completion requires zero uncovered P0 IDs, zero failed required component/INT/
  E2E cases and zero expired waiver.
