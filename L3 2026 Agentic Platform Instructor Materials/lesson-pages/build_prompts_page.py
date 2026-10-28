"""Build a prompts-only page for a session: every prompt in order, with what it does for the build.

    python3 build_prompts_page.py 1

Writes lesson-pages/NN-just-prompts.html and docs/lesson-NN-just-prompts/index.html. The styles and
script come from the session's full page, and the prompts are copied verbatim from LEARNER_PROMPTS.md,
so rerun this whenever either changes. The explanations below are the only text written here.
"""
import html
import re
import sys
from pathlib import Path

from publish import wrap

HERE = Path(__file__).resolve().parent
MATERIALS = HERE.parent
REPO = MATERIALS.parent
PROMPTS = MATERIALS / "incident-platform" / "LEARNER_PROMPTS.md"
SITE = "https://maxvpavlov.github.io/ciklum-innovate-l3-2026"
COURSE = "https://github.com/maxvpavlov/ciklum-innovate-l3-2026"

# Per session: the full page it borrows its look from, and what each prompt does for the build.
# Each step is (prompt heading, short title, files, what it does, expected result).
SESSIONS = {
    1: {
        "full_page": "01-agent-runtime.html",
        "title": "The ReAct runtime",
        "goal": "By the end you have the agent runtime every later agent runs on: a bounded "
                "reason-act-observe loop that answers INC-001 with cited evidence and stops every "
                "run with a named reason. Run the prompts in this order, in your coding agent "
                "started in ~/agentic-course, and read each result before you paste the next one.",
        "facts": ["<b>9 prompts</b> in order", "ends at <b>7 passed</b> · <code>LESSON = 1</code>",
                  "offline mock model · no API keys"],
        "outcomes": [("A bounded loop", "the model proposes, the runtime checks and executes, the tool observes."),
                     ("Cited answers", "INC-001 ends in a cause with the log and runbook it came from."),
                     ("Named stops", "step_budget, token_budget, TimeoutError, repeated_action.")],
        "steps": [
            ("Prepare the workspace", "Set up your project", "lesson-00 · once per course",
             "Creates the course folder, a read-only copy of the course repository with its learner kit, "
             "and your own project from the kit's starter, then signs you in to gitlab.ciklum.net and pushes "
             "the project to a private repository named after your Ciklum acronym. Everything later is built "
             "in this project.",
             "<b>1 passed</b>, <code>LESSON = 0</code>, and <code>agentic-platform-&lt;your acronym&gt;</code> "
             "in your group on gitlab.ciklum.net."),
            ("Add the check pack", "Add the check pack", "given files and checks · no code yet",
             "Copies the given synthetic Astro data and the seven checks into your project (the given mock model "
             "is pasted in at step 2), then lists the exact interfaces the checks expect. This defines done "
             "before anything is built.",
             "The new test file fails to import, because the runtime does not exist yet."),
            ("Build step 1", "The run contract", "new · incident/core.py",
             "Defines Context, Limits, Reply and Run: who the run is for and what it may use (set by the "
             "platform), how far it may go, the shape of a model's reply, and the state of a run. Nothing the "
             "model sends can change the first two.",
             "A short contract script shows the fields and defaults. No lesson test can run yet."),
            ("Build step 2", "Model adapters", "new · incident/providers.py",
             "Adds the given mock model and adapters for OpenAI-compatible and Anthropic APIs, all returning "
             "one Reply shape, so the loop never depends on which model answers. Keys come only from the "
             "environment.",
             "Both request shapes checked against mock HTTP; the check pack's adapter tests run after step 3."),
            ("Build step 3", "The loop", "incident/core.py · run_agent",
             "Builds the reason-act-observe loop: each proposed tool call is recorded before it runs, each "
             "result goes back tagged with its call ID, and the final answer must cite only sources a tool "
             "returned. Adds the first guard, the step limit.",
             "The happy path, the step limit and both adapter checks pass: <b>5 of 7</b>."),
            ("Build step 4", "The guards", "incident/core.py · token, time, repeat",
             "Adds the token budget (checked before each model call), one deadline for the whole run, and the "
             "repeated-action guard, so every run ends in an answer or a named stop. Then triggers each one "
             "on purpose.",
             "<b>7 passed</b>; INC-001 answers <b>connection_pool_exhaustion</b> citing log-astro-001 and rb-pool-v1."),
            ("Learner exercise", "Break it on purpose", "a throwaway script",
             "Changes one limit at a time, predicts the failure, then runs it: one step, a tiny token budget, "
             "a short deadline with a slow mock. You see each guard stop a run for its own reason, then "
             "restore the normal limits.",
             "step_budget, token_budget and TimeoutError as predicted; the cited answer returns afterwards."),
            ("Verify the checkpoint", "Verify and push", "LESSON = 1 · commit · push",
             "Runs the full suite and the Session 01 demo unchanged, raises the checkpoint to 1 only if the "
             "capability is there, and pushes your work. This is the evidence, not the agent's summary.",
             "<b>7 passed</b>, <code>LESSON = 1</code>, and your work on gitlab.ciklum.net."),
            ("Review the result", "Review", "no changes",
             "Walks through what you built against the completion criteria and points out the design choices "
             "the checks do not force, such as how your loop enforces its deadline, and what each costs or gains.",
             "A review you can discuss in the next session."),
        ],
        "recover": [
            ("Recover when live mode fails before a request", "Only if you switched to a real model and it fails at once."),
            ("Recover when the final message cannot be parsed", "When the run fails because the last answer is not the expected JSON."),
            ("Recover when the lesson command says the checkpoint is too early", "When the demo refuses to run because LESSON is still 0."),
            ("Recover when a native python package cannot load on macos", "When Python fails before any course code runs, on a Mac."),
        ],
        "next": "Session 02: Reliable tools and MCP integration",
    },
    2: {
        "full_page": "02-tools-and-mcp.html",
        "fold": True,
        "title": "Reliable tools and MCP",
        "goal": "By the end your project has its lasting layout, a running platform with a console, and a "
                "tool boundary every call passes through: checked before dispatch, approved per exact action, "
                "written once, and reached over a real MCP connection. Run the prompts in this order, in your "
                "coding agent started in ~/agentic-course, and read each result before you paste the next one.",
        "facts": ["<b>10 prompts</b> in order", "ends at <b>12 passed</b> · <code>LESSON = 2</code>",
                  "offline mock model · real MCP over stdio"],
        "outcomes": [("A visible platform", "your Session 01 agent runs INC-001 from the console before you build anything."),
                     ("A tool boundary", "known tool, granted to this run, valid arguments, before any handler runs."),
                     ("Exact approval, one effect", "an approval covers one action, and a repeated write happens once."),
                     ("Real MCP", "the read tools travel over stdio, and the boundary does not move.")],
        "steps": [
            ("Prepare the workspace", "Prepare", "confirms lesson-01 · refreshes the course copy",
             "Opens your project, confirms your Session 01 work still passes, and updates your read-only copy "
             "of the course repository, because the kit has changed since Session 01. Your project is not changed.",
             "the course copy moved to the latest commit, with the Lesson 02 kit files that changed; "
             "<code>learner-kit/lessons/02/README.md</code> opens with \"First: move to the course layout and start "
             "the platform\". Your project still at <code>LESSON = 1</code>, <b>7 passed</b>."),
            ("Move to the course layout and start the platform", "Move and start the platform",
             "incident/ → agent_runtime/ and course/ · new agentic_platform/",
             "Moves your runtime into <code>agent_runtime/</code> and the course scaffolding into <code>course/</code>, "
             "copies the given platform shell from the kit into <code>agentic_platform/</code> (each as its own commit), "
             "adds AGENTS.md, the briefing your coding agent reads at the start of every later session, and starts "
             "the platform. Sign in as demo-astro, submit INC-001 in Runs, and open Tools.",
             "still <b>7 passed</b>; the console shows checkpoint lesson-01, INC-001 answered with cited evidence, and "
             "a Tools view saying the tool boundary is not built yet."),
            ("Add the check pack", "Add the check pack", "checks · no code yet",
             "Copies the Session 02 checks into your project and lists the exact interfaces they expect, including "
             "what the given platform needs from your executor. This defines done before anything is built.",
             "<code>test_lesson02.py</code> fails to import, because the tool boundary does not exist yet."),
            ("Build step 1", "Validate before dispatch", "new · agent_runtime/tools.py",
             "Builds ToolExecutor: an unknown tool, a tool the run was not granted, and malformed or extra "
             "arguments are refused before any handler runs, with errors that say whether a retry can help.",
             "rejections shown in a demonstration; Session 01 tests still <b>7 passed</b> (the new test file "
             "imports from step 2)."),
            ("Build step 2", "Exact approval, one effect", "agent_runtime/tools.py · approval and ledger",
             "Adds the mock_remediate write tool, an approval bound to tenant, run, tool and arguments, and a "
             "SQLite ledger that records the effect once, so a repeated approved write is replayed, not redone.",
             "replayed false, then true after reopening; one effect stored; <b>11 passed, 1 failed</b> (the MCP check)."),
            ("Build step 3", "The MCP server", "new · agent_runtime/mcp_bridge.py",
             "Puts the two read tools and the runbook resource behind a real MCP server, with the tenant fixed "
             "by the launcher and stdout kept for the protocol.",
             "discovery lists log_lookup, runbook_search and the runbook resource; still <b>11 passed, 1 failed</b>."),
            ("Build step 4", "Reads over MCP", "agent_runtime/mcp_bridge.py · client and adapter",
             "Connects the stdio client behind the executor and runs the same investigation through it. "
             "Discovery grants nothing: the executor still decides, and a lost connection comes back as tool_unavailable.",
             "protocol 2026-07-28, the same cited answer as Session 01, and <b>12 passed</b>."),
            ("Learner exercise", "Break it on purpose", "a throwaway script and the console",
             "Predicts, then runs: a tenant argument, a write from a read-only run, a tiny output limit and an "
             "approved write repeated after reopening. Then repeats the denied and approval cases in the "
             "console's Tools view as demo-astro and demo-operator.",
             "invalid_arguments, permission_denied, output_too_large, replayed true, and approval_required with a key."),
            ("Verify the checkpoint", "Verify and push", "LESSON = 2 · commit · push",
             "Runs the full suite and the Session 02 demo unchanged, raises the checkpoint to 2 only if the "
             "capability is there, and pushes your work. This is the evidence, not the agent's summary.",
             "<b>12 passed</b>, <code>LESSON = 2</code>, a Lesson 02 entry in <code>AGENTS.md</code>, and your work on gitlab.ciklum.net."),
            ("Review the result", "Review", "no changes",
             "Walks through what you built against the completion criteria and points out the design choices "
             "the checks do not force, such as what your adapter trusts about the tenant.",
             "A review you can discuss in the next session."),
        ],
        "recover": [
            ("Recover when mcp startup or parsing fails", "When the MCP server will not start or its replies cannot be read."),
            ("Recover when result-field attribute error", "When code reading an MCP result fails on a missing field."),
            ("Recover when tool exists but returns permission_denied", "When a tool you expect to work is refused for this run."),
            ("Recover when a changed schema breaks an integration", "When a tool's contract changed and a caller now fails."),
        ],
        "next": "Session 03: Context, retrieval and memory",
    },
}


