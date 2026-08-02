# Coding-Agent Implementation Handoff

**Status:** Normative execution contract for implementation agents
**Start here after:** README, system context, contract catalog, state/error model,
test strategy, integration matrix and implementation sequence

## 1. Mission and Completion Standard

Implement the approved AWS lineage collection application exactly as specified
by C01-C18 and the shared contracts. The goal is a deployable, secure, tested
vertical system, not a set of disconnected service stubs.

A component is complete only when:

- every P0 requirement has code and a passing component test;
- its versioned contracts/examples and compatibility cases pass;
- every touching INT row passes all six boundary dimensions in the required
  deployed environment;
- applicable E2E, security/privacy, accessibility, load, chaos and DR cases pass;
- logs/metrics/traces/audit/alarms/runbooks and cleanup are operational; and
- a signed immutable TestEvidenceManifest links the exact build and effects.

Do not report success from compilation, unit tests, a workflow SUCCEEDED state,
an HTTP 200, a manually inspected graph or an unlinked CI job.

## 2. Authority and Requirement Navigation

Use this decision order:

1. Component-package design and this PRD package.
2. Approved AWS architecture.
3. Element-level lineage v2 analyzer semantics.
4. Throughline platform PRD product language.
5. Earlier source material for context only.

For each implementation slice, write the requirement IDs in the change
description, open the component's Interfaces, Failure Semantics, Component Test
Matrix, Integration Obligations and Definition of Done, then follow the shared
traceability row. A stricter privacy, security, idempotency, immutability,
versioning, completeness or visibility rule wins until documents are reconciled.

## 3. Approved Technology and Ownership

- **TypeScript 5** owns control-plane services, APIs, web application, contract
  generation where practical, conditional state transitions and infrastructure.
- **Python 3.12** owns heavy analyzers/parsers, verification/reconciliation,
  graph export/projection and large report workers.
- **AWS CDK v2** with TypeScript owns all AWS infrastructure. No manually
  configured production dependency is an accepted implementation.
- JSON Schema 2020-12 and OpenAPI 3.1 own JSON/API contracts. OpenLineage plus
  governed versioned facets owns external lineage interchange.
- pnpm workspace owns JavaScript/TypeScript dependencies; uv with a committed
  lock owns Python environments. Tool versions are pinned at repository root.
- Container images are minimal, nonroot, digest-pinned, signed, scanned and
  recorded in SBOM/provenance.
- Amazon EventBridge routes, SQS buffers, Step Functions Standard coordinates,
  Batch analyzes, S3 preserves, DynamoDB controls, Neptune traverses,
  OpenSearch discovers, API Gateway/web presents and the user approves.

Do not replace an approved AWS service or introduce another language, database,
message bus, orchestration engine, model gateway, generic plugin/tool system or
client framework without an architecture decision and updated PRD/contracts/
tests. A library choice inside the approved boundary is allowed when pinned,
licensed, scanned and consistent with repository conventions.

## 4. Repository Layout

    apps/
      lineage-web/
    contracts/
      schemas/
      openapi/
      openlineage/
      examples/
    packages/
      contracts-ts/
      contracts-py/
      evidence-client/
      analyzer-sdk/
      api-client/
      ui-components/
      telemetry-contract/
      test-support/
    services/
      contract-registry/
      identity-registry/
      source-adapters/
      inventory-builder/
      event-normalizer/
      eligibility/
      context-index/
      run-controller/
      run-timeline/
      native-ingest/
      evidence-registry/
      cache-index/
      confidence-policy/
      proposal-review/
      review-assignment/
      ci-drift/
      artifact-binder/
      deployment-lineage-controller/
      publication-controller/
      query-api/
      runtime-session/
      agent-task-builder/
      agent-tools/
      opaque-control/
      reconciliation-controller/
      operations-api/
    workers/
      native-*/
      deterministic-*/
      agent-resolver/
      opaque-aggregate/
      reconciliation/
      verification/
      graph-exporter/
      neptune-projector/
      opensearch-projector/
      projection-reconciler/
    sidecars/
      runtime-evidence/
    source-local/
      opaque-collector/
    workflows/
      redrive/
      regional-recovery/
    infra/
      bin/
      lib/constructs/
      lib/stacks/
    policies/
    dashboards/
    docs/runbooks/
    tests/
      fixtures/lineage/
      unit/
      contract/
      integration/
      e2e/
      accessibility/
      security/
      operations/
      load/
      chaos/
      dr/

