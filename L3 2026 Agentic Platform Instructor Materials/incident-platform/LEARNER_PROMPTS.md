# Coding agent prompts for the course

Give your coding agent access to the reference repository and your learner project. Use the current prompts even when inspecting earlier code checkpoints. The agent handles environment setup, repository operations, execution and verification. You set scope, inspect code and decide whether the observed evidence meets the lesson criteria.

The reference implementation and its tests are unchanged. These prompts guide a learner implementation; a coding agent’s completion message is not proof that its result passed the checks. Use offline fixtures unless you deliberately configure and authorize a live integration.

## 01. Agent architecture and the ReAct runtime

Starting reference: lesson-00. Ending reference: lesson-01.

### Prepare the workspace

> Prepare my Python learner project for Lesson 01, starting from lesson-00. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

### Orient to the reference

> Compare my current project with lesson-00 and prepare a read-only view of lesson-01 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

### Build step 1

> For Lesson 01, continue in my learner project. Create the Context, Limits, Reply and Run contracts in incident/core.py. Separate application-owned tenant identity, permissions and run identifiers from model messages and results. Make run state serializable and give the runtime explicit step, token and time limits. Keep this step focused on the contracts; do not implement later platform features. Show the fields, their owners and one example of a value the model must not control. Use lesson-01 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 01, continue in my learner project. Implement the provider interface in incident/providers.py using the current core contracts. Add the deterministic offline provider and configurable OpenAI-compatible and Anthropic adapters. Normalize messages, tool calls, errors and usage into Reply. Use mock HTTP responses to check both adapter request shapes without paid calls. Explain how provider selection and secrets are configured without exposing credentials. Use lesson-01 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 01, continue in my learner project. Implement run_agent in incident/core.py and connect the synthetic readers in incident/fixtures.py. Preserve assistant tool-call IDs when appending observations, track pending calls before dispatch, and finish with a structured answer and observed evidence IDs. Use the existing provider interface. Show the complete model-to-tool-to-observation path for INC-001 and explain how the same loop can later support checkpointing. Use lesson-01 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 01, continue in my learner project. Review and enforce the runtime's step, token, elapsed-time and repeated-action guards. Complete the Session 01 lab runner and tests. Demonstrate the normal cited answer and deliberately trigger each limit using offline fixtures. Explain the approximate pre-dispatch token estimate and distinguish reported usage from configured cost. Show which guard caused each failure and why the run stopped. Use lesson-01 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 01 learner exercise in my existing project: Change Limits in a small local invocation to allow one step, then a tiny token budget, then a short deadline with a slow MockProvider. Predict and observe step_budget, token_budget and TimeoutError. Restore the normal limits and verify the cited happy-path answer. Keep your workflow baseline for comparison. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 01 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 1 only when the required capability is present. Run tests/test_lesson01.py, the Session 01 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

### Review the result

> Compare my completed Lesson 01 work with reference lesson-01. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

### Recover when live mode fails before a request

> I am working on Lesson 01. The symptom is: Live mode fails before a request. Diagnostic focus: Check MODEL_PROVIDER, MODEL_NAME and whether MODEL_API_KEY is set. Do not print the key. Recovery guidance: Switch to MODEL_PROVIDER=mock and rerun the demo. Configure the live adapter separately after class. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the final message cannot be parsed

> I am working on Lesson 01. The symptom is: The final message cannot be parsed. Diagnostic focus: The runtime expects a JSON answer with status, cause, summary and evidence. Recovery guidance: Inspect the normalized message in a debugger and compare it with MockProvider. Keep malformed-output tests separate from tool transport problems. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the lesson command says the checkpoint is too early

> I am working on Lesson 01. The symptom is: The lesson command says the checkpoint is too early. Diagnostic focus: incident/__init__.py still identifies the starting checkpoint. Recovery guidance: After completing the lesson changes, set LESSON to 1 or use the completed reference snapshot. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a native python package cannot load on macos

> I am working on Lesson 01. The symptom is: A native Python package cannot load on macOS. Diagnostic focus: A binary-wheel or local interpreter compatibility issue can occur before the course code runs. Recovery guidance: Use a compatible Python 3.12 installation or the tested Docker route described in the repository. Do not disable operating-system security protections. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 02. Reliable tools and MCP integration

Starting reference: lesson-01. Ending reference: lesson-02.

### Prepare the workspace

> Prepare my Python learner project for Lesson 02, starting from lesson-01. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

### Orient to the reference

> Compare my current project with lesson-01 and prepare a read-only view of lesson-02 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

### Build step 1

