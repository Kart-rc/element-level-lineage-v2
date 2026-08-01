# AWS Lineage Collection Platform Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a production-ready AWS platform that inventories and classifies up to 10,000 repositories, generates business-application baseline lineage, performs determinant-based incremental updates, collects metadata-only integration-test runtime evidence, and publishes only human-approved lineage with complete evidence, confidence, audit, resilience, and operational visibility.

**Architecture:** EventBridge routes normalized triggers, priority SQS queues absorb spikes, and Step Functions coordinates baseline, incremental, runtime, and publication workflows. AWS Batch executes containerized analysis; Bedrock receives only named unresolved holes; AppConfig controls metadata-only integration sidecars; a validation Lambda assigns per-sidecar Kinesis partitions; S3 is immutable truth; DynamoDB holds operational state; Neptune and OpenSearch are rebuildable approved projections.

**Tech Stack:** TypeScript 5 and AWS CDK v2 for infrastructure/control services; Python 3.12 for analyzers, verification, confidence, and projection workers; Go 1.24 for the runtime sidecar; React and TypeScript for the review UI; JSON Schema and OpenAPI contracts; Jest/CDK assertions, pytest, Go tests, Vitest, Playwright, and controlled AWS load/chaos harnesses.

---

## Execution Rules

- Read `docs/plans/2026-08-01-aws-lineage-collection-architecture-design.md` first.
- Work in a dedicated feature worktree.
- Use test-driven development and commit after every task.
- Pass large payloads by immutable S3 URI and checksum.
- Never add raw payloads or unbounded property maps to runtime evidence.
- Treat EventBridge, SQS, Kinesis, and workflow delivery as duplicateable.
- Do not implement production auto-publication.
- Do not infer lineage from a CloudWatch interaction alone.
- Do not let an LLM automatically exclude repositories or emit uncited edges.
- Run the task test after each change and the full suite at every phase gate.

## Proposed Repository Layout

```text
contracts/{schemas,openapi,examples}/
infra/{bin,lib,test}/
services/{event-normalizer,eligibility,context-builder,runtime-controller,proposal-api,query-api,run-timeline}/
workers/{analyzer,verifier,projector}/
sidecars/lineage-observer/
web/review-ui/
tests/{contract,integration,load,chaos,e2e,fixtures}/
docs/{adr,runbooks}/
```

## Phase Gates

| Gate | Evidence required |
|---|---|
| Foundation | Synthesized CDK, contract suite, encrypted immutable stores, idempotent intake |
| Baseline | Synthetic business-application baseline with eligibility and approval |
| Incremental | Determinant-bounded diff for application, library, infrastructure, documentation, mixed, and unknown changes |
| Runtime | Metadata-only evidence, production hard-deny, completeness reconciliation |
| Publication | Reviewer-controlled fenced publication and rebuildable projections |
| Enterprise | 10,000-repository load, spike fairness, chaos, privacy, security, and DR gates |

### Task 1: Scaffold the Workspace and Record Architecture Decisions

**Files:**
- Create: `package.json`
- Create: `tsconfig.base.json`
- Create: `infra/package.json`
- Create: `infra/tsconfig.json`
- Create: `workers/analyzer/pyproject.toml`
- Create: `workers/verifier/pyproject.toml`
- Create: `workers/projector/pyproject.toml`
- Create: `sidecars/lineage-observer/go.mod`
- Create: `docs/adr/0001-control-plane-and-compute.md`
- Create: `docs/adr/0002-authoritative-data-and-projections.md`
- Create: `docs/adr/0003-runtime-evidence-privacy.md`
- Test: `tests/contract/test_workspace_layout.py`

**Step 1: Write the failing workspace test**

Assert that every directory exists and the ADRs contain:

- EventBridge routes; SQS buffers; Step Functions coordinates.
- S3 manifests are authoritative; Neptune/OpenSearch are projections.
- Runtime evidence is integration-only and metadata-only.

**Step 2: Verify failure**

Run:

```bash
python -m pytest tests/contract/test_workspace_layout.py -v
```

Expected: FAIL because the workspace does not exist.

**Step 3: Add the minimal workspace**

Use npm workspaces for infrastructure, control services, and web code. Pin CDK
and TypeScript in the lockfile. Define Python projects with pytest and ruff.
Initialize the observer:

```go
module github.com/enterprise/lineage-observer

go 1.24
```

Each ADR contains Context, Decision, Alternatives, Consequences, and Review
Date.

**Step 4: Verify**

```bash
python -m pytest tests/contract/test_workspace_layout.py -v
npm install
npm run typecheck --workspaces --if-present
go test ./sidecars/lineage-observer/...
```

Expected: PASS.

**Step 5: Commit**

```bash
git add package.json package-lock.json tsconfig.base.json infra workers sidecars docs/adr tests/contract
git commit -m "build: scaffold lineage platform workspace"
```

### Task 2: Define Canonical Contracts Before Services

