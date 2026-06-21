# Product Requirements Document: Throughline

**Enterprise Data Lineage and Impact Analysis Platform**  
**Status:** Draft for stakeholder review  
**Version:** 1.0  
**Date:** June 20, 2026  
**Audience:** Executive sponsors, product leadership, enterprise architecture, engineering, data platform, security, and governance teams  
**Canonical lineage format:** OpenLineage

## Executive Summary

Throughline is an enterprise platform for understanding how data is produced, transformed, exchanged, and consumed across operational services, streaming systems, analytical workloads, object storage, files, and external transfers. It gives leaders a portfolio-level view of data dependencies while allowing engineers to drill down to the dataset, column, field, job, run, and contract evidence behind each relationship.

The product addresses a common operational gap: organizations make schema, API, pipeline, and data-contract changes without a reliable way to know every downstream consumer that could fail. Existing knowledge is fragmented across orchestration tools, service catalogs, schema registries, code, dashboards, and team memory. As a result, impact analysis is slow, incidents are discovered after deployment, and ownership is unclear.

Throughline will use OpenLineage as the canonical format for lineage ingestion, interoperability, and export. It will accept OpenLineage run, job, and dataset events, preserve the original event evidence, and materialize a query-optimized graph for search, visualization, and impact analysis. Standard OpenLineage facets will be preferred. Throughline-specific extensions will use versioned, namespaced custom facets only when standard facets cannot express the required metadata.

The experience is organized into three connected workspaces:

1. **Lineage** shows data movement and transformation from enterprise domain to field level.
2. **Interactions** shows runtime service-to-service requests separately from persisted or transformed data lineage.
3. **Impact** simulates proposed changes, calculates blast radius, classifies risk, and links every conclusion to evidence and accountable owners.

Production success means that critical assets have fresh, explainable lineage; change owners can complete reliable impact analysis before release; platform teams can operate ingestion at enterprise scale; and governance teams can audit who knew what, when, and from which source.

## 1. Problem and Opportunity

### 1.1 Current Problems

- Lineage metadata is distributed across tools and represented inconsistently.
- Dataset-level lineage is often available, but element-level dependencies are incomplete or invisible.
- Runtime API calls are frequently mixed into data-flow diagrams even though requests and persisted datasets have different semantics.
- Schema changes are reviewed with manual searches, tribal knowledge, or broad dependency lists that do not identify the exact affected field.
- Ownership, freshness, confidence, and source evidence are missing from many lineage relationships.
- Existing diagrams do not scale from thousands of enterprise assets to a focused investigation.
- Security and governance teams cannot consistently determine where sensitive fields propagate or how they are transformed.
- Platform operators lack a unified view of connector health, ingestion lag, rejected events, and graph quality.

### 1.2 Opportunity

An OpenLineage-native platform can standardize metadata collection while preserving tool choice. A trustworthy graph projection can then support discovery, impact analysis, governance, and operational workflows without creating a proprietary exchange format. The combination of service-level orientation and field-level evidence gives both executives and engineers a useful view of the same system.

## 2. Product Vision and Principles

### 2.1 Vision

Every material data change can be evaluated against a current, explainable dependency graph before it reaches production.

### 2.2 Product Principles

1. **Open by default.** OpenLineage is the canonical lineage format for ingestion and export.
2. **Evidence before inference.** Every relationship exposes its producer, event time, observation time, schema version, confidence, and derivation method.
3. **Separate semantics.** Data lineage, runtime service interactions, and organizational groupings are connected but not conflated.
4. **Progressive disclosure.** Users move from domain to service, job, dataset, and field without loading the entire enterprise graph at once.
5. **Explain impact.** Every severity and affected asset must be traceable to a rule, contract, or uncertain assumption.
6. **Make uncertainty visible.** Stale, incomplete, conflicting, and inferred metadata is explicitly labeled.
7. **Secure metadata as production data.** Access control, auditability, privacy, retention, and operational resilience are first-class requirements.
8. **Do not automate irreversible action.** Initial releases advise and coordinate; they do not change schemas, code, or production systems.

## 3. Goals, Non-Goals, and Success Definition

### 3.1 Goals

- Establish OpenLineage as the enterprise lineage interchange contract.
- Provide searchable, multi-level lineage from domains to columns and fields.
- Support batch, streaming, file, topic, table, view, model, cache, and temporary dataset representations.
- Identify downstream impact of schema and field changes before deployment.
- Keep runtime service interactions discoverable without polluting the lineage graph.
- Provide ownership, classification, freshness, provenance, and confidence for assets and relationships.
- Scale ingestion, storage, traversal, and search for enterprise use.
- Support secure sharing, saved views, audit trails, exports, and APIs.
- Measure coverage, freshness, accuracy, adoption, incident reduction, and platform reliability.

