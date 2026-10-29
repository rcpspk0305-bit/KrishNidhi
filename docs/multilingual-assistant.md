# Languages and floating assistant

Scope: English, Telugu, and Hindi across the existing web application. Keep the current design and routes. Persist only language preference in the browser; keep chat messages in memory. Localized interface copy comes from a shared catalog, not a paid translation request on every render. Use the selected language for new assistant replies.

The floating assistant answers questions through `POST /api/v1/assistant/chat` (also `/api/assistant/chat`). Its suggested questions focus on the dashboard, offline devices, and plant care. Input: bounded `message`, `language` (`en`, `te`, `hi`), and up to twelve user/assistant history entries. The server uses `OPENROUTER_API_KEY` and optional `OPENROUTER_MODEL` (default `openrouter/free`). It does not browse or invoke hardware tools. Missing configuration, provider errors, and timeouts produce a localized 503 response, never a fabricated AI answer.

Cost admission defaults to six requests per client per minute and 200 total attempts per UTC day, controlled by `ASSISTANT_REQUESTS_PER_MINUTE` and `ASSISTANT_DAILY_REQUEST_LIMIT`. Limits return localized HTTP 429 with `Retry-After`. Failed attempts consume admission so repeated provider failures cannot cause unlimited retries. The personal single-process deployment keeps these counters in memory; they reset on restart. Multi-worker/public deployments need shared durable quota storage or a gateway enforcing the same limits.

The integration follows [OpenRouter's chat-completions API](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion), using asynchronous HTTP, server-only Bearer authentication, system instructions, and bounded output. The [free router](https://openrouter.ai/openrouter/free) chooses among available free models; capacity and language quality vary. The existing agronomy-specific Gemini chatbot and Streamlit APIs are retained.

## Run locally

In `backend/.env`, set `OPENROUTER_API_KEY` to your OpenRouter key and optionally set `OPENROUTER_MODEL=openrouter/free`. Never put the key in a `NEXT_PUBLIC_*` variable. Install `backend/requirements.txt`, then restart the backend: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` from `backend/`. From the same directory, `python -m scripts.check_assistant` performs a small live readiness request and prints only sanitized diagnostics on failure.

Verification covers catalog completeness, persistence/locale behavior, request validation, history forwarding, chosen output language, unavailable states, and desktop/mobile widget interactions. Provider-generated language quality requires a configured, reachable model; mocked provider tests are not evidence of live inference.

Verified locally on 2026-10-29: 24 backend assistant/analytics tests and six frontend state/catalog tests passed. Scoped ESLint passed. A real OpenRouter free-router request returned a plant-care answer in English. The initial 30-second request timed out; the server now allows at most 55 seconds, with a 60-second widget timeout. Live Telugu/Hindi generation quality has not been independently reviewed.
