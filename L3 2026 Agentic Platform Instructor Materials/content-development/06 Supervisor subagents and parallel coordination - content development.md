# Session 06 content development: Supervisor subagents and parallel coordination

> Markdown copy of [`06 Supervisor subagents and parallel coordination - content development.docx`](06%20Supervisor%20subagents%20and%20parallel%20coordination%20-%20content%20development.docx) for reading on GitHub. The Word document in this repository is the single source of truth; edit it, then regenerate this page with `guide-builder/content_md.py`.

## 1. Topic Overview

### 1.1 Topic Title - Multi-agent: Supervisor, subagents and parallel coordination (Session 06)

**Owner: [SME]**

### 1.2 Short Topic Description

**Owner: [SME]**

Write 2–4 sentences explaining what the topic is about, why it matters and what learners will explore.

**Your input:**

This session turns the single agent into a small team the application keeps in bounds. A supervisor's model proposes pieces of work as delegation contracts (a task ID, a role and a bounded objective); the application validates each one, starts a child run with only its role's tool, a new run ID, the parent's ID and no approvals, and charges it to one shared budget reserved before the child starts. Independent children then run in parallel under a concurrency limit and a deadline that keeps finished work and cancels the rest, replies are accepted only when they match their request and the next artifact version, and a producer-reviewer loop escalates when it does not converge. Learners also measure whether the team is worth it against the Session 04 single-agent baseline.

### 1.3 Level

**Owner: [SME + L&D]**

Select Beginner / Intermediate / Advanced and add context if useful.

**Your input:**

**Context:** L3 is the advanced, selective level of the programme for experienced software engineers. Session 06 builds on the durable single-agent runtime of Sessions 01 to 05: every child is an ordinary run, and the same tool boundary, evaluation harness and run records apply to each one.

Advanced

### 1.4 Prerequisites

**Owner: [SME]**

List previous topics, knowledge, tools, access or skills required. If none, write “No prerequisites.”

**Your input:**

• Session 05 completed: your project in the course GitLab group with the Lesson 05 check pack passing (21 tests), LESSON = 5, and a Lesson 05 entry in AGENTS.md.

• The Session 04 single-agent baseline for INC-001 (75 fixture tokens, 3 steps), to compare the team against.

• The earlier prerequisites: independent Python, async code and tests, LLM foundations, and reviewing code a coding agent writes.

• Python asyncio basics: tasks, timeouts, cancellation and locks.

• Your coding agent signed in to gitlab.ciklum.net, and a local browser for the platform console.

### 1.5 Session Details

**Owner: [L&D]**

L&D provides date, calendar details and delivery logistics. SME provides estimated time needed and timing constraints.

**Date:** **Dec 2, 2026**

**Session link: zoom**

**Calendar invitation text:**

Draft for L&D: "L3 Building Agentic Platforms, Session 06: Supervisor, subagents and parallel coordination, Dec 2, 2026 (120 min). Bring your Session 05 checkpoint. A supervisor delegates bounded work to scoped log and runbook agents under typed contracts and one shared budget, runs independent work in parallel under a deadline, and accepts only the replies it asked for. Session page: https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-06/"

**Duration (SME):** 120 minutes: 30 min discussion (recall, concept and whether a team is worth it) + 90 min guided build, practice and verification. Timing constraint: learners need their Session 05 project passing before the session; the session runs fully offline on the mock model and a given planning fixture.

### 1.6 Speaker(s)

**Owner: [SME + L&D]**

List the main speaker, co-speakers and guest experts and clarify their roles.

**Your input:**   
Maksym Pavlov

**Role:** Maksym Pavlov is the main speaker and SME: the recall discussion, the concept discussion and the guided build, showing each prompt and reviewing the change before learners run it in their own project. Learners' code is checked by the Session 06 check pack (29 tests) and the review prompt. The session page has an instructor view (the page opened with ?instructor) that carries the guide's script and timings.

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

