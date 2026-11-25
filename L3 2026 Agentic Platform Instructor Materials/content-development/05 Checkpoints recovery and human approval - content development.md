# Session 05 content development: Checkpoints recovery and human approval

> Markdown copy of [`05 Checkpoints recovery and human approval - content development.docx`](05%20Checkpoints%20recovery%20and%20human%20approval%20-%20content%20development.docx) for reading on GitHub. The Word document in this repository is the single source of truth; edit it, then regenerate this page with `guide-builder/content_md.py`.

## 1. Topic Overview

### 1.1 Topic Title - Durability: Checkpoints, recovery and human approval (Session 05)

**Owner: [SME]**

### 1.2 Short Topic Description

**Owner: [SME]**

Write 2–4 sentences explaining what the topic is about, why it matters and what learners will explore.

**Your input:**

This session makes a run durable. Until now a run lived only in the memory of the process running it: a crash lost it, and a write it had already made could be made again on the retry. Learners save the run's state at every boundary of the agent loop, with each tool call saved before it is dispatched; stop the run cleanly as waiting_approval when a write needs a person's decision; store that decision for the exact action, with an expiry; and resume the same loop from the saved pending call. A deliberate crash right after a write proves that recovery reads saved evidence (the run, the decision and the effect ledger) rather than asking the model what happened, and leaves exactly one effect.

### 1.3 Level

**Owner: [SME + L&D]**

Select Beginner / Intermediate / Advanced and add context if useful.

**Your input:**

**Context:** L3 is the advanced, selective level of the programme for experienced software engineers. Session 05 completes the single-agent runtime built in Sessions 01 to 04: after it, a run survives worker loss and waits safely for a human decision, which the multi-agent sessions and the platform core build on.

Advanced

### 1.4 Prerequisites

**Owner: [SME]**

List previous topics, knowledge, tools, access or skills required. If none, write “No prerequisites.”

**Your input:**

• Session 04 completed: your project in the course GitLab group with the Lesson 04 check pack passing (19 tests), LESSON = 4, and a Lesson 04 entry in AGENTS.md.

• The Session 02 approval gate and effect ledger in your project: mock_remediate raises ApprovalRequired without an approved action key, and an approved write commits once.

• The earlier prerequisites: independent Python, async code and tests, LLM foundations, and reviewing code a coding agent writes.

• Basic database transactions: what commits together, and what a crash between two writes leaves behind.

• Your coding agent signed in to gitlab.ciklum.net, and a local browser for the platform console.

### 1.5 Session Details

**Owner: [L&D]**

L&D provides date, calendar details and delivery logistics. SME provides estimated time needed and timing constraints.

**Date:** **Nov 25, 2026**

**Session link: zoom**

**Calendar invitation text:**

Draft for L&D: "L3 Building Agentic Platforms, Session 05: Checkpoints, recovery and human approval, Nov 25, 2026 (90 min). Bring your Session 04 checkpoint. You make a run durable: its state saved at every boundary, a write that waits for a person's decision on the exact action, and a run that resumes after a crash without repeating an effect. Session page: https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-05/"

**Duration (SME):** 90 minutes: 30 min discussion (recall and concept) + 60 min guided build, practice and verification. Timing constraint: learners need their Session 04 project passing before the session; the session runs fully offline on the mock model and a labelled remediation fixture.

### 1.6 Speaker(s)

**Owner: [SME + L&D]**

List the main speaker, co-speakers and guest experts and clarify their roles.

**Your input:**   
Maksym Pavlov

**Role:** Maksym Pavlov is the main speaker and SME: the recall discussion, the concept discussion and the guided build, showing each prompt and reviewing the change before learners run it in their own project. Learners' code is checked by the Session 05 check pack (21 tests) and the review prompt. The session page has an instructor view (the page opened with ?instructor) that carries the guide's script and timings.

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

Explain why a run must be able to stop and continue, and define a snapshot, a pending call, a checkpoint, an approval decision, the effect ledger and a terminal state.

**Objective 2:**

