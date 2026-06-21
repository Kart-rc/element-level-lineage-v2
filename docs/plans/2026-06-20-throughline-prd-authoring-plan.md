# Throughline Production PRD Authoring Plan

> **For Codex:** Create and verify the requested PRD task-by-task using the documents and verification-before-completion skills.

**Goal:** Produce a mixed-audience production PRD for Throughline, with OpenLineage as the canonical lineage format, in Markdown and visually verified DOCX formats.

**Architecture:** Author one canonical Markdown PRD from the approved design and source prototype. Generate a Word document from that content using the `standard_business_brief` preset and `memo_masthead` opening pattern, then render every page for visual inspection.

**Tech Stack:** Markdown, bundled Python 3, `python-docx`, OOXML helpers, LibreOffice rendering, Poppler PNG rendering.

---

### Task 1: Author the Canonical PRD

**Files:**
- Create: `deliverables/Throughline-OpenLineage-Platform-PRD.md`

**Steps:**
1. Write the executive summary, problem, vision, users, jobs, goals, non-goals, assumptions, and product principles.
2. Define Lineage, Interactions, and Impact user journeys and acceptance criteria.
3. Define the OpenLineage event contract, naming, facets, ingestion, graph projection, and extension policy.
4. Add enterprise governance, security, reliability, performance, observability, and accessibility requirements.
5. Add APIs, integrations, data model, success metrics, phased roadmap, dependencies, risks, and open decisions.
6. Audit the PRD against the approved design and prototype evidence.

### Task 2: Build the Word Deliverable

**Files:**
- Create: `scripts/build_prd_docx.py`
- Create: `deliverables/Throughline-OpenLineage-Platform-PRD.docx`

**Steps:**
1. Configure US Letter geometry and the `standard_business_brief` token map.
2. Implement the `memo_masthead` title block, running header, footer, real heading styles, and real list numbering.
3. Render prose, requirement tables, callouts, and roadmap content from the canonical PRD.
4. Apply fixed DXA table geometry, repeating header rows, cell margins, and accessible header markings.
5. Generate the DOCX using the bundled Python runtime.

### Task 3: Verify Content and Layout

**Files:**
- Inspect: `deliverables/Throughline-OpenLineage-Platform-PRD.md`
- Inspect: `deliverables/Throughline-OpenLineage-Platform-PRD.docx`
- Generate internally: `/private/tmp/throughline-prd-render/page-*.png`

**Steps:**
1. Check both deliverables for placeholders, internal tokens, missing required sections, and broken links.
2. Audit DOCX styles, page geometry, numbering, table geometry, headers, and footers.
3. Render the DOCX to PNG using the packaged renderer.
4. Inspect every rendered page at full resolution for clipping, overlap, bad page breaks, and cramped tables.
5. Correct the source or builder and repeat generation and rendering until all pages pass.
6. Run final file, content, and render-count verification before delivery.

