# Session 01 content development: Agent architecture and the ReAct runtime

> Markdown copy of [`01 Agent architecture and the ReAct runtime - content development.docx`](01%20Agent%20architecture%20and%20the%20ReAct%20runtime%20-%20content%20development.docx) for reading on GitHub. The Word document is the original; edit it there and regenerate this page.

## 1. Topic Overview

### 1.1 Topic Title - Agent foundations: Agent architecture and the ReAct runtime (Session 01)

**Owner: [SME]**

### 1.2 Short Topic Description

**Owner: [SME]**

Write 2–4 sentences explaining what the topic is about, why it matters and what learners will explore.

**Your input:**

This first session of "Building Agentic Platforms" explains how an AI agent actually works: a model proposes an action, a runtime decides whether to execute it, and a tool returns an observation, in a loop bounded by explicit limits. It matters because every later capability of the platform (tools, memory, subagents, remote agents, the tool gateway, identity and the console) is built around this one loop. Learners compare workflows with agents, see the target platform they will build over 12 sessions, and direct their own coding agent to build a bounded, observable single-agent runtime for a sandbox incident investigation.

### 1.3 Level

**Owner: [SME + L&D]**

Select Beginner / Intermediate / Advanced and add context if useful.

**Your input:**

**Context:** L3 is the advanced, selective level of the programme for experienced software engineers. The session is hands-on engineering, not an introduction to LLMs.

Advanced

### 1.4 Prerequisites

**Owner: [SME]**

List previous topics, knowledge, tools, access or skills required. If none, write “No prerequisites.”

**Your input:**

• Independent programming in Python (or TypeScript): API integration, async execution, error handling and automated tests.

• LLM foundations: prompting, context limits, embeddings, retrieval and RAG (the 2025 L2 material).

• HTTP and JSON basics; comfortable reading code produced by a coding agent and reviewing it critically.

• Access to an AI coding agent (for example Claude Code) and a personal Git repository. No paid model account is needed: the course runs on an offline, deterministic mock provider.

• Local Python 3.12 environment (the coding agent installs pinned dependencies) or Docker.

### 1.5 Session Details

**Owner: [L&D]**

L&D provides date, calendar details and delivery logistics. SME provides estimated time needed and timing constraints.

**Date:** **Sep 22, 2026**

**Session link: zoom**

**Calendar invitation text:**

Draft for L&D (please adjust date and link): "L3 Building Agentic Platforms, Session 01: Agent architecture and the ReAct runtime (120 min: 30 min discussion + 90 min guided build). We start the incident-investigation platform you will extend all course long. Before the session: set up your repository and coding agent, and read 'Building effective agents' and the ReAct paper. Bring a laptop with your coding agent working."

**Duration (SME):** 120 minutes. Timing constraint: the guided build needs at least 70 uninterrupted minutes; learners need their coding agent and repository ready before the session starts.

**Note for L&D:** this template says Sep 22, 2026, but the Selection sheet of the curriculum workbook plans the first session for 2026-10-28. Please confirm the date.

### 1.6 Speaker(s)

**Owner: [SME + L&D]**

List the main speaker, co-speakers and guest experts and clarify their roles.

**Your input:**   
Maksym Pavlov

**Role:** Maksym Pavlov is the main speaker and SME: concept discussion, live demo of each build step, review of learners' code and evidence. Co-speakers or mentors: none named yet.

## 2. Learning Objectives

**Owner: [SME]**

Define what learners should be able to do after completing the topic. Aim for 3–5 measurable objectives.

Use action verbs: explain, identify, compare, apply, analyze, create, configure, demonstrate, evaluate, troubleshoot.

Avoid vague verbs such as “understand”, “know” or “learn about”.

Example:

By the end of this topic, you will be able to:  
 • Explain the main components of a RAG architecture.  
 • Identify when RAG is an appropriate solution.  
 • Compare different retrieval approaches.  
 • Apply basic RAG concepts to a practical use case.

