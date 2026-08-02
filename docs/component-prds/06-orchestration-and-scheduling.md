# C06 Workflow Orchestration and Workload Scheduling PRD

## 1. Document Control

| Field | Value |
|---|---|
| Component | C06 |
| Status | Approved for implementation |
| Launch phase | Foundation through enterprise |
| Criticality | P0; coordinates every long-running collection, verification, publication, and recovery flow |
| Primary owner | Lineage workflow platform team |
| Required approvers | Architecture, operations, analysis, review/publication, security |
| Upstream dependencies | C03 normalized queues, C04 decisions, C05 context/invalidation, C12 state/evidence foundations |
| Downstream dependencies | C07-C18 |
| Authoritative sources | AWS architecture §§5-6, 8-10, 14-17; shared state/error model |

## 2. Purpose and Outcomes

C06 turns durable triggers and immutable manifests into visible, resumable
workflows. Step Functions Standard coordinates; SQS buffers; Batch executes
heavy analysis; Lambda performs short control actions. C06 enforces dependency
order, idempotent stage transitions, priority fairness, quotas, timeout/cancel,
finally cleanup, and run-timeline events without becoming the content authority.

Measurable outcomes:

- Every C03 accepted work item produces one run/no-impact/deferred decision.
- Baseline, incremental, runtime, verification/review handoff, publication,
  reconciliation, and projection rebuild can resume/redrive without repeating
  valid completed work or duplicating business effects.
- Tier-1 incremental start latency remains within five minutes p95 during
  baseline/backfill and domain-skew load.
- Users can see current/completed stages, elapsed/retry/redrive/missing evidence,
  review/publication/projection status without AWS console access.

## 3. Scope and Non-Goals

### In scope

- Step Functions Standard definitions and stage contracts for all long-running
  workflows; Distributed Map for S3 manifests.
- Idempotent run creation, dependency/stage readiness, checkpoints, retry/catch,
  compensation/finally, cancellation, expiry, redrive, and child run linkage.
- Priority-aware Batch queues/job definitions/capacity reservations, per-domain
  admission, Bedrock/runtime quota coordination, and fairness.
- Stage/run status, progress, timeline events, and operational reconciliation.

### Non-goals

- Routing ingress events (C03), computing eligibility/invalidation (C04/C05),
  analyzing/reconciling content (C07-C13), or approving/publishing graph state
  (C15/C16).
- Embedding large evidence/proposals in Step Functions state.
- Using Lambda as a long-running orchestrator or repository analyzer.
- Assuming retries are safe without the called component's idempotency contract.

## 4. Actors and Use Cases

| Actor/component | Use case |
|---|---|
| C03 | Hand off priority-normalized work and receive durable consume outcome |
| Application owner | Start baseline/cancel permitted run and inspect timeline |
| C07-C13 workers | Receive pinned inputs, budget, callback/result contract |
| C15/C16 | Receive review/publication handoff and conditionally advance state |
| Operator | Redrive failed stage, pause admission, drain queue, reconcile stuck run |
| Capacity owner | Configure reserved/borrowed capacity and quotas by priority/domain |

## 5. Component Boundary

### Owned behavior

- `CollectionRun`, `StageAttempt`, workflow definitions, execution/job/session
  linkage, admission/scheduling, and timeline emission.
- Dependency/timeout/retry/redrive/finally rules and stage output validation.

### Inputs

- C03 queue message plus normalized event reference/checksum/idempotency.
- C04 eligibility/lane and C05 context/invalidation manifests.
- Workflow policy, quotas, priority/domain, and expected state versions.

### Outputs

- Child Batch/Lambda/Step Functions/C11 work, immutable stage-result references,
  run state/timeline, proposal/publication/reconciliation triggers.

### Forbidden behavior