**Files:**
- Create: `contracts/schemas/event-envelope.schema.json`
- Create: `contracts/schemas/repository-event.schema.json`
- Create: `contracts/schemas/repository-eligibility.schema.json`
- Create: `contracts/schemas/application-context.schema.json`
- Create: `contracts/schemas/runtime-session.schema.json`
- Create: `contracts/schemas/runtime-evidence.schema.json`
- Create: `contracts/schemas/analysis-package.schema.json`
- Create: `contracts/schemas/lineage-proposal.schema.json`
- Create: `contracts/schemas/accepted-manifest.schema.json`
- Create: `contracts/openapi/review-api.yaml`
- Create: `contracts/examples/`
- Test: `tests/contract/test_json_schemas.py`
- Test: `tests/contract/test_runtime_evidence_privacy.py`

**Step 1: Write failing contract tests**

Assert:

- Events include event ID/type/time, organization, correlation, schema version,
  and typed data.
- Repository changes contain repository/commit and optional artifact digest.
- SCM idempotency requires commit SHA; deployment idempotency requires artifact
  digest and environment. Missing immutable identities cannot collapse to an
  empty shared key.
- Eligibility uses only approved classes.
- Runtime evidence has no raw value, payload, body, header, SQL parameter,
  credential, or generic attributes map.
- Proposals contain base version, before/after diff, both confidence axes,
  evidence, holes, and review state.
- Accepted manifests contain reviewer, time, proposal version, checksum, and
  expected prior graph version.

Use:

```python
FORBIDDEN_RUNTIME_KEYS = {
    "value", "rawValue", "payload", "body", "requestBody",
    "responseBody", "sqlParameters", "credentials", "headers",
}
```

**Step 2: Verify failure**

```bash
python -m pytest tests/contract/test_json_schemas.py tests/contract/test_runtime_evidence_privacy.py -v
```

Expected: FAIL.

**Step 3: Implement schemas**

Set `additionalProperties: false` at every runtime-evidence boundary. Model
extensions as typed, versioned variants. Structural and derivational confidence
are separate:

```json
{
  "band": "UNCALIBRATED",
  "evidenceRefs": ["s3://evidence/checksum"],
  "policyVersion": "confidence-v1",
  "calibrated": false
}
```

**Step 4: Verify**

```bash
python -m pytest tests/contract -v
```

Expected: PASS.

**Step 5: Commit**

```bash
git add contracts tests/contract
git commit -m "feat: define lineage platform contracts"
```

### Task 3: Build Immutable Evidence and Control-State Foundations

**Files:**
- Create: `infra/lib/config/environments.ts`
- Create: `infra/lib/constructs/evidence-store.ts`
- Create: `infra/lib/constructs/control-tables.ts`
- Create: `infra/lib/stacks/data-stack.ts`
- Test: `infra/test/data-stack.test.ts`

**Step 1: Write failing CDK assertions**

Assert:

- S3 versioning, KMS, TLS-only policy, public-access block, lifecycle,
  replication hooks, and Object Lock.
- Separate roles/prefixes for raw evidence, proposals, accepted manifests, and
  graph exports.
- DynamoDB tables for runs, idempotency, eligibility/dependencies/determinants,
  runtime sessions, proposals, and graph pointers.
- PITR and deletion protection on durable tables.
- TTL only on leases and temporary session records.
- No wildcard data-plane permissions.

**Step 2: Verify failure**

```bash
npm test --workspace infra -- data-stack.test.ts
```

Expected: FAIL.

**Step 3: Implement narrow grant methods**

Expose methods such as:

```ts
evidenceStore.grantWriteAnalyzerOutput(analyzerRole);
controlTables.grantIdempotency(eventNormalizerRole);
controlTables.grantProposalTransition(proposalApiRole);
```

Do not expose `grantReadWriteAll`.

**Step 4: Verify**

```bash
npm test --workspace infra -- data-stack.test.ts
npm run cdk --workspace infra -- synth
```

Expected: PASS with no public buckets or unencrypted tables.

**Step 5: Commit**

```bash
git add infra/lib/config infra/lib/constructs infra/lib/stacks infra/test
git commit -m "feat: add immutable evidence and control state"
```

### Task 4: Implement Event Intake and Priority Queues

**Files:**
- Create: `services/event-normalizer/src/adapters/scm-webhook.ts`
- Create: `services/event-normalizer/src/adapters/deployment-event.ts`
- Create: `services/event-normalizer/src/handler.ts`
- Create: `services/event-normalizer/src/idempotency.ts`
- Create: `services/event-normalizer/test/scm-webhook.test.ts`
- Create: `services/event-normalizer/test/deployment-event.test.ts`
- Create: `services/event-normalizer/test/handler.test.ts`
- Create: `infra/lib/constructs/event-intake.ts`
- Create: `infra/lib/stacks/control-plane-stack.ts`
- Test: `infra/test/control-plane-stack.test.ts`

**Step 1: Write failing tests**

Cover authenticated SCM webhook and deployment-event adaptation, canonical
normalization, duplicate replay, source-specific immutable identities,
distinct Tier-1/incremental/baseline/backfill routing, DLQs, encryption,
queue-age alarms, and EventBridge archive.

Assert SCM keys include `commitSha` and deployment keys include
`artifactDigest + environment`. Reject SCM events without a commit SHA and
quarantine deployment events without a digest.

**Step 2: Verify failure**

```bash
npm test --workspace services/event-normalizer
npm test --workspace infra -- control-plane-stack.test.ts
```

Expected: FAIL.

**Step 3: Implement**

Validate and authenticate source adapters before recording idempotency. Invalid
events go to a rejected-event store with reason codes. Use event-type-specific
keys so separate pre-deployment commits cannot deduplicate each other. Connect
analysis through SQS, never directly from EventBridge.