Keep business logic in pure packages/modules with explicit ports. Lambda/Batch/
Step Functions/API/SDK handlers adapt transports; they do not redefine the
domain. Do not create a generic shared package for unrelated helpers. A shared
package needs an owner, stable contract and at least two real consumers.

## 5. Component-to-Code Map

| Component | Primary code targets | Runtime |
|---|---|---|
| C01 | contracts, contracts-ts/py, contract-registry, identity-registry | TypeScript plus generated Python |
| C02 | source-adapters, inventory-builder | TypeScript control; bounded Python adapter only when SDK requires |
| C03 | event-normalizer and EventBridge/SQS/archive constructs | TypeScript |
| C04 | eligibility pure evaluator/registry | TypeScript |
| C05 | context-index/dependency/determinant workers | TypeScript control plus Python for large index jobs |
| C06 | run-controller/timeline and Step Functions/Batch constructs | TypeScript |
| C07 | native-ingest and Spark/dbt/Airflow parsers | TypeScript intake; Python workers |
| C08 | deterministic analyzers and analyzer SDK | Python workers; TypeScript control |
| C09 | task builder/tools/resolver/gateway/cache | Python resolver/tools; TypeScript admission/state |
| C10 | opaque control/source-local collector/aggregate | TypeScript control; approved source-local/Python worker |
| C11 | runtime session, sidecar, validator pipeline | TypeScript control; sidecar runtime selected per supported app |
| C12 | evidence-registry/cache-index/client and storage constructs | TypeScript |
| C13 | reconciliation/verification/confidence policy | Python workers; TypeScript policy/control |
| C14 | CI drift/binder/deployment controller | TypeScript; Python deterministic diff if reused |
| C15 | proposal/review/assignment/corpus control | TypeScript |
| C16 | publication controller and graph/search projection | TypeScript control; Python export/project workers |
| C17 | query-api, API client, UI components/web | TypeScript |
| C18 | security/observability IaC, operations/reconcile/redrive/recovery | TypeScript control/IaC; Python large reconciliation |

## 6. Contract-First and Test-Driven Loop

**Contract-first** and **test-driven** are required for every feature/fix:

1. Select the smallest requirement/test/INT slice that produces one observable
   business behavior.
2. Add/update schema, valid/invalid examples, compatibility matrix and ownership.
3. Add a failing component test and, for a boundary, producer/consumer contract
   test. Confirm failure is for the intended missing behavior.
4. Implement the pure domain/state logic; run fast unit/property/golden tests.
5. Implement persistence/transport adapter with conditional/idempotent effects.
6. Add failure, duplicate/order, timeout/recovery, privacy/security and telemetry
   tests before calling the boundary complete.
7. Deploy the slice to the phase's ephemeral AWS environment; run INT cases,
   fault injection, cleanup and evidence verification.
8. Run all affected upstream/downstream tests and applicable E2E gate.
9. Commit one coherent slice with requirement/test IDs and evidence link.

Never edit a golden solely to make a failed test pass. Explain the semantic
change, version the fixture/contract and obtain affected owner approval.

## 7. Canonical Data and Contract Rules

Every durable/event/API artifact:

- carries schema ID/semantic version and immutable business identity;
- uses additionalProperties false at privacy-sensitive boundaries;
- distinguishes absent from empty; missing identity never becomes an empty
  idempotency key;
- carries or references applicable common correlation fields;
- passes large content by immutable S3 URI, version and SHA-256 checksum;
- has producer/consumer owners, compatibility policy and valid/invalid examples;
- uses canonical UTC timestamps plus explicit source/event/processing meaning;
- records policy/analyzer/context/artifact/effective versions affecting result;
- never embeds repository archives, payload values, credentials or model
  transcript into workflow/event/log state.

Use C01 libraries for URNs/canonical serialization/checksum. Do not independently
format an identity in a service. Validate on both producer and consumer; a
consumer must not trust a producer merely because both are internal.

## 8. State, Idempotency and Failure Implementation