- Starting work from an unverified/mismatched S3 checksum or mixed input version.
- Passing repository archive, evidence package, or graph manifest inline.
- Retrying deterministic invalid/verification/privacy failure as transient.
- Allowing baseline/backfill to consume Tier-1 reserved capacity.
- Marking a run complete before required evidence/review/publication semantics.
- Failing to disable runtime collection in a terminal-path finally action.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| C06-FR-001 | C06 must use Step Functions Standard for baseline, incremental, runtime, verification/proposal, approval-publication, reconciliation, and projection-rebuild workflows. | P0 |
| C06-FR-002 | Run creation must conditionally bind the C03 business identity to one `CollectionRun`; duplicate deliveries must return/reuse the same run or terminal decision. | P0 |
| C06-FR-003 | Every run/stage must pin contract, policy, analyzer, inventory/context/index, commit/artifact/environment, and accepted graph versions applicable to the run. | P0 |
| C06-FR-004 | Large inputs/outputs must pass as immutable S3 URI/version/checksum; C06 must verify checksum/schema before stage start and result acceptance. | P0 |
| C06-FR-005 | The baseline workflow must execute inventory, eligibility, context/index, lane analysis/runtime as required, verification, proposal/review handoff, and approved publication; critical UNKNOWN/incomplete states must prevent false completion. | P0 |
| C06-FR-006 | The incremental workflow must load class/invalidation plan, execute only planned analysis, compare accepted baseline, create a before/after proposal, bind artifact, and publish only after approval. | P0 |
| C06-FR-007 | The runtime workflow must request a signed C11 session, wait for all expected sidecars `READY`, start named tests, drain/persist/verify, disable in a finally path, and pass only terminal completeness to C13. | P0 |
| C06-FR-008 | Verification/proposal workflow must preserve every collector result, hole/conflict/coverage outcome, and route human review without holding workflow compute open indefinitely. | P0 |
| C06-FR-009 | Publication workflow must call C16 with approved immutable manifest, expected prior graph version, and idempotency; retries/redrive must reuse reservation/result rules. | P0 |
| C06-FR-010 | Reconciliation workflows must cover inventory-to-decision/run, deployment-to-lineage, run/stage timeout, event-to-run, full-scan divergence, and projection watermark/rebuild. | P0 |
| C06-FR-011 | Lambda tasks must be bounded control actions; source checkout, full SCA, large reconciliation, verification, and projection preparation must run in AWS Batch. | P0 |
| C06-FR-012 | C06 must apply error-class-specific bounded retry/backoff/jitter, catch/quarantine, DLQ/redrive, and cleanup; deterministic invalid input must not consume repeated capacity. | P0 |
| C06-FR-013 | Stage redrive must reuse verified completed outputs when inputs/versions remain identical and re-execute only invalid/missing/failed dependent stages. | P0 |
| C06-FR-014 | Cancellation/expiry must be authorized/idempotent, stop or detach child work, clean ephemeral resources, run mandatory finally actions, and preserve completed evidence/audit. | P0 |
| C06-FR-015 | Separate scheduling pools must provide Tier-1 incremental reservation, standard incremental borrowing, baseline/backfill exclusion from Tier-1, independent LLM rate/cost limit, isolated runtime stream capacity, and per-domain admission. | P0 |
| C06-FR-016 | Step Functions Distributed Map concurrency must be explicitly below the minimum downstream Batch, Bedrock, SCM, schema, and datastore quota; configured maximum is not assumed safe. | P0 |
| C06-FR-017 | Every run/stage/attempt transition must emit the common correlation contract and a user timeline event with current state, elapsed, retry/redrive, missing evidence, and result reference. | P0 |
| C06-FR-018 | A reconciliation process must detect accepted queue work with no run, nonterminal runs without live execution/lease, orphan child jobs/sessions, and terminal workflows missing durable result. | P0 |
| C06-FR-019 | Capacity/policy/config changes must be versioned/canaried and must not mutate pinned in-flight run semantics. | P1 |

### Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| C06-NFR-001 | Tier-1 incremental work must start within five minutes p95 during representative baseline/backfill and domain-skew load. | P0 |
| C06-NFR-002 | Normal incremental analysis orchestration must finish within 30 minutes p95 excluding human review and deferred post-analysis runtime evidence. | P0 |
| C06-NFR-003 | C06 must coordinate a 10,000-repository baseline within the 12-hour platform window at validated quotas and at least 10,000 deployed-artifact decisions/day. | P0 |
| C06-NFR-004 | Run-control state must be 99.95% available monthly, Multi-AZ, and recover/redrive within C18 RPO/RTO without duplicate business effects. | P0 |

## 7. Data and Durable State

`CollectionRun` includes run ID/type/priority/domain, trigger/business identity,
application/repository/commit/artifact/environment, all pinned versions, current
state/stage, progress, required/optional stage graph, input/result references,
child execution IDs, review/proposal/graph linkage, error/owner action, and
created/updated/terminal timestamps.

`StageAttempt` includes stage/attempt identity, expected prior state, component,
input schema/reference/checksum, budget/quota, lease/heartbeat, child job/token,
start/end, error class/code, retry/redrive relation, output reference/checksum,
metrics, and cleanup status.

`SchedulingDecision` includes priority/pool/domain, requested resource shape,
quota snapshot/policy version, admission/defer reason, queue/start/end time, and
cost tags.

DynamoDB holds run/stage/idempotency/lease state with conditional transitions and
PITR. Step Functions execution history is operational evidence, not sole
authority. C12 S3 holds immutable manifests/results; EventBridge emits timeline
events; CloudWatch/ADOT/CloudTrail cover telemetry/audit.

## 8. Interfaces and Contracts

### Consume work

C06 consumers receive the C03 queue envelope, fetch/validate `EventEnvelope`,
conditionally create/reuse run, then delete SQS only after durable ownership or
terminal prior outcome. Visibility heartbeat extends only while the consumer
owns the run lease.

### Worker invocation

Every task input is:

```text
run/stage/attempt IDs
component operation and contract version
immutable input references/checksums
pinned identity/policy/analyzer/context/graph versions
resource/time/cost budget
callback/result location and correlation
```

Workers conditionally register start/heartbeat/result and write immutable
result before completion callback. A late/stale attempt cannot replace a newer
accepted stage result.

### Commands/status

- `POST /v1/runs/{id}:cancel`, `:redrive`, or `:reconcile` require expected
  version, scoped role, reason, and idempotency.
- `GET /v1/runs/{id}` and `/timeline` return read-model pages/references.
- Events: `collection.run/stage.started|progressed|completed|failed|redriven`,
  `collection.run.awaiting-review`, and terminal outcomes.

## 9. Processing and State Model

### Baseline workflow

```text
REQUESTED -> INVENTORY -> ELIGIBILITY -> CONTEXT -> ANALYSIS_FANOUT
          -> RUNTIME_OPTIONAL -> VERIFY -> PROPOSAL -> AWAITING_REVIEW
          -> PUBLISH -> PROJECTION_READY -> COMPLETE
```

Eligibility fanout produces analysis work only for eligible path units; library,
infrastructure, contract, documentation, and test units feed context/reconcile
actions. Critical unknown remains visible and blocks complete.

### Incremental workflow

```text
RECEIVED -> LOAD_CONTEXT -> INVALIDATION_PLAN -> TARGETED_ANALYSIS
         -> RUNTIME_OPTIONAL -> VERIFY_DIFF -> PROPOSAL
         -> AWAITING_REVIEW -> BIND -> PUBLISH -> COMPLETE
```

`NO_LINEAGE_IMPACT` is terminal only with C04/C05 typed decision/evidence.

### Runtime workflow

```text
REQUEST_SESSION -> ENABLING -> WAIT_READY -> START_TESTS -> COLLECT
                -> DRAIN -> DISABLE -> ACCEPT_RESULT
```

Every state enters a finally chain that requests disable/expiry confirmation.
`INCOMPLETE`/`TRUNCATED` results reach C13 but cannot promote confidence.

### Retry/redrive rule

