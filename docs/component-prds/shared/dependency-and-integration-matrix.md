# Dependency and Integration Test Matrix

**Status:** Normative implementation and launch specification
**Applies to:** C01-C18, external producers, AWS dependencies, user clients and
enterprise control systems

## 1. Purpose

This matrix is the authoritative definition of every INT-nnn obligation named
by the component PRDs. A component is not integrated because its happy-path API
call succeeds. Its boundary is complete only when the common six-path protocol,
the row-specific invariant, security policy, recovery behavior and retained
evidence pass in the required deployed environment.

The component PRD owns behavior on its side of a boundary. This matrix owns the
joint producer-consumer proof. If the documents conflict, the stricter
validation, privacy, idempotency, versioning or visibility rule applies and the
contract owners must reconcile the specifications before promotion.

## 2. Component Dependency and Release Gates

| Component | Required upstream before implementation integration | Required downstream proof before component complete | Primary gate |
|---|---|---|---|
| C01 | Schema registry, KMS, policy and identity fixtures | C02/C07/C08/C11/C13/C15/C16/C17/C18 consume one pinned identity meaning | Foundation contracts |
| C02 | C01, enterprise inventory sources and scoped credentials | C03-C05/C17/C18 receive complete or explicit partial snapshots | Inventory |
| C03 | C01/C02, authenticated producers, EventBridge/SQS | C04/C06/C14/C17/C18 account for every accepted/quarantined trigger | Intake |
| C04 | C01-C03 and eligibility policy registry | C05-C11/C14/C15/C17/C18 preserve class/lane/unknown decisions | Classification |
| C05 | C01/C02/C04 and source dependency metadata | C06/C08/C11/C13/C14/C17/C18 use one pinned context/determinant set | Context |
| C06 | C03-C05 and scheduler/service quotas | C07-C18 stage, retry, redrive, fairness and timeline proofs | Orchestration |
| C07 | C01/C04-C06 and native engines | C12/C13/C15/C17/C18 preserve exact/unresolved native semantics | Native collection |
| C08 | C01/C04-C06 and deterministic toolchains | C09/C12-C15/C17/C18 preserve byte-stable proof and holes | Deterministic analysis |
| C09 | C06/C08, enterprise model gateway and tool policy | C12/C13/C15/C17/C18 preserve citations, caps, budgets and abstention | Agentic residual |
| C10 | C01/C04-C06 and source-local privacy controls | C12-C15/C17/C18 preserve advisory scope/cap/expiry/abstention | Opaque advisory |
| C11 | C01/C03/C05/C06, AppConfig, sidecars and test service | C12/C13/C15/C17/C18 prove complete metadata-only integration sessions | Runtime evidence |
| C12 | C01 and C02-C11 producer schemas, S3/DynamoDB/KMS | C13/C15-C18 read immutable exact versions and recover authority | Evidence |
| C13 | C01/C05/C07-C12 and policy/calibration versions | C14/C15/C17/C18 preserve gates, drops, holes and two axes | Trust |
| C14 | C03/C05/C06/C08/C13 and CI/build/deploy/signing | C15-C18 bind every deployment digest to a freshness decision | CI/freshness |
| C15 | C12-C14 and enterprise ownership/SSO | C16-C18 preserve immutable review, labels and exact approval | Governance |
| C16 | C06/C12/C14/C15 and DynamoDB/Neptune/OpenSearch | C17/C18 prove fenced pointer, projection watermark and rebuild | Publication |
| C17 | C01/C06/C12-C16 and enterprise identity | Browser/API users and C18 prove authorized version-consistent experience | Experience |
| C18 | Enterprise organization/security/network/audit/incident/finance | Every component passes local plus cross-cutting controls and recovery | Security/operations/DR |

## 3. Mandatory Six-Path Boundary Protocol

Every matrix row creates these six executable cases. The test ID is the matrix
ID plus the suffix shown; the integration report must list all six.