Model transitions as explicit pure functions returning next state, durable
effects and audit/telemetry intents. Persist with expected state/version,
conditional writes or one transaction. Include attempt and immutable operation
identity; never use last-write-wins for review, publication, policy or recovery.

At-least-once delivery is normal. Define idempotency from immutable business
identity in the component PRD. Identical duplicates return/reuse the prior
effect. Same identity with different checksum/version is CONFLICT and preserves
both claims for quarantine/review; it is never silently overwritten.

Implement the shared classes:

- TRANSIENT: bounded exponential backoff plus jitter, max attempt/time and
  idempotent checkpoint.
- DETERMINISTIC_INVALID: no repeated retry; quarantine with reason/owner/action.
- INCOMPLETE: preserve partial evidence and coverage gap; no false success or
  confidence promotion.
- CONFLICT: preserve competing versions/evidence; conditional resolution/review.
- POISON_REPEATED: DLQ after bounded attempts; governed plan/redrive/reconcile.

Finally/cleanup behavior is part of the state machine. Cancellation, timeout,
host loss and redrive must disable runtime flags, close sessions, release leases,
persist checkpoints and reconcile orphans as specified.

## 9. AWS Implementation Guardrails

- EventBridge rules route normalized envelopes; they are not a work backlog.
- SQS Standard queue delivery can duplicate/reorder. Separate priority lanes,
  DLQs and visibility/heartbeat policy; never assume FIFO unless approved.
- Step Functions Standard holds IDs, small state and immutable references only.
  Use callbacks for external review and Distributed Map for measured fan-out.
- Lambda performs bounded control actions; repository checkout, parsers, graph
  export and large reconciliation run in Batch/approved workers.
- S3 evidence buckets use versioning/KMS/Object Lock where specified. Workload
  roles cannot shorten retention/delete authoritative objects.
- DynamoDB tables use explicit partition/access patterns, conditional state,
  PITR and item-size guard. Do not store large artifacts or scan as a normal API.
- Neptune receives only immutable target-version graph data through C16.
  OpenSearch receives only versioned index builds and atomic alias/watermark.
- IAM is component/stage/environment/resource scoped; private networking and
  endpoint policies apply. Egress uses the approved broker/firewall.
- CloudTrail/application audit is not ordinary debug logging and cannot be
  sampled or deleted by workload roles.

## 10. Security and Privacy by Construction

Before coding a new data path, write:

- data classification and exact allowed fields;
- producer/consumer identities and resource scope;
- encryption key/network/egress/secret path;
- retention/legal hold/deletion and audit;
- negative cross-domain/cross-account/direct-access cases;
- prohibited-data canaries and all sinks to scan.

Production runtime field evidence is denied at AppConfig validation, organization
policy, IAM/resource policy and sidecar/session attestation. No implementation
flag may weaken that. Runtime metadata can change structural confidence only.
Opaque collection is source-local/advisory and never stores raw/reversible
values. Agent tasks are hole-only with bounded facts/tools/citations; repository
text cannot change instructions/policy.

Logs/traces/metrics use safe IDs/hashes and bounded cardinality. Do not log full
events, object bodies, headers/tokens, SQL/source spans, model prompts/results,
fingerprints, signed URLs or authorization policy internals.

## 11. Feature Flags and Rollout

**Feature flags** may:

- canary a new adapter/analyzer/parser by explicit application/domain cohort;
- shadow-compute a result without publishing/enforcing it;
- select a contract-compatible implementation or measured capacity strategy;
- pause optional Lane C/agentic/backfill work during incident/cost pressure;
- expose a C17 route only after its API/security/accessibility gate.

Feature flags must not:

- bypass contract/checksum/identity validation, review/approval, fencing,
  idempotency, G1-G5, evidence ABAC, audit or privacy;
- enable instrumented production runtime evidence;
- silently exclude UNKNOWN/incomplete/conflicting work;
- auto-publish or auto-approve at launch;
- change confidence meaning without policy/version/migration.

Flags have owner, purpose, allowed environment/cohort, default-safe state,
creation/expiry, rollback, alarm and audit. Expiry fails closed. Rollout stages
are local/unit, deployed test tenant, nonserving canary, pilot application,
domain cohort and enterprise; each stage requires prior evidence.

## 12. Local validation commands