**Objective 1:**

Compare a fixed workflow with an agent loop and choose which one fits a given incident-investigation task.

**Objective 2:**

Design an application-owned run contract that separates tenant identity, permissions and limits from anything the model produces.

**Objective 3:**

Build, by directing a coding agent, a bounded model → tool → observation loop with step, token, time and repeated-action guards.

**Objective 4:**

Evaluate a run from its event log and structured, cited answer, distinguishing completed execution from a supported conclusion.

**Objective 5:**

Describe the target agentic platform (runtime, agent registry, MCP tool gateway, identity and credentials, console, operations) and locate the runtime within it.

## 3. Pre-work

**Owner: [SME]**

Define anything participants need to complete before the live session: reading, video, previous course/module, tool setup, account/access, short task, reflection question or preparation of data/files.

If nothing is required, write: “No pre-work required.”

**Pre-work:**

• Refresh LLM, prompting and RAG basics, plus HTTP, JSON, async programming and tests (about 1–2 hours).

• Read 'Building effective agents' (Anthropic) and the ReAct paper; skim your model provider's tool-calling docs (about 1 hour).

• Set up a personal Git repository and a working AI coding agent; ask it to prepare the Lesson 01 workspace from the reference repository (prompt provided in the course materials). Confirm the baseline checks run.

• Write five acceptance scenarios for the sample incident and a simple fixed-workflow baseline to compare against later.

• Sketch the target platform you expect to build, labelling each component with the session that builds it.

## 4. Live Session Design

### 4.1 Session Agenda

**Owner: [SME]**

Provide the proposed flow and approximate timing.

| Section | Topic | Approx. time | Format |
|---|---|---|---|
| 1 | Opening: the incident, the target platform blueprint | 0–10 min | Discussion |
| 2 | Concept: model, runtime and tools; workflows vs agents; limits | 10–30 min | Presentation + discussion |
| 3 | Build steps 1–2: run contract; provider adapters | 30–50 min | Live demo + guided build |
| 4 | Build steps 3–4: the loop and pending calls; guards and evidence | 50–75 min | Live demo + guided build |
| 5 | Learner exercise: fault injection on limits | 75–100 min | Hands-on exercise |
| 6 | Acceptance checks and interpreting results | 100–115 min | Verification + discussion |
| 7 | Questions, reflection and checkpoint handoff | 115–120 min | Reflection |

### 4.2 Topic-by-Topic Content

**Owner: [SME]**

For each section, provide:

Key concepts — what does the participant need to know?

Common misconceptions — what do learners frequently misunderstand?

Key message — the one thing participants should remember from this section.

**Section 1:**

From workflows to agents, and the platform we will build

**Key concepts:** a workflow prescribes steps in advance; an agent chooses the next permitted action from observations. An agentic platform wraps the agent runtime with an agent registry, an MCP tool gateway, identity and delegated credentials, a web console and operations. Today builds only the runtime at the centre.

**Common misconceptions:** agents always beat workflows (keep the workflow baseline and compare); a fluent answer is a successful investigation (success needs a cause, cited evidence, or an explicit insufficient-evidence result).

**Key message:** the runtime is the core every later platform component wraps, so its contracts and events must be explicit.

**Section 2:**

The run contract and model access

**Key concepts:** Context (tenant, role, permitted tools, run id) is owned by application code; Run holds messages, events and the answer; Limits bound steps, tokens, elapsed time and output size. Provider adapters normalize OpenAI-compatible and Anthropic responses into one Reply; a deterministic mock provider makes behaviour reproducible without credentials.

**Common misconceptions:** the model can be trusted to state its own permissions; a passing offline test proves live-model quality; zero configured price means a provider is free.

**Key message:** anything the model produces is untrusted input; authority is constructed by the application.

**Section 3:**

The bounded loop, guards and evidence

