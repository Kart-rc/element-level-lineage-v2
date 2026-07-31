# Ontology on Snowflake: How to Make AI Actually Understand Your Data

> **Provenance.** Summary of the Snowflake Summit 2026 presentation "Ontology on Snowflake —
> unifying data, making semantics scale, and grounding AI reasoning" (principal AI architect,
> Snowflake). Recording: <https://www.youtube.com/watch?v=Ooan6cErKCM>. Supplied as input to
> [deliverables/snowflake-ontology-lineage-assessment.md](../deliverables/snowflake-ontology-lineage-assessment.md)
> on 2026-07-31.

## Overview
In the AI era, companies do not compete merely on who stores more data; they compete on who understands how their business actually works. Currently, AI agents often provide confident but incorrect answers. This happens because "meaning" is missing. Facts live in databases, while definitions and business logic live in people's heads or scattered documentation.

This summary explores how to fix this by making meaning explicit, scalable, and usable without leaving Snowflake through an **Ontology-Driven Architecture**.

---

## The Core Problem
* **What we store today:** Raw tables, foreign keys, and encrypted column names.
* **The Reality:** The real world operates through objects, people, teams, and contracts that relate to each other in specific ways (e.g., a "person" works for a "team", bound by a "contract").
* **The Gap:** Feeding raw schemas to AI expects the system to infer reality. This leads to brutal SQL, duplicated logic, and AI hallucinations.
* **The Goal:** Move from simply joining rows to reasoning over concepts.

---

## Ontology vs. Knowledge Graph
People often use these terms interchangeably, but they serve different distinct purposes:

| Concept | Description | Example | Change Frequency |
| :--- | :--- | :--- | :--- |
| **Ontology** | The **Blueprint**. It defines abstracted rules: what is allowed to exist and how things can relate. | *A person can work for an organization. A player is a type of person.* | Evolves slowly and intentionally. |
| **Knowledge Graph** | The **Building**. Concrete facts and instances materialized from the blueprint. | *Kylian Mbappé (player) plays for Real Madrid (organization).* | Changes frequently (e.g., every transfer window). |

**Key Rule:** Keep them separate. The ontology defines what relationships are allowed, and the knowledge graph materializes which ones actually exist.

---

## The 5-Layer Architecture Native to Snowflake
To effectively build this out, Snowflake uses a 5-layer architecture.
**Mantra:** *"Store facts once, define meanings as configurations, and let intelligence orchestrate dynamically."*

### 1. Foundation: Physical Storage
Radically simple storage consisting of just two tables:
* **Nodes Table:** Stores everything that exists.
* **Edges Table:** Stores every connection between things.
*(Uses variant columns for flexible properties. Adding a new entity type means inserting a node, not rewriting a schema!)*

### 2. Meaning: Ontology Metadata
Pure configuration layer. This is where business meaning is declared (classes, hierarchies, relationships). It operates like Object-Oriented Programming for your data (e.g., declaring that a `player` and a `coach` are both types of a `person`).

### 3. Generation: Compiled Views
A compiler reads the layer 2 metadata and automatically generates views. If you add a new subtype, you just rerun the compiler and the semantic views expand automatically with zero downstream code changes.

### 4. Semantic Lenses: Purpose-Built Models
One gigantic view cannot answer all queries efficiently. Instead, three distinct models sit on top of the same ontology:
* **Knowledge Graph Model:** Fast, concrete, and attribute-rich. Optimized for specific operational queries (e.g., *"Who plays for Real Madrid?"*).
* **Ontology Model:** Abstract and polymorphic. Built for AI reasoning across type boundaries (e.g., *"Who works for Real Madrid?"* returns both players and coaches).
* **Governance Model:** The system describing itself. Defines what types exist, what relationships are defined, and access controls.

### 5. The Brain: Cortex Agent
The AI agent doesn't act as a monolithic entity. Instead, it acts as a conductor leading an orchestra. It parses natural language to understand the intent, picks the right tool (or multiple tools in parallel), and merges the results into one grounded, coherent answer.

---

## Automation: The Ontology Stack Builder
Building this manually would take weeks of handwritten SQL. Snowflake introduces the **Ontology Stack Builder** (a Cortex skill):
1. Give it your tables and business questions.
2. It introspects the schema and proposes an ontology.
3. Provides a visual graph editor to drag nodes and draw relationships.
4. Once approved, it generates all SQL, deploys layers 1-3, creates semantic views, and wires up the Cortex Agent.
*What used to take months can now be done in an hour.*

---

## Key Takeaways
1. **Make Meaning Explicit:** Store facts once, define meaning as metadata, and let the system generate the rest.
2. **Use Purpose-Built Lenses:** Concrete knowledge graphs for speed, abstract ontologies for reasoning, and governance for trust.
3. **Intent-Driven Routing:** Let the AI agent orchestrate specialized tools dynamically instead of relying on hard-coded paths.

Data gives you facts. Ontology gives you meaning. The agent gives you intelligence. Together, they create one unified system native to Snowflake that actually understands your business.

---

## Additional implementation detail from the full talk

Points from the recording that go beyond the summary above, retained because the assessment cites them:

- **Layer 1** is exactly two tables (`nodes`, `edges`) with VARIANT property columns. Adding an entity type is an insert, never a schema migration ("the schema never changes; facts are stable; meaning evolves above").
- **Layer 2** is pure declarative configuration: class hierarchy (`player is-a person`, `coach is-a person`) plus relationship constraints ("only a player can `play_for` a club"). Evolving the model is one metadata insert.
- **Layer 3** is a compiler stored procedure (`generate_ontology_view`) that reads layer-2 metadata and generates polymorphic union views (e.g. `ontology_person` = players ∪ coaches). Adding a subtype and rerunning the compiler expands every dependent view with zero downstream query changes.
- **Layer 4** exists because "one gigantic semantic view didn't work": concrete operational questions and abstract polymorphic questions have fundamentally different query shapes. The knowledge-graph model supports multi-hop SQL traversal directly over the node/edge tables.
- **Layer 5** routes by intent: specific-instance questions → knowledge-graph model; abstract questions → ontology model; "what types exist / who has access" → governance model; "shortest path between two entities" → graph analytics tooling; multiple tools may run in parallel and merge.
- The **Ontology Stack Builder** is a seven-phase, gated, human-in-the-loop workflow: schema introspection → proposed ontology → visual graph editing → approval → SQL generation → deployment of layers 1–3 + semantic views → Cortex Agent wiring and end-to-end validation.
