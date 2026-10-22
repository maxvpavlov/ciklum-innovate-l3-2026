# Candidate model endpoints for real-model runs

Status: **Groq and Google AI Studio (Gemini) partly tested on 22 October 2026 (see the test log); Groq is the current recommendation, with the system-prompt fix below. The others are not tested.** Session 01 and every check pack run on the offline mock model. This page lists
endpoints learners could use later for real-model runs, and the test each one has to pass before the
course recommends it. Researched on 20 October 2026; free tiers, limits and model lists change monthly,
so re-check them before testing.

## How the platform connects to any of them

All candidates speak the OpenAI chat-completions format, which the reference's `HTTPProvider` supports
as `openai-compatible`. The coding agent sets these environment variables (never in the repository or
the chat):

| Variable | Value |
|---|---|
| `MODEL_PROVIDER` | `openai-compatible` |
| `MODEL_BASE_URL` | the provider's base URL from the table below (`/chat/completions` is appended) |
| `MODEL_NAME` | a model ID from the provider's current list |
| `MODEL_API_KEY` | the learner's own key |
| `MODEL_ALLOWED_HOSTS` | the base URL's host name; from lesson 10 the platform refuses any other host |

From lesson 10 the endpoint check also requires HTTPS, except for `http://localhost` and `127.0.0.1`. Usage cost stays 0
unless `MODEL_INPUT_USD_PER_MILLION` and `MODEL_OUTPUT_USD_PER_MILLION` are set: report "no prices
configured", never "free".

## Candidates

| # | Provider | Base URL | Sign-up | Free limits as reported (unverified) | Notes |
|---|---|---|---|---|---|
| 1 | OpenRouter | `https://openrouter.ai/api/v1` | Individual account, free key | About 20 requests/min and 50/day with no credits; a one-off $10 top-up reportedly raises it to 1,000/day | One key, many models. Free models appear and disappear, and tool calling varies per model, so name two or three. Reported tool-capable free options include `qwen/qwen3-coder:free` and MiniMax M3 (free). `openrouter/free` routes to free models only. |
| 2 | Groq | `https://api.groq.com/openai/v1` | Free account; the key starts with `gsk_` | Measured from response headers: 1,000 requests/day and 8,000 tokens/min per model (7,000 input tokens/min on `qwen/qwen3.8-27b`). Tokens per minute bind first: about 3 to 5 investigations a minute | Fast (about 1 s per investigation) and stable. Tool-capable models on the key: `qwen/qwen3.8-27b` and `openai/gpt-oss-20b` passed with the prompt fix; `openai/gpt-oss-120b` did not. |
| 3 | Google AI Studio (Gemini) | `https://generativelanguage.googleapis.com/v1beta/openai` | Google account, no card: the default key on the API keys page works on the free tier. Close the "Link a paid API key" dialog; it is the optional paid upgrade. | Measured: 5 requests/min per model on `gemini-3.6-flash`; daily limit not measured | Free-tier prompts may be used to improve Google's products, except for users in the EEA, Switzerland and the UK. Acceptable only because all course data is synthetic. Pro, image, video and music models need billing. |
| 4 | OpenCode Zen | `https://opencode.ai/zen/v1` | opencode.ai account | Several free models listed, e.g. `deepseek-v4-flash-free`, `qwen3.6-plus-free`, `minimax-m3-free` | Uncertain: one source says access without paying was shut off for non-official clients on 23 September 2026; others mention a deposit or billing details. Live list: `GET /zen/v1/models`. |
| 5 | Local Ollama | `http://localhost:11434/v1` | None | No limits or cost | Works offline; needs a capable laptop. Small local models are often weak at tool calling. Set `MODEL_ALLOWED_HOSTS=localhost`. |

## Test to run for each candidate

The live adapters have only been tested against fake HTTP responses, so the first real run is the test.

1. Get a key and confirm the model list contains the chosen model and that it supports tool calling.
2. With the reference at `lesson-01`, run the INC-001 investigation with the variables above. Pass: the
   run completes, `cause` is `connection_pool_exhaustion`, and the evidence cites `log-astro-001` and
   `rb-pool-v1`.
3. Run INC-003. Pass: status `insufficient_evidence`, no invented cause.
4. Note the number of requests and the reported token usage.
5. Watch for the most likely failure: the final answer must be bare JSON. A model that wraps it in a
   Markdown code fence or adds prose makes `json.loads` fail ("The final message cannot be parsed").
   Record whether it happened and how often across 3 runs.
6. Repeat once at `lesson-10` or later, where the key passes through the credential store and the
   endpoint check is active, to confirm `MODEL_ALLOWED_HOSTS` works for that host.
7. Record the result in the log below. Recommend a provider only after it passes steps 2 to 6.

## Expected request volume

- Session 01 investigation: about 3 requests.
- Session 04 evaluation, 5 cases × 2 trials: about 30 requests.
- Capstone before/after comparison: a few dozen requests.

That fits OpenRouter's 50/day only with few retries, and fits Groq or Gemini comfortably.

## Rules to give learners

- Use a personal key in an environment variable or the platform's credential store; never paste it into
  the chat, a prompt or the repository.
- Send only the course's synthetic data. No work code or client data through personal or free-tier keys.
- Check Ciklum's AI usage policy on personal accounts before the course recommends one.
- Check packs keep running on the mock model: their exact expected outcomes only hold for it.

## Test log

