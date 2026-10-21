# Lesson 01 Agent architecture and the ReAct runtime

*Instructor guide for the L3 agentic platform programme*

**Outcome** A working, bounded single-agent runtime in the learner's own repository, with interchangeable model access and observable tool use.

Duration: 120 minutes. Starting checkpoint: lesson-00. Ending checkpoint: lesson-01 (7133fdc).

Word version: [01 Agent architecture and the ReAct runtime.docx](01%20Agent%20architecture%20and%20the%20ReAct%20runtime.docx)

## Where this session sits in the platform

This session builds the agent runtime that the platform will host: the bounded ReAct loop that every agent runs on, and that every later component wraps rather than replaces. The runtime is the core of the agent, not of the platform; from Session 08 the platform hosts it, and in this course the platform runs agents in its own process as a teaching compromise. The agent registry (Session 08), MCP tool gateway (Session 09), identity and credentials (Session 10) and operations (Session 11) all sit around this loop. The run's event log, which records each model step, tool observation and failure, is the data that the console's Runs view renders as an event timeline from Session 08; today learners read it as JSON.

| Session | Platform component | Status |
|---|---|---|
| 01 | Agent runtime: bounded ReAct loop, typed run state, event log | **This session** |
| 02 | Tool contracts, approval boundary and MCP transport | Later session |
| 03 | Context selection, retrieval, memory and versioned artifacts | Later session |
| 04 | Evaluation harness and single-agent baseline | Later session |
| 05 | Durable runs, crash recovery and exact-action approval | Later session |
| 06 | Supervisor, scoped subagents and parallel coordination | Later session |
| 07 | Remote agents over A2A | Later session |
| 08 | Platform core: agent registry, run API and platform console | Later session |
| 09 | MCP tool gateway: policy, audit and shared upstream sessions | Later session |
| 10 | Agent identity, delegated credentials and credential store | Later session |
| 11 | Operations: traces, admission control and evaluated releases | Later session |
| 12 | Tuning, before/after evidence and the capstone presentation | Later session |

## Preparation

Refresh 2025 LLM/prompting/RAG basics and HTTP, JSON, async programming and tests. Prepare a demonstration project from the course kit's starter exactly as a learner would, with a repository in the course group on gitlab.ciklum.net, and rehearse all thirteen prompts on it. Keep the reference checkpoints at hand as the answer key for the excerpts. Read the architecture, ReAct and chosen model API tool-calling references.

Sketch the target platform that you will draw in the opening, labelling each component with the session that builds it; the platform table above gives the order.

