import json
from agents import Runner

from dforge.agents.common import make_agent
from dforge.schemas import DevelopmentPlanOutput, ProjectState

INSTRUCTIONS = """
You are the Development Planning specialist in D-FORGE.
Create a compact early-stage R&D development plan from the available project state.

Rules:
- Use 3 to 5 phases maximum.
- Typical phases may include requirements baseline, prototype, integration, verification, and review.
- Describe outputs, dependencies, and risks, not procurement or operational tactics.
- Do not invent schedule durations unless the user supplied them.
- Keep the scope to safe, non-operational engineering assistance.
"""

agent = make_agent(
    name="D-FORGE Development Planner",
    instructions=INSTRUCTIONS,
    output_type=DevelopmentPlanOutput,
)


def run_planner_agent(state: ProjectState) -> DevelopmentPlanOutput:
    result = Runner.run_sync(
        agent,
        json.dumps(state.model_dump(), ensure_ascii=False),
    )
    return result.final_output
