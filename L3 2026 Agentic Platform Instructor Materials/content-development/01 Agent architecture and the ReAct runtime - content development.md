# Session 01 content development: Agent architecture and the ReAct runtime

> Markdown copy of [`01 Agent architecture and the ReAct runtime - content development.docx`](01%20Agent%20architecture%20and%20the%20ReAct%20runtime%20-%20content%20development.docx) for reading on GitHub. The Word document in this repository is the single source of truth; edit it, then regenerate this page with `guide-builder/content_md.py`.

## 1. Topic Overview

### 1.1 Topic Title - Agent foundations: Agent architecture and the ReAct runtime (Session 01)

**Owner: [SME]**

### 1.2 Short Topic Description

**Owner: [SME]**

Write 2–4 sentences explaining what the topic is about, why it matters and what learners will explore.

**Your input:**

This first session of "Building Agentic Platforms" opens the course: why enterprise work needs several agents working together, why that calls for a platform, and the parts of the platform learners will build over 12 sessions. It then explains how one AI agent actually works: a model proposes an action, a runtime decides whether to execute it, and a tool returns an observation, in a loop bounded by explicit limits. Every later capability (tools, memory, subagents, remote agents, the tool gateway, identity and the console) is built around this loop. In class the instructor directs a coding agent to build that bounded runtime for a sandbox incident investigation; after the session each learner repeats the same prompts in their own project.

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

• Access to an AI coding agent (for example Claude Code) and to the course GitLab group (you receive an invitation); the setup prompt installs the GitLab CLI. No paid model account is needed: the course runs on an offline, deterministic mock provider.

• Local Python 3.12 environment (the coding agent installs pinned dependencies) or Docker.

• None of this has to be ready for Session 01 itself: the session is a demonstration, and learners set up their project afterwards with the setup prompt.

### 1.5 Session Details

**Owner: [L&D]**

L&D provides date, calendar details and delivery logistics. SME provides estimated time needed and timing constraints.

**Date:** **Oct 28, 2026**

**Session link: zoom**

**Calendar invitation text:**

Draft for L&D (please add the link): "L3 Building Agentic Platforms, Session 01: Agent architecture and the ReAct runtime (120 min: 30 min discussion + 90 min instructor demonstration). We open the course and start the incident-investigation platform you will extend all course long. Nothing to prepare: after the session you repeat the demonstrated prompts in your own project. Session page: https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-01/"

**Duration (SME):** 120 minutes. Timing constraint: the demonstration needs about 45 uninterrupted minutes with the session page and a terminal shared on screen. Learners need nothing installed to attend.

### 1.6 Speaker(s)

**Owner: [SME + L&D]**

List the main speaker, co-speakers and guest experts and clarify their roles.

**Your input:**   
Maksym Pavlov

**Role:** Maksym Pavlov is the main speaker and SME: the course opening and concept discussion, and the live demonstration of the setup prompt, the check pack and each build step. Learners' own code is checked after the session by the Session 01 check pack and the review prompt. Co-speakers or mentors: none named yet.

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

Explain the ReAct loop (the model reasons and proposes an action, the runtime executes it, and the observation feeds the next step) and why an incident investigation needs it rather than a hard-coded sequence.

**Objective 2:**

Build, by directing a coding agent, a ReAct runtime bounded by step, token, time and repeated-action limits.

**Objective 3:**

Design a run contract in which application code, not the model, owns tenant identity, permissions and limits.

**Objective 4:**

Evaluate a run from its event log and cited answer, distinguishing a completed run from a supported conclusion.

**Objective 5:**

Describe the target agentic platform (agent registry, MCP tool gateway, identity and credentials, console, operations), when a task needs more than one agent, and where the ReAct runtime sits within it.

## 3. Pre-work

**Owner: [SME]**

Define anything participants need to complete before the live session: reading, video, previous course/module, tool setup, account/access, short task, reflection question or preparation of data/files.

If nothing is required, write: “No pre-work required.”

**Pre-work:**

No pre-work required. The readings and the project setup are part of the after-class work (4.4).

## 4. Live Session Design

### 4.1 Session Agenda

**Owner: [SME]**

Provide the proposed flow and approximate timing.

| Section | Topic | Approx. time | Format |
|---|---|---|---|
| 1 | Course opening: why agent teams, when to split work, why a platform and its parts, and the incident premise | 0–17 min | Presentation + discussion |
| 2 | Concept: the ReAct loop, one real run, who owns identity and limits | 17–30 min | Presentation + discussion |
| 3 | Instructor demo: the setup prompt, the check pack and build steps 1–4 on a fresh project | 30–75 min | Live demo |
| 4 | Break it on purpose: learners predict each guard's failure, the instructor runs it | 75–95 min | Discussion + live demo |
| 5 | Verification evidence, the review prompt and pushing the checkpoint to GitLab | 95–110 min | Live demo |
| 6 | Questions and the after-class assignment: repeat every prompt in your own project | 110–120 min | Discussion |