### 3.2 Non-Goals

- Moving, transforming, or orchestrating customer data.
- Replacing an application performance monitoring or distributed tracing platform.
- Replacing source schema registries, service catalogs, data catalogs, or workflow orchestrators.
- Serving as a general-purpose query editor or data exploration environment.
- Automatically approving, deploying, or rolling back schema changes in the initial production release.
- Treating every service call as data lineage.
- Requiring producers to adopt a proprietary event format.
- Guaranteeing complete lineage when source systems do not emit sufficient evidence.

### 3.3 Success Definition

The platform is successful when a change owner can select or submit a proposed change, identify affected services and datasets, inspect field-level evidence and uncertainty, contact accountable owners, and export a review record without consulting multiple disconnected tools.

## 4. Users and Jobs to Be Done

| Persona | Primary job | Required outcome |
|---|---|---|
| Software engineer | Understand data produced or consumed by a service before changing a contract | A focused dependency view with endpoints, jobs, datasets, fields, and owners |
| Data engineer | Trace source-to-target transformations and diagnose failed or stale pipelines | Run-aware lineage with column transformations, versions, freshness, and evidence |
| Analytics or ML engineer | Determine which models, features, files, and activations depend on a field | Element-level upstream and downstream paths with transformation semantics |
| Enterprise architect | Understand cross-domain coupling and high-risk dependency concentration | Domain-level topology, ownership, criticality, and trend reporting |
| Data governance or privacy lead | Locate sensitive elements and verify masking or propagation | Classification-aware lineage with policy filters and auditable exports |
| Change approver | Evaluate whether a proposed change can proceed | Explainable blast radius, severity, unknowns, owners, and sign-off status |
| Platform operator | Keep metadata collection reliable and current | Connector health, ingestion lag, rejection reasons, replay, and reconciliation tools |
| Executive sponsor | Track adoption, risk reduction, and coverage | Portfolio metrics tied to critical systems and prevented or shortened incidents |

## 5. Scope and Product Experience

### 5.1 Global Navigation and Search

Users can search services, OpenLineage jobs, datasets, topics, files, columns, fields, domains, owners, tags, and external systems from a shared entry point. Search results display asset type, namespace, environment, owner, criticality, freshness, and evidence status. Deep links preserve scope, selected path, graph version, and filters.

### 5.2 Lineage Workspace

The Lineage workspace presents a data-flow graph with progressive levels:

1. Enterprise domains and cross-domain dependency counts.
2. Services, external sources, analytical applications, transfers, and data-processing jobs.
3. Input and output datasets, topics, files, views, models, and temporary outputs.
4. Columns or fields and their direct or indirect transformations.
5. Run and source evidence supporting a selected relationship.

Batch and stream relationships are visually distinct. Selecting an asset focuses its immediate neighborhood and fades unrelated nodes. Users can expand or collapse nodes, trace upstream or downstream paths, filter by environment or time, and inspect ownership and metadata in a side panel.

### 5.3 Interactions Workspace

The Interactions workspace displays runtime service calls as a caller-to-callee matrix. It supports REST, GraphQL, gRPC, and asynchronous event contracts. Selecting a populated cell displays operation, direction, mode, payload or schema reference, latency objective, source system, last observation time, and linked OpenLineage jobs or datasets when available.

Service interactions are a separate model because an API request is not necessarily an OpenLineage dataset transformation. The platform may cross-reference the two models but must not manufacture lineage edges from traces without an explicit, reviewable mapping rule.

### 5.4 Impact Workspace

The Impact workspace accepts a proposed change from a manual schema diff, supported schema file, contract registry integration, source-control integration, or OpenLineage dataset metadata comparison. The impact engine evaluates a versioned graph snapshot and returns:

- Originating asset and element
- Proposed additions, removals, renames, type changes, nullability changes, and semantic changes
- Affected services, jobs, datasets, fields, files, topics, models, transfers, and external consumers
- Severity of `BREAK`, `WARN`, `INFO`, or `UNKNOWN`
- The rule, evidence, graph path, and freshness behind each result
- Owners, criticality, and notification or review status
- Known metadata gaps that could invalidate the result

Users first see the service-level blast radius, then drill down to datasets, fields, schema diffs, and consumers. The analysis can be saved, shared, exported, compared, and re-run against a newer graph snapshot.

## 6. Core User Journeys

### 6.1 Investigate an Existing Field

1. The user searches for a qualified dataset or field.
2. The platform displays matching assets with namespace and environment context.
3. The user opens the Lineage workspace and selects upstream, downstream, or both.
4. The graph shows a bounded path and indicates incomplete or stale evidence.
5. The user selects a field to view direct and indirect dependencies, transformations, masking, and owning teams.
6. The user saves or shares the view with its graph version and filters.

