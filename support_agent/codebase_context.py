"""A curated technical knowledge snapshot of Tariflow-AI, the real product
this support agent is grounded in (github.com/RolexAlexander/Tariflow-AI).

Today's build (see /docs/scope for the hackathon's own honest cut) uses a
static, hand-curated snapshot rather than live repo ingestion -- every fact
below was read directly out of the actual source (src/index.ts,
src/services/tariff-manager.ts, src/utils/asycuda.ts, src/queues/*.ts) on
2026-09-11, not invented. "Deepen tomorrow" work replaces this with live
ingestion (see docs/roadmap.md) so the agent stays current as the codebase
changes -- this snapshot is the correctness baseline that live ingestion
gets checked against.
"""

TARIFLOW_CONTEXT = """
# Tariflow-AI -- Technical Support Knowledge Base

Tariflow-AI is an AI-powered customs clearance assistant: it automates
document processing, item extraction, and HS-code tariff classification for
customs brokers and importers. It runs as a Cloudflare Worker (Hono
framework, TypeScript), backed by Supabase (Postgres + Storage), Cloudflare
Queues, Cloudflare KV, and an R2 bucket.

## Endpoints and what they actually do

- `GET /health` -- liveness check, returns service name + version.
- `GET /tariff-status` -- reports whether the cached tariff schedule file
  (used for classification) is currently valid.
- `POST /operations` -- uploads a customs document and starts processing.
  Requires `Content-Type: multipart/form-data` and an `X-User-Id` header;
  missing either returns 400/401. Accepts an optional `operationId` to
  update an existing draft instead of creating a new one.
- `POST /operations/:id/classify` -- enqueues HS-code classification for an
  already-uploaded operation.
- `POST /classify-items` -- classifies ad-hoc items directly (no DB write),
  using Gemini with the cached tariff schedule PDF as grounding context.

## Known, real constraints that cause support issues

- **Upload size threshold at 300KB.** Files at or under 300KB are base64-
  encoded and sent inline through the processing queue -- but only if the
  resulting base64 payload also fits Cloudflare Queues' ~128KB message
  limit (with an ~8KB safety buffer reserved for JSON overhead). Files
  larger than that, or whose base64 encoding pushes past the queue limit,
  are instead uploaded directly to Supabase Storage (bucket: `documents`)
  and a document row is created immediately so the UI shows the file while
  processing continues. **If a customer's larger file "isn't showing up
  right away" or "processing seems stuck," this inline-vs-storage branching
  is the first thing to check** -- it's an intentional path, not a bug, but
  it does mean large-file uploads look different in the UI timeline than
  small ones.
- **Missing `X-User-Id` header returns a 401**, and a missing/incorrect
  `Content-Type` on the upload returns a 400 with `Content-Type must be
  multipart/form-data`. Both are common integration mistakes on the
  customer's client side, not server bugs.
- **Per-IP rate limit: 200 requests/minute**, enforced via a Cloudflare KV
  token-bucket keyed by `CF-Connecting-IP` and the current UTC minute.
  Exceeding it returns `{"error": "rate_limited"}` with HTTP 429. This is a
  common cause of intermittent failures for customers polling status
  endpoints too aggressively.
- **The tariff classification file cache is valid for 47 hours.** The
  service uploads the tariff schedule PDF (from an R2 bucket) to the
  Gemini Files API and caches the resulting file ID in KV. If a customer
  reports `"Tariff file not available"` (a 500 from `/classify-items`),
  the most likely causes are: the R2 bucket/tariff PDF isn't configured
  (`TARIFF_BUCKET`), or the Gemini API key is invalid/exhausted, or the
  cached file expired and re-upload is failing.
- **Classification uses Gemini with the tariff PDF as file-grounded
  context**, applying the Harmonized System (HS) and the General
  Interpretative Rules (GIRs) -- classification requests explicitly ask for
  the 10-digit HS code, chapter/heading/subheading, reasoning, applicable
  GIRs, alternative codes considered, and a confidence score. If a customer
  says classification results "don't cite reasoning" or "seem low
  confidence," that's the model's own output quality on a given item, not
  a service outage -- worth walking them through re-submitting with a
  clearer item description.
- **Processing is asynchronous via three named Cloudflare Queues**:
  `tariflow-doc-processing` (document parsing), `tariflow-classify` (HS
  classification), `tariflow-export` (currently disabled/commented out in
  the live route, so a customer asking for an export endpoint should be
  told it isn't live yet, not that it's broken). A customer reporting a job
  that "never finishes" is describing an async queue in flight, not
  necessarily a stuck process -- ask for the `request_id` returned at
  submission time to check status.
- **ASYCUDA export.** There is a utility (`createAsycudaImportXml`) that
  converts a structured declaration into the real ASYCUDA Guyana IMPORT XML
  format used by customs authorities, calculating customs duty (`CUS`) and
  VAT per item based on CIF value (invoice + freight + insurance + other
  costs, converted at the declared currency rate). If a customer reports
  "wrong tax totals" on an export, check whether `dutyRate`/`vatRate` were
  supplied per item -- taxes are only calculated for items where those
  rates are greater than zero.

## Tone guidance for support calls

Tariflow-AI's actual users are customs brokers and importers -- often under
real time pressure (a shipment sitting at port, a declaration deadline).
Be warm, direct, and concrete: cite the specific mechanism causing their
issue rather than generic troubleshooting steps, and always end with either
a clear resolution or a clear, specific next step (e.g. "resubmit with the
X-User-Id header set" rather than "try again").
"""
