# Shared State and Error Model

**Status:** Normative  
**Applies to:** C01-C18

## 1. Design Rule

Transport delivery is at least once. Business state is idempotent by immutable
identity and conditional write. A successful retry or replay produces the same
observable business result, while preserving attempt-level operational history.

Every operation ends in a success state, a visible incomplete/conflict state,
a deterministic quarantine with an owner action, or a retry/redrive path. No
repository, deployment, hole, candidate edge, evidence envelope, proposal,
decision, or publication attempt disappears silently.

## 2. Common Operation Record

Every asynchronous consumer records:

- Idempotency identity and payload checksum.
- Contract, producer, policy, and software versions.
- First/last received time and delivery/attempt count.
- Current processing state and lease/fencing token where applicable.
- Immutable input/output `EvidenceReference` values.
- Error class/code, sanitized detail, dependency, retry eligibility, next
  attempt, and owner action.
- Common correlation identifiers and audit event reference.

Conditional creation chooses one of:

1. `NEW`: reserve the business identity and process.
2. `DUPLICATE_SAME_CONTENT`: acknowledge and return the prior result.
3. `DUPLICATE_CONFLICTING_CONTENT`: enter `CONFLICT`; preserve both checksums.
4. `IN_PROGRESS`: do not start a second writer; retry after lease or return the
   existing run.
5. `TERMINAL_REDRIVE_ALLOWED`: create a new attempt linked to prior history.

## 3. Error Classes

| Class | Meaning | Examples | Retry | Required terminal/next state |
|---|---|---|---|---|
| `TRANSIENT` | Same valid input may succeed without correction | Throttle, timeout, network reset, temporary Batch capacity, Neptune conflict | Bounded exponential backoff with jitter | Retry, then `POISON_REPEATED` after policy limit |
| `DETERMINISTIC_INVALID` | Input/policy/implementation cannot succeed unchanged | Schema failure, missing immutable identity, unsupported syntax, prohibited evidence | No automatic retry | Quarantine with reason and named remediation |
| `INCOMPLETE` | Expected evidence/input did not arrive | Missing inventory page, sidecar manifest, dependency, native facet | Retry only when missing dependency can arrive | Explicit incomplete state; block completion/promotion as specified |
| `CONFLICT` | Two individually valid claims cannot be selected safely | Identity collision, evidence disagreement, expected graph version changed | No blind retry | Preserve claims; deterministic resolver or human review |
| `POISON_REPEATED` | Delivery repeatedly fails beyond bounded policy | Consumer crash on one envelope, persistent dependency defect | DLQ; governed redrive only | DLQ/quarantine with alert, runbook, audit |

Privacy violations are always `DETERMINISTIC_INVALID`, even when the sender
could retry after removing the field. The invalid content is not copied into
operational logs; only allowlisted metadata, field name/path, reason code, and
content hash are retained under the security policy.

## 4. Retry Policy

- Retry only `TRANSIENT` failures or explicitly waiting `INCOMPLETE` states.
- Use capped exponential backoff with full jitter and a component-specific
  maximum elapsed time.
- Respect dependency `Retry-After` and service quotas.
- Do not retry schema, authorization, privacy, unsupported-language, missing
  immutable identity, or verification correctness failures.
- Each attempt rechecks lease/fencing ownership before side effects.
- Retries reuse business identity and output location; they do not create a new
  proposal, graph version, or accepted manifest unless the prior attempt did
  not make that business transition.
- Exhaustion produces a durable terminal record, metric, alert where P0, and
  owner/runbook link.

## 5. Quarantine

A quarantine record contains business identity, sanitized source metadata,
input checksum/reference where policy permits, contract/policy version, error
class/code, first/last occurrence, owner/domain, required correction, replay
eligibility, and correlation fields.

Required rules:

- Quarantine is queryable through C17 and measurable through C18.
- Corrected data creates a new source event/version and links to the quarantine.
- Replay requires authorization and records actor, reason, selected records,
  target contract/policy version, and new run IDs.
- An UNKNOWN classification quarantine cannot be auto-resolved by an LLM into
  an exclusion.
- A forbidden runtime envelope is never forwarded to Kinesis or the general
  evidence store.

## 6. DLQ, Redrive, and Replay

Every SQS work queue has a dedicated DLQ with:

- Maximum receive count based on operation cost and expected transience.
- Alarm on first Tier-1 item and on age/depth thresholds for other priorities.
- Runbook naming validation, dependency-health, code rollback, and replay steps.
- Redrive allowlist, batch limit, concurrency limit, and circuit breaker.
- Attempt linkage so redrive cannot bypass idempotency or create duplicate
  business effects.

EventBridge archive replay re-enters C03 validation and idempotency. Step
Functions redrive resumes from recorded stage outputs when valid rather than
repeating completed Batch work. Projection rebuild reads accepted manifests,
not mutable Neptune/OpenSearch state.

## 7. Baseline Run State

```text
REQUESTED -> INVENTORY -> CLASSIFICATION -> CONTEXT -> ANALYSIS
          -> VERIFICATION -> PROPOSAL -> AWAITING_REVIEW
          -> PUBLICATION -> COMPLETE
```