Learners need two things: their own project repository in the course GitLab group on gitlab.ciklum.net, and the [learner kit](https://github.com/maxvpavlov/ciklum-innovate-l3-2026/tree/main/learner-kit) in the public course repository, which holds the starter project and, for each lesson, the given files and the check pack. Learners build their own implementation; the reference checkpoints in the same repository are the instructor's answer key.

Your coding agent handles preparation, implementation and execution. You set the scope, inspect its changes and explain the evidence. This development assistant is separate from the investigation agents inside the platform.

> **PROMPT** Set up my project for the Building Agentic Platforms course, starting at lesson-00. Clone the public course repository from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 into ~/agentic-course/course and treat that folder as read-only; its learner-kit folder is the course kit. Create my own project in ~/agentic-course/my-platform by copying learner-kit/starter, and make it a fresh Git repository on branch main with one initial commit; if Git has no user name or email, set them for this repository only and tell me. Install the pinned dependencies with uv for Python 3.12, run the tests with python -m pytest, and confirm that incident/__init__.py says LESSON = 0. Install the GitLab CLI, glab, if it is missing, and sign me in to the course GitLab at gitlab.ciklum.net. glab may already be signed in to other GitLab hosts, such as gitlab.com: keep those sign-ins, add gitlab.ciklum.net alongside them, and name gitlab.ciklum.net as the host in every glab command, because glab otherwise uses a default host. When a browser sign-in is needed, tell me what to do, and never ask me to paste a token into the chat. Ask me for the name of the group I was invited to on gitlab.ciklum.net. Every learner shares that group, so name my repository agentic-platform- followed by my Ciklum acronym: read my account through my glab sign-in on gitlab.ciklum.net and take the part of my @ciklum.com email before the @, in lowercase (abcd for abcd@ciklum.com gives agentic-platform-abcd); if the account shows no @ciklum.com email, ask me for my acronym. if a project with that name already exists in the group, stop and ask me instead of pushing to it. Create it as a private repository in that group, set it as the origin remote and push my project to it. Report both folder paths, the files in my project, the test result, the GitLab repository address and anything missing, such as uv, Python 3.12, glab or access to the group on gitlab.ciklum.net. Do not ask me to run terminal commands.

Next, have the coding agent read this lesson's check pack and add it to the project before any code is written.

> **PROMPT** Read learner-kit/lessons/01 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

**Instructor readiness** Rehearse the session with a learner project built from the course kit, so you see what learners see: the check pack fails until each capability is built. The reference checkpoint remains your answer key for the excerpts below. In class, use one bounded prompt at a time; learners inspect the change, explain the control decision and review the check evidence.

Session 01 is a demonstration. Learners need nothing before class and do not build during it: after class they repeat every prompt in their own project, starting with the setup prompt that creates their repository in the course GitLab group on gitlab.ciklum.net. Show each prompt exactly as they will use it, and point out where the check pack, the given files and the push happen.

**Offline fallback** Have the coding agent use the offline mock provider for class. If live access fails, restore that configuration and continue. Keep credentials in secure configuration. Adapter request shapes were tested with mock HTTP; live account access was not exercised.

Pinned versions in pyproject.toml and uv.lock: Python 3.12, MCP 2.2.0, A2A SDK 1.1.2, httpx 0.28.1, FastAPI 0.141.1, uvicorn 0.52.4, jsonschema 4.26.0, pytest 9.1.1 and pytest-asyncio 1.4.0. Have the coding agent manage their installation.

## Timed agenda

| Minutes | Activity | Format |
|---|---|---|
| 00 to 17 | Course opening: why agent teams, when to split work, why a platform, its parts, and the incident premise | Discussion |
| 17 to 30 | Concept script: the ReAct loop, one real run, who owns identity and limits | Discussion |
| 30 to 75 | Instructor demonstration of the setup prompt, the check pack and build steps 1 to 4 on a fresh project | Instructor demo |
| 75 to 95 | Break it on purpose: learners predict each guard's failure, the instructor runs it | Discussion |
| 95 to 110 | Verification evidence, the review prompt and pushing the checkpoint to GitLab | Instructor demo |
| 110 to 120 | Questions and the after-class assignment: repeat every prompt in your own project | Discussion |

## Instructor script and code walkthrough

Use SAY for instructor narration, SHOW and REVIEW for the code and evidence participants examine, PROMPT for text they give their coding agents, and PAUSE for discussion. Prompts define scope and expected behaviour; the agent handles command execution. Code excerpts remain as reading and review material from the exact reference checkpoint, not manual typing instructions.

### Opening and orientation

**SAY** Today we begin the platform that you will extend throughout this programme, so first draw where it is going. Put the agent runtime in the centre. Around it, sketch an agent registry of versioned definitions, remote agents and tool servers (Session 08); one MCP tool gateway that applies policy to every tool call and keeps an audit trail (Session 09); agent identity with delegated, short-lived credentials and a credential store (Session 10); and operations with evaluated releases (Session 11). Across the top, draw the platform console: a web UI that shows the registry, runs and approvals from Session 08, and later the gateway audit, identity and operations. Today we build only the centre box. Our incident is a payments service that slowed after a deployment; we want an investigation with cited evidence from mock logs and runbooks. Ask what a successful investigation should contain: a likely cause, the source of that claim, and a clear statement when evidence is insufficient. A fluent paragraph by itself is not an acceptance test. Our first checkpoint must also stop when it exhausts its allowance or begins repeating an action.

**SHOW** The coding agent’s baseline report, current learner project, synthetic incident records and lesson outcome. Ask participants to explain what already works before authorizing the next bounded change.

### Concept discussion

**SAY** Now zoom into the centre box and draw the model, runtime and tools as three separate boxes. The model proposes an action, the runtime decides whether and how to execute it, and the tool returns an observation. This is the ReAct loop: a thought, an action and an observation, repeated until the agent can answer. Explain what one model turn can contain. Every call returns one assistant message, and the provider reports why it ended. Tool calls mean the runtime runs the permitted ones and returns each observation with the same call ID. Text only is a candidate final answer that the runtime must check against the answer contract. A cut-off or refused turn is not an answer and should stop with a named reason, and text that is not the answer must be handled explicitly, never guessed at. Reasoning, whether visible text before a tool call or a provider's separate thinking, is never an action and never evidence. Be honest that today's runtime handles only tool calls and a valid JSON answer; truncation, refusals and non-final text fail without a named reason until we harden it for real models. Every later capability, including subagents and remote agents, reuses this loop. A hard-coded sequence can prescribe the steps in advance, and for INC-001 alone it would work. An AI investigation platform is worth building because real incidents do not follow a path written in advance: the next step depends on what the last one revealed, and the investigation should end in an approved fix. An agent chooses the next permitted action from what it has observed, and later sessions add subagents, remote specialists and approved remediation around this loop. Explain that our default provider is a deterministic fixture policy. It produces a known series of requests, so everyone can debug the same behaviour without credentials or network variability. OpenAI-compatible and Anthropic adapters normalize real provider responses into that same internal contract. A passing offline test validates the loop and its boundaries; assessing live-model reasoning will require a separate benchmark. Finish by asking which component owns a timeout. The runtime owns it, because a model instruction cannot enforce elapsed time.

**PAUSE** Invite one learner to trace the control flow and another to identify a failure boundary. Resolve different interpretations before opening the implementation.

### 1 Define the run contract

**SAY** Start with the values that application code controls. Tenant, run identifier, role and permitted tools belong in the execution context. They must not be supplied by a retrieved document. Keep the evolving messages and result in Run. This separation will matter when we persist a run or create a child: we can serialize task state while deliberately constructing its authority. Walk through one example context for Astro, then point to Limits. We have separate limits on steps, reported tokens, elapsed time and maximum requested output. These limits address different failure modes. Ask participants to identify the limit that catches a provider that hangs without producing any tokens.

**SHOW** The current learner implementation and `incident/core.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 01, continue in my learner project. Create the Context, Limits, Reply and Run contracts in incident/core.py. Separate application-owned tenant identity, permissions and run identifiers from model messages and results. Make run state serializable and give the runtime explicit step, token and time limits. The check pack needs these exact shapes: Limits takes the keywords steps, tokens and seconds, plus max_output_tokens, with defaults large enough for a three-step investigation (for example 8 steps, 8000 tokens, 20 seconds, 500 output tokens); a Context whose defaults work without arguments, because the checks call the runtime without one: tenant astro, a generated run_id, role investigator, allowed tools log_lookup and runbook_search, no approved actions and no parent_id; Reply(message, tokens=0, cost_usd=0); and a Run that exposes its context, messages, status (running, completed or failed), steps (model calls), tokens, cost_usd, pending, answer and error. Keep this step focused on the contracts; do not implement later platform features. No lesson test can run until run_agent exists, so check the contracts with a short script. Show the fields, their owners and one example of a value the model must not control. Build to the interfaces the Lesson 01 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 10 to 17 at lesson-01; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
@dataclass
class Context:
    tenant: str = "astro"
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    role: str = "investigator"
    allowed: tuple[str, ...] = ("log_lookup", "runbook_search")
    approved: tuple[str, ...] = ()
    parent_id: str | None = None
```

**Explain the choice** Typed dataclasses make ownership visible without introducing an orchestration framework. Run.snapshot exposes serializable state for later checkpoints. Token admission uses an approximate character-based input estimate at this stage; the provider's returned usage is checked again after each response.

**ASK** Why not place allowed tools inside the model's answer?

**Likely answer** An answer is untrusted output. The application constructs Context and decides the permitted capabilities independently.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 2 Normalize model access

**SAY** Keep provider-specific response shapes out of the loop. MockProvider and HTTPProvider both return a Reply containing an assistant message and usage. Show how an OpenAI tool call becomes an internal name and JSON arguments. Then show the Anthropic conversion, where tool results are user content blocks associated with a tool-use identifier. These are adapters around the same runtime. The environment selects the provider and model; credentials never go into the repository. Point out that changing a base URL is a configuration choice, not an instruction the agent is permitted to make during an investigation. For today's build, keep MODEL_PROVIDER set to mock.

**SHOW** The current learner implementation and `incident/providers.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 01, continue in my learner project. Implement the provider interface in incident/providers.py using the current core contracts. Paste the given MockProvider from the course kit unchanged, and implement configurable OpenAI-compatible and Anthropic adapters as HTTPProvider(kind, model, api_key, base_url=None, transport=None) with kind openai, openai-compatible or anthropic; complete(messages, tools, max_tokens=500) must work without max_tokens, and Reply.tokens is input plus output tokens. Provider selection comes from MODEL_PROVIDER (default mock), MODEL_NAME, MODEL_API_KEY and MODEL_BASE_URL, which overrides the default endpoint and is needed for OpenAI-compatible providers other than OpenAI. Normalize messages, tool calls and usage into Reply, and raise one provider error type whose message never includes the key or a response body. For Anthropic, the system message goes in a top-level system field and each tool's parameters become input_schema; OpenAI-compatible requests send the key as a Bearer Authorization header. Use mock HTTP responses (httpx.MockTransport) to check both adapter request shapes without paid calls; the check pack's adapter tests can only run after step 3, so rerun them then. Explain how provider selection and secrets are configured without exposing credentials. Build to the interfaces the Lesson 01 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 106 to 117 at lesson-01; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def provider_from_env():
    kind = os.getenv("MODEL_PROVIDER", "mock")
    if kind == "mock":
        return MockProvider()
    if kind not in {"openai", "openai-compatible", "anthropic"}:
        raise ValueError("Unsupported MODEL_PROVIDER")
    key, model = os.getenv("MODEL_API_KEY"), os.getenv("MODEL_NAME")
    if not key or not model:
        raise ValueError("Live mode requires MODEL_API_KEY and MODEL_NAME")
    return HTTPProvider(kind, model, key, os.getenv("MODEL_BASE_URL"),
                        input_rate=float(os.getenv("MODEL_INPUT_USD_PER_MILLION", "0")),
                        output_rate=float(os.getenv("MODEL_OUTPUT_USD_PER_MILLION", "0")))
```

**Explain the choice** The loop can be tested without a paid API. The two HTTP adapter contract tests inspect request bodies and normalize responses with a mock HTTP transport. They do not claim that a live account or a particular model was exercised.

**ASK** What does the adapter test prove, and what does it leave open?

**Likely answer** It proves request and response translation for the tested shapes. Credentials, account access, provider-specific model behaviour and live latency remain to be verified.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 3 Implement the loop and pending calls

**SAY** Now follow one iteration with a concrete call to log_lookup for INC-001. We record the proposed tool call before executing it, dispatch the name and arguments, and attach the observation using the same call identifier. The next model request includes that observation. Pause here and ask a learner to trace the identifier from assistant message to tool message. A repeated action with identical arguments is detected within the run. Later, pending calls will also become our recovery boundary. Notice that the model never invokes Python directly: the runtime calls the supplied executor. This makes the first implementation small enough to inspect and gives us one place to add contracts and authorization in Session 02.

**SHOW** The current learner implementation and `incident/core.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 01, continue in my learner project. Implement run_agent in incident/core.py and connect the synthetic readers in the given incident/fixtures.py. Use the signature run_agent(provider, execute, schemas, task, context=None, limits=None, checkpoint=None): start the conversation with a system message and the task as a user message, preserve assistant tool-call IDs when appending observations as tool messages, and track pending calls before dispatch. Finish with a JSON answer that has status (complete or insufficient_evidence), cause, summary and evidence, where evidence lists source_id values actually seen in tool results. Count each model call as a step; the INC-001 path takes 3. Use the existing provider interface. Show the complete model-to-tool-to-observation path for INC-001 and explain how the same loop can later support checkpointing. Add the step guard now: when the step limit is reached without an answer, fail the run with step_budget. After this step the happy path, step-limit and adapter tests should pass; the token, time and repeated-action guards come in step 4. Build to the interfaces the Lesson 01 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 91 to 111 at lesson-01; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
while run.pending:
    call = run.pending[0]
    key = json.dumps([call["name"], call["args"]], sort_keys=True)
    if key in seen:
        raise ValueError("repeated_action")
    seen.add(key)
    started = time.monotonic()
    try:
        result = await execute(call["name"], call["args"], run.context)
    except ApprovalRequired:
        run.status = "waiting_approval"
        save()
        return run
    run.event("tool", name=call["name"], ok=result.get("ok", True),
              elapsed_ms=(time.monotonic()-started)*1000)
    run.messages.append({"role": "tool", "tool_call_id": call["id"],
                         "content": json.dumps(result)})
    run.pending.pop(0)
    save()
# Reserve the requested maximum completion before dispatch.
estimated_input = len(json.dumps(run.messages)) // 3
```

**Explain the choice** Preserving tool-call identifiers is necessary for valid provider conversations. Recording pending work before execution is the foundation for later approval and recovery. The first lesson's simple_tools function is intentionally replaced by the validated executor in the next lesson.

**ASK** What goes wrong if we append a tool result without its assistant tool call?

**Likely answer** The conversation no longer contains a valid request/result pair. Providers may reject it, and the runtime loses the evidence needed to explain what happened.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 4 Bound and verify execution

**SAY** Run the happy path before introducing failures. The fixture requests logs, requests a runbook, and returns a final answer after three model steps. It cites log-astro-001 and rb-pool-v1. Next, run the limit tests and the repeating-provider example. Explain each failure as a controlled outcome rather than an unexplained exception. A one-step allowance prevents completion, a tiny token allowance prevents dispatch, and a deadline cancels an outstanding operation. Ask everyone to change one limit, predict the error, and then run the check. Close this section by locating the event records. We record actions and usage, and do not need access to hidden model reasoning to diagnose the loop. From Session 08, the platform console renders these same records as a run's event timeline, so keep them structured and complete.

**SHOW** The current learner implementation and `incident/core.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 01, continue in my learner project. This is build step 4, so the guards that step 3 deferred are now in scope. Keep the step guard and add the token, elapsed-time and repeated-action guards now, so that runs fail with exactly these error codes: step_budget, token_budget, TimeoutError (the deadline must cancel a provider call in progress) and repeated_action (the same tool with the same arguments requested twice in one run, refused before it runs again). Estimate input tokens before each model call as roughly the length of the serialized messages divided by three, and refuse the call if the tokens already reported in this run plus that estimate plus max_output_tokens would exceed the budget. Make the Session 01 check pack pass. Demonstrate the normal cited answer and deliberately trigger each limit using offline fixtures. Explain the approximate pre-dispatch token estimate and distinguish reported usage from configured cost. Show which guard caused each failure and why the run stopped. Build to the interfaces the Lesson 01 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 111 to 130 at lesson-01; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
estimated_input = len(json.dumps(run.messages)) // 3
if run.tokens + estimated_input + limits.max_output_tokens > limits.tokens:
    raise ValueError("token_budget")
reply = await provider.complete(run.messages, schemas,
                                limits.max_output_tokens)
run.steps += 1
run.tokens += reply.tokens
run.cost_usd += reply.cost_usd
run.event("model", step=run.steps, tokens=reply.tokens,
          cost_usd=reply.cost_usd)
run.messages.append(reply.message)
if run.tokens > limits.tokens:
    raise ValueError("token_budget")
calls = reply.message.get("tool_calls", [])
if calls:
    run.pending = [{"id": c["id"], "name": c["function"]["name"],
                    "args": json.loads(c["function"]["arguments"])}
                   for c in calls]
    save()
    continue
```

**Explain the choice** The fixture makes stop conditions reproducible. Costs are computed only from explicitly configured rates; zero configured pricing is not evidence that a live provider is free. Later lessons add stronger final-answer validation and structured tracing.

**ASK** Does a completed run necessarily mean the incident was solved?

**Likely answer** No. Execution can finish with an insufficient_evidence answer. Evaluation must distinguish successful execution from a supported task outcome.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

## Learner practice and checkpoints

> **PROMPT** Help me carry out the Lesson 01 learner exercise in my existing project: In a throwaway script run from the project root, pass different Limits values to run_agent, without editing the defaults: allow one step, then a tiny token budget, then a short deadline with a slow MockProvider (MockProvider(latency=...)). Predict and observe step_budget, token_budget and TimeoutError. Restore the normal limits and verify the cited happy-path answer. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

**VERIFY** Give the coding agent the verification prompt below, then inspect its evidence and explain the result in your own words.

> **PROMPT** Verify my Lesson 01 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 1 only when the required capability is present. Run the full test suite, which includes the Lesson 01 check pack and every earlier lesson's tests, and then the Session 01 demonstration with python -m incident.lab 1, all unchanged and using the offline provider (MODEL_PROVIDER unset or set to mock). Confirm that the passing count matches the one in the Lesson 01 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my repository on gitlab.ciklum.net; if glab is also signed in to other GitLab hosts, make sure the push goes to gitlab.ciklum.net. Do not equate an unrun or skipped check with a pass.

**Expected behaviour** The coding agent returns actual check results and the demonstration’s structured output. Run identifiers and elapsed times vary. Compare the status and capability outcomes with the recorded reference below, and investigate differences.

```json
{
  "capability": "bounded ReAct loop",
  "answer": {
    "status": "complete",
    "cause": "connection_pool_exhaustion",
    "summary": "INC-001: connection_pool_exhaustion",
    "evidence": [
      "log-astro-001",
      "rb-pool-v1"
    ]
  },
  "model_steps": 3,
  "repeated_action": "repeated_action"
}
```

**PAUSE** Ask learners to explain the evidence before accepting the checkpoint. If a check fails, use the specific recovery prompt below and review the resulting correction.

## Completion criteria

- INC-001 finishes with connection_pool_exhaustion and observed source IDs.
- The repeating provider stops with repeated_action.
- Step, token and elapsed-time limits produce the expected failures.
- Both live-provider request-shape tests pass without using real credentials.

The independently unpacked lesson-01 checkpoint passed its full test suite and this lesson demo, and so does the Lesson 01 check pack from the course kit. Recorded test result: 7 passed in 0.25s. Learners commit and push their checkpoint to their GitLab repository; lesson-01 (7133fdc) remains the instructor's answer key.

### Files changed in this checkpoint

In the reference, this checkpoint changed the files below. Learners write the implementation files themselves; the lab, the tests and any given files arrive in the Lesson 01 check pack. Ask the agent to explain any additional file changes it needs.

- `incident/__init__.py`
- `incident/core.py`
- `incident/fixtures.py`
- `incident/labs/l01.py`
- `incident/providers.py`
- `tests/test_lesson01.py`

> **PROMPT** Review my completed Lesson 01 work against the Lesson 01 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

## Demo troubleshooting

### Live mode fails before a request

> **PROMPT** I am working on Lesson 01. The symptom is: Live mode fails before a request. Diagnostic focus: Check MODEL_PROVIDER, MODEL_NAME and whether MODEL_API_KEY is set. Do not print the key. Recovery guidance: Switch to MODEL_PROVIDER=mock and rerun the demo. Configure the live adapter separately after class. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### The final message cannot be parsed

> **PROMPT** I am working on Lesson 01. The symptom is: The final message cannot be parsed. Diagnostic focus: The runtime expects a JSON answer with status, cause, summary and evidence. Recovery guidance: Inspect the normalized message in a debugger and compare it with MockProvider. Keep malformed-output tests separate from tool transport problems. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### The lesson command says the checkpoint is too early

> **PROMPT** I am working on Lesson 01. The symptom is: The lesson command says the checkpoint is too early. Diagnostic focus: incident/__init__.py still identifies the starting checkpoint. Recovery guidance: After completing the lesson changes, set LESSON to 1. If you are a lesson behind, ask your instructor for a catch-up checkpoint. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### A native Python package cannot load on macOS

> **PROMPT** I am working on Lesson 01. The symptom is: A native Python package cannot load on macOS. Diagnostic focus: A binary-wheel or local interpreter compatibility issue can occur before the course code runs. Recovery guidance: Use a compatible Python 3.12 installation or the tested Docker route described in the repository. Do not disable operating-system security protections. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## Practice and discussion

- Add a missing-incident acceptance scenario and explain what a supported insufficient-evidence response should look like.
- Write INC-001's investigation as a hard-coded sequence and run it and the agent loop on all three tickets. Note where the sequence gives a wrong or unsupported answer, and compare step counts and stop reasons.
- Redraw the platform blueprint in your own notes and mark the box today's checkpoint fills. For each later console view, note whether today's event log already records the data it needs.

**Discussion prompt** Which decision would change for a larger or more sensitive workload, and what additional evidence would you require before changing it? Tie the answer to the code, the task requirements and the acceptance checks.

## Verification scope

All course tags were independently unpacked and tested. The completed repository has 51 passing tests. Real local MCP stdio, the tool gateway's shared sessions and pinned definitions, A2A HTTP discovery, streaming, delegated-token authentication and cancellation were exercised. The platform console was driven in a headless Chromium browser against every checkpoint from lesson-08 onward.

Live model credentials, paid provider calls, live model judging, third-party MCP or A2A services, remote MCP OAuth, an enterprise identity provider, a managed secret vault, production cloud rollout and an external observability collector were not tested. The offline provider is a deterministic fixture, so its usage and quality results are teaching measurements. Read TESTING.md for the full scope and environment details.

## Session close

**SAY** You now own the loop that every later agent will use: the centre box of the platform you drew today. After class, repeat today's prompts in your own project, starting with the setup prompt, and push your checkpoint to your GitLab repository. Be ready to explain how one action moves from model proposal to tool observation. Keep your blueprint; we will add a component to it in most sessions, and from Session 08 the console will render these same run events. In the next session we make that tool boundary reliable and connect the same capabilities through MCP.

## References and further study

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [ReAct paper](https://arxiv.org/abs/2210.03629)