Make the agent loop save each tool call before dispatching it and stop as waiting_approval when a write needs approval, and persist runs under tenant and run ID so another tenant cannot load them.

**Objective 3:**

Implement, by directing a coding agent, an approval decision bound to the exact action key, with expiry and denial, kept separate from the run and never taken by the agent on the learner's behalf.

**Objective 4:**

Resume a stored run in the same loop with only the approvals still valid, refusing denied or cancelled runs, and prove with a deliberate crash after a write that exactly one effect exists.

**Objective 5:**

Distinguish the local exactly-once guarantee of a shared transaction from the behaviour of an external API, and name the evidence needed before replaying an unknown remote effect.

## 3. Pre-work

**Owner: [SME]**

Define anything participants need to complete before the live session: reading, video, previous course/module, tool setup, account/access, short task, reflection question or preparation of data/files.

If nothing is required, write: “No pre-work required.”

**Pre-work:**

Complete your Session 04 checkpoint (the Session 04 after-class work): your project in the course GitLab group with the Lesson 04 check pack passing (19 tests) and LESSON = 4. Optional (20 min): the LangGraph pages on persistence and interrupts, as design examples. Think of one write your team's systems make: what happens if the process dies right after it?

## 4. Live Session Design

### 4.1 Session Agenda

**Owner: [SME]**

Provide the proposed flow and approximate timing.

| Section | Topic | Approx. time | Format |
|---|---|---|---|
| 1 | Reconnect: recall the Session 02 approval gate and the Session 04 baseline | 0–10 min | Discussion |
| 2 | Concept: a run that stops and continues; snapshot, approval decision and effect ledger; where a crash can happen | 10–30 min | Presentation + discussion |
| 3 | Build steps 1 and 2: save the run and pause the loop, store the exact decision | 30–45 min | Guided build |
| 4 | Build steps 3 and 4: resume from the pending call, crash on purpose | 45–60 min | Guided build |
| 5 | Exercise: crash after the write, an expired approval, a denial, changed arguments | 60–75 min | Hands-on practice |
| 6 | Verify and push (21 checks), and interpret the crash demonstration | 75–85 min | Verification |
| 7 | Questions and handoff to Session 06 | 85–90 min | Discussion |

### 4.2 Topic-by-Topic Content

**Owner: [SME]**

For each section, provide:

Key concepts — what does the participant need to know?

Common misconceptions — what do learners frequently misunderstand?

Key message — the one thing participants should remember from this section.

**Section 1:**

The snapshot: save the run, and save the call before making it

**Key concepts:** a snapshot is the whole run as data (messages, pending tool calls, step and token counters, status, answer and events), saved under its tenant and run ID. The loop records the model's tool calls as pending and saves before dispatching them, so a crash at any later moment still leaves the call on record. When the tool boundary raises ApprovalRequired, the loop stops with status waiting_approval, keeps the call pending and saves; many learners' loops need this small change, because every check up to Session 04 passes without it.

**Common misconceptions:** saving the chat transcript or the final answer is enough to recover; the store can infer the tenant from the messages; process memory survives a restart.

**Key message:** save the whole run under tenant and run ID, and save each call before it runs.

**Section 2:**

The approval decision: one exact action, for a limited time

**Key concepts:** a decision is its own record: tenant, run, the action key of the pending call, an expiry and the verdict, approve or deny. The action key binds tenant, run, tool and canonical arguments, so approving a rollback of INC-001 says nothing about INC-002. A denial ends the run as denied. The proposal comes from a clearly labelled fixture, RemediationProvider, not from an operational recommendation.

**Common misconceptions:** an approved flag on the run is enough; an approval lasts for ever; the coding agent may approve on the learner's behalf to finish the demonstration.

**Key message:** a person approves one exact action key, with an expiry, as a record of its own.

**Section 3:**

Resume: the same loop, from the saved pending call

**Key concepts:** resume_run loads the snapshot, refuses a denied or cancelled run, replaces the run's approved keys with the decisions still valid, and continues the same run_agent with initial=run. The loop executes the pending call before asking the model anything. An expired approval makes the boundary raise ApprovalRequired again, so the run is back to waiting_approval: authority is never renewed silently.

