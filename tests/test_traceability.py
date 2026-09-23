from dforge.schemas import (
    ArchitectureOutput,
    Module,
    Requirement,
    RequirementOutput,
    TestCase,
    VerificationOutput,
)
from dforge.validator import check_traceability


def test_traceability_detects_missing_test_mapping():
    requirements = RequirementOutput(
        requirements=[
            Requirement(id="REQ-001", category="functional", description="A"),
            Requirement(id="REQ-002", category="functional", description="B"),
        ]
    )
    architecture = ArchitectureOutput(
        modules=[
            Module(
                id="MOD-001",
                name="Module A",
                purpose="A",
                related_requirements=["REQ-001", "REQ-002"],
            )
        ]
    )
    verification = VerificationOutput(
        tests=[
            TestCase(
                id="TEST-001",
                requirement_ids=["REQ-001"],
                objective="Check A",
                method="Simulation",
                pass_criteria="Expected behavior observed",
            )
        ]
    )

    result = check_traceability(requirements, architecture, verification)

    assert result.missing_module_mapping == []
    assert result.missing_test_mapping == ["REQ-002"]
