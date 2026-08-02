import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRD_ROOT = ROOT / "docs" / "component-prds"

EXPECTED_COMPONENTS = {
    "C01": "01-canonical-contracts-and-identity.md",
    "C02": "02-source-adapters-and-inventory.md",
    "C03": "03-event-intake-and-queues.md",
    "C04": "04-eligibility-and-substrate-routing.md",
    "C05": "05-context-dependency-and-determinants.md",
    "C06": "06-orchestration-and-scheduling.md",
    "C07": "07-lane-b-native-collectors.md",
    "C08": "08-lane-a-deterministic-analyzers.md",
    "C09": "09-lane-a-agentic-resolver.md",
    "C10": "10-lane-c-opaque-collector.md",
    "C11": "11-runtime-session-and-sidecar.md",
    "C12": "12-evidence-store-and-cache.md",
    "C13": "13-reconciliation-verification-confidence.md",
    "C14": "14-ci-artifact-binding-and-freshness.md",
    "C15": "15-proposal-review-and-corpus.md",
    "C16": "16-publication-and-projections.md",
    "C17": "17-query-api-review-ui-and-timeline.md",
    "C18": "18-security-observability-operations-dr.md",
}

EXPECTED_SHARED = {
    "00-system-context-and-architecture.md",
    "shared/contract-catalog.md",
    "shared/state-and-error-model.md",
    "shared/dependency-and-integration-matrix.md",
    "shared/test-strategy-and-fixtures.md",
    "shared/end-to-end-acceptance-tests.md",
    "shared/requirements-traceability-matrix.md",
    "shared/implementation-sequence.md",
    "shared/coding-agent-handoff.md",
}

REQUIRED_COMPONENT_HEADINGS = {
    "## 1. Document Control",
    "## 2. Purpose and Outcomes",
    "## 3. Scope and Non-Goals",
    "## 4. Actors and Use Cases",
    "## 5. Component Boundary",
    "## 6. Functional Requirements",
    "## 7. Data and Durable State",
    "## 8. Interfaces and Contracts",
    "## 9. Processing and State Model",
    "## 10. Failure Semantics",
    "## 11. Security and Privacy",
    "## 12. Scale, Performance, and Availability",
    "## 13. Observability",
    "## 14. Acceptance Criteria",
    "## 15. Component Test Matrix",
    "## 16. Integration Obligations",
    "## 17. Definition of Done",
    "## 18. Implementation Notes",
    "## 19. Traceability",
}

