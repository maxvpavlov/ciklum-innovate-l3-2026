# Candidate model endpoints for real-model runs

Status: **not tested.** Session 01 and every check pack run on the offline mock model. This page lists
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
| 2 | Groq | `https://api.groq.com/openai/v1` | Free account | Per model; e.g. about 30/min and 1,000/day for `openai/gpt-oss-120b`, with a tokens-per-minute cap | Fast and comparatively stable. Confirm tool calling for the chosen model. |
| 3 | Google AI Studio (Gemini) | Google's OpenAI-compatible Gemini endpoint (take the URL from Google's docs) | Google account, no card | Generous daily quota; sources disagree on the numbers | Free-tier prompts may be used to improve Google's products. Acceptable only because all course data is synthetic. |
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
| | | | | | |

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