> For Lesson 02, continue in my learner project. Implement ToolExecutor in incident/tools.py. Check tool existence, application-owned capabilities and JSON arguments before dispatch. Reject unexpected tenant arguments and oversized results. Return structured errors that distinguish terminal failures from retryable read failures. Preserve the existing agent loop. Demonstrate malformed arguments and an unauthorized write proposal being rejected before a handler performs an effect. Use lesson-02 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 02, continue in my learner project. Add exact-action approval and idempotent mock remediation to ToolExecutor. Bind the action key to tenant, run, tool name and canonical arguments. Commit the local mock effect and its deduplication record atomically in SQLite. Test the same approved write after reopening the executor and test changed arguments against the original approval. Show that only one local effect exists, and explain the limit of this guarantee for external APIs. Use lesson-02 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 02, continue in my learner project. Implement the MCP server in incident/mcp_bridge.py with the pinned SDK. Expose the existing tenant-scoped log and runbook readers plus the runbook resource. Bind tenant identity in trusted launcher configuration, keep protocol stdout clean, and limit the server to the capabilities required by this lesson. Explain the host, client, server and resource roles before demonstrating discovery. Use lesson-02 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 02, continue in my learner project. Implement the MCP read adapter and connect it behind ToolExecutor. Use the real local stdio transport and the pinned SDK's result shapes. Complete the Session 02 lab and contract tests, show the negotiated protocol and discovered tools, and run the same investigation through the adapter. Confirm that transport discovery does not grant new permissions and show the unchanged cited outcome. Use lesson-02 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 02 learner exercise in my existing project: Add an unexpected tenant argument to a log request, call mock_remediate with a read-only Context, lower output_limit, and repeat an approved mock write after reopening the SQLite executor. Record the error category or replay behaviour for each case. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 02 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 2 only when the required capability is present. Run tests/test_lesson02.py, the Session 02 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

### Review the result

> Compare my completed Lesson 02 work with reference lesson-02. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

### Recover when mcp startup or parsing fails

> I am working on Lesson 02. The symptom is: MCP startup or parsing fails. Diagnostic focus: Look for debug output written to stdout or a process started from the wrong repository directory. Recovery guidance: Keep protocol stdout clean, use stderr logging and rerun the isolated stdio test. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when result-field attribute error

> I am working on Lesson 02. The symptom is: Result-field attribute error. Diagnostic focus: Compare the installed MCP version with the lock file and the result field names in the adapter. Recovery guidance: Restore the pinned Python 3.12 environment from the project lock file. Avoid mixing 1.x tutorial code with the 2.2.0 adapter. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when tool exists but returns permission_denied

> I am working on Lesson 02. The symptom is: Tool exists but returns permission_denied. Diagnostic focus: Inspect Context.allowed rather than the server's discovery list. Recovery guidance: Use the intended read-only investigator or construct an operator-owned context explicitly for the mock-approval exercise. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a changed schema breaks an integration

> I am working on Lesson 02. The symptom is: A changed schema breaks an integration. Diagnostic focus: The client-side tool contract and the discovered server contract differ. Recovery guidance: Pin the compatible server/client versions, update the adapter deliberately and rerun contract tests before using the changed tool. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 03. Context, retrieval and memory

Starting reference: lesson-02. Ending reference: lesson-03.

### Prepare the workspace

> Prepare my Python learner project for Lesson 03, starting from lesson-02. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

### Orient to the reference

> Compare my current project with lesson-02 and prepare a read-only view of lesson-03 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

### Build step 1

> For Lesson 03, continue in my learner project. Implement tenant-scoped runbook retrieval and context_tools in incident/context.py. Filter authorized sources before ranking and retain source IDs and versions. Use transparent lexical ranking for this lesson so I can inspect why a record was selected. Compare the same payments query for Acme and Globex. Keep the tool contract compatible with the existing executor and explain the returned evidence. Use lesson-03 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 03, continue in my learner project. Add select_context and connect it to the runtime as selection for the next model request. Preserve the instruction and original task, retain complete assistant/tool rounds within the configured allowance, and keep the full run history separately. Reject a task that cannot fit. Demonstrate a reduced conversation with no orphaned tool-call IDs and explain the evidence that was omitted. Use lesson-03 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 03, continue in my learner project. Implement EvidenceStore's versioned artifact operations. Scope identities by tenant, require the writer's expected version and reject stale updates in a transaction. Demonstrate version one, a conflicting update and a cross-tenant lookup. Preserve newer evidence rather than automatically overwriting it after a conflict. Show how a caller should inspect and reconcile the current artifact before retrying. Use lesson-03 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 03, continue in my learner project. Add expiring tenant-scoped memory and complete the Session 03 lab and tests. Compare memory with versioned artifacts and the current task history. Demonstrate expiration, provenance and access boundaries, then compare the investigation with full history and bounded context. Report the outcome as well as context size; do not call a smaller prompt an improvement if required evidence is lost. Use lesson-03 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 03 learner exercise in my existing project: Run the same retrieval for Acme and Globex, inspect source IDs, and attempt a stale artifact write. Build a long synthetic conversation and reduce max_chars while checking valid tool-call pairs. Compare the investigation outcome before and after context selection. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 03 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 3 only when the required capability is present. Run tests/test_lesson03.py, the Session 03 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

### Review the result

> Compare my completed Lesson 03 work with reference lesson-03. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

### Recover when no runbook matches

> I am working on Lesson 03. The symptom is: No runbook matches. Diagnostic focus: Inspect the tokenized query and the authorized source population. Recovery guidance: Use a diagnostic term from the fixture, then expand evaluation cases before changing ranking. Do not remove the tenant filter to obtain a result. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a provider rejects conversation history

