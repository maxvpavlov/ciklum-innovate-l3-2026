# Session 02 content development: Reliable tools and MCP integration

> Markdown copy of [`02 Reliable tools and MCP integration - content development.docx`](02%20Reliable%20tools%20and%20MCP%20integration%20-%20content%20development.docx) for reading on GitHub. The Word document in this repository is the single source of truth; edit it, then regenerate this page with `guide-builder/content_md.py`.

## 1. Topic Overview

### 1.1 Topic Title - Tools and integration: Reliable tools and MCP integration (Session 02)

**Owner: [SME]**

### 1.2 Short Topic Description

**Owner: [SME]**

Write 2–4 sentences explaining what the topic is about, why it matters and what learners will explore.

**Your input:**

This session turns an agent's tool calls into a boundary the model cannot talk its way through: validated tool contracts, application-owned permissions, structured errors that say whether a retry can help, exact-action approval for a write, and an idempotent effect ledger. Learners then put the read tools behind the Model Context Protocol (MCP) with a real stdio client and server, and see that the protocol changes how tools are reached, not who may use them. From this session the platform is also visible: the course kit gives a small run API and console, where learners submit runs, read their event timelines and try allowed and denied tool calls. It is a guided build: learners run each prompt in their own project after the instructor shows it.

### 1.3 Level

**Owner: [SME + L&D]**

Select Beginner / Intermediate / Advanced and add context if useful.

**Your input:**

**Context:** L3 is the advanced, selective level of the programme for experienced software engineers. Session 02 builds directly on the Session 01 runtime and is hands-on engineering.

Advanced

### 1.4 Prerequisites

**Owner: [SME]**

List previous topics, knowledge, tools, access or skills required. If none, write “No prerequisites.”

**Your input:**

• Session 01 completed: your project in the course GitLab group with the Lesson 01 check pack passing (7 tests) and LESSON = 1.

• The Session 01 prerequisites: independent Python, async code and tests, LLM foundations, and reviewing code produced by a coding agent.

• Basic JSON Schema and HTTP API concepts; awareness of database transactions helps for the effect ledger.

• Your coding agent, signed in to gitlab.ciklum.net, and a local browser for the platform console. No paid model account is needed: the course runs on an offline, deterministic mock provider.

• A machine that can run Python 3.12 and start a local subprocess (the MCP server), or Docker.

### 1.5 Session Details

**Owner: [L&D]**

L&D provides date, calendar details and delivery logistics. SME provides estimated time needed and timing constraints.

**Date:** To be confirmed by L&D (the week after Session 01, which is Oct 28, 2026)

**Session link: zoom**

**Calendar invitation text:**

Draft for L&D (please add the date and link): "L3 Building Agentic Platforms, Session 02: Reliable tools and MCP integration (120 min: 30 min discussion + 90 min guided build). Bring your Session 01 checkpoint: your project in the course GitLab group with its 7 checks passing. You build the tool boundary and the MCP integration in your own project and open your platform's first console. Session page: https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-02/"

**Duration (SME):** 120 minutes: 30 min discussion + 90 min guided build. Timing constraint: learners need their Session 01 project working before minute 30, a local browser for the console, and a machine that can start a local Python subprocess for the MCP server.

### 1.6 Speaker(s)

**Owner: [SME + L&D]**

List the main speaker, co-speakers and guest experts and clarify their roles.

**Your input:**   
Maksym Pavlov

**Role:** Maksym Pavlov is the main speaker and SME: the concept discussion and the guided build, showing each prompt and reviewing the change before learners run it in their own project. Learners' code is checked by the Session 02 check pack and the review prompt. Mentors, if available, help learners whose environment or MCP subprocess fails. Co-speakers or mentors: none named yet.

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

Explain why a tool call is untrusted input, and order the checks a tool boundary applies before dispatch: known tool, the run's permission, the argument schema.

**Objective 2:**

Build, by directing a coding agent, a tool executor whose structured errors distinguish terminal from retryable failures.

**Objective 3:**

Implement exact-action approval and an idempotent effect ledger, and explain why the local guarantee does not extend to external APIs.

**Objective 4:**

Configure an MCP server and stdio client, describe the host, client, server, tool and resource roles, and demonstrate that discovery does not grant permission.

**Objective 5:**

Use the platform console to submit a run, read its event timeline, and verify the tool boundary's decisions for an analyst and an operator.

## 3. Pre-work

