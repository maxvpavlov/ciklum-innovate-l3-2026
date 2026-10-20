# Coding agent prompts for the course

Each learner builds their own platform in their own repository in the course GitLab group, by prompting a coding agent. The learner kit in the public course repository (https://github.com/maxvpavlov/ciklum-innovate-l3-2026/tree/main/learner-kit) supplies the starter project and, for every lesson, the given files and a check pack of tests that fail until the capability is built. It contains no solutions. The agent handles setup, repository operations, execution and verification. You set scope, inspect code and decide whether the observed evidence meets the lesson criteria.

These prompts guide a learner implementation; a coding agent’s completion message is not proof that its result passed the checks. Use offline fixtures unless you deliberately configure and authorize a live integration.

## 01. Agent architecture and the ReAct runtime

Course kit: learner-kit/lessons/01. Instructor answer key: lesson-00 to lesson-01.

### Prepare the workspace

> Set up my project for the Building Agentic Platforms course, starting at lesson-00. Clone the public course repository from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 into ~/agentic-course/course and treat that folder as read-only; its learner-kit folder is the course kit. Create my own project in ~/agentic-course/my-platform by copying learner-kit/starter, and make it a fresh Git repository on branch main with one initial commit; if Git has no user name or email, set them for this repository only and tell me. Install the pinned dependencies with uv for Python 3.12, run the tests with python -m pytest, and confirm that incident/__init__.py says LESSON = 0. Install the GitLab CLI, glab, if it is missing, and sign me in to GitLab; when a browser sign-in is needed, tell me what to do, and never ask me to paste a token into the chat. Ask me for the name of the GitLab group I was invited to, create a private repository for my project in that group, and push my project to it. Report both folder paths, the files in my project, the test result, the GitLab repository address and anything missing, such as uv, Python 3.12, glab or access to the group. Do not ask me to run terminal commands.

### Add the check pack

> Read learner-kit/lessons/01 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

### Build step 1

> For Lesson 01, continue in my learner project. Create the Context, Limits, Reply and Run contracts in incident/core.py. Separate application-owned tenant identity, permissions and run identifiers from model messages and results. Make run state serializable and give the runtime explicit step, token and time limits. The check pack needs these exact shapes: Limits takes the keywords steps, tokens and seconds, plus max_output_tokens, with defaults large enough for a three-step investigation (for example 8 steps, 8000 tokens, 20 seconds, 500 output tokens); a default Context whose tenant is astro, because the checks call the runtime without one; Reply(message, tokens=0, cost_usd=0); and a Run that exposes messages, status (running, completed or failed), steps (model calls), tokens, pending, answer and error. Keep this step focused on the contracts; do not implement later platform features. No lesson test can run until run_agent exists, so check the contracts with a short script. Show the fields, their owners and one example of a value the model must not control. Build to the interfaces the Lesson 01 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 01, continue in my learner project. Implement the provider interface in incident/providers.py using the current core contracts. Paste the given MockProvider from the course kit unchanged, and implement configurable OpenAI-compatible and Anthropic adapters as HTTPProvider(kind, model, api_key, base_url=None, transport=None) with kind openai, openai-compatible or anthropic; complete(messages, tools, max_tokens=500) must work without max_tokens, and Reply.tokens is input plus output tokens. Provider selection comes from MODEL_PROVIDER (default mock), MODEL_NAME, MODEL_API_KEY and MODEL_BASE_URL. Normalize messages, tool calls, errors and usage into Reply. Use mock HTTP responses (httpx.MockTransport) to check both adapter request shapes without paid calls; the check pack's adapter tests can only run after step 3, so rerun them then. Explain how provider selection and secrets are configured without exposing credentials. Build to the interfaces the Lesson 01 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 01, continue in my learner project. Implement run_agent in incident/core.py and connect the synthetic readers in the given incident/fixtures.py. Use the signature run_agent(provider, execute, schemas, task, context=None, limits=None, checkpoint=None): start the conversation with a system message and the task as a user message, preserve assistant tool-call IDs when appending observations as tool messages, and track pending calls before dispatch. Finish with a JSON answer that has status (complete or insufficient_evidence), cause, summary and evidence, where evidence lists source_id values actually seen in tool results. Count each model call as a step; the INC-001 path takes 3. Use the existing provider interface. Show the complete model-to-tool-to-observation path for INC-001 and explain how the same loop can later support checkpointing. After this step the happy path, step-limit and adapter tests should pass; the token and time limits come in step 4. Build to the interfaces the Lesson 01 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 01, continue in my learner project. Review and enforce the runtime's step, token, elapsed-time and repeated-action guards, failing the run with exactly these error codes: step_budget, token_budget, TimeoutError (the deadline must cancel a provider call in progress) and repeated_action (the same tool with the same arguments requested twice in one run). Estimate input tokens before each model call as roughly the length of the serialized messages divided by three, add max_output_tokens, and refuse the call if that would exceed the budget. Make the Session 01 check pack pass. Demonstrate the normal cited answer and deliberately trigger each limit using offline fixtures. Explain the approximate pre-dispatch token estimate and distinguish reported usage from configured cost. Show which guard caused each failure and why the run stopped. Build to the interfaces the Lesson 01 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 01 learner exercise in my existing project: In a throwaway script, change Limits to allow one step, then a tiny token budget, then a short deadline with a slow MockProvider (MockProvider(latency=...)). Predict and observe step_budget, token_budget and TimeoutError. Restore the normal limits and verify the cited happy-path answer. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 01 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 1 only when the required capability is present. Run the full test suite, which includes the Lesson 01 check pack and every earlier lesson's tests, and then the Session 01 demonstration with python -m incident.lab 1, all unchanged and using the offline provider. Confirm that the passing count matches the one in the Lesson 01 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

### Review the result

> Review my completed Lesson 01 work against the Lesson 01 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

### Recover when live mode fails before a request

> I am working on Lesson 01. The symptom is: Live mode fails before a request. Diagnostic focus: Check MODEL_PROVIDER, MODEL_NAME and whether MODEL_API_KEY is set. Do not print the key. Recovery guidance: Switch to MODEL_PROVIDER=mock and rerun the demo. Configure the live adapter separately after class. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the final message cannot be parsed

> I am working on Lesson 01. The symptom is: The final message cannot be parsed. Diagnostic focus: The runtime expects a JSON answer with status, cause, summary and evidence. Recovery guidance: Inspect the normalized message in a debugger and compare it with MockProvider. Keep malformed-output tests separate from tool transport problems. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the lesson command says the checkpoint is too early

> I am working on Lesson 01. The symptom is: The lesson command says the checkpoint is too early. Diagnostic focus: incident/__init__.py still identifies the starting checkpoint. Recovery guidance: After completing the lesson changes, set LESSON to 1. If you are a lesson behind, ask your instructor for a catch-up checkpoint. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a native python package cannot load on macos

> I am working on Lesson 01. The symptom is: A native Python package cannot load on macOS. Diagnostic focus: A binary-wheel or local interpreter compatibility issue can occur before the course code runs. Recovery guidance: Use a compatible Python 3.12 installation or the tested Docker route described in the repository. Do not disable operating-system security protections. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 02. Reliable tools and MCP integration

Course kit: learner-kit/lessons/02. Instructor answer key: lesson-01 to lesson-02.

### Prepare the workspace

> Prepare my learner project for Lesson 02. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-01 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

### Add the check pack

> Read learner-kit/lessons/02 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

### Build step 1

> For Lesson 02, continue in my learner project. Implement ToolExecutor in incident/tools.py. Check tool existence, application-owned capabilities and JSON arguments before dispatch. Reject unexpected tenant arguments and oversized results. Return structured errors that distinguish terminal failures from retryable read failures. Preserve the existing agent loop. Demonstrate malformed arguments and an unauthorized write proposal being rejected before a handler performs an effect. Build to the interfaces the Lesson 02 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 02, continue in my learner project. Add exact-action approval and idempotent mock remediation to ToolExecutor. Bind the action key to tenant, run, tool name and canonical arguments. Commit the local mock effect and its deduplication record atomically in SQLite. Test the same approved write after reopening the executor and test changed arguments against the original approval. Show that only one local effect exists, and explain the limit of this guarantee for external APIs. Build to the interfaces the Lesson 02 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 02, continue in my learner project. Implement the MCP server in incident/mcp_bridge.py with the pinned SDK. Expose the existing tenant-scoped log and runbook readers plus the runbook resource. Bind tenant identity in trusted launcher configuration, keep protocol stdout clean, and limit the server to the capabilities required by this lesson. Explain the host, client, server and resource roles before demonstrating discovery. Build to the interfaces the Lesson 02 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 02, continue in my learner project. Implement the MCP read adapter and connect it behind ToolExecutor. Use the real local stdio transport and the pinned SDK's result shapes. Make the Session 02 check pack pass, show the negotiated protocol and discovered tools, and run the same investigation through the adapter. Confirm that transport discovery does not grant new permissions and show the unchanged cited outcome. Build to the interfaces the Lesson 02 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 02 learner exercise in my existing project: Add an unexpected tenant argument to a log request, call mock_remediate with a read-only Context, lower output_limit, and repeat an approved mock write after reopening the SQLite executor. Record the error category or replay behaviour for each case. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 02 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 2 only when the required capability is present. Run the full test suite, which includes the Lesson 02 check pack and every earlier lesson's tests, and then the Session 02 demonstration with python -m incident.lab 2, all unchanged and using the offline provider. Confirm that the passing count matches the one in the Lesson 02 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

### Review the result

> Review my completed Lesson 02 work against the Lesson 02 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

### Recover when mcp startup or parsing fails

> I am working on Lesson 02. The symptom is: MCP startup or parsing fails. Diagnostic focus: Look for debug output written to stdout or a process started from the wrong repository directory. Recovery guidance: Keep protocol stdout clean, use stderr logging and rerun the isolated stdio test. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when result-field attribute error

> I am working on Lesson 02. The symptom is: Result-field attribute error. Diagnostic focus: Compare the installed MCP version with the lock file and the result field names in the adapter. Recovery guidance: Restore the pinned Python 3.12 environment from the project lock file. Avoid mixing 1.x tutorial code with the 2.2.0 adapter. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when tool exists but returns permission_denied

> I am working on Lesson 02. The symptom is: Tool exists but returns permission_denied. Diagnostic focus: Inspect Context.allowed rather than the server's discovery list. Recovery guidance: Use the intended read-only investigator or construct an operator-owned context explicitly for the mock-approval exercise. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a changed schema breaks an integration

> I am working on Lesson 02. The symptom is: A changed schema breaks an integration. Diagnostic focus: The client-side tool contract and the discovered server contract differ. Recovery guidance: Pin the compatible server/client versions, update the adapter deliberately and rerun contract tests before using the changed tool. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 03. Context, retrieval and memory

Course kit: learner-kit/lessons/03. Instructor answer key: lesson-02 to lesson-03.

### Prepare the workspace

> Prepare my learner project for Lesson 03. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-02 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

### Add the check pack

> Read learner-kit/lessons/03 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

### Build step 1

> For Lesson 03, continue in my learner project. Implement tenant-scoped runbook retrieval and context_tools in incident/context.py. Filter authorized sources before ranking and retain source IDs and versions. Use transparent lexical ranking for this lesson so I can inspect why a record was selected. Compare the same payments query for Astro and Locomotive. Keep the tool contract compatible with the existing executor and explain the returned evidence. Build to the interfaces the Lesson 03 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 03, continue in my learner project. Add select_context and connect it to the runtime as selection for the next model request. Preserve the instruction and original task, retain complete assistant/tool rounds within the configured allowance, and keep the full run history separately. Reject a task that cannot fit. Demonstrate a reduced conversation with no orphaned tool-call IDs and explain the evidence that was omitted. Build to the interfaces the Lesson 03 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 03, continue in my learner project. Implement EvidenceStore's versioned artifact operations. Scope identities by tenant, require the writer's expected version and reject stale updates in a transaction. Demonstrate version one, a conflicting update and a cross-tenant lookup. Preserve newer evidence rather than automatically overwriting it after a conflict. Show how a caller should inspect and reconcile the current artifact before retrying. Build to the interfaces the Lesson 03 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 03, continue in my learner project. Add expiring tenant-scoped memory and make the Session 03 check pack pass. Compare memory with versioned artifacts and the current task history. Demonstrate expiration, provenance and access boundaries, then compare the investigation with full history and bounded context. Report the outcome as well as context size; do not call a smaller prompt an improvement if required evidence is lost. Build to the interfaces the Lesson 03 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 03 learner exercise in my existing project: Run the same retrieval for Astro and Locomotive, inspect source IDs, and attempt a stale artifact write. Build a long synthetic conversation and reduce max_chars while checking valid tool-call pairs. Compare the investigation outcome before and after context selection. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 03 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 3 only when the required capability is present. Run the full test suite, which includes the Lesson 03 check pack and every earlier lesson's tests, and then the Session 03 demonstration with python -m incident.lab 3, all unchanged and using the offline provider. Confirm that the passing count matches the one in the Lesson 03 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

### Review the result

> Review my completed Lesson 03 work against the Lesson 03 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

### Recover when no runbook matches

> I am working on Lesson 03. The symptom is: No runbook matches. Diagnostic focus: Inspect the tokenized query and the authorized source population. Recovery guidance: Use a diagnostic term from the fixture, then expand evaluation cases before changing ranking. Do not remove the tenant filter to obtain a result. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a provider rejects conversation history

> I am working on Lesson 03. The symptom is: A provider rejects conversation history. Diagnostic focus: Check that retained tool messages have their matching assistant calls. Recovery guidance: Run the complete-round test and restore the grouping logic before tuning the budget. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when an artifact update reports stale_artifact_version

> I am working on Lesson 03. The symptom is: An artifact update reports stale_artifact_version. Diagnostic focus: Another write has advanced the artifact version. Recovery guidance: Read the latest artifact, reconcile the content and submit the correct expected version. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when memory seems to disappear

> I am working on Lesson 03. The symptom is: Memory seems to disappear. Diagnostic focus: Check TTL and tenant identity. Recovery guidance: Use a non-expired test value in the same tenant. Treat expiry as intended retention behaviour rather than bypassing it. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 04. Build the agent evaluation harness

Course kit: learner-kit/lessons/04. Instructor answer key: lesson-03 to lesson-04.

### Prepare the workspace

> Prepare my learner project for Lesson 04. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-03 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

### Add the check pack

> Read learner-kit/lessons/04 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

### Build step 1

> For Lesson 04, continue in my learner project. Add the given versioned evaluation cases to incident/evaluate.py unchanged. They cover supported diagnoses, missing evidence, ambiguity and another tenant, with explicit expected outcomes and development versus held-out partitions. Record dataset identity. Explain each case before running the agent. Do not change expected answers simply to make the current implementation pass. Build to the interfaces the Lesson 04 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 04, continue in my learner project. Implement separate outcome, evidence and tool-policy checks in grade. Demonstrate rejection of a plausible but wrong diagnosis. Check the offline provider's missing-evidence behaviour, then replace MockProvider with the given Lesson 04 version and explain how it stops a generic runbook from becoming proof of an incident cause. Preserve the original test expectations and show the regression evidence. Build to the interfaces the Lesson 04 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 04, continue in my learner project. Implement repeated evaluation with fresh execution context per trial, per-case result rows, dataset identity, selected partition, quality, usage and latency measurements. Keep live cost unavailable when pricing is missing, and clearly label offline fixture usage. Run two trials on the held-out partition and show the four underlying rows, including failures rather than only a favourable aggregate. Build to the interfaces the Lesson 04 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 04, continue in my learner project. Implement paired human-versus-judge agreement checks and the optional model_judge interface. Validate judge output, treat the agent answer as untrusted grading input and expose disagreements for human review. Make the Session 04 check pack pass using its offline calibration examples. Explain what is verified locally and what would still require a calibrated live judge and authorized provider access. Build to the interfaces the Lesson 04 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 04 learner exercise in my existing project: Add one unsupported-answer case and one tool-policy violation to a local test. Verify that the relevant check fails. Run two repeated trials on the held-out partition and locate every per-case result. Use the calibration example to explain why the flagged disagreement needs human review. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 04 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 4 only when the required capability is present. Run the full test suite, which includes the Lesson 04 check pack and every earlier lesson's tests, and then the Session 04 demonstration with python -m incident.lab 4, all unchanged and using the offline provider. Confirm that the passing count matches the one in the Lesson 04 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

### Review the result

> Review my completed Lesson 04 work against the Lesson 04 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

### Recover when a comparison improves after changing the cases

> I am working on Lesson 04. The symptom is: A comparison improves after changing the cases. Diagnostic focus: The dataset hash or partition differs. Recovery guidance: Restore the same dataset and compare like-for-like before attributing an improvement to the implementation. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when live cost appears unavailable

> I am working on Lesson 04. The symptom is: Live cost appears unavailable. Diagnostic focus: Input and output pricing rates are not configured. Recovery guidance: Provide explicit current rates in the environment and rerun. Keep cost unavailable until then. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when one live trial passes and another fails

> I am working on Lesson 04. The symptom is: One live trial passes and another fails. Diagnostic focus: Inspect outcome variation and the individual traces. Recovery guidance: Increase representative trials and investigate the failure mode rather than selecting only a favourable run. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the judge disagrees with an obvious check

> I am working on Lesson 04. The symptom is: The judge disagrees with an obvious check. Diagnostic focus: The rubric, human label or judge may be wrong. Recovery guidance: Review the example manually. Keep deterministic permission and schema checks authoritative for those properties. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 05. Checkpoints, recovery and human approval

Course kit: learner-kit/lessons/05. Instructor answer key: lesson-04 to lesson-05.

### Prepare the workspace

> Prepare my learner project for Lesson 05. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-04 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

### Add the check pack

> Read learner-kit/lessons/05 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

### Build step 1

> For Lesson 05, continue in my learner project. Implement RunStore in incident/durable.py so it persists and reconstructs the current runtime state under tenant and run ID. Preserve messages, pending calls, usage counters and control state. Use a persistent local database for restart checks. Show which data must survive a crash before a tool observation is recorded, and demonstrate that another tenant cannot load the run. Build to the interfaces the Lesson 05 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 05, continue in my learner project. Implement durable approval decisions with exact action keys, expiry and denial. Reach the waiting state using the clearly labelled remediation fixture, with no real external action. Show the exact proposed tool and arguments. Keep the human decision separate from execution: do not approve on my behalf while preparing the demonstration. Explain how the stored decision is checked again at resume time. Build to the interfaces the Lesson 05 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 05, continue in my learner project. Implement resume_run using the stored pending call and the same run_agent loop. Refresh currently valid approvals, reject denied or cancelled work and use the local effect ledger to reconcile a replay. Demonstrate why recovery consults durable application evidence rather than asking a model whether an earlier write succeeded. Preserve the original tenant and action boundaries. Build to the interfaces the Lesson 05 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 05, continue in my learner project. Make the Session 05 check pack pass, including its crash-injection demonstration. Simulate worker loss after a committed mock effect but before the result checkpoint, reopen the database and resume. Prove that there is one effect. Also demonstrate expired and denied approvals. Separate this automated fixture test from my manually controlled demonstration, and explain why the local transaction does not guarantee exactly-once behaviour for arbitrary remote APIs. Build to the interfaces the Lesson 05 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 05 learner exercise in my existing project: Run the crash-after-effect demonstration, then inspect the stored snapshot and effect count. Repeat with an expired approval and a denied proposal. Change the incident arguments and verify that the earlier approval does not authorize the new action. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 05 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 5 only when the required capability is present. Run the full test suite, which includes the Lesson 05 check pack and every earlier lesson's tests, and then the Session 05 demonstration with python -m incident.lab 5, all unchanged and using the offline provider. Confirm that the passing count matches the one in the Lesson 05 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

### Review the result

> Review my completed Lesson 05 work against the Lesson 05 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

### Recover when resume still waits after approval

> I am working on Lesson 05. The symptom is: Resume still waits after approval. Diagnostic focus: Check expiry, tenant, run ID and the action key against the pending arguments. Recovery guidance: Review the current proposal and issue a fresh, exact decision if appropriate. Do not copy an old approval flag. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a restart loses the run

> I am working on Lesson 05. The symptom is: A restart loses the run. Diagnostic focus: The store may have used :memory: or a temporary directory that was removed. Recovery guidance: Use the same persistent database path for both processes. Temporary demo directories are intentionally cleaned up after the assertion. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when two effects appear

> I am working on Lesson 05. The symptom is: Two effects appear. Diagnostic focus: The effect and idempotency record may no longer share a transaction, or the action key changed. Recovery guidance: Restore the transaction boundary and canonical key, then rerun the crash test. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a remote effect cannot be reconciled

> I am working on Lesson 05. The symptom is: A remote effect cannot be reconciled. Diagnostic focus: The external receiver does not provide durable idempotency evidence. Recovery guidance: Stop automatic replay and implement explicit reconciliation. Do not infer success from the model's narrative. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 06. Supervisor, subagents and parallel coordination

Course kit: learner-kit/lessons/06. Instructor answer key: lesson-05 to lesson-06.

### Prepare the workspace

> Prepare my learner project for Lesson 06. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-05 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

### Add the check pack

> Read learner-kit/lessons/06 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

### Build step 1

> For Lesson 06, continue in my learner project. Implement the bounded delegate schema, the given offline planning fixture, SupervisorProvider, and the delegate method in incident/supervisor.py. Accept only known roles, stable task IDs and bounded objectives. Map each role to a fixed tool set, refuse capabilities the parent lacks, reuse identical contracts and reject a changed objective under the same task ID. Give each child a new run ID, the parent's ID, only its role's tools and no approvals. Label offline planning separately from live model planning. Build to the interfaces the Lesson 06 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 06, continue in my learner project. Implement shared budget reservation and settlement with depth, agent-count and token limits. Reserve before starting a child, give it bounded limits, settle from reported usage and charge the full reservation when usage is missing. Demonstrate a plan that exceeds the agent-count allowance, preserving completed evidence and reporting the incomplete result honestly. Note that the parent's own usage is outside this pool. Build to the interfaces the Lesson 06 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 06, continue in my learner project. Implement WorkItem and schedule in incident/coordination.py. Reject duplicate IDs, unknown dependencies and cycles before launching work, respect the concurrency limit, block dependants of failed work, and at the deadline keep completed results, cancel and await the rest and report partial status. Add an optional batch hook to the runtime and a supervisor adapter that sends pending delegate calls through the scheduler without bypassing delegate's checks. Compare sequential and parallel runs with the same injected latency. Build to the interfaces the Lesson 06 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 06, continue in my learner project. Implement typed reply correlation and bounded producer-reviewer coordination in incident/coordination.py. Require matching correlation, task and artifact identity and the next version. Give one component ownership of saving the reviewed artifact and escalate review that does not converge within its round limit, keeping the history. Make the Session 06 check pack pass, including a deadline-cancelled worker, a stale reply and a reviewer that never accepts. Build to the interfaces the Lesson 06 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 06 learner exercise in my existing project: Reduce max_agents to one, request a log worker from a parent with only runbook access, and reuse a task ID with a changed objective. Then schedule two independent tasks and one dependent task, inject a slow worker and a failed predecessor, and submit a stale reply. Explain each result and compare the two-worker run with the single-agent baseline. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 06 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 6 only when the required capability is present. Run the full test suite, which includes the Lesson 06 check pack and every earlier lesson's tests, and then the Session 06 demonstration with python -m incident.lab 6, all unchanged and using the offline provider. Confirm that the passing count matches the one in the Lesson 06 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

### Review the result

> Review my completed Lesson 06 work against the Lesson 06 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

### Recover when delegation fails before a child starts

> I am working on Lesson 06. The symptom is: Delegation fails before a child starts. Diagnostic focus: Read the code: invalid_delegation, task_id_conflict, child_privilege_escalation or delegation_budget each name a different check. Recovery guidance: Use a bounded objective, a fresh task ID for new work and an allowance that fits the plan. Keep the permission check intact. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the parent declares success with one failed child

> I am working on Lesson 06. The symptom is: The parent declares success with one failed child. Diagnostic focus: The aggregation may ignore failed or missing observations. Recovery guidance: Keep partial evidence but report insufficient_evidence unless every delegated outcome succeeded. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the scheduler appears to hang

> I am working on Lesson 06. The symptom is: The scheduler appears to hang. Diagnostic focus: Check for a cycle, an unknown dependency or a runner that ignores cancellation. Recovery guidance: Validate the graph first and reproduce with a small asynchronous fixture. Keep the deadline and the await after cancellation. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when parallel execution is not faster

> I am working on Lesson 06. The symptom is: Parallel execution is not faster. Diagnostic focus: The batch hook may be disabled, the work CPU-bound, or the fixture short of independent waiting time. Recovery guidance: Confirm both runs use the same injected latency and that parallel mode uses the batch adapter. Record the result honestly; a slower multi-agent run is a valid finding. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 07. A2A across independent agent services

Course kit: learner-kit/lessons/07. Instructor answer key: lesson-06 to lesson-07.

### Prepare the workspace

> Prepare my learner project for Lesson 07. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-06 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

### Add the check pack

> Read learner-kit/lessons/07 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

### Build step 1

> For Lesson 07, continue in my learner project. Create the independent runbook specialist in incident/a2a_service.py with the pinned A2A SDK. Advertise the expected skill, interface, protocol and streaming capability through an Agent Card. Enforce the local teaching bearer credential at the endpoint and keep the service read-only and tenant-scoped. Explain what the card advertises, what application code actually enforces, and why this shared credential is temporary. Build to the interfaces the Lesson 07 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 07, continue in my learner project. Implement SpecialistExecutor's task lifecycle using the SDK's event flow. Enqueue the initial task before status updates, run the existing agent loop with runbook-only access, publish evidence as an artifact and report the correct terminal state. Add the deterministic slow-task fixture for cancellation. Demonstrate incomplete execution without manufacturing a successful answer. Build to the interfaces the Lesson 07 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 07, continue in my learner project. Implement the platform-facing RemoteSpecialist adapter in incident/a2a_client.py. Check the allowed tenant, discover the expected capability, consume streamed artifacts and status, and normalize a completed result into the platform contract. Reject an incomplete stream. Show the evidence and remote run identifier, and explain what must be retained for later reconciliation. Build to the interfaces the Lesson 07 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 07, continue in my learner project. Make the Session 07 check pack pass with the real local HTTP demonstration, using the given service launcher for cleanup. Show discovery, streamed progress and evidence, rejection of an unauthenticated request, and confirmed cancellation of a slow remote task. Keep third-party services and live model calls out of this local check. Explain why a disconnected client is not proof that remote work has stopped. Build to the interfaces the Lesson 07 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 07 learner exercise in my existing project: Run the local service separately, fetch its Agent Card and call the client adapter. Try a missing bearer credential, an unsupported skill declaration and a deliberately slow task. Record the distinction between authentication failure, capability mismatch, incomplete streaming and confirmed cancellation. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 07 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 7 only when the required capability is present. Run the full test suite, which includes the Lesson 07 check pack and every earlier lesson's tests, and then the Session 07 demonstration with python -m incident.lab 7, all unchanged and using the offline provider. Confirm that the passing count matches the one in the Lesson 07 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

### Review the result

> Review my completed Lesson 07 work against the Lesson 07 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

### Recover when an old tutorial's types or imports fail

> I am working on Lesson 07. The symptom is: An old tutorial's types or imports fail. Diagnostic focus: Check whether it targets A2A 0.3 rather than the pinned 1.1.2 SDK and 1.0 protocol. Recovery guidance: Use the repository's protobuf request types, factory API and generated routes. Restore the lock file before debugging application logic. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the server rejects a status event

> I am working on Lesson 07. The symptom is: The server rejects a status event. Diagnostic focus: A Task may not have been enqueued before the status update. Recovery guidance: Restore the initial Task event and rerun the lifecycle test. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the stream ends with no complete answer

> I am working on Lesson 07. The symptom is: The stream ends with no complete answer. Diagnostic focus: Inspect terminal status and whether an artifact was received. Recovery guidance: Report incomplete_remote_task and reconcile by task ID. Do not treat a disconnected stream as success. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a local port is already occupied

> I am working on Lesson 07. The symptom is: A local port is already occupied. Diagnostic focus: Another process is using the fixed manual-demo port. Recovery guidance: Use the ephemeral-port lab helper or choose a different explicit loopback port and update the advertised base URL. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 08. Platform core, agent registry and console

Course kit: learner-kit/lessons/08. Instructor answer key: lesson-07 to lesson-08.

### Prepare the workspace

> Prepare my learner project for Lesson 08. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-07 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

### Add the check pack

> Read learner-kit/lessons/08 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

### Build step 1

> For Lesson 08, continue in my learner project. Add an agent registry in incident/registry.py on the platform's SQLite file. Validate each definition against a strict schema, require known tools, store a SHA-256 content hash and reject different content under an existing version. Track one active version per agent, allow activating any non-retired version and refuse to retire the active one. Seed single, team and remediator at version 1. Show the rejection codes for an unknown field, an unknown tool and an in-place rewrite. Build to the interfaces the Lesson 08 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 08, continue in my learner project. Register remote A2A agents by pinning the SHA-256 of their Agent Card, and refuse a changed card unless an explicit reviewed acceptance is given. Add discovery by skill across active local agents and pinned remote agents. Make the A2A client check the fetched card against the pin before creating a client, and register the specialist at startup when a remote URL is configured. Demonstrate discovery for the runbooks skill and the refusal of a modified card. Build to the interfaces the Lesson 08 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 08, continue in my learner project. Build the platform core in incident/platform.py and the run API in incident/api.py. Submission resolves the requested or active definition, refuses retired versions, requires an operator for the remediator, builds the context in application code and saves the queued run with the resolved definition before launch. Claim a durable lease per run. Expose submit, list, inspect, cancel, decision and resume bound to the authenticated tenant, with 404 for another tenant's run and a conflict for a stale action key. Keep every handler asynchronous, because workers and handlers share one SQLite connection. Show both configurations completing with their recorded version and hash. Build to the interfaces the Lesson 08 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 08, continue in my learner project. Serve a platform console at /console as a static HTML shell with vanilla ES modules, under a strict same-origin Content-Security-Policy with no inline or external scripts. Render every API value as text through a small element helper, never as HTML. Add Overview with the platform map from a blueprint module, Registry, Runs with run detail, and Approvals. Scope views to the signed-in identity and show operator controls only to operators while the API still enforces them. Show me the response headers and the check for HTML injection sinks. Build to the interfaces the Lesson 08 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 08 learner exercise in my existing project: Start the platform API on loopback with the offline provider and a temporary database, and give me the console address. I will sign in as demo-astro, submit INC-001 with single and team, and compare the two run details. As demo-locomotive I will confirm that the Astro runs are absent. As demo-operator I will compare the Registry and Approvals views with the analyst's, submit the remediator and decide the pending action myself. Then run a registry version experiment: register single version 2 with a smaller context budget, attempt to rewrite version 1, let me activate version 2 as the operator, submit a run, retire version 1 and try to run it. Confirm that the older run still records version 1 and its hash. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 08 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 8 only when the required capability is present. Run the full test suite, which includes the Lesson 08 check pack and every earlier lesson's tests, and then the Session 08 demonstration with python -m incident.lab 8, all unchanged and using the offline provider. Confirm that the passing count matches the one in the Lesson 08 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

### Review the result

> Review my completed Lesson 08 work against the Lesson 08 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

### Recover when the console loads but stays blank

> I am working on Lesson 08. The symptom is: The console loads but stays blank. Diagnostic focus: Look for Content-Security-Policy violations in the browser developer console: an inline script, a script from another origin, or a page opened as a local file instead of from /console. Recovery guidance: Serve the console from the platform on loopback and keep all scripts as same-origin modules. Do not add unsafe-inline or external sources to the policy. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when submitting a run returns 400

> I am working on Lesson 08. The symptom is: Submitting a run returns 400. Diagnostic focus: Read the error code. unknown_agent, unknown_agent_version and retired_version come from the registry lifecycle; the database may hold an earlier experiment. Recovery guidance: List the agent's versions, states and active version. Activate a non-retired version or register a new one; never edit a stored definition in place. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the team run fails with agent_card_changed

> I am working on Lesson 08. The symptom is: The team run fails with agent_card_changed. Diagnostic focus: The specialist's current Agent Card no longer matches the pinned hash, often after a restart with a different base URL or card content. Recovery guidance: Compare the pinned and fetched cards and explain the difference. Accept the change explicitly only if it is expected; never remove the runtime pin check. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when tests fail intermittently after adding an endpoint

> I am working on Lesson 08. The symptom is: Tests fail intermittently after adding an endpoint. Diagnostic focus: A synchronous handler runs in the framework's thread pool and shares the SQLite connection with running workers; test_api_handlers_run_on_the_event_loop names it. Recovery guidance: Declare the handler asynchronous. Do not delete the test or open an unsynchronised connection per request. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 09. MCP tool gateway and policy

Course kit: learner-kit/lessons/09. Instructor answer key: lesson-08 to lesson-09.

### Prepare the workspace

> Prepare my learner project for Lesson 09. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-08 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

### Add the check pack

> Read learner-kit/lessons/09 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

### Build step 1

> For Lesson 09, continue in my learner project. Extend the registry with tool-server records whose manifest names the transport, the tenants served and each tool's risk as read or write. Validate the name and manifest shape, reject a changed manifest under an existing name, and add a catalog from tool to server, risk, tenants and status. Seed the MCP read server and the local write-action server. Show the catalog and one rejected manifest. Build to the interfaces the Lesson 09 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 09, continue in my learner project. Create a ToolGateway with an explicit policy: a per-run call budget, a maximum argument size and the roles allowed to use write tools. Check each call in a fixed order, returning a stable reason code for every denial before any upstream connection. Audit every decision with an argument hash, not the raw arguments. Wrap the existing executor for allowed calls so validation, approval and effects stay unchanged. Show one allowed call and three denials with their audit rows. Build to the interfaces the Lesson 09 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 09, continue in my learner project. Replace per-run MCP clients with one upstream session per server and tenant in the gateway, created under a lock and shared by all workers. Open and close each client in a single owner task so its cancel scopes are entered and exited by the same task. Stop waiting callers from cancelling the shared session, drop a session after an upstream error and close all sessions at shutdown. Show the launch count after several runs. Build to the interfaces the Lesson 09 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 09, continue in my learner project. Pin each MCP tool definition by hash on the gateway's first connection to a server, and quarantine the server if a later connection reports different definitions. Deny every tool on a quarantined server before any upstream call. Route single runs, team workers and remediation through the gateway, and add the Gateway console view. Show a changed-definition fixture and the resulting quarantine. Build to the interfaces the Lesson 09 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 09 learner exercise in my existing project: Create a second gateway over the same registry with a lower per-run call budget and a tighter argument limit, leaving the platform's policy unchanged. Predict which calls of one investigation and three hand-written calls will be denied, and with which reason codes. Run them, compare the audit rows with your prediction and view the platform's audit in the console Gateway view. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 09 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 9 only when the required capability is present. Run the full test suite, which includes the Lesson 09 check pack and every earlier lesson's tests, and then the Session 09 demonstration with python -m incident.lab 9, all unchanged and using the offline provider. Confirm that the passing count matches the one in the Lesson 09 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

### Review the result

> Review my completed Lesson 09 work against the Lesson 09 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

### Recover when the session count is higher than one per tenant

> I am working on Lesson 09. The symptom is: The session count is higher than one per tenant. Diagnostic focus: A run path still creates its own MCP client or tool executor, the supervisor ignores the injected gateway, or sessions are created outside the gateway lock. Recovery guidance: Pass the platform's gateway to every run kind and to the supervisor, and create sessions only inside the locked session method. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when shutdown hangs or reports a cancel scope exited in a different task

> I am working on Lesson 09. The symptom is: Shutdown hangs or reports a cancel scope exited in a different task. Diagnostic focus: The MCP client is opened in one task and closed in another, or a waiting caller cancels the shared session future. Recovery guidance: Keep open, listing, pinning and close in one owner task per session, signal it with a stop event, shield the shared future and close the platform from the API lifespan. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when every call to incident-tools is denied as tool_definition_changed

> I am working on Lesson 09. The symptom is: Every call to incident-tools is denied as tool_definition_changed. Diagnostic focus: The server was quarantined earlier, often by the changed-definition fixture writing to the same platform database. Recovery guidance: Find which definition changed and why. For a local experiment use a fresh database. Do not overwrite the pins or weaken the quarantine check to get a pass. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a normal investigation is denied by gateway policy

> I am working on Lesson 09. The symptom is: A normal investigation is denied by gateway policy. Diagnostic focus: Read the audit reason: tool_call_budget counts allowed calls per run ID, argument_policy measures serialized arguments and not_granted means the agent definition lacks the tool. Recovery guidance: Change the policy or agent definition deliberately with a recorded reason, or fix the caller. Do not bypass the gateway. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 10. Agent identity, delegated credentials and containment

Course kit: learner-kit/lessons/10. Instructor answer key: lesson-09 to lesson-10.

### Prepare the workspace

> Prepare my learner project for Lesson 10. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-09 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

### Add the check pack

> Read learner-kit/lessons/10 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

### Build step 1

> For Lesson 10, continue in my learner project. Add a token issuer that signs short-lived JWT-shaped tokens with a configured development key and verifies signature, issuer, expiry and audience with distinct reasons and a constant-time comparison. Let the API exchange a demo credential for a signed platform token and record the signed-in subject on each run. Show tampered, expired and wrong-audience tokens being rejected, and explain why a shared key is a teaching simplification. Build to the interfaces the Lesson 10 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 10, continue in my learner project. Add delegated credentials. Mint a short-lived tool-gateway token for each executing run, with the user as subject, the agent definition as actor and the run's allowed tools as scope. Give each local or remote child a token that only narrows the parent's scope and extends the actor chain. Record grants for inspection, keep token values out of run state, and revoke a run's tokens and its children's when the run ends. Show the three actor chains of a team run. Build to the interfaces the Lesson 10 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 10, continue in my learner project. Enforce delegated credentials at the tool gateway and the A2A specialist. At the gateway, deny calls without a delegated token, verify it for the gateway audience, and deny a tenant mismatch or a tool outside its scope, auditing each reason. At the specialist, replace the static shared token with a delegated token for its own audience and derive tenant and subject from the verified claims. Show a missing credential, a cross-tenant call and a wrong-audience request being refused. Build to the interfaces the Lesson 10 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 10, continue in my learner project. Add a credential store that keeps secrets under secret:// references, releases a value only to a named consumer, audits every release and denial, and wraps values so they cannot be printed or serialized. Lease the model key to the provider adapter and let definitions name credentials only by reference. Keep the hostile-provider, path, endpoint, citation and redaction checks working. Show a denied lease and zero injected effects, and do not describe the store as a vault. Build to the interfaces the Lesson 10 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 10 learner exercise in my existing project: Run the Session 10 lab and read each rejection. Then present a token signed with another key to the API, request a child tool the parent lacks, lease the model key as the wrong consumer, and add a symlink escape or lookalike host. Record the control, reason and audit row or grant for each. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 10 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 10 only when the required capability is present. Run the full test suite, which includes the Lesson 10 check pack and every earlier lesson's tests, and then the Session 10 demonstration with python -m incident.lab 10, all unchanged and using the offline provider. Confirm that the passing count matches the one in the Lesson 10 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

### Review the result

> Review my completed Lesson 10 work against the Lesson 10 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

### Recover when the a2a specialist rejects the delegated token

> I am working on Lesson 10. The symptom is: The A2A specialist rejects the delegated token. Diagnostic focus: bad_signature usually means the two processes use different PLATFORM_SIGNING_KEY values; wrong_audience means the remote grant was minted for the tool gateway. Recovery guidance: Configure the same development key for both processes and mint the remote grant for the specialist's audience. Do not relax signature or audience checks. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when gateway calls fail with no_delegated_credential

> I am working on Lesson 10. The symptom is: Gateway calls fail with no_delegated_credential. Diagnostic focus: The run may not have been executed through the platform, a child run may have been created without the grant hook, or tokens may be revoked before children finish. Recovery guidance: Mint the run token before any tool call, grant every child through the supervisor's grant hook and revoke only in the finally block. Keep the gateway's credential check. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a live provider is blocked by endpoint policy or the credential store

> I am working on Lesson 10. The symptom is: A live provider is blocked by endpoint policy or the credential store. Diagnostic focus: egress_host_denied means the host is not in MODEL_ALLOWED_HOSTS; secret_access_denied means the model key is missing or leased by a consumer other than model-adapter. Recovery guidance: Explicitly configure the trusted provider host and the model key. Do not accept a host from retrieved content, disable TLS verification or put a key in a definition. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when someone calls these controls a production identity system or sandbox

> I am working on Lesson 10. The symptom is: Someone calls these controls a production identity system or sandbox. Diagnostic focus: Teaching controls are being confused with an identity provider, a managed vault and OS isolation. Recovery guidance: State the boundaries: shared HMAC key, in-memory store, loopback-only demo credentials and path checks rather than an execution sandbox. Name the Session 11 restricted container as a further layer. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 11. Operating and releasing agent platforms

Course kit: learner-kit/lessons/11. Instructor answer key: lesson-10 to lesson-11.

### Prepare the workspace

> Prepare my learner project for Lesson 11. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-10 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

### Add the check pack

> Read learner-kit/lessons/11 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

### Build step 1

> For Lesson 11, continue in my learner project. Implement bounded admission and active-worker controls in incident/operations.py and connect them to Platform. Distinguish queue capacity from per-tenant arrival limits and active concurrency, record rejected submissions and map them to distinct API responses. Release admission, leases and tasks on success, failure and cancellation. Make the supervisor reserve its own allowance from the shared team budget. Show excess-work rejection and prove that cancellation restores capacity. Build to the interfaces the Lesson 11 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 11, continue in my learner project. Implement the tenant-scoped parent-and-child trace, its escaped HTML view and an API endpoint that returns it only to the owning tenant. Run the hybrid investigation through the registry-pinned remote specialist, the tool gateway and delegated credentials. Show the three correlated run nodes, their roles and events, and usage counted once per run. Explain that this is the application's trace view and identify any external observability integration that remains untested. Build to the interfaces the Lesson 11 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 11, continue in my learner project. Implement release_gate and evaluate_platform using the actual immutable registry configurations, and add a release log that records every decision with its checks and summaries whether or not the candidate is activated. Compare the same dataset and partition, retain per-case rows and enforce explicit quality, latency and usage limits. Evaluate a candidate context policy and demonstrate that a degraded or mismatched report is rejected and recorded. Explain which thresholds are teaching values. Build to the interfaces the Lesson 11 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 11, continue in my learner project. Complete the Session 11 end-to-end, overload, rollout and rollback demonstration. Show the correlated trace, accepted and rejected load, a passing candidate that is recorded and activated, and the return to the previous version. Show the release in the console Operations view. Inspect the existing restricted container recipe and run it only if the environment supports it. Report its temporary-state limitation and any untested deployment behaviour. Build to the interfaces the Lesson 11 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 11 learner exercise in my existing project: Run the hybrid end-to-end investigation and inspect its three-node trace in the API and the console. Lower queue capacity, send excess work and verify rejection and cleanup. Evaluate a deliberately worse candidate and show that the release gate blocks it and the release log records the rejection. Then activate a passing version and roll back. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 11 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 11 only when the required capability is present. Run the full test suite, which includes the Lesson 11 check pack and every earlier lesson's tests, and then the Session 11 demonstration with python -m incident.lab 11, all unchanged and using the offline provider. Confirm that the passing count matches the one in the Lesson 11 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

### Review the result

> Review my completed Lesson 11 work against the Lesson 11 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

### Recover when the parent completes but a trace child is missing

> I am working on Lesson 11. The symptom is: The parent completes but a trace child is missing. Diagnostic focus: Child persistence or parent correlation may have been omitted, or the remote child was saved under another tenant. Recovery guidance: Inspect the child run IDs in the delegation summary, confirm each child context carries the parent ID and tenant, and save completed child snapshots before building the trace. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when capacity remains full after cancellation

> I am working on Lesson 11. The symptom is: Capacity remains full after cancellation. Diagnostic focus: The worker cleanup may not leave admission, release its lease or remove the task. Recovery guidance: Run the cancellation regression test and keep all three cleanup actions in the worker's finally block for both waiting and active work. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the operations view shows no release decisions

> I am working on Lesson 11. The symptom is: The Operations view shows no release decisions. Diagnostic focus: The gate may have been evaluated without recording the decision, or the release log may use a different database from the API process. Recovery guidance: Record every decision, including rejections, in the platform's release log, confirm the API and the demo share the platform database, and check the operations endpoint before the console. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when container replacement loses sandbox state

> I am working on Lesson 11. The symptom is: Container replacement loses sandbox state. Diagnostic focus: The supplied restricted Compose recipe uses tmpfs for the writable state directory. Recovery guidance: Use the local persistent SQLite demo for recovery exercises, or provision and test a persistent deployment volume before relying on container restart durability. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 12. Tune and present your agentic platform

Course kit: learner-kit/lessons/12. Instructor answer key: lesson-11 to lesson-12.

### Prepare the workspace

> Prepare my learner project for Lesson 12. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-11 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

### Add the check pack

> Read learner-kit/lessons/12 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

### Build step 1

> For Lesson 12, continue in my learner project. Review my working Session 11 platform and the Lesson 12 check pack. Help me state one bounded tuning hypothesis and identify the smallest change needed to test it, expressed as a new immutable registry version. Explain the given EfficientMockProvider, how the platform selects it from the definition's provider profile, and where early completion is safe or unsafe in these fixtures. Preserve the baseline and define the evidence that would justify adopting or rejecting my change before implementing it. Build to the interfaces the Lesson 12 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 12, continue in my learner project. Apply the selected tuning change as a new registry version. Evaluate before and after on the same cases, partitions and trial conditions, retaining failures and per-case rows. Use the actual platform path. Activate the candidate only if the release gate approves it, and record the decision in the release log either way. Keep fixture usage separate from live-model economics and preserve the original expected outcomes. Show the comparison, the recorded decision and its limitations. Build to the interfaces the Lesson 12 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 12, continue in my learner project. Help me evaluate caching or routing as a separate capstone experiment when relevant. Preserve tenant, configuration, input, schema and freshness boundaries in cache identity, and report cold and warm behaviour separately. Check uncertainty routing without assuming a cheaper provider is always adequate. Run the focused tests and explain the correctness risks and the evidence needed for a live deployment. Build to the interfaces the Lesson 12 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 12, continue in my learner project. Prepare a console demonstration of my completed platform and a concise evidence pack: the platform map, the registry with the released version, one end-to-end run with its trace, gateway audit and delegation chain, one permission or recovery failure case, and the recorded before-and-after release. Use actual code and recorded results, clearly identifying anything not demonstrated live. Ask me to explain the tradeoffs in my own words. Do not invent improvements or adopt a change whose evidence is inadequate. Build to the interfaces the Lesson 12 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 12 learner exercise in my existing project: Before class, select a small tuning intervention, apply it as a new registry version and generate a comparable before-and-after report with a recorded release decision. During class, present the working platform through its console and demonstrate one failure-control case. Explain the evidence, tradeoffs and adoption decision. Use the fixture experiment only as a rehearsal when live model access is unavailable. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 12 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 12 only when the required capability is present. Run the full test suite, which includes the Lesson 12 check pack and every earlier lesson's tests, and then the Session 12 demonstration with python -m incident.lab 12, all unchanged and using the offline provider. Confirm that the passing count matches the one in the Lesson 12 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

### Review the result

> Review my completed Lesson 12 work against the Lesson 12 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

### Recover when the demo fails during a presentation

> I am working on Lesson 12. The symptom is: The demo fails during a presentation. Diagnostic focus: Locate the failing checkpoint, service, console view or configuration and preserve the error evidence. Recovery guidance: Use the prepared completed reference snapshot, its console screenshots and the saved trace to continue the explanation. State which part was demonstrated live and which was shown from recorded evidence. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the console does not show the tuned version or its release

> I am working on Lesson 12. The symptom is: The console does not show the tuned version or its release. Diagnostic focus: The candidate may have been evaluated in a temporary database, as the lab does, rather than in the platform database the API reads, or it was recorded but not activated. Recovery guidance: Register, evaluate, activate and record the candidate against the platform database the console uses, then confirm the registry and operations endpoints before presenting. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a participant presents fixture usage as real savings

> Review my Lesson 12 presentation claims against the recorded comparison report and release log. Identify any synthetic fixture usage described as real model cost or savings. Correct those claims and label the measurement conditions clearly. Explain what live benchmark and pricing evidence would be needed to estimate actual cost. Preserve the recorded results and do not invent an improvement.

### Recover when there is not enough time for every individual presentation

> Help me organize Lesson 12 presentations within the existing 90-minute agenda. Ask for the cohort size if it is missing. Allocate the 35-to-70-minute presentation block using review groups or pre-recorded console demonstrations when necessary. Keep the remaining agenda timings and shared review criteria, give every participant a review opportunity and prepare a short plenary discussion. Show the proposed schedule and timing totals; no implementation changes are needed.