Before reuse, C06 verifies stage input refs/checksums/versions equal the accepted
attempt and all dependent policies still permit reuse. Otherwise it creates a
new attempt and invalidates dependent results. Human review is externalized:
the run transitions to awaiting review and resumes from a decision event rather
than keeping an execution open without bound.

## 10. Failure Semantics

| Code | Class | Required behavior |
|---|---|---|
| `RUN_IDEMPOTENCY_CONFLICT` | `CONFLICT` | Preserve both checksums; no second run |
| `INPUT_REFERENCE_INVALID` | `DETERMINISTIC_INVALID` | Quarantine stage; do not invoke worker |
| `DOWNSTREAM_THROTTLED` | `TRANSIENT` | Bounded backoff/admission defer; retain priority/age |
| `WORKER_HEARTBEAT_LOST` | `TRANSIENT`/`POISON_REPEATED` | Verify child/lease, cancel/orphan-reconcile, retry policy |
| `REQUIRED_STAGE_INCOMPLETE` | `INCOMPLETE` | Surface gap; block false complete/promotion |
| `STALE_STAGE_RESULT` | `CONFLICT` | Reject late callback; retain attempt evidence |
| `RUNTIME_DISABLE_UNCONFIRMED` | `INCOMPLETE` security-critical | Retry/expire/alert; no complete result |
| `REVIEW_VERSION_CONFLICT` | `CONFLICT` | Wait for current proposal/decision; no blind resume |
| `PUBLICATION_VERSION_CONFLICT` | `CONFLICT` | Rebase/supersede through C15/C16; active pointer unchanged |
| `ORPHAN_WORK_DETECTED` | `INCOMPLETE` operational | Reconcile/cancel/adopt under runbook and audit |

## 11. Security and Privacy

| ID | Requirement | Priority |
|---|---|---|
| C06-SEC-001 | Each workflow/task must use a component/operation-specific role limited to exact queue, state, S3 prefixes, KMS keys, job definitions, and callback actions; no wildcard data-plane role. | P0 |
| C06-SEC-002 | Workflow state/logs/events must contain metadata and immutable references only; repository contents, runtime payloads, credentials, and Bedrock prompts/results remain in restricted stores. | P0 |
| C06-SEC-003 | Cancel/redrive/replay/admission override/config activation must require scoped authorization, reason, expected version, and CloudTrail/audit. | P0 |
| C06-SEC-004 | Batch workspaces must be ephemeral/encrypted, use short-lived source credentials/controlled egress, and prove cleanup at terminal/cancel. | P0 |
| C06-SEC-005 | Runtime production hard-deny and finally disable/expiry must be encoded as independent policy/control tasks that analysis/test success cannot bypass. | P0 |

## 12. Scale, Performance, and Availability

Capacity formula:

```text
requiredConcurrency = repositoryCount * meanJobMinutes
                      / (targetWindowMinutes * utilization)
```

For 10,000 repositories, 15-minute mean, 12 hours, 70% utilization, plan about
298 slots and initially quota/load-test 500. Incremental demand reserves
separate priority capacity. Resource shapes/timeout vary by measured archetype
and repository size; one domain cannot consume all slots.

Distributed Map input/output is an S3 manifest. MaxConcurrency is calculated
from validated downstream quotas and safety margin. Admission controllers expose
queue age and borrow/reserve decisions. Workflows use Standard durability/redrive
and Multi-AZ managed services; warm-Region IaC/state/evidence supports RPO/RTO.

## 13. Observability

| ID | Signal | Dimensions/alert | Priority |
|---|---|---|---|
| C06-OBS-001 | Run/stage count/latency/status | type/stage/priority/domain/archetype/version | P0 |
| C06-OBS-002 | Queue-to-start and admission defer | pool/priority/domain; Tier-1 SLO alert | P0 |
| C06-OBS-003 | Retry/redrive/orphan/heartbeat | component/error/attempt/runbook | P0 |
| C06-OBS-004 | Concurrency/quota/utilization | Batch shape, Map, Bedrock, source/datastore | P0 |
| C06-OBS-005 | Incomplete/missing evidence/UNKNOWN | application/repository/stage/owner | P0 |
| C06-OBS-006 | Runtime cleanup | session state, disable/expiry confirmation; security alert | P0 |
| C06-OBS-007 | Cost | run/stage/application/domain/lane/cache hit | P1 |