### 6.2 Review a Proposed Schema Change

1. The change owner selects an asset and supplies the proposed schema or diff.
2. The platform validates the input and identifies the baseline version.
3. The impact engine traverses field and dataset dependencies using a consistent graph snapshot.
4. Results are grouped by affected service, with breaking items first.
5. The owner inspects the evidence, unknowns, and compatibility rules.
6. Accountable teams acknowledge, approve, reject, or request remediation.
7. The platform stores an immutable analysis record and can re-run it before deployment.

### 6.3 Diagnose a Production Data Incident

1. An engineer opens a failed run, stale dataset, or affected output.
2. The platform shows recent run events and the graph version active at the incident time.
3. The engineer traces upstream jobs and datasets, filtering by failed or changed assets.
4. Field-level lineage identifies relevant transformations and versions.
5. The engineer exports the evidence path or links it to the incident system.

### 6.4 Review a Service Contract

1. An engineer selects a caller-to-callee cell in the Interactions matrix.
2. The platform shows protocol, operation, mode, contract reference, objective, and evidence source.
3. Linked jobs, datasets, and impact analyses are shown separately.
4. The engineer follows a cross-reference into Lineage only when a supported mapping exists.

## 7. Functional Requirements

### 7.1 Lineage and Discovery

| ID | Requirement | Acceptance criteria |
|---|---|---|
| LIN-001 | Provide domain, service/job, dataset, and element-level navigation | A user can move from a domain summary to a field and back without losing scope |
| LIN-002 | Support upstream, downstream, and bidirectional traversal | Direction is selectable and preserved in deep links and exports |
| LIN-003 | Render batch and stream data relationships distinctly | Every displayed edge exposes channel, producer evidence, and last observation |
| LIN-004 | Provide progressive expansion and bounded graph queries | The UI never requires loading the complete enterprise graph for normal navigation |
| LIN-005 | Expose field transformation semantics | Direct identity, transformation, aggregation, and indirect join/filter/group/sort/window/conditional relationships are distinguishable when supplied |
| LIN-006 | Show provenance and confidence | Each node and edge exposes producer, event time, observed time, schema URL, evidence type, and confidence state |
| LIN-007 | Show incomplete, stale, inferred, or conflicting lineage | Such states are labeled in the graph, details panel, API, and export |
| LIN-008 | Support time-aware lineage | Users can inspect the latest graph or a retained historical snapshot within policy limits |
| LIN-009 | Support filters | At minimum: domain, owner, environment, asset type, criticality, classification, freshness, evidence source, and channel |
| LIN-010 | Provide saved views and deep links | A saved view restores asset, graph version, direction, depth, filters, and selection |

### 7.2 Runtime Service Interactions

| ID | Requirement | Acceptance criteria |
|---|---|---|
| INT-001 | Maintain service interactions outside the OpenLineage graph projection | Interaction edges are stored and queried separately from lineage edges |
| INT-002 | Provide a caller-to-callee matrix | Rows are callers, columns are callees, and populated cells expose one or more contracts |
| INT-003 | Support REST, GraphQL, gRPC, and asynchronous contracts | Protocol, direction, operation, mode, and source evidence are queryable |
| INT-004 | Cross-reference interactions and lineage | Links exist only when an explicit mapping references an OpenLineage job or dataset |
| INT-005 | Preserve observation metadata | Each interaction includes source, first/last observed time, environment, and confidence |
| INT-006 | Prevent inferred requests from appearing as verified lineage | The UI and APIs retain type and evidence distinctions throughout navigation and export |

### 7.3 Impact Analysis

| ID | Requirement | Acceptance criteria |
|---|---|---|
| IMP-001 | Accept proposed schema and element changes | Supported inputs include manual diff and at least one machine-readable schema format at launch |
| IMP-002 | Use a consistent graph snapshot | Every result records the graph version, baseline schema, policy version, and analysis time |
| IMP-003 | Detect common schema changes | Add, remove, rename, type, length/precision, nullability, and compatibility changes are represented |
| IMP-004 | Calculate service-first blast radius | Results summarize affected services before dataset and field drill-down |
| IMP-005 | Provide explainable severity | Every `BREAK`, `WARN`, `INFO`, or `UNKNOWN` result includes the rule and dependency path |
| IMP-006 | Propagate through field-level lineage | Derived fields and indirect dependencies are included according to configured policy |
| IMP-007 | Make unknown impact explicit | Missing, stale, or contradictory evidence creates an `UNKNOWN` result or coverage warning |
| IMP-008 | Identify accountable owners | Impacted items expose technical owner, business owner when available, and escalation route |
| IMP-009 | Support review workflow | Authorized users can acknowledge, comment, approve, reject, or request remediation |
| IMP-010 | Support re-analysis and comparison | A saved analysis can be rerun and differences between results are visible |
| IMP-011 | Export an immutable review record | Export contains proposal, evidence paths, results, unknowns, decisions, actors, and timestamps |
| IMP-012 | Avoid automatic production changes | No impact action modifies source schemas, contracts, pipelines, or deployments in initial scope |

