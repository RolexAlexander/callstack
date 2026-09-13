# Tariflow Support Agent

**A technical support agent that actually understands your codebase — built for [CALL-E: Your Code Is Calling](https://call-e.devpost.com/).**

Most support bots read a FAQ. This one reads the actual product: it's grounded in real, specific facts pulled directly from [Tariflow-AI](https://github.com/RolexAlexander/Tariflow-AI)'s source code — exact size thresholds, cache TTLs, header requirements, queue names — and uses that grounding to diagnose a customer's technical issue correctly, then hands [CALL-E](https://call-e.devpost.com/) a task to actually phone the customer and walk them through the real fix.

## Why this, not another FAQ bot

Early-stage founders lose enormous amounts of time to technical support — especially the kind of support that requires actually knowing how the product works internally, not just matching keywords to a help article. This agent's diagnosis step is grounded in facts read directly out of Tariflow-AI's real source (`src/index.ts`, `src/services/tariff-manager.ts`, `src/utils/asycuda.ts`) — the 300KB inline-upload threshold, the 47-hour tariff-file cache, the per-IP rate limit, the async queue names — so it can say something like *"your file is 450KB, which pushes it into the Supabase Storage upload path rather than the inline queue — that's why it looks different in your timeline, not a failure"* instead of a generic "have you tried restarting."

## How it works

```
customer support message
        |
        v
+--------------------+     grounded in support_agent/codebase_context.py
|  diagnosis step     |     (real facts from Tariflow-AI's actual source)
|  (Gemini)           |
+--------------------+
        |
        v
   diagnosis + a natural-language call task
        |
        v
  no-call preview printed  <-- default stop point, nothing dialed yet
        |
        v  (only with --dispatch)
+--------------------+
|  CALL-E             |     places the real phone call, has the live
|  (calls.create_and_ |     conversation, confirms resolution, returns a
|   wait)             |     structured result
+--------------------+
```

## Safety: no-call preview by default

A customer's message flows straight into an LLM diagnosis — that diagnosis should never flow straight into a real phone call with no human in the loop. Running `main.py` **always** prints the diagnosis and the exact call task first and stops there; a real call is only placed with an explicit `--dispatch` flag, after you've reviewed what CALL-E is about to say. No credentials are even required for the preview path.

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in GOOGLE_API_KEY and CALLE_API_KEY

# Preview only -- diagnosis + call task printed, nothing dialed.
python main.py "+15550123456" "My 5MB customs document upload isn't showing up in the operation list"

# After reviewing the preview, place the real call:
python main.py "+15550123456" "My 5MB customs document upload isn't showing up in the operation list" --dispatch
```

Set `SUPPORT_MOCK=1` in `.env` to run `--dispatch` against a stub instead of a real call (useful for testing the full flow without spending CALL-E call credits).

### Testing without spending anything

```bash
python -m unittest tests.test_calle_client -v
```

Mocks the CALL-E SDK entirely and verifies the integration against the real installed package's actual API shape (`client.calls.create_and_wait(task=, recipient=, result_schema=)`) — every assertion here was checked for free before a single real call was placed.

## What's built today vs. what's next

**Built:**
- A curated, accurate technical knowledge snapshot of Tariflow-AI (`support_agent/codebase_context.py`) — read directly from the real source, not invented.
- A diagnosis step that cites the real mechanism behind a customer's issue.
- A no-call preview default with an explicit `--dispatch` flag required before any real call is placed — matching the safety pattern used across CALL-E's own community submissions.
- A working, tested CALL-E integration that places a real phone call with a structured result schema (`issue_resolved`, `customer_sentiment`, `summary`, `follow_up_needed`).

**Next:**
- Replace the static knowledge snapshot with live repo ingestion (read the actual current source at call time, so the agent stays correct as the codebase changes) — the static snapshot becomes the correctness baseline live ingestion gets checked against.
- Broader scenario coverage beyond upload/cache/rate-limit issues.
- A real inbound-call path (customer calls in) in addition to the current outbound diagnose-then-call flow.

## License

MIT — see [`LICENSE`](LICENSE).
