# Test Strategy and Canonical Fixtures

**Status:** Normative implementation, integration, and launch specification  
**Applies to:** All C01-C18 code, contracts, infrastructure, clients and
operational workflows

## 1. Quality Contract

Testing proves business effects and invariants, not merely process exit codes.
Every requirement test states its fixture, immutable input versions, action or
fault, expected durable state/output, forbidden effects, observability, cleanup
and retained evidence. A successful API response, workflow state or empty diff
is insufficient if evidence, idempotency, coverage, authorization, projection
or recovery is not verified.

Required principles:

- Contract-first: producer and consumer tests use the same versioned schemas
  and golden examples from contracts/.
- Test-driven implementation: a requirement or defect begins with a failing
  test at the lowest layer that proves the behavior.
- Deterministic core: fixed inputs, deterministic clock, seeded randomness,
  stable IDs and pinned tool/model/policy versions produce reproducible results.
- Truth-aware assertions: S3 immutable artifacts plus control-state records are
  asserted before rebuildable Neptune/OpenSearch projections.
- Failure is first-class: invalid, incomplete, conflict, duplicate, out-of-
  order, timeout, partial dependency, privacy and authorization cases accompany
  every happy path.
- No hidden test bypass: environment flags may select a fixture/dependency but
  cannot disable identity, authorization, privacy, approval, fencing,
  idempotency, visibility or checksum validation.

## 2. Required Test Layers

| Layer | Runs on | Required coverage | Gate it can close |
|---|---|---|---|
| Static specification layer | Developer/CI | Documentation validator, schema lint, OpenAPI, IaC/policy lint, typecheck, dependency/license/secret checks | Documentation/foundation only |
| Component unit layer | Developer/CI | Pure parsing, identity, state transition, determinant, gate, confidence, redaction and query-bound logic | Individual deterministic requirement |
| Local contract layer | Developer/CI | Producer/consumer schema examples, compatibility, serializers, generated clients, fake clock/IDs and invalid corpus | Contract semantics without AWS claims |
| Local integration layer | CI container | Real language runtime, filesystem, parser/DB emulator/LocalStack where semantic fidelity is documented | Internal adapter/store logic only |
| Deployed integration layer | Ephemeral AWS account/Region | EventBridge/SQS/Step Functions/Batch/S3/DynamoDB/KMS/IAM/AppConfig/Kinesis/API and pairwise INT rows | Managed-service and cross-component gates |
| Production-shaped acceptance layer | Isolated staging accounts/primary plus standby Region | Neptune/OpenSearch, multi-account ABAC, full steel threads, security, load/fairness, chaos, backup/rebuild and DR | Launch and enterprise gates |
| Production verification layer | Production canary/synthetic | Read-only/safe nonserving canaries, SLO, audit delivery, replication, expiry and reconciliation | Continued operation; never replaces prelaunch tests |

The Local contract layer must be fast enough for every pull request. Emulators
do not close tests for Object Lock, IAM/SCP/resource policies, KMS grants,
Step Functions redrive, AppConfig validators, Kinesis ordering, Neptune
transactions, OpenSearch aliases, cross-Region replication or warm standby.
Those require the Deployed integration layer or Production-shaped acceptance
layer.

## 3. Canonical Fixture Catalog

All fixtures live under tests/fixtures/lineage/ with a fixture-manifest.json
containing fixture ID/version, file/object checksums, seed, expected IDs,
allowed data classification, golden outputs, owners and change approval.
Fixtures contain synthetic data only; no copied production payload or secret.

### FX-PILOT — representative 70-repository cohort

Purpose: validate pilot behavior across Spring Boot, FastAPI, Dask, Spark, dbt,
Airflow/SQL, shared libraries, IaC and documentation repositories.

Contents and oracle:

- 70 repositories across six application/domain owners, with active, archived,
  fork, template, infrastructure, shared-library and documentation examples.
- Included/excluded/mixed/unknown eligibility goldens and explicit evidence
  precedence/override/expiry.
- Commits, signed artifact digests, deployments, schemas, test associations,
  native runs and expected application context snapshots.
- Exact baseline nodes/edges, open holes, conflicts, coverage denominators,
  before/after proposal and active manifest checksums.
- At least one secret canary in a prohibited input path that must quarantine and
  never appear in output/telemetry.

### FX-MIXED-MONOREPO — path-scoped classification and lanes

Purpose: prove one repository can contain application runtime, Spark/dbt,
shared library, infrastructure and documentation paths without repository-wide
misclassification.

Oracle:

- Path rules assign Lane A/B or no expensive analysis exactly.
- A critical unknown path blocks completion and is visible in review.
- A change touching multiple paths coalesces one run while preserving every
  determinant and per-path outcome.
