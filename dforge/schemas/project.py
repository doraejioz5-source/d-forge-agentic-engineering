from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class Requirement(BaseModel):
    id: str = Field(description="Stable ID such as REQ-001")
    category: Literal["functional", "non_functional", "constraint"]
    description: str
    rationale: str = ""
    verification_hint: str = ""


class RequirementOutput(BaseModel):
    needs_clarification: bool = False
    clarification_questions: list[str] = Field(default_factory=list)
    requirements: list[Requirement] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class Module(BaseModel):
    id: str = Field(description="Stable ID such as MOD-001")
    name: str
    purpose: str
    related_requirements: list[str] = Field(default_factory=list)
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)


class ArchitectureOutput(BaseModel):
    modules: list[Module] = Field(default_factory=list)
    interfaces: list[str] = Field(default_factory=list)
    design_notes: list[str] = Field(default_factory=list)


class TestCase(BaseModel):
    id: str = Field(description="Stable ID such as TEST-001")
    requirement_ids: list[str] = Field(default_factory=list)
    objective: str
    method: str
    pass_criteria: str


class VerificationOutput(BaseModel):
    tests: list[TestCase] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class FailureIssue(BaseModel):
    issue_id: str = Field(description="Stable ID such as ISSUE-001")
    test_id: str = ""
    symptom: str
    observed_condition: str = ""
    engineer_note: str = ""


class FailureAnalysisOutput(BaseModel):
    issue: FailureIssue
    related_requirements: list[str] = Field(default_factory=list)
    related_modules: list[str] = Field(default_factory=list)
    related_tests: list[str] = Field(default_factory=list)
    investigation_candidates: list[str] = Field(default_factory=list)
    evidence_to_check: list[str] = Field(default_factory=list)
    uncertainty_note: str = ""


class ImpactItem(BaseModel):
    target_type: Literal["requirement", "module", "test", "document", "interface"]
    target_id: str
    reason: str


class ChangeImpactOutput(BaseModel):
    issue_id: str
    impacted_items: list[ImpactItem] = Field(default_factory=list)
    review_scope: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class RetestCandidate(BaseModel):
    test_id: str
    reason: str
    priority: Literal["high", "medium", "low"] = "medium"


class RetestOutput(BaseModel):
    issue_id: str
    candidates: list[RetestCandidate] = Field(default_factory=list)
    prerequisite_checks: list[str] = Field(default_factory=list)
    decision_note: str = ""


class ReviewOutput(BaseModel):
    summary: str
    issues: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)


class DevelopmentPhase(BaseModel):
    phase: str
    goal: str
    outputs: list[str] = Field(default_factory=list)


class DevelopmentPlanOutput(BaseModel):
    phases: list[DevelopmentPhase] = Field(default_factory=list)
    key_dependencies: list[str] = Field(default_factory=list)
    key_risks: list[str] = Field(default_factory=list)


class TraceabilityResult(BaseModel):
    requirement_ids: list[str] = Field(default_factory=list)
    mapped_to_module: list[str] = Field(default_factory=list)
    mapped_to_test: list[str] = Field(default_factory=list)
    missing_module_mapping: list[str] = Field(default_factory=list)
    missing_test_mapping: list[str] = Field(default_factory=list)

    @property
    def coverage_ok(self) -> bool:
        return not self.missing_module_mapping and not self.missing_test_mapping


class RouteDecision(BaseModel):
    action: Literal[
        "requirements",
        "architecture",
        "verification",
        "failure_analysis",
        "impact_analysis",
        "retest",
        "review",
        "planning",
        "run_all",
        "status",
        "question",
    ]
    reason: str = ""


class AdvisorOutput(BaseModel):
    answer: str
    suggested_next_action: Literal[
        "requirements",
        "architecture",
        "verification",
        "failure_analysis",
        "impact_analysis",
        "retest",
        "review",
        "planning",
        "run_all",
        "none",
    ] = "none"


class ProjectState(BaseModel):
    project_goal: str
    requirements: RequirementOutput | None = None
    architecture: ArchitectureOutput | None = None
    verification: VerificationOutput | None = None
    traceability: TraceabilityResult | None = None
    failure_analysis: FailureAnalysisOutput | None = None
    impact_analysis: ChangeImpactOutput | None = None
    retest_plan: RetestOutput | None = None
    review: ReviewOutput | None = None
    development_plan: DevelopmentPlanOutput | None = None