**Step 4: Verify**

```bash
npm test --workspace services/event-normalizer
npm test --workspace infra
```

Expected: PASS.

**Step 5: Commit**

```bash
git add services/event-normalizer infra
git commit -m "feat: add idempotent lineage event intake"
```

### Task 5: Implement Repository Eligibility

**Files:**
- Create: `services/eligibility/src/classify.ts`
- Create: `services/eligibility/src/precedence.ts`
- Create: `services/eligibility/src/registry.ts`
- Create: `services/eligibility/src/handler.ts`
- Create: `services/eligibility/test/classify.test.ts`
- Create: `tests/fixtures/repositories/`

**Step 1: Write failing classification tests**

Cover application, pipeline, library, Terraform-only infrastructure, pure
documentation, documentation with OpenAPI/Avro, test automation, mixed
monorepo, mis-tagged deployable image, conflicting evidence, and expired
override.

Expected:

- Governed inclusion wins over heuristic exclusion.
- Machine-readable schema is CONTRACT_SCHEMA_SOURCE.
- Conflicts become UNKNOWN.
- LLM suggestion cannot set `eligible=false`.
- Every exclusion has reasons, evidence, policy, owner, and review metadata.

**Step 2: Verify failure**

```bash
npm test --workspace services/eligibility
```

Expected: FAIL.

**Step 3: Implement deterministic precedence**

```ts
type RepositoryClass =
  | "APPLICATION_RUNTIME"
  | "DATA_PIPELINE"
  | "CONTRACT_SCHEMA_SOURCE"
  | "SHARED_LIBRARY"
  | "INFRASTRUCTURE"
  | "DOCUMENTATION"
  | "TEST_AUTOMATION"
  | "MIXED_MONOREPO"
  | "UNKNOWN";
```

Persist current decisions in DynamoDB and immutable history in S3. Reclassify
when metadata/content signature or policy changes.

**Step 4: Verify**

```bash
npm test --workspace services/eligibility
```

Expected: PASS.

**Step 5: Commit**

```bash
git add services/eligibility tests/fixtures/repositories
git commit -m "feat: add reviewable repository eligibility"
```

### Task 6: Build Application Context and the Dependency Index

**Files:**
- Create: `services/context-builder/src/test-automation-client.ts`
- Create: `services/context-builder/src/scm-client.ts`
- Create: `services/context-builder/src/deployment-client.ts`
- Create: `services/context-builder/src/cloudwatch-context.ts`
- Create: `services/context-builder/src/native-lineage.ts`
- Create: `services/context-builder/src/dependencies.ts`
- Create: `services/context-builder/src/build-context.ts`
- Create: `services/context-builder/test/build-context.test.ts`
- Create: `services/context-builder/test/connectors.test.ts`
- Create: `tests/fixtures/application-context/`

**Step 1: Write failing context tests**

Assert:

- Active repositories come from the Test Automation Service.
- Each active repository resolves to an immutable SCM commit and current
  deployed artifact digest through explicit connector interfaces.
- Missing or conflicting deployment evidence is retained as a context gap and
  never silently replaced with the repository default branch.
- Association evidence retains its source and precedence.
- Production CloudWatch data creates interaction context only.
- Libraries map to consumers plus pinned versions/digests.
- Infrastructure maps routes/topics/queues/endpoints/config to applications.
- Test scenarios map to applications and expected runtime sidecars.
- Snapshots are immutable, content-addressed, and schema-valid.

**Step 2: Verify failure**

```bash
npm test --workspace services/context-builder
```

Expected: FAIL.

**Step 3: Implement connectors behind interfaces**

Implement the Test Automation, SCM, deployment/artifact, and CloudWatch
connectors behind typed interfaces. Persist RepositoryInventorySnapshot,
ApplicationContextSnapshot, current dependency entries, and immutable
dependency history. Mark service calls as `INTERACTION`; require an explicit
governed mapping before lineage projection.

**Step 4: Verify**

```bash
npm test --workspace services/context-builder
python -m pytest tests/contract -v
```

Expected: PASS.

**Step 5: Commit**

```bash
git add services/context-builder tests/fixtures/application-context
git commit -m "feat: build application context and dependency index"
```

### Task 7: Create the Analyzer Job Framework and Cache

**Files:**
- Create: `workers/analyzer/src/lineage_analyzer/models.py`
- Create: `workers/analyzer/src/lineage_analyzer/router.py`
- Create: `workers/analyzer/src/lineage_analyzer/cache.py`
- Create: `workers/analyzer/src/lineage_analyzer/holes.py`
- Create: `workers/analyzer/src/lineage_analyzer/adapters/native.py`
- Create: `workers/analyzer/src/lineage_analyzer/adapters/sca.py`
- Create: `workers/analyzer/src/lineage_analyzer/adapters/rules.py`
- Create: `workers/analyzer/src/lineage_analyzer/adapters/bedrock_residual.py`
- Create: `workers/analyzer/src/lineage_analyzer/main.py`
- Create: `workers/analyzer/tests/test_router.py`
- Create: `workers/analyzer/tests/test_cache.py`
- Create: `workers/analyzer/tests/test_native_adapter.py`
- Create: `workers/analyzer/tests/test_sca_adapter.py`
- Create: `workers/analyzer/tests/test_rules_adapter.py`
- Create: `workers/analyzer/tests/test_bedrock_residual.py`
- Create: `workers/analyzer/Dockerfile`
- Create: `infra/lib/constructs/analyzer-batch.ts`
- Create: `infra/lib/constructs/bedrock-residual.ts`
- Test: `infra/test/analyzer-batch.test.ts`
- Test: `infra/test/bedrock-residual.test.ts`