**Common misconceptions:** resuming means starting the run again from the task; the model can be asked whether the earlier write succeeded; an expired approval should be extended automatically.

**Key message:** recovery uses saved application evidence, never the model's account of what happened.

**Section 4:**

Crash on purpose: one effect, whatever happens

**Key concepts:** fault injection visits the moment happy-path checks never reach: the effect has committed but the run has not saved the observation. The check pack's demonstration executes the approved write, raises WorkerCrash (a BaseException, so nothing handles it as an ordinary error), opens a new store and executor on the same database file and resumes. The Session 02 ledger finds the action key and returns the stored result with replayed true, so exactly one effect exists. The same holds for a crash before the write; an expired approval leaves zero.

**Common misconceptions:** a passing happy path proves recovery; one effect in the local ledger means exactly-once for any external API; a simulated crash can be an ordinary exception.

**Key message:** the local guarantee rests on one transaction; an external API needs its own idempotency or reconciliation.

### 4.3 Interactive Activities

**Owner: [SME content + L&D learning design]**

Identify where participants should actively engage.
- Poll**✔ (approval block) Is an approved=true flag on the run enough to authorise a write?**
- Discussion**✔ (opening, 0–10 min) Recall: what did your Session 02 boundary do with an unapproved write, and what happened to the run?**
- Case study**✔ (crash block) The worker dies right after the rollback commits: what does each saved record say, and what does resume do?**
- Breakout activity
- Quiz
- Hands-on exercise**✔ (30–75 min) Learners run the build prompts and break the recovery on purpose in their own project**
- Live demo**✔ (30–60 min) The instructor shows each prompt, its change and the crash demonstration**
- Problem-solving activity**✔ (close) Which writes in your own systems could be replayed safely, and which need reconciliation first?**
- Reflection**✔ (close) Mark durable runs and approvals on your platform blueprint**

**Activity details (SME content and L&D will turn into activity in zoom or whiteboard):**

For each activity include: Purpose • Instructions • Time • Expected outcome • Debrief / discussion points.

**1. Discussion: recall the approval gate.** Purpose: connect Session 02 and Session 04 to today. Instructions: three questions: what the Session 02 boundary did with an unapproved write and what happened to the run; why the same approved rollback executed twice gives one effect; which of the Session 04 baseline numbers today's change should move. Time: 10 min. Expected outcome: learners name ApprovalRequired, the effect ledger and its shared transaction, and expect no change to the baseline. Debrief: today adds the records around the gate, not a new gate.

**2. Poll: is an approved flag enough?** Options: yes, a flag on the run / no, a decision bound to the exact action key with an expiry / only if the model asks again. Correct: the exact key with an expiry. Time: 2 min. Debrief: a flag does not say which operation and arguments were reviewed, so a changed proposal could inherit it.

**3. Guided build: the four build steps.** Purpose: learners make runs durable in their own project. Instructions: for each step the instructor explains it and runs the prompt; learners run the same prompt and compare the agent's change and the checks with the excerpt on the session page, then answer the page's 'Read your code' questions from their own code. Time: 30 min. Expected outcome: the loop pauses and continues, runs are stored under tenant and run ID, decisions are stored with expiry, and resume_run passes the Lesson 05 checks. Debrief: where in your code is a call saved before it runs?

**4. Case study: the crash after the write.** Purpose: place each failure on the state diagram. Instructions: walk through the check pack's crash demonstration; for crash before the write, crash after the write, an expired approval and a denial, name what is saved and what resume does. Time: 5 min. Expected outcome: one effect after either crash, zero after expiry or denial, each resolved from a saved record. Debrief: the model is never asked what happened.

**5. Hands-on: break the recovery on purpose.** Purpose: prove the guarantees hold. Instructions: first approve, as your own decision, the run build step 2 left waiting, and resume it; then predict, and run in a throwaway script: the crash after the write (inspect the stored snapshot and the effect count), an expired approval, a denied proposal, and an approval for INC-001 against a fixture variant proposing INC-002. Time: 15 min. Expected outcome: your run completed; completed with one effect, still waiting, PermissionError, and a new key the old approval does not cover. Debrief: which record decided each case?