**Owner: [SME]**

Define anything participants need to complete before the live session: reading, video, previous course/module, tool setup, account/access, short task, reflection question or preparation of data/files.

If nothing is required, write: “No pre-work required.”

**Pre-work:**

Complete your Session 01 checkpoint (the Session 01 after-class work): your project in the course GitLab group with the Lesson 01 check pack passing (7 tests) and LESSON = 1. Optional (20 min): the MCP architecture overview, https://modelcontextprotocol.io/docs/learn/architecture.

## 4. Live Session Design

### 4.1 Session Agenda

**Owner: [SME]**

Provide the proposed flow and approximate timing.

| Section | Topic | Approx. time | Format |
|---|---|---|---|
| 1 | Reconnect to INC-001 and your Session 01 checkpoint; open your platform's first console | 0–10 min | Discussion + live demo |
| 2 | Concept: the tool boundary, terminal vs retryable errors, exact approval, MCP roles | 10–30 min | Presentation + discussion |
| 3 | Build steps 1 and 2: the executor, approval and the effect ledger | 30–50 min | Guided build |
| 4 | Build steps 3 and 4: the MCP server and the read adapter | 50–75 min | Guided build |
| 5 | Break the boundary on purpose, in a script and in the console's Tools view | 75–100 min | Hands-on practice |
| 6 | Verify and push (12 checks), and interpret the evidence | 100–115 min | Verification |
| 7 | Questions and handoff to Session 03 | 115–120 min | Discussion |

### 4.2 Topic-by-Topic Content

**Owner: [SME]**

For each section, provide:

Key concepts — what does the participant need to know?

Common misconceptions — what do learners frequently misunderstand?

Key message — the one thing participants should remember from this section.

**Section 1:**

The tool boundary

**Key concepts:** every model proposal is untrusted input. One executor checks, in order, that the tool exists, that the run's Context allows it, and that the arguments match the platform's JSON Schema (which forbids extra properties, so a tenant cannot be chosen through an argument). Reads get a 2-second timeout, one retry and an output-size limit. Every error is structured and says whether a retry can help: unknown_tool, permission_denied, invalid_arguments and output_too_large are terminal; tool_unavailable is retryable.

**Common misconceptions:** a correct schema makes a tool safe; retrying any error is harmless; a model that sees a denial can argue its way past it.

**Key message:** authority comes from Context, shape from the schema, consequences from approval: separate checks, in this order, before anything runs.

**Section 2:**

Exact approval and idempotent effects

**Key concepts:** the first write tool, mock_remediate, records a simulated rollback. An approval covers one action key: sha256 of tenant, run id, tool name and canonical arguments. Without the key in the run's approved actions the executor raises ApprovalRequired and nothing happens. The effect and its deduplication record are written in one SQLite transaction, so a repeat after a restart returns the stored result with replayed true.

**Common misconceptions:** approving a rollback approves any rollback; an in-memory list of done actions is enough; local idempotency makes an external API exactly-once.

**Key message:** an approval covers one exact action, and a repeated approved write happens once, locally; external APIs need receiver-side idempotency or reconciliation.

**Section 3:**

MCP, and the platform console

**Key concepts:** the Model Context Protocol (an open standard introduced by Anthropic in November 2024) connects AI applications to tools and data. A host application starts servers; its client discovers and calls them over a transport (stdio here, Streamable HTTP for remote servers) with JSON-RPC messages such as tools/list and tools/call. Tools are operations the model may ask for; resources are addressable content. The launcher fixes the tenant, and stdout carries only protocol messages. From this session the kit gives a platform shell: a run API and a console with Overview, Runs and a Tools view that shows each executor decision.

**Common misconceptions:** MCP decides who may use a tool; a newly advertised tool is usable; the stdio demo tests remote authentication; the console is decoration rather than a client of the same API.

**Key message:** MCP standardizes how tools are found and reached; the platform decides who may use them, and the console makes those decisions visible.

### 4.3 Interactive Activities

**Owner: [SME content + L&D learning design]**

Identify where participants should actively engage.
- Poll**✔ (concept block) Can a correct JSON Schema make a tool safe by itself?**
- Discussion**✔ (opening) What could a model put in a tool call? (75–100 min) Predict each failure before it runs.**
- Case study**✔ (MCP block) The server is not your policy: an extra tenant argument**
- Breakout activity
- Quiz
- Hands-on exercise**✔ (30–100 min) Learners run the build prompts and break the boundary in their own project and console**
- Live demo**✔ (30–75 min) The instructor shows each prompt and its change before learners run it**
- Problem-solving activity**✔ (step 2) Work out what an approval covers when INC-001 becomes INC-002**
- Reflection**✔ (close) Mark the tool boundary and the console on your platform blueprint**