- Published URNs retain repository/path/application/environment/effective
  version without duplicate edges.

### FX-SHARED-LIBRARY — determinant fan-out

Purpose: prove library changes invalidate only actual version-range consumers
and respect artifact/deployment bindings.

Oracle:

- Two applications consume the changed exported symbol; one application pins a
  nonaffected version; one merely shares a repository label.
- Symbol/API change schedules the two actual consumers; documentation change
  closes with no lineage impact.
- A missing consumer index is detected by scheduled full-scan divergence and
  inventory/dependency reconciliation.

### FX-INFRASTRUCTURE — topology versus capacity

Purpose: distinguish endpoint/routing/binding changes from CPU/memory/replica
capacity changes.

Oracle:

- Endpoint/queue/topic/schema binding changes invalidate affected lineage.
- Capacity-only change records explainable no-impact and never invents an edge.
- An ambiguous template expression creates a visible hole/conflict rather than
  selecting a plausible resource.

### FX-CONTRACT — schema evolution and compatibility

Purpose: validate canonical contracts, OpenLineage facets, OpenAPI clients,
events and stored artifacts across supported versions.

Contents:

- Current and prior compatible producer/consumer pairs.
- Unknown additive fields at permitted boundaries, reordered JSON, Unicode,
  size limits, null/absent distinctions and additionalProperties violations.
- Unsupported major, semantic meaning change, checksum mismatch, missing
  immutable identity and privacy-prohibited property.
- Golden serialization/checksum/canonicalization and migration results.

Oracle: supported versions interoperate without meaning change; incompatible
inputs fail before durable business mutation with version/correlation evidence.

### FX-RUNTIME — metadata-only integration session

Purpose: validate C11 sidecar/session behavior and C13 structural-only use.

Contents:

- Three expected sidecars, two tests, signed integration attestation, artifact
  digest, schema registry and deterministic session key.
- Valid monotonic events/heartbeats/closing manifests plus duplicate, reorder,
  gap, truncation, timeout and late-event variants.
- Raw strings, encoded values, known secrets, low-cardinality sensitive fields,
  reversible fingerprints and production attestation attacks.

Oracle:

- Tests start only after all expected READY; disable executes in finally.
- Valid metadata closes COMPLETE with exact checksums; gaps/truncation close
  INCOMPLETE/TRUNCATED and cannot increase confidence.
- Every prohibited/production attempt is denied/quarantined/audited with no
  forbidden bytes in evidence, logs, traces or DLQs.

### FX-NATIVE — engine-native exactness

Contains Spark OpenLineage facets/plans, dbt manifest/catalog/run results and
Airflow/SQL examples bound to immutable artifacts. Goldens cover aliases,
select-star with schema, UDF/dynamic unresolved cases, multi-producer fields,
missing listeners and duplicate runs. Only engine-proven exact mappings are
derivational oracle.

### FX-STATIC-HOLES — deterministic and agentic boundary

Contains Spring Boot and FastAPI handlers, Dask code, configuration keys,
reflection/dynamic SQL, resolvable symbols and explicitly unsupported
constructs. C08 goldens define byte-identical provable edges and named Holes;
C09 goldens allow only search/read_span/resolve_symbol/call_graph/schema_lookup
over bounded facts and require file:line citations or abstention.

### FX-OPAQUE — advisory privacy boundary

Synthetic source-local windows include high/low cardinality, sensitive and
non-sensitive fields, insufficient observations, collision/ambiguity, key
expiry and nonmatching dependencies. Goldens contain only approved aggregate/
fingerprint metadata and advisory confidence caps; no raw value is stored.

### FX-REVIEW — immutable proposal and labels

Contains before/after proposals, exact material edges, two concurrent reviewer
versions, assignment/revocation, correction/reject/approve, stale base and bulk
accept. The corpus subfixture contains at least 200 material labelled edges
across six archetypes plus dynamic SQL, opaque UDF and multi-producer hard cases.
Bulk-unreviewed edges never enter correctness/correction statistics.

### FX-PUBLICATION — lease, fencing and projection

Contains approved/draft/rejected/unlocked manifests, two proposals against the
same expected prior graph, staged partial/corrupt targets, expired worker,
OpenSearch lag and prior versions. Oracle allows one current fencing token to
activate a fully verified immutable target and provides exact graph/search
rebuild checksums.

### FX-SECURITY — multi-account authorization and prohibited data

Defines enterprise identities, domains, roles/attributes, proposer/approver,
operators/break-glass, revoked users, cross-organization principals, resource
tags, KMS/network/egress policies and secret/payload canaries. Expected access
matrix covers positive, denied, redacted, no-existence-leak, audit and expiry.

