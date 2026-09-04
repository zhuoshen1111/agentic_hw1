"""
Phase 0: The Black Box

This script demonstrates what happens when you run an unmanaged "raw loop"
without an SDK or orchestrator.

Run this script to observe three distinct failure modes:
1. "outage": The backend raises an exception and crashes the whole process.
2. "stubborn": The agent gets stuck in an infinite loop.
3. "duplicate": The agent asks to enroll the same student twice, and succeeds.

You do not need to write any code here. This is a demonstration.
"""
from registrar import (
    fake_model,
    sis_enroll,
    STUDENT_ID,
    reset_registrar,
    banner,
    crashed,
    step,
)

def run_raw_loop(transcript_name: str, max_turns: int = 5):
    reset_registrar()
    model = fake_model(transcript_name)
    history = []
    
    print(f"\n--- Running: {transcript_name} ---")
    try:
        while True:
            # 1. Ask the model
            reply = model.respond(history)
            
            # 2. If it's a final answer, we are done
            if "final" in reply:
                step("Final Answer:", reply["final"]["summary"])
                break
                
            # 3. If it's a tool request, execute it
            if "tool_calls" in reply:
                for call in reply["tool_calls"]:
                    name = call["name"]
                    args = call["arguments"]
                    
                    if name == "enroll":
                        # The raw loop doesn't have idempotency or error handling
                        step(f"Tool {name}:", str(args))
                        result = sis_enroll(args["section_id"], STUDENT_ID)
                        history.append({"role": "tool", "content": result})
                    elif name == "check_eligibility":
                        step(f"Tool {name}:", str(args))
                        history.append({"role": "tool", "content": "You are eligible."})
                    elif name == "drop_all_courses":
                        step(f"Tool {name}:", str(args))
                        history.append({"role": "tool", "content": "Dropped all courses."})
                    elif name == "search_sections":
                        step(f"Tool {name}:", str(args))
                        history.append({"role": "tool", "content": "Found section 30412."})
                    else:
                        history.append({"role": "tool", "content": f"Unknown tool: {name}"})
                        
            if len(history) > max_turns:
                crashed("Infinite loop detected", f"Stopped after {max_turns} turns")
                break
                
    except Exception as e:
        crashed("Process crashed", f"{type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    banner("Phase 0: The Black Box")
    run_raw_loop("outage")     # Crashes on SISUnavailable
    run_raw_loop("stubborn")   # Gets stuck in an infinite loop
    run_raw_loop("duplicate")  # Double enrolls the student
