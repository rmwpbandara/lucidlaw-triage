# LucidLaw — AI Triage Prototype

A working triage prototype for **LucidLaw**, a legal platform for everyday Australians.
Describe a legal situation in plain language; the system classifies the area of law,
detects the Australian jurisdiction, and returns a short, supportive, plain-language
response with a sensible next step.

> **Live demo:** https://demo1.eseeds.lk
> **API health:** https://demo1-api.eseeds.lk/health
> **Source:** https://github.com/rmwpbandara/lucidlaw-triage
> _Always-on (self-hosted, no cold starts). The five test cases below are reproduced from this live deployment._

---

## What I built and why

A two-part system that mirrors LucidLaw's real platform direction:

- A **FastAPI** backend that exposes `POST /api/triage` — this is the real artifact, "the
  triage engine."
- A **Next.js** front end that keeps the experience simple and warm, as the brief asked.
- **Anthropic Claude** (`claude-sonnet-4-6`) does the classification, called through
  **forced tool use** so the response is structured by construction.

I treated the prototype as a small system built to a production standard, rather than a
throwaway script — clean module boundaries, typed contracts, tests, linting, CI, and
Docker — so it reads as the seed of the larger architecture it would grow into.

## Key technical decisions

- **Structured output via Claude tool use, not text parsing.** The model is forced to call a
  typed tool, so the result already matches the schema and can't drift into prose.
- **Pydantic validation at the boundary.** Enums and range checks guarantee a well-formed
  response (valid category, `confidence` in `[0, 1]`) before anything reaches the user.
- **Brand voice enforced in code.** Beyond the system prompt, a guardrail scans the
  user-facing text for combative/legalistic words and retries once if any slip through.
- **Honest ambiguity.** Uncertainty is explicit via `confidence`, `needs_clarification`, and
  `clarifying_question`, rather than a forced confident guess.

A fuller write-up of the design and trade-offs is in [`ARCHITECTURE.md`](./ARCHITECTURE.md).

## The output contract

Every request returns this structure:

```json
{
  "category": "tenancy_and_housing",
  "jurisdiction": "South Australia",
  "confidence": 0.92,
  "urgency": "medium",
  "summary": "You may be able to recover your bond if your landlord can't show evidence of damage beyond normal wear and tear.",
  "suggested_next_step": "We can help you put together a clear bond-recovery application for SACAT — it usually takes about 10 minutes.",
  "escalate_to_professional": false,
  "needs_clarification": false,
  "clarifying_question": null
}
```

The first seven fields are the brief's mandatory set. `needs_clarification` and
`clarifying_question` are **two additions** for honest ambiguity handling: when the situation
is unclear, `needs_clarification` is `true` and `clarifying_question` carries a gentle
follow-up (see Test 5 below). The brief welcomes extra fields.

## The five test cases