### 4.2 Topic-by-Topic Content

**Owner: [SME]**

For each section, provide:

Key concepts — what does the participant need to know?

Common misconceptions — what do learners frequently misunderstand?

Key message — the one thing participants should remember from this section.

**Section 1:**

Why agentic platforms, and the investigation premise

**Key concepts:** single agents are everyday tools, while enterprise work needs agents that work together: when the work outgrows one context, is better done in a clean context, needs a different model per sub-task, or needs access isolated to one system or person. A platform spawns, configures, hosts and governs those agents and adds the control points: who called what, on whose behalf, when a run stops, whether version 2 is better, how agents work together and what actually happened. The course builds one: an incident-investigation platform for two fictional companies, Astro and Locomotive.

**Common misconceptions:** more agents are always better (each one adds cost, latency and failure modes and has to earn its place); a platform is only infrastructure (it is where identity, policy, evaluation and audit live).

**Key message:** a platform is the natural next step for agentic applications; today we build its core, the agent runtime, whose contracts and events every later component relies on.

**Section 2:**

The ReAct loop and the run contract

**Key concepts:** the ReAct loop: the model reasons and proposes an action, the runtime decides whether and how to execute it, and the observation feeds the next step. An AI investigation platform is worth building where incidents are too varied to follow a hard-coded sequence. Context (tenant, role, permitted tools, run id) is owned by application code; Run holds messages, events and the answer; Limits bound steps, tokens, elapsed time and output size. Provider adapters normalize OpenAI-compatible and Anthropic responses into one Reply; a deterministic mock provider makes behaviour reproducible without credentials.

**Common misconceptions:** an agent is always better than a hard-coded sequence (measure every change against a baseline on the same cases); the model can be trusted to state its own permissions; a passing offline test proves live-model quality; zero configured price means a provider is free.

**Key message:** anything the model produces is untrusted input; authority is constructed by the application.

**Section 3:**

The bounded loop, guards and evidence

**Key concepts:** model proposes a tool call, the runtime records it as pending, executes it and appends the observation with the same call id. Guards stop the run with a named code (step_budget, token_budget, TimeoutError, repeated_action). The event log records actions and usage, not hidden reasoning; from Session 08 the platform console renders it as a run timeline.

**Common misconceptions:** a fluent answer is a successful investigation (success needs a cause, cited evidence, or an explicit insufficient-evidence result); a completed run means the incident is solved; a coding agent's 'done' message is evidence; a timeout can be enforced by instructing the model.

**Key message:** every stop is a controlled, explained outcome, and evidence comes from runs and checks, not from claims.

### 4.3 Interactive Activities

**Owner: [SME content + L&D learning design]**

Identify where participants should actively engage.
- Poll**✔ (concept block) Which limit catches a provider that hangs without returning tokens?**
- Discussion  ✔ (opening) What must a successful investigation contain? (75–95 min) Predict each guard's failure before it runs.
- Case study
- Breakout activity
- Quiz
- Hands-on exercise  ✔ (after the session) Repeat the demonstrated prompts and the fault-injection exercise in your own project
- Live demo  ✔ (30–75 min) The instructor runs the setup prompt, adds the check pack and demonstrates each bounded build step
- Problem-solving activity**✔ (step 3) Trace one tool-call id from proposal to observation**
- Reflection**✔ (close) Redraw the platform blueprint and mark today's box**

**Activity details (SME content and L&D will turn into activity in zoom or whiteboard):**

For each activity include: Purpose • Instructions • Time • Expected outcome • Debrief / discussion points.

**1. Discussion: what does success look like?** Purpose: set acceptance criteria before building. Instructions: show the synthetic INC-001 record (payments slow after a deployment); ask learners to list what a good investigation must contain. Time: 5 min. Expected outcome: likely cause, cited source, explicit 'insufficient evidence' when data is missing. Debrief: a fluent paragraph is not an acceptance test.

**2. Poll: which component owns a timeout?** Purpose: separate runtime responsibilities from model behaviour. Options: the model / the tool / the runtime / the provider. Correct: the runtime. Time: 2 min. Debrief: an instruction to the model cannot enforce elapsed time; only the loop can.

**3. Live demo: setup and the four build steps.** Purpose: show the way of working that learners repeat after the session. Instructions: the instructor runs the setup prompt on a fresh project and adds the Session 01 check pack, then for each build step explains it, runs the prompt, and reviews the agent's change and the checks against the code excerpt on the session page. Time: 45 min. Expected outcome: learners can name each prompt, what it changes and what evidence it should produce. Debrief: ask learners to explain one boundary in the agent's change.

