import json
from agents import Runner

from dforge.agents.common import make_agent
from dforge.schemas import ProjectState, ReviewOutput

INSTRUCTIONS = """
You are the Engineering Reviewer in D-FORGE.
Review traceability gaps and early-stage engineering consistency.

Rules:
- Focus on missing requirement-to-module or requirement-to-test links.
- Recommend small corrective actions rather than redesigning the entire system.
- Be concise.
- Keep the scope to safe, non-operational engineering assistance.
"""

agent = make_agent(
    name="D-FORGE Engineering Reviewer",
    instructions=INSTRUCTIONS,
    output_type=ReviewOutput,
)


def run_reviewer_agent(state: ProjectState) -> ReviewOutput:
    payload = {
        "project_goal": state.project_goal,
        "traceability": state.traceability.model_dump() if state.traceability else {},
        "requirements": state.requirements.model_dump() if state.requirements else {},
        "architecture": state.architecture.model_dump() if state.architecture else {},
        "verification": state.verification.model_dump() if state.verification else {},
    }
    result = Runner.run_sync(agent, json.dumps(payload, ensure_ascii=False))
    return result.final_output