These are the **real, current outputs** from the live deployment (https://demo1-api.eseeds.lk),
not hand-written examples. Summary first, full JSON below.

| # | Situation | category | jurisdiction | confidence | urgency | escalate |
|---|---|---|---|---|---|---|
| 1 | Landlord in Adelaide won't return bond, 6 weeks | `tenancy_and_housing` | South Australia | 0.97 | medium | false |
| 2 | Made redundant, no notice, unpaid leave, 4 yrs | `employment` | not specified | 0.93 | high | **true** |
| 3 | Laptop screen failed at 3 months, no refund | `consumer_rights` | not specified | 0.95 | medium | false |
| 4 | Separating, two kids, can't agree on living | `family_law` | not specified | 0.97 | **high** | **true** |
| 5 | Someone parks in my driveway, can't stop them | `tenancy_and_housing` | not specified | **0.45** | medium | false |

**Test 1 — "My landlord in Adelaide is refusing to return my bond even though I left the place clean. It's been 6 weeks."**

```json
{
  "category": "tenancy_and_housing",
  "jurisdiction": "South Australia",
  "confidence": 0.97,
  "urgency": "medium",
  "summary": "It sounds like your landlord may be holding onto your bond without a valid reason, and after six weeks you have every right to take steps to get it back.",
  "suggested_next_step": "We can help you put together a clear, firm letter to your landlord requesting the bond be returned, and walk you through how to lodge an application with Consumer and Business Services SA if they don't respond.",
  "escalate_to_professional": false,
  "needs_clarification": false,
  "clarifying_question": null
}
```

**Test 2 — "I was made redundant last week with no notice and they haven't paid out my leave. I've worked there for four years."**

```json
{
  "category": "employment",
  "jurisdiction": "Australia — state not specified",
  "confidence": 0.93,
  "urgency": "high",
  "summary": "After four years with your employer, it looks like you may be owed notice pay and your accrued leave entitlements — both of which your employer is generally required to pay out when ending your employment through redundancy.",
  "suggested_next_step": "We can help you work out exactly what you're owed — including notice and leave — and put together a clear, calm letter to your employer asking them to make it right.",
  "escalate_to_professional": true,
  "needs_clarification": false,
  "clarifying_question": null
}
```

**Test 3 — "I bought a laptop three months ago and the screen has completely failed. The store is refusing to refund or replace it."**

```json
{
  "category": "consumer_rights",
  "jurisdiction": "Australia — state not specified",
  "confidence": 0.95,
  "urgency": "medium",
  "summary": "A laptop screen failing after just three months is likely covered by Australian Consumer Law guarantees, which give you the right to a repair, replacement, or refund when a product doesn't last as long as it reasonably should — and the store may not be able to simply turn you away.",
  "suggested_next_step": "We can help you put together a clear, confident letter to the store outlining your rights under Australian Consumer Law and asking them to make things right.",
  "escalate_to_professional": false,
  "needs_clarification": false,
  "clarifying_question": null
}
```

**Test 4 — "My partner and I are separating. We have two kids and we can't agree on where they'll live."**

```json
{
  "category": "family_law",
  "jurisdiction": "Australia — state not specified",
  "confidence": 0.97,
  "urgency": "high",
  "summary": "You and your partner are going through a separation and are working through where your two children will live — this is one of the most important things to sort out, and there are clear steps and support available to help you reach a safe, stable arrangement for your kids.",
  "suggested_next_step": "We can help you understand how parenting arrangements work in Australia and connect you with a family law professional who can guide you through next steps with care and clarity.",
  "escalate_to_professional": true,
  "needs_clarification": false,
  "clarifying_question": null
}
```

**Test 5 — "Someone keeps parking in my driveway and I can't get them to stop."** _(deliberately ambiguous)_

```json
{
  "category": "tenancy_and_housing",
  "jurisdiction": "Australia — state not specified",
  "confidence": 0.45,
  "urgency": "medium",
  "summary": "It sounds like someone is regularly blocking access to your driveway, which can be frustrating and may affect your ability to use your property — there are practical steps that could help put a stop to it.",
  "suggested_next_step": "To point you in the right direction, it would help to know a little more — for example, whether this is happening at a rental property or your own home, and who is doing the parking (a neighbour, a stranger, or someone connected to a body corporate).",
  "escalate_to_professional": false,
  "needs_clarification": true,
  "clarifying_question": "Could you tell us a bit more about your situation — for example, do you own or rent your home, and do you know who keeps parking there (a neighbour, a visitor, or someone else)?"
}
```

Case 5 is the deliberately ambiguous one. Rather than force a confident label, it returns a
**low-confidence (0.45)** best fit with `needs_clarification: true` and a gentle question.
Driveway/neighbour issues sit closest to tenancy & housing in the taxonomy, so that is the
nearest fit — but the honesty matters more than a confident guess.

## What it does well

- Reliable, validated JSON for any plain-language input.
- Clean, warm, resolution-first language with no legal jargon — enforced in code.
- Graceful, honest handling of the ambiguous case.
- Production-shaped foundation: tests, linting, CI, Docker, clear module boundaries.

## What it doesn't do yet (known limits)

- **No grounding in real legislation** — summaries are general information, not verified law.
- **Single-turn only** — no follow-up conversation after a clarifying question.
- **Jurisdiction detection is signal-based** (city/state mentions), not exhaustive.
- **No persistence, accounts, or rate limiting** — out of scope for a prototype.

## If I were building this for production, the first three things I would add

1. **Citation-grounded answers (RAG).** Retrieve real Australian legislation and guidance and
   require every statement to cite a verified source — zero-hallucination is the core trust
   requirement for legal content.
2. **A multi-agent flow with a safety layer.** Intake → classify → jurisdiction → retrieve →
   reason, with human-in-the-loop and a dedicated, separated safety pathway (e.g. family/DV),
   plus a scope guardrail that keeps the system on the information side of the
   information-vs-advice line.
3. **A compliance foundation.** Australian data residency, an append-only audit trail, and
   consent capture — the groundwork that makes a legal product lawful and investable.

---

## Running it locally

### Prerequisites
- Python 3.11+ · Node.js 18+ · an Anthropic API key (`console.anthropic.com`)

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # paste your real ANTHROPIC_API_KEY
uvicorn app.main:app --reload # http://localhost:8000  (docs at /docs)
```

Smoke test:
```bash
curl -s localhost:8000/api/triage -H 'Content-Type: application/json' \
  -d '{"description":"My landlord in Adelaide won'\''t return my bond after 6 weeks."}' \
  | python -m json.tool
```

### Frontend
```bash
cd frontend
cp .env.local.example .env.local
npm install && npm run dev    # http://localhost:3000
```

### With Docker (both services)
```bash
export ANTHROPIC_API_KEY=sk-ant-...
docker compose up --build
```

## Testing

```bash
cd backend
pytest             # offline suite: schema, guardrail, taxonomy
pytest -s -m live  # live suite: runs the five cases against the real API (needs a key)
```

## Deployment

The live demo runs as an **isolated Docker stack on a VPS**, behind a shared nginx reverse
proxy with TLS terminated at the edge (Cloudflare Origin certificate):

- `docker-compose.prod.yml` builds two containers (`demo1-backend`, `demo1-web`) on a private
  Docker network — **no host ports exposed**.
- The edge nginx proxy routes by hostname: `demo1.eseeds.lk` → web, `demo1-api.eseeds.lk` →
  backend.
- `NEXT_PUBLIC_API_URL` is baked into the frontend at **build time** (a Docker build arg);
  backend secrets (`ANTHROPIC_API_KEY`, `MODEL`, `CORS_ORIGINS`) are read from a host `.env`.

Run the same production stack anywhere with Docker:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Each service also ships a standalone `Dockerfile`, so it deploys cleanly to Railway, Render,
or Fly.io (backend) and Vercel (frontend) without the compose file.

## Project structure

```
lucidlaw-triage/
├── backend/                  FastAPI triage engine (Claude tool use, validation, guardrail, tests)
├── frontend/                 Next.js consumer UI
├── ARCHITECTURE.md           design decisions and trade-offs
├── docker-compose.yml        local two-service dev stack
├── docker-compose.prod.yml   production stack (private network, build args)
└── .github/workflows/ci.yml  lint + test on every push
```

## Tech stack

Python · FastAPI · Pydantic v2 · Anthropic Claude (`claude-sonnet-4-6`) · Next.js ·
TypeScript · Ruff · pytest · Docker · GitHub Actions.

---

_Built for the LucidLaw technical co-founder assessment._