### 7.4 Search, Collaboration, and Administration

| ID | Requirement | Acceptance criteria |
|---|---|---|
| XFN-001 | Search all supported asset types | Results can be filtered and resolve ambiguous names with namespace and environment |
| XFN-002 | Provide stable asset URLs | Renames retain redirect or alias history where supported by source evidence |
| XFN-003 | Support comments and mentions | Comments are permission-aware, timestamped, and included in audit records |
| XFN-004 | Provide notifications and webhooks | Users can subscribe by asset, domain, owner, analysis, or severity |
| XFN-005 | Integrate with ticketing and chat systems | Impact findings can create or link work items without exposing unauthorized metadata |
| XFN-006 | Provide bulk ownership and classification operations | Changes require authorization and produce audit records |
| XFN-007 | Provide connector administration | Operators can configure, pause, test, replay, and monitor connectors |
| XFN-008 | Provide graph quality dashboards | Coverage, freshness, conflicts, orphans, rejected events, and source distribution are visible |
| XFN-009 | Provide API access | Search, traversal, asset detail, impact, administration, and export have documented APIs |
| XFN-010 | Provide accessible keyboard operation | Core search, graph selection, tables, side panels, and review workflows are usable without a pointer |

## 8. OpenLineage Requirements

### 8.1 Canonical Contract

OpenLineage is the authoritative interchange format for lineage. Throughline will ingest and export the OpenLineage object model rather than defining a parallel proprietary lineage envelope.

| ID | Requirement | Acceptance criteria |
|---|---|---|
| OL-001 | Accept OpenLineage `RunEvent`, `JobEvent`, and `DatasetEvent` payloads | Conforming payloads are validated, durably stored, acknowledged, and projected |
| OL-002 | Preserve original event evidence | The exact accepted payload, producer, schema URL, transport metadata, and receipt time remain retrievable subject to retention policy |
| OL-003 | Enforce naming policy | Jobs and datasets are keyed by OpenLineage namespace and name; runs retain source run IDs |
| OL-004 | Support run lifecycle states | Start, running, complete, abort, fail, and other states are retained without collapsing event history |
| OL-005 | Use standard facets first | Schema, column lineage, dataset type, ownership, lifecycle, version, source, parent, and quality metadata use published standard facets when applicable |
| OL-006 | Preserve unknown facets | Valid unrecognized facets remain in raw events and can be reprocessed after platform upgrades |
| OL-007 | Govern custom facets | Custom facets use a Throughline prefix, immutable schema URL, documented owner, compatibility policy, and deprecation path |
| OL-008 | Support column-level lineage | Output fields can reference input namespace, dataset, field, transformation type/subtype, description, and masking state |
| OL-009 | Validate schema URLs and payloads | Invalid events receive actionable errors and are never silently accepted into the trusted projection |
| OL-010 | Support HTTP and Kafka ingestion | Both transports expose authentication, encryption, backpressure, retry, and health metrics |
| OL-011 | Provide idempotent processing | Replayed identical events do not create duplicate logical observations or edges |
| OL-012 | Provide dead-letter and replay workflows | Authorized operators can inspect, correct at source, and replay rejected or failed events |
| OL-013 | Publish a compatibility matrix | Supported OpenLineage schema, client, integration, and facet versions are documented and tested |
| OL-014 | Export valid OpenLineage events | Exports validate against their declared schema URLs and do not embed internal graph-only fields in standard objects |
| OL-015 | Avoid identity mutation during projection | Domain, owner, alias, and UI labels do not replace canonical OpenLineage namespace/name identity |

### 8.2 Extension Policy

Throughline-specific metadata must not be placed in a custom facet when a standard OpenLineage facet can represent it. Proposed custom facets require architecture and governance review. Each facet must define:

- Entity attachment point: run, job, input dataset, or output dataset
- Business purpose and accountable owner
- Namespaced key and PascalCase schema type
- Immutable, versioned `_schemaURL`
- `_producer` identity
- Required and optional fields
- Compatibility, migration, and removal policy
- Security classification and retention behavior
- Projection rules and API exposure

Organizational domains, UI layout, saved views, impact review state, and runtime interaction observations may remain platform metadata rather than OpenLineage facets when they do not describe a job, run, or dataset.