| Suffix | Dimension | Required assertion |
|---|---|---|
| POS | positive | Contract-valid input produces the exact durable business effect and consumer acknowledgement. |
| NEG | negative | Invalid, unauthorized, incomplete, conflicting and privacy-prohibited input is rejected/quarantined with no forbidden effect. |
| DUP | duplicate | Duplicate and, when applicable, out-of-order delivery produces one idempotent effect or a documented conflict, never silent loss. |
| COMPAT | compatibility | Current and supported prior schema/client versions interoperate; unsupported major/semantic changes fail before business mutation. |
| REC | timeout/recovery | Producer/consumer/dependency timeout, throttling and partial failure follows bounded retry/checkpoint/redrive/reconcile without false success. |
| OBS | observability | Logs, metrics, traces, audit, state and C17 timeline carry safe correlation and make result/retry/quarantine/conflict visible. |

For read-only browser or control boundaries, DUP means repeated request/action
identity and REC includes stale cache/version/dependency recovery. For recovery
boundaries, COMPAT covers backup/schema/IaC/policy compatibility. A row may add
stronger cases but may not omit a dimension. Each case records fixture version,
producer/consumer builds, contract/policy versions, fault, timestamps, IDs,
expected/observed effects, checksums and artifact URIs as retained evidence.

## 4. Authoritative Boundary Matrix

### C01 contracts and identity

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-001 | C01↔C02 | Inventory aliases under pinned registry/environment/effective version | Every observation resolves once or is visibly ambiguous; snapshot checksum binds registry version. |
| INT-002 | C01↔C07/C08/C11 | Multi-lane canonical entity fixture | Native/static/runtime references converge to identical URNs without changing evidence meaning. |
| INT-003 | C01↔C13 | Candidate identity resolution | Ambiguity blocks deduplication/promotion and retains competing aliases/evidence. |
| INT-004 | C01↔C15/C17 | Alias inspection/correction | Authorized correction creates immutable version; old/new identities remain traceable and UI never rewrites history. |
| INT-005 | C01↔C16 | Published canonical nodes/edges | Target graph validates URN grammar, environment/effective version and manifest checksum before activation. |
| INT-006 | C01↔C18 | Registry security/rollback/recovery | Outage/rollback/cross-account denial/audit/restore preserves last valid pinned semantics. |

### C02 inventory and adapters

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-007 | C01↔C02 | Adapter observation and identity registry | Same as INT-001 plus invalid aliases cannot enter an authoritative snapshot. |
| INT-008 | C02↔C03 | Snapshot-created/reconciliation EventEnvelope | Exact snapshot URI/checksum/watermark is authenticated, deduplicated and routed once. |
| INT-009 | C02↔C04 | Repository/path inventory | Every discovered item receives included/excluded/mixed/unknown decision; none disappear. |
| INT-010 | C02↔C05 | Deployment/schema/native/test/context observations | One checksummed snapshot produces version-pinned context; explicit missing sources remain partial. |
| INT-011 | C02↔C17 | Inventory/source completeness | Counts, source watermarks, partial state and reconciliation gaps match snapshot truth and ABAC. |
| INT-012 | C02↔C18 | Source credentials/outage/audit/recovery | Throttle/outage/secret scan/restore yields bounded retry or PARTIAL, never leaked credentials or false complete. |

### C03 intake and queues

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-013 | C02↔C03 | Inventory trigger payload reference | Checksum/schema/source/identity validate before idempotent intake and archive. |
| INT-014 | External producers↔C03 | SCM/deploy/test signatures and immutable IDs | Forged/missing commit or digest quarantines; valid burst is accepted without loss. |
| INT-015 | C03↔C04 | Repository classification trigger | Exact repository/path/commit/snapshot identity reaches one governed eligibility decision. |
| INT-016 | C03↔C06 | Routed work trigger | Each accepted trigger maps to one visible workflow, coalesced membership, no-impact or deferral record. |
| INT-017 | C03↔C14 | Deployment/hotfix trigger | Every deployed digest/environment creates one freshness decision, including emergency paths. |
| INT-018 | C03↔C18 | Queue/DLQ/archive/replay | Enqueue/dequeue/DLQ/redrive/replay counts reconcile and poison messages cannot consume unbounded retry. |
| INT-019 | C03↔C17 | Intake timeline/status | Accepted/duplicate/coalesced/quarantined/deferred reason and correlation are user-visible without payload. |