Explain how a supervisor, a delegation contract, a child run and a shared budget relate, and why a child is a separate run rather than a reworded prompt in a shared transcript.

**Objective 2:**

Implement, by directing a coding agent, contract validation and scoped child runs: only the role's tool, a new run ID, the parent's ID, no approvals, identical contracts reused and changed ones refused.

**Objective 3:**

Enforce one shared budget for all children by reserving before launch and settling from reported usage, and report an incomplete investigation honestly when the budget refuses a child.

**Objective 4:**

Schedule independent work with a concurrency limit and a deadline that keeps finished results and cancels the rest, and run the supervisor's children in parallel through the same checks.

**Objective 5:**

Validate replies against their request and the next artifact version, bound a producer-reviewer loop, and judge with fixture evidence whether a team is worth its extra calls.

## 3. Pre-work

**Owner: [SME]**

Define anything participants need to complete before the live session: reading, video, previous course/module, tool setup, account/access, short task, reflection question or preparation of data/files.

If nothing is required, write: “No pre-work required.”

**Pre-work:**

Complete your Session 05 checkpoint (the Session 05 after-class work): your project in the course GitLab group with the Lesson 05 check pack passing (21 tests) and LESSON = 5. Optional (20 min): Anthropic's 'Multi-agent research system'. Think of one task your team would split between agents: which parts need different tools or permissions?

## 4. Live Session Design

### 4.1 Session Agenda

**Owner: [SME]**

Provide the proposed flow and approximate timing.

| Section | Topic | Approx. time | Format |
|---|---|---|---|
| 1 | Reconnect: recall runs, workers and the Session 04 baseline | 0–10 min | Discussion |
| 2 | Concept: supervisor, contract, child run, shared budget; is a team worth it | 10–30 min | Presentation + discussion |
| 3 | Build steps 1 and 2: contracts and scoped children, the shared budget | 30–50 min | Guided build |
| 4 | Build steps 3 and 4: parallel scheduling with a deadline, replies and review | 50–75 min | Guided build |
| 5 | Exercise: budget, escalation, conflicts, deadline, failed predecessor, stale reply | 75–100 min | Hands-on practice |
| 6 | Verify and push (29 checks), and compare the team with the single agent | 100–115 min | Verification |
| 7 | Questions and handoff to Session 07 | 115–120 min | Discussion |

### 4.2 Topic-by-Topic Content

**Owner: [SME]**

For each section, provide:

Key concepts — what does the participant need to know?

Common misconceptions — what do learners frequently misunderstand?

Key message — the one thing participants should remember from this section.

**Section 1:**

Contracts and scoped children

**Key concepts:** the supervisor's model has one tool, delegate, and may propose only a task ID, a role (logs or runbooks) and an objective of at most 500 characters. The application validates the contract, maps the role to a fixed tool, refuses a child that would hold a tool its parent lacks, reuses the result of an identical contract and refuses a changed objective under the same task ID. Each child is an ordinary run: a new run ID, the parent's run ID as parent_id, only its role's tool, no approvals and its own messages.

**Common misconceptions:** a subagent is a differently worded prompt in the same transcript; the model can grant a child the tools it needs; a child inherits the parent's approvals.

**Key message:** the model proposes the work; the application decides each child's authority.

**Section 2:**

One shared budget

**Key concepts:** all children draw on one allowance of tokens, agents and delegation depth. A child reserves its share (1,800 fixture tokens) under a lock before it starts, and the budget is settled from what it reported using; a child that produced no run is charged the full reservation. A plan that needs more agents than allowed is refused at the start, and the supervisor answers insufficient_evidence while keeping the evidence it has.

**Common misconceptions:** checking usage after the children finish is enough; each concurrent child can see the whole allowance; the supervisor's own calls are in the pool (they are not until Session 11).

**Key message:** reserve before launch, settle after; a refused child makes the answer honest, not silent.

**Section 3:**