### 8.3 Naming and Identity

- Dataset namespaces identify their data source using published OpenLineage conventions where available.
- Dataset names remain stable within a namespace and preserve source-qualified structure.
- Job namespaces identify the scheduler, platform, or integration context.
- Job names remain unique within a namespace.
- Run IDs are supplied by the producer and retained across lifecycle events for the same run.
- Environment is represented consistently through supported facets or governed platform metadata; it is not appended inconsistently to display names.
- Alias and rename records do not merge assets without evidence or administrative review.

### 8.4 Event Processing

1. Authenticate and authorize the producer.
2. Apply payload-size, rate, and transport controls.
3. Validate the declared OpenLineage schema and registered custom facets.
4. Stamp immutable receipt metadata.
5. Store the accepted raw event before projection acknowledgement.
6. Compute a stable event fingerprint for idempotency.
7. Publish the event to projection processing.
8. Update entity, facet, lifecycle, and lineage materializations.
9. Update search and quality indices.
10. Emit success, lag, rejection, and conflict telemetry.

## 9. Logical Architecture and Data Model

### 9.1 Major Components

- **Ingestion gateway:** HTTP and Kafka entry points, authentication, quotas, validation, and acknowledgements.
- **Raw event store:** Immutable accepted OpenLineage payloads and transport metadata.
- **Schema registry:** Supported OpenLineage and governed custom-facet schemas.
- **Projection pipeline:** Idempotent processing that materializes entities, facets, runs, edges, versions, and evidence.
- **Lineage graph:** Query-optimized, version-aware representation of jobs, runs, datasets, fields, and relationships.
- **Interaction store:** Separate service call and contract observations.
- **Search index:** Qualified, permission-aware discovery across assets and fields.
- **Impact engine:** Versioned traversal, compatibility rules, severity, confidence, and explanation generation.
- **Policy and governance service:** Ownership, classification, retention, authorization, and extension governance.
- **API and web application:** Search, graph, impact, administration, exports, and collaboration.
- **Observability plane:** Metrics, logs, traces, health, reconciliation, and operator workflows.

### 9.2 Core Entities

| Entity | System of record | Notes |
|---|---|---|
| Job | OpenLineage event history | A recurring process that consumes or produces datasets |
| Run | OpenLineage event history | A time-specific instance of a job with lifecycle state |
| Dataset | OpenLineage event history | Input or output identified by namespace and name |
| Field | Schema and column-lineage facets | Qualified within a dataset and versioned with evidence |
| Lineage relationship | OpenLineage inputs, outputs, and column lineage | Stores source event and projection derivation |
| Service | Service catalog or governed platform metadata | Not automatically equivalent to an OpenLineage job |
| Interaction | Contract or telemetry integration | Stored separately and optionally cross-referenced |
| Domain | Governed platform taxonomy | Organizational grouping that does not alter OpenLineage identity |
| Impact analysis | Throughline | Immutable proposal, graph snapshot, policy, result, and review record |

### 9.3 Evidence and Conflict Rules

- Raw observations are append-only within retention policy.
- Projected current state is reproducible from retained observations and projection code/version.
- Source precedence is configurable by metadata type, not globally assumed.
- Conflicting schemas or ownership claims are preserved and surfaced until policy resolves them.
- Latest event time is not automatically considered most trustworthy when producer priority or run state contradicts it.
- Inferred edges are stored separately from observed edges and never exported as observed OpenLineage events.

## 10. Impact Analysis Model

### 10.1 Inputs

- Baseline dataset and schema version
- Proposed schema or field changes
- Graph snapshot or effective time
- Compatibility policy version
- Scope, depth, domain, environment, and criticality filters
- Optional deployment, ticket, or source-control reference

### 10.2 Severity

| Severity | Meaning | Example |
|---|---|---|
| BREAK | A known contract, compatibility rule, or consumer requirement is violated | Removed required field or incompatible fixed-width export |
| WARN | A consumer is affected but compatibility is uncertain, reviewable, or likely safe | Wider string used in a cast or regenerated derived feature |
| INFO | The path is affected but no action is currently required | Compatible addition propagated to a versioned snapshot |
| UNKNOWN | Metadata is insufficient, stale, or contradictory | Consumer schema or field mapping is unavailable |

### 10.3 Explanation Contract

Each impact finding includes:

- Origin and affected asset identifiers
- Affected field or dataset
- Dependency path and transformation semantics
- Rule or policy that produced severity
- Evidence producer and timestamps
- Graph and schema versions
- Confidence and metadata-quality warnings
- Accountable owner and review status

### 10.4 Reference Acceptance Scenario