The Phase 0 scaffold must implement these stable commands:

    corepack pnpm install --frozen-lockfile
    uv sync --frozen --all-groups
    pnpm format:check
    pnpm lint
    pnpm typecheck
    pnpm test:unit
    pnpm test:contract
    pnpm test:policy
    pnpm cdk:synth
    uv run pytest tests/unit tests/contract
    pnpm validate:docs
    pnpm validate:all

validate:all runs formatting, lint, typecheck, unit, contract, policy, secret/
dependency/license/SBOM, IaC synth and documentation checks without deploying.
Component filters must not change assertions, only selected test IDs.

## 13. Deployed Validation Commands

The test harness must implement:

    pnpm env:create -- --phase=<0-9> --test-run=<id>
    pnpm test:deployed -- --phase=<0-9> --test-run=<id>
    pnpm test:component -- --components=<Cxx-list>
    pnpm test:integration -- --ids=<INT-range/list>
    pnpm test:e2e -- --ids=<E2E-range/list>
    pnpm test:security -- --scope=<scope>
    pnpm test:accessibility
    pnpm test:load -- --profile=<LP-name>
    pnpm test:chaos -- --scope=<scope>
    pnpm test:dr -- --scenario=regional-failover-failback
    pnpm evidence:verify -- --candidate=<build>
    pnpm env:cleanup -- --test-run=<id>
    pnpm env:reconcile -- --test-run=<id>

**Deployed validation commands** require explicit account/Region/profile
confirmation, unique testRunId, cost estimate/budget, approved fault scope and
cleanup trap. They print no secrets. Environment deletion never bypasses Object
Lock; immutable test evidence stays under its approved retention class.

## 14. Environment Assumptions

Required nonproduction topology:

- separate lineage control/compute, evidence/data, application/API, central
  observability/security and integration application accounts;
- isolated primary and warm-standby Regions, Multi-AZ primary managed services,
  private DNS/subnets/endpoints, controlled egress and central audit;
- enterprise SSO/SCIM test identities/ownership/ABAC matrix;
- test integrations for SCM, Test Automation, build/release/deploy, schema/
  catalog, native engines, model gateway, SIEM/on-call and finance;
- service quotas/capacity sufficient for each declared load profile;
- synthetic fixtures only and no connection to production payload sources.

If an external integration is unavailable, implement its versioned port plus
contract emulator and continue local logic, but do not mark the touching INT/E2E
or component complete. Record the dependency as a gate, not a successful mock.

## 15. Commit Cadence and Change Shape

**Commit cadence** is one coherent, reviewable behavior:

1. failing test/contract fixture where useful;
2. minimal implementation plus tests;
3. deployed integration/IaC slice and evidence plumbing;
4. documentation/runbook update.

Small slices may combine these when still reviewable. A commit message names the
component and behavior; the body lists requirement/CT/INT/E2E IDs, migration/
rollback and evidence location. Never mix unrelated refactors, generated
goldens, dependency upgrades and behavior changes.

Before committing:

    git diff --check
    pnpm validate:all
    uv run pytest <affected-python-tests>
    pnpm test:component -- --components=<affected>

Before a phase release, run every phase Validation Command on the same immutable
candidate. Do not rewrite published Git history or delete failed-first evidence.

## 16. Non-negotiable invariants

1. Every trigger/repository/deployment/hole/evidence/proposal/approval has a
   visible durable outcome; none is silently dropped.
2. Every repository/path is included, excluded with reason, mixed or UNKNOWN;
   critical UNKNOWN cannot silently pass baseline.
3. Large payloads use immutable S3 URI/version/checksum, never workflow/event
   bodies.
4. S3 accepted evidence/manifests/labels plus controlled state are authority;
   Neptune/OpenSearch are rebuildable projections.
5. Canonical identities include environment/effective version where meaning
   differs; missing immutable identity quarantines.
6. Deterministic/native evidence is preferred. An LLM sees only a named Hole
   and emits cited result or abstention.
7. Service interaction, OTel or runtime execution alone never proves an
   internal transformation.
8. Structural confidence and derivational confidence remain independent;
   incomplete runtime cannot promote, and sole-LLM/opaque evidence stays capped.
9. Material launch proposals require explicit authorized human approval;
   corrections create immutable versions and bulk accept stays unreviewed.