Every transition includes the common correlation contract. Metrics reconcile C03
accepted work to run/no-impact/deferred/quarantine and run stages to immutable
results. C17 timeline uses a purpose-built read model rather than Step Functions
console access.

## 14. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| C06-AC-001 | Given a mixed business application, the baseline workflow routes every class/path correctly and reaches review/publish only after required context/evidence/verification. |
| C06-AC-002 | Given a determinant-bounded change, the incremental workflow invokes only planned workloads and produces a complete before/after proposal relative to the pinned baseline. |
| C06-AC-003 | Given duplicate/out-of-order queue delivery, one run/business effect occurs and all delivery/attempt history remains visible. |
| C06-AC-004 | Given failure after completed expensive stages, redrive reuses matching checksummed outputs and reruns only failed/invalid dependents. |
| C06-AC-005 | Given runtime test failure, sidecar crash, timeout, or cancel, the finally path disables/expires collection and passes exact completeness without promotion. |
| C06-AC-006 | Given baseline/backfill plus 10,000 deployment work, Tier-1 starts within five minutes p95 and lower priority cannot consume reservation. |
| C06-AC-007 | Given stale callback/lease or expected graph conflict, C06 rejects the stale side effect and routes governed recompute/rebase without changing active state. |
| C06-AC-008 | Given Region/process failure, reconciliation finds orphan/missing state and recovery/redrive meets RPO/RTO without duplicate proposal/publication. |

## 15. Component Test Matrix

| ID | Level | Fixture/precondition | Action | Expected result | Retained evidence |
|---|---|---|---|---|---|
| C06-CT-001 | State-machine assertion | Baseline/incremental/runtime/publish definitions | Synthesize/inspect | Required states/catches/finally/refs and no unsafe Lambda analysis | CDK/ASL assertion |
| C06-CT-002 | Baseline integration harness | Mixed app manifest incl UNKNOWN | Execute | Correct fanout; UNKNOWN prevents false complete; outputs pinned | Execution/result manifest |
| C06-CT-003 | Incremental | Config/library/infra/docs/contract/test plans | Execute | Exactly planned jobs/no-impact/review paths | Job/run comparison |
| C06-CT-004 | Idempotency/order | Duplicate/out-of-order SQS events | Consume concurrently | One run/effect; attempts/events preserved | State/event counts |
| C06-CT-005 | Retry classification | Transient versus deterministic worker failures | Execute | Only transient bounded retry; invalid quarantined | History/metrics |
| C06-CT-006 | Redrive | Fail after two expensive completed stages | Redrive | Reuse exact outputs; rerun failed/dependents only | Attempt/output refs |
| C06-CT-007 | Runtime cleanup | Test failure, sidecar crash, cancel, expiry | Execute | Finally disable/expiry confirmed; incomplete no-promotion | Session/workflow/audit |
| C06-CT-008 | Stale result | Worker loses lease then returns | Callback | Result rejected; newer attempt remains authoritative | Conditional state/audit |
| C06-CT-009 | Security | Oversized inline/sensitive state and unauthorized redrive | Invoke | Reject/deny; no sensitive history; audit | ASL/log scan/audit |
| C06-CT-010 | Fairness/load | 10,000 baseline/deploy events, domain skew, constrained slots | Schedule | Reservation/borrowing/per-domain and SLOs pass | Load/scheduling report |
| C06-CT-011 | Reconciliation | Missing run, stuck state, orphan Batch/session, missing result | Reconcile | Exact findings and safe cancel/adopt/redrive action | Reconciliation report |
| C06-CT-012 | DR | Region interruption with in-flight stages | Recover warm Region/redrive | RPO/RTO and no duplicate effects; pinned refs intact | Recovery exercise |