**Key concepts:** model proposes a tool call, the runtime records it as pending, executes it and appends the observation with the same call id. Guards stop the run with a named code (step_budget, token_budget, TimeoutError, repeated_action). The event log records actions and usage, not hidden reasoning; from Session 08 the platform console renders it as a run timeline.

**Common misconceptions:** a completed run means the incident is solved; a coding agent's 'done' message is evidence; a timeout can be enforced by instructing the model.

**Key message:** every stop is a controlled, explained outcome, and evidence comes from runs and checks, not from claims.

### 4.3 Interactive Activities

**Owner: [SME content + L&D learning design]**

Identify where participants should actively engage.
- Poll**✔ (concept block) Which limit catches a provider that hangs without returning tokens?**
- Discussion**✔ (opening) What must a successful investigation contain?**
- Case study
- Breakout activity
- Quiz
- Hands-on exercise**✔ (75–100 min) Fault injection on runtime limits**
- Live demo**✔ (build steps 1–4) Instructor demonstrates each bounded change and its checks**
- Problem-solving activity**✔ (step 3) Trace one tool-call id from proposal to observation**
- Reflection**✔ (close) Redraw the platform blueprint and mark today's box**

**Activity details (SME content and L&D will turn into activity in zoom or whiteboard):**

For each activity include: Purpose • Instructions • Time • Expected outcome • Debrief / discussion points.

**1. Discussion: what does success look like?** Purpose: set acceptance criteria before building. Instructions: show the synthetic INC-001 record (payments slow after a deployment); ask learners to list what a good investigation must contain. Time: 5 min. Expected outcome: likely cause, cited source, explicit 'insufficient evidence' when data is missing. Debrief: a fluent paragraph is not an acceptance test.

**2. Poll: which component owns a timeout?** Purpose: separate runtime responsibilities from model behaviour. Options: the model / the tool / the runtime / the provider. Correct: the runtime. Time: 2 min. Debrief: an instruction to the model cannot enforce elapsed time; only the loop can.

**3. Live demo with guided build (4 steps).** Purpose: show each bounded change. Instructions: for each step the instructor explains, shows the prompt learners give their coding agent, then compares the agent's change with the reference excerpt. Time: 45 min. Expected outcome: a working bounded runtime in each learner's repository. Debrief: ask each learner to explain one boundary in their agent's change.

**4. Problem-solving: trace a tool-call id.** Purpose: understand why call ids must be preserved. Instructions: follow the log_lookup call for INC-001 from the assistant message to the tool message. Time: 5 min. Expected outcome: learners can explain what breaks if a result is appended without its call. Debrief: pending calls are the future recovery boundary.

**5. Hands-on exercise: fault injection.** Purpose: make every stop condition observable. Instructions: in a local invocation allow one step, then a tiny token budget, then a short deadline with a slow mock provider; predict each failure first. Time: 25 min. Expected outcome: step_budget, token_budget and TimeoutError observed, then the normal cited answer restored. Debrief: compare predictions with observations and explain discrepancies.

**6. Reflection: platform blueprint.** Purpose: connect today's build to the whole course. Instructions: redraw the blueprint and mark the box built today; note which later console views already have their data in today's event log. Time: 5 min. Expected outcome: a personal architecture sketch kept for the next sessions.

### 4.4 Practical Application After the Session

**Owner: [SME]**

Describe what participants will actually do.

**Task:**

Extend your Session 01 checkpoint with one new acceptance scenario and a workflow-versus-agent comparison.

**Instructions:**

• Ask your coding agent to add a missing-incident scenario (for example INC-404) and define what a supported insufficient_evidence answer looks like.

• Run the workflow baseline and the agent loop on the same fixtures; record step counts, stop reasons and error handling.

• Redraw the platform blueprint and note which later console views the event log can already feed.

• Have the agent run the full test suite and save a recoverable checkpoint; keep the actual output as evidence.

**Expected result:**

A committed checkpoint with the new scenario and passing checks (7 tests at the reference checkpoint), a short comparison table, and an updated blueprint sketch.