### FX-SCALE-10K — enterprise load profile

Generates 10,000 repositories with recorded size/language/lane/domain/tier
distribution, 10,000 daily artifact decisions, graph degree distribution,
release burst, baseline backlog, reviewer activity and query mix. Seed and
generator version are fixed; the generated manifest/checksums are retained.

### FX-DR — backup, replication and regional recovery

Defines one consistent recovery point plus later writes within/outside RPO,
S3 versions/Object Lock/CRR, DynamoDB state/pointers/idempotency, proposal
history, accepted manifests, graph/search projections, audit and IaC versions.
The recovery oracle lists exact retained/lost-within-objective records, counts,
checksums, pointer/watermark, authorization and failback result.

## 4. Deterministic Time, Identity and Ordering

The test support package supplies:

- A deterministic clock with explicit advance/freeze and separate event,
  processing, lease, expiry and observation timestamps.
- UUIDv7/ULID fixture generators seeded by test case; canonical run, event,
  artifact, proposal, graph, session, evidence and operation IDs.
- Deterministic SHA-256 content and canonical JSON helpers.
- Seeded backoff/jitter, property-based generators and load distributions.
- Monotonic per-producer sequence generators plus deliberate duplicate,
  reorder, gap, rollover and delayed delivery controls.

Production code receives clock/ID/random interfaces; it must not patch global
time or rely on test-only branches. Tests involving AWS-issued timestamps record
tolerance and compare ordering/expiry behavior, not byte equality.

## 5. Contract and Golden Testing

For every schema:

1. Validate the canonical valid example and at least one invalid example per
   constraint/security boundary.
2. Serialize, canonicalize, checksum, deserialize and compare semantic equality.
3. Run current producer against current and supported prior consumers, and
   supported prior producer against current consumer.
4. Prove unsupported major/semantic change fails before side effects.
5. Verify missing versus empty identity, large-payload S3 reference/checksum,
   unknown field policy and redaction.
6. Snapshot only stable, reviewed output. Dynamic timestamps/IDs are normalized
   by fixture interfaces, never erased from correctness assertions.

Golden updates require a fixture version bump, human-readable semantic diff,
contract owner and affected consumer approval. A test is not fixed by blindly
regenerating a golden.

## 6. Fault Injection

The fault injection library names the boundary and activation count/time so a
test can fail before, during and after durable mutation:

- Throttle, timeout, connection reset, DNS/network partition and dependency
  unavailable.
- Duplicate, reorder, delay, drop, poison, old schema and checksum corruption.
- Process kill, Batch host interruption, Lambda timeout, Step Functions retry/
  redrive and callback loss.
- S3 partial/mismatched reference, DynamoDB conditional conflict/throttle,
  Kinesis shard throttle/sequence gap, AppConfig propagation/validator failure.
- Neptune partial stage/transaction conflict/writer loss and OpenSearch partial
  bulk/alias/watermark lag.
- KMS deny/key unavailable, secret rotation/revocation, IAM/ABAC/tag/ownership
  change, egress deny and audit delivery degradation.
- Availability Zone and Region loss, replication lag, stale backup, corrupt
  projection and recovery cutover/failback interruption.

Each fault test asserts the shared error class, retryability, terminal state,
idempotent durable effects, cleanup/finally, alarm/audit/timeline and safe
operator action. Fault hooks are unavailable in production application APIs.

## 7. Load, Performance and Fairness Profiles

| Profile | Workload | Mandatory assertions |
|---|---|---|
| LP-INGRESS-BURST | 10,000 events then 100 normalized triggers/second | No loss; duplicate safety; queue age/DLQ/latency and archive reconcile |
| LP-BASELINE-10K | FX-SCALE-10K full baseline | Complete within 12 hours at measured capacity; explicit incomplete; 70 percent planning utilization target measured |
| LP-RELEASE-STORM | Tier-1 deployments plus baseline/backfill | Tier-1 starts within five minutes p95; lower priority cannot starve forever |
| LP-INCREMENTAL | Representative determinant changes | Finish analysis within 30 minutes p95 excluding review/deferred runtime |
| LP-RUNTIME-10X | Ten times forecast sidecar events and sequence cardinality | Overhead budget, no silent sampling, complete/truncated semantics and finally cleanup |
| LP-PUBLICATION | 100 applications plus 100,000-edge changes | Per-app serialization, cross-app parallelism, 95 percent queryable within 60 seconds |
| LP-QUERY | 500 rps, high-degree/cyclic graph and concurrent reviewers | One-hop within two seconds p95, hard bounds, fair quotas, no mixed versions |
| LP-RECONCILE | Full inventory/deployment/evidence/pointer comparison | 100 percent scope, bounded cost/checkpoints and exact discrepancy counts |