> I am working on Lesson 03. The symptom is: A provider rejects conversation history. Diagnostic focus: Check that retained tool messages have their matching assistant calls. Recovery guidance: Run the complete-round test and restore the grouping logic before tuning the budget. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when an artifact update reports stale_artifact_version

> I am working on Lesson 03. The symptom is: An artifact update reports stale_artifact_version. Diagnostic focus: Another write has advanced the artifact version. Recovery guidance: Read the latest artifact, reconcile the content and submit the correct expected version. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when memory seems to disappear

> I am working on Lesson 03. The symptom is: Memory seems to disappear. Diagnostic focus: Check TTL and tenant identity. Recovery guidance: Use a non-expired test value in the same tenant. Treat expiry as intended retention behaviour rather than bypassing it. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 04. Build the agent evaluation harness

Starting reference: lesson-03. Ending reference: lesson-04.

### Prepare the workspace

> Prepare my Python learner project for Lesson 04, starting from lesson-03. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

### Orient to the reference

> Compare my current project with lesson-03 and prepare a read-only view of lesson-04 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

### Build step 1

> For Lesson 04, continue in my learner project. Create the versioned evaluation cases in incident/evaluate.py. Cover supported diagnoses, missing evidence, ambiguity and another tenant, with explicit expected outcomes and development versus held-out partitions. Preserve the supplied acceptance scenarios and record dataset identity. Explain each case before running the agent. Do not change expected answers simply to make the current implementation pass. Use lesson-04 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 04, continue in my learner project. Implement separate outcome, evidence and tool-policy checks in grade. Demonstrate rejection of a plausible but wrong diagnosis. Check the offline provider's missing-evidence behaviour and make the smallest required correction in incident/providers.py so a generic runbook does not become proof of an incident cause. Preserve the original test expectations and show the regression evidence. Use lesson-04 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 04, continue in my learner project. Implement repeated evaluation with fresh execution context per trial, per-case result rows, dataset identity, selected partition, quality, usage and latency measurements. Keep live cost unavailable when pricing is missing, and clearly label offline fixture usage. Run two trials on the held-out partition and show the four underlying rows, including failures rather than only a favourable aggregate. Use lesson-04 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 04, continue in my learner project. Implement paired human-versus-judge agreement checks and the optional model_judge interface. Validate judge output, treat the agent answer as untrusted grading input and expose disagreements for human review. Complete the Session 04 lab and tests using offline calibration examples. Explain what is verified locally and what would still require a calibrated live judge and authorized provider access. Use lesson-04 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 04 learner exercise in my existing project: Add one unsupported-answer case and one tool-policy violation to a local test. Verify that the relevant check fails. Run two repeated trials on the held-out partition and locate every per-case result. Use the calibration example to explain why the flagged disagreement needs human review. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 04 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 4 only when the required capability is present. Run tests/test_lesson04.py, the Session 04 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

### Review the result

> Compare my completed Lesson 04 work with reference lesson-04. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

### Recover when a comparison improves after changing the cases

> I am working on Lesson 04. The symptom is: A comparison improves after changing the cases. Diagnostic focus: The dataset hash or partition differs. Recovery guidance: Restore the same dataset and compare like-for-like before attributing an improvement to the implementation. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when live cost appears unavailable

> I am working on Lesson 04. The symptom is: Live cost appears unavailable. Diagnostic focus: Input and output pricing rates are not configured. Recovery guidance: Provide explicit current rates in the environment and rerun. Keep cost unavailable until then. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when one live trial passes and another fails

> I am working on Lesson 04. The symptom is: One live trial passes and another fails. Diagnostic focus: Inspect outcome variation and the individual traces. Recovery guidance: Increase representative trials and investigate the failure mode rather than selecting only a favourable run. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the judge disagrees with an obvious check

> I am working on Lesson 04. The symptom is: The judge disagrees with an obvious check. Diagnostic focus: The rubric, human label or judge may be wrong. Recovery guidance: Review the example manually. Keep deterministic permission and schema checks authoritative for those properties. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 05. Checkpoints, recovery and human approval

Starting reference: lesson-04. Ending reference: lesson-05.

### Prepare the workspace

> Prepare my Python learner project for Lesson 05, starting from lesson-04. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

### Orient to the reference

> Compare my current project with lesson-04 and prepare a read-only view of lesson-05 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

### Build step 1

> For Lesson 05, continue in my learner project. Implement RunStore in incident/durable.py so it persists and reconstructs the current runtime state under tenant and run ID. Preserve messages, pending calls, usage counters and control state. Use a persistent local database for restart checks. Show which data must survive a crash before a tool observation is recorded, and demonstrate that another tenant cannot load the run. Use lesson-05 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 05, continue in my learner project. Implement durable approval decisions with exact action keys, expiry and denial. Reach the waiting state using the clearly labelled remediation fixture, with no real external action. Show the exact proposed tool and arguments. Keep the human decision separate from execution: do not approve on my behalf while preparing the demonstration. Explain how the stored decision is checked again at resume time. Use lesson-05 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 05, continue in my learner project. Implement resume_run using the stored pending call and the same run_agent loop. Refresh currently valid approvals, reject denied or cancelled work and use the local effect ledger to reconcile a replay. Demonstrate why recovery consults durable application evidence rather than asking a model whether an earlier write succeeded. Preserve the original tenant and action boundaries. Use lesson-05 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 05, continue in my learner project. Complete the Session 05 crash-injection demonstration and tests. Simulate worker loss after a committed mock effect but before the result checkpoint, reopen the database and resume. Prove that there is one effect. Also demonstrate expired and denied approvals. Separate this automated fixture test from my manually controlled demonstration, and explain why the local transaction does not guarantee exactly-once behaviour for arbitrary remote APIs. Use lesson-05 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 05 learner exercise in my existing project: Run the crash-after-effect demonstration, then inspect the stored snapshot and effect count. Repeat with an expired approval and a denied proposal. Change the incident arguments and verify that the earlier approval does not authorize the new action. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 05 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 5 only when the required capability is present. Run tests/test_lesson05.py, the Session 05 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

