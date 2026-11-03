# Session 03 content development: Context retrieval and memory

> Markdown copy of [`03 Context retrieval and memory - content development.docx`](03%20Context%20retrieval%20and%20memory%20-%20content%20development.docx) for reading on GitHub. The Word document in this repository is the single source of truth; edit it, then regenerate this page with `guide-builder/content_md.py`.

## 1. Topic Overview

### 1.1 Topic Title - Tools and context: Context, retrieval and memory (Session 03)

**Owner: [SME]**

### 1.2 Short Topic Description

**Owner: [SME]**

Write 2–4 sentences explaining what the topic is about, why it matters and what learners will explore.

**Your input:**

This session builds the platform's evidence layer: the agent reads only its own tenant's sources, ranked transparently and cited by ID; the conversation is trimmed for the next model call by complete rounds, never half a round; investigation reports are versioned artifacts that refuse a stale overwrite; and memory expires. Then the same loop talks to a real cloud model for the first time: learners harden the runtime for what real models do, connect their platform to Groq with their own free key kept outside the repository, and watch in the console which model answered, where and how fast.

### 1.3 Level

**Owner: [SME + L&D]**

Select Beginner / Intermediate / Advanced and add context if useful.

**Your input:**

**Context:** L3 is the advanced, selective level of the programme for experienced software engineers. Session 03 builds on the tool boundary from Session 02 and introduces the first real-model run of the course.

Advanced

### 1.4 Prerequisites

**Owner: [SME]**

List previous topics, knowledge, tools, access or skills required. If none, write “No prerequisites.”

**Your input:**

• Session 02 completed: your project in the course GitLab group with the Lesson 02 check pack passing (12 tests), LESSON = 2, the course layout (agent_runtime/, agentic_platform/, course/) and an AGENTS.md briefing.

• The earlier prerequisites: independent Python, async code and tests, LLM foundations, and reviewing code a coding agent writes.

• Basic retrieval ideas (lexical vs embedding search) and what a database transaction guarantees.

• A free Groq account and API key, created before the session from the course page https://maxvpavlov.github.io/ciklum-innovate-l3-2026/groq-key/ (no card needed), kept private: never in a prompt, a chat or a repository.

• Your coding agent signed in to gitlab.ciklum.net, a local browser for the platform console, and a machine that can run Python 3.12 and reach api.groq.com.

### 1.5 Session Details

**Owner: [L&D]**

L&D provides date, calendar details and delivery logistics. SME provides estimated time needed and timing constraints.

**Date:** **Nov 4, 2026**

**Session link: zoom**

**Calendar invitation text:**

Draft for L&D: "L3 Building Agentic Platforms, Session 03: Context, retrieval and memory, Nov 4, 2026 (90 min). Bring your Session 02 checkpoint and your own free Groq API key (get it before the session: https://maxvpavlov.github.io/ciklum-innovate-l3-2026/groq-key/). You build tenant-scoped retrieval, bounded context, versioned artifacts and expiring memory, and connect your platform to a real cloud model for the first time. Session page: https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-03/"

**Duration (SME):** 90 minutes: 20 min discussion + 70 min guided build, practice and verification. Timing constraint: learners need their Session 02 project working and their Groq key created before the session; Groq's free tier allows about 8,000 tokens a minute per model on each account, so each learner uses their own key.

### 1.6 Speaker(s)

**Owner: [SME + L&D]**

List the main speaker, co-speakers and guest experts and clarify their roles.

**Your input:**   
Maksym Pavlov

**Role:** Maksym Pavlov is the main speaker and SME: the concept discussion and the guided build, showing each prompt and reviewing the change before learners run it in their own project, and the first live run on Groq. Learners' code is checked by the Session 03 check pack and the review prompt; the live run is observed, not graded.

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

Explain why a larger context window does not decide which information is relevant, current or authorized, and distinguish message history, source records, memory and versioned artifacts by their lifetime.

**Objective 2:**

Build, by directing a coding agent, tenant-scoped retrieval that filters authorized sources before ranking and returns source IDs and versions, and justify why filtering after a global top-k search is wrong.

**Objective 3:**