**Step 1: Write failing tests**

Cover native-plan adapters, deterministic SCA extraction, governed rules,
substrate routing, deterministic repeatability, named holes, LLM-only hole
invocation, full cache-key versioning, S3 checkpoints, and separate
incremental/baseline/backfill/residual Batch queues.

Assert Bedrock is not invoked when no named hole remains; its request contains
only the bounded hole context and approved code/AST slice, never runtime
payloads; its response is schema-valid and evidence-cited; timeout, throttling,
or invalid output leaves the hole unresolved. CDK assertions restrict
`bedrock:InvokeModel` to approved model ARNs and only the residual job role.

The residual cache key is:

```text
codeSliceHash + schemaHash + modelVersion + promptVersion + policyVersion
```

**Step 2: Verify failure**

```bash
python -m pytest workers/analyzer/tests -v
npm test --workspace infra -- analyzer-batch.test.ts
npm test --workspace infra -- bedrock-residual.test.ts
```

Expected: FAIL.

**Step 3: Implement concrete analyzers and the job protocol**

Implement versioned adapters for native substrate plans, deterministic static
code analysis, and governed mapping rules. Route their evidence into named
holes before constructing any bounded Bedrock residual request. Bedrock output
remains proposed evidence and cannot publish or exclude a repository.

Each job receives an S3 manifest URI, checksum, correlation IDs, and output
prefix. It writes a schema-valid AnalysisPackage and stage manifest. Never put
source code or large results in Step Functions state.

Use Fargate for small incremental jobs, EC2 On-Demand for baseline floor, and
Spot for interruptible baseline/backfill.

**Step 4: Verify**

```bash
python -m pytest workers/analyzer/tests -v
npm test --workspace infra -- analyzer-batch.test.ts
npm test --workspace infra -- bedrock-residual.test.ts
```

Expected: PASS.

**Step 5: Commit**

```bash
git add workers/analyzer infra/lib/constructs/analyzer-batch.ts infra/lib/constructs/bedrock-residual.ts infra/test/analyzer-batch.test.ts infra/test/bedrock-residual.test.ts
git commit -m "feat: add concrete scalable lineage analyzers"
```

### Task 8: Implement the Business-Application Baseline Workflow

**Files:**
- Create: `infra/lib/constructs/baseline-workflow.ts`
- Create: `infra/test/baseline-workflow.test.ts`
- Create: `tests/integration/test_baseline_workflow.py`
- Create: `tests/fixtures/baseline/ten-application-estate.json`

**Step 1: Write failing workflow assertions**

Assert the workflow:

1. Builds inventory and application context.
2. Classifies every repository.
3. Blocks critical UNKNOWN repositories.
4. Writes a unique-digest manifest to S3.
5. Uses Distributed Map with configurable concurrency.
6. Runs analyzer jobs and aggregates all outcomes.
7. Verifies and creates a baseline proposal.
8. Ends at AWAITING_REVIEW, not publication.
9. Exposes all stages in the run ledger.
10. Supports failure threshold and failed-child redrive.
11. Sends shared-library, infrastructure, documentation, and test-only
    repositories only through metadata/dependency indexing, never standalone
    workload analysis.
12. Invokes Bedrock only for named holes and runtime tests only when the
    evidence plan explicitly requires them.

**Step 2: Verify failure**

```bash
npm test --workspace infra -- baseline-workflow.test.ts
python -m pytest tests/integration/test_baseline_workflow.py -v
```

Expected: FAIL.

**Step 3: Implement Standard parent and child workflows**

Use S3 ItemReader/ResultWriter. Configure concurrency by environment and
downstream quotas; never use the service maximum as a target.

**Step 4: Verify**

Run the commands from Step 2.

Expected: PASS with a reviewable proposal and explicit
included/excluded/mixed/unknown counts.

**Step 5: Commit**

```bash
git add infra/lib/constructs/baseline-workflow.ts infra/test/baseline-workflow.test.ts tests/integration/test_baseline_workflow.py tests/fixtures/baseline
git commit -m "feat: orchestrate business application baselines"
```

### Task 9: Implement Determinant-Based Incremental Updates

**Files:**
- Create: `services/context-builder/src/determinants.ts`
- Create: `infra/lib/constructs/incremental-workflow.ts`
- Create: `infra/test/incremental-workflow.test.ts`
- Create: `tests/integration/test_incremental_routing.py`
- Create: `tests/fixtures/incremental/`

**Step 1: Write failing routing tests**

Cover:

- Application code affecting one edge.
- Configuration selecting a new implementation.
- Library serializer used by two of five consumers.
- Library change absent from deployed consumers.
- Infrastructure capacity/tag change.
- Infrastructure topic/binding/schema-reference change.
- Documentation-only and contract changes.
- Test-scenario change.
- Mixed monorepo paths.
- UNKNOWN hold/replay.
- Stale baseline fallback.
- No Bedrock call when deterministic analysis leaves no named hole.
- No runtime session when the accepted baseline and change evidence are
  sufficient; selected integration tests run only for a named evidence gap.