### Review the result

> Compare my completed Lesson 05 work with reference lesson-05. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

### Recover when resume still waits after approval

> I am working on Lesson 05. The symptom is: Resume still waits after approval. Diagnostic focus: Check expiry, tenant, run ID and the action key against the pending arguments. Recovery guidance: Review the current proposal and issue a fresh, exact decision if appropriate. Do not copy an old approval flag. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a restart loses the run

> I am working on Lesson 05. The symptom is: A restart loses the run. Diagnostic focus: The store may have used :memory: or a temporary directory that was removed. Recovery guidance: Use the same persistent database path for both processes. Temporary demo directories are intentionally cleaned up after the assertion. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when two effects appear

> I am working on Lesson 05. The symptom is: Two effects appear. Diagnostic focus: The effect and idempotency record may no longer share a transaction, or the action key changed. Recovery guidance: Restore the transaction boundary and canonical key, then rerun the crash test. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a remote effect cannot be reconciled

> I am working on Lesson 05. The symptom is: A remote effect cannot be reconciled. Diagnostic focus: The external receiver does not provide durable idempotency evidence. Recovery guidance: Stop automatic replay and implement explicit reconciliation. Do not infer success from the model's narrative. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 06. Supervisor and scoped subagents

Starting reference: lesson-05. Ending reference: lesson-06.

### Prepare the workspace

> Prepare my Python learner project for Lesson 06, starting from lesson-05. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

### Orient to the reference

> Compare my current project with lesson-05 and prepare a read-only view of lesson-06 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

### Build step 1

> For Lesson 06, continue in my learner project. Define the bounded delegate schema and supervisor planning fixture in incident/supervisor.py. Accept only known worker roles, stable task IDs and bounded objectives. Keep model-proposed decomposition separate from the application's role and permission mapping. Explain the log and runbook tasks and how their outputs will be independently checked. Label prescribed offline planning separately from live model planning. Use lesson-06 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 06, continue in my learner project. Implement shared worker-budget reservation and settlement with explicit agent-count and depth limits. Reserve before starting a child, account for returned usage and handle missing usage conservatively. Demonstrate a plan that exceeds the child-count allowance. Preserve useful completed evidence while reporting incomplete work. Explain that this checkpoint's worker pool is separate from the parent's existing runtime limit. Use lesson-06 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 06, continue in my learner project. Create isolated child contexts and run each worker through the existing runtime. Give it a new run ID, the correct parent ID, a narrow role-specific tool set and no inherited approvals. Pass only the bounded objective and permitted inputs. Demonstrate that a child cannot acquire a capability absent from its parent, and show its messages and lifecycle identifiers for review. Use lesson-06 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 06, continue in my learner project. Complete duplicate-contract handling, result aggregation and the Session 06 lab and tests. Reuse an identical completed contract, reject a changed objective under the same task ID, and preserve incomplete or contradictory findings. Compare the two-worker result with the single-agent baseline. Report quality and overhead without assuming that adding agents must be beneficial. Use lesson-06 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 06 learner exercise in my existing project: Reduce max_agents to one, try a log worker from a parent that only has runbook access, and submit the same task ID twice. Then change the objective while retaining the ID. Explain each observed result and compare the normal two-worker run with the single-agent baseline. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 06 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 6 only when the required capability is present. Run tests/test_lesson06.py, the Session 06 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

### Review the result

> Compare my completed Lesson 06 work with reference lesson-06. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

### Recover when delegation fails before a child starts

> I am working on Lesson 06. The symptom is: Delegation fails before a child starts. Diagnostic focus: Inspect the schema, role mapping and shared reservation limits. Recovery guidance: Use a valid bounded objective and an allowance that fits the planned children. Keep the permission check intact. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a child cannot find expected evidence

> I am working on Lesson 06. The symptom is: A child cannot find expected evidence. Diagnostic focus: Its objective or capability set may be insufficient. Recovery guidance: Refine the delegation contract and evaluate it. Avoid copying the full parent transcript as the first response. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the parent declares success with one failed child

> I am working on Lesson 06. The symptom is: The parent declares success with one failed child. Diagnostic focus: The aggregation policy may be ignoring required work. Recovery guidance: Preserve partial results but require the necessary child outcomes before reporting a supported complete answer. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when delegation is slower than the baseline