**Activity details (SME content and L&D will turn into activity in zoom or whiteboard):**

For each activity include: Purpose • Instructions • Time • Expected outcome • Debrief / discussion points.

**1. Discussion: the most consequential line.** Purpose: see a tool call as untrusted input. Instructions: show `result = await execute(...)` from the Session 01 loop and ask what a model could put in a call. Time: 5 min. Expected outcome: a list including an unknown tool, an ungranted tool, malformed or extra arguments (a tenant), a huge result, a hang, an unapproved write and a duplicate write. Debrief: each gets one named check today.

**2. Poll: can a correct JSON Schema make a tool safe by itself?** Options: yes / no / only for read tools. Correct: no. Time: 2 min. Debrief: a well-formed request can still be unauthorized or harmful; shape, authority and consequences are separate checks.

**3. Guided build: the four build steps.** Purpose: learners build the boundary in their own project. Instructions: for each step the instructor explains it and runs the prompt; learners run the same prompt, then compare the agent's change and the checks with the code excerpt on the session page. Time: 45 min. Expected outcome: the Lesson 02 check pack passing (12 tests). Debrief: ask learners which check stops an injected request for mock_remediate.

**4. Case study: the server is not your policy.** Purpose: separate discovery from permission. Instructions: show the discovery output, call the server directly with an extra tenant argument (accepted), then call through the executor (invalid_arguments). Time: 5 min. Expected outcome: learners explain why the platform validates against its own contract. Debrief: what if the server advertised a new write tool?

**5. Hands-on: break the boundary on purpose.** Purpose: make every check observable. Instructions: predict, then run: a tenant argument, a write from a read-only run, a tiny output limit, and an approved write repeated after reopening the executor; then repeat the denied and approval cases in the console's Tools view as demo-astro and demo-operator. Time: 25 min. Expected outcome: invalid_arguments, permission_denied, output_too_large, replayed true, and approval_required with an exact-action key. Debrief: which outcomes are retryable, and who decides an approval?

**6. Reflection: the platform blueprint.** Purpose: connect today's work to the platform. Instructions: mark the tool boundary and the console on your blueprint, and note which later session adds which console view. Time: 3 min. Expected outcome: an updated sketch kept for the next sessions.

### 4.4 Practical Application After the Session

**Owner: [SME]**

Describe what participants will actually do.

**Task:**

Finish the Session 02 build in your own project, then explore it through the console.

**Instructions:**

• Finish any prompt you did not complete in class, in order: Prepare, Move to the course layout and start the platform, Add the check pack, Build steps 1–4, the exercise, Verify and push, and Review.

• Read each change before running the next prompt. The check pack must pass unchanged; never edit it to get a pass.

• Open your platform's console, sign in as demo-astro and then demo-operator, submit INC-001, and repeat the denied and approval cases in the Tools view.

• Practice: make a read handler fail once with a connection error and then succeed, then fail every time; confirm the single retry, the retryable error, and that permission_denied is never retried.

• Practice: sketch what a remote HTTP MCP server would add (client authentication, token validation, tenant mapping, per-tool authorization) and mark what the tool gateway (Session 09) and delegated credentials (Session 10) will provide.

• Read 'Writing effective tools for agents' (Anthropic) and the MCP architecture overview (about 1 hour).

**Expected result:**

Your project in the course GitLab group with the Lesson 02 check pack passing unchanged (12 tests) and LESSON = 2, a short note from the retry experiment and the remote-MCP sketch. Estimated time: 2–3 hours.

**Feedback / debrief points:**

• Did the coding agent's claims match the check output? Unrun or skipped checks are not passes.

• Which of your failure cases were terminal and which retryable, and did anything retry a terminal error?

• In the console, what could the analyst see and do that the operator could not, and the other way round?

## 5. Presentation

### 5.1 Presentation Content

**Owner: [SME]**

Provide the presentation content or draft. Recommended logic: Context → Concept → Example → Application → Practice → Summary.

**Presentation / slide deck:**