def prompts_for(n):
    text = PROMPTS.read_text(encoding="utf-8")
    section = re.split(rf"^## {n:02d}\. .*$", text, flags=re.M)[1]
    section = re.split(r"^## \d\d\. ", section, flags=re.M)[0]
    return {m.group(1).strip(): m.group(2).strip()
            for m in re.finditer(r"^### (.+?)\n\n> (.+?)$", section, re.M)}


def band(pid, label, files, goal, prompt, expect=None, fold=False):
    block = f'<div class="prompt" id="{pid}-text"><span class="pfx">PROMPT ▸ </span>{html.escape(prompt, quote=False)}</div>'
    if fold:  # collapsed by default, with the expected result; the copy button outside still copies the prompt
        if expect:
            block += f'<div class="expect"><span class="pfx">EXPECT ▸ </span>{expect}</div>'
            expect = None
        block = ('<details class="fold"><summary><span class="show">Show prompt</span>'
                 f'<span class="hide">Hide prompt</span></summary>{block}</details>')
    parts = [f'  <div class="terminal" id="{pid}">',
             f'    <div class="bar"><span class="switch">{label}</span><span class="file">{files}</span></div>',
             '    <div class="body">',
             f'      <p class="goal">{goal}</p>',
             f'      {block}',
             f'      <div><button class="copy" type="button" data-copy="{pid}-text">Copy prompt</button></div>']
    if expect:
        parts.append(f'      <p class="check">Expect: {expect}</p>')
    parts += ['    </div>', '  </div>']
    return "\n".join(parts)