10. Only C16 with current lease/fencing token and expected prior may activate a
    fully verified immutable graph target.
11. Query responses pin one active graph version and disclose projection
    watermark/lag; bounded traversal is mandatory.
12. Production cannot enable or submit instrumented runtime evidence; no raw
    integration payload or reversible fingerprint is stored.
13. Privacy/security deterministic failures quarantine and audit; they are not
    repeatedly retried.
14. Replays/redrives/recovery are planned, bounded, conditional, idempotent,
    audited and reconciled.
15. Missing/stale/conflicting/incomplete/excluded/unresolved/redacted state is
    explicit in APIs, UI, metrics and timeline.

## 17. Stop and Escalate Conditions

**Stop and escalate** to the named owners before implementation/deployment when:

- two authoritative specifications conflict on identity, evidence semantics,
  confidence, approval, publication, privacy, retention, RPO/RTO or AWS service;
- a required contract has no producer/consumer owner or stable immutable key;
- completion would require weakening a P0 invariant, expected-state check,
  Object Lock, no-payload rule, production hard-deny, ABAC or audit;
- the only solution requires arbitrary model/repository access, generic tools,
  public endpoint, unrestricted egress, wildcard cross-account trust or shared
  admin role;
- an irreversible/destructive migration lacks tested backup/restore/rollback
  and exact target resolution;
- representative load/graph/source behavior differs enough to invalidate the
  approved capacity model or SLO;
- external source API, Region, account, retention, domain SLO tier, graph
  sizing/partition or model choice is not approved and materially changes code;
- a required deployed INT/E2E/DR test cannot run because account/quota/source/
  identity/standby access is absent;
- a security/privacy test finds prohibited content outside quarantine or an
  uncontained production-enable path;
- an expired waiver, critical UNKNOWN, missing owner/runbook or failed recovery
  would be carried into release.

Continue safe contract/unit work when a deployed dependency is blocked, but
label the component incomplete and never fabricate evidence or silently choose
a materially different architecture.

## 18. Review and Pull-Request Checklist

Each change answers:

- Which requirement, CT, INT and E2E IDs change?
- What immutable business identity and idempotency rule apply?
- What exact durable state/effect and forbidden effects were asserted?
- Which contracts/examples/clients and compatibility versions changed?
- What transient, invalid, incomplete, conflict, poison and finally paths pass?
- What least-privilege/data class/network/KMS/egress/retention/audit controls
  changed and which negative tests prove them?
- What metrics/logs/traces/audit/alarms/runbooks/timeline are added?
- What scale/cost/capacity behavior and rollback/migration apply?
- Which deployed test environment and immutable evidence manifest prove it?
- Did cleanup/reconciliation finish with no orphan/active test state?

Reviewers reject vague claims such as supports, handles, resilient, secure,
tested or backwards compatible without the observable proof defined here.

## 19. Final Evidence Checklist

The **Final evidence checklist** for a release candidate contains:

- Git commit, signed container digests/SBOM/provenance, dependency locks, CDK
  assembly hash, contract/policy/analyzer/model and fixture versions.
- Passing documentation/static/type/unit/contract/policy/component results.
- C01-CT through C18-CT manifests and all 585 P0 traceability coverage.
- INT-001..INT-138 reports with all six dimensions.
- E2E-001..E2E-014 signed manifests on the same candidate.
- IAM/ABAC/network/KMS/egress/secrets/supply-chain/CloudTrail/S3-data-event and
  prohibited-data scan reports.
- Accessibility, browser, load/fairness/SLO/cost, chaos, reconciliation,
  redrive/replay, projection rebuild, backup/restore and regional failover/
  failback reports.
- Active accepted-manifest/proposal/pointer/Neptune/OpenSearch counts/checksums/
  watermarks and query/timeline captures for the launch canary.
- Dashboard/alarms/synthetics/no-data state, on-call routing and exercised
  runbooks with owners.
- Cleanup/orphan/cost/credential/flag/session/lease reconciliation.
- Current waivers with scope/owner/compensating control/expiry; none may weaken
  a non-waivable P0 launch gate.
- Product, architecture, security/privacy, governance, accessibility, QA, SRE
  and release approvals.

Only after evidence verification passes may the coding agent state that the
working lineage collection application is successfully implemented.