**Feedback / debrief points:**

• Did the coding agent's claims match the check output? Unrun or skipped checks are not passes.

• Where did the workflow outperform the agent, and why?

• Which limit fired first in each failure case, and was the failure explained rather than an unexplained exception?

## 5. Presentation

### 5.1 Presentation Content

**Owner: [SME]**

Provide the presentation content or draft. Recommended logic: Context → Concept → Example → Application → Practice → Summary.

**Presentation / slide deck:**

Draft outline (Context → Concept → Example → Application → Practice → Summary). The full instructor script is in instructor guide 01 (instructor-guides/01 Agent architecture and the ReAct runtime.docx).

• 1. Title and course promise: build one agentic platform in 12 sessions.

• 2. Context: the sandbox incident (payments slow after deploy d42) and what 'solved' means.

• 3. The target platform blueprint: runtime, registry, tool gateway, identity, console, operations; session map.

• 4. Concept: workflow vs agent; model, runtime and tools as three boxes.

• 5. Concept: the run contract (Context, Run, Limits) and who owns each field.

• 6. Concept: provider adapters and the deterministic mock provider.

• 7. Example: one iteration for INC-001, from tool call to observation.

• 8. Example: guards and their failure codes.

• 9. Application: the four build prompts learners give their coding agent.

• 10. Practice: fault-injection exercise and acceptance checks.

• 11. Evidence, not claims: reading the event log and test output.

• 12. Summary, reflection questions and what comes next.

## 6. Session Wrap-up

### 6.1 Conclusions / Key Takeaways

**Owner: [SME]**

Define 3–5 essential messages participants should leave the session with. These will also be used in e-learning.

**Key takeaway 1:**

An agent is a loop: the model proposes, the runtime decides and executes, the tool observes.

**Key takeaway 2:**

Authority (tenant, role, permitted tools) is set by application code, never by model output.

**Key takeaway 3:**

Every run must be bounded; each stop is a named, explained outcome.

**Key takeaway 4:**

Completed execution is not a solved incident: look for cited evidence or an explicit insufficient-evidence result.

**Key takeaway 5:**

The runtime is the core of the platform; its event log is what the console will later show.

### 6.2 Lesson Reflection

**Owner: [SME]**

Provide 2–4 questions that help participants connect the topic to their own work.

Suggested framing: “Before moving on, consider:”

**Reflection question 1:**

Which task in your current project would be better served by a fixed workflow than by an agent, and why?

**Reflection question 2:**

What does your team currently accept as evidence that an AI-assisted change works?

**Reflection question 3:**

Which limit would you need first if you ran an agent against a production system, and who should own it?

### 6.3 What's Next

**Owner: [SME + L&D]**

Identify the logical next step: next session, next topic, practice assignment, certification or deeper learning.

**What's next:**

Session 02, Reliable tools and MCP integration (120 min): validated tool contracts, application-owned permissions, an approval gate for mock remediation and real MCP transport. Bring your Session 01 checkpoint.

## 7. Post-session E-learning Content

The e-learning version will be available to anyone interested in the topic, including people who did not attend the live session.

### 7.1 Session Recording

**Owner: [L&D]**

L&D records the session, uploads the recording and adds it to the topic page. SME ensures the session content is suitable for recording and future access.

**Your input:**

### 7.2 Short Learning Version

**Owner: [SME + L&D]**

L&D structures, edits and adapts the content for self-paced learning. SME can provide an outline + detailed notes or a draft script.

**Your input:**

Outline for a 20–25 minute self-paced version:

• Video 1 (5 min): what an agent is, workflow vs agent, and the platform blueprint.

• Video 2 (6 min): the run contract and why the application owns authority.

• Video 3 (6 min): walkthrough of one INC-001 run and its event log.

• Video 4 (4 min): guards and failure codes, with the fault-injection demo.

• Knowledge check (7.4) and the self-paced assignment (7.5).