ID_RE = re.compile(
    r"\b(?:C\d{2}-(?:FR|NFR|SEC|OBS|AC|CT)-\d{3}|INT-\d{3}|E2E-\d{3})\b"
)
DEFINITION_RE = re.compile(
    r"^\|\s*((?:C\d{2}-(?:FR|NFR|SEC|OBS|AC|CT)-\d{3}|INT-\d{3}|E2E-\d{3}))\s*\|",
    re.MULTILINE,
)
P0_RE = re.compile(
    r"^\|\s*(C\d{2}-(?:FR|NFR|SEC|OBS)-\d{3})\s*\|.*\|\s*P0\s*\|\s*$",
    re.MULTILINE,
)
PLACEHOLDER_RE = re.compile(r"\b(?:TBD|TODO|FIXME)\b", re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class PackageIndexTests(unittest.TestCase):
    def test_readme_metadata_and_component_inventory(self):
        path = PRD_ROOT / "README.md"
        self.assertTrue(path.exists(), "component PRD package README is missing")
        source = read(path)
        self.assertIn("# AWS Lineage Collection Component PRDs", source)
        self.assertIn("Authoritative Sources", source)
        self.assertIn("How to Use This Package", source)
        self.assertIn("Package Completion Rule", source)
        for component_id in EXPECTED_COMPONENTS:
            self.assertIn(component_id, source)

    def test_readme_relative_links_resolve(self):
        path = PRD_ROOT / "README.md"
        self.assertTrue(path.exists())
        missing = []
        for target in LINK_RE.findall(read(path)):
            if target.startswith(("http://", "https://", "#")):
                continue
            clean_target = target.split("#", 1)[0]
            if clean_target and not (path.parent / clean_target).resolve().exists():
                missing.append(target)
        self.assertEqual(missing, [], f"README contains unresolved links: {missing}")


class PackageCompletenessTests(unittest.TestCase):
    def test_expected_files_exist(self):
        expected = {"README.md"} | set(EXPECTED_COMPONENTS.values()) | EXPECTED_SHARED
        missing = sorted(str(path) for path in expected if not (PRD_ROOT / path).exists())
        self.assertEqual(missing, [], f"missing PRD package files: {missing}")

    def test_component_prds_have_required_sections(self):
        for component_id, relative_path in EXPECTED_COMPONENTS.items():
            with self.subTest(component=component_id):
                path = PRD_ROOT / relative_path
                self.assertTrue(path.exists(), f"{component_id} PRD is missing")
                source = read(path)
                self.assertRegex(source.splitlines()[0], rf"^# {component_id}\b")
                missing = sorted(REQUIRED_COMPONENT_HEADINGS - set(source.splitlines()))
                self.assertEqual(missing, [], f"{component_id} missing sections: {missing}")
                self.assertGreaterEqual(
                    len(re.findall(rf"\b{component_id}-FR-\d{{3}}\b", source)),
                    4,
                    f"{component_id} must define at least four functional requirements",
                )
                self.assertGreaterEqual(
                    len(re.findall(rf"\b{component_id}-CT-\d{{3}}\b", source)),
                    5,
                    f"{component_id} must define at least five component tests",
                )

    def test_package_has_no_unresolved_placeholders(self):
        if not PRD_ROOT.exists():
            self.fail("component PRD package is missing")
        findings = []
        for path in sorted(PRD_ROOT.rglob("*.md")):
            for match in PLACEHOLDER_RE.finditer(read(path)):
                line = read(path).count("\n", 0, match.start()) + 1
                findings.append(f"{path.relative_to(ROOT)}:{line}:{match.group(0)}")
        self.assertEqual(findings, [], f"unresolved placeholders: {findings}")

    def test_definition_ids_are_unique(self):
        if not PRD_ROOT.exists():
            self.fail("component PRD package is missing")
        definitions = {}
        duplicates = []
        for path in sorted(PRD_ROOT.rglob("*.md")):
            for identifier in DEFINITION_RE.findall(read(path)):
                if identifier in definitions:
                    duplicates.append(
                        f"{identifier}: {definitions[identifier]} and {path.relative_to(ROOT)}"
                    )
                else:
                    definitions[identifier] = path.relative_to(ROOT)
        self.assertEqual(duplicates, [], f"duplicate ID definitions: {duplicates}")

    def test_every_p0_requirement_is_in_traceability_matrix(self):
        matrix = PRD_ROOT / "shared" / "requirements-traceability-matrix.md"
        self.assertTrue(matrix.exists(), "traceability matrix is missing")
        matrix_source = read(matrix)
        missing = []
        for component_id, relative_path in EXPECTED_COMPONENTS.items():
            path = PRD_ROOT / relative_path
            self.assertTrue(path.exists(), f"{component_id} PRD is missing")
            for requirement_id in P0_RE.findall(read(path)):
                if requirement_id not in matrix_source:
                    missing.append(requirement_id)
        self.assertEqual(missing, [], f"P0 requirements missing traceability: {missing}")


class SharedSpecificationTests(unittest.TestCase):
    def test_system_context_covers_components_flows_and_invariants(self):
        path = PRD_ROOT / "00-system-context-and-architecture.md"
        self.assertTrue(path.exists(), "system context is missing")
        source = read(path)
        for component_id in EXPECTED_COMPONENTS:
            self.assertIn(component_id, source)
        for token in (
            "Baseline Collection Flow",
            "Incremental Collection Flow",
            "Integration Runtime Evidence Flow",
            "Platform Invariants",
            "EventBridge routes",
            "SQS buffers",
            "Step Functions coordinates",
        ):
            self.assertIn(token, source)

    def test_contract_catalog_names_canonical_artifacts_and_ownership(self):
        path = PRD_ROOT / "shared" / "contract-catalog.md"
        self.assertTrue(path.exists(), "contract catalog is missing")
        source = read(path)
        for artifact in (
            "CanonicalUrn",
            "EventEnvelope",
            "RepositoryInventorySnapshot",
            "RepositoryEligibilityDecision",
            "ApplicationContextSnapshot",
            "DeterminantSet",
            "RuntimeEvidenceSession",
            "LineageProposal",
            "AcceptedLineageManifest",
            "ReviewLabel",
        ):
            self.assertIn(artifact, source)
        self.assertIn("Producer", source)
        self.assertIn("Consumers", source)
        self.assertIn("Compatibility", source)

    def test_state_and_error_model_is_normative(self):
        path = PRD_ROOT / "shared" / "state-and-error-model.md"
        self.assertTrue(path.exists(), "state and error model is missing")
        source = read(path)
        for error_class in (
            "TRANSIENT",
            "DETERMINISTIC_INVALID",
            "INCOMPLETE",
            "CONFLICT",
            "POISON_REPEATED",
        ):
            self.assertIn(error_class, source)
        for behavior in ("retry", "quarantine", "DLQ", "redrive", "replay", "audit"):
            self.assertIn(behavior, source)


class ComponentSpecificTests(unittest.TestCase):
    def test_c01_identity_spec_is_implementation_ready(self):
        path = PRD_ROOT / EXPECTED_COMPONENTS["C01"]
        self.assertTrue(path.exists(), "C01 PRD is missing")
        source = read(path)
        for token in (
            "Canonical URN Grammar",
            "Resolution Precedence",
            "AMBIGUOUS_IDENTITY",
            "environment",
            "effective version",
            "C01-CT-",
            "INT-",
        ):
            self.assertIn(token, source)

    def test_c02_inventory_spec_is_implementation_ready(self):
        path = PRD_ROOT / EXPECTED_COMPONENTS["C02"]
        self.assertTrue(path.exists(), "C02 PRD is missing")
        source = read(path)
        for token in (
            "RepositoryInventorySnapshot",
            "Test Automation Service",
            "source watermark",
            "PARTIAL",
            "10,000 repositories",
            "C02-CT-",
            "INT-",
        ):
            self.assertIn(token, source)

    def test_c03_intake_spec_is_implementation_ready(self):
        path = PRD_ROOT / EXPECTED_COMPONENTS["C03"]
        self.assertTrue(path.exists(), "C03 PRD is missing")
        source = read(path)
        for token in (
            "EventEnvelope",
            "idempotency",
            "coalescing",
            "EventBridge archive",
            "priority",
            "DLQ",
            "C03-CT-",
            "INT-",
        ):
            self.assertIn(token, source)

    def test_c04_eligibility_spec_is_implementation_ready(self):
        path = PRD_ROOT / EXPECTED_COMPONENTS["C04"]
        self.assertTrue(path.exists(), "C04 PRD is missing")
        source = read(path)
        for token in (
            "APPLICATION_RUNTIME",
            "MIXED_MONOREPO",
            "UNKNOWN",
            "Lane A",
            "Lane B",
            "Lane C",
            "override",
            "C04-CT-",
            "INT-",
        ):
            self.assertIn(token, source)

    def test_c05_context_and_determinants_spec_is_implementation_ready(self):
        path = PRD_ROOT / EXPECTED_COMPONENTS["C05"]
        self.assertTrue(path.exists(), "C05 PRD is missing")
        source = read(path)
        for token in (
            "ApplicationContextSnapshot",
            "DependencyRecord",
            "DeterminantSet",
            "configuration key",
            "shared library",
            "full-scan divergence",
            "C05-CT-",
            "INT-",
        ):
            self.assertIn(token, source)

    def test_c06_orchestration_spec_is_implementation_ready(self):
        path = PRD_ROOT / EXPECTED_COMPONENTS["C06"]
        self.assertTrue(path.exists(), "C06 PRD is missing")
        source = read(path)
        for token in (
            "Step Functions Standard",
            "baseline workflow",
            "incremental workflow",
            "runtime workflow",
            "finally",
            "priority fairness",
            "redrive",
            "C06-CT-",
            "INT-",
        ):
            self.assertIn(token, source)

    def test_c07_lane_b_spec_is_implementation_ready(self):
        path = PRD_ROOT / EXPECTED_COMPONENTS["C07"]
        self.assertTrue(path.exists(), "C07 PRD is missing")
        source = read(path)
        for token in (
            "Spark OpenLineage",
            "dbt manifest",
            "Airflow",
            "select *",
            "artifact digest",
            "derivational oracle",
            "unresolved",
            "C07-CT-",
            "INT-",
        ):
            self.assertIn(token, source)

    def test_c08_deterministic_analyzer_spec_is_implementation_ready(self):
        path = PRD_ROOT / EXPECTED_COMPONENTS["C08"]
        self.assertTrue(path.exists(), "C08 PRD is missing")
        source = read(path)
        for token in (
            "Spring Boot",
            "FastAPI",
            "provable edges",
            "Hole",
            "holes_opened",
            "byte-identical",
            "DeterminantSet",
            "C08-CT-",
            "INT-",
        ):
            self.assertIn(token, source)

    def test_c09_agentic_resolver_spec_is_implementation_ready(self):
        path = PRD_ROOT / EXPECTED_COMPONENTS["C09"]
        self.assertTrue(path.exists(), "C09 PRD is missing")
        source = read(path)
        for token in (
            "hole-only",
            "search",
            "read_span",
            "resolve_symbol",
            "call_graph",
            "schema_lookup",
            "emit_edge",
            "file:line",
            "content-addressed",
            "Never a guess",
            "C09-CT-",
            "INT-",
        ):
            self.assertIn(token, source)

    def test_c10_opaque_collector_spec_is_implementation_ready(self):
        path = PRD_ROOT / EXPECTED_COMPONENTS["C10"]
        self.assertTrue(path.exists(), "C10 PRD is missing")
        source = read(path)
        for token in (
            "advisory",
            "opaque",
            "fingerprint",
            "minimum observation",
            "low-cardinality",
            "confidence cap",
            "raw values",
            "C10-CT-",
            "INT-",
        ):
            self.assertIn(token, source)

    def test_c11_runtime_session_spec_is_implementation_ready(self):
        path = PRD_ROOT / EXPECTED_COMPONENTS["C11"]
        self.assertTrue(path.exists(), "C11 PRD is missing")
        source = read(path)
        for token in (
            "REQUESTED -> ENABLING -> READY -> COLLECTING -> DRAINING",
            "AppConfig",
            "monotonic sequence",
            "closing manifest",
            "session-scoped keyed HMAC",
            "production hard-deny",
            "finally",
            "C11-CT-",
            "INT-",
        ):
            self.assertIn(token, source)

    def test_c12_evidence_store_spec_is_implementation_ready(self):
        path = PRD_ROOT / EXPECTED_COMPONENTS["C12"]
        self.assertTrue(path.exists(), "C12 PRD is missing")
        source = read(path)
        for token in (
            "S3 Object Lock",
            "content-addressed",
            "SHA-256",
            "immutable",
            "legal hold",
            "cross-Region replication",
            "projection",
            "C12-CT-",
            "INT-",
        ):
            self.assertIn(token, source)

    def test_c13_trust_engine_spec_is_implementation_ready(self):
        path = PRD_ROOT / EXPECTED_COMPONENTS["C13"]
        self.assertTrue(path.exists(), "C13 PRD is missing")
        source = read(path)
        for token in (
            "G1",
            "G2",
            "G3",
            "G4",
            "G5",
            "drop",
            "downgrade",
            "structural confidence",
            "derivational confidence",
            "UNCALIBRATED",
            "C13-CT-",
            "INT-",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