**4. Problem-solving: trace a tool-call id.** Purpose: understand why call ids must be preserved. Instructions: follow the log_lookup call for INC-001 from the assistant message to the tool message. Time: 5 min. Expected outcome: learners can explain what breaks if a result is appended without its call. Debrief: pending calls are the future recovery boundary.

**5. Discussion: break it on purpose.** Purpose: make every stop condition observable. Instructions: for each change (one step, a tiny token budget, a short deadline with a slow mock provider, a repeating provider) learners predict the failure, then the instructor runs it. Time: 20 min. Expected outcome: step_budget, token_budget, TimeoutError and repeated_action observed, then the normal cited answer restored. Debrief: compare predictions with observations and explain discrepancies. Learners repeat the exercise in their own project after the session.

**6. Reflection: platform blueprint.** Purpose: connect today's build to the whole course. Instructions: redraw the blueprint and mark the box built today; note which later console views already have their data in today's event log. Time: 5 min. Expected outcome: a personal architecture sketch kept for the next sessions.

### 4.4 Practical Application After the Session

**Owner: [SME]**

Describe what participants will actually do.

**Task:**

Repeat today's prompts in your own project, then extend it.

**Instructions:**

• Run the prompts on the Session 01 page in order: the setup prompt (it clones the course repository, creates your project from the learner kit and pushes it to a new private repository in the course GitLab group), Add the check pack, Build steps 1–4, the exercise, Verify and push, and Review.

• Read each change before running the next prompt. The check pack must pass unchanged; never edit it to get a pass.

• Read 'Building effective agents' (Anthropic) and the ReAct paper (about 1 hour).

• Extension: ask your coding agent to add a missing-incident scenario (for example INC-404) and define what a supported insufficient_evidence answer looks like.

• Extension: write INC-001's investigation as a hard-coded sequence and run it and the agent loop on all three tickets; record step counts, stop reasons and error handling.

• Redraw the platform blueprint and note which later console views the event log can already feed.

**Expected result:**

Your project in the course GitLab group with the Lesson 01 check pack passing unchanged (7 tests) and LESSON = 1, plus a short comparison table and an updated blueprint sketch. Estimated time: 2–3 hours.

**Feedback / debrief points:**

• Did the coding agent's claims match the check output? Unrun or skipped checks are not passes.

• Where did the hard-coded sequence give a wrong or unsupported answer, and why?

• Which limit fired first in each failure case, and was the failure explained rather than an unexplained exception?

## 5. Presentation

### 5.1 Presentation Content

**Owner: [SME]**

Provide the presentation content or draft. Recommended logic: Context → Concept → Example → Application → Practice → Summary.

**Presentation / slide deck:**

The Session 01 page is the presentation, with Read and Present views (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-01/). The full instructor script is in instructor guide 01. Outline (Context → Concept → Example → Application → Practice → Summary):

• 1. Title and course promise: build one agentic platform in 12 sessions.

• 2. Why agent teams: single agents are everyday tools; enterprise work needs orchestrated agents.

• 3. When to split the work across agents: context size, a clean context, a model per sub-task, isolated access.

• 4. Why a platform, and its parts: the control points and the map of what the course builds.

• 5. How we work: coding agents, checkpoints, evidence over claims, offline synthetic data.

• 6. The premise: the incident-investigation platform, Astro's tickets, what a runbook is, and INC-001.

• 7. Concept: the ReAct loop as three boxes, and why an agent rather than a hard-coded sequence.

• 8. Example: one real run of INC-001, step by step.

• 9. Concept: who owns identity and limits; the four guards.

• 10. Application: the setup prompt, the check pack and the four build prompts.

• 11. Practice: break it on purpose, then verification evidence and the push to GitLab.

• 12. Summary and the after-class assignment.

## 6. Session Wrap-up

### 6.1 Conclusions / Key Takeaways

**Owner: [SME]**

Define 3–5 essential messages participants should leave the session with. These will also be used in e-learning.

**Key takeaway 1:**

An agent is a ReAct loop: the model reasons and proposes, the runtime decides and executes, the tool returns an observation.

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

Which task in your current project would be better served by a hard-coded sequence than by an agent, and why?

**Reflection question 2:**

What does your team currently accept as evidence that an AI-assisted change works?

**Reflection question 3:**

Which limit would you need first if you ran an agent against a production system, and who should own it?

### 6.3 What's Next

**Owner: [SME + L&D]**

Identify the logical next step: next session, next topic, practice assignment, certification or deeper learning.

**What's next:**

Session 02, Reliable tools and MCP integration (120 min): validated tool contracts, application-owned permissions, an approval gate for mock remediation and real MCP transport. It starts from your Session 01 checkpoint in your GitLab repository.

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