Source material: instructor guide 01 (SAY sections), the reference repository at tag lesson-01 and its lab output.

### 7.3 Examples / Use Cases

**Owner: [SME]**

Provide examples that can stand on their own in e-learning. Include enough context for someone who was not at the live session.

**Your input:**

**Example 1: a supported answer.** INC-001 (tenant astro): logs show DB pool wait of 900 ms after deploy d42; the runbook matches connection-pool exhaustion. After three model steps the agent answers 'connection_pool_exhaustion', citing log-astro-001 and rb-pool-v1.

**Example 2: an honest 'insufficient evidence'.** INC-003: latency is elevated but there are no diagnostic logs. A good agent returns status insufficient_evidence instead of guessing; the run still completes successfully.

**Example 3: a controlled stop.** A provider that keeps requesting the same tool call with the same arguments is stopped with repeated_action; a one-step allowance stops with step_budget. Both are expected outcomes, not crashes.

### 7.4 Knowledge Check

**Owner: [SME]**

Provide 3–5 questions testing the most important concepts. Include question, options if applicable, correct answer and explanation. L&D adapts them into the final interaction.

**Your input:**

**Q1. Who should decide which tools an agent may call?** A) the model, in its answer  B) the retrieved runbook  C) application code, when it builds the run context  D) the tool itself. Correct: C. Model output and retrieved text are untrusted; authority is constructed by the application.

**Q2. A run finishes with status completed. What does that prove?** A) the incident is solved  B) the loop ended within its limits with a valid answer  C) the model is accurate  D) nothing. Correct: B. The answer may still be insufficient_evidence; evaluation must check the outcome separately.

**Q3. Which guard catches a provider that hangs without returning any tokens?** A) step limit  B) token budget  C) elapsed-time limit  D) repeated-action check. Correct: C. No steps or tokens are consumed while it hangs.

**Q4. Why record a proposed tool call before executing it?** A) faster execution  B) it lets the run pause, resume or be approved without losing or repeating the action  C) providers require it  D) to hide it from the model. Correct: B.

**Q5. The offline mock provider's tests all pass. What have you verified?** A) live-model quality  B) the loop, contracts and boundaries  C) API costs  D) provider availability. Correct: B. Live behaviour needs a separate, authorized check.

### 7.5 Practice / Assignment

**Owner: [SME]**

Create a task that can be completed without attending the live session. Include task, context, expected output, estimated time, success criteria and resources.

**Your input:**

**Task:** Using your own coding agent and the course reference repository, build the Session 01 checkpoint: a bounded single-agent runtime for the sample incident.

**Context:** The four build prompts and the verification prompt are in LEARNER_PROMPTS.md (Lesson 01); no paid model account is needed.

**Expected output:** a repository whose Lesson 01 tests pass, the lab output for INC-001 citing log-astro-001 and rb-pool-v1, and a short note explaining each guard you triggered.

**Estimated time:** 2–3 hours.

**Success criteria:** INC-001 answers connection_pool_exhaustion with observed sources; the repeating provider stops with repeated_action; step, token and time limits each produce their expected failure; both provider request-shape tests pass without real credentials.

**Resources:** instructor guide 01, LEARNER_PROMPTS.md, reference tag lesson-01.

### 7.6 Lesson Reflection

**Owner: [SME]**

Provide reflection questions for independent learners. These may be the same as or adapted from the live session.

**Your input:**

Use the three live-session questions (6.2), plus: 'Where in your own work have you accepted an AI tool's completion message as proof? What evidence would you ask for now?'

### 7.7 Deep Dive / Additional Resources

**Owner: [SME]**

Provide articles, videos, books, documentation, research, internal resources, tools, tutorials or examples. Distinguish Recommended / Essential from Optional / Deep Dive.

**Your input:**

**Essential:** Building effective agents (Anthropic): https://www.anthropic.com/engineering/building-effective-agents

**Essential:** ReAct: Synergizing Reasoning and Acting in Language Models: https://arxiv.org/abs/2210.03629

