# Codebase Support Agent

**A technical support agent that actually understands *your* codebase — whatever it is — built for [CALL-E: Your Code Is Calling](https://call-e.devpost.com/).**

Most support bots read a FAQ. This one reads the actual product: point it at any codebase (a local path or a git URL) and it ingests the real README and source, uses that to diagnose a customer's technical issue correctly, then hands [CALL-E](https://call-e.devpost.com/) a task to actually phone the customer and walk them through the real fix. Demoed against two unrelated real services — [LightOnOCR-Server](https://github.com/RolexAlexander/LightOnOCR-Server) (a FastAPI/RQ/Redis OCR job queue) and [fast-mmg](https://github.com/RolexAlexander/fast-mmg) (a payment integration layer) — to prove it's genuinely generic, not tuned to one product.

## Why this, not another FAQ bot

Early-stage founders lose enormous amounts of time to technical support — especially the kind that requires actually knowing how the product works internally, not just matching keywords to a help article. This agent's diagnosis step is grounded in whatever real source it's pointed at: exact endpoints, queue names, rate limits, cache behavior, config values — so it can say something concrete and specific instead of a generic "have you tried restarting."

## How it works

```
--repo <path or git URL>          "customer support message"
        |                                 |
        v                                 |
+--------------------+                    |
|  ingest_codebase()  |  clones/reads      |
|                     |  README + source   |
+--------------------+                    |
        |                                 |
        +----------------+----------------+
                          v
                +--------------------+
                |  diagnosis step     |   grounded in whatever was
                |  (Gemini)           |   actually ingested above
                +--------------------+
                          |
                          v
             diagnosis + a natural-language call task
                          |
                          v
              no-call preview printed  <-- default stop point
                          |
                          v  (only with --dispatch)
                +--------------------+
                |  CALL-E             |   places the real phone call,
                |  (calls.create_and_ |   confirms resolution, returns
                |   wait)             |   a structured result
                +--------------------+
```

## Safety: no-call preview by default

A customer's message flows straight into an LLM diagnosis — that diagnosis should never flow straight into a real phone call with no human in the loop. Running `main.py` **always** prints the diagnosis and the exact call task first and stops there; a real call is only placed with an explicit `--dispatch` flag, after you've reviewed what CALL-E is about to say. No credentials are even required for the preview path. This mirrors the safety pattern used across nearly every accepted submission in CALL-E's own community repo.

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in GOOGLE_API_KEY and CALLE_API_KEY

# Preview only -- ingests the real repo, diagnoses, prints the call task. Nothing dialed.
python main.py --repo https://github.com/RolexAlexander/LightOnOCR-Server \
  "+15550123456" "My OCR job has been stuck in the queue for 20 minutes"

# Works identically against a completely different codebase -- this is the point.
python main.py --repo https://github.com/RolexAlexander/fast-mmg \
  "+15550123456" "My payment signature keeps getting rejected"

# After reviewing the preview, place the real call:
python main.py --repo https://github.com/RolexAlexander/LightOnOCR-Server \
  "+15550123456" "My OCR job has been stuck in the queue for 20 minutes" --dispatch
```

`--repo` also accepts a local path, and works on a private repo if your local git credentials already have access to it — exactly like a normal `git clone`.

Set `SUPPORT_MOCK=1` in `.env` to run `--dispatch` against a stub instead of a real call (useful for testing the full flow without spending CALL-E call credits).

### Testing without spending anything

```bash
python -m unittest discover tests -v
```

- `tests/test_repo_ingest.py` verifies ingestion against a synthetic local directory (no network) — the test that actually backs the "works on any codebase" claim.
- `tests/test_calle_client.py` mocks the CALL-E SDK entirely and verifies the integration against the real installed package's actual API shape (`client.calls.create_and_wait(task=, recipient=, result_schema=)`).

Both were checked before a single real call was placed.

## What's built vs. what's next

**Built:**
- Generic codebase ingestion (`support_agent/repo_ingest.py`) — any local path or git URL, not hand-curated for one product.
- A diagnosis step grounded in whatever was actually ingested, honest when the knowledge base doesn't cover an issue rather than inventing a mechanism that isn't there.
- A no-call preview default with an explicit `--dispatch` flag required before any real call is placed.
- A working, tested CALL-E integration with a structured result schema (`issue_resolved`, `customer_sentiment`, `summary`, `follow_up_needed`).
- Verified live against two unrelated real, public repositories.

**Next:**
- Smarter file selection during ingestion (currently a simple size-capped walk; a real version would prioritize files most relevant to the customer's specific issue rather than reading breadth-first).
- Broader scenario coverage beyond what a first pass surfaces.
- A real inbound-call path (customer calls in) in addition to the current outbound diagnose-then-call flow.

## License

MIT — see [`LICENSE`](LICENSE).
