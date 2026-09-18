# HW 1 Answers

**1. Why does an infinite loop occur in an unmanaged raw agent loop?**

> An unmanaged raw loop keeps sending tool results back to the model whenever the model requests another tool call. The model is not guaranteed to stop or produce a final answer, so it may repeatedly request the same tool. Without a host-enforced limit such as `max_turns`, the loop has no reliable termination condition.

**2. What happens to the model when a tool raises an unhandled Python exception like `SISUnavailable`?**

> The exception escapes from the tool and crashes the host program before a tool result can be added to the conversation. Therefore, the model does not receive a structured failure message and cannot reason about or recover from the outage. The current run and its intermediate progress may also be lost.

**3. Why is it dangerous to return raw strings from a tool instead of a dictionary with metadata like `observed_as_of`?**

> A raw string does not provide a reliable structure, source, or timestamp for the reported information. The model may treat a seat count as current even though it was observed earlier and may make unsupported claims based on stale data. A structured dictionary lets the host and model distinguish the value from its metadata, including when and where it was observed.

**4. How does setting `needs_approval=True` affect the execution flow of the Runner?**

>  When the model requests that tool, the Runner does not execute it immediately. Instead, it pauses the run and exposes a `ToolApprovalItem` in the interruptions. The host converts the result to a run state, asks a human to approve or reject the call, records the decision with `state.approve()` or `state.reject()`, and then resumes the same run. Only an approved call is allowed to perform the mutation.