> I am working on Lesson 06. The symptom is: Delegation is slower than the baseline. Diagnostic focus: The fixture may not have enough independent work to offset extra calls. Recovery guidance: Record the result. Next session measures the effect of parallel execution on the same bounded tasks. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 07. Subagent coordination and collaboration

Starting reference: lesson-06. Ending reference: lesson-07.

### Prepare the workspace

> Prepare my Python learner project for Lesson 07, starting from lesson-06. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

### Orient to the reference

> Compare my current project with lesson-06 and prepare a read-only view of lesson-07 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

### Build step 1

> For Lesson 07, continue in my learner project. Implement WorkItem and dependency validation in incident/coordination.py. Reject duplicate task IDs, unknown dependencies and cycles before launching work. Demonstrate a valid graph with two independent tasks and a dependent task. Keep scheduling independent of model behaviour by using small asynchronous fixtures. Explain readiness and the configured concurrency limit separately. Use lesson-07 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 07, continue in my learner project. Implement bounded scheduling with deadlines, explicit completion states and cancellation cleanup. Preserve a fast result when another worker exceeds the deadline, mark failed dependencies as blocked, and await cancelled tasks so no orphan work remains. Demonstrate the concurrency bound and distinguish partial completion from success. Show the results by task identity rather than arrival order. Use lesson-07 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 07, continue in my learner project. Connect pending delegate calls to the scheduler through Supervisor.batch and the runtime's bounded batch path. Preserve contract validation, inherited capabilities, shared reservations and original tool-call IDs. Compare sequential and parallel execution on the same tasks with the same injected waiting time. Explain the observed timing and avoid treating one exact millisecond value as a universal expectation. Use lesson-07 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 07, continue in my learner project. Implement typed reply correlation and bounded producer-reviewer coordination. Validate correlation, task, artifact and version identity; reject stale or mismatched replies. Give one component ownership of artifact writes and escalate review that does not converge within its allowance. Complete the Session 07 lab and tests with duplicate results, failed workers and a reviewer that never accepts. Use lesson-07 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 07 learner exercise in my existing project: Create a graph with two independent tasks and one dependent task. Inject a slow worker and then a failed predecessor. Verify concurrency, partial completion and blocked dependencies. Finally, submit a stale envelope and run a reviewer that never accepts; neither should silently succeed. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 07 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 7 only when the required capability is present. Run tests/test_lesson07.py, the Session 07 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

### Review the result

> Compare my completed Lesson 07 work with reference lesson-07. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

### Recover when the scheduler appears to hang

> I am working on Lesson 07. The symptom is: The scheduler appears to hang. Diagnostic focus: Check for a dependency cycle, an unknown dependency or a runner that ignores cancellation. Recovery guidance: Run graph validation first and reproduce with the small asynchronous fixture before involving model calls. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when parallel execution is not faster

> I am working on Lesson 07. The symptom is: Parallel execution is not faster. Diagnostic focus: The work may be CPU-bound, serialized by a resource owner or limited by provider rate limits. Recovery guidance: Measure where time is spent. Keep bounded concurrency and compare equivalent workloads. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a late reply overwrites newer evidence

> I am working on Lesson 07. The symptom is: A late reply overwrites newer evidence. Diagnostic focus: Correlation or expected-version checks were omitted. Recovery guidance: Restore envelope validation and have the single artifact owner reconcile the reply. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the reviewer loops indefinitely

> I am working on Lesson 07. The symptom is: The reviewer loops indefinitely. Diagnostic focus: The acceptance rule or round limit is missing. Recovery guidance: Use bounded_review and return an escalated outcome with the remaining disagreements. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 08. A2A across independent agent services

Starting reference: lesson-07. Ending reference: lesson-08.

### Prepare the workspace

> Prepare my Python learner project for Lesson 08, starting from lesson-07. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

### Orient to the reference

> Compare my current project with lesson-07 and prepare a read-only view of lesson-08 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

### Build step 1

> For Lesson 08, continue in my learner project. Create the independent runbook specialist in incident/a2a_service.py with the pinned A2A SDK. Advertise the expected skill, interface, protocol and streaming capability through an Agent Card. Enforce the local teaching bearer credential at the endpoint and keep the service read-only and tenant-scoped. Explain what the card advertises and what application code actually enforces. Use lesson-08 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 08, continue in my learner project. Implement SpecialistExecutor's task lifecycle using the SDK's event flow. Enqueue the initial task before status updates, run the existing agent loop with runbook-only access, publish evidence as an artifact and report the correct terminal state. Add the deterministic slow-task fixture for cancellation. Demonstrate incomplete execution without manufacturing a successful answer. Use lesson-08 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 08, continue in my learner project. Implement the platform-facing RemoteSpecialist adapter in incident/a2a_client.py. Check the allowed tenant, discover the expected capability, consume streamed artifacts and status, and normalize a completed result into the platform contract. Reject an incomplete stream. Show the evidence and remote run identifier, and explain what must be retained for later reconciliation. Use lesson-08 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 08, continue in my learner project. Complete the real local HTTP demonstration, service cleanup and Session 08 tests. Show discovery, streamed progress and evidence, rejection of an unauthenticated request, and confirmed cancellation of a slow remote task. Keep third-party services and live model calls out of this local check. Explain why a disconnected client is not proof that remote work has stopped. Use lesson-08 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 08 learner exercise in my existing project: Run the local service separately, fetch its Agent Card and call the client adapter. Try a missing bearer credential, an unsupported skill declaration and a deliberately slow task. Record the distinction between authentication failure, capability mismatch, incomplete streaming and confirmed cancellation. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 08 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 8 only when the required capability is present. Run tests/test_lesson08.py, the Session 08 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