The prototype scenario is retained as an end-to-end acceptance test: a proposed change to `customer_raw.email` from `string` to `varchar(320)` must identify direct and derived consumers, distinguish a fixed-width partner export as breaking, identify analytical transformations as warnings where appropriate, display service-level blast radius first, and provide dataset and field-level evidence on drill-down. Test data must use synthetic metadata and must not depend on production customer information.

## 11. Integrations

### 11.1 Required Integration Categories

- Generic OpenLineage HTTP producer
- OpenLineage Kafka transport
- Workflow orchestration and data-processing integrations that emit OpenLineage
- Spark and dbt OpenLineage integrations
- Kafka and schema registry metadata
- S3 and file/object metadata
- Warehouse and lakehouse datasets through OpenLineage-producing integrations
- Service catalog ownership and domain metadata
- OpenAPI, GraphQL schema, and gRPC descriptor sources for Interactions
- Distributed tracing or service telemetry sources for observed interactions
- Identity provider, SCIM, ticketing, chat, and notification systems

### 11.2 Connector Contract

Every connector must publish a support matrix, required permissions, data collected, event or polling semantics, expected freshness, rate limits, secret handling, failure behavior, and removal procedure. Connectors must expose health, last success, lag, throughput, rejection count, and version. A connector may not silently downgrade field-level evidence to dataset-level certainty.

## 12. APIs and Exports

### 12.1 Ingestion APIs

- OpenLineage-compatible event endpoint
- Producer authentication and scoped credentials
- Synchronous validation response with durable-acceptance semantics
- Batch and compression support subject to size limits
- Idempotency and correlation identifiers
- Rate-limit and retry guidance

### 12.2 Query APIs

- Asset search and autocomplete
- Qualified asset detail and facet history
- Upstream/downstream traversal with depth, time, and filter controls
- Run history and lifecycle events
- Field-level lineage and evidence
- Interaction matrix and contract detail
- Impact create, status, results, compare, review, and export
- Connector health and graph-quality administration

### 12.3 Exports

- Valid OpenLineage event export for lineage interoperability
- Human-readable impact report
- Machine-readable impact result with policy and evidence versions
- Permission-filtered CSV or JSON for approved administrative uses
- Stable deep links for UI collaboration

## 13. Security, Privacy, and Governance

| ID | Requirement | Acceptance criteria |
|---|---|---|
| SEC-001 | Enterprise authentication | OIDC or SAML SSO is required; local production passwords are disabled by default |
| SEC-002 | Provisioning | SCIM or equivalent lifecycle integration supports timely grant and revocation |
| SEC-003 | Authorization | RBAC supports platform, domain, connector, impact-review, and read-only roles; sensitive metadata can add attribute-based restrictions |
| SEC-004 | Least privilege | Producers can submit only to authorized namespaces or environments and cannot query metadata unless separately authorized |
| SEC-005 | Encryption | Data is encrypted in transit and at rest using organization-approved controls |
| SEC-006 | Secret management | Connector and transport secrets use an approved secret store, rotation, and access audit |
| SEC-007 | Audit | Authentication, administration, access to restricted metadata, exports, reviews, and policy changes are immutable and queryable |
| SEC-008 | Metadata minimization | Raw data values are not collected for lineage; SQL, payload examples, and error details are configurable and redactable |
| SEC-009 | Sensitive metadata | Classifications and restricted names are permission-filtered in UI, APIs, search, notifications, and exports |
| SEC-010 | Retention | Raw events, projections, audits, and exports have explicit, configurable retention and legal-hold behavior |
| SEC-011 | Tenant/environment isolation | Data and credentials cannot cross configured organizational or environment boundaries |
| SEC-012 | Security operations | Vulnerability management, dependency scanning, incident response, backup, and recovery procedures are documented and tested |

## 14. Non-Functional Requirements

Initial targets are production design objectives and must be validated with representative load tests before launch.

| Category | Requirement |
|---|---|
| Availability | User-facing query and impact services target 99.9% monthly availability excluding approved maintenance |
| Durability | An acknowledged accepted event is stored durably before asynchronous projection |
| Ingestion latency | Under qualified normal load, 95% of accepted events are searchable and traversable within 60 seconds |
| Search performance | Permission-filtered search returns within 2 seconds at p95 under qualified load |
| Traversal performance | A bounded one-hop neighborhood returns within 2 seconds at p95; larger traversals stream or paginate |
| Impact performance | A qualified analysis over up to 50,000 visited graph elements completes within 30 seconds at p95 or runs asynchronously with progress |
| Scale baseline | Validate at 5 million assets, 100 million projected relationships, 1 billion retained observations, and 10,000 events/second burst ingestion |
| Backpressure | Ingestion protects durability and reports throttling; it does not drop accepted events silently |
| Recovery | Target recovery point of 15 minutes and recovery time of 4 hours for the production metadata plane |
| Consistency | Query responses expose projection watermark and graph version so users can identify lag |
| Observability | Each component emits metrics, structured logs, traces, health, saturation, lag, error, and dependency signals |
| Accessibility | Core workflows meet WCAG 2.2 AA objectives and include non-graph tabular alternatives |
| Browser support | Support current enterprise-approved evergreen browsers with a published matrix |
| Localization | Initial release is English; timestamps, time zones, and number formatting are unambiguous and API-stable |
| Maintainability | Projection rebuild, schema migration, connector upgrade, and rollback procedures are automated and tested |

