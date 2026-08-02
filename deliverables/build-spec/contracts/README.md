# Contracts — Machine-Readable Shapes for the Collection Platform

| | |
|---|---|
| **Status** | Draft — for review (normative once approved) |
| **Role** | The package's machine-readable contract set: JSON Schema (draft 2020-12) for data shapes, OpenAPI 3.1 for API surfaces, and the event catalog for the 17 triggers. These files formalize contracts that previously existed only as prose. |

## Provenance rule

Every file here carries an `x-source` field (or a source table for markdown) citing the exact prose section it formalizes. **For shape questions the file is normative; for semantics the cited prose remains normative.** A change to a shape is a reviewed PR against this directory *and* the prose it cites — they must not drift (checked by [../10-verification-and-traceability.md](../10-verification-and-traceability.md)).

Constraints a JSON Schema cannot express (scoring ceilings, coverage accounting, cross-environment rejection) are listed in each file's `x-non-schema-constraints` / noted in prose, with the component that enforces them.

## Inventory

| File | Formalizes | Primary producer → consumers |
|---|---|---|
| `schemas/observation-envelope.schema.json` | Ingestion envelope + OL-aligned payload + per-signal assertion constraints (workflow-spec §5.1–5.2) | all signal emitters → B7 gateway |
| `schemas/lineage-artifact.schema.json` | Immutable candidate artifact (assessment §3 + determinants) | C3 extractor → C4 registry, C6 diff, W3 gate |
| `schemas/delta.schema.json` | `{added, changed, removed}` delta (workflow-spec §6) | C6 diff → C9 renderer, B8 UI, C8 policy |
| `schemas/determinant-set.schema.json` | Per-edge determinant set, F-03 (workflow-spec §7) | C3 extractor → X2 classifier (inverted index) |
| `schemas/repo-classification.schema.json` | Business App registry record + ADR-029 classification | B1 registry → W1, X1, X2, X4 |
| `schemas/coverage-report.schema.json` | Coverage report states (workflow-spec §1/§8, approval spec screen 1) | X4 reporter → B8 UI, endpoint 22 |
| `schemas/flow-status.schema.json` | Per-flow status record, ADR-026 (08 §5.3) | every workflow → endpoint 29, screen 7 |
| `schemas/review-record.schema.json` | Immutable review record (ADR-024, approval spec §7) | B8/B9 → endpoint 27, auditors |
| `openapi/registry-api.openapi.yaml` | Endpoints 21–22 + reclassification (B1 surface) | UI/catalog sync → B1 |
| `openapi/ingest-gateway.openapi.yaml` | Envelope submission + schema serving (B7 surface) | signal emitters → B7 |
| `openapi/approval-api.openapi.yaml` | Endpoints 23–29 (B8 surface) | SPA → B8 |
| `events/event-catalog.md` | The 17 trigger rows as EventBridge events | emitters per row → workflow rules |

## Out of scope

Endpoints 1–20 (graph-core catalog: lineage read, impact, attestations, waivers) remain specified in [../../architecture-review-v8/04-high-level-design.md](../../architecture-review-v8/04-high-level-design.md) §7 as prose — the graph core is outside the collection plane this package specifies. `throughline.yaml` (including the ADR-029 `kind:` field) is specified in HLD §6.2; formalizing it as JSON Schema is a Phase-0 implementation task noted in [../01-onboard.md](../01-onboard.md).

## Versioning

Schema evolution follows ADR-027 / workflow-spec §5.4: additive-first (new optional fields/facets = minor), removals/re-typing = major with a dual-publish window. `$id` embeds the version. The git history of this directory is the registry history; publication to S3 (B6) is a build artifact of this directory.