Parallel work under a deadline

**Key concepts:** the scheduler validates the work graph first (duplicate IDs, unknown dependencies, cycles), launches ready items up to the concurrency limit, blocks dependants of failed work, and at the deadline keeps finished results, cancels and awaits the rest and reports partial. The runtime gains one optional hook, execute_batch, through which the supervisor's pending delegate calls run in parallel, each still through delegate's checks, with results matched back by tool-call ID.

**Common misconceptions:** parallel means the tool executor runs everything concurrently; at the deadline everything is lost; a partial result can be reported as complete.

**Key message:** keep what finished, cancel what did not, and say which is which.

**Section 4:**

Replies, versions and bounded review

**Key concepts:** every request travels in an envelope with a correlation ID, a task ID, an artifact ID and a version; a reply is accepted only if the three IDs match and its version is exactly the next one, so a late or misdirected reply cannot overwrite newer evidence. A producer-reviewer loop has a round limit: without acceptance it escalates with the artifact and every review kept, and one component owns and saves the reviewed artifact.

**Common misconceptions:** the latest reply to arrive is the right one; a better prompt fixes coordination errors; review should run until the reviewer agrees.

**Key message:** match every reply to its request, and turn disagreement into an escalation with evidence.

### 4.3 Interactive Activities

**Owner: [SME content + L&D learning design]**

Identify where participants should actively engage.
- Poll**✔ (contract block) Should a worker choose its own permissions after reading its objective?**
- Discussion**✔ (opening, 0–10 min) Recall: what makes a run a run, and what would a two-agent team have to show to beat the single-agent baseline?**
- Case study**✔ (design choice) The same INC-001 answer from one agent (75 fixture tokens) and from a team (170): when is the team worth it?**
- Breakout activity
- Quiz
- Hands-on exercise**✔ (30–100 min) Learners run the build prompts and break the coordination on purpose in their own project**
- Live demo**✔ (30–75 min) The instructor shows each prompt, its change and the parallel demonstration**
- Problem-solving activity**✔ (replies block) Tell a genuine evidence conflict from a reviewer whose criteria keep changing**
- Reflection**✔ (close) Mark the supervisor and its children on your platform blueprint**

**Activity details (SME content and L&D will turn into activity in zoom or whiteboard):**

For each activity include: Purpose • Instructions • Time • Expected outcome • Debrief / discussion points.

**1. Discussion: recall runs.** Purpose: connect Sessions 04 and 05 to today. Instructions: three questions: which parts of a run a child has of its own and which it takes from its parent; what a team would have to show against the 75-token baseline; whether a child should be able to propose a write. Time: 10 min. Expected outcome: own run ID and messages, parent's tenant and ID, no approvals; a measured improvement on the same cases. Debrief: every child is a run.

**2. Poll: who chooses a child's tools?** Options: the child, after reading its objective / the supervisor's model / the application, from the role. Correct: the application. Time: 2 min. Debrief: the role maps to a fixed tool, and the parent's tools are the ceiling.

**3. Guided build: the four build steps.** Purpose: learners build the team in their own project. Instructions: for each step the instructor explains it and runs the prompt; learners run the same prompt and compare the agent's change and the checks with the excerpt on the session page, then answer the page's 'Read your code' questions. Time: 45 min. Expected outcome: delegate, the shared budget, the scheduler with the batch hook, and reply and review checks, with the Lesson 06 checks passing. Debrief: where in your code is a child's authority decided?

**4. Case study: is a team worth it?** Purpose: judge multi-agent designs by evidence. Instructions: compare the single agent (3 model calls, 75 fixture tokens) with the team (6 calls, 170 tokens) on the same INC-001 answer, and the sequential and parallel timings. Time: 5 min. Expected outcome: the team costs more and buys time only; worth it when work truly splits or isolation matters. Debrief: the Session 04 harness is how you would show it.