Implement context selection that keeps the instruction, the task and complete assistant/tool rounds within a budget, and demonstrate that no tool result is left without its call.

**Objective 4:**

Apply optimistic versioning to artifacts and a retention policy to memory, and explain why a stale write must fail rather than overwrite, and why memory is selected context, not truth or authority.

**Objective 5:**

Configure the platform for a real model on Groq with a key kept outside the repository, harden the runtime for real-model behaviour (spelled-out procedure, tolerant answer parsing, named provider failures, a bounded retry of refused tool calls), and interpret live runs in the console as observations, not test results.

## 3. Pre-work

**Owner: [SME]**

Define anything participants need to complete before the live session: reading, video, previous course/module, tool setup, account/access, short task, reflection question or preparation of data/files.

If nothing is required, write: “No pre-work required.”

**Pre-work:**

Complete your Session 02 checkpoint (the Session 02 after-class work): your project in the course GitLab group with the Lesson 02 check pack passing (12 tests) and LESSON = 2. Create a free Groq account and an API key following https://maxvpavlov.github.io/ciklum-innovate-l3-2026/groq-key/ and keep it private. Optional (20 min): 'Effective context engineering for AI agents' (Anthropic) and a refresher on retrieval and embeddings.

## 4. Live Session Design

### 4.1 Session Agenda

**Owner: [SME]**

Provide the proposed flow and approximate timing.

| Section | Topic | Approx. time | Format |
|---|---|---|---|
| 1 | Reconnect to INC-001 and your Session 02 checkpoint; confirm your Groq key is ready | 0–5 min | Discussion |
| 2 | Concept: four stores with different lifetimes; tenant-first retrieval; complete rounds; versions and expiry | 5–20 min | Presentation + discussion |
| 3 | Build steps 1 and 2: tenant-scoped retrieval and context selection | 20–35 min | Guided build |
| 4 | Build steps 3 and 4: versioned artifacts and expiring memory | 35–50 min | Guided build |
| 5 | Harden the runtime and connect a real model (Groq) | 50–65 min | Guided build + live demo |
| 6 | Push on each boundary: retrieval, a stale write, a shrinking context | 65–75 min | Hands-on practice |
| 7 | Verify and push (17 checks), and interpret the evidence | 75–85 min | Verification |
| 8 | Questions and handoff to Session 04 | 85–90 min | Discussion |

### 4.2 Topic-by-Topic Content

**Owner: [SME]**

For each section, provide:

Key concepts — what does the participant need to know?

Common misconceptions — what do learners frequently misunderstand?

Key message — the one thing participants should remember from this section.

**Section 1:**

Tenant-scoped retrieval

**Key concepts:** retrieval is a tool the agent calls, not a blob pasted into the prompt. The platform filters runbooks by the run's tenant, taken from Context, before ranking; ranking here is transparent word overlap with a source-ID tie break, so learners can see why a record was chosen. Every result keeps its source ID and version, and the final answer may cite only source IDs a tool returned.

**Common misconceptions:** a bigger context window removes the need for retrieval; filtering another tenant's results after a global top-k search is equivalent; lexical ranking is a toy that a vector store simply replaces.

**Key message:** filter by tenant first, then rank; keep the source ID with every piece of evidence.

**Section 2:**

Context selection by complete rounds

**Key concepts:** the next model request gets the instruction, the original task and the newest complete assistant/tool rounds that fit the budget; the full run history is kept separately for persistence and diagnosis. A task that cannot fit is rejected rather than silently truncated.

**Common misconceptions:** a shorter prompt is always better; dropping the oldest messages one by one is safe; trimming deletes history.

**Key message:** trim by complete rounds, never half a round: a tool result without its call breaks the next model request.

**Section 3:**

Versioned artifacts and expiring memory

**Key concepts:** an investigation report is an artifact with an identity and a version: a writer states the version it expects to replace, and a stale expectation fails as stale_artifact_version. Memory is a tenant-scoped convenience with an expiry: an expired value reads as nothing, also after the database is reopened, and another tenant never sees it.

**Common misconceptions:** the last write is the right one; on a version conflict just retry with the newest number; memory is a source of truth or of permission.

