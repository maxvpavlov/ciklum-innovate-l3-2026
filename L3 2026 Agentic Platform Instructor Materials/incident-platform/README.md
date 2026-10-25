# Incident platform course

A Python reference implementation for the 12-session agentic platform course.
Participants guide their own coding agents to prepare, extend and verify a
learner project. The coding agent handles repository operations, dependency
setup, command execution and tests. Participants define the scope, inspect the
changes and explain the evidence.

The coding agent used for development is separate from the incident-investigation
agents that the project implements. The default investigation provider is an
offline deterministic fixture, so the course can run without paid model access.

The finished platform has four platform components around the agent runtime, and
learners build each of them:

- an **agent registry** of immutable, versioned agent definitions, pinned remote
  A2A agents and tool-server manifests (Session 08);
- an **MCP tool gateway**, the single policy, audit and connection point for every
  agent tool call, with shared upstream sessions and pinned tool definitions (Session 09);
- **agent identity and credentials**: signed short-lived tokens, delegation chains from
  user to agent to worker or remote agent, and a credential store (Session 10);
- a **platform console** at `/console` that visualizes what has been built: the
  platform map, runs and traces, tool checks, registry, approvals, gateway audit,
  identity and operations. From Session 02 the kit gives a first console with its run
  API (runs and a Tools view); learners extend it from Session 08, and every later
  session adds a view.

## How learners work