**6. Problem-solving: replay or reconcile?** Purpose: carry the lesson to real systems. Instructions: for one write your team's systems make, decide whether a retry is safe (the receiver keeps an idempotency key and its result) or whether recovery must first reconcile with the external system. Time: 3 min. Expected outcome: a named write and the evidence each choice needs.

**7. Reflection: durable runs.** Purpose: connect today to the platform. Instructions: mark durable runs and approvals on your blueprint; Session 08 puts this store behind the platform's run API and adds the console's Approvals view, and Session 10 lets the operator present a signed token. Time: 3 min. Expected outcome: an updated sketch.

### 4.4 Practical Application After the Session

**Owner: [SME]**

Describe what participants will actually do.

**Task:**

Finish the Session 05 build in your own project and prove the crash recovery.

**Instructions:**

• Finish any prompt you did not complete in class, in order: Prepare, Add the check pack, Build steps 1–4, the exercise, Verify and push, and Review.

• Read each change before running the next prompt, using the page's 'Read your code' questions. The check pack must pass unchanged; never edit it to get a pass.

• Practice: add a crash before the write and compare its stored state with the after-write case: the same pending call, but no ledger row.

• Practice: write a short recovery runbook: which operations can be retried automatically and which require reconciliation with the external system first.

• In the console: check mock_remediate in the Tools view as demo-operator, change one argument and compare the action keys, then restart the platform and see that the shell's in-memory runs are gone.

• Read the LangGraph pages on persistence and interrupts, about 40 minutes.

**Expected result:**

Your project in the course GitLab group with the Lesson 05 check pack passing unchanged (21 tests), LESSON = 5, a Lesson 05 entry in AGENTS.md, and the crash demonstration's result: paused waiting_approval, resumed completed, one effect. Estimated time: 2–3 hours.

**Feedback / debrief points:**

• Did the coding agent's claims match the check output? Unrun or skipped checks are not passes.

• Did your coding agent leave the run you were shown waiting for your decision, or did it approve on your behalf?

• Which record answers each question after a crash: where the run stopped, whether a person approved, whether the write happened?

## 5. Presentation

### 5.1 Presentation Content

**Owner: [SME]**

Provide the presentation content or draft. Recommended logic: Context → Concept → Example → Application → Practice → Summary.

**Presentation / slide deck:**

The Session 05 page is the presentation, with Read and Present views (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-05/), plus an Instructor view for the presenter (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-05/?instructor) and a prompts-only page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-05-just-prompts/). No slide deck is made: the session page replaces it. Outline:

• 1. Recall: the Session 02 approval gate and effect ledger; what happened to a run that hit it.

• 1b. Words first: investigation, run, step, worker and run ID, and how they relate (a diagram).