Alternative visible states: `INCOMPLETE`, `QUARANTINED`, `FAILED`, `CANCELLED`,
and `SUPERSEDED`.

- A critical `UNKNOWN` repository prevents `COMPLETE` but does not erase work
  completed for other repositories.
- A source inventory marked partial propagates an incomplete coverage reason.
- Human review time is not counted as workflow compute failure.
- Publication failure after approval remains redrivable; the proposal stays
  approved and the active pointer remains unchanged until fencing succeeds.

## 8. Incremental Run State

```text
RECEIVED -> NORMALIZED -> CLASSIFIED -> INVALIDATION_PLANNED
         -> ANALYSIS -> VERIFICATION -> DIFF_READY
         -> AWAITING_REVIEW -> BOUND -> PUBLISHED -> COMPLETE
```

- Documentation no-impact may transition from `CLASSIFIED` to `COMPLETE` with
  an immutable reason record.
- An event awaiting UNKNOWN resolution remains replayable from the normalized
  trigger.
- A deployment must reach a lineage decision: current binding, approved new
  binding, explicit stale/missing alert, or governed blocked deployment.
- Superseding an undeployed PR commit records both identities. A deployed
  artifact is never coalesced away.

## 9. Runtime Session State

```text
REQUESTED -> ENABLING -> READY -> COLLECTING -> DRAINING
          -> DISABLED -> COMPLETE
```

Terminal alternatives: `INCOMPLETE`, `TRUNCATED`, `FAILED`, `EXPIRED`, and
`CANCELLED`.

Normative transition rules:

- `READY` requires every expected sidecar to attest the integration environment,
  compatible version, matching digest, and active signed session.
- Test start before `READY` is rejected and audited.
- `DRAINING` waits for expected sequence ranges and closing manifests subject
  to the session deadline.
- The flag-disable action executes in a finally path for every outcome.
- Expiry is an independent kill switch and cannot be extended by a sidecar.
- `COMPLETE` requires all manifests, no sequence gap, matching checksum, and
  persisted evidence.
- `INCOMPLETE` or `TRUNCATED` cannot promote confidence.

## 10. Proposal State

```text
DRAFT -> AWAITING_REVIEW -> APPROVED -> PUBLISHING -> ACTIVE
                         -> REJECTED
                         -> SUPERSEDED
AWAITING_REVIEW -> DRAFT  (correction creates a new version)
PUBLISHING -> FAILED -> PUBLISHING  (governed redrive)
```

- State transitions use proposal ID/version plus expected current state.
- Reviewer corrections never mutate the prior proposal.
- A stale browser edit receives a conflict response containing current version;
  it cannot overwrite a newer decision.
- Rejection, supersession, and failed publication preserve evidence and audit.
- Approval records the exact proposal checksum reviewed.

## 11. Publication State and Fencing

```text
RESERVING -> STAGING -> VERIFYING -> COMMITTING -> PROJECTING -> ACTIVE
                         \-> FAILED_REDRIVABLE
RESERVING -> VERSION_CONFLICT
```

1. Conditional reservation requires expected active graph version.
2. The reservation issues target version, lease expiry, and monotonic fencing
   token.
3. Staging writes an immutable target-version namespace.
4. Verification checks accepted-manifest checksum, expected counts, endpoint
   identities, and target namespace.
5. The committing transaction rechecks reservation owner, unexpired lease,
   fencing token, and expected prior pointer.
6. A worker that loses lease can finish local work but cannot advance state.
7. OpenSearch projection lag does not roll back an already active Neptune graph;
   it produces a watermark/alert and idempotent projection retry.

## 12. Evidence Conflict State

Conflicts are data, not exceptions to discard:

- `IDENTITY_AMBIGUITY`: multiple canonical endpoints remain possible.
- `STRUCTURAL_DISAGREEMENT`: collectors disagree whether an edge/path exists.
- `DERIVATION_DISAGREEMENT`: mappings/transforms disagree.
- `VERSION_MISMATCH`: evidence refers to different commits/digests/environments.
- `SCHEMA_MISMATCH`: field/type/catalog versions cannot be reconciled.

C13 records all claims and precedence decisions. A deterministic higher-
authority claim may resolve a conflict automatically under versioned policy;
otherwise C15 exposes it for review. Conflict never becomes a high-confidence
edge merely by averaging sources.

## 13. Cancellation and Expiry

- Cancellation is authorized, idempotent, and records actor/reason.
- Batch cancellation cleans ephemeral workspaces and leaves immutable completed
  stage outputs addressable for audit.
- Runtime cancellation disables collection and drains only within the remaining
  privacy/session deadline.
- Lease/session expiry uses a service-side trusted clock.
- TTL may remove temporary lease/session-operational rows only after immutable
  terminal evidence exists. TTL never applies to accepted manifests, labels,
  decisions, graph pointers, or required audit history.

## 14. Operator Evidence

For every P0 failure/recovery test, retain:

- Trigger/input identity and checksum.
- Run/workflow/job/session/proposal/graph IDs.
- Before/after durable state.
- Attempt/retry/redrive history.
- Sanitized error class/code and emitted metrics/alarms.
- Operator action and runbook revision.
- Proof of idempotent result and absence of duplicate business effects.
- For privacy/security failures, the corresponding audit record without the
  prohibited content.