**5. Hands-on: break the coordination on purpose.** Purpose: prove each check. Instructions: predict, then run in a throwaway script: max_agents 1; a logs child for a runbook-only parent; a reused task ID with a changed objective; a slow worker past the deadline; a failed predecessor; a stale reply. Time: 25 min. Expected outcome: insufficient_evidence, child_privilege_escalation, task_id_conflict, partial with the slow item cancelled, blocked, ValueError. Debrief: which of these could a prompt have prevented?

**6. Problem-solving: a review that never converges.** Purpose: treat review as bounded coordination. Instructions: decide how to tell a genuine evidence conflict from a reviewer whose criteria keep changing, and what each should lead to. Time: 3 min. Expected outcome: explicit acceptance rules for both; escalate the conflict with evidence, fix the reviewer's criteria.

**7. Reflection: the team on the blueprint.** Purpose: connect today to the platform. Instructions: mark the supervisor and children; Session 07 moves the runbook child to an independent service over A2A, and Session 08 lists children in the console with a link to their parent. Time: 3 min. Expected outcome: an updated sketch.

### 4.4 Practical Application After the Session

**Owner: [SME]**

Describe what participants will actually do.

**Task:**

Finish the Session 06 build in your own project and compare the team with your single agent.

**Instructions:**

• Finish any prompt you did not complete in class, in order: Prepare, Add the check pack, Build steps 1–4, the exercise, Verify and push, and Review.

• Read each change before running the next prompt, using the page's 'Read your code' questions. The check pack must pass unchanged; never edit it to get a pass.

• Practice: design a third worker on paper, with objective, inputs, tools and acceptance criteria, and decide which tasks may run in parallel with it.

• Practice: compare two concurrency limits on the same fixtures, and add a contradictory-evidence review case with an explicit acceptance rule.

• In the console: run INC-001 (still the single agent, 75 tokens), ask your agent to submit the team agent (400 unknown_agent until Session 08), and find the children in the Session 06 demonstration's output.

• Read 'Multi-agent research system' and 'Building effective agents' (Anthropic), about 1 hour.

**Expected result:**

Your project in the course GitLab group with the Lesson 06 check pack passing unchanged (29 tests), LESSON = 6, a Lesson 06 entry in AGENTS.md, and the demonstration's result: two children, 110 shared tokens spent, the parallel run faster, a partial deadline result and an escalated review. Estimated time: 3 hours.

**Feedback / debrief points:**

• Did the coding agent's claims match the check output? Unrun or skipped checks are not passes.

• Where in your code is a child's authority decided, and could the supervisor's model change it?

• For your own team's work, would two agents beat one on the same cases, and how would you show it?

## 5. Presentation

### 5.1 Presentation Content

**Owner: [SME]**

Provide the presentation content or draft. Recommended logic: Context → Concept → Example → Application → Practice → Summary.

**Presentation / slide deck:**

The Session 06 page is the presentation, with Read and Present views (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-06/), plus an Instructor view for the presenter (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-06/?instructor) and a prompts-only page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-06-just-prompts/). No slide deck is made: the session page replaces it. Outline:

• 1. Recall: a child run is a run; the Session 04 baseline; can a child write?

• 2. Words first: supervisor, delegation contract, child run, shared budget, work item, envelope (a diagram).

• 3. The idea: the model proposes the split, the application decides; four checks before a child starts (a diagram).

• 4. Design choice: is a team worth it? The single agent against the team on INC-001.

• 5. Contracts and scoped children: the schema, contract identity and the child's Context (a diagram).

• 6. One shared budget: reserve, settle and the ledger of the INC-001 team (a diagram).

• 7. Parallel work under a deadline: the scheduler and the batch hook (a diagram).

• 8. Replies and review: envelopes, versions and a bounded review (a diagram).

• 9. Application: the prepare and check-pack prompts, then the four build prompts, each with 'Read your code'.

• 10. Practice and verification: break the coordination on purpose; 29 passed.

