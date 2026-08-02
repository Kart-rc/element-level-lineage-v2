# 09 — End-User Testing

| | |
|---|---|
| **Status** | Draft — for review (normative once approved) |
| **Role** | Comprehensive end-user testing for the application and its interfaces: personas, the full interface inventory, and the numbered end-to-end journeys (E2E-01…E2E-07) that compose the step docs' use cases into user-visible proof. Each journey is executable as an acceptance run on the pilot slice. |

## 1. Personas

| Persona | Who | Primary interfaces |
|---|---|---|
| **Repo developer** | Pushes code, opens PRs, reads the gate | PR check + comment (C9), scaffold PRs, flow status by SHA |
| **Edge owner / viewer** | Team member reviewing own edges | Screens 2–4, PR jump-link |
| **Domain steward** | Finalizes proposals; works identity/waiver/drift queues | Screens 1–6, endpoints 23–28 |
| **Platform admin** | Registers apps, ramp stages, installation health | Screen 7, registry API |
| **Operator** | Runs the fleet | Dashboards, DLQ/redrive, replay, wave calendar, quotas |

## 2. Interface inventory

| Interface | Definition | Journeys touching it |
|---|---|---|
| PR status check + comment | [03 §5.6](03-incremental-collection.md) (C9) | E2E-02, 03, 06 |
| Approval SPA screens 1–7 | [06 §5.1](06-approval.md) (B8); approval spec §3 | E2E-01, 02, 04, 05 |
| Registry API (endpoints 21–22 + reclassify) | [`registry-api.openapi.yaml`](contracts/openapi/registry-api.openapi.yaml) | E2E-01 |
| Approval API (endpoints 23–29) | [`approval-api.openapi.yaml`](contracts/openapi/approval-api.openapi.yaml) | E2E-01, 02, 05 |
| Coverage report | [`coverage-report.schema.json`](contracts/schemas/coverage-report.schema.json), screen 1 | E2E-01, 05, 07 |
| Flow status ("where is my run?") | [`flow-status.schema.json`](contracts/schemas/flow-status.schema.json), endpoint 29, screen 7 | all |
| Scaffold PRs | [01](01-onboard.md)/[02](02-baseline-collection.md) (C2) | E2E-01 |
| F-06 / drift / expiry notifications | [05](05-deployment-promotion.md), [07](07-nightly-reconciliation.md), [06](06-approval.md) | E2E-04, 05 |
| Operator dashboards + runbooks | [08 §5.1](08-scale-and-visibility.md) (C12) | E2E-07 |

Every journey below ends with the same two assertions: **(V1)** each flow involved has a complete flow-status record reachable by correlation ID, repo/SHA, or deploymentId; **(V2)** every rendered confidence is integer + band, and every absent/unknown region renders as one of the seven consumer states — never blank space.

## 3. End-to-end journeys

### E2E-01 — Onboard to approved graph (the pilot's founding journey)

Personas: platform admin → repo developer → domain steward. Composes: UC-1-01…-08, UC-2-01…-07, UC-6-01.

1. Admin registers the pilot Business App (screen 7 / endpoint 21) with 3–5 member repos of mixed classes and activity.
2. **Expect:** 201; nothing else to do — baseline visible as in-flight in flow status within minutes.
3. A member repo lacking `throughline.yaml` receives a scaffold PR; extraction proceeds anyway (developer sees the PR; F-05).
4. **Expect (≤ overnight):** coverage dashboard (screen 1) shows every member in exactly one state (`automated` / `library` / `automated:declarations` / `excluded:*` / `dormant` / `error`); app graph queryable at Advisory; review inbox (screen 2) seeded with the baseline proposal, material edges flagged.
5. Steward opens the proposal, reviews evidence per edge (screen 4: signals, determinants, the "capped at 64" cap where no runtime evidence exists), accepts/corrects material edges, finalizes.
6. **Expect:** 422 first if any material edge is unacknowledged (deliberately test it); then a chain-valid review record (screen 6, `chainVerified: true`); edges `ProducerAttested`; trust and band shown as separate facts on every edge.

### E2E-02 — Push to delta to approval

Personas: repo developer → edge owner → steward. Composes: UC-3-01…-03, UC-6-01/-04, UC-8-01.

