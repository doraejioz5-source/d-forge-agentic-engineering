import json
from agents import Runner

from dforge.agents.common import make_agent
from dforge.schemas import AdvisorOutput, ProjectState

INSTRUCTIONS = """
You are the conversational Engineering Advisor inside D-FORGE.
Answer the user's question using the current ProjectState.

Rules:
- Explain what the current engineering artifacts mean in simple language.
- Refer to existing REQ, MOD, and TEST IDs when useful.
- Do not pretend an artifact exists when it is missing.
- If the user asks for a modification that requires regenerating a stage, explain which stage should be rerun.
- Keep answers concise enough for an interactive engineering assistant.
- Do not invent numeric performance targets or unsupported facts.
- Keep the scope to safe, non-operational R&D assistance.
"""

agent = make_agent(
    name="D-FORGE Engineering Advisor",
    instructions=INSTRUCTIONS,
    output_type=AdvisorOutput,
)


def answer_project_question(user_message: str, state: ProjectState) -> AdvisorOutput:
    payload = {
        "user_message": user_message,
        "project_state": state.model_dump(),
    }
    result = Runner.run_sync(agent, json.dumps(payload, ensure_ascii=False))
    return result.final_output