### Review the result

> Compare my completed Lesson 08 work with reference lesson-08. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

### Recover when an old tutorial's types or imports fail

> I am working on Lesson 08. The symptom is: An old tutorial's types or imports fail. Diagnostic focus: Check whether it targets A2A 0.3 rather than the pinned 1.1.2 SDK and 1.0 protocol. Recovery guidance: Use the repository's protobuf request types, factory API and generated routes. Restore the lock file before debugging application logic. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the server rejects a status event

> I am working on Lesson 08. The symptom is: The server rejects a status event. Diagnostic focus: A Task may not have been enqueued before the status update. Recovery guidance: Restore the initial Task event and rerun the lifecycle test. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when the stream ends with no complete answer

> I am working on Lesson 08. The symptom is: The stream ends with no complete answer. Diagnostic focus: Inspect terminal status and whether an artifact was received. Recovery guidance: Report incomplete_remote_task and reconcile by task ID. Do not treat a disconnected stream as success. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a local port is already occupied

> I am working on Lesson 08. The symptom is: A local port is already occupied. Diagnostic focus: Another process is using the fixed manual-demo port. Recovery guidance: Use the ephemeral-port lab helper or choose a different explicit loopback port and update the advertised base URL. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 09. Build the reusable platform core

Starting reference: lesson-08. Ending reference: lesson-09.

### Prepare the workspace

> Prepare my Python learner project for Lesson 09, starting from lesson-08. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

### Orient to the reference

> Compare my current project with lesson-08 and prepare a read-only view of lesson-09 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

### Build step 1

> For Lesson 09, continue in my learner project. Implement immutable versioned agent definitions in incident/platform.py. Store the name, version, specification and content hash, and reject conflicting content under an existing version. Provide single-agent and team configurations that reuse the existing services. Explain which values belong to a definition and which belong to a tenant-specific run. Use lesson-09 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 09, continue in my learner project. Implement submission, durable run metadata and explicit worker ownership. Resolve the definition, enforce the operator-only remediation configuration, construct context in application code and save queued state before launch. Add a bounded durable lease so two active workers cannot claim the same run. Demonstrate the ownership conflict and explain recovery after lease expiry. Use lesson-09 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 09, continue in my learner project. Compose the existing runtime, context, tool, MCP, supervisor, A2A, state and artifact adapters behind the platform service. Keep the single-agent and team paths as configurations of shared services. Persist child identities and the chosen configuration, and save the final artifact with its expected version. Trace one incident from submission through a child tool call to stored evidence. Use lesson-09 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 09, continue in my learner project. Expose authenticated submit, inspect, cancel, decision and resume operations in incident/api.py. Bind tenant identity to authentication, require an operator for approval, and reject a stale reviewed action key. Complete the Session 09 tests with two configurations and cross-tenant inspection. For a manual remediation demo, show me the pending action and wait for my explicit decision; automated tests may exercise their labelled fixtures. Use lesson-09 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 09 learner exercise in my existing project: Submit INC-001 using single and team, inspect each stored definition version and compare the answers. Try to inspect the Acme run with the Globex identity. Then submit the operator-only remediation fixture, reject a stale approval key, approve the current proposal and resume it. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 09 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 9 only when the required capability is present. Run tests/test_lesson09.py, the Session 09 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

### Review the result

> Compare my completed Lesson 09 work with reference lesson-09. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

### Recover when unknown agent or version

> I am working on Lesson 09. The symptom is: Unknown agent or version. Diagnostic focus: The definition was not registered or the requested version differs from the intended checkpoint. Recovery guidance: Inspect Definitions and use the registered configuration. Create a new immutable version for a deliberate change. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when resume reports that the run is already owned

> I am working on Lesson 09. The symptom is: Resume reports that the run is already owned. Diagnostic focus: A worker still has an active lease. Recovery guidance: Inspect the owner and wait for valid release or expiry. Do not disable ownership checks to force a duplicate launch. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when an operator action returns 403

> I am working on Lesson 09. The symptom is: An operator action returns 403. Diagnostic focus: The request used an analyst identity. Recovery guidance: Use the explicitly configured operator credential for the local approval exercise. Do not place that authority in the agent's prompt. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a configuration update unexpectedly changes old runs

> I am working on Lesson 09. The symptom is: A configuration update unexpectedly changes old runs. Diagnostic focus: The implementation may be reading only a mutable current definition. Recovery guidance: Keep the resolved version and hash in each run snapshot and reject in-place definition changes. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 10. Security and tenant isolation

Starting reference: lesson-09. Ending reference: lesson-10.

### Prepare the workspace

> Prepare my Python learner project for Lesson 10, starting from lesson-09. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

### Orient to the reference