### C04 eligibility and lane routing

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-020 | C02↔C04 | Inventory cohort/path evidence | Complete decision cardinality equals discovered items and critical unknown blocks baseline completion. |
| INT-021 | C03↔C04 | Duplicate/out-of-order policy triggers | Same input/policy reuses decision; newer evidence supersedes conditionally; stale event cannot overwrite. |
| INT-022 | C04↔C05 | Class/lane/override policy | Context and determinants include effective class/path reasons, policy/expiry and conflicts. |
| INT-023 | C04↔C06/C07-C11 | Lane assignment | Eligible workload routes exactly to approved lane(s); excluded/unknown never runs expensive collector silently. |
| INT-024 | C04↔C14 | Class/lane/policy invalidation | Effective change invalidates the exact artifact binding and triggers governed reanalysis. |
| INT-025 | C04↔C15/C17 | Unknown/conflict/override review | Reviewer sees evidence/expiry/history; authorized immutable decision updates downstream state. |
| INT-026 | C04↔C18 | Policy activation/expiry/reconciliation | Rollback/outage/waiver expiry/load and audit preserve last valid policy and expose every mismatch. |

### C05 context, dependencies and determinants

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-027 | C01/C02/C04↔C05 | Pinned inventory, class and identities | One context version resolves repository/path/application/schema/environment without mixed snapshots. |
| INT-028 | C05↔C06 | Invalidation manifest | Planned work cardinality/reasons exactly match scheduled/coalesced/no-impact outcomes. |
| INT-029 | C05↔C08/C13 | Determinant round trip | Edge/hole determinants reference existing versioned facts and can reproduce invalidation decision. |
| INT-030 | C05↔C14 | Config/library/infra/contract/test change | Correct consumers/artifacts invalidate; capacity-only/docs-only changes produce explainable no-impact. |
| INT-031 | C05↔C11 | Test/scenario/sidecar mapping | Expected session participants and tests are exact; missing/conflict becomes INCOMPLETE before confidence use. |
| INT-032 | C05↔C17 | Context/dependency explanation | Authorized UI/API shows reason path, conflicts, versions and fan-out without sensitive source leakage. |
| INT-033 | C05↔C18 | Index outage/fan-out/rebuild | Reconciliation and full scan detect missing consumers; rebuild matches source checksums within fairness limits. |

### C06 orchestration and scheduling

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-034 | C03↔C06 | Accepted route to run | Exactly one run/no-impact/deferred record per idempotency/coalescing membership and priority. |
| INT-035 | C04/C05↔C06 | Lane/context/invalidation plan | Workflow pins inputs and schedules exact eligible work under version/priority policy. |
| INT-036 | C06↔C07-C10 | Analysis job protocol | Budget/heartbeat/checkpoint/result/finally/retry semantics produce one durable stage outcome. |
| INT-037 | C06↔C11 | Runtime session orchestration | Tests start after READY; drain/disable finally executes; closing completeness controls downstream. |
| INT-038 | C06↔C12/C13 | Stage artifacts to verification | Checksummed immutable outputs feed one verification input; missing/conflict stays INCOMPLETE. |
| INT-039 | C06↔C15/C16 | Review wait/resume/publication | External callback identity/state is conditional; retry cannot duplicate decision or active pointer advance. |
| INT-040 | C06↔C17 | Run timeline/redrive action | All stages/attempts/reasons/artifacts correlate; permitted operator action is bounded and current-state checked. |
| INT-041 | C06↔C18 | Fairness/orphan/DR operations | Tier-1 start SLO holds under load; orphan/retry/quota/failure reconciles and restores safely. |

### C07 native lineage

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-042 | C01/C04/C05↔C07 | Lane B pinned job/context/aliases | Collector accepts only eligible exact engine/artifact context and emits canonical versioned mappings. |
| INT-043 | C06↔C07 | Expected native-run workflow | Missing listener/artifact, retry and reconciliation yield exact run outcome without fabricated mapping. |
| INT-044 | Spark/dbt/Airflow↔C07 | Native facets/manifests/plans | Exact columns/transforms and unresolved select-star/dynamic cases match engine goldens and artifact digest. |
| INT-045 | C07↔C12 | Native package persistence | First immutable checksum wins; identical duplicate reuses, conflicting same identity quarantines. |
| INT-046 | C07↔C13 | Native derivational oracle | Exact mappings can verify derivation; execution-only/unresolved evidence cannot. |
| INT-047 | C07↔C15/C17 | Native review/query provenance | Users see run/digest/exactness/unresolved/coverage and can trace evidence authorization. |
| INT-048 | C07↔C18 | Native fault/privacy/load/DR | Missing facets, outage, secret scan, capacity and restore produce visible exact/incomplete outcomes. |

