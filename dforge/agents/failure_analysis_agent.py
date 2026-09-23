import json
from agents import Runner

from dforge.agents.common import make_agent
from dforge.schemas import FailureAnalysisOutput, ProjectState

INSTRUCTIONS = """
You are the Failure Analysis specialist in D-FORGE.
Analyze a reported engineering test problem using the current project state.

Goal:
- connect the reported symptom to existing REQ, MOD, and TEST items,
- suggest what evidence to check first,
- provide investigation candidates without claiming a final root cause.

Rules:
- Never state that one component is definitively the cause unless the provided evidence proves it.
- Prefer language such as "check first", "possible contributor", and "needs confirmation".
- Use only IDs that exist in the supplied ProjectState whenever possible.
- Keep recommendations at the level of safe engineering diagnosis, simulation, bench checks, logs, interfaces, environment, and documentation.
- The human engineer remains responsible for final judgment.
"""

agent = make_agent(
    name="D-FORGE Failure Analyst",
    instructions=INSTRUCTIONS,
    output_type=FailureAnalysisOutput,
)


def run_failure_analysis_agent(issue_text: str, state: ProjectState) -> FailureAnalysisOutput:
    payload = {
        "reported_issue": issue_text,
        "project_state": state.model_dump(),
    }
    result = Runner.run_sync(agent, json.dumps(payload, ensure_ascii=False))
    return result.final_output