**Step 2: Verify failure**

```bash
python -m pytest tests/integration/test_incremental_routing.py -v
npm test --workspace infra -- incremental-workflow.test.ts
```

Expected: FAIL.

**Step 3: Implement class-specific invalidation**

- Serialize relevant work with repository/application leases.
- Emit explainable NO_LINEAGE_IMPACT records.
- Analyze consumers, not a library as a standalone producer.
- Activate library effects only with a consuming application artifact.
- Resolve contract/schema changes to connected producers and consumers before
  targeted analysis.
- Update test-scenario coverage and runtime-evidence freshness without running
  standalone SCA on a test-automation repository; recollect only when needed.
- Produce added, removed, modified, confidence, unresolved, and coverage diffs.
- End material changes at AWAITING_REVIEW.

**Step 4: Verify**

Run the commands from Step 2.

Expected: PASS.

**Step 5: Commit**

```bash
git add services/context-builder/src/determinants.ts infra/lib/constructs/incremental-workflow.ts infra/test/incremental-workflow.test.ts tests/integration/test_incremental_routing.py tests/fixtures/incremental
git commit -m "feat: add determinant-based incremental lineage"
```

### Task 10: Implement the Metadata-Only Runtime Sidecar

**Files:**
- Create: `sidecars/lineage-observer/internal/evidence/model.go`
- Create: `sidecars/lineage-observer/internal/evidence/fingerprint.go`
- Create: `sidecars/lineage-observer/internal/session/session.go`
- Create: `sidecars/lineage-observer/internal/output/cloudwatch.go`
- Create: `sidecars/lineage-observer/cmd/observer/main.go`
- Create: `sidecars/lineage-observer/internal/evidence/model_test.go`
- Create: `sidecars/lineage-observer/internal/evidence/privacy_test.go`
- Create: `sidecars/lineage-observer/internal/session/session_test.go`
- Create: `sidecars/lineage-observer/Dockerfile`

**Step 1: Write failing privacy/lifecycle tests**

Assert:

- Evidence serializes only approved fields.
- Reflection finds no raw value/body/payload/header/credential field.
- Unknown JSON properties fail.
- HMAC is stable inside a session and different across sessions.
- Sensitive/low-cardinality fields are excluded.
- Expired or production sessions refuse collection.
- Sequence numbers are monotonic.
- Closing manifest has sequence range, count, checksum, and sidecar ID.
- Output failure never blocks the application.

**Step 2: Verify failure**

```bash
go test ./sidecars/lineage-observer/... -race
```

Expected: FAIL.

**Step 3: Implement the observer**

Receive typed instrumented metadata through a local Unix socket or localhost
endpoint. Do not proxy traffic or accept arbitrary maps. Use bounded buffers
and explicit truncation. Emit CloudWatch records and a closing manifest. The
container is nonessential.

**Step 4: Verify**

```bash
go test ./sidecars/lineage-observer/... -race
go vet ./sidecars/lineage-observer/...
```

Expected: PASS.

**Step 5: Commit**

```bash
git add sidecars/lineage-observer
git commit -m "feat: add metadata-only lineage observer"
```

### Task 11: Implement Runtime Session Control and Streaming

**Files:**
- Create: `services/runtime-controller/src/session.ts`
- Create: `services/runtime-controller/src/appconfig-validator.ts`
- Create: `services/runtime-controller/src/reconcile.ts`
- Create: `services/runtime-controller/test/session.test.ts`
- Create: `services/runtime-ingress/src/handler.ts`
- Create: `services/runtime-ingress/src/validate.ts`
- Create: `services/runtime-ingress/test/handler.test.ts`
- Create: `infra/lib/constructs/runtime-evidence.ts`
- Create: `infra/lib/constructs/runtime-workflow.ts`
- Create: `infra/test/runtime-evidence.test.ts`
- Create: `tests/integration/test_runtime_session.py`

**Step 1: Write failing tests**

Cover artifact/test/environment/expiry binding, production rejection, READY
barrier, finally-path disable, independent expiry, governed CloudWatch
subscription, validation-router rejection of prohibited fields,
`runtimeSessionId + sidecarId` Kinesis partition assignment, duplicate and
out-of-order delivery, per-sidecar sequence/manifest reconciliation, and
INCOMPLETE confidence suppression. Assert that a direct CloudWatch-to-Kinesis
subscription is not configured.

**Step 2: Verify failure**

```bash
npm test --workspace services/runtime-controller
npm test --workspace services/runtime-ingress
npm test --workspace infra -- runtime-evidence.test.ts
python -m pytest tests/integration/test_runtime_session.py -v
```

Expected: FAIL.

**Step 3: Implement lifecycle**

```text
REQUESTED -> ENABLING -> READY -> COLLECTING -> DRAINING
          -> DISABLED -> COMPLETE
```

Support INCOMPLETE, FAILED, EXPIRED, CANCELLED, and TRUNCATED. Store evidence in
S3 and state in DynamoDB. Route governed CloudWatch subscription batches
through the validation Lambda, then call Kinesis PutRecords with
`runtimeSessionId + sidecarId` as the explicit partition key. Treat Kinesis
ordering as per-sidecar only; COMPLETE requires every expected closing manifest
and sequence range after persisted evidence has drained. Production roles
receive no evidence-write permission.