## 15. Data Quality and Trust

The platform must measure its own metadata quality. At minimum it will report:

- Critical asset coverage by environment and domain
- Dataset and field schema coverage
- Dataset-level and column-level lineage coverage
- Ownership and classification coverage
- Freshness distribution and assets outside source-specific SLA
- Orphan assets and disconnected critical systems
- Conflicting facets and identity collisions
- Invalid and rejected OpenLineage events by producer and reason
- Inferred versus observed edge counts
- Impact analyses containing unknown results
- Reconciliation differences between source inventory and graph inventory

Quality scores may summarize these signals but must not hide the underlying measures or imply certainty that the evidence does not support.

## 16. Analytics and Success Metrics

### 16.1 Adoption

- Monthly active users by persona and domain
- Search-to-lineage and lineage-to-impact conversion
- Saved/shared views and impact review participation
- API consumers and recurring integrations

### 16.2 Coverage and Reliability

- At least 80% of designated Tier 1 datasets have fresh dataset-level lineage before broad rollout.
- At least 60% of designated Tier 1 transformation outputs have usable field-level lineage before field-level impact is presented as complete.
- At least 95% of accepted events are projected within the freshness objective under normal load.
- Connector success and replay rates meet connector-specific objectives.

### 16.3 Outcome Metrics

- Median time to complete a change-impact review
- Median time to identify the owner and dependency path during an incident
- Percentage of reviewed changes with all breaking findings acknowledged
- Confirmed production incidents caused by previously unidentified data dependencies
- Prevented or corrected releases attributable to Throughline findings
- Sampled precision and recall of impact results against expert-reviewed ground truth

Target values for incident reduction and analysis accuracy will be baselined during pilot rather than asserted without evidence.

## 17. Rollout Plan and Gates

### Phase 0: Foundation and Governance

- Approve OpenLineage naming, producer identity, schema compatibility, custom-facet, retention, and security policies.
- Deploy ingestion gateway, raw event store, schema validation, and operator telemetry.
- Onboard synthetic producers and validate replay, rebuild, and isolation.

**Gate:** Security review complete; accepted events are durable, replayable, and traceable to producers.

### Phase 1: Trusted Lineage

- Onboard priority OpenLineage producers and integrations.
- Deliver search, asset pages, domain overlay, service/job views, dataset lineage, and evidence inspection.
- Establish coverage, freshness, conflict, and reconciliation dashboards.

**Gate:** Tier 1 dataset-level coverage and freshness thresholds are met for pilot domains.

### Phase 2: Element-Level Lineage and Impact

- Enable schema and column-lineage facets for qualified sources.
- Deliver proposed-change input, versioned impact engine, severity rules, unknown-state handling, and review exports.
- Validate the reference scenario and domain-specific compatibility policies.

**Gate:** Expert evaluation meets agreed precision/recall threshold; every finding is explainable and permission-filtered.

### Phase 3: Interactions and Collaboration

- Add service-contract and telemetry integrations.
- Deliver the interaction matrix, explicit cross-references, notifications, ticketing, comments, and approval workflows.

**Gate:** Service interaction data remains semantically and physically distinct from OpenLineage projections.

### Phase 4: Enterprise Scale and Optimization

- Expand connectors, environments, domains, historical analysis, APIs, and executive reporting.
- Complete scale, recovery, chaos, security, and accessibility validation.

**Gate:** Production objectives and operational runbooks pass launch review.

## 18. Launch Criteria

The platform may enter general production only when:

- OpenLineage validation, storage, projection, export, and replay pass compatibility testing.
- Security architecture, threat model, access controls, audit, secrets, retention, and recovery are approved.
- Critical pilot sources meet agreed coverage and freshness thresholds.
- Impact findings are explainable, uncertainty is visible, and sampled accuracy meets the pilot gate.
- Search, traversal, impact, ingestion, and recovery objectives pass representative tests.
- Operators have dashboards, alerts, runbooks, escalation paths, and tested rebuild procedures.
- Core workflows pass accessibility review and include tabular alternatives to graph-only information.
- Product, engineering, architecture, security, governance, and pilot-domain owners sign off.

