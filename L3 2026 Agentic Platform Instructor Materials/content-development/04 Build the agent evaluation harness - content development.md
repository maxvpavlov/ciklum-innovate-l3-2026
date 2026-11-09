# Session 04 content development: Build the agent evaluation harness

> Markdown copy of [`04 Build the agent evaluation harness - content development.docx`](04%20Build%20the%20agent%20evaluation%20harness%20-%20content%20development.docx) for reading on GitHub. The Word document in this repository is the single source of truth; edit it, then regenerate this page with `guide-builder/content_md.py`.

## 1. Topic Overview

### 1.1 Topic Title - Evaluation: Build the agent evaluation harness (Session 04)

**Owner: [SME]**

### 1.2 Short Topic Description

**Owner: [SME]**

Write 2–4 sentences explaining what the topic is about, why it matters and what learners will explore.

**Your input:**

This session builds the platform's measuring instrument. One good run proves nothing about an agent: the same incident can pass once and fail the next time, and a fluent answer can be wrong. Learners write down the expected outcome of five incident cases before running anything, grade every run on three separate checks (outcome, evidence, tool policy), repeat each case several times, keep a held-out split they never tune against, and record the dataset's identity with every result. An optional model judge is calibrated against human labels before anyone trusts it. The result is a single-agent baseline that every later change, and the Session 11 release gate, is measured against.

### 1.3 Level

**Owner: [SME + L&D]**

Select Beginner / Intermediate / Advanced and add context if useful.

**Your input:**

**Context:** L3 is the advanced, selective level of the programme for experienced software engineers. Session 04 turns the agent learners built in Sessions 01 to 03, which now also runs on a real model, into something they can measure.

Advanced

### 1.4 Prerequisites

**Owner: [SME]**

List previous topics, knowledge, tools, access or skills required. If none, write “No prerequisites.”

**Your input:**

• Session 03 completed: your project in the course GitLab group with the Lesson 03 check pack passing (17 tests), LESSON = 3, and a Lesson 03 entry in AGENTS.md.

• Your Groq key saved in ~/agentic-course/groq.env (from Session 03); today's checks run on the offline mock and do not need it.

• The earlier prerequisites: independent Python, async code and tests, LLM foundations, and reviewing code a coding agent writes.

• Basic statistics: a mean, a rate, and why a small sample varies.

• Your coding agent signed in to gitlab.ciklum.net, and a local browser for the platform console.

### 1.5 Session Details

**Owner: [L&D]**

L&D provides date, calendar details and delivery logistics. SME provides estimated time needed and timing constraints.

**Date:** **Nov 11, 2026**

**Session link: zoom**

**Calendar invitation text:**

Draft for L&D: "L3 Building Agentic Platforms, Session 04: Build the agent evaluation harness, Nov 11, 2026 (90 min). Bring your Session 03 checkpoint. You turn incident cases into a repeatable evaluation: expected outcomes written in advance, separate grades for outcome, evidence and tool policy, repeated trials, a held-out split, and a recorded single-agent baseline. Session page: https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-04/"

**Duration (SME):** 90 minutes: 30 min discussion (recall and concept) + 60 min guided build, practice and verification. Timing constraint: learners need their Session 03 project passing before the session; the session runs fully offline on the mock model.

### 1.6 Speaker(s)

**Owner: [SME + L&D]**

List the main speaker, co-speakers and guest experts and clarify their roles.

**Your input:**   
Maksym Pavlov

**Role:** Maksym Pavlov is the main speaker and SME: the recall discussion, the concept discussion and the guided build, showing each prompt and reviewing the change before learners run it in their own project. Learners' code is checked by the Session 04 check pack (19 tests) and the review prompt. The session page has an instructor view (the page opened with ?instructor) that carries the guide's script and timings.

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

Explain why one successful run is not evidence of agent quality, and define a case, a trial, a split (development and held-out) and a dataset identity.

**Objective 2:**

Write evaluation cases as requirements, with the expected outcome stated before any run, including missing, ambiguous and other-tenant cases, and justify why outcomes, not tool-call sequences, are what is fixed.

**Objective 3:**

Implement, by directing a coding agent, separate grades for outcome, evidence and tool policy, and show that a plausible but wrong cause fails.

**Objective 4:**