• 11. Summary (what changed in the project, what to try in the console), recovery prompts and the after-class assignment.

## 6. Session Wrap-up

### 6.1 Conclusions / Key Takeaways

**Owner: [SME]**

Define 3–5 essential messages participants should leave the session with. These will also be used in e-learning.

**Key takeaway 1:**

The model may propose the work; the application decides who does it, with which tool and how much it may spend.

**Key takeaway 2:**

A child is a separate run: a new run ID, the parent's ID, only its role's tool, no approvals, no delegate.

**Key takeaway 3:**

Reserve from one shared budget before a child starts, settle after; a refused child lowers the answer honestly.

**Key takeaway 4:**

Run independent work in parallel under a deadline that keeps finished results and cancels the rest.

**Key takeaway 5:**

Accept only the reply to the request you made at the next version, and escalate a review that does not converge; measure whether the team is worth it.

### 6.2 Lesson Reflection

**Owner: [SME]**

Provide 2–4 questions that help participants connect the topic to their own work.

Suggested framing: “Before moving on, consider:”

**Reflection question 1:**

Which task in your own work would you split between agents, and which tool or permission would each part need?

**Reflection question 2:**

Where would a team of agents in your systems spend more than one agent, and what would it have to buy?

**Reflection question 3:**

When agents in your systems reply late or twice, what stops an old reply from overwriting newer results?

### 6.3 What's Next

**Owner: [SME + L&D]**

Identify the logical next step: next session, next topic, practice assignment, certification or deeper learning.

**What's next:**

Session 07, A2A across independent agent services (90 min): the runbook child becomes an independent service found, authenticated to, streamed from and cancelled over A2A. Bring your Session 06 checkpoint.

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

• Video 1 (5 min): supervisor, contract, child run and shared budget, and why a child is a separate run.

• Video 2 (5 min): validating contracts and scoping children; reserving and settling the budget.

• Video 3 (4 min): parallel work under a deadline, and the batch hook.

• Video 4 (5 min): correlated replies, artifact versions and bounded review; is a team worth it?

• Knowledge check (7.4) and the self-paced assignment (7.5).

Source material: the Session 06 page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-06/) and instructor guide 06.

### 7.3 Examples / Use Cases

**Owner: [SME]**

Provide examples that can stand on their own in e-learning. Include enough context for someone who was not at the live session.

**Your input:**

**Example 1: a plan larger than the budget.** With max_agents set to 1, the supervisor proposes two children. The logs child reserves and runs; the runbooks child is refused as delegation_budget before it starts. The supervisor answers insufficient_evidence, keeping the log evidence it has, instead of guessing the missing half.

**Example 2: a child above its parent.** A parent allowed only runbook_search asks for a logs child. The role maps to log_lookup, which the parent does not hold, so delegate refuses it as child_privilege_escalation: the parent's tools are the ceiling.

**Example 3: a reply that arrives late.** A request for the report at version 1 is answered twice: once with version 2, accepted, and later again with version 2 for an earlier correlation ID. The second fails as mismatched_reply, so it cannot overwrite the accepted evidence.

### 7.4 Knowledge Check

**Owner: [SME]**

Provide 3–5 questions testing the most important concepts. Include question, options if applicable, correct answer and explanation. L&D adapts them into the final interaction.

**Your input:**

**Q1. What may the supervisor's model propose in a delegation?** A) a task ID, a role and an objective  B) the child's tools and approvals  C) the child's budget. Correct: A. The application decides the rest.

**Q2. What does a child run get from its parent?** A) the parent's conversation and approvals  B) the tenant and the parent's run ID, with only its role's tool  C) everything. Correct: B.

**Q3. Why reserve from the budget before a child starts?** A) it is faster  B) concurrent children could otherwise all see the same allowance and overspend  C) the model needs to know. Correct: B.

**Q4. At the deadline one child has finished and one has not. What does the scheduler report?** A) failed, nothing kept  B) partial, the finished result kept and the other cancelled  C) completed. Correct: B.