The Session 02 page is the presentation, with Read and Present views (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-02/). The full instructor script is in instructor guide 02. Outline (Context → Concept → Example → Application → Practice → Summary):

• 1. Where we are: the Session 01 loop's most consequential line, where today's work sits, and the agenda.

• 2. From today your platform has a console: the given run API and console, with screenshots of the Tools and Runs views.

• 3. What can go wrong at the tool line: eight model behaviours and the check that stops each.

• 4. The tool boundary: three checks before anything runs, then the read and write paths.

• 5. Effects: exact-action approval and the effect ledger, and where the guarantee ends.

• 6. MCP in brief: what the protocol standardizes and what it does not.

• 7. Host, client and server; what discovery actually returns; the server is not your policy.

• 8. How the platform hands tools to an agent: server list, discovery, catalogue, per-run tools.

• 9. Example: one call of the INC-001 investigation through MCP.

• 10. Application: the prepare and check-pack prompts and the four build prompts.

• 11. Practice: break the boundary on purpose, in a script and in the console; verification evidence (12 passed).

• 12. Summary, recovery prompts and the after-class assignment.

## 6. Session Wrap-up

### 6.1 Conclusions / Key Takeaways

**Owner: [SME]**

Define 3–5 essential messages participants should leave the session with. These will also be used in e-learning.

**Key takeaway 1:**

Check, then dispatch: known tool, allowed for this run, valid arguments, before any handler runs.

**Key takeaway 2:**

Every error carries a decision: terminal or retryable, so nobody retries a permission.

**Key takeaway 3:**

An approval covers one exact action, and a repeated approved write happens once locally; external APIs need their own idempotency.

**Key takeaway 4:**

Discovery is not permission: MCP finds and reaches tools; the platform decides who may use them.

**Key takeaway 5:**

Your platform is visible: the console shows each run and every tool decision, and each later session adds to it.

### 6.2 Lesson Reflection

**Owner: [SME]**

Provide 2–4 questions that help participants connect the topic to their own work.

Suggested framing: “Before moving on, consider:”

**Reflection question 1:**

Which tool would you let an agent call in your system today, and which check would stop its most dangerous variant?

**Reflection question 2:**

Where in your systems does something retry an error that can never succeed, such as a permission failure?

**Reflection question 3:**

If a vendor shipped an MCP server for a system you own, what would you verify before an agent may call it?

### 6.3 What's Next

**Owner: [SME + L&D]**

Identify the logical next step: next session, next topic, practice assignment, certification or deeper learning.

**What's next:**

Session 03, Context, retrieval and memory (90 min): which evidence enters the model's context, ranked retrieval, versioned artifacts and expiring memory, kept separate from authority. It starts from your Session 02 checkpoint in your GitLab repository.

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

• Video 1 (5 min): the tool line as untrusted input; the three checks before dispatch and terminal vs retryable errors.

• Video 2 (5 min): exact-action approval and the effect ledger, with a restart and a replay.

• Video 3 (6 min): MCP in brief: host, client, server, tools and resources, discovery, and why the server is not your policy.

• Video 4 (5 min): a tour of the platform console: submit a run, read its timeline, and try calls in the Tools view as an analyst and an operator.

• Knowledge check (7.4) and the self-paced assignment (7.5).

Source material: the Session 02 page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-02/), instructor guide 02 (SAY sections) and the lesson-02 lab output.

### 7.3 Examples / Use Cases

**Owner: [SME]**

Provide examples that can stand on their own in e-learning. Include enough context for someone who was not at the live session.

**Your input:**

**Example 1: denied before dispatch.** An analyst's run proposes mock_remediate for INC-001. The executor returns permission_denied with retryable false: the tool exists, but this run was not granted it, so its arguments are never examined and nothing runs. In the console's Tools view the same call shows as a red 'deny'.

**Example 2: one exact approval, one effect.** An operator's run proposes rollback of INC-001. The executor raises ApprovalRequired with the action key. After the operator approves that key the effect is recorded (replayed false); after a restart the same approved call returns the stored result (replayed true), and the effects table still holds one row. Proposing INC-002 needs a new approval.

**Example 3: the server is not your policy.** Called directly, the MCP server accepts log_lookup with an extra tenant argument and quietly returns Astro's record, because its advertised schema does not forbid extra properties. Through the platform's executor the same request fails with invalid_arguments: the platform's own contract decides.

### 7.4 Knowledge Check

**Owner: [SME]**