> Compare my current project with lesson-09 and prepare a read-only view of lesson-10 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

### Build step 1

> For Lesson 10, continue in my learner project. Create the hostile-provider fixture that proposes mock_remediate from a read-only investigation context. Exercise the actual executor rather than relying on a model to refuse. Show the denied tool event and prove that the effect ledger remains empty. Preserve the platform's existing permission policy and explain which application control contains the bad proposal. Use lesson-10 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 10, continue in my learner project. Implement and test tenant workspace containment and explicit endpoint policy in incident/security.py. Resolve paths before containment checks, reject traversal and symlink escapes, require exact approved hosts and appropriate transport security, and constrain discovered remote interfaces. Do not disable TLS or operating-system protections. Explain the difference between these application checks and a full execution sandbox. Use lesson-10 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 10, continue in my learner project. Strengthen final-answer validation using structured source metadata and the expected answer shape. Demonstrate that merely mentioning a fabricated source ID in prose cannot satisfy evidence validation. Preserve the distinction between observing a source and proving that it supports the conclusion. Add focused provenance regressions while keeping existing valid investigations working. Use lesson-10 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 10, continue in my learner project. Add redaction for observable events without removing useful operational counters. Complete the Session 10 lab and adversarial tests, then rerun the tenant and approval checks from earlier lessons. Show sanitized evidence and identify the actual containment boundary. Explain untested production responsibilities such as storage protection and infrastructure-level isolation without claiming they are already implemented. Use lesson-10 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 10 learner exercise in my existing project: Run the hostile-provider fixture and verify zero effects. Add a symlink escape, a lookalike host and a fabricated citation to the local tests. Re-run cross-tenant API inspection and exact-action approval checks. Record the control and evidence for each rejection. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 10 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 10 only when the required capability is present. Run tests/test_lesson10.py, the Session 10 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

### Review the result

> Compare my completed Lesson 10 work with reference lesson-10. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

### Recover when a live provider is blocked by endpoint policy

> I am working on Lesson 10. The symptom is: A live provider is blocked by endpoint policy. Diagnostic focus: The configured base host is not in MODEL_ALLOWED_HOSTS. Recovery guidance: Review and explicitly configure the intended trusted provider host. Do not accept a host chosen by retrieved content or disable TLS verification. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a legitimate artifact path is rejected

> I am working on Lesson 10. The symptom is: A legitimate artifact path is rejected. Diagnostic focus: The path may be absolute, outside the tenant root or resolved through a symlink. Recovery guidance: Use a relative path within the intended tenant workspace and inspect the resolved location. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when redaction removes too much diagnostic detail

> I am working on Lesson 10. The symptom is: Redaction removes too much diagnostic detail. Diagnostic focus: A sensitive key name may have been used for a non-sensitive value. Recovery guidance: Improve the telemetry schema and retain separate safe counters rather than weakening credential protection. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when someone calls the path helper a full sandbox

> I am working on Lesson 10. The symptom is: Someone calls the path helper a full sandbox. Diagnostic focus: Application containment is being confused with OS isolation. Recovery guidance: State the actual boundary and use the restricted container or an appropriate production execution sandbox for infrastructure-level isolation. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 11. Operating and releasing agent platforms

Starting reference: lesson-10. Ending reference: lesson-11.

### Prepare the workspace

> Prepare my Python learner project for Lesson 11, starting from lesson-10. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

### Orient to the reference

> Compare my current project with lesson-10 and prepare a read-only view of lesson-11 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

### Build step 1

> For Lesson 11, continue in my learner project. Implement bounded admission and active-worker controls in incident/operations.py and connect them to Platform. Distinguish queue capacity from per-tenant arrival limits and active concurrency. Release reservations and leases on success, failure and cancellation. Include parent and child allowances in shared budget accounting. Show excess-work rejection and prove that cancellation restores capacity. Use lesson-11 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 11, continue in my learner project. Implement the tenant-scoped parent-and-child trace and its escaped, redacted HTML view. Run the hybrid investigation with a local MCP-backed log worker and independent A2A runbook specialist. Show the three correlated run nodes, their evidence and usage counted once. Explain that this is the application's trace view, and identify any external observability integration that remains untested. Use lesson-11 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 11, continue in my learner project. Implement release_gate and evaluate_platform using the actual immutable configurations. Compare the same dataset and partition, retain per-case results and enforce explicit quality, latency and usage thresholds. Evaluate a candidate context policy and demonstrate rejection of a degraded or mismatched report. Explain which thresholds are teaching values and which need workload-specific decisions. Use lesson-11 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 11, continue in my learner project. Complete the Session 11 end-to-end, overload, rollout and rollback demonstration. Show the runnable platform, correlated trace, accepted and rejected load, passing candidate activation and return to the previous version. Inspect the existing restricted container recipe and run it if the environment supports it. Report its temporary-state limitation and any untested deployment behaviour. Leave the working platform ready for tuning and presentation. Use lesson-11 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 11 learner exercise in my existing project: Run the hybrid end-to-end investigation and inspect its three-node trace. Lower queue capacity, send excess work and verify rejection and cleanup. Evaluate a deliberately worse candidate and show that the release gate blocks it. Then activate a passing version and roll back. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 11 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 11 only when the required capability is present. Run tests/test_lesson11.py, the Session 11 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