**Key message:** artifacts keep their versions and refuse stale writes; memory expires and never authorizes anything.

**Section 4:**

The same loop, a real model

**Key concepts:** only the provider changes. Real models need what the mock never did: the system prompt spells out the tool procedure and the answer format; the given tool definitions describe what each tool returns and every argument; the loop takes the first JSON object from a reply (a fence or a sentence before it is accepted, a reply with none fails as invalid_final_answer); a tool call Groq refuses (tool_use_failed) is requested again at most twice, then fails as provider_tool_call_invalid; rate limits, outages and timeouts end the run with named codes. MODEL_REASONING_EFFORT=low lets the course model think briefly before each call. The key lives in ~/agentic-course/groq.env, outside the repository, loaded only into the platform process; the console's run page shows the model, host and time of every call, including a request that failed.

**Common misconceptions:** a live run is a test result; a passed citation check means the answer is right; a prompt that works on one model works on another; the checks need the key.

**Key message:** the checks stay on the exact mock; a live run is an observation of one model on one day, reported as seen.

### 4.3 Interactive Activities

**Owner: [SME content + L&D learning design]**

Identify where participants should actively engage.
- Poll**✔ (retrieval block) Could we search all runbooks, take the top 10 and then drop other tenants' results?**
- Discussion**✔ (opening) Which of today's four stores holds what, and how long should each live?; (65–75 min) predict each boundary's result before it runs**
- Case study**✔ (real-model block) The live INC-003 answer names a cause and the citation check passed: is it right?**
- Breakout activity
- Quiz
- Hands-on exercise**✔ (20–75 min) Learners run the build prompts, harden and connect their platform, and push on each boundary in their own project**
- Live demo**✔ (20–65 min) The instructor shows each prompt and its change, and the first live run on Groq in the console**
- Problem-solving activity**✔ (step 3) Decide what a writer should do after a stale_artifact_version failure**
- Reflection**✔ (close) Mark the evidence layer and the real-model connection on your platform blueprint**

**Activity details (SME content and L&D will turn into activity in zoom or whiteboard):**

For each activity include: Purpose • Instructions • Time • Expected outcome • Debrief / discussion points.

**1. Discussion: four stores, four lifetimes.** Purpose: separate what the model reads from where it is kept. Instructions: draw the message history, runbook sources, memory and versioned artifacts; learners place a tool observation, a runbook, the task state and a saved report. Time: 5 min. Expected outcome: each store named with its lifetime, and permissions kept outside all four, in Context. Debrief: what happens when memory disagrees with the current logs?

**2. Poll: filter after a global top-10?** Options: yes, it is the same / no / only if the index is small. Correct: no. Time: 2 min. Debrief: filtering after ranking can return too few authorized results and leaks that other tenants' sources exist; the access boundary belongs on the searched population.

**3. Guided build: the four build steps.** Purpose: learners build the evidence layer in their own project. Instructions: for each step the instructor explains it and runs the prompt; learners run the same prompt and compare the agent's change and the checks with the code excerpt on the session page. Time: 30 min. Expected outcome: retrieval, context selection, artifacts and memory built, with the Lesson 03 checks passing step by step. Debrief: where does the tenant come from in your retrieval code?

**4. Guided build and live demo: a real model.** Purpose: run the same loop on a real cloud model. Instructions: the Harden prompt adds the spelled-out system prompt, tolerant answer parsing, named provider failures and the bounded retry; the Connect prompt writes ~/agentic-course/groq.env outside the repository, restarts the platform with it, and submits INC-001, then INC-003 once INC-001 has finished. Learners read the model, host, tokens and time on the run page. Time: 15 min. Expected outcome: a cited INC-001 answer from Groq, or a named failure code the learner can explain. Debrief: what changed in the loop? Only the provider.

**5. Case study: right answer or plausible answer?** Purpose: separate a valid citation from a correct conclusion. Instructions: show a live INC-003 run whose answer names a cause while the citation check passes. Time: 5 min. Expected outcome: learners notice that INC-003's evidence names no cause, so the supported answer is insufficient_evidence; the citation check proves the sources were observed, not that the reasoning is sound. Debrief: this is why Session 04 measures outcomes.