• 1c. Design choice: who owns the run. A: the platform owns runs on shared compute, the runtime embedded and created on demand (like multi-tenant SaaS); B: each runtime instance owns its sessions (like a premium client's dedicated instance), where an approval becomes cross-system state management. Two diagrams and a comparison.

• 2. The idea: a run must stop and continue without guessing; definitions of snapshot, pending call, checkpoint, approval decision, effect ledger, resume and terminal state.

• 3. One tool call through the loop, with the moments a crash can happen and the approval branch.

• 4. The snapshot: save before dispatch, pause on ApprovalRequired, store under tenant and run ID.

• 5. The approval: one exact action key, an expiry, approve or deny.

• 6. Resume: the same loop, only valid approvals, terminal runs refused.

• 7. Crash on purpose: one effect after a crash after the write; the local guarantee and its limit.

• 8. Application: the prepare and check-pack prompts, then the four build prompts, each with 'Read your code'.

• 9. Practice: break the recovery on purpose.

• 10. Verification: 21 passed and the crash demonstration.

• 11. Summary (what changed in the project, what to try in the console), recovery prompts and the after-class assignment.

## 6. Session Wrap-up

### 6.1 Conclusions / Key Takeaways

**Owner: [SME]**

Define 3–5 essential messages participants should leave the session with. These will also be used in e-learning.

**Key takeaway 1:**

A run must be able to stop and continue, after a crash or a person's decision, without guessing what already happened.

**Key takeaway 2:**

Save each tool call before it runs, and stop the run as waiting_approval when a write needs a decision.

**Key takeaway 3:**

A person approves one exact action key, with an expiry, as a record of its own; the agent never approves.

**Key takeaway 4:**

Resume the same loop from the saved pending call, with only the approvals still valid; denied and cancelled runs never resume.

**Key takeaway 5:**

Recovery reads saved records, never the model's account; one effect in a local ledger does not make an external API exactly-once.

### 6.2 Lesson Reflection

**Owner: [SME]**

Provide 2–4 questions that help participants connect the topic to their own work.

Suggested framing: “Before moving on, consider:”

**Reflection question 1:**

Which write in your own systems would be repeated today if the process died right after making it?

**Reflection question 2:**

Where does your team keep the record that a person approved an action, and does it name the exact action?

**Reflection question 3:**

For one external API you call, what evidence would tell a resumed run that its earlier write already happened?

### 6.3 What's Next

**Owner: [SME + L&D]**

Identify the logical next step: next session, next topic, practice assignment, certification or deeper learning.

**What's next:**

Session 06, Supervisor, subagents and parallel coordination (120 min): a supervisor delegates to scoped subagents with narrowed context and permissions under one shared budget. Bring your Session 05 checkpoint.

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

• Video 1 (5 min): why a run must stop and continue; snapshot, approval decision and effect ledger.

• Video 2 (5 min): saving before dispatch and pausing as waiting_approval.

• Video 3 (4 min): an exact, expiring approval and resuming from the pending call.

• Video 4 (5 min): the crash after the write, and the limit of a local guarantee.

• Knowledge check (7.4) and the self-paced assignment (7.5).

Source material: the Session 05 page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-05/) and instructor guide 05.

### 7.3 Examples / Use Cases

**Owner: [SME]**

Provide examples that can stand on their own in e-learning. Include enough context for someone who was not at the live session.

**Your input:**

**Example 1: the crash after the write.** An operator approves the INC-001 rollback. The worker executes it, the effect and its ledger row commit, and the process dies before the observation is saved. The stored run still has the call pending. On resume the call executes again; the ledger finds its action key and returns the stored result marked replayed, and the run completes with one effect.

**Example 2: an approval that expired.** A rollback was approved for five minutes, and the run resumes an hour later. resume_run passes only the approvals still valid, the boundary raises ApprovalRequired again, and the run is back to waiting_approval with no effect. The operator decides again on the current proposal.

**Example 3: an approval for different arguments.** The operator approved a rollback of INC-001; the run now proposes a rollback of INC-002. The action key binds the arguments, so the keys differ and the old approval does not cover the new action: the run waits for a new decision.

### 7.4 Knowledge Check

**Owner: [SME]**

Provide 3–5 questions testing the most important concepts. Include question, options if applicable, correct answer and explanation. L&D adapts them into the final interaction.

**Your input:**

**Q1. When does the loop save a tool call the model asked for?** A) after it returns a result  B) before it is dispatched  C) only at the end of the run. Correct: B. Saved before dispatch, the call survives any crash that follows.

**Q2. A write needs approval and none is stored. What should the loop do?** A) fail the run  B) stop as waiting_approval, keep the call pending and save  C) ask the model to choose another tool. Correct: B.

**Q3. The worker died right after an approved write committed. How does the resumed run know not to write again?** A) it asks the model  B) the effect ledger holds the action key and its stored result  C) it cannot know. Correct: B.

**Q4. An approval expired before resume. What happens?** A) it is extended automatically  B) the run waits for a new decision  C) the write runs anyway. Correct: B. Authority is never renewed silently.