**Optional / deep dive:** your model provider's tool-calling documentation (OpenAI function calling or Anthropic tool use).

**Optional / deep dive:** the reference repository at tag lesson-01 (incident/core.py, incident/providers.py) and TESTING.md.

### 7.8 What's Next

**Owner: [L&D + SME]**

Define the next topic, recommended learning path, practice or next action.

**Your input:**

Next: Session 02, Reliable tools and MCP integration. Recommended path: complete the 7.5 assignment first; Session 02 starts from that checkpoint.

## 8. Materials & Assets

**Owner: [SME]**

Indicate which assets are needed and provide them where applicable.
- Presentation**✔ outline in 5.1; slides to be produced**
- Speaker notes**✔ SAY sections of instructor guide 01**
- Script**✔ instructor guide 01 (complete)**
- Examples**✔ three worked examples in 7.3**
- Case study
- Demo**✔ reference repository, tags lesson-00 → lesson-01**
- Screenshots
- Diagrams**✔ platform blueprint (drawn live; a slide version is still to be produced)**
- Templates
- Sample files**✔ synthetic incidents and runbooks in the reference repository**
- Quiz questions**✔ five questions in 7.4**
- Practice assignment**✔ 7.5 and LEARNER_PROMPTS.md, Lesson 01**
- Additional resources**✔ 7.7**
- Other:

## 9. Content Accuracy & SME Notes

### 9.1 Important Terminology

**Owner: [SME]**

List terminology that must be used consistently.

**Your input:**

• Agent vs workflow: an agent chooses the next permitted action from observations; a workflow's steps are fixed in advance.

• Runtime (the loop): the code that calls the model, executes permitted tools and enforces limits.

• Run, Context, Limits: run state; application-owned identity and permissions; step, token, time and output bounds.

• Tool call / observation: a model's proposed action and the tool's result, linked by the same call id.

• Event log: recorded actions and usage of a run (not the model's hidden reasoning).

• Mock (fixture) provider: a deterministic stand-in for a model; its 'tokens' are teaching metrics, not real usage or cost.

• Checkpoint: a reference repository tag (lesson-NN) marking the end state of a session.

• insufficient_evidence: the correct answer status when the evidence does not support a cause.

• Platform components (used all course): agent registry, MCP tool gateway, identity and delegated credentials, platform console.

### 9.2 Common Misconceptions

**Owner: [SME]**

List frequent misunderstandings. This will inform explanations, examples, knowledge checks and FAQs.

**Your input:**

• 'The model can be told its permissions or deadline.' Authority and limits are enforced by the runtime, not by prompts.

• 'Completed means correct.' Execution status and task outcome are different things.

• 'The coding agent said it passed.' Only executed checks count; skipped or unrun checks are not passes.

• 'Offline tests prove the model works.' They prove the loop and boundaries; live quality needs a separate benchmark.

• 'Agents are always better than workflows.' Keep a workflow baseline and compare on the same cases.

### 9.3 Important Nuances

**Owner: [SME]**

Document exceptions, limitations, risks, assumptions or cases where the recommended approach does not apply.

**Your input:**

• The token budget is checked before each call with an approximate estimate, then against reported usage; it is not a tokenizer count.

• Cost is computed only from explicitly configured prices; zero configured pricing is not evidence that a provider is free.

• Live provider adapters were tested only against mock HTTP; paid calls require explicit authorization and are not part of the session.

• All incident data are synthetic; no real systems are touched.

• Learners write prompts for their coding agent rather than typing code; the reference excerpts are for review, not copying.

## 10. L&D Production & Delivery

**Owner: [L&D]**

L&D will coordinate:

- Learning design
- Presentation formatting
- Session link
- Calendar invitation
- Recording
- E-learning page
- Content editing
- Interactive elements
- Knowledge checks
- Assignment formatting
- Resource formatting
- Publishing
- Participant communication
- Learning tracking
- Feedback collection
