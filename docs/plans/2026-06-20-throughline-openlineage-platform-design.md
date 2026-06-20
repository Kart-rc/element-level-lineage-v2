# Throughline OpenLineage Platform Design

**Date:** June 20, 2026  
**Status:** Approved  
**Audience:** Mixed executive and technical stakeholders

## Product Intent

Throughline is an enterprise data lineage and impact analysis platform. It gives teams a trustworthy, searchable view of how data elements move and transform across services, APIs, streams, datasets, analytical applications, files, and external transfers. Change owners can simulate schema changes and identify downstream breakages before deployment.

## Product Workspaces

1. **Lineage:** Navigate from enterprise domains to services, jobs, datasets, endpoints, columns, and fields. Trace upstream and downstream dependencies and distinguish batch, stream, file, cache, and transfer channels.
2. **Interactions:** Explore runtime service calls in a caller-to-callee matrix. Inspect REST, GraphQL, gRPC, and asynchronous contracts without mixing request traffic into the data-lineage graph.
3. **Impact:** Propose a schema or field change, calculate its blast radius, classify affected assets, and drill from services to datasets, field diffs, consumers, owners, and remediation evidence.

## OpenLineage Architecture

OpenLineage is the canonical lineage ingestion, exchange, and export format.

- Accept and preserve `RunEvent`, `JobEvent`, and `DatasetEvent` payloads.
- Follow OpenLineage namespace and naming conventions for jobs, runs, and datasets.
- Use standard facets first, including schema, column lineage, ownership, lifecycle, version, source-code, parent, and quality facets.
- Use immutable-schema, namespaced custom facets only for Throughline-specific metadata that the standard does not represent.
- Support HTTP and Kafka transport with validation, idempotency, retry, dead-letter handling, and replay.
- Maintain an immutable raw-event store and build a query-optimized graph projection. The projection is not a competing exchange format.
- Keep runtime service interactions in a separate model and cross-reference them to OpenLineage entities when a relationship exists.

## Production Capabilities

- Connector-based and push-based event ingestion
- Domain-to-field discovery and global search
- Element-level lineage and transformation semantics
- Change-impact simulation and severity classification
- Ownership, governance, privacy, evidence, confidence, and freshness metadata
- Enterprise SSO, scoped RBAC, audit logging, encryption, and retention controls
- Connector health, graph reconciliation, observability, and disaster recovery
- APIs, exports, saved views, deep links, notifications, and collaboration workflows

## Product Principles

- Preserve evidence and provenance for every projected node and edge.
- Make stale, incomplete, inferred, and conflicting lineage visible.
- Separate observed facts from inferred relationships.
- Keep executive summaries connected to field-level technical evidence.
- Prefer OpenLineage standard facets over custom extensions.
- Treat scale, security, auditability, and operability as product requirements.

## Source Standards

- [OpenLineage object model](https://openlineage.io/docs/1.37.0/spec/object-model/)
- [OpenLineage naming conventions](https://openlineage.io/docs/spec/naming)
- [OpenLineage facets and extensibility](https://openlineage.io/docs/spec/facets/)
- [OpenLineage column-level lineage facet](https://openlineage.io/docs/1.42.1/spec/facets/dataset-facets/column_lineage_facet/)
- [OpenLineage API](https://openlineage.io/apidocs/openapi/)