Run repeated trials per case, keep every per-trial row alongside the means, and compare results only when the dataset hash and split match.

**Objective 5:**

Calibrate an optional model judge against paired human labels, and explain why deterministic checks stay authoritative for permissions and missing evidence.

## 3. Pre-work

**Owner: [SME]**

Define anything participants need to complete before the live session: reading, video, previous course/module, tool setup, account/access, short task, reflection question or preparation of data/files.

If nothing is required, write: “No pre-work required.”

**Pre-work:**

Complete your Session 03 checkpoint (the Session 03 after-class work): your project in the course GitLab group with the Lesson 03 check pack passing (17 tests) and LESSON = 3. Optional (20 min): 'Demystifying evals for AI agents' (Anthropic). Think of one real agent your team runs or plans: what would a case for it look like?

## 4. Live Session Design

### 4.1 Session Agenda

**Owner: [SME]**

Provide the proposed flow and approximate timing.

| Section | Topic | Approx. time | Format |
|---|---|---|---|
| 1 | Reconnect: recall discussion on artifacts and the Session 03 checkpoint | 0–10 min | Discussion |
| 2 | Concept: why one run proves nothing; cases, trials, splits, dataset identity; three separate grades | 10–30 min | Presentation + discussion |
| 3 | Build steps 1 and 2: the cases, and grading outcome, evidence and policy | 30–45 min | Guided build |
| 4 | Build steps 3 and 4: repeated trials, and calibrating a model judge | 45–60 min | Guided build |
| 5 | Exercise: break a check on purpose, held-out trials, a flagged judge disagreement | 60–75 min | Hands-on practice |
| 6 | Verify and push (19 checks), and interpret the baseline report | 75–85 min | Verification |
| 7 | Questions and handoff to Session 05 | 85–90 min | Discussion |

### 4.2 Topic-by-Topic Content

**Owner: [SME]**

For each section, provide:

Key concepts — what does the participant need to know?

Common misconceptions — what do learners frequently misunderstand?

Key message — the one thing participants should remember from this section.

**Section 1:**

Cases: the expected outcome comes first

