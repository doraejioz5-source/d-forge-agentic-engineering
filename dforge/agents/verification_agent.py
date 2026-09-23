import json
from agents import Runner

from dforge.agents.common import make_agent
from dforge.schemas import ArchitectureOutput, RequirementOutput, VerificationOutput

INSTRUCTIONS = """
You are the Verification Engineering specialist in D-FORGE.
Create an early verification plan from requirements and a functional architecture.

Rules:
- Use stable IDs TEST-001, TEST-002, ...
- Every test must list one or more related REQ IDs.
- Prefer safe bench, simulation, software, interface, and functional verification language.
- Pass criteria must be clear but must not invent numeric thresholds unless supplied by the user.
- Identify engineering risks at a high level.
- Keep the scope to safe, non-operational engineering assistance.
"""

agent = make_agent(
    name="D-FORGE Verification Engineer",
    instructions=INSTRUCTIONS,
    output_type=VerificationOutput,
)


def run_verification_agent(
    project_goal: str,
    requirements: RequirementOutput,
    architecture: ArchitectureOutput,
) -> VerificationOutput:
    payload = {
        "project_goal": project_goal,
        "requirements": requirements.model_dump(),
        "architecture": architecture.model_dump(),
    }
    result = Runner.run_sync(agent, json.dumps(payload, ensure_ascii=False))
    return result.final_output
