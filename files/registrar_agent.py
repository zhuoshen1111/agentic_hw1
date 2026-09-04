"""
Phase 1 & 2: Adult Supervision, Tools, and Mutations

This file uses the OpenAI Agents SDK to fix the broken raw loop.
You will replace the raw loop with a managed `Runner`, enforce strict tool
schemas with `@function_tool`, and add idempotency and approval to mutations.
"""

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from openai import AsyncOpenAI
from agents import Agent, Runner, RunConfig, function_tool

from registrar import (
    sis_enroll,
    alternatives_for,
    STUDENT_ID,
    CATALOG_OBSERVED_AS_OF,
    CATALOG_DATA_SOURCE,
    reset_registrar,
    enrolled_section_ids
)

# Use LM Studio by default, but use OpenAI API if a real key is present
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    os.environ["OPENAI_API_KEY"] = "not-needed"
    os.environ["OPENAI_BASE_URL"] = "http://localhost:1234/v1"
    
    # LM Studio supports the Chat Completions API, not the experimental Responses API
    from agents.models._openai_shared import set_use_responses_by_default
    set_use_responses_by_default(False)

# TODO 1: Setup the Agent and Runner
# Add `check_availability` and `enroll_student` to the Agent's tools.
raise NotImplementedError("TODO 1 -- see the comment above")

# TODO 2: Tool Engineering
# Convert `check_availability` into a strict tool.
# Add the `@function_tool` decorator.
# Write a docstring that acts as the prompt.
# Add strict Python type hints (section_id: str).
# Return a dictionary that includes the observed_as_of timestamp.
raise NotImplementedError("TODO 2 -- see the comment above")

# TODO 3: Mutations
# Decorate `enroll_student` with `@function_tool`.
# Make it safe by preventing double-enrollment (idempotency).
# Set `needs_approval=True` so humans can intercept it.
raise NotImplementedError("TODO 3 -- see the comment above")

# Now that tools are defined, attach them to the agent

async def run_agent(request: str):
    print(f"\n--- Running: {request} ---")
    reset_registrar()
    
    # TODO 4: Tracing & Human-in-the-Loop
    # Run the agent and turn on event streaming to peek inside the black box.
    # 1. Use `Runner.run_streamed()` in a `while True` loop to watch events in real-time.
    # 2. Check if the runner was interrupted by a `ToolApprovalItem`.
    # 3. If so, prompt the user with `input()`, approve it via `state.approve()`, and resume the loop!
    ...  # <-- your code here (TODO 4)

if __name__ == "__main__":
    asyncio.run(run_agent("Enroll me in EE 599 section 30412."))