**Key concepts:** a case is one incident with its expected result written down before any run: tenant, incident, cause, and whether the evidence should be sufficient. The five course cases cover a known cause (INC-001, pool exhaustion), a second one (INC-002, clock skew), a missing incident (INC-404, which must stay unknown), an ambiguous one (INC-003, insufficient evidence) and another tenant (Locomotive's INC-001, quota exhaustion). Three are for development and two are held out. The hash of the case list is the dataset's identity.

**Common misconceptions:** a case should fix the exact tool calls; it is fine to edit the held-out cases when the agent fails them; a bigger dataset is always better.

**Key message:** write the outcome down first, fix outcomes not paths, and never tune against the held-out cases.

**Section 2:**

Three grades, not one score

**Key concepts:** every run is graded on outcome (right status and cause), evidence (a known cause must be backed by cited sources) and tool policy (no remediation during an investigation). A plausible but wrong cause fails the outcome check, which is what catches Session 03's INC-003 live answer that named a cause the evidence did not support.

**Common misconceptions:** a single success percentage tells you whether a change is acceptable; a cited source means the answer is right; a completed run is a correct run.

**Key message:** separate checks say why a run failed; one blended score hides it.

**Section 3:**

Repeated trials and the baseline

**Key concepts:** each case runs several times, each trial with a fresh executor and context. Every trial keeps its own row (checks, tokens, steps, elapsed time, cost when rates are known); the report adds the success rate and means, the provider, the split and the dataset hash. The mock's results are identical every trial; a real model's are not, which is exactly what repeated trials reveal.

**Common misconceptions:** the mean is enough; a passing offline run proves live quality; fixture tokens are cost.

**Key message:** keep the rows, report the identity, and compare only like with like: same dataset hash, same split.

**Section 4:**

A judge is a measuring tool that needs checking

**Key concepts:** a model judge can grade what code cannot, such as whether a summary is faithful. It is another fallible model, so it is calibrated first: paired human and judge labels give an agreement rate and the indices where they disagree, and each disagreement is reviewed by a person. The agent's answer stays untrusted data even inside the judge's prompt.

**Common misconceptions:** a judge replaces deterministic checks; high agreement on a handful of labels proves a judge reliable; when the judge disagrees, change the agent.

**Key message:** calibrate before trusting; keep permission and evidence checks deterministic.

### 4.3 Interactive Activities

**Owner: [SME content + L&D learning design]**

Identify where participants should actively engage.
- Poll**✔ (concept) Should a case require exactly two tool calls for a correct investigation?**
- Discussion**✔ (opening, 0–10 min) Recall: what made the Session 03 report an artifact, and which artifacts does an evaluation produce?**
- Case study**✔ (grades block) Session 03's live INC-003 answer named a cause and passed the citation check: which grade catches it?**
- Breakout activity
- Quiz
- Hands-on exercise**✔ (30–75 min) Learners run the build prompts and break each check on purpose in their own project**
- Live demo**✔ (30–60 min) The instructor shows each prompt, its change and the baseline report**
- Problem-solving activity**✔ (step 4) Decide what to do with a flagged judge disagreement**
- Reflection**✔ (close) Mark the evaluation harness on your platform blueprint and note your baseline**

**Activity details (SME content and L&D will turn into activity in zoom or whiteboard):**

For each activity include: Purpose • Instructions • Time • Expected outcome • Debrief / discussion points.

**1. Discussion: recall artifacts.** Purpose: connect Session 03 to today. Instructions: four questions: which Session 03 outputs are artifacts, memory or history; what happens when an approved plan is edited; what artifacts your team's agents produce; which artifacts an evaluation produces and what makes two comparable. Time: 10 min. Expected outcome: learners name provenance, versions and lifecycle, and arrive at the dataset hash and split. Debrief: today's report is an artifact too.

**2. Poll: fix the path or the outcome?** Options: require exactly two tool calls / check only the outcome and the policy / both. Correct: outcome and policy. Time: 2 min. Debrief: different valid strategies reach the same supported answer; fix what matters.

**3. Guided build: the four build steps.** Purpose: learners build the harness in their own project. Instructions: for each step the instructor explains it and runs the prompt; learners run the same prompt and compare the agent's change and the checks with the excerpt on the session page. Time: 30 min. Expected outcome: cases, grades, repeated trials and judge calibration built, with the Lesson 04 checks passing step by step. Debrief: where in your code would a wrong cause be caught?

**4. Case study: the INC-003 live answer.** Purpose: show why outcome grading matters. Instructions: recall the Session 03 live run whose INC-003 answer named a cause and passed the citation check; ask which of today's grades fails it. Time: 5 min. Expected outcome: the outcome check fails it, because INC-003's expected result is insufficient evidence. Debrief: a valid citation proves provenance, not correctness.

**5. Hands-on: break each check on purpose.** Purpose: prove the checks catch what they claim. Instructions: in a local test add an unsupported answer and a remediation call, and confirm the evidence and policy checks fail; run two trials on the held-out split and find every row; use the calibration example to explain the flagged disagreement. Time: 15 min. Expected outcome: two failing checks, four held-out rows, one disagreement index. Debrief: which failure would a single score have hidden?

**6. Problem-solving: a judge disagrees.** Purpose: treat the judge as a measuring tool. Instructions: given a disagreement between a human label and the judge, decide what to review first. Time: 3 min. Expected outcome: review the case and the rubric, correct the label or the judge, and never change the agent just to please the judge.

**7. Reflection: the baseline.** Purpose: connect today to the platform. Instructions: note your baseline (success rate, mean tokens, dataset hash) and mark the harness on your blueprint; it becomes the release gate in Session 11 and the comparison point for the Session 12 capstone. Time: 3 min. Expected outcome: an updated sketch and a saved report.

### 4.4 Practical Application After the Session

**Owner: [SME]**

Describe what participants will actually do.

**Task:**

Finish the Session 04 build in your own project and record your single-agent baseline.

**Instructions:**

• Finish any prompt you did not complete in class, in order: Prepare, Add the check pack, Build steps 1–4, the exercise, Verify and push, and Review.

• Read each change before running the next prompt. The check pack must pass unchanged; never edit it, or the cases, to get a pass.

• Practice: create a versioned extension of the dataset with one new case and its rationale, and keep the previous baseline next to the new one: the dataset hash will differ, so say why the two are not directly comparable.

• Practice: compare full history and bounded context (Session 03) on the same cases, and report outcome quality and usage together.

• Optional: run INC-003 a few times on Groq from your console and compare with the mock's result; treat it as an observation, not a test.

• Read 'Demystifying evals for AI agents' and 'Writing tools for agents' (Anthropic), about 1 hour.

**Expected result:**

Your project in the course GitLab group with the Lesson 04 check pack passing unchanged (19 tests), LESSON = 4, a Lesson 04 entry in AGENTS.md, and your baseline report (success rate, mean tokens and steps, dataset hash and split). Estimated time: 2–3 hours.

**Feedback / debrief points:**

• Did the coding agent's claims match the check output? Unrun or skipped checks are not passes.

• Which of your three checks would have caught the Session 03 INC-003 live answer, and why?

• What would make you trust a model judge for a property your code cannot check?

## 5. Presentation

### 5.1 Presentation Content

**Owner: [SME]**

Provide the presentation content or draft. Recommended logic: Context → Concept → Example → Application → Practice → Summary.

**Presentation / slide deck:**

The Session 04 page is the presentation, with Read and Present views (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-04/), plus an Instructor view for the presenter (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-04/?instructor) and a prompts-only page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-04-just-prompts/). No slide deck is made: the session page replaces it. Outline:

• 1. Recall: what made the Session 03 report an artifact; which artifacts an evaluation produces.

• 2. The idea: one good run proves nothing; definitions of case, trial, grade, split, dataset hash and baseline.

• 3. The harness at a glance: cases → trials → grades → report.

• 4. Cases: expected outcomes first; the five course cases and their splits.

• 5. Three grades: outcome, evidence, tool policy; the INC-003 live answer as the example.

• 6. Repeated trials: per-trial rows, means and the dataset identity.

• 7. A model judge: calibration, agreement and disagreements.

• 8. Application: the prepare and check-pack prompts, then the four build prompts.

• 9. Practice: break each check on purpose; held-out trials.

• 10. Verification: 19 passed and the baseline report.

• 11. Summary, recovery prompts and the after-class assignment.

## 6. Session Wrap-up

### 6.1 Conclusions / Key Takeaways

**Owner: [SME]**

Define 3–5 essential messages participants should leave the session with. These will also be used in e-learning.

**Key takeaway 1:**

One good run proves nothing: measure the same cases many times and keep every result.

**Key takeaway 2:**

Write the expected outcome before the run, and fix outcomes, not tool-call paths.

**Key takeaway 3:**

Grade outcome, evidence and tool policy separately, so a failure says why.

**Key takeaway 4:**

Compare results only with the same dataset hash and split, and never tune against the held-out cases.

**Key takeaway 5:**

A model judge is a measuring tool: calibrate it against people before trusting it, and keep permission and evidence checks deterministic.

### 6.2 Lesson Reflection

**Owner: [SME]**

Provide 2–4 questions that help participants connect the topic to their own work.

Suggested framing: “Before moving on, consider:”

**Reflection question 1:**

Which decision of one of your own agents is judged today by one good demo rather than by repeated cases?

**Reflection question 2:**

What would your team's first five evaluation cases be, and which of them would you hold out?

**Reflection question 3:**

Which property of your agent's answers can code check, and which would need a judge, and how would you calibrate it?

### 6.3 What's Next

**Owner: [SME + L&D]**

Identify the logical next step: next session, next topic, practice assignment, certification or deeper learning.

**What's next:**

Session 05, Checkpoints, recovery and human approval (90 min): a run that survives a crash without duplicating its effects, and an exact-action approval that persists. Bring your Session 04 checkpoint.

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

• Video 1 (5 min): why one good run proves nothing; cases, trials, splits and the dataset identity.

• Video 2 (5 min): three grades and the plausible-but-wrong answer.

• Video 3 (4 min): repeated trials, per-trial rows and a baseline you can compare against.

• Video 4 (5 min): calibrating a model judge against human labels.

• Knowledge check (7.4) and the self-paced assignment (7.5).

Source material: the Session 04 page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-04/) and instructor guide 04.

### 7.3 Examples / Use Cases

**Owner: [SME]**

Provide examples that can stand on their own in e-learning. Include enough context for someone who was not at the live session.

**Your input:**

