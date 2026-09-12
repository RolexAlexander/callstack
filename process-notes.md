# Process Notes

## Day 1 (2026-09-11) -- light pass

- Brain dump from Rolex: a support agent for founders, especially technical
  support, that connects to their actual source code and understands what's
  there well enough to resolve real issues, delivered in a friendly way.
- Chose Tariflow-AI (Rolex's real customs-clearance product) as the demo
  codebase over a synthetic one -- same authenticity principle as the
  Agentic Cinema build: real technical grounding reads far more credibly
  than invented specifics.
- Read the actual Tariflow-AI source directly (local checkout, not GitHub
  API) to build `codebase_context.py`: Cloudflare Worker/Hono API, the
  300KB inline-vs-Supabase-Storage upload threshold, the 128KB Cloudflare
  Queue limit, the `X-User-Id`/`Content-Type` requirements, the 200
  req/min per-IP rate limit, the 47-hour tariff-file cache backed by the
  Gemini Files API, the three named processing queues, and the ASYCUDA
  export's duty/VAT calculation logic. Every fact in the context file is
  real, read from source on this date -- none invented.
- Caught a real integration trap before writing code around it (same
  pattern as the Parallel/`parallel` PyPI mixup from the last hackathon):
  `pip install calle` fails -- the real package is `calle-ai` (import name
  still `calle`). Verified the actual installed SDK's method signatures
  directly (`client.calls.create_and_wait(task=, recipient=,
  result_schema=)`) via `inspect` before writing the wrapper, rather than
  trusting docs prose alone.
- Built: diagnosis step (Gemini, grounded in the curated context) ->
  CALL-E call-task construction -> real CALL-E integration with a
  structured result schema. All verified structurally via mocked unit
  tests (zero cost) before spending any real call credits.
- Deliberately light scope today: static knowledge snapshot (not live repo
  ingestion), single outbound-call flow, narrow scenario coverage. Full
  list of what's deferred to the deepening pass is in the README.

## Still needed before submission (deadline: 2026-09-14, 11:45pm SGT)

- One real end-to-end test call once Rolex provides `GOOGLE_API_KEY` and
  `CALLE_API_KEY`.
- The PR to `CALLE-AI/awesome-phone-call-agents` per submission requirements.
- 3-minute demo video.
- Broaden scenario coverage and consider live repo ingestion during the
  deepening pass.
