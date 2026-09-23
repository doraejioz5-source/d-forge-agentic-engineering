import json
from agents import Runner

from dforge.agents.common import make_agent
from dforge.schemas import ProjectState, RetestOutput

INSTRUCTIONS = """
You are the Retest Planning specialist in D-FORGE.
Propose candidate tests to review or repeat after a reported issue or engineering change.

Rules:
- Prefer existing TEST IDs from the current verification plan.
- Rank candidates as high, medium, or low priority.
- Explain why each test is relevant to the reported issue or impact scope.
- Include prerequisite checks before any repeat testing.
- Do not present the retest list as a final authority; it is an engineering review aid.
"""

agent = make_agent(
    name="D-FORGE Retest Planner",
    instructions=INSTRUCTIONS,
    output_type=RetestOutput,
)


def run_retest_agent(state: ProjectState) -> RetestOutput:
    payload = state.model_dump()
    result = Runner.run_sync(agent, json.dumps(payload, ensure_ascii=False))
    return result.final_output