### Review the result

> Compare my completed Lesson 11 work with reference lesson-11. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

### Recover when the parent completes but a trace child is missing

> I am working on Lesson 11. The symptom is: The parent completes but a trace child is missing. Diagnostic focus: Child persistence or parent correlation may have been omitted. Recovery guidance: Inspect child run IDs and save their completed snapshots before building the trace. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when capacity remains full after cancellation

> I am working on Lesson 11. The symptom is: Capacity remains full after cancellation. Diagnostic focus: The worker cleanup may not release its reservation or lease. Recovery guidance: Run the cancellation regression test and keep cleanup in finally for both waiting and active work. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a release gate fails on latency

> I am working on Lesson 11. The symptom is: A release gate fails on latency. Diagnostic focus: Inspect the measured cases and environment rather than only the mean. Recovery guidance: Diagnose the slow stage, rerun representative trials and use justified project thresholds. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when container replacement loses sandbox state

> I am working on Lesson 11. The symptom is: Container replacement loses sandbox state. Diagnostic focus: The supplied restricted Compose recipe uses tmpfs for the writable state directory. Recovery guidance: Use the local persistent SQLite demo for recovery exercises, or provision and test a persistent deployment volume before relying on container restart durability. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## 12. Tune and present your agentic platform

Starting reference: lesson-11. Ending reference: lesson-12.

### Prepare the workspace

> Prepare my Python learner project for Lesson 12, starting from lesson-11. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

### Orient to the reference

> Compare my current project with lesson-11 and prepare a read-only view of lesson-12 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

### Build step 1

> For Lesson 12, continue in my learner project. Review my working Session 11 platform and the capstone reference. Help me state one bounded tuning hypothesis and identify the smallest change needed to test it. Explain the EfficientMockProvider example and where early completion is safe or unsafe in these fixtures. Preserve the baseline and define evidence that would justify adopting or rejecting my change before implementing it. Use lesson-12 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 2

> For Lesson 12, continue in my learner project. Apply the selected tuning change as a new version or clearly isolated patch. Evaluate before and after on the same cases, partitions and trial conditions, retaining failures and per-case rows. Use the actual platform path. Keep fixture usage separate from live-model economics and preserve the original expected outcomes. Show the comparison and release decision with its limitations. Use lesson-12 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 3

> For Lesson 12, continue in my learner project. Help me evaluate caching or routing as a separate capstone experiment when relevant. Preserve tenant, configuration, input, schema and freshness boundaries in cache identity; report cold and warm behaviour separately. Check uncertainty routing without assuming a cheaper provider is always adequate. Run the focused tests and explain correctness risks and evidence needed for a live deployment. Use lesson-12 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Build step 4

> For Lesson 12, continue in my learner project. Prepare a demonstration of my completed platform and a concise evidence pack: architecture, one end-to-end investigation, one permission or recovery failure case, and the before-and-after tuning report. Use actual code and recorded results, clearly identifying anything not demonstrated live. Ask me to explain the tradeoffs in my own words. Do not invent improvements or automatically adopt a change whose evidence is inadequate. Use lesson-12 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

### Learner exercise

> Help me carry out the Lesson 12 learner exercise in my existing project: Before class, select a small tuning intervention and generate a comparable before-and-after report. During class, demonstrate the working platform and one failure-control case. Explain the evidence, tradeoffs and adoption decision. Use the fixture experiment only as a rehearsal when live model access is unavailable. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

### Verify the checkpoint

> Verify my Lesson 12 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 12 only when the required capability is present. Run tests/test_lesson12.py, the Session 12 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

### Review the result

> Compare my completed Lesson 12 work with reference lesson-12. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

### Recover when the demo fails during a presentation

> I am working on Lesson 12. The symptom is: The demo fails during a presentation. Diagnostic focus: Locate the failing checkpoint, service or configuration and preserve the error evidence. Recovery guidance: Use the prepared completed reference snapshot and saved trace to continue the explanation. State which part was demonstrated live and which was shown from recorded evidence. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a tuning change improves one case and harms another

> I am working on Lesson 12. The symptom is: A tuning change improves one case and harms another. Diagnostic focus: Inspect per-case outcomes and the acceptance criteria. Recovery guidance: Revise or reject the change, or define a justified routing policy and evaluate it separately. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Recover when a participant presents fixture usage as real savings

> Review my Lesson 12 presentation claims against the recorded comparison report. Identify any synthetic fixture usage described as real model cost or savings. Correct those claims and label the measurement conditions clearly. Explain what live benchmark and pricing evidence would be needed to estimate actual cost. Preserve the recorded results and do not invent an improvement.

### Recover when there is not enough time for every individual presentation

> Help me organize Lesson 12 presentations within the existing 90-minute agenda. Ask for the cohort size if it is missing. Allocate the 25-to-65-minute presentation block using review groups or pre-recorded demonstrations when necessary. Keep the remaining agenda timings and shared review criteria, give every participant a review opportunity and prepare a short plenary discussion. Show the proposed schedule and timing totals; no implementation changes are needed.