**6. Hands-on: push on each boundary.** Purpose: make every boundary observable. Instructions: predict, then run: the same retrieval for Astro and Locomotive, a stale artifact write, and a long synthetic conversation with a shrinking max_chars, checking that every tool result keeps its call; compare the outcome before and after selection. Time: 10 min. Expected outcome: different sources per tenant, stale_artifact_version, and no orphaned tool-call IDs. Debrief: which reduction changed the outcome, and how would you know without a test?

**7. Reflection: the platform blueprint.** Purpose: connect today's work to the platform. Instructions: mark the evidence layer and the real-model connection on your blueprint, and note that from Session 08 the platform saves each run's answer in this artifact store. Time: 3 min. Expected outcome: an updated sketch kept for the next sessions.

### 4.4 Practical Application After the Session

**Owner: [SME]**

Describe what participants will actually do.

**Task:**

Finish the Session 03 build in your own project, then watch your platform answer on a real model.

**Instructions:**

• Finish any prompt you did not complete in class, in order: Prepare, Add the check pack, Build steps 1–4, Harden the runtime for a real model, Connect the platform to Groq, the exercise, Verify and push, and Review.

• Read each change before running the next prompt. The check pack must pass unchanged; never edit it to get a pass.

• Keep your Groq key in ~/agentic-course/groq.env only; never paste it into a prompt, a chat or a file in your repository. The checks run on the mock and do not need it.

• Practice: submit INC-003 three times on Groq and compare with the mock. Does the real model ever claim a cause the evidence does not support, and would the citation check catch it?

• Practice: put a different ranking function behind context_tools and compare the supported outcomes, not just the scores; then add a conflicting-memory case and decide which source should win and why.

• Read 'Effective context engineering for AI agents' (Anthropic) and the LangGraph persistence and memory overview (about 1 hour).

**Expected result:**

Your project in the course GitLab group with the Lesson 03 check pack passing unchanged (17 tests), LESSON = 3, a Lesson 03 entry in AGENTS.md, a short note on your live INC-001 and INC-003 runs (status, cause, cited evidence, model, host, time) and your INC-003 comparison. Estimated time: 2–3 hours.

**Feedback / debrief points:**

• Did the coding agent's claims match the check output? Unrun or skipped checks are not passes.

• Did your live runs differ from the mock, and from each other? What did the failure codes, if any, tell you?

• Which store would you put a customer's preference in, and which an incident report, and why?

## 5. Presentation

### 5.1 Presentation Content

**Owner: [SME]**

Provide the presentation content or draft. Recommended logic: Context → Concept → Example → Application → Practice → Summary.

**Presentation / slide deck:**

The Session 03 page is the presentation, with Read and Present views (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-03/); a prompts-only page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-03-just-prompts/) and the Groq key page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/groq-key/) support it. No slide deck is made: the session page replaces it. Outline:

• 1. Bring your own free Groq key: why each learner needs their own, and why it never enters a prompt or repository.

• 2. Where we are: yesterday the platform decided what a tool may do; today it decides what the model gets to read.

• 3. Four stores with different lifetimes: messages, sources, memory and artifacts; permissions stay in Context.

• 4. Filter by tenant first, then rank: transparent retrieval with source IDs.

• 5. Trim the conversation by complete rounds, never half a round.

• 6. Artifacts keep their versions; memory expires.

• 7. The same loop, a real model: only the provider changes; what real models do that the mock never did.

• 8. What your console shows for a live run: model, host, tokens and time of every call.

• 9. Application: the prepare and check-pack prompts, the four build prompts, Harden and Connect.

• 10. Practice: push on each boundary; verification evidence (17 passed).

• 11. Summary, recovery prompts and the after-class assignment.

## 6. Session Wrap-up

### 6.1 Conclusions / Key Takeaways

**Owner: [SME]**

Define 3–5 essential messages participants should leave the session with. These will also be used in e-learning.

**Key takeaway 1:**

Filter by tenant first, then rank, and keep the source ID with every piece of evidence.

**Key takeaway 2:**

Trim the conversation by complete rounds, never half a round; keep the full history elsewhere.

