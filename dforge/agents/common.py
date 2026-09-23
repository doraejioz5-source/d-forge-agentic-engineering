from __future__ import annotations

import os
from agents import Agent


def make_agent(*, name: str, instructions: str, output_type):
    kwargs = {
        "name": name,
        "instructions": instructions,
        "output_type": output_type,
    }
    model = os.getenv("OPENAI_MODEL", "").strip()
    if model:
        kwargs["model"] = model
    return Agent(**kwargs)