### C08 deterministic analysis

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-049 | C01/C04/C05↔C08 | Lane A request and DeterminantSet | Analyzer pins commit/context/tool/config/schema and rejects unsupported/mixed identity. |
| INT-050 | C06↔C08 | Batch job lifecycle/cache | Admission/budget/heartbeat/checkpoint/result/retry/redrive creates one byte-stable stage result. |
| INT-051 | C08↔C09 | Named Hole handoff | Only open hole and approved bounded facts/tools pass; deterministic proof is never reanalyzed. |
| INT-052 | C08↔C12 | Package/fact/cache persistence | Content key reproduces byte-identical package; conflict/partial write quarantines. |
| INT-053 | C08↔C13 | Provable edge/hole verification | G1/G2/G4 pass only with cited resolvable evidence; hole counters balance. |
| INT-054 | C08↔C14/C15/C17 | Drift/review/evidence presentation | Changed determinants produce exact diff; proof/holes/versions remain visible end to end. |
| INT-055 | C08↔C18 | Sandbox/determinism/load/recovery | No network/secret leak; repeated analysis is byte-identical and recoverable within quotas. |

### C09 agentic residual resolution

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-056 | C08↔C09 | Open hole/fact/tool scope | Hole identity, facts and allowed operations round-trip; closed/nonexistent hole is rejected. |
| INT-057 | C06↔C09 | Residual queue and budget | Admission/retry/defer prevents starvation and produces resolved/abstained/budget-exhausted outcome once. |
| INT-058 | C09↔Enterprise gateway | Model/Region/tool/CI identity policy | Only approved model and bounded prompt/tool path executes; outage degrades to unresolved. |
| INT-059 | C09↔C12 | Task/result/content cache | Result checksum binds hole/facts/model/prompt/tools; duplicate reuses and conflict quarantines. |
| INT-060 | C09↔C13 | Citation/evidence verification | Each emitted edge cites existing file:line/fact; G1-G5 drops unsupported edges and reopens hole. |
| INT-061 | C09↔C15/C17 | Agent provenance/review | UI exposes LLM provenance, citations, cap, budget and unresolved reason without model transcript. |
| INT-062 | C09↔C18 | IAM/privacy/injection/cost/DR | Prompt injection, arbitrary search/egress, secret context and spend limits are denied/audited; outage is safe. |

### C10 opaque advisory evidence

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-063 | C01/C04/C05↔C10 | Lane C enrollment/field policy | Only approved opaque sources/fields/windows enter collection; sensitive/low-cardinality fields suppress. |
| INT-064 | C06↔C10 | Advisory job/budget/kill/finally | Optional work sheds before critical paths; failure/kill closes state and never blocks launch. |
| INT-065 | Source-local collector↔C10/C12 | Fingerprint key/window/aggregate package | Raw values never leave source; session/window-key expiry and minimum observation enforce privacy. |
| INT-066 | C10↔C13 | G1/G3/G5 advisory semantics | Nonmatch/ambiguity/expiry abstains; confidence cap prevents verified derivation. |
| INT-067 | C10↔C14/C15 | Nonblocking evidence/review | Opaque evidence never enters deterministic blocking; reviewers see advisory label/cap. |
| INT-068 | C10↔C17 | Advisory query presentation | Scope/window/support/ambiguity/expiry and no raw values render accurately under ABAC. |
| INT-069 | C10↔C18 | Privacy kill/key/source fault/load | Incident revokes keys/stops collection; outage/cost/load/recovery retains safe advisory state. |

