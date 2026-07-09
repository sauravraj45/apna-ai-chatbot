# APNA AI — Intelligent Shopping Assistant for APNA STORE

A standalone, production-ready **AI chatbot microservice** built with **FastAPI** and **Python 3.12+**, designed to sit alongside your existing APNA STORE stack (React + Vite frontend, Node.js/Express backend, PostgreSQL on Railway) without modifying it.

It answers natural-language questions about a logged-in customer's profile, addresses, and orders, explains store policies (cancellation, refunds, returns, payments), and does all of it **without ever fabricating data** — every user-specific fact comes from a tool call against your real database.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Folder Structure](#folder-structure)
3. [How It Stays Safe & Grounded](#how-it-stays-safe--grounded)
4. [Installation](#installation)
5. [Environment Variables](#environment-variables)
6. [Aligning Models With Your Real Schema](#aligning-models-with-your-real-schema)
7. [Running Locally](#running-locally)
8. [Testing the API](#testing-the-api)
9. [Running Tests](#running-tests)
10. [Deploying to Railway](#deploying-to-railway)
11. [Integrating With Your React Frontend](#integrating-with-your-react-frontend)
12. [Future Expansion](#future-expansion)

---

## Architecture

```
React Frontend  ──(JWT)──►  Node.js/Express  ──►  PostgreSQL (Railway)
       │                                              ▲
       │ (same JWT)                                   │
       ▼                                              │
  FastAPI Chatbot Microservice ────────────────────────┘
       │
       ├─ Middleware: verifies JWT, extracts user_id
       ├─ AI Service: builds prompt, calls LLM, runs tool-calling loop
       ├─ Tools: User / Address / Orders / Order Items / Order Address / FAQ
       │         (each tool queries Postgres scoped to the authenticated user_id)
       ├─ Conversation Memory: per-conversation history (in-memory by default)
       └─ Response Formatter: cleans/sanitizes the final reply
```

**Key principle:** the LLM never touches the database directly. It can only call a small set of well-defined **tools**, each of which independently re-verifies that any data returned belongs to the authenticated user. This is what makes the "never expose another user's data" and "never hallucinate" requirements structurally enforced rather than just prompt-requested.

### Request flow for `POST /chat`

1. `auth_middleware.get_current_user_id` verifies the JWT and extracts `user_id`. Nothing downstream ever trusts a `user_id` from the request body.
2. `AIService.handle_chat_turn` loads conversation history, builds the message list (system prompt + history + new message), and calls the LLM with the tool specs.
3. If the LLM requests a tool (e.g. `get_user_orders`), `tool_registry.dispatch_tool_call` instantiates that tool **with the current session's `db` and `user_id`** and runs it.
4. Tool results (small, typed Pydantic objects — never raw ORM rows) are fed back to the LLM, which either calls another tool or produces the final answer.
5. The reply is sanitized by `ResponseFormatter`, saved to memory, and returned in the standard JSON envelope.

---

## Folder Structure

```
apna-ai-chatbot/
├── app/
│   ├── config/          # Settings (env-driven, singleton)
│   ├── database/        # Async SQLAlchemy engine/session, declarative Base
│   ├── models/          # ORM models mapping to EXISTING tables (users, address, orders, order_items, order_address)
│   ├── schemas/         # Pydantic request/response + tool-result schemas
│   ├── routers/         # FastAPI route handlers (chat, conversation, auth, health)
│   ├── services/        # AIService (orchestration), LLMClient, AuthService, ResponseFormatter
│   ├── tools/           # BaseTool + concrete tools + tool registry + FAQ knowledge base
│   ├── memory/          # Conversation memory abstraction (in-memory now, Redis-ready later)
│   ├── middleware/      # JWT auth dependency, request logging, global error handler
│   ├── prompts/         # System prompt + prompt manager
│   ├── utils/           # Logger, custom exceptions, JWT helpers
│   ├── tests/           # Unit + API tests
│   └── main.py          # FastAPI app factory / entrypoint
├── requirements.txt
├── .env.example
├── Procfile              # Railway start command
├── railway.json          # Railway build/deploy config
└── README.md
```

---

## How It Stays Safe & Grounded

| Requirement | How it's enforced |
|---|---|
| Never expose another user's data | `user_id` comes **only** from the verified JWT (`auth_middleware.py`). Every tool query filters by it, and order-specific tools (`OrderItemsTool`, `OrderAddressTool`) re-verify ownership even when an `order_id` is supplied by the LLM. |
| Never hallucinate user data | The system prompt explicitly forbids it, but more importantly, the LLM has **no other way** to get user data except by calling a tool — there's no raw DB access or freeform SQL available to it. |
| Never reveal internal details | `ResponseFormatter` strips a few implementation terms as a last line of defense; the system prompt instructs the model never to mention databases, tables, APIs, or prompts; the global exception handler never leaks stack traces or raw DB errors. |
| Consistent, safe error responses | `app/utils/exceptions.py` defines a typed exception hierarchy; `app/middleware/error_handler.py` maps every exception to a uniform `{success, error_code, message}` JSON shape. |
| No sensitive data in logs | `app/middleware/logging_middleware.py` logs only method/path/status/duration; `app/utils/logger.py` provides a `redact()` helper for anything sensitive that must be referenced. |

---

## Installation

Requires **Python 3.12+**.

```bash
cd apna-ai-chatbot
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# now edit .env with your real DATABASE_URL, JWT_SECRET, OPENAI_API_KEY, etc.
```

---

## Environment Variables

See `.env.example` for the full list with defaults. The essentials:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Your Railway PostgreSQL connection string (same DB as your Node.js backend). |
| `JWT_SECRET` | **Must exactly match** the secret your Node.js backend uses to sign JWTs. |
| `JWT_USER_ID_CLAIM` | The claim name in your JWT payload holding the user id (default `user_id`). Check what your Node backend actually puts in its tokens and adjust if needed. |
| `OPENAI_API_KEY` / `GEMINI_API_KEY` | API key for whichever `LLM_PROVIDER` you choose. |
| `MODEL_NAME` | e.g. `gpt-4o-mini`, or the Gemini model name if using `LLM_PROVIDER=gemini`. |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins. |

---

## Aligning Models With Your Real Schema

The ORM models in `app/models/` were written from the table/column names implied by your project brief (`users`, `address`, `orders`, `order_items`, `order_address`), since the actual DDL wasn't provided. **Before connecting to your production database**, open each file in `app/models/` and confirm:

- `__tablename__` matches exactly (including case — PostgreSQL is case-sensitive for quoted identifiers).
- Every `mapped_column(...)` name matches your real column names (e.g. your `orders` table might use `order_status` instead of `status`, or `created_at` might be named `placed_at`).
- Foreign key targets (`ForeignKey("users.id")`, etc.) are correct.

Because tools only ever request specific named fields (not `SELECT *`), a mismatched column name will raise a clear SQLAlchemy error at startup/query time rather than silently returning wrong data — so this is a quick, safe check to do once.

---

## Running Locally

```bash
uvicorn app.main:app --reload --port 8000
```

- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Getting a test JWT

Since the real login flow lives in your Node.js backend, use the **local-testing-only** endpoint to mint a token for a given `user_id` that already exists in your `users` table:

```bash
curl -X POST http://localhost:8000/auth/dev-token \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

This endpoint automatically returns `403` if `APP_ENV=production`, so it can never be hit accidentally in production.

---

## Testing the API

```bash
TOKEN="paste-the-access_token-from-above"

curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Track my latest order"}'
```

Follow-up in the same conversation (note the `conversation_id` from the previous response):

```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Cancel it", "conversation_id": "<id-from-previous-response>"}'
```

View history / reset:

```bash
curl "http://localhost:8000/conversation/history?conversation_id=<id>" -H "Authorization: Bearer $TOKEN"
curl -X POST "http://localhost:8000/conversation/reset?conversation_id=<id>" -H "Authorization: Bearer $TOKEN"
```

---

## Running Tests

```bash
pytest
```

Covers:
- JWT verification (valid/invalid/expired/missing claim)
- Tool-level unit tests (ownership scoping, "no data found" behavior, FAQ matching)
- API-level tests (auth enforcement, request validation, response shape) with the LLM call mocked out so tests run offline and deterministically

---

## Deploying to Railway

1. Push this project to its own GitHub repo (kept separate from your main APNA STORE repo, per the brief).
2. In Railway, create a new service from that repo.
3. Set all variables from `.env.example` in Railway's Variables tab — in particular point `DATABASE_URL` at the **same Postgres instance** your Node.js backend uses (Railway lets you reference another service's `DATABASE_URL` variable directly).
4. Railway will detect `railway.json` / `Procfile` and run:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Once deployed, confirm `https://<your-service>.up.railway.app/health` returns `{"status": "ok", ...}`.

---

## Integrating With Your React Frontend

Once you're ready to connect this to your existing app, from React you'd call it like:

```js
const response = await fetch(`${CHATBOT_BASE_URL}/chat`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${jwtFromYourNodeBackend}`,
  },
  body: JSON.stringify({ message: userInput, conversation_id: currentConversationId }),
});
const data = await response.json();
```

Store `data.conversation_id` in your chat widget's state and pass it back on every subsequent message so context (memory) is preserved.

---

## Future Expansion

The architecture was deliberately kept modular so these can be added without rewrites:

- **Product recommendations / search / wishlist / cart** → add new tools (`ProductSearchTool`, `WishlistTool`, `CartTool`) and register them in `tool_registry.py`. No changes needed to the AI service loop.
- **Redis-backed memory** → implement a `RedisBackend(MemoryBackend)` in `app/memory/memory_store.py` and swap it in `get_memory_backend()`. `ConversationMemory` and the routers don't need to change.
- **RAG / vector database for FAQs** → replace `find_faq_answer()` in `app/tools/faq_knowledge.py` with a vector similarity search; `FAQTool`'s interface stays identical.
- **Streaming responses / WebSockets** → add a new router using FastAPI's `StreamingResponse` or a WebSocket endpoint that calls into `AIService` with a streaming-aware LLM client.
- **LangGraph** → `AIService._run_tool_loop` can be replaced with a LangGraph graph while keeping the same public `handle_chat_turn` signature.
- **Multilingual support** → extend `PromptManager` to inject a language instruction based on a user preference or `Accept-Language` header.
- **Admin dashboard / analytics** → add a new router reading from a `conversations` table if you migrate memory to Postgres.

---

## License

Internal project tooling for APNA STORE. Adapt as needed.