**Step 4: Verify**

Run the commands from Step 2.

Expected: PASS, including timeout and production-deny cases.

**Step 5: Commit**

```bash
git add services/runtime-controller services/runtime-ingress infra/lib/constructs/runtime-evidence.ts infra/lib/constructs/runtime-workflow.ts infra/test/runtime-evidence.test.ts tests/integration/test_runtime_session.py
git commit -m "feat: control integration runtime evidence sessions"
```

### Task 12: Build Verification and Two-Axis Confidence

**Files:**
- Create: `workers/verifier/src/lineage_verifier/models.py`
- Create: `workers/verifier/src/lineage_verifier/gates.py`
- Create: `workers/verifier/src/lineage_verifier/confidence.py`
- Create: `workers/verifier/src/lineage_verifier/diff.py`
- Create: `workers/verifier/src/lineage_verifier/main.py`
- Create: `workers/verifier/tests/test_gates.py`
- Create: `workers/verifier/tests/test_confidence.py`
- Create: `workers/verifier/tests/test_diff.py`

**Step 1: Write failing tests**

Gates cover entity/schema existence, evidence checksum, type compatibility,
deterministic reachability, and native/runtime agreement. Hard failures drop a
candidate and reopen its hole; soft conflicts downgrade and remain visible.

Confidence tests prove:

- Runtime affects structural confidence only.
- Ordinary CloudWatch interaction cannot create verified lineage.
- LLM-only evidence is capped.
- Native exact plans can provide derivational oracle evidence.
- Uncalibrated policy emits `calibrated=false`.
- No collapsed score exists.

Diff tests separate added, removed, modified, structural-confidence,
derivational-confidence, unresolved, and coverage changes.

**Step 2: Verify failure**

```bash
python -m pytest workers/verifier/tests -v
```

Expected: FAIL.

**Step 3: Implement deterministic, versioned policy**

Store every result with evidence refs and policy version. Never let a model
self-score its output.

**Step 4: Verify**

```bash
python -m pytest workers/verifier/tests -v
```

Expected: PASS.

**Step 5: Commit**

```bash
git add workers/verifier
git commit -m "feat: verify lineage with two-axis confidence"
```

### Task 13: Implement Proposal Review and Fenced Publication

**Files:**
- Create: `services/proposal-api/src/transitions.ts`
- Create: `services/proposal-api/src/corrections.ts`
- Create: `services/proposal-api/src/reservation.ts`
- Create: `services/proposal-api/src/publication.ts`
- Create: `services/proposal-api/src/orphan-cleanup.ts`
- Create: `services/proposal-api/src/handler.ts`
- Create: `services/proposal-api/test/transitions.test.ts`
- Create: `services/proposal-api/test/publication-concurrency.test.ts`
- Create: `infra/lib/constructs/publication-workflow.ts`
- Create: `infra/test/publication-workflow.test.ts`
- Create: `tests/integration/test_approval_publication.py`

**Step 1: Write failing state tests**

Allow only:

```text
DRAFT -> AWAITING_REVIEW
AWAITING_REVIEW -> APPROVED | REJECTED | SUPERSEDED
AWAITING_REVIEW -> DRAFT (new correction version)
APPROVED -> PUBLISHING
PUBLISHING -> ACTIVE | FAILED
FAILED -> PUBLISHING (redrive)
```

Assert:

- Corrections never mutate the original.
- Material proposals need reviewer identity/approval.
- Rejected proposals cannot publish.
- Accepted manifest is immutable and checksummed.
- Publication checks the expected prior graph version.
- Stale publication returns REBASE_REQUIRED.
- Two proposals based on the same graph version cannot both acquire the
  application publication reservation.
- A lost or expired lease cannot activate its target graph namespace.
- Neptune mutations target an immutable, inactive graph-version namespace.
- Active pointer changes only after graph verification and a fenced DynamoDB
  transaction.
- Abandoned graph namespaces are marked ORPHANED and are never queryable
  through the active pointer.
- Search lag is exposed as a watermark.
- Engine-versus-human diff enters the evaluation corpus.

**Step 2: Verify failure**

```bash
npm test --workspace services/proposal-api
npm test --workspace infra -- publication-workflow.test.ts
python -m pytest tests/integration/test_approval_publication.py -v
```

Expected: FAIL.

**Step 3: Implement conditional transitions and publication fencing**

Use an application-scoped DynamoDB reservation conditioned on the expected
active version. Issue a target version, lease, and fencing token. Apply bounded
Neptune mutations with transaction-conflict retry only inside that immutable
target-version namespace. After graph version/checksum verification, use a
DynamoDB transaction conditioned on the live fencing token to advance the
active pointer and proposal state. A cleanup workflow marks and removes
ORPHANED namespaces from expired workers. Mark ACTIVE only after the fenced
transaction succeeds.

**Step 4: Verify**

Run the commands from Step 2.

Expected: PASS.

**Step 5: Commit**

```bash
git add services/proposal-api infra/lib/constructs/publication-workflow.ts infra/test/publication-workflow.test.ts tests/integration/test_approval_publication.py
git commit -m "feat: add governed lineage approval and publication"
```