**Example 1: the missing incident.** Case INC-404 does not exist for Astro, so the expected result is status insufficient_evidence with cause unknown. An agent that searches runbooks and answers 'connection_pool_exhaustion' from the most common runbook sounds plausible and fails the outcome check: a generic runbook is not proof of this incident's cause.

**Example 2: a policy violation in a correct answer.** A run reaches the right cause for INC-001 but called mock_remediate along the way. Outcome and evidence pass; tool policy fails, so the run fails. One blended score would have hidden that the agent changed a system during an investigation.

**Example 3: two reports that are not comparable.** A report from last week shows 80% success; today's shows 100%. The dataset hashes differ: a case was edited. The improvement belongs to the dataset, not the agent; rerun both on the same cases and split before claiming anything.

### 7.4 Knowledge Check

**Owner: [SME]**

Provide 3–5 questions testing the most important concepts. Include question, options if applicable, correct answer and explanation. L&D adapts them into the final interaction.

**Your input:**

**Q1. When should a case's expected outcome be written?** A) after the first run, from what the agent did  B) before any run  C) whenever the agent fails it. Correct: B. Written afterwards, the case only records what the agent happens to do.

**Q2. An answer names the right cause and cites sources, but the run called mock_remediate. Does it pass?** A) yes, the outcome is right  B) no, the tool-policy check fails  C) only if a judge agrees. Correct: B. Each check must pass on its own.

**Q3. Two reports have different success rates and different dataset hashes. What can you conclude?** A) the agent improved  B) nothing yet about the agent: they evaluated different cases  C) the judge drifted. Correct: B. Compare only with the same dataset hash and split.

**Q4. Why keep every per-trial row when the report already has means?** A) to save memory  B) means hide a case that fails sometimes, outliers and variation  C) the tests require it only. Correct: B.

**Q5. The judge disagrees with a human label. What first?** A) change the agent until the judge agrees  B) review the case, the label and the rubric  C) drop the case. Correct: B. A judge is a measuring tool that needs checking.

### 7.5 Practice / Assignment

**Owner: [SME]**

Create a task that can be completed without attending the live session. Include task, context, expected output, estimated time, success criteria and resources.

**Your input:**

**Task:** Using your own coding agent and the learner kit in the course repository, build the Session 04 checkpoint: the five cases, three separate grades, repeated trials with per-trial rows and a dataset identity, and judge calibration.

**Context:** Start from your Session 03 checkpoint. Run the prompts on the Session 04 page in order (Prepare, Add the check pack, Build steps 1–4, the exercise, Verify and push, Review); the same prompts are in LEARNER_PROMPTS.md (Lesson 04). The Lesson 04 check pack also gives a fixed console file, so the Runs view keeps INC-002 and INC-003 selected. No model key is needed.

**Expected output:** your repository in the course GitLab group with the Lesson 04 check pack passing unchanged (19 tests), LESSON = 4, and the lab report: dataset hash 7d345084…, success rate 1.0 on the mock, mean 75 tokens and 3 steps, and a calibration result that flags one disagreement for review.

**Estimated time:** 3 hours.

**Success criteria:** two held-out cases with two trials produce four rows; a plausible but wrong cause is rejected; missing or ambiguous evidence is never reported as a supported diagnosis; reports identify the dataset and keep per-trial results; judge calibration names the mismatching labels.

**Resources:** the Session 04 page, learner-kit/lessons/04 in the course repository, LEARNER_PROMPTS.md (Lesson 04), and the 7.7 reading.

### 7.6 Lesson Reflection

**Owner: [SME]**

Provide reflection questions for independent learners. These may be the same as or adapted from the live session.

**Your input:**

Use the three live-session questions (6.2), plus: 'Which number in your baseline would you watch first after changing the model, and which case would you check by hand?'

### 7.7 Deep Dive / Additional Resources

**Owner: [SME]**

Provide articles, videos, books, documentation, research, internal resources, tools, tutorials or examples. Distinguish Recommended / Essential from Optional / Deep Dive.

**Your input:**

**Essential:** Demystifying evals for AI agents (Anthropic): https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

**Essential:** Writing effective tools for agents, including evaluating them (Anthropic): https://www.anthropic.com/engineering/writing-tools-for-agents

**Optional / deep dive:** the course's record of real-model tests, inference-candidates.md in the course repository: repeated live trials of the course model and how they varied.