**Q5. A reply has the right IDs but the same version as the request. What happens?** A) it is accepted  B) it is refused as stale  C) it replaces the newest version. Correct: B. Only the next version is accepted.

### 7.5 Practice / Assignment

**Owner: [SME]**

Create a task that can be completed without attending the live session. Include task, context, expected output, estimated time, success criteria and resources.

**Your input:**

**Task:** Using your own coding agent and the learner kit in the course repository, build the Session 06 checkpoint: validated delegation contracts and scoped child runs, one shared budget, a deadline-bounded scheduler with the batch hook, and reply correlation with bounded review.

**Context:** Start from your Session 05 checkpoint. Run the prompts on the Session 06 page in order (Prepare, Add the check pack, Build steps 1–4, the exercise, Verify and push, Review); the same prompts are in LEARNER_PROMPTS.md (Lesson 06). The kit gives one file, the offline SupervisorProvider planning fixture. No model key is needed.

**Expected output:** your repository in the course GitLab group with the Lesson 06 check pack passing unchanged (29 tests), LESSON = 6, and the lab result: the INC-001 answer from two children (logs with log_lookup, runbooks with runbook_search, 55 fixture tokens each, 110 shared), parallel faster than sequential, a partial deadline result, review escalated and the report saved as version 1.

**Estimated time:** 3 hours.

**Success criteria:** children have distinct run IDs, the correct parent ID, only their role's tools and no inherited approvals; a child cannot exceed its parent's capabilities, identical contracts are reused and changed ones rejected; the shared budget enforces agent-count, depth and token limits before launch; concurrency never exceeds its limit and dependent work waits for successful predecessors; a deadline preserves completed results and cancels unfinished work, and cycles are rejected; mismatched or stale replies fail validation, and non-converging review escalates.

**Resources:** the Session 06 page, learner-kit/lessons/06 in the course repository, LEARNER_PROMPTS.md (Lesson 06), and the 7.7 reading.

### 7.6 Lesson Reflection

**Owner: [SME]**

Provide reflection questions for independent learners. These may be the same as or adapted from the live session.

**Your input:**

Use the three live-session questions (6.2), plus: 'For one of your own multi-agent ideas, what would you measure to decide whether the team beats one agent?'

### 7.7 Deep Dive / Additional Resources

**Owner: [SME]**

Provide articles, videos, books, documentation, research, internal resources, tools, tutorials or examples. Distinguish Recommended / Essential from Optional / Deep Dive.

**Your input:**

**Essential:** Multi-agent research system (Anthropic): https://www.anthropic.com/engineering/multi-agent-research-system

**Essential:** Building effective agents, parallel and evaluator-optimizer patterns (Anthropic): https://www.anthropic.com/engineering/building-effective-agents

**Optional / deep dive:** Effective context engineering for AI agents, on context isolation and subagents (Anthropic): https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents; and Python's asyncio tasks, timeouts and cancellation: https://docs.python.org/3/library/asyncio-task.html

**Optional / deep dive:** one finished implementation, the course reference at tag lesson-06 (agent_runtime/supervisor.py and agent_runtime/coordination.py) and TESTING.md; read it after building your own.

### 7.8 What's Next

**Owner: [L&D + SME]**

Define the next topic, recommended learning path, practice or next action.

**Your input:**

Next: Session 07, A2A across independent agent services. Recommended path: complete the 7.5 assignment first; Session 07 starts from the Session 06 checkpoint and moves the runbook child to a remote service.

## 8. Materials & Assets

**Owner: [SME]**