Each learner builds the platform in their own repository in the course GitLab group, by
prompting a coding agent. The `learner-kit/` folder at the root of the public course repository
(https://github.com/maxvpavlov/ciklum-innovate-l3-2026) supplies the starter project
(`lesson-00`) and, for every lesson, the given files
(synthetic data and deterministic test doubles such as the mock model) and a check pack
(the lesson's demo and the cumulative tests). The kit is generated from these tags by
`guide-builder/kit.py`, which also verifies each check pack against its tag.

The first prompt creates the learner's project and repository:

> Set up my project for the Building Agentic Platforms course, starting at lesson-00. Clone the public course repository from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 into ~/agentic-course/course and treat that folder as read-only; its learner-kit folder is the course kit. Create my own project in ~/agentic-course/my-platform by copying learner-kit/starter, and make it a fresh Git repository on branch main with one initial commit; if Git has no user name or email, set them for this repository only and tell me. Install the pinned dependencies with uv for Python 3.12, run the tests with python -m pytest, and confirm that course/__init__.py says LESSON = 0. Explain the project layout: agent_runtime/ is where I build the agent runtime, course/ holds the course scaffolding (the LESSON marker, the lab runner and given data), tests/ holds the checks, and agentic_platform/ arrives with the platform shell in Lesson 02. Install the GitLab CLI, glab, if it is missing, and sign me in to the course GitLab at gitlab.ciklum.net. glab may already be signed in to other GitLab hosts, such as gitlab.com: keep those sign-ins, add gitlab.ciklum.net alongside them, and name gitlab.ciklum.net as the host in every glab command, because glab otherwise uses a default host. When a browser sign-in is needed, tell me what to do, and never ask me to paste a token into the chat. Ask me for the name of the group I was invited to on gitlab.ciklum.net. Every learner shares that group, so name my repository agentic-platform- followed by my Ciklum acronym: read my account through my glab sign-in on gitlab.ciklum.net and take the part of my @ciklum.com email before the @, in lowercase (abcd for abcd@ciklum.com gives agentic-platform-abcd); if the account shows no @ciklum.com email, ask me for my acronym. if a project with that name already exists in the group, stop and ask me instead of pushing to it. Create it as a private repository in that group, set it as the origin remote and push my project to it. Report both folder paths, the files in my project, the test result, the GitLab repository address and anything missing, such as uv, Python 3.12, glab or access to the group on gitlab.ciklum.net. Do not ask me to run terminal commands.

Continue with the lesson-specific prompts in [LEARNER_PROMPTS.md](LEARNER_PROMPTS.md).
They cover preparation, adding the check pack, incremental implementation, verification,
review and targeted recovery for every lesson.

## Instructor materials

The destination for the twelve Google Docs is the
[instructor materials folder](https://drive.google.com/drive/u/0/folders/1wos8PjyC0mTDQxrcZ89b9mG0yYV57Zr3).
Native publication is pending browser upload access or a connected Drive
connector. The prepared .docx guides are in the course repository's `instructor-guides`
folder and are generated from specs by its `guide-builder`.

Each guide contains instructor narration, copyable coding-agent prompts,
reference Python excerpts, expected results, review questions and troubleshooting.
The Python excerpts support code review; the agent carries out the implementation.
A completion message alone does not establish that a learner's code works.

## Checkpoint sequence

| End tag | Capability | Minutes |
|---|---|---:|
| lesson-01 | Bounded ReAct runtime and configurable provider adapters | 120 |
| lesson-02 | Tool contracts, approval boundary, idempotent mock effects, real MCP stdio and the platform shell | 120 |
| lesson-03 | Context selection, retrieval, expiring memory and versioned artifacts | 90 |
| lesson-04 | Repeated evaluation, held-out cases and optional judge calibration | 90 |
| lesson-05 | Durable checkpoints, crash recovery and exact-action approval | 90 |
| lesson-06 | Supervisor, scoped subagents, shared budgets, parallel scheduling and bounded review | 120 |
| lesson-07 | Independent A2A specialist, streaming, authentication and cancellation | 90 |
| lesson-08 | Platform core: agent registry, durable run API, registry and approval views | 90 |
| lesson-09 | MCP tool gateway: policy, audit, shared sessions and pinned tool definitions | 90 |
| lesson-10 | Agent identity, delegated credentials, credential store and containment | 90 |
| lesson-11 | Operations: correlated traces, admission control and evaluated releases | 120 |
| lesson-12 | Tuning, before/after comparison and presentation evidence | 90 |

Total: 12 sessions and 20 contact hours. Preparation and practice are additional.
The reference tags preserve the implementation at each lesson. They are the
instructor's answer key and the source of the guide excerpts; learners prove their own
implementation with each lesson's check pack instead.

## Demonstrate the complete platform

Give the coding agent this prompt after Session 11:

> Use my completed platform to demonstrate INC-001 with the team configuration.
> Select the offline provider, start the local platform and the independent A2A
> specialist on loopback using the existing project entry points, and configure
> their connection so the platform registers and pins the specialist's Agent Card.
> Handle process and environment setup yourself without disturbing unrelated
> services. Submit the investigation, wait for its actual outcome and show the
> parent, the gateway-backed worker and the remote specialist. Show the delegation
> chain each of them acted under and the gateway audit entries. Export and open the
> correlated trace, explain the cited evidence and report failures honestly. Stop
> only the temporary services you started when finished.

The normal platform API exposes health, token exchange, registry, run lifecycle,
gateway, identity, operations and authenticated trace operations. The self-contained lab demonstrations provide the same reference
scenarios with automatic local-service cleanup. The coding agent can inspect
the existing entry points to choose how to execute them.

## Open the platform console

> Start my platform locally on loopback with the offline provider and open its
> console. Sign in first as the demo analyst and then as the demo operator, and
> show me what each identity can see and do in the Overview, Registry, Runs, Tools,
> Approvals, Gateway, Identity and Operations views. Submit one single-agent and
> one team investigation from the console, then explain the run timeline, the
> correlated trace, the gateway audit and the delegation chains. Never paste a
> signed token into chat or a file. Stop the services you started when finished.

The console is served by the platform at `/console`. It uses the demo identities
`demo-astro` (analyst), `demo-operator` and `demo-locomotive`, which it exchanges once for a
one-hour signed token. Those demo credentials are for loopback use only. The console
renders every API value as text and runs under a strict Content-Security-Policy,
because model answers and tool evidence are untrusted.
Screenshots of each view are in the course's `console-screenshots` folder.

## Practice approval and recovery

Use this prompt for a manually controlled mock-remediation demonstration:

> Prepare the operator-owned mock-remediation scenario for INC-001 using the
> existing local fixture. Show me the exact proposed action, arguments and
> approval key, and confirm that the run is waiting with no new effect.
> Do not approve the proposal on my behalf. Wait for my explicit approve or deny
> decision, then carry it out and show the resulting run state. For recovery
> testing, run the labelled automated crash fixture separately and demonstrate
> that resume leaves one mock effect. Explain why that local guarantee does not
> automatically apply to external APIs.

No real systems are modified. The remediation configuration uses a scripted
fixture and writes only to the local SQLite effect ledger.

## Configure live model access only when needed

The adapters support tool-capable OpenAI-compatible Chat Completions and
Anthropic Messages. Live services are optional and were not exercised for the
reference verification.

> Help me configure the existing model adapter for a provider and model I am
> authorized to use. Inspect the configuration interface, identify required
> environment values and check credential availability without revealing
> secrets. Keep credentials out of chat, source files and reports. Use the exact
> approved endpoint and preserve TLS and host restrictions. Run a small live
> check only after I explicitly authorize the provider use and its cost; otherwise
> keep the offline provider. Report what was actually tested and any missing
> prerequisite.

For the coding agent's reference, provider selection uses MODEL_PROVIDER,
MODEL_NAME, MODEL_API_KEY and optionally MODEL_BASE_URL and MODEL_ALLOWED_HOSTS.
Pricing uses MODEL_INPUT_USD_PER_MILLION and MODEL_OUTPUT_USD_PER_MILLION.
The project does not automatically load a .env file. Unknown live pricing
remains unavailable in evaluation reports.

## Evaluate and tune the platform

> Preserve my current baseline and evaluate the completed platform on the
> existing development and held-out cases. Retain per-case rows and the dataset
> identity. Apply one bounded tuning change as a new version or isolated patch,
> rerun the same conditions and compare quality, latency and usage. Keep failures
> visible and do not alter the expected outcomes to obtain a pass. Report cold
> and warm caching separately. Explain the adoption decision and prepare the
> evidence for my capstone presentation.

The reference capstone writes a comparison report to var/capstone-comparison.json.
On its deterministic fixtures, the candidate preserves success on five cases
and reduces mean simulated usage from 75 to 63, a 16% reduction. Those fixture
measurements are not a claim about live model quality or actual API savings.

## Verify the restricted container demonstration

> Inspect the repository's existing container recipe and, if this environment
> supports it, build and run the end-to-end offline demonstration in its
> restricted container. Preserve the non-root user, read-only filesystem,
> temporary writable directories, network restrictions and dropped capabilities.
> Show the observed result and explain the storage lifecycle. Do not weaken
> protections to make a failing check pass. If the environment cannot run it,
> report that limitation and continue with the local offline checks.

The Linux ARM64 image and restricted end-to-end demonstration were tested.
The supplied Compose sandbox has temporary writable state, so container
replacement discards that sandbox data. The normal local SQLite file supports
worker recovery. Persistent deployment storage, real identity, secrets and
infrastructure controls require deliberate configuration and validation.

## Verification and limits

See [TESTING.md](TESTING.md) for the reference verification record. Every code
checkpoint was independently unpacked and tested, with 53 tests passing at the
final checkpoint. Actual local MCP stdio, the gateway's shared sessions and
pinned tool definitions, A2A HTTP transport, streaming, delegated-token
authentication and cancellation were exercised, and the console was driven in a
headless browser.

A learner coding agent must still run and report checks against its own output;
these prompts are instructions, not a guarantee of a correct implementation.
Live model accounts, third-party MCP/A2A services, remote OAuth, an enterprise
identity provider, a managed secret vault, production cloud rollout and an
external observability collector were not tested. Tokens are signed with one
shared development key (`PLATFORM_SIGNING_KEY`); a production issuer signs
asymmetrically and publishes verification keys. The credential store keeps values
in process memory and is not a vault. The remote specialist's task store is in
memory, and public demo credentials must not secure an exposed deployment.

The project retains executable CLI tools, lab runners and tests for coding
agents to operate. Learner-facing preparation and walkthrough instructions are
provided as prompts rather than terminal command snippets.