### C11 integration runtime evidence

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-070 | C01/C05/C06↔C11 | Test/context/digest/expected sidecars | Session binds exact integration environment/scenarios/artifact and rejects missing/mismatched participants. |
| INT-071 | AppConfig↔C11 | Signed enable/readiness/disable/expiry | Flag enables only attested integration session and disables in finally/expiry even after fault. |
| INT-072 | Sidecar↔CloudWatch/validator/Kinesis/C12 | Evidence schema/sequence/closing manifest | Allowed metadata arrives in order per sidecar, checksum closes, forbidden values quarantine. |
| INT-073 | C11↔C13 | Runtime completeness semantics | COMPLETE may raise structural only; incomplete/truncated/failed cannot; derivational never changes. |
| INT-074 | C11↔C15/C17 | Session evidence/coverage UI | Tests, participants, gaps, truncation and privacy state remain versioned and visible. |
| INT-075 | C11↔C18 | Production hard-deny/security ops | AppConfig/IAM/resource/attestation layers each deny production and emit incident-grade audit. |
| INT-076 | C11↔C03/C06 | Callback replay/redrive | Duplicate/stale READY/event/close cannot rerun tests, reopen session or duplicate evidence. |
| INT-077 | C11↔C18 load/DR | Storm/quota/Region failure | Sequence/completeness/final disable and recovery meet overhead/fairness/RPO/RTO. |

### C12 immutable evidence and cache

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-078 | C01/C02-C11↔C12 | Producer schema/prefix/data class | Each producer writes only allowed contract/prefix/key; checksum/URN/version/privacy validate first. |
| INT-079 | C06↔C12 | Stage start/result reference | Workflow records exact immutable URI/checksum/schema; partial/missing write never marks success. |
| INT-080 | C08/C09/C10↔C12 | Content-addressed caches | Complete key includes all determinants/policy/tool inputs; identical hit safe, conflicting identity quarantined. |
| INT-081 | C11↔C12 | Runtime validator-only write | Direct sidecar/write is denied; sequence/manifest/privacy validator determines immutable completeness. |
| INT-082 | C12↔C13/C15 | Evidence/proposal/label exact reads | Consumers verify checksum/version/Object Lock and cannot mutate or read outside ABAC. |
| INT-083 | C12↔C16/C17 | Accepted manifest/export/query reference | Publication/query uses approved exact artifacts; pointer/projection are not evidence authority. |
| INT-084 | C12↔C18 security/records | IAM/KMS/private/Object Lock/legal hold/audit | Unauthorized/delete/tamper attempts fail and required data access is centrally audited. |
| INT-085 | C12↔C18 operations | Integrity/replication/backup/restore/rebuild | Inventory/checksum/CRR/RPO/RTO reconcile exact immutable truth under load and Region fault. |

### C13 trust engine

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-086 | C01/C05↔C13 | Identity/context/schema/determinants | Candidate merge uses one version and blocks ambiguity/staleness/conflict visibly. |
| INT-087 | C07↔C13 | Native oracle/unresolved coverage | Exact native maps verify derivation; missing/duplicate/conflict preserves coverage and evidence. |
| INT-088 | C08/C09↔C13 | Proof/hole/citation verification | G1-G5 deterministic results are repeatable; dropped agent edge returns open hole/reason. |
| INT-089 | C10↔C13 | Advisory scope/cap/expiry | Opaque evidence affects only allowed structural advisory result and abstains when invalid. |
| INT-090 | C11↔C13 | Runtime complete/incomplete | Runtime changes structural only under complete session and cannot prove transform/exclude paths. |
| INT-091 | C13↔C14/C15 | Blocking set and proposal input | Deterministic-only policy, gates, holes/conflicts/coverage/checksum transfer immutably. |
| INT-092 | C13↔C17 | Trust rendering/API | Both axes/gates/caps/calibration/evidence/drop/coverage render separately and accurately. |
| INT-093 | C13↔C18 | Policy/load/chaos/recovery | Policy authorization, determinism, reconciliation and restore reproduce exact verified set/checksum. |