**Key takeaway 3:**

Artifacts keep their versions and refuse a stale overwrite; memory expires and never authorizes anything.

**Key takeaway 4:**

The same loop runs on a real model when only the provider changes, provided the runtime spells out the procedure and names every failure.

**Key takeaway 5:**

The checks stay on the exact mock; a live run is an observation of one model on one day, reported as seen.

### 6.2 Lesson Reflection

**Owner: [SME]**

Provide 2–4 questions that help participants connect the topic to their own work.

Suggested framing: “Before moving on, consider:”

**Reflection question 1:**

Where in your systems does an agent or service read data across a tenant or customer boundary before filtering it?

**Reflection question 2:**

Which of your stored facts would you treat as memory that expires, and which as a versioned record that must never be silently overwritten?

**Reflection question 3:**

If your team switched the model behind an agent tomorrow, what would you have to spell out that the old model did implicitly, and how would you know it still works?

### 6.3 What's Next

**Owner: [SME + L&D]**

Identify the logical next step: next session, next topic, practice assignment, certification or deeper learning.

**What's next:**

Session 04, Build the agent evaluation harness (90 min): the same cases run many times and scored on outcome, evidence and tool policy, so a change is judged by measurement rather than by one good run. Bring your Session 03 checkpoint.

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

• Video 1 (5 min): four stores with different lifetimes, and why a bigger context window does not decide relevance or authority.

• Video 2 (5 min): tenant-first retrieval with source IDs, and context selection by complete rounds.

• Video 3 (4 min): versioned artifacts and a stale write; memory with an expiry.

• Video 4 (6 min): the same loop on a real model: hardening, the key outside the repository, and reading a live run in the console.

• Knowledge check (7.4) and the self-paced assignment (7.5).

Source material: the Session 03 page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-03/), instructor guide 03, and the Groq key page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/groq-key/).

### 7.3 Examples / Use Cases

**Owner: [SME]**

Provide examples that can stand on their own in e-learning. Include enough context for someone who was not at the live session.

**Your input:**

**Example 1: one query, two tenants.** The same payments query runs for Astro and for Locomotive. Astro's retrieval returns the connection-pool runbook; Locomotive's returns its quota runbook; neither ever sees the other's sources, because the tenant from Context filters the runbooks before ranking. Each result carries its source ID and version, so the final answer can cite exactly what it used.

**Example 2: a stale write fails.** Two writers read the INC-001 report at version 1. The first saves version 2. The second still expects version 1, so its write fails as stale_artifact_version instead of silently replacing the newer report; it must read version 2 and decide again.

**Example 3: a real model, named failures.** With a learner's Groq key, INC-001 runs on qwen/qwen3.8-27b. The run page shows each model call with its model, host, tokens and time. If Groq refuses a malformed tool call, the provider asks again at most twice and then the run fails as provider_tool_call_invalid; a rate limit fails as provider_rate_limited, and a request with no reply within 15 seconds as provider_timeout. A failed request still appears on the run page as a model call with its error. The mock and the checks are unaffected.

### 7.4 Knowledge Check

**Owner: [SME]**

Provide 3–5 questions testing the most important concepts. Include question, options if applicable, correct answer and explanation. L&D adapts them into the final interaction.

**Your input:**

**Q1. Where should the tenant filter go in retrieval?** A) after ranking all tenants' sources  B) before ranking, on the searched population  C) in the system prompt. Correct: B. Filtering afterwards can return too few authorized results and reveals that other sources exist; the model must never decide the tenant.

**Q2. The selector must cut a long conversation. What may it drop?** A) the oldest messages one by one  B) whole older assistant/tool rounds  C) the original task. Correct: B. Dropping half a round leaves a tool result without its call and breaks the next request; the task is kept or the request is rejected.

**Q3. A write expects version 1 but the artifact is at version 2. What should happen?** A) overwrite, last write wins  B) retry automatically with version 2  C) fail as stale_artifact_version so the writer reads the newer version first. Correct: C. An automatic retry would turn conflict detection into an unconditional overwrite.