**Optional / deep dive:** one finished implementation, the course reference at tag lesson-04 (agent_runtime/evaluate.py) and TESTING.md; read it after building your own.

### 7.8 What's Next

**Owner: [L&D + SME]**

Define the next topic, recommended learning path, practice or next action.

**Your input:**

Next: Session 05, Checkpoints, recovery and human approval. Recommended path: complete the 7.5 assignment first; Session 05 starts from the Session 04 checkpoint, and its changes are measured with this harness.

## 8. Materials & Assets

**Owner: [SME]**

Indicate which assets are needed and provide them where applicable.
- Presentation**✔ the Session 04 page (https://maxvpavlov.github.io/ciklum-innovate-l3-2026/lesson-04/), with Read and Present views, an Instructor view (?instructor) and the prompts-only page**
- Speaker notes**✔ SAY sections of instructor guide 04, also shown in the page's Instructor view**
- Script**✔ instructor guide 04 (complete)**
- Examples**✔ three worked examples in 7.3**
- Case study**✔ the Session 03 INC-003 live answer (activity 4)**
- Demo**✔ the learner kit (learner-kit/lessons/04 in the course repository); the reference tags lesson-03 → lesson-04**
- Screenshots
- Diagrams**✔ the harness (cases → trials → grades → report) and the three grades, on the Session 04 page**
- Templates**✔ the baseline report format (dataset hash, provider, split, trials, rates and per-trial rows)**
- Sample files**✔ the five given evaluation cases (CASES) and the evaluation mock provider, in learner-kit/lessons/04/given, plus the fixed console app.js**
- Quiz questions**✔ five questions in 7.4**
- Practice assignment**✔ 7.5 and LEARNER_PROMPTS.md, Lesson 04**
- Additional resources**✔ 7.7**
- Other:

## 9. Content Accuracy & SME Notes

### 9.1 Important Terminology

**Owner: [SME]**

List terminology that must be used consistently.

**Your input:**

• Case: one incident with its expected outcome (tenant, incident, cause, sufficient or not), written before any run.

• Trial: one run of one case, with a fresh executor and context.

• Split: development cases are for building and tuning; held-out cases only check, and are never tuned against.

• Dataset hash (dataset_sha256): the identity of the case list; reports with different hashes are not comparable.

• Outcome check: the right status and cause (insufficient_evidence and unknown when the evidence names no cause).

• Evidence check: a known cause must be backed by cited sources.

• Tool-policy check: no remediation call during an investigation.

• Baseline: the recorded single-agent result later changes are compared against.

• Model judge: a model that grades answers; optional, and only after calibration.

• Calibration (judge_agreement): paired human and judge labels give an agreement rate and the indices to review.

• Success rate: the share of trials that passed all three checks.

• Fixture tokens: the mock's teaching measurement (20 per tool call, 35 per answer), not tokenizer counts or cost.

### 9.2 Common Misconceptions

**Owner: [SME]**

List frequent misunderstandings. This will inform explanations, examples, knowledge checks and FAQs.

**Your input:**

• 'It worked when I tried it.' One run proves nothing; repeated trials on fixed cases do.

• 'Fix the expected tool calls.' Valid agents take different paths; fix outcomes and policy.

• 'A cited answer is correct.' Citation proves the sources were read, not that they support the cause.

• 'The success rate went up, so the agent improved.' Check the dataset hash and split first.

• 'Edit the held-out case that fails.' Then it no longer measures anything.

• 'A judge can replace the checks.' It is another fallible model; calibrate it and keep deterministic checks.

### 9.3 Important Nuances

**Owner: [SME]**

Document exceptions, limitations, risks, assumptions or cases where the recommended approach does not apply.

**Your input:**

• The mock is deterministic, so every offline trial is identical; repeated trials show their value with a real model, where results vary.

• The offline provider was corrected in this checkpoint so a generic runbook no longer becomes a diagnosis when the log names no cause: a regression example, not a claim that a live model improved.

• Cost is reported only when pricing rates are configured; it stays unavailable rather than being shown as free.

• The calibration example uses a handful of labels to show the method; it cannot establish a judge's reliability for real workloads.

• Elapsed times vary with the machine; dataset hash, rates and means on the mock do not.

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