### C14 CI, artifact binding and freshness

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-094 | C05/C08/C13↔C14 | Determinant-scoped drift package | Changed determinants/proof/holes/gates yield exact deterministic drift/no-drift output. |
| INT-095 | C03/C06↔C14 | Deployment/hotfix/waiver-expiry flow | Every digest/environment gets one current/missing/stale/blocked/suppressed decision and run. |
| INT-096 | CI/SCM↔C14 | Status/comment/patch contract | Exact user strings/status, no-auto-commit and untrusted-fork security behave compatibly/idempotently. |
| INT-097 | Build/release/signing↔C14 | Already-built artifact/package signature | Binding names immutable digest and approved package/provenance; tag-only or unsigned input fails. |
| INT-098 | C14↔C15/C16 | Approved package to publication | Exact proposal/package/digest/freshness/base binds accepted manifest; stale cannot activate. |
| INT-099 | Deployment↔C14/C17 | Freshness and incident query | Decision becomes visible quickly; stale-suppressed lineage is excluded from current incident result. |
| INT-100 | C14↔C18 | Policy/signing/audit/reconcile/DR | Phase/waiver/security/load/outage/restore maintains a decision for every deployment. |
| INT-101 | C14↔Incident queries | Stale-suppression enforcement | Current query filters known stale bindings and explains exclusion with authorized evidence. |

### C15 proposal, review and corpus

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-102 | C13↔C15 | Verified set to immutable proposal | Deterministic before/after/diff/checksum/base/materiality reproduces exactly; blockers transfer. |
| INT-103 | C14↔C15 | Artifact/freshness/blocker input | Review shows exact digest/phase/decision; stale/expired policy blocks approval until rebased. |
| INT-104 | C15↔C16 | Approved manifest handoff | Exact approved version/checksum/base/reviewer/policy publishes once; reject/supersede never publishes. |
| INT-105 | C15↔C17 | Review API/UI | Assignment/diff/evidence/two axes/holes/conflicts/materiality and optimistic concurrency match C15. |
| INT-106 | SSO/SCIM/catalog↔C15 | Ownership/role/delegation/separation | Current authorized reviewer only; revoked/expired/cross-domain decision denies and audits. |
| INT-107 | C15↔C12 | Immutable review artifacts | Proposal/correction/decision/label checksums and Object Lock retain history and exact reads. |
| INT-108 | C15↔C18 | Review SLO/security/recovery | Notification/escalation/audit/privacy/export/backup restore preserves decisions and no duplicate publish. |
| INT-109 | C15↔C13/C14 corpus | Label/calibration gate | At least 200 valid material labelled edges across six archetypes/hard cases; bulk unreviewed excluded. |

### C16 fenced publication and projections

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-110 | C12/C15↔C16 | Approved Object-Locked manifest/base | Signature/checksum/approval/base validate before reservation; draft/reject/unlocked fails. |
| INT-111 | C06↔C16 | Publication workflow | Submit/retry/redrive/cancel/reconcile preserves request identity/fence and one terminal callback. |
| INT-112 | C16↔DynamoDB/Neptune | Lease/fence/stage/pointer transaction | Only current fence and expected prior activate fully verified immutable target; stale worker loses. |
| INT-113 | C16↔OpenSearch | Active projection/alias/watermark | Build exact active version, atomically expose alias/watermark; failure lags visibly and retries. |
| INT-114 | C16↔C17 | Active graph/search version | Query pins pointer/watermark, never mixes version, and handles lag/rebuild/rollback explicitly. |
| INT-115 | C16↔C15 | Publication callbacks | Publishing/active/failed/conflict callback is conditional on exact proposal/version and idempotent. |
| INT-116 | C16↔C18 | Publication controls/operations | IAM/network/KMS/audit/alarm/reconcile/chaos/cleanup preserve prior active and immutable truth. |
| INT-117 | C12/C16/C18 DR | Projection recovery | Restore accepted manifests/pointer history and rebuild exact Neptune/OpenSearch within RPO/RTO. |