**Q4. A live run on Groq answers INC-003 with a specific cause, and the citation check passes.** A) the answer is correct  B) the cited sources were observed, but the evidence may not support the cause  C) the model is broken. Correct: B. The citation check proves provenance, not reasoning; INC-003's evidence names no cause.

**Q5. Where does a learner's Groq key belong?** A) in the repository's .env  B) in the prompt, so the agent can use it  C) in ~/agentic-course/groq.env, outside the repository, loaded only into the platform process. Correct: C. The checks run on the mock and never need it.

### 7.5 Practice / Assignment

**Owner: [SME]**

Create a task that can be completed without attending the live session. Include task, context, expected output, estimated time, success criteria and resources.

**Your input:**

**Task:** Using your own coding agent and the learner kit in the course repository, build the Session 03 checkpoint: tenant-scoped retrieval, context selection by complete rounds, versioned artifacts and expiring memory, a runtime hardened for real models, and your platform connected to Groq.

**Context:** Start from your Session 02 checkpoint. Run the prompts on the Session 03 page in order (Prepare, Add the check pack, Build steps 1–4, Harden, Connect, the exercise, Verify and push, Review); the same prompts are in LEARNER_PROMPTS.md (Lesson 03). Get your free Groq key first from https://maxvpavlov.github.io/ciklum-innovate-l3-2026/groq-key/. No paid model access is needed.

**Expected output:** your repository in the course GitLab group with the Lesson 03 check pack passing unchanged (17 tests), LESSON = 3, the lab output (the cited INC-001 answer, artifact version 1, expired memory and cross-tenant artifact both null), and a short note on your live runs.

**Estimated time:** 3 hours.

**Success criteria:** retrieval returns only the selected tenant's sources with their IDs; selection keeps every tool result with its call; a stale artifact write fails; expired memory is gone, also after a reopen; a fenced answer is accepted and a reply without JSON fails by name; provider failures are named; the key never appears in the repository, a prompt or the chat.

**Resources:** the Session 03 page, learner-kit/lessons/03 in the course repository, LEARNER_PROMPTS.md (Lesson 03), the Groq key page, and the 7.7 reading.

### 7.6 Lesson Reflection

**Owner: [SME]**

Provide reflection questions for independent learners. These may be the same as or adapted from the live session.

**Your input:**

Use the three live-session questions (6.2), plus: 'Which answer of your own agents would you trust only after checking that its evidence supports it, not just that its sources exist?'

### 7.7 Deep Dive / Additional Resources

**Owner: [SME]**

Provide articles, videos, books, documentation, research, internal resources, tools, tutorials or examples. Distinguish Recommended / Essential from Optional / Deep Dive.

**Your input:**

**Essential:** Effective context engineering for AI agents (Anthropic): https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

**Essential:** Persistence and memory stores (LangGraph): https://docs.langchain.com/oss/python/langgraph/persistence

**Optional / deep dive:** Groq OpenAI compatibility (https://console.groq.com/docs/openai) and the course's record of how the course model was chosen and tuned, inference-candidates.md in the course repository.

**Optional / deep dive:** one finished implementation, the course reference at tag lesson-03 (agent_runtime/context.py, agent_runtime/core.py, agent_runtime/providers.py) and TESTING.md; read it after building your own.

### 7.8 What's Next

**Owner: [L&D + SME]**

Define the next topic, recommended learning path, practice or next action.

**Your input:**

Next: Session 04, Build the agent evaluation harness. Recommended path: complete the 7.5 assignment first; Session 04 starts from the Session 03 checkpoint and measures the agent you just connected.

## 8. Materials & Assets

**Owner: [SME]**

Indicate which assets are needed and provide them where applicable.
- Presentation**✔ the Session 03 page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-03/), with Read and Present views; the prompts-only page and the Groq key page**
- Speaker notes**✔ SAY sections of instructor guide 03**
- Script**✔ instructor guide 03 (complete)**
- Examples**✔ three worked examples in 7.3**
- Case study**✔ 'Right answer or plausible answer?' with a live INC-003 run (activity 5)**
- Demo**✔ the learner kit (learner-kit/lessons/03 in the course repository); the reference tags lesson-02 → lesson-03; a Groq key for the instructor's live run**
- Screenshots**✔ the console's run page for a live run (model, host, tokens and time per call), on the Session 03 page**
- Diagrams**✔ four stores and their lifetimes, tenant-first retrieval, complete-round selection, artifacts vs memory, and the loop with a real model, on the Session 03 page**
- Templates**✔ groq.env, the key file outside the repository (its contents are shown on the Groq key page)**
- Sample files**✔ synthetic incidents and runbooks for Astro and Locomotive; the given course/fixtures.py with described tools and arguments, and the console's run view, in learner-kit/lessons/03/given**
- Quiz questions**✔ five questions in 7.4**
- Practice assignment**✔ 7.5 and LEARNER_PROMPTS.md, Lesson 03**
- Additional resources**✔ 7.7**
- Other:

## 9. Content Accuracy & SME Notes

### 9.1 Important Terminology

**Owner: [SME]**

List terminology that must be used consistently.

**Your input:**

• Retrieval as a tool: runbook_search returns tenant-filtered, ranked sources with their source IDs and versions.

• Tenant boundary: the tenant comes from the run's Context, set by the platform; the model cannot choose it.

• Source ID: the identifier a final answer cites; an answer may cite only source IDs a tool returned.

• Context selection (select_context): what the next model request contains: instruction, task and the newest complete rounds within max_chars; the full history is kept separately.

• Complete round: an assistant message with tool calls together with every tool result for those calls.

• Artifact and version: a saved output with an identity; a write states the version it expects to replace.

• stale_artifact_version: the failure when that expectation is out of date.

• Memory and retention: tenant-scoped convenience with an expiry; expired values read as nothing.

• Provider: the adapter that talks to a model; HTTPProvider for Groq's OpenAI-compatible API, the mock offline.

• Named provider failures: provider_rate_limited (429), provider_unavailable (5xx), provider_http_<status>, provider_timeout, provider_tool_call_invalid, and invalid_final_answer for a reply with no JSON object.

• MODEL_REASONING_EFFORT: sent as reasoning_effort; low lets the course model think briefly before each call.

• groq.env: the learner's key file in ~/agentic-course, outside the repository, loaded only into the platform process.

### 9.2 Common Misconceptions

**Owner: [SME]**

List frequent misunderstandings. This will inform explanations, examples, knowledge checks and FAQs.

**Your input:**

• 'A bigger context window solves this.' It does not decide what is relevant, current or authorized.

• 'Filter after the global top-k.' That returns too few authorized results and leaks that other sources exist.

• 'Trimming message by message is fine.' A tool result without its call breaks the next request; trim whole rounds.

• 'Last write wins.' A stale write must fail; an automatic retry with the newest version is an overwrite in disguise.

• 'Memory is truth.' It is selected context that can be stale; it never grants permission.

• 'A live run that passes is a test.' It is an observation; the checks run on the exact mock, and a passed citation check proves provenance, not correctness.

### 9.3 Important Nuances

**Owner: [SME]**

Document exceptions, limitations, risks, assumptions or cases where the recommended approach does not apply.

**Your input:**

• Ranking is deliberately lexical and visible; an embedding or hybrid retriever can replace it behind the same tool contract if tenant filtering, provenance and the return shape stay.

• Memory expiry is enforced on read; production cleanup, encryption and storage policy need further decisions.

• Live results vary by model, day and load. In the course's November 2026 tests qwen/qwen3.8-27b on Groq succeeded on INC-001 and INC-003 with the hardened runtime and reasoning effort low, and in two learner dry runs of the Session 03 prompts on 3 November INC-001 completed 2 of 2 and INC-003 2 of 3 (one Groq timeout); the sample is small, and free model lists and limits change, so the instructor reruns the live step shortly before the session.

• Groq's free tier allows about 8,000 tokens a minute per model on each account and one investigation uses about 3,000, so learners submit INC-003 only after INC-001 finishes, and each learner needs their own key.

• Token counts from the mock (20 per tool call, 35 per answer) are teaching measurements; live counts come from the endpoint and are not cost claims.

• All incident data are synthetic, and the demo identities are for loopback use only.

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
