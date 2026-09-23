import json
from agents import Runner

from dforge.agents.common import make_agent
from dforge.schemas import ChangeImpactOutput, ProjectState

INSTRUCTIONS = """
You are the Change Impact specialist in D-FORGE.
Given a failure analysis and current engineering artifacts, propose the scope that should be reviewed if the issue leads to a change.

Rules:
- Trace likely impact through requirement, module, interface, test, and document relationships.
- Do not claim every linked item must be changed; distinguish "review scope" from "confirmed change".
- Use existing REQ, MOD, and TEST IDs whenever they are available.
- Keep the result concise and suitable for an engineer deciding what to inspect next.
- The human engineer makes the final change decision.
"""

agent = make_agent(
    name="D-FORGE Change Impact Analyst",
    instructions=INSTRUCTIONS,
    output_type=ChangeImpactOutput,
)


def run_change_impact_agent(state: ProjectState) -> ChangeImpactOutput:
    payload = state.model_dump()
    result = Runner.run_sync(agent, json.dumps(payload, ensure_ascii=False))
    return result.final_output