| Date | Provider | Model | Steps passed | Requests | Notes |
|---|---|---|---|---|---|
| 2026-10-22 | Google AI Studio | `gemini-flash-lite-latest` | 1, 2 and 3 only with a fix (see notes); 4 done; 6 not run | about 37 model calls in total across all models | Every final answer (6 of 6) came in a ```` ```json ```` fence, so the unmodified runtime fails with "Expecting value". Adding "Reply with the JSON object only: no Markdown code fence and no other text." to the system prompt fixed it (3 of 3 bare JSON). With the fence stripped, INC-001 completed with the right cause and cited evidence, and INC-003 returned `insufficient_evidence`. With the prompt fix, one INC-003 run instead concluded `connection_pool_exhaustion` from `rb-pool-v1`, which it had really retrieved, so the citation check passed an unsupported cause. Two calls exceeded the 15 s HTTP timeout (`provider_ReadTimeout`); one took 10.4 s. Tool-call IDs were unique, thought signatures (`extra_content`) round-tripped without errors, and parallel tool calls in one turn worked. |
| 2026-10-22 | Google AI Studio | `gemini-3.5-flash` (served as `gemini-3.6-flash`) | 1; 2 failed on the fence | included above | 3 to 4 calls per investigation. Hit 429 after about 5 requests in a minute (free tier: 5 requests/min per model). `usage.total_tokens` exceeds `prompt_tokens + completion_tokens` (1063 vs 684) because of thinking tokens, which `HTTPProvider` does not count, so token budgets and reports undercount. |
| 2026-10-22 | Google AI Studio | `gemini-3.8-flash`, `gemini-flash-latest` | none | 2 | 503 "high demand" on the first call: temporary capacity errors on Google's side. |
| 2026-10-22 | Groq | `qwen/qwen3.8-27b` | 1 to 4 with the prompt fix (4 of 4 runs); 6 not run | about 25 across the three Groq models | Without the fix: 2 of 3 INC-001 answers fenced, one run stopped by our `repeated_action` guard (it looked up INC-001 again), and INC-003 kept searching until the tokens-per-minute limit (429). With the fix ("Give the final answer as your message text, not as a tool call, and reply with the JSON object only: no Markdown code fence and no other text."): INC-001 3 of 3 complete with `log-astro-001` and `rb-pool-v1`; INC-003 `insufficient_evidence`, cause `unknown`. 3 to 4 steps, about 1,800 reported tokens per INC-001 run. |
| 2026-10-22 | Groq | `openai/gpt-oss-20b` | 1 to 4 with the prompt fix (4 of 4 runs) | included above | Without the fix: 1 of 3 INC-001 answers fenced, and INC-003 over-claimed `connection_pool_exhaustion`. With the fix: INC-001 3 of 3 complete (once citing both sources, twice only `log-astro-001`); INC-003 `insufficient_evidence`. 0.7 to 1.5 s per run. |
| 2026-10-22 | Groq | `openai/gpt-oss-120b` | fails | included above | Gives its final answer as a call to a tool named `json` or `JSON`, which Groq rejects with HTTP 400 `tool_use_failed` (our runtime reports `provider_HTTPStatusError`). 4 of 4 runs without the fix, 2 of 4 with it. Do not recommend. |

### What the Groq test means for the course

- Groq is the best candidate so far: no card, fast, and limits that fit the course (1,000 requests a day; the Session 04 evaluation of about 30 requests fits in a few minutes).
- Recommend `qwen/qwen3.8-27b`, with `openai/gpt-oss-20b` as the alternative. Model lists change, so re-check them before each cohort.
- The same system-prompt sentence fixed both answer-format problems seen on real models: Markdown fences and an answer sent as a fake tool call. It belongs in the hardening that real-model use needs, together with named failures for HTTP 400, 429 and 503.
- Groq returns a `reasoning` field and its own tool-call ID format; the provider ignores the first and the runtime handled the second.

### What the Gemini test means for the course

- A free key with no card is enough, and the existing `openai-compatible` adapter needs no code change to reach Gemini.
- Before learners use a real model, the runtime needs the hardening deferred from Session 01: accept the JSON answer inside a Markdown fence, or tell the model not to use one, and turn HTTP 429, 503 and timeouts into named, explained failures instead of `provider_HTTPStatusError` or `provider_ReadTimeout`.
- 5 requests per minute allows about one investigation a minute. The Session 04 evaluation (about 30 requests) needs pacing or retries with the server's `retryDelay`.
- Counting `total_tokens`, not prompt plus completion, would include thinking tokens.
- The INC-003 over-claim is a real-model example for the evaluation session: an observed citation is necessary but not sufficient, so the evaluation must also judge whether the evidence supports the cause.

## Sources

- [OpenCode Zen (Docker docs)](https://docs.docker.com/ai/docker-agent/providers/opencode-zen/)
- [pi-opencode-zen README, free-tier shutdown claim](https://github.com/Feng-H/pi-opencode-zen)
- [ccs issue #114, OpenCode Zen through an OpenAI-compatible profile](https://github.com/kaitranntt/ccs/issues/114)
- [OpenCode Zen API key guide (freeaiapi.org)](https://freeaiapi.org/articles/opencode-api-key-guide)
- [OpenCode Zen free tier (freellm.net)](https://freellm.net/providers/opencode)
- [OpenRouter: free LLM APIs compared](https://openrouter.ai/blog/tutorials/free-llm-apis-compared/)
- [OpenRouter free models 2026 (aitoolsradar)](https://aitoolsradar.org/blog/guides/openrouter-free-models-2026/)
- [OpenRouter free credits limit (aireiter)](https://aireiter.com/blog/openrouter-free-credits-limit)
- [Free LLM API comparison 2026 (Novita)](https://blogs.novita.ai/free-llm-api-comparison-2026/)
- [Best free AI APIs 2026: limits and data policies (aireiter)](https://aireiter.com/blog/best-free-ai-api)
- [Free LLM API tiers (benchlm)](https://benchlm.ai/md/free-tier.md)