### C17 query APIs, UI and timeline

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-118 | C16↔C17 | Pointer/namespace/checksum/watermark | Every response pins permitted active graph and labels projection lag/version; pointer race never mixes. |
| INT-119 | C15↔C17 | Proposal/review conditional command | UI/API mirrors immutable C15 state and stale edit cannot overwrite newer proposal. |
| INT-120 | C12↔C17 | Evidence/export authorization | Checksum/Object Lock/purpose/ABAC/redaction/expiry/audit pass; no existence leakage. |
| INT-121 | C13↔C17 | Gates/confidence/coverage display | Separate axes/caps/calibration/holes/conflicts/drop reasons/denominator match trust output. |
| INT-122 | C03/C06/C14/C16↔C17 | Run timeline events | Attempts/decisions/gaps/retry/redrive/publication/watermark order under common correlation. |
| INT-123 | C01↔C17 | URN/OpenAPI/client/deep links | Supported contracts round-trip canonical identity; ambiguous/unsupported version rejects safely. |
| INT-124 | C18↔C17 | Identity/WAF/network/audit/SLO/DR | API/UI/export controls, synthetics, alarms and regional behavior pass with no payload telemetry. |
| INT-125 | Neptune/OpenSearch↔C17 | Bounded query/load/lag | Depth/result/time/cost guards and replica/index failures meet SLO or explicit safe error. |
| INT-126 | Browser↔C17 | User journeys/accessibility | Supported browsers/assistive tech pass search, graph, review, timeline, stale/error/concurrency states. |

### C18 cross-cutting security, operations and recovery

| ID | Boundary | Contract and fixture focus | Exact joint pass invariant |
|---|---|---|---|
| INT-127 | C01-C03↔C18 | Foundation/intake controls | Contract policy, identity, network, secret/egress, audit, queue/DLQ and trigger reconciliation pass. |
| INT-128 | C04-C06↔C18 | Classification/context/orchestration controls | Unknown/determinant/fairness/retry/redrive/run gaps remain visible and recoverable. |
| INT-129 | C07-C10↔C18 | Analysis compute controls | Role/sandbox/egress/Bedrock/privacy/cost/fault controls pass without hiding incomplete work. |
| INT-130 | C11↔C18 | Runtime privacy/production hard-deny | Every deny layer, metadata sequence/completeness, cleanup, incident and DR path passes. |
| INT-131 | C12↔C18 | Evidence records/security/DR | KMS/Object Lock/retention/legal hold/data audit/CRR/checksum/restore preserve authority. |
| INT-132 | C13-C15↔C18 | Trust/review governance controls | RBAC/ABAC/separation/audit/backlog/waiver/retention/recovery preserves verified decisions. |
| INT-133 | C16↔C18 | Publication operational controls | Fence/pointer/capacity/alarm/reconcile/rebuild/chaos prove no partial or stale activation. |
| INT-134 | C17↔C18 | Experience controls | Identity/WAF/private/ABAC/export/audit/SLO/synthetic/stale/recovery pass. |
| INT-135 | External systems↔C18 | Trust/credentials/egress/outage | Scoped access and audit pass; dependency failure circuits to explicit partial/retry. |
| INT-136 | Audit/SIEM/incident↔C18 | Audit/finding/alarm/response | Required events arrive immutable/correlated, route on time and retain incident evidence. |
| INT-137 | Primary↔warm standby | Replication/backup/key/IaC/quota/recovery | Exercise restores/rebuilds/cuts over/fails back within RPO/RTO and exact reconciliation. |
| INT-138 | Finance/governance↔C18 | Tags/cost/budget/control/waiver | Spend attributes correctly, guardrails preserve critical work, waivers alert/expire/fail closed. |

## 5. Execution Ownership and Evidence

The producer team owns valid/invalid/duplicate payload fixtures and producer
telemetry. The consumer team owns validation, idempotent durable effects,
failure injection and recovery. Both owners sign the joint report. C18 owns the
deployed control evidence; QA owns fixture integrity and report completeness.

An integration result is valid only when run against immutable producer and
consumer builds with the production contract, IAM, KMS, network, queue/workflow,
data-store and telemetry topology appropriate to the gate. Local mocks may
prove logic but cannot close an INT row involving a managed-service semantic,
cross-account authorization, projection, load, chaos or recovery guarantee.

Failed rows block the dependent component gate. A waived nonfunctional case
must be P1/P2, cannot weaken a platform invariant or P0 requirement, and follows
C18 scoped expiry. Security/privacy, approval/fencing, immutable truth,
idempotency, complete visibility and RPO/RTO cases cannot be waived for launch.