Reports include workload generator/seed, quotas, infrastructure versions/sizes,
warm-up, duration, raw latency distributions, errors, saturation, cost,
autoscaling, backlog recovery and fairness by domain/tier. Averages alone do
not pass percentile SLOs.

## 8. Security, Privacy and Accessibility Testing

Security tests cover authentication, session expiry, least privilege,
cross-account trust/confused deputy, RBAC/ABAC/count/existence leakage, KMS,
network/public access, SSRF/egress, injection, supply chain, direct storage/
projection access, audit and break-glass.

Privacy tests seed unique canaries in raw, encoded, compressed and nested forms,
then scan S3/DynamoDB/Neptune/OpenSearch, queues/DLQs, workflow state, Batch
workspace/images, logs/traces/metrics/audit, exports, tickets and test reports.
The canary must exist only in the intentionally quarantined protected fixture
location and approved security incident record hash, never a copied value.

C17 primary journeys run automated semantic/accessibility checks on every
change and manual keyboard, screen-reader, 200 percent zoom/reflow, contrast and
reduced-motion checks before release. Graph views require an equivalent
navigable textual/table representation.

## 9. Test Environment and Data Lifecycle

Each deployed run creates a unique environment/testRunId prefix and tags every
resource/object/state record. Tests may reuse foundation accounts but not mutable
business state. Parallel runs use isolated application/environment/URN
namespaces and quota reservations.

Setup verifies account/Region, identity, network, KMS, contract/policy versions,
service quotas, clean namespace and fault-hook scope. Cleanup:

1. Disable runtime flags/sessions and stop optional workers in a finally path.
2. Cancel executions/exports and drain test-only queues after result capture.
3. Delete ephemeral mutable resources/state through IaC lifecycle.
4. Retain immutable evidence/audit required by the test under a dedicated test
   retention class; never weaken Object Lock to make cleanup pass.
5. Reconcile that no active pointer, public endpoint, role session, secret,
   orphan namespace or cost-incurring worker remains.

Cleanup failure fails the test and pages the environment owner. Synthetic
fixtures must never share production application IDs or destinations.

## 10. Retained Evidence and Result Schema

Every component, INT and E2E execution emits a signed TestEvidenceManifest:

- requirement/test IDs, result and failure reason;
- fixture IDs/versions/checksums and random seed;
- code/image/IaC/contract/policy/analyzer/model versions;
- account/Region/environment and approved resource configuration hashes;
- start/end/phase timestamps, deterministic clock plan and correlation IDs;
- actions/faults, expected and observed durable effects, forbidden-effect scan;
- S3/DynamoDB/Neptune/OpenSearch counts/checksums/versions/watermarks as relevant;
- API/UI/trace/audit/alarm/runbook/load/accessibility/security/recovery artifact
  references and checksums;
- cleanup/reconciliation status, owner/reviewer and waiver reference/expiry.

The manifest and material logs/reports/screenshots/traces are retained evidence
in C12/audit storage under the approved test class. Secrets/raw payloads are
redacted before evidence creation. A CI link without immutable manifest and
checksums is not launch evidence.

## 11. Flaky-Test Policy

The flaky-test policy is zero silent reruns and zero quarantined P0 gate tests.

- CI records the first failure before any diagnostic rerun. Automatic rerun may
  occur once only for tests explicitly tagged as transient-diagnostic; it does
  not convert the original result to pass.
- A nondeterministic test creates an owned defect with first-seen build, layer,
  fixture/seed, frequency, artifacts and seven-day remediation target.
- A temporarily quarantined P1/P2 test must keep executing nonblocking, display
  status, have owner/expiry and cannot be the sole proof of a P0 requirement,
  security/privacy invariant, publication fence, data integrity or RPO/RTO.
- Test code fixes must identify root cause: product race, environment capacity,
  unordered assertion, uncontrolled clock/ID, eventual-consistency bound or
  faulty fixture. Increasing sleep/retry without evidence is not a fix.
- Release candidates require all required cases pass on the same immutable
  build/environment set and no unexpired P0 quarantine.

## 12. Completion Rule

A component is successfully implemented only when:

- its component matrix passes at the required layer;
- every dependency-and-integration-matrix row touching it passes all six paths;
- applicable E2E steel threads, performance, security/privacy, accessibility,
  chaos and recovery gates pass;
- the implementation matches current contracts and no fixture golden was
  changed without approved semantic review;
- retained evidence and cleanup reconciliation are complete; and
- no open failure is hidden as success, empty, omitted telemetry or an
  indefinite waiver.