Provide 3–5 questions testing the most important concepts. Include question, options if applicable, correct answer and explanation. L&D adapts them into the final interaction.

**Your input:**

**Q1. An analyst's run asks for mock_remediate with valid arguments. What happens?** A) the rollback is recorded  B) invalid_arguments  C) permission_denied, before the arguments are examined  D) approval is requested. Correct: C. The tool exists but is not in the run's allowed tools; permission is checked before the schema.

**Q2. Which of these errors should a caller retry?** A) permission_denied  B) invalid_arguments  C) tool_unavailable  D) unknown_tool. Correct: C. It is the only one marked retryable; asking again cannot change the others.

**Q3. An operator approved the rollback of INC-001. The agent now proposes the rollback of INC-002.** A) it runs under the same approval  B) it needs a new approval  C) it is denied permanently  D) it returns replayed. Correct: B. The action key binds tenant, run, tool and the exact arguments.

**Q4. The MCP server starts advertising a new write tool. What can an agent do with it?** A) call it at once  B) nothing: it is unknown_tool until the platform adds it to its catalogue and a run's allowed tools  C) call it after approval  D) call it if it is read-only. Correct: B. Discovery is information, not permission.

**Q5. Your local effect ledger makes duplicate writes safe. What else does a real payment API need?** A) nothing  B) a receiver-side idempotency key or a reconciliation step  C) a longer timeout  D) more retries. Correct: B. A local record cannot make a remote operation exactly-once.

### 7.5 Practice / Assignment

**Owner: [SME]**

Create a task that can be completed without attending the live session. Include task, context, expected output, estimated time, success criteria and resources.

**Your input:**

**Task:** Using your own coding agent and the learner kit in the course repository, build the Session 02 checkpoint: the tool boundary, exact approval with an idempotent mock effect, real MCP transport, and the platform console.

**Context:** Start from your Session 01 checkpoint. Run the prompts on the Session 02 page in order (Prepare, Move to the course layout and start the platform, Add the check pack, Build steps 1–4, the exercise, Verify and push, Review); the same prompts are in LEARNER_PROMPTS.md (Lesson 02). No paid model account is needed.

**Expected output:** your repository in the course GitLab group with the Lesson 02 check pack passing unchanged (12 tests), the lab output (tools log_lookup and runbook_search, protocol 2026-07-28, the cited INC-001 answer, and a denied write), and a short note of the decisions you saw in the console's Tools view as an analyst and as an operator.

**Estimated time:** 3 hours.

**Success criteria:** malformed and denied requests fail before dispatch; changing an approved action's arguments needs a new approval; a duplicate approved write produces one stored effect; the real stdio client discovers both read tools and the investigation still cites the observed log and runbook; the console shows the run's timeline and each Tools check's decision.

**Resources:** the Session 02 page, learner-kit/lessons/02 in the course repository, LEARNER_PROMPTS.md (Lesson 02).

### 7.6 Lesson Reflection

**Owner: [SME]**

Provide reflection questions for independent learners. These may be the same as or adapted from the live session.

**Your input:**

Use the three live-session questions (6.2), plus: 'Which decision in your systems is made by the same component that then carries it out? What would change if a separate boundary made it?'

### 7.7 Deep Dive / Additional Resources

**Owner: [SME]**

Provide articles, videos, books, documentation, research, internal resources, tools, tutorials or examples. Distinguish Recommended / Essential from Optional / Deep Dive.

**Your input:**

**Essential:** Writing effective tools for agents (Anthropic): https://www.anthropic.com/engineering/writing-tools-for-agents

**Essential:** MCP architecture overview: https://modelcontextprotocol.io/docs/learn/architecture

