"""
EE 599 -- HW 1: does this machine have a model it can talk to?

Run this before Part 8. Nothing else in the assignment needs it: Parts 1
through 7 use a ScriptedModel and never touch the network.

    python check_llm.py
    python check_llm.py --url http://localhost:1234/v1

It checks two backends and tells you which ones Part 9 can use.

    LM Studio   a model running on your own machine, serving the OpenAI
                chat-completions API on http://localhost:1234 by default.
                Start LM Studio, load a model, turn the local server on.
                No account, no key, no cost, and it works on a plane.

    OpenAI      the hosted API. Needs a key in .env. Costs a small amount.
                Better at agentic tool use than most local models.

Either is enough, and neither is required: Part 9 is a bonus part and Parts 1
to 8 never touch the network.

The Codex CLI is not listed. It is a command-line program rather than a model
provider, so the Agents SDK cannot drive it: the SDK needs a model object it
can call, not a subprocess.

Both are the same protocol. LM Studio implements the OpenAI chat-completions
API, which is why the SDK drives both and the only difference is which client
you hand to the Agent. That is the practical meaning of "OpenAI-compatible",
and it is why local models are worth knowing about: the agent you write against
one runs against the other.

Only the standard library is used here, on purpose. A diagnostic that needs a
working environment in order to tell you your environment is broken is not a
diagnostic.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_URL = "http://localhost:1234/v1"


def load_env(path: str = ".env") -> dict[str, str]:
    """Read KEY=VALUE lines from a .env file into os.environ.

    Twelve lines instead of a dependency, and it is imported by part8_live.py
    too. Values already set in the real environment win, because an explicit
    `OPENAI_API_KEY=... python part8_live.py` should beat a stale file.

    Nothing here is clever. Read it once so you know exactly what your secrets
    are being loaded by.
    """
    loaded: dict[str, str] = {}
    file = Path(path)
    if not file.exists():
        return loaded
    for line in file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if not value:
            continue
        loaded[key] = value
        os.environ.setdefault(key, value)
    return loaded

GREEN, RED, YELLOW, DIM, BOLD, OFF = (
    "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m"
)


def ok(label: str, detail: str = "") -> None:
    print(f"  {GREEN}PASS{OFF}  {label:<34} {DIM}{detail}{OFF}")


def bad(label: str, detail: str = "") -> None:
    print(f"  {RED}FAIL{OFF}  {label:<34} {DIM}{detail}{OFF}")


def warn(label: str, detail: str = "") -> None:
    print(f"  {YELLOW}WARN{OFF}  {label:<34} {DIM}{detail}{OFF}")


def post(url: str, payload: dict, timeout: float = 180) -> tuple[dict, float]:
    """POST JSON and return the decoded reply and how long it took."""
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 # LM Studio ignores the value but some clients insist on one.
                 "Authorization": "Bearer lm-studio"},
    )
    started = time.time()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read()), time.time() - started


def check_lmstudio(base_url: str) -> bool:
    """Four checks against a local OpenAI-compatible server."""
    print(f"\n{BOLD}LM Studio at {base_url}{OFF}")

    # 1. Is anything listening, and what has it loaded?
    try:
        with urllib.request.urlopen(f"{base_url}/models", timeout=10) as response:
            models = [entry["id"]
                      for entry in json.loads(response.read())["data"]]
    except urllib.error.URLError as error:
        bad("server reachable", f"{error.reason}")
        print(f"        {DIM}Open LM Studio, load a model, and switch the "
              f"local server on (Developer tab).{OFF}")
        return False
    except Exception as error:  # noqa: BLE001
        bad("server reachable", f"{type(error).__name__}: {error}")
        return False

    chat_models = [name for name in models if "embed" not in name.lower()]
    if not chat_models:
        bad("a chat model is loaded", f"only found {models}")
        return False
    model = chat_models[0]
    ok("server reachable", f"{len(models)} model(s) loaded")
    ok("chat model", model)

    # 2. Does it answer at all?
    try:
        reply, seconds = post(f"{base_url}/chat/completions", {
            "model": model,
            "messages": [{"role": "user",
                          "content": "Reply with the single word: ready"}],
            "max_tokens": 64,
        })
        text = (reply["choices"][0]["message"].get("content") or "").strip()
        ok("plain chat", f"{seconds:.1f}s -> {text[:40]!r}")
    except Exception as error:  # noqa: BLE001
        bad("plain chat", f"{type(error).__name__}: {error}")
        return False

    # 3. Structured output. This is what Part 8 falls back on if the model
    #    cannot do tool calling.
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"},
                       "arguments_json": {"type": "string"}},
        "required": ["name", "arguments_json"],
        "additionalProperties": False,
    }
    structured = False
    try:
        reply, seconds = post(f"{base_url}/chat/completions", {
            "model": model,
            "messages": [{"role": "user", "content":
                          "Call search_sections with the query EE 599. "
                          "arguments_json must be a JSON string."}],
            "response_format": {"type": "json_schema", "json_schema": {
                "name": "tool_call", "strict": True, "schema": schema}},
            "max_tokens": 300,
        })
        payload = json.loads(reply["choices"][0]["message"]["content"])
        assert "name" in payload and "arguments_json" in payload
        structured = True
        ok("structured output", f"{seconds:.1f}s -> {payload['name']}")
    except Exception as error:  # noqa: BLE001
        warn("structured output", f"{type(error).__name__}: {str(error)[:60]}")

    # 4. Native tool calling. This is the one Part 8 prefers, because it takes
    #    the output of your TODO 3 unmodified.
    tools = [{
        "type": "function",
        "function": {
            "name": "search_sections",
            "description": "Search the USC catalog. Example query: EE 599",
            "parameters": {"type": "object",
                           "properties": {"query": {"type": "string"}},
                           "required": ["query"]},
        },
    }]
    tool_calling = False
    try:
        reply, seconds = post(f"{base_url}/chat/completions", {
            "model": model,
            "messages": [{"role": "user",
                          "content": "Find the EE 599 agents class."}],
            "tools": tools, "tool_choice": "auto", "max_tokens": 300,
        })
        made = reply["choices"][0]["message"].get("tool_calls") or []
        assert made, "the model replied with prose instead of a tool call"
        tool_calling = True
        ok("native tool calling",
           f"{seconds:.1f}s -> {made[0]['function']['name']}"
           f"({made[0]['function']['arguments'][:40]})")
    except Exception as error:  # noqa: BLE001
        warn("native tool calling", f"{type(error).__name__}: {str(error)[:60]}")

    if not (structured or tool_calling):
        print(f"        {DIM}The server works but this model cannot be "
              f"constrained. Load an instruct model that advertises tool "
              f"use.{OFF}")
    return structured or tool_calling


def check_openai() -> bool:
    """Is there a usable OPENAI_API_KEY, and does the chosen model exist?"""
    print(f"\n{BOLD}OpenAI API{OFF}")
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        warn("OPENAI_API_KEY", "not set")
        print(f"        {DIM}cp .env.example .env, then paste a key from "
              f"https://platform.openai.com/api-keys{OFF}")
        return False
    # Never print a key. Four characters is enough to tell two apart.
    ok("OPENAI_API_KEY", f"set, ends {key[-4:]}, {len(key)} chars")

    wanted = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    request = urllib.request.Request(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            available = {entry["id"]
                         for entry in json.loads(response.read())["data"]}
    except urllib.error.HTTPError as error:
        bad("key accepted", f"HTTP {error.code} -- the key was rejected")
        return False
    except Exception as error:  # noqa: BLE001
        bad("key accepted", f"{type(error).__name__}: {error}")
        return False

    ok("key accepted", f"{len(available)} model(s) available")
    if wanted in available:
        ok("OPENAI_MODEL", wanted)
        return True
    bad("OPENAI_MODEL", f"{wanted!r} is not one of them")
    suggestions = sorted(name for name in available
                         if name.startswith("gpt-"))[:6]
    print(f"        {DIM}try one of: {', '.join(suggestions)}{OFF}")
    return False


def main() -> int:
    url = DEFAULT_URL
    if "--url" in sys.argv:
        url = sys.argv[sys.argv.index("--url") + 1].rstrip("/")

    print(f"{BOLD}{'=' * 70}\nEE 599 HW 1 -- model backend check\n{'=' * 70}{OFF}")
    loaded = load_env()
    print(f"  {DIM}.env: "
          f"{'loaded ' + ', '.join(sorted(loaded)) if loaded else 'not found'}"
          f"{OFF}")
    if "--url" not in sys.argv:
        url = os.environ.get("LMSTUDIO_BASE_URL", url).rstrip("/")

    lmstudio = check_lmstudio(url)
    openai_api = check_openai()

    print(f"\n{BOLD}Verdict{OFF}")
    if lmstudio:
        print(f"  {GREEN}LM Studio:{OFF}  python part9_live.py")
    if openai_api:
        print(f"  {GREEN}OpenAI API:{OFF} python part9_live.py --openai")
    if not (lmstudio or openai_api):
        print(f"  {YELLOW}No live backend found.{OFF} Part 9 is a bonus; "
              f"skip it.")
        print(f"  {DIM}Parts 1-8 do not need one at all.{OFF}")
    if lmstudio and not openai_api:
        print(f"  {DIM}Note: small local models are often poor at agentic "
              f"tool use. Part 9 has something to say about that.{OFF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