### Task 14: Build Projections and Query APIs

**Files:**
- Create: `workers/projector/src/lineage_projector/neptune.py`
- Create: `workers/projector/src/lineage_projector/opensearch.py`
- Create: `workers/projector/src/lineage_projector/rebuild.py`
- Create: `workers/projector/tests/test_projection.py`
- Create: `services/query-api/src/handler.ts`
- Create: `services/query-api/src/authorization.ts`
- Create: `services/query-api/test/handler.test.ts`
- Create: `infra/lib/constructs/query-plane.ts`
- Create: `infra/test/query-plane.test.ts`

**Step 1: Write failing tests**

Assert:

- Only ACTIVE accepted manifests project.
- Interactions remain distinct from lineage.
- Projected edges retain graph version and evidence.
- Query resolution reads only the graph-version namespace selected by the
  active DynamoDB pointer; staged and ORPHANED namespaces are invisible.
- Replay is idempotent.
- Full rebuild matches incremental projection.
- Queries expose graph version and watermark.
- Traversal enforces depth/visited limits.
- Search and graph enforce domain RBAC/ABAC.
- OpenSearch deletion/rebuild loses no authoritative data.

**Step 2: Verify failure**

```bash
python -m pytest workers/projector/tests -v
npm test --workspace services/query-api
npm test --workspace infra -- query-plane.test.ts
```

Expected: FAIL.

**Step 3: Implement**

Use Neptune graph-version namespaces for traversals and OpenSearch for
discovery. Resolve the active DynamoDB pointer before each bounded query.
Implement asynchronous impact queries beyond synchronous bounds.

**Step 4: Verify**

Run the commands from Step 2.

Expected: PASS.

**Step 5: Commit**

```bash
git add workers/projector services/query-api infra/lib/constructs/query-plane.ts infra/test/query-plane.test.ts
git commit -m "feat: project and query approved lineage"
```

### Task 15: Build Review UI and User Run Timeline

**Files:**
- Create: `web/review-ui/package.json`
- Create: `web/review-ui/src/routes/Proposal.tsx`
- Create: `web/review-ui/src/components/LineageDiff.tsx`
- Create: `web/review-ui/src/components/ConfidenceEvidence.tsx`
- Create: `web/review-ui/src/components/RunTimeline.tsx`
- Create: `web/review-ui/src/components/EligibilitySummary.tsx`
- Create: `web/review-ui/src/components/CorrectionEditor.tsx`
- Create: `web/review-ui/src/api/client.ts`
- Create: `web/review-ui/src/component-tests/Proposal.test.tsx`
- Create: `services/run-timeline/src/handler.ts`
- Create: `services/run-timeline/test/handler.test.ts`
- Create: `tests/e2e/review-flow.spec.ts`

**Step 1: Write failing UI/E2E tests**

Show added, removed, modified, both confidence changes, holes, coverage,
evidence source/time/digest/policy/completeness, eligibility summary, and the
Triggered-to-Publication timeline. Correction creates a new version; rejection
cannot publish; approval requires authorization/base version. Provide a
tabular alternative to the graph.

**Step 2: Verify failure**

```bash
npm test --workspace web/review-ui
npm test --workspace services/run-timeline
npx playwright test tests/e2e/review-flow.spec.ts
```

Expected: FAIL.

**Step 3: Implement**

Render both confidence axes without collapsing them. Display INCOMPLETE,
UNKNOWN, and stale prominently. Build the timeline from the run ledger, not raw
Step Functions history.

**Step 4: Verify**

Run the commands from Step 2 and the configured accessibility audit.

Expected: PASS.

**Step 5: Commit**

```bash
git add web/review-ui services/run-timeline tests/e2e
git commit -m "feat: add lineage review and run visibility"
```

### Task 16: Add Security, Observability, Reconciliation, and DR

**Files:**
- Create: `infra/lib/constructs/security-boundaries.ts`
- Create: `infra/lib/constructs/observability.ts`
- Create: `infra/lib/constructs/dr.ts`
- Create: `infra/test/security-boundaries.test.ts`
- Create: `infra/test/observability.test.ts`
- Create: `services/run-timeline/src/reconcile.ts`
- Create: `tests/integration/test_reconciliation.py`
- Create: `docs/runbooks/dlq-redrive.md`
- Create: `docs/runbooks/projection-rebuild.md`
- Create: `docs/runbooks/regional-failover.md`
- Create: `docs/runbooks/runtime-session-stuck.md`
- Create: `docs/runbooks/missing-deployment-lineage.md`

**Step 1: Write failing assertions**

Security:

- Private data plane/VPC endpoints, KMS, scoped organization roles.
- No production principal can start or write runtime evidence.
- CloudTrail and required S3 data events.
- Reviewer and publisher permissions separable.

Observability:

- Queue age/DLQ, workflow, Batch, Bedrock, Kinesis, runtime completeness,
  projection lag, and database alarms.
- Required correlation IDs propagate.
- Every stage updates user timeline.

Reconciliation:

- Inventory versus eligibility.
- Accepted triggers versus runs.
- Deployed artifacts versus lineage decisions.
- Accepted manifests versus projection watermarks.
- Incremental versus scheduled full scan.

DR:

- S3 replication/restore, DynamoDB recovery, Neptune recovery, OpenSearch
  rebuild, and measured 15-minute RPO/four-hour RTO.