Indicate which assets are needed and provide them where applicable.
- Presentation**✔ the Session 06 page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-06/), with Read and Present views, an Instructor view (?instructor) and the prompts-only page**
- Speaker notes**✔ SAY sections of instructor guide 06, also shown in the page's Instructor view**
- Script**✔ instructor guide 06 (complete)**
- Examples**✔ three worked examples in 7.3**
- Case study**✔ is a team worth it: the single agent against the team on INC-001 (activity 4)**
- Demo**✔ the learner kit (learner-kit/lessons/06 in the course repository); the reference tags lesson-05 → lesson-06**
- Screenshots
- Diagrams**✔ six on the Session 06 page: the team's runs, the checks before a child starts, contracts and the child's Context, the budget ledger, the scheduler timeline, replies and review**
- Templates**✔ the 'Read your code' questions after each build step, on the Session 06 page**
- Sample files**✔ the given SupervisorProvider planning fixture (learner-kit/lessons/06/given) and the Lesson 06 check pack (course/labs/l06.py, tests/test_lesson06.py)**
- Quiz questions**✔ five questions in 7.4**
- Practice assignment**✔ 7.5 and LEARNER_PROMPTS.md, Lesson 06**
- Additional resources**✔ 7.7**
- Other:

## 9. Content Accuracy & SME Notes

### 9.1 Important Terminology

**Owner: [SME]**

List terminology that must be used consistently.

**Your input:**

• Supervisor: an agent whose only tool is delegate; its run is the parent of every child it starts.

• Delegation contract: task_id, role (logs or runbooks) and an objective of at most 500 characters.

• Child run: an ordinary run_agent with a new run ID, parent_id set to the supervisor's run ID, only its role's tool, no approvals and its own messages; it never gets delegate.

• Error codes: invalid_delegation, task_id_conflict, child_privilege_escalation, delegation_budget.

• SharedBudget: 5,000 fixture tokens, at most 2 agents, depth 1; each child reserves 1,800 and settles what it used.

• WorkItem and schedule: items with dependencies, a concurrency limit (2) and a deadline; statuses completed, failed, blocked, cancelled; the report completed or partial.

• execute_batch: the optional hook in run_agent through which pending calls run as one batch, results by tool-call ID.

• Envelope: correlation ID, task ID, artifact ID, version and body; accept_reply takes only the next version.

• bounded_review: a reviewer and a producer for at most max_rounds (2); then accepted or escalated with history.

• SupervisorProvider: the given offline planning fixture; a live model could use the same delegate schema.

• Team usage on INC-001: the supervisor 60 fixture tokens, each child 55, 110 from the shared budget; the single agent 75.

• Fixture tokens: the mock's teaching measurement (20 per tool call, 35 per answer, 30 per supervisor reply), not tokenizer counts or cost.

### 9.2 Common Misconceptions

**Owner: [SME]**

List frequent misunderstandings. This will inform explanations, examples, knowledge checks and FAQs.

**Your input:**

• 'A subagent is a different prompt.' It is a separate run with its own ID, messages, tools and limits.

• 'The child can ask for the tools it needs.' The application maps the role to a tool; the parent's tools are the ceiling.

• 'Check the budget after the children finish.' By then concurrent children may have overspent; reserve first.

• 'More agents give a better answer.' On INC-001 the team gives the same answer for more than twice the tokens.

• 'At the deadline everything is lost.' Finished results are kept; only unfinished work is cancelled.

• 'The latest reply wins.' Only the reply matching the request at the next version is accepted.

### 9.3 Important Nuances

**Owner: [SME]**

Document exceptions, limitations, risks, assumptions or cases where the recommended approach does not apply.

**Your input:**

• The supervisor's plan comes from a given offline fixture; planning by a real model was not tested, though the same delegate schema and checks would apply.

• The shared budget covers the children only; the supervisor's own calls sit outside it until Session 11.

• The sequential and parallel timings depend on the machine; judge their direction, not their milliseconds.

• The console shell (Sessions 02 to 07) runs only the single agent: a team submission answers 400 unknown_agent, and child runs appear in the console from Session 08.

• The lab's reviewer always rejects, to show escalation; real review needs explicit acceptance rules.

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