**Optional / deep dive:** the MCP specification (https://modelcontextprotocol.io/specification) and the JSON Schema reference (https://json-schema.org/understanding-json-schema).

**Optional / deep dive:** one finished implementation, the course reference at tag lesson-02 (agent_runtime/tools.py, agent_runtime/mcp_bridge.py, agentic_platform/api.py) and TESTING.md; read it after building your own.

### 7.8 What's Next

**Owner: [L&D + SME]**

Define the next topic, recommended learning path, practice or next action.

**Your input:**

Next: Session 03, Context, retrieval and memory. Recommended path: complete the 7.5 assignment first; Session 03 starts from that checkpoint.

## 8. Materials & Assets

**Owner: [SME]**

Indicate which assets are needed and provide them where applicable.
- Presentation**✔ the Session 02 page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-02/), with Read and Present views**
- Speaker notes**✔ SAY sections of instructor guide 02**
- Script**✔ instructor guide 02 (complete)**
- Examples**✔ three worked examples in 7.3**
- Case study**✔ 'The server is not your policy' on the Session 02 page (MCP section)**
- Demo**✔ the learner kit (learner-kit/lessons/02 in the course repository); the reference tags lesson-01 → lesson-02 are the instructor's answer key**
- Screenshots**✔ the console's Tools and Runs views on the Session 02 page**
- Diagrams**✔ where today sits, the tool boundary, MCP host/client/server and how the platform hands tools to an agent, on the Session 02 page**
- Templates
- Sample files**✔ the given platform shell (run API and console) in learner-kit/lessons/02/given; synthetic incidents and runbooks from Session 01**
- Quiz questions**✔ five questions in 7.4**
- Practice assignment**✔ 7.5 and LEARNER_PROMPTS.md, Lesson 02**
- Additional resources**✔ 7.7**
- Other:

## 9. Content Accuracy & SME Notes

### 9.1 Important Terminology

**Owner: [SME]**

List terminology that must be used consistently.

**Your input:**

• Tool boundary (ToolExecutor): the one place every tool call passes through, whichever way the tool is reached.

• Context.allowed: the tools a run may use, set by the platform; the model cannot widen it by naming a tool.

• Terminal vs retryable error: unknown_tool, permission_denied, invalid_arguments and output_too_large are terminal; tool_unavailable is retryable after the executor's own single retry.

• Action key: sha256 of tenant, run id, tool name and canonical arguments; what an approval refers to.

• ApprovalRequired: the executor's signal that a write was proposed but not performed.

• Effect ledger and replayed: the effect and its deduplication record are committed in one transaction; a repeat returns the stored result with replayed true.

• MCP host, client and server: the application that starts servers, its connection to one server, and the program that offers capabilities.

• Tool vs resource: an operation the model may ask to run vs addressable content the application reads (incident://runbooks).

• Transport: stdio in this course (the host starts the server as a child process); Streamable HTTP for remote servers.

• Discovery: what a server says it offers (tools/list); information, never permission.

• Platform shell and console: the given run API and web UI at /console (Overview, Runs, Tools); learners extend it from Session 08.

### 9.2 Common Misconceptions

**Owner: [SME]**

List frequent misunderstandings. This will inform explanations, examples, knowledge checks and FAQs.

**Your input:**

• 'A correct JSON Schema makes a tool safe.' The schema checks shape; permission, approval and the effect ledger are separate checks.

• 'Retrying is always harmless.' A permission or argument error will not change on retry; only errors marked retryable should be retried, and a write needs an idempotency design.

• 'Approving a rollback approves rollbacks.' An approval covers one exact action: tenant, run, tool and canonical arguments.

• 'MCP decides who may use a tool.' MCP standardizes discovery and calls; a newly advertised tool is unknown_tool until the platform adds it on purpose.

• 'Local idempotency makes an external API exactly-once.' It does not; the receiver has to support it.

• 'The console is decoration.' It is a client of the same API, scoped to the signed-in tenant and role, and it shows the executor's real decisions.

### 9.3 Important Nuances

**Owner: [SME]**

Document exceptions, limitations, risks, assumptions or cases where the recommended approach does not apply.

**Your input:**

• With stdio, identity is the process boundary: the trusted launcher fixes the tenant and the command, and model output can never choose either. A remote HTTP MCP server needs real authentication, token validation and authorization; remote MCP OAuth is not exercised in this course.

• Launching one MCP server per client is deliberately simple. Session 09 replaces it with a central tool gateway: shared upstream sessions, one policy, an audit ledger and pinned tool definitions.

• The effect ledger makes a repeated approved write safe only locally. For an external API the receiver must support an idempotency key, or a reconciliation step must check what actually happened.

• The given platform shell keeps runs in memory, so they are lost when the process restarts; Session 05 makes runs durable and Session 08 replaces the shell with the platform core. A Tools check in the console never approves a write.

• The reference pins mcp 2.2.0, and the stdio connection negotiates protocol 2026-07-28. Tutorial code for the 1.x SDK uses different result field names (isError instead of is_error).

• Demo identities (demo-astro, demo-operator, demo-locomotive) are for loopback use only. All incident data are synthetic; no real system is touched.

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