**Step 2: Verify failure**

```bash
npm test --workspace infra -- security-boundaries.test.ts observability.test.ts
python -m pytest tests/integration/test_reconciliation.py -v
```

Expected: FAIL.

**Step 3: Implement controls and runbooks**

Every runbook contains trigger, impact, owner, diagnostics, safe action,
verification, rollback, and audit. Reconciliation discrepancies create work;
they never silently delete authoritative state.

**Step 4: Verify**

```bash
npm test --workspace infra
python -m pytest tests/integration/test_reconciliation.py -v
```

Expected: PASS.

**Step 5: Commit**

```bash
git add infra/lib/constructs infra/test services/run-timeline/src/reconcile.ts tests/integration/test_reconciliation.py docs/runbooks
git commit -m "feat: harden lineage operations and recovery"
```

### Task 17: Validate Enterprise Scale and the Steel Thread

**Files:**
- Create: `tests/load/generate_estate.py`
- Create: `tests/load/test_event_burst.py`
- Create: `tests/load/test_baseline_capacity.py`
- Create: `tests/load/test_incremental_fairness.py`
- Create: `tests/load/test_runtime_stream.py`
- Create: `tests/chaos/test_transient_failures.py`
- Create: `tests/chaos/test_projection_rebuild.py`
- Create: `tests/chaos/test_regional_recovery.py`
- Create: `tests/e2e/test_enterprise_steel_thread.py`
- Create: `docs/runbooks/load-test.md`
- Create: `docs/runbooks/chaos-test.md`
- Create: `docs/launch-readiness-checklist.md`

**Step 1: Write the failing steel-thread test**

It must:

1. Inventory and classify a business application.
2. Exclude docs and register library/infra dependencies.
3. Produce, correct, and approve a baseline.
4. Process an application diff.
5. Fan out a library change only to deployed consumers.
6. Process an infrastructure binding change.
7. Close documentation as no-impact.
8. Reject production sidecar enable.
9. Recover duplicate, Batch, Kinesis, and Neptune failures.
10. Publish only approval and rebuild identical projections.

Load targets:

- 10,000-event accepted burst.
- 100 normalized triggers/second.
- 10,000-repository baseline in 12 hours.
- Incremental analysis in 30 minutes p95 excluding review.
- Tier-1 start in five minutes p95 during baseline.
- Approved projection in 60 seconds p95.
- One-hop query in two seconds p95.

Privacy targets:

- Zero raw fixture values across evidence, state, logs, traces, and errors.
- Fingerprint key unavailable after closure.

**Step 2: Run smoke tests and verify failure**

```bash
python -m pytest tests/e2e/test_enterprise_steel_thread.py -v
python -m pytest tests/load -m smoke -v
python -m pytest tests/chaos -m smoke -v
```

Expected: FAIL until all components exist.

**Step 3: Implement the nonproduction harness**

Parameterize repository count, archetype, scan duration, spikes, runtime rate,
failures, and domain fairness. Record service quotas before each run. Never run
destructive recovery tests against production/shared evidence.

**Step 4: Execute staged validation**

```bash
python -m pytest tests/e2e/test_enterprise_steel_thread.py -v
python -m pytest tests/load -v
python -m pytest tests/chaos -v
```

Expected: PASS with percentiles, capacity, cost, throttles, data quality,
recovery time, and open exceptions attached.

**Step 5: Complete launch review**

Product, architecture, platform, SRE, security, privacy, governance, Test
Automation, and pilot application owners sign applicable gates. Confidence
remains labelled UNCALIBRATED and auto-publication remains disabled until
governed calibration.

**Step 6: Commit**

```bash
git add tests/load tests/chaos tests/e2e/test_enterprise_steel_thread.py docs/runbooks/load-test.md docs/runbooks/chaos-test.md docs/launch-readiness-checklist.md
git commit -m "test: validate enterprise lineage steel thread"
```

## Final Verification

Run:

```bash
npm test --workspaces --if-present
npm run typecheck --workspaces --if-present
python -m pytest tests workers -v
go test ./sidecars/lineage-observer/... -race
go vet ./sidecars/lineage-observer/...
npx playwright test
npm run cdk --workspace infra -- synth
git diff --check
```

Expected: all commands succeed.

Then run the deployed nonproduction suite:

```bash
python -m pytest tests/e2e/test_enterprise_steel_thread.py -v
python -m pytest tests/load -v
python -m pytest tests/chaos -v
```

Expected: all gates pass or have explicitly approved, time-bounded exceptions
in `docs/launch-readiness-checklist.md`.

## Completion Evidence

Implementation is complete only when all are present:

- Synthesized/reviewed infrastructure.
- Versioned contracts and compatibility tests.
- Baseline and incremental workflows.
- Eligibility registry with no silent exclusions.
- Library/infrastructure dependency triggers.
- Metadata-only sidecar with production hard-deny.
- Two-axis confidence and calibration corpus.
- Immutable proposal/review/accepted history.
- Tested graph/search projection rebuild.
- Before/after review UI and run timeline.
- SLOs, alarms, runbooks, reconciliation, and audit.
- 10,000-repository load and spike-fairness evidence.
- Privacy/security, chaos, and regional-recovery evidence.
- Signed pilot launch checklist.