**Q5. Does one effect in the local ledger guarantee exactly-once for an external API?** A) yes  B) no: the receiver must support idempotency, or recovery must reconcile first  C) only with a real model. Correct: B.

### 7.5 Practice / Assignment

**Owner: [SME]**

Create a task that can be completed without attending the live session. Include task, context, expected output, estimated time, success criteria and resources.

**Your input:**

**Task:** Using your own coding agent and the learner kit in the course repository, build the Session 05 checkpoint: a loop that pauses and continues, a run store keyed by tenant and run ID, exact and expiring approval decisions, resume_run, and the crash demonstration with one effect.

**Context:** Start from your Session 04 checkpoint. Run the prompts on the Session 05 page in order (Prepare, Add the check pack, Build steps 1–4, the exercise, Verify and push, Review); the same prompts are in LEARNER_PROMPTS.md (Lesson 05). This lesson's kit has no given files, only the check pack. No model key is needed.

**Expected output:** your repository in the course GitLab group with the Lesson 05 check pack passing unchanged (21 tests), LESSON = 5, and the lab result: paused waiting_approval, the approved mock_remediate rollback of INC-001, resumed completed, effects_after_crash_and_resume 1.

**Estimated time:** 3 hours.

**Success criteria:** the initial remediation run waits for approval with no effect; an approved action survives a simulated worker crash and resumes; crash-after-write recovery leaves exactly one effect; an expired approval does not execute the action; denied and cancelled runs cannot be resumed as approved work.

**Resources:** the Session 05 page, learner-kit/lessons/05 in the course repository, LEARNER_PROMPTS.md (Lesson 05), and the 7.7 reading.

### 7.6 Lesson Reflection

**Owner: [SME]**

Provide reflection questions for independent learners. These may be the same as or adapted from the live session.

**Your input:**

Use the three live-session questions (6.2), plus: 'Which of your platform's runs could be waiting for a person right now, and where would you see it?'

### 7.7 Deep Dive / Additional Resources

**Owner: [SME]**

Provide articles, videos, books, documentation, research, internal resources, tools, tutorials or examples. Distinguish Recommended / Essential from Optional / Deep Dive.

**Your input:**

**Essential:** Persistence, checkpoints and threads (LangGraph documentation, as a design example): https://docs.langchain.com/oss/python/langgraph/persistence

**Essential:** Interrupts and human approval (LangGraph documentation, as a design example): https://docs.langchain.com/oss/python/langgraph/interrupts

**Optional / deep dive:** Making retries safe with idempotent APIs (Amazon Builders' Library): https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/

**Optional / deep dive:** one finished implementation, the course reference at tag lesson-05 (agent_runtime/durable.py) and TESTING.md; read it after building your own.

### 7.8 What's Next

**Owner: [L&D + SME]**

Define the next topic, recommended learning path, practice or next action.

**Your input:**

Next: Session 06, Supervisor, subagents and parallel coordination. Recommended path: complete the 7.5 assignment first; Session 06 starts from the Session 05 checkpoint, and its subagents run under the same runtime and authority boundaries.

## 8. Materials & Assets

**Owner: [SME]**

Indicate which assets are needed and provide them where applicable.
- Presentation**✔ the Session 05 page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-05/), with Read and Present views, an Instructor view (?instructor) and the prompts-only page**
- Speaker notes**✔ SAY sections of instructor guide 05, also shown in the page's Instructor view**
- Script**✔ instructor guide 05 (complete)**
- Examples**✔ three worked examples in 7.3**
- Case study**✔ the check pack's crash after the write (activity 4)**
- Demo**✔ the learner kit (learner-kit/lessons/05 in the course repository); the reference tags lesson-04 → lesson-05**
- Screenshots
- Diagrams**✔ one tool call through the loop, with the crash points and the approval branch, on the Session 05 page**
- Templates**✔ the 'Read your code' questions after each build step, on the Session 05 page**
- Sample files**✔ the Lesson 05 check pack: the crash demonstration and the labelled RemediationProvider fixture (course/labs/l05.py) and tests/test_lesson05.py**
- Quiz questions**✔ five questions in 7.4**
- Practice assignment**✔ 7.5 and LEARNER_PROMPTS.md, Lesson 05**
- Additional resources**✔ 7.7**
- Other:

## 9. Content Accuracy & SME Notes

### 9.1 Important Terminology

**Owner: [SME]**

List terminology that must be used consistently.

**Your input:**

• Investigation: what someone asks the platform for: a supported cause for one incident of one tenant (Runs view, POST /runs).

• Run: one agent's attempt at one task, from the request to a final status, under one run ID and one tenant. Each investigation submitted starts one run to answer it; submitting it again starts another run; from Session 06 one investigation is a parent run with child runs. A run is not always an investigation: the lesson's remediation run is one too.

• Step: one model call inside a run; tool calls happen between steps.

• Worker: the process that executes a run for a while; from this session a run can be continued by another worker and stays the same run.

• Snapshot: the whole run as data (messages, pending calls, counters, status, answer, events), saved under tenant and run ID.

• Pending call: a tool call the model asked for that has no observation yet; saved before it is dispatched.

• Checkpoint: the loop's save of the snapshot, after recording pending calls, after each observation, on a pause and at the end.

• waiting_approval: the status of a run stopped because a write's action key is not approved.

• Action key: a SHA-256 binding tenant, run ID, tool name and canonical arguments (Session 02).

• Approval decision: tenant, run, action key, expiry and approve or deny, stored apart from the run.

• Effect ledger: the effects table, one row per action key, written in the same transaction as the effect.

• resume_run: loads the snapshot, refuses denied or cancelled runs, refreshes approvals and continues run_agent with initial=run.

• Terminal states: completed, failed, denied, cancelled; denied and cancelled never resume as approved work.

• WorkerCrash: the check pack's simulated process loss, a BaseException so it is not handled as an error.

• RemediationProvider: a deterministic fixture that proposes one rollback; not an operational recommendation.

• Replayed: the flag on a result returned from the ledger for an action key that already committed.

### 9.2 Common Misconceptions

**Owner: [SME]**

List frequent misunderstandings. This will inform explanations, examples, knowledge checks and FAQs.

**Your input:**

• 'Saving the transcript is enough.' Recovery needs the pending calls, counters and control state too.

• 'Approved is a yes/no flag.' A decision names the exact action key and expires.

• 'The agent can approve to finish the demo.' The person decides; the agent shows the proposal and stops.

• 'Ask the model whether the write succeeded.' The ledger is the evidence; the model's narrative is not.

• 'An expired approval can be extended on resume.' The run waits for a new decision.

• 'One local effect means exactly-once everywhere.' External APIs need their own idempotency or reconciliation.

### 9.3 Important Nuances

**Owner: [SME]**

Document exceptions, limitations, risks, assumptions or cases where the recommended approach does not apply.

**Your input:**

• The exactly-once demonstration rests on the mock effect and its ledger row sharing one SQLite transaction; it does not extend to arbitrary remote APIs.

• Every check up to Session 04 passes without the loop catching ApprovalRequired, because the given console shell catches it itself; build step 1 asks learners' agents to add only what their loop lacks.

• After a crash right after the write, the stored status can still read waiting_approval until the resumed run saves again; resume reads the pending call and the ledger, not the status. A platform that shows status to people should save running before dispatching a resumed call.

• The action key binds the run ID, so the lab's key changes on every run; the rest of its output does not.

• The console shell (Sessions 02 to 07) keeps runs in memory and has no approval view: a restart empties it. The platform core puts the durable store behind the run API and adds the Approvals view in Session 08.

• Design choice: the course builds platform-owned runs (design A): one run store, the runtime created per execution, an approval as a stored decision plus a resume. With independent runtime instances that own their sessions (design B), the decision must reach the instance and session that asked, so correlation, persistence on the runtime side, expiry on both sides and one agreed source of truth for status become the platform's problem. Session 07's A2A specialist, which keeps its tasks in its own memory, is design B in miniature.

• All incident data are synthetic, the remediation is a mock, and the demo identities are for loopback use only.

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