## 16. Integration Obligations

- **INT-034 C03↔C06:** every accepted route maps to one run/no-impact/deferred
  outcome under duplicate/out-of-order/load/replay.
- **INT-035 C04/C05↔C06:** classes, lanes, context, and invalidation manifests
  produce exact scheduled work with pinned versions.
- **INT-036 C06↔C07-C10:** Batch/native/agent/opaque analysis inputs, budgets,
  callbacks, checksum validation, retry, and cache reuse interoperate.
- **INT-037 C06↔C11:** session readiness/test/drain/disable finally/completeness
  flows pass every terminal/failure case.
- **INT-038 C06↔C12/C13:** immutable stage artifacts feed verification once;
  incomplete/conflict/stale attempts cannot promote or overwrite.
- **INT-039 C06↔C15/C16:** review externalization/resume and fenced publication
  handle correction, rejection, stale decision, redrive, and version conflict.
- **INT-040 C06↔C17:** user timeline is complete/correlated and supports bounded
  cancel/redrive authorization without console access.
- **INT-041 C06↔C18:** quotas/fairness, alarms/runbooks, orphan reconciliation,
  chaos, cost, and cross-Region recovery pass.

## 17. Definition of Done

- IaC and versioned ASL/task contracts implement every required workflow, queue/
  compute pool, run/stage state, admission rule, and reconciliation process.
- C06 P0 requirements and C06-CT-001 through C06-CT-012 pass.
- INT-034 through INT-041 pass in a production-like nonproduction environment.
- Baseline/incremental/runtime/review/publication/reconciliation steel threads
  retain execution/result IDs and prove required negative/finally paths.
- Enterprise load proves 12-hour baseline capacity, daily decisions, Tier-1
  latency/fairness, exact event/run/result reconciliation, and quota headroom.
- Security/privacy, cancellation, redrive, orphan, quota, and DR runbooks are
  exercised; dashboards/alarms link real evidence.

## 18. Implementation Notes

```text
contracts/schemas/runs/
infra/lib/stacks/workflow-stack.ts
infra/lib/constructs/lineage-workflows.ts
infra/lib/constructs/batch-capacity.ts
services/run-controller/
services/run-timeline/
tests/contract/workflows/
tests/integration/workflows/
tests/load/scheduling/
tests/chaos/workflows/
```

Use TypeScript 5/CDK v2 for control services/IaC. Step Functions Standard owns
coordination, Distributed Map reads S3 manifests, Lambda performs bounded
control tasks, Batch performs heavy jobs. Use callback tokens only with strict
attempt/lease/state validation and timeout. Do not implement a custom scheduler
inside Lambda.

Build order: run/stage contracts/idempotency; compute/priority pools; baseline;
incremental; runtime finally; verify/review/publish; reconciliation/timeline;
load/chaos/DR. Canary new workflow versions for new runs; in-flight runs remain
pinned to their definition/policy.

## 19. Traceability

| Source decision | C06 requirements | Component evidence | Integration/launch evidence |
|---|---|---|---|
| Step Functions coordinates, Batch analyzes, Lambda controls | C06-FR-001/004/011/016 | C06-CT-001/009 | INT-036/038 |
| Baseline/incremental/runtime/review/publish flows | C06-FR-005 through C06-FR-010 | C06-CT-002/003/007 | INT-035/037/039 |
| Idempotency/retry/redrive/reconcile | C06-FR-002/003/012-014/018 | C06-CT-004/005/006/008/011 | INT-034/038/041 |
| Priority fairness/enterprise scale | C06-FR-015/016; C06-NFR-001-003 | C06-CT-010 | Enterprise load/fairness gate |
| Security/finally/DR/visibility | C06-SEC-001 through C06-SEC-005; C06-FR-017 | C06-CT-007/009/012 | INT-037/040/041 |
