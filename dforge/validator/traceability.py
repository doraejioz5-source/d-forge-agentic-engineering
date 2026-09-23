from dforge.schemas import ArchitectureOutput, RequirementOutput, TraceabilityResult, VerificationOutput


def check_traceability(
    requirements: RequirementOutput,
    architecture: ArchitectureOutput,
    verification: VerificationOutput,
) -> TraceabilityResult:
    req_ids = [r.id for r in requirements.requirements]

    module_refs = {
        req_id
        for module in architecture.modules
        for req_id in module.related_requirements
    }
    test_refs = {
        req_id
        for test in verification.tests
        for req_id in test.requirement_ids
    }

    mapped_to_module = [rid for rid in req_ids if rid in module_refs]
    mapped_to_test = [rid for rid in req_ids if rid in test_refs]

    return TraceabilityResult(
        requirement_ids=req_ids,
        mapped_to_module=mapped_to_module,
        mapped_to_test=mapped_to_test,
        missing_module_mapping=[rid for rid in req_ids if rid not in module_refs],
        missing_test_mapping=[rid for rid in req_ids if rid not in test_refs],
    )
