from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from dforge.agents import (
    run_planner_agent,
    run_requirement_agent,
    run_reviewer_agent,
    run_system_agent,
    run_verification_agent,
)
from dforge.schemas import ProjectState
from dforge.validator import check_traceability

ProgressCallback = Callable[[str, str], None]


@dataclass
class WorkflowResult:
    state: ProjectState
    stopped_for_clarification: bool = False


def run_dforge(project_goal: str, on_progress: ProgressCallback | None = None) -> WorkflowResult:
    def progress(step: str, message: str):
        if on_progress:
            on_progress(step, message)

    state = ProjectState(project_goal=project_goal)

    progress("requirements", "요구사항을 구조화하고 있습니다.")
    state.requirements = run_requirement_agent(project_goal)

    if state.requirements.needs_clarification:
        progress("clarification", "추가 정보가 필요합니다.")
        return WorkflowResult(state=state, stopped_for_clarification=True)

    progress("architecture", "요구사항을 기능 모듈에 연결하고 있습니다.")
    state.architecture = run_system_agent(project_goal, state.requirements)

    progress("verification", "요구사항 기반 시험 항목을 생성하고 있습니다.")
    state.verification = run_verification_agent(
        project_goal,
        state.requirements,
        state.architecture,
    )

    progress("traceability", "REQ → MOD → TEST 연결을 검사하고 있습니다.")
    state.traceability = check_traceability(
        state.requirements,
        state.architecture,
        state.verification,
    )

    progress("review", "누락 연결과 설계 일관성을 검토하고 있습니다.")
    state.review = run_reviewer_agent(state)

    progress("planning", "개발 단계를 정리하고 있습니다.")
    state.development_plan = run_planner_agent(state)

    progress("complete", "Engineering Report 생성이 완료되었습니다.")
    return WorkflowResult(state=state)
