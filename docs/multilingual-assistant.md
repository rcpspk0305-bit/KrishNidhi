# Languages and floating assistant

Scope: English, Telugu, and Hindi across the existing web application. Keep the current design and routes. Persist only language preference in the browser; keep chat messages in memory. Localized interface copy comes from a shared catalog, not a paid translation request on every render. Use the selected language for new assistant replies.

The floating assistant answers general questions through `POST /api/v1/assistant/chat` (also `/api/assistant/chat`). Input: bounded `message`, `language` (`en`, `te`, `hi`), and up to twelve user/assistant history entries. The server uses `GEMINI_API_KEY` and optional `GEMINI_CHAT_MODEL` (default `gemini-flash-latest`). It does not browse or invoke hardware tools. Missing configuration, provider errors, and timeouts produce a localized 503 response, never a fabricated AI answer.

Cost admission defaults to six requests per client per minute and 200 total attempts per UTC day, controlled by `ASSISTANT_REQUESTS_PER_MINUTE` and `ASSISTANT_DAILY_REQUEST_LIMIT`. Limits return localized HTTP 429 with `Retry-After`. Failed attempts consume admission so repeated provider failures cannot cause unlimited retries. The personal single-process deployment keeps these counters in memory; they reset on restart. Multi-worker/public deployments need shared durable quota storage or a gateway enforcing the same limits.

SDK integration follows https://googleapis.github.io/python-genai/ (async generate_content, system instructions, bounded output). The existing agronomy-specific chatbot and Streamlit APIs are retained.

Verification covers catalog completeness, persistence/locale behavior, request validation, history forwarding, chosen output language, unavailable states, and desktop/mobile widget interactions. Provider-generated language quality requires a configured, reachable model; mocked provider tests are not evidence of live inference.