def build(n):
    cfg, nn = SESSIONS[n], f"{n:02d}"
    prompts = prompts_for(n)
    full = (HERE / cfg["full_page"]).read_text(encoding="utf-8")
    head = full.split("</style>", 1)[0] + "</style>"
    head = re.sub(r"<title>.*?</title>", f"<title>Session {nn} Prompts</title>", head, count=1)
    script = "<script>" + full.split("<script>", 1)[1]
    brand = re.search(r'<svg class="brand".*?</svg>', full, re.S).group(0)  # the Ciklum logo, inline

    route = []
    for i, step in enumerate(cfg["steps"]):
        route.append(f'<a href="#s{i}">{step[1]}</a>')
    bands = []
    for i, (heading, title, files, goal, expect) in enumerate(cfg["steps"]):
        label = f"Prompt {i + 1} of {len(cfg['steps'])} · {title}"
        bands.append(band(f"s{i}", label, files, goal, prompts[heading], expect, cfg.get("fold", False)))
    recover = []
    for j, (heading, when) in enumerate(cfg["recover"]):
        symptom = re.search(r"The symptom is: (.+?)\. Diagnostic", prompts[heading])
        title = symptom.group(1) if symptom else heading.removeprefix("Recover when ").capitalize()
        recover.append(band(f"r{j}", f"Recover · {html.escape(title)}", "only when you hit it", when, prompts[heading],
                            fold=cfg.get("fold", False)))
    used = {s[0] for s in cfg["steps"]} | {r[0] for r in cfg["recover"]}
    missing = set(prompts) - used
    assert not missing, f"prompts not on the page: {missing}"

    outcomes = "\n".join(f"      <div><b>{t}</b>{d}</div>" for t, d in cfg["outcomes"])
    facts = "".join(f"<span>{f}</span>" for f in cfg["facts"])
    body = f"""
<div class="view" role="group" aria-label="View">
  <button type="button" data-view="read" aria-pressed="true">Read</button>
  <button type="button" data-view="present" aria-pressed="false">Present</button>
</div>

<main>

<header class="hero" id="start">
  <p class="course">{brand}<span aria-hidden="true">·</span><span>Innovate</span><span aria-hidden="true">·</span><span>2026</span><span aria-hidden="true">·</span><span>Session {nn} of 12 · just the prompts</span></p>
  <h1>{cfg["title"]}<span class="sub">Every prompt for this session, in order, with what each one adds to your platform</span></h1>
  <p class="lede">{cfg["goal"]}</p>
  <div class="facts">{facts}</div>
</header>

<section class="ch" id="goal">
  <p class="eyebrow"><span>The build goal</span></p>
  <h2>What these prompts build</h2>
  <div class="stack">
    <div class="criteria">
{outcomes}
    </div>
    <nav class="route" id="route" aria-label="Prompt route">
      {'<span class="arr" aria-hidden="true">→</span>'.join(route)}
    </nav>
    <p class="muted">A coding agent saying "done" is not evidence: after each prompt, look at the change and at the check output before you paste the next one. The explanations, diagrams and code are on the <a href="{SITE}/lesson-{nn}/">full Session {nn} page</a>.</p>
  </div>
</section>

<section class="ch" id="prompts">
  <p class="eyebrow"><span>The prompts</span></p>
  <h2>Paste them in this order</h2>
{chr(10).join(bands)}
</section>

<section class="ch" id="recover">
  <p class="eyebrow"><span>When something breaks</span></p>
  <h2>Recovery prompts</h2>
  <p class="lede">Use one only when you see its symptom. Each asks your agent to reproduce the problem, make the smallest fix and rerun the checks.</p>
{chr(10).join(recover)}
</section>

<footer>
  <p>Full session page: <a href="{SITE}/lesson-{nn}/">{SITE.removeprefix("https://")}/lesson-{nn}/</a> · kit: <code>learner-kit/lessons/{nn}</code> · all prompts: <a href="{COURSE}/blob/main/L3%202026%20Agentic%20Platform%20Instructor%20Materials/incident-platform/LEARNER_PROMPTS.md">LEARNER_PROMPTS.md</a></p>
  <p>Next: {cfg["next"]}.</p>
</footer>
</main>
"""
    page = head + "\n" + body + "\n" + script
    (HERE / f"{nn}-just-prompts.html").write_text(page, encoding="utf-8")
    out = REPO / "docs" / f"lesson-{nn}-just-prompts" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(wrap(page), encoding="utf-8")
    print(f"wrote {nn}-just-prompts.html and {out.relative_to(REPO)}")


if __name__ == "__main__":
    for arg in sys.argv[1:] or ["1"]:
        build(int(arg))