## 19. Dependencies and Ownership

| Dependency | Required owner |
|---|---|
| OpenLineage naming and producer standards | Enterprise architecture and data platform |
| Source instrumentation and integration upgrades | Source system and platform teams |
| Domain, owner, criticality, and classification taxonomy | Governance and business data owners |
| Identity, SSO, SCIM, and role mapping | Identity and security teams |
| Contract and trace integrations | Application platform and observability teams |
| Compatibility rules and change policies | Architecture, data platform, and domain owners |
| Infrastructure, SLOs, backup, and recovery | Platform engineering and SRE |
| Adoption, training, and workflow integration | Product and change-management leads |

## 20. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Inconsistent namespace and naming conventions | Duplicate or disconnected assets | Enforce producer policy, validation, compatibility tests, aliases, and reviewed reconciliation |
| Sparse field-level lineage | False confidence in impact results | Show coverage and `UNKNOWN`; gate completeness claims by source capability |
| Stale metadata | Incorrect blast radius | Source-specific freshness SLAs, watermarks, warnings, and analysis-time checks |
| Overuse of custom facets | Reduced interoperability | Standard-first review, central schema registry, ownership, and deprecation policy |
| Service calls confused with lineage | Misleading graph and impact | Separate stores and UI workspaces; require explicit cross-reference rules |
| Sensitive metadata leakage | Security or compliance incident | Metadata minimization, redaction, permission-aware search, export controls, and auditing |
| Graph scale or high-degree nodes | Slow or unusable navigation | Progressive disclosure, bounded traversal, pagination, aggregation, and asynchronous analysis |
| Conflicting source evidence | Unstable current state | Preserve observations, expose conflicts, apply governed precedence by metadata type |
| Connector failure or source upgrades | Coverage and freshness degradation | Version matrix, health telemetry, canary upgrades, dead-letter handling, and replay |
| Impact false positives | Review fatigue | Explainable rules, policy tuning, feedback capture, and sampled accuracy measurement |
| Impact false negatives | Production breakage | Explicit unknowns, coverage gates, conservative propagation, and expert validation |

## 21. Open Decisions

The following decisions are required before detailed implementation commitments:

1. Deployment model: managed service, customer cloud, private network, or supported combination.
2. Initial production domains, Tier 1 asset inventory, and source-of-truth owners.
3. Qualified OpenLineage schema and client versions for the launch compatibility matrix.
4. Default retention for raw events, historical projections, impact records, and audit logs.
5. Graph, event, search, and analytical storage technologies after benchmark validation.
6. Initial machine-readable schema formats accepted by impact analysis.
7. Domain-specific compatibility rules and the authority allowed to override severity.
8. Runtime interaction evidence sources and required observation freshness.
9. Exact SLOs, data residency requirements, and recovery tiers by deployment model.
10. Product naming, branding, licensing, and support model.

## 22. Source References

- [OpenLineage overview and core model](https://openlineage.io/docs)
- [OpenLineage object model](https://openlineage.io/docs/spec/object-model/)
- [OpenLineage naming conventions](https://openlineage.io/docs/spec/naming)
- [OpenLineage facets and extensibility](https://openlineage.io/docs/spec/facets/)
- [OpenLineage column-level lineage facet](https://openlineage.io/docs/spec/facets/dataset-facets/column_lineage_facet/)
- [OpenLineage API](https://openlineage.io/apidocs/openapi/)
- Data Lineage Impact Platform prototype archive supplied for this requirement

## Appendix A: Requirement Traceability Summary

| Requirement area | Primary sections | Launch evidence |
|---|---|---|
| OpenLineage interoperability | 8, 9, 11, 12 | Compatibility suite, valid event export, replay test |
| Lineage navigation | 5, 6, 7 | End-to-end domain-to-field workflow tests |
| Runtime interactions | 5, 6, 7 | Store separation test and matrix workflow tests |
| Impact analysis | 5, 6, 7, 10 | Reference scenario, sampled accuracy, immutable report |
| Security and governance | 13, 15 | Security review, access tests, audit and retention evidence |
| Production readiness | 14, 17, 18 | Load, availability, recovery, accessibility, and runbook reviews |

## Appendix B: Definition of Done for a Supported Source

A source is considered supported only when:

1. Its identity and namespace rules are documented and tested.
2. Its OpenLineage or connector version is in the compatibility matrix.
3. Required permissions and collected metadata are documented.
4. Events validate and preserve producer and schema evidence.
5. Dataset and field coverage behavior is measured, including known limitations.
6. Freshness objectives, health metrics, alerts, and replay procedures exist.
7. Sensitive metadata behavior and retention are approved.
8. Upgrade, rollback, and decommission procedures are tested.