1. Developer pushes a doc-only commit. **Expect:** no PR noise; flow status for the SHA reads `no-impact` with the classifier's evidence; zero compute beyond the classifier.
2. Developer pushes a SQL transform change. **Expect:** flow status shows the selective path; only determinant-affected edges re-derived; delta lands in the inbox with before/after side-by-side (screen 3).
3. Edge owner corrects one edge (the engine's expression was wrong). **Expect:** correction captures before/after; after finalize, the record freezes both; the calibration corpus gains an honest labeled pair.
4. Lockfile-bump variant: bump a shared library in a consumer repo. **Expect:** consumer edges re-derive via manifest determinants (the ADR-029 library bridge) — no scan of the library repo itself.

### E2E-03 — PR gate under 30 seconds

Persona: repo developer. Composes: UC-3-04…-06, -08, -09, -11.

1. Open a PR changing a material mapping. **Expect:** one status check + one comment, p95 < 30 s over 20 trials; delta highlighted; jump-link opens screen 3 pre-filtered.
2. Push more commits. **Expect:** the same comment updates in place (no spam); prior decision superseded, kept for audit.
3. Force a timeout (test hook). **Expect:** fail-open + warn check stating the degradation — never green-by-silence.
4. With ramp = block and a deterministic breaking change: **Expect:** block with evidence; an LLM-derived edge in the same delta surfaces as information only; waiver flow works from the check (downstream owner approves; developer's self-approval rejected).
5. Truncated-traversal variant. **Expect:** warn with "impact bounded — truncated at N", never "no impact".

### E2E-04 — Deploy, promote, rollback

Personas: repo developer → operator. Composes: UC-5-01…-08, UC-3-07.

1. Merge the E2E-03 PR. **Expect:** candidate `MergedCandidate`; lineage views still answer with the *previous* deployment's version for the environment.
2. Deploy succeeds. **Expect (≤ 10 min):** the exact digest's lineage is authoritative for the environment; a new PR on the service now diffs against this deployment (visible in its gate comment's baseline line).
3. Roll back. **Expect:** prior version reactivated; both transitions in queryable history; drift re-evaluation fired; nothing deleted.
4. Hotfix drill: deploy a digest with no lineage package. **Expect:** unskippable F-06 alert in the team channel + admin health screen; `observed-unbound` visible; closure path (baseline the SHA, re-bind) works.

### E2E-05 — Nightly catches what the day missed

Personas: operator → steward → repo developer. Composes: UC-7-01…-05, UC-6-11.

1. Simulate a dropped webhook (receiver disabled for one push, re-enabled). **Expect:** next nightly emits a `missed-event` finding; the state is repaired attributably (nightly correlation ID); the developer's flow-status query for that SHA shows the repair.
2. Seed a classifier bug (drill rule pack). **Expect:** `classifier-miss` findings with the suspect rule pack named; divergence trend alarm; steward drift tab shows the roll-up, not a flood.
3. One finding contradicts a `ProducerAttested` edge. **Expect:** edge demoted to `UnderReview` with the finding attached; steward re-reviews from the drift tab.
4. Coverage refresh: a member gone quiet past its channel window shows `stale` — dimmed with an age badge, excluded from Verified styling.

### E2E-06 — Sidecar lifts confidence inside the change loop

Personas: repo developer. Composes: UC-4-01…-03, UC-3-04.

1. Open a PR whose integration tests run under the flagged sidecar. **Expect:** the PR comment gains "N of M changed paths executed under integration tests" before merge.
2. Inspect an executed edge (screen 4). **Expect:** test-environment evidence listed; in prod context the band tops out at Probable ("test-corroborated"); prod Verified appears only after prod evidence (CloudWatch/OTel) lands — visible later as an asynchronous band change with no human action.
3. Negative check: no `sidecar-test` evidence exists tagged prod anywhere; the misconfiguration alarm drill (inject one) fires.

### E2E-07 — 10k-repo wave with lanes held (Phase 5 rehearsal)

Personas: operator. Composes: UC-8-02/-03/-08, UC-2-09, UC-7-09.

1. Launch the synthetic 7,000-active-repo baseline wave (2k design point and 10k ceiling both exercised in the rehearsal plan).
2. **Expect:** wall-clock within `W / C_wave` prediction; quota alarms quiet (headroom requested ahead of need); Spot interruptions retried invisibly.
3. Mid-wave, run E2E-03 concurrently. **Expect:** gate p95 unmoved — the PR lane's reservation held.
4. Trigger backpressure (constrain the budget). **Expect:** backfill pauses first, checkpointed; resumes; nothing lost; the whole drama legible on the lane dashboard.
5. Operator answers "where is repo X's baseline?" in one lookup (screen 7).

## 4. Execution and tooling

- Journeys run against the **test stage + sandbox GitHub org** (the live-dependency environments of each step doc's §10); E2E-07 runs in the Phase 5 rehearsal window.
- Each journey is scripted (Playwright for SPA legs, API scripts for the rest) with human sign-off checkpoints where judgement is the feature under test (steward decisions).
- A journey passes only if its composed UCs' criteria hold **and** V1/V2 hold at every step.
- Accessibility gate on SPA legs: severity/trust never color-only; decision flow keyboard-completable (approval spec §8) — checked with automated a11y scans plus a manual keyboard run of E2E-01 step 5.

## 5. Traceability

- Journey → UC map: E2E-01 → UC-1-01…-08, UC-2-01…-07, UC-6-01 · E2E-02 → UC-3-01…-03, UC-6-01/-04, UC-8-01 · E2E-03 → UC-3-04…-06/-08/-09/-11 · E2E-04 → UC-5-01…-08, UC-3-07 · E2E-05 → UC-7-01…-05, UC-6-11 · E2E-06 → UC-4-01…-03, UC-3-04 · E2E-07 → UC-8-02/-03/-08, UC-2-09, UC-7-09.
- Every persona exercises at least one journey; every interface in §2 appears in at least one journey.
