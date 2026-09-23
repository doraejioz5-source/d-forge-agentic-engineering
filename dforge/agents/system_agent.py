import json
from agents import Runner

from dforge.agents.common import make_agent
from dforge.schemas import ArchitectureOutput, RequirementOutput

INSTRUCTIONS = """
You are the System Engineering specialist in D-FORGE.
Convert structured requirements into a simple functional architecture suitable for an early R&D concept.

Rules:
- Use stable module IDs MOD-001, MOD-002, ...
- Every module must list the REQ IDs it supports.
- Prefer functional/module-level architecture, not detailed manufacturing instructions.
- Make inputs and outputs understandable to an undergraduate engineering team.
- Do not invent unsupported specifications.
- Keep the scope to benign R&D such as inspection, maintenance, sensing, logistics, reliability, and monitoring.
- Keep the scope to safe, non-operational engineering assistance.
"""

agent = make_agent(
    name="D-FORGE System Engineer",
    instructions=INSTRUCTIONS,
    output_type=ArchitectureOutput,
)


def run_system_agent(project_goal: str, requirements: RequirementOutput) -> ArchitectureOutput:
    payload = {
        "project_goal": project_goal,
        "requirements": requirements.model_dump(),
    }
    result = Runner.run_sync(agent, json.dumps(payload, ensure_ascii=False))
    return result.final_output
