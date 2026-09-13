# Final Demo Run

The real, live end-to-end test — this is what the demo video should show.

## Setup

- Codebase: [LightOnOCR-Server](https://github.com/RolexAlexander/LightOnOCR-Server) (real, public, ingested live via `--repo`)
- Customer message: *"My OCR job has been stuck in the queue for 20 minutes and I don't know if it's still processing"*
- Destination: a Twilio number (`+16893994083`) configured with a TwiML Bin that auto-answers, speaks a line, and records with transcription -- set up specifically because CALL-E's supported-regions list does not include Guyana, so a Guyana number couldn't be used directly (see "Known limitation" below).

## What happened

The no-call preview correctly diagnosed the issue, citing real specifics from the live-ingested source: no RQ worker consuming the queue, or the job exceeding the real `job_timeout=1000` (~16.5 minute) limit configured in the actual codebase, with the real retry backoff (`Retry(max=3, interval=[10, 30, 60])`) and the real status endpoint (`GET /jobs/{job_id}`).

With `--dispatch`, CALL-E placed a real call to the Twilio number and had a live conversation asking specifically about the 20-minute OCR job delay -- confirmed firsthand by Rolex, who received the call. This is the pipeline working exactly as designed, end to end, for real: live ingestion of a real codebase -> grounded diagnosis -> an actual phone call that named the real problem correctly.

## Known limitation surfaced by this run

CALL-E's supported-regions list does not include Guyana in any language (verified directly against their docs) -- a genuine platform constraint, not a bug in this project. `support_agent/calle_client.py` already handles the resulting `CalleAPIError` gracefully (see git history) rather than crashing, and this is documented here so it doesn't read as an oversight.

## Second codebase, same agent: fast-mmg

To prove genericity further, the same agent (unchanged code) was pointed at a
completely different real repo -- [fast-mmg](https://github.com/RolexAlexander/fast-mmg),
a payment integration layer, nothing like an OCR job queue.

Customer message: *"My payment signature keeps getting rejected by the API"*

The diagnosis correctly cited real, specific mechanics from the actual source:
the RSA key pair used in the signed checkout flow (`signed_server/main.py`),
the `PUBLIC_KEY_PATH`/`PRIVATE_KEY_PATH` convention naming keys after the
merchant MID, and the `SECRET_KEY`/`CLIENT_ID`/`MERCHANT_MSISDN` environment
variables packaged into the encrypted token. The call task walked through
checking the `keys/` directory, verifying `docker-compose.yml` env vars
match MMG's registered credentials, and testing `/generate-checkout` again.

**This one was not dispatched** -- the CALL-E account hit `insufficient_balance`
at the moment of dispatch. That's a real, honestly-surfaced account-balance
limit, not a code failure: the error was caught cleanly by
`support_agent/calle_client.py`'s `CalleAPIError` handling (`{"status":
"error", "error_code": "insufficient_balance", ...}`) rather than crashing --
which is itself evidence the error-handling work held up under a real,
unplanned failure mode. Worth showing in the demo video as a no-call preview:
different codebase, correctly diagnosed, same unmodified agent.

## Honest gap in this record

The structured JSON result (`issue_resolved`, `customer_sentiment`, `summary`, `follow_up_needed`) wasn't captured locally -- the polling script was intentionally stopped mid-wait, and CALL-E's API has no list-calls endpoint to retrieve it after the fact without the call ID. The call itself and its content are independently confirmed by Rolex having actually received and heard it. If the CALL-E web dashboard shows call history/transcripts, pull the transcript from there for the demo video rather than relying on this file alone.