• Video 1 (5 min): why agent teams need a platform, what an agent is, agent vs hard-coded sequence, and the platform blueprint.

• Video 2 (6 min): the run contract and why the application owns authority.

• Video 3 (6 min): walkthrough of one INC-001 run and its event log.

• Video 4 (4 min): guards and failure codes, with the fault-injection demo.

• Knowledge check (7.4) and the self-paced assignment (7.5).

Source material: the Session 01 page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-01/), instructor guide 01 (SAY sections) and the lesson-01 lab output.

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

**Task:** Using your own coding agent and the learner kit in the course repository, build the Session 01 checkpoint: a bounded single-agent runtime for the sample incident.

**Context:** Run the prompts on the Session 01 page in order, starting with the setup prompt, which creates your project and its repository in the course GitLab group; the same prompts are in LEARNER_PROMPTS.md (Lesson 01). No paid model account is needed.

**Expected output:** your repository in the course GitLab group with the Lesson 01 check pack passing unchanged (7 tests), the lab output for INC-001 citing log-astro-001 and rb-pool-v1, and a short note explaining each guard you triggered.

**Estimated time:** 2–3 hours.

**Success criteria:** INC-001 answers connection_pool_exhaustion with observed sources; the repeating provider stops with repeated_action; step, token and time limits each produce their expected failure; both provider request-shape tests pass without real credentials.

**Resources:** the Session 01 page, learner-kit/lessons/01 in the course repository, LEARNER_PROMPTS.md (Lesson 01).

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

**Optional / deep dive:** one finished implementation, the course reference at tag lesson-01 (incident/core.py, incident/providers.py) and TESTING.md; read it after building your own.

### 7.8 What's Next

**Owner: [L&D + SME]**

Define the next topic, recommended learning path, practice or next action.

**Your input:**

Next: Session 02, Reliable tools and MCP integration. Recommended path: complete the 7.5 assignment first; Session 02 starts from that checkpoint.

## 8. Materials & Assets

**Owner: [SME]**

Indicate which assets are needed and provide them where applicable.
- Presentation  ✔ the Session 01 page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-01/), with Read and Present views
- Speaker notes**✔ SAY sections of instructor guide 01**
- Script**✔ instructor guide 01 (complete)**
- Examples**✔ three worked examples in 7.3**
- Case study
- Demo  ✔ the learner kit (learner-kit/ in the course repository); the reference tags lesson-00 → lesson-01 are the instructor's answer key
- Screenshots
- Diagrams  ✔ the orchestration, platform blueprint and ReAct loop diagrams on the Session 01 page
- Templates
- Sample files  ✔ synthetic incidents and runbooks in learner-kit/lessons/01/given
- Quiz questions**✔ five questions in 7.4**
- Practice assignment**✔ 7.5 and LEARNER_PROMPTS.md, Lesson 01**
- Additional resources**✔ 7.7**
- Other:

## 9. Content Accuracy & SME Notes

### 9.1 Important Terminology

**Owner: [SME]**

List terminology that must be used consistently.

**Your input:**

• Agent vs hard-coded sequence: an agent chooses the next permitted action from observations; a hard-coded sequence's steps are fixed in advance.

• Runtime (the loop): the code that calls the model, executes permitted tools and enforces limits.

• Run, Context, Limits: run state; application-owned identity and permissions; step, token, time and output bounds.

• Tool call / observation: a model's proposed action and the tool's result, linked by the same call id.

• Event log: recorded actions and usage of a run (not the model's hidden reasoning).

• Mock (fixture) provider: a deterministic stand-in for a model; its 'tokens' are teaching metrics, not real usage or cost.

• Checkpoint: the tagged state of a learner's project at the end of a session. The course's own lesson-NN tags are the instructor's answer key.

• Learner kit and check pack: the starter project, the given files and each lesson's tests, in learner-kit/ of the course repository; a lesson's check pack fails until its capability is built.

• Given files: synthetic data and deterministic test doubles, such as the mock provider, that everyone uses unchanged.

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

• 'An agent is always better than a hard-coded sequence.' Measure against a baseline on the same cases.

### 9.3 Important Nuances

**Owner: [SME]**

Document exceptions, limitations, risks, assumptions or cases where the recommended approach does not apply.

**Your input:**

• The token budget is checked before each call with an approximate estimate, then against reported usage; it is not a tokenizer count.

• Cost is computed only from explicitly configured prices; zero configured pricing is not evidence that a provider is free.

• Live provider adapters were tested only against mock HTTP; paid calls require explicit authorization and are not part of the session.

• All incident data are synthetic; no real systems are touched.

• Learners write prompts for their coding agent rather than typing code. The code excerpts on the session page show one way to write it; the check pack, not a comparison with the reference, proves a learner's own implementation.

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
