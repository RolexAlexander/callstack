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

## Day 3 (2026-09-13) -- deepening pass

- Rolex flagged, correctly, that Tariflow-AI (the demo codebase from day 1)
  is actually a **private** repo -- verified via `gh repo view`. Rolex's
  stated policy is that private repos are mostly real business ideas, so
  grounding a public submission's content in it was a real miss on my
  part; I should have checked visibility before choosing it, not after.
  Rolex later judged, after seeing what was actually exposed, that the
  content didn't reveal meaningful architecture and was comfortable
  leaving the existing history as-is rather than requiring a repo
  delete/recreate -- noted here as his explicit call, not something I
  decided unilaterally.
- Verified `stocksphere` (a candidate Rolex asked about) is also private.
  Confirmed two genuinely public, technical candidates instead:
  `LightOnOCR-Server` (FastAPI/RQ/Redis OCR queue) and `fast-mmg` (payment
  integration layer) -- both verified via `gh repo view --json isPrivate`
  before use, not assumed.
- Bigger fix, prompted by Rolex directly asking whether this "spins up on
  any codebase" -- it didn't yet; day 1's build was a hand-curated,
  single-codebase-specific snapshot. Rebuilt as genuine generic ingestion
  (`support_agent/repo_ingest.py`): given any local path or git URL, reads
  the real README + a capped sample of real source files at call time.
  `diagnose()` now takes this as a parameter instead of importing a fixed
  constant. Verified for real (zero-cost, just a git clone) against the
  live LightOnOCR-Server repo -- 8,159 characters of real content ingested
  correctly on the first try.
- Demo plan upgraded accordingly: show the same agent correctly diagnosing
  issues against two unrelated real codebases (LightOnOCR-Server and
  fast-mmg) in the video, which is a much stronger proof of genericity
  than one example.

- Renamed the project to **Callstack** (call stack + phone calls) once the
  build genuinely became a generic framework rather than a one-codebase
  tool -- fitting, since the name only became honest after the ingestion
  rewrite above. Renamed the GitHub repo, local directory, git remote, and
  updated the already-open PR (#536) to match, rather than leaving stale
  branding in a submission that had already moved past it. Added Rolex's
  logo to `assets/logo.png`.
- PR to `CALLE-AI/awesome-phone-call-agents` opened and kept in sync with
  the rename: https://github.com/CALLE-AI/awesome-phone-call-agents/pull/536

## Still needed before submission (deadline: 2026-09-14, 11:45am Guyana time / 11:45pm SGT)

- One real end-to-end test call now that Rolex has `GOOGLE_API_KEY` and
  `CALLE_API_KEY` ready to add.
- 3-minute demo video -- plan: same agent against two unrelated repos
  (LightOnOCR-Server, fast-mmg) to make the genericity claim visible, not
  just asserted.
- Broaden scenario coverage if time allows.
