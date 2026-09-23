import json
from agents import Runner

from dforge.agents.common import make_agent
from dforge.schemas import ProjectState, RouteDecision

INSTRUCTIONS = """
You are the routing manager for D-FORGE, an Agentic Engineering Assistant.
Your job is only to choose the next engineering action for the user's latest message.

Choose exactly one action:
- requirements: start, refine, or update requirements
- architecture: create or explain the system/function architecture
- verification: create or explain tests and verification
- review: inspect traceability gaps or engineering consistency
- planning: create or explain the R&D development plan
- run_all: user explicitly asks to continue everything, finish everything, or generate the full report
- status: user asks what is complete or where the project currently stands
- question: user asks a general explanatory question about the existing project

Routing rules:
- If the project has no goal yet, choose requirements.
- If the user provides new project constraints or changes core functionality, choose requirements.
- If a requested stage depends on missing earlier stages, still choose the requested stage; the app will create prerequisites.
- Do not produce engineering content. Only route.
- Keep the scope to safe, non-operational R&D assistance.
"""

agent = make_agent(
    name="D-FORGE Router",
    instructions=INSTRUCTIONS,
    output_type=RouteDecision,
)


def route_message(user_message: str, state: ProjectState) -> RouteDecision:
    payload = {
        "user_message": user_message,
        "project_state": state.model_dump(),
    }
    result = Runner.run_sync(agent, json.dumps(payload, ensure_ascii=False))
    return result.final_output
