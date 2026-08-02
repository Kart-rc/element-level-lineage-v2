# Event Catalog — the 17 Triggers as Machine Events

| | |
|---|---|
| **Status** | Draft — for review (normative once approved) |
| **Role** | The trigger matrix's 17 rows ([../../../aws-lineage-collection-plan/03-trigger-matrix.md](../../../aws-lineage-collection-plan/03-trigger-matrix.md)) as buildable EventBridge events: name, emitter, payload essentials, idempotency key, queue lane. Semantics live in the trigger matrix and the owning step docs — this catalog adds only the machine-facing details. There is no row for manual invocation (ADR-023), and none may ever be added. |

Conventions: all events go to the `throughline-collection` EventBridge bus with `source = tl.<emitter-id>` and `detail-type = <event name>`; every `detail` carries `correlationId` (the originating envelope `eventId`) plus the fields below; rule names mirror the HLD Kafka topic map 1:1 (ADR-022). Dedup happens at the consumer against the idempotency key (EventBridge is at-least-once).

| Row | Event (`detail-type`) | Emitter | Payload essentials (`detail`) | Idempotency key | Lane | Owning doc |
|---|---|---|---|---|---|---|
| 1 | `onboarding.registered` | B1 registry | `{appId, repos[], environments[], criticalityTier}` | `appId` + registration hash | baseline/backfill | [01](../../01-onboard.md) |
| 2 | `repo.onboarded` | C1 receiver | `{repo, installationId, defaultBranch}` | `X-GitHub-Delivery` GUID | baseline/backfill | [01](../../01-onboard.md) |
| 3 | `repo.inventory.delta` / `repo.classified` | B2 adapter / B1 registry | `{added[], removed[], syncRunId}` / `{repo, appId, class, method, classifiedAt}` | `syncRunId` / `(repo, classifiedAt)` | baseline/backfill | [01](../../01-onboard.md) |
| 4 | `repo.push` | C1 receiver | `{repo, sha, changedFiles[], pusher}` | `X-GitHub-Delivery` GUID | (EventBridge-direct → W2) | [03](../../03-incremental-collection.md) |
| 5 | `repo.pr.updated` | C1 receiver | `{repo, prNumber, headSha, baseSha, action}` | `X-GitHub-Delivery` GUID | pr-gate (FIFO by repo) | [03](../../03-incremental-collection.md) |
| 6 | `repo.pr.rebased` | C1 receiver | `{repo, prNumber, oldHeadSha, newHeadSha}` | `X-GitHub-Delivery` GUID | pr-gate | [03](../../03-incremental-collection.md) |
| 7 | `repo.pr.merged` | C1 receiver | `{repo, prNumber, mergeSha, headSha}` | `X-GitHub-Delivery` GUID | (EventBridge-direct, candidate recorder) | [03](../../03-incremental-collection.md) |
| 8 | `deploy.succeeded` | C10 adapter | `{environment, serviceUrn, artifactDigest, deploymentId, deployedAt}` | `deploymentId` | deploy | [05](../../05-deployment-promotion.md) |
| 9 | `deploy.failed` / `deploy.rolledback` | C10 adapter | `{environment, serviceUrn, artifactDigest?, priorDeploymentId?, deploymentId}` | `deploymentId` + outcome | deploy | [05](../../05-deployment-promotion.md) |
| 10 | `schedule.nightly` | EventBridge Scheduler | `{scopeWave, date}` | `(date, scopeWave)` | baseline/backfill | [07](../../07-nightly-reconciliation.md) |
| 11 | `interaction.aggregation` | Scheduler → B3 | `{window, logGroupScope}` | `(window, scope)` | (bypass — Firehose path, never the bus at span scale) | [04](../../04-runtime-corroboration.md) |
| 12 | `registry.changed` | Registry adapter | `{subject, version, changeKind, deleted?}` | `(subject, version)` | baseline/backfill | [07](../../07-nightly-reconciliation.md) |
| 13 | `collector.heartbeat-lost` | Freshness monitor (C12 SLIs) | `{collector, lastSeenAt, channelWindow}` | `(collector, windowEnd)` | (EventBridge-direct, coverage lifecycle) | [04](../../04-runtime-corroboration.md) |
| 14 | `ttl.expiry-approaching` | TTL sweep (Scheduler) | `{kind: waiver\|attestation, id, expiresAt, owner}` | `(id, expiresAt)` | (EventBridge-direct, steward notifier) | [06](../../06-approval.md) |
| 15 | `toolchain.updated` | Config-repo merge (CI) | `{promptVersion?, modelVersion?, rulePackVersions?, mergeSha}` | `mergeSha` | baseline/backfill (nightly Bedrock batch — never the PR path, F-04) | [03](../../03-incremental-collection.md) |
| 16 | `proposal.finalized` | B8 approval API | `{proposalId, appId, recordId, promotions[]}` | `recordId` | (EventBridge-direct → X3) | [06](../../06-approval.md) |
| 17 | `test.run.completed` | Test-automation service → B2 | `{testRunId, commitSha, artifactDigest, environment, flagState}` | `testRunId` | (EventBridge-direct → sidecar-evidence ingestion) | [04](../../04-runtime-corroboration.md) |

Notes:

- **Lanes.** Only three physical SQS lanes exist (pr-gate FIFO > deploy > baseline/backfill, ADR-026). Rows marked "EventBridge-direct" start their workflow from an EventBridge rule without queuing through a lane — they are either latency-tolerant singletons (7, 13, 14, 16) or the push path (4), whose classifier stage is Lambda-milliseconds and whose extraction stage competes for the shared Fargate budget, shedding per 08 §3.
- **Ordering.** Per-repo ordering matters only on the pr-gate lane (`MessageGroupId = repo`). Push events may arrive out of order across repos; within a repo the artifact key `(repo, sha, toolchainHash)` makes reordering harmless (later SHAs supersede by deployment/default-branch pointer, not by arrival).
- **Spikes.** A release train is an absorption problem, not a throughput problem: 100× spike ≈ 57 events/s vs EventBridge/SQS limits three orders of magnitude higher (08 §1).
