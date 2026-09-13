# Demo Video Script (~3 minutes)

## 0:00-0:20 — Hook
"Most support bots read a FAQ. Callstack reads your actual codebase — point
it at any repo, and it diagnoses customer issues grounded in what's really
there, then has CALL-E place a real phone call to walk them through it."

## 0:20-0:40 — Architecture, fast
Show the README diagram. "Ingest any codebase, diagnose with Gemini, hand
CALL-E a task. No-call preview by default — a real call only happens with
an explicit --dispatch flag, after human review."

## 0:40-1:40 — Real run #1: LightOnOCR-Server (dispatched, live)
Screen: terminal running
```
python main.py --repo https://github.com/RolexAlexander/LightOnOCR-Server \
  "+16893994083" "My OCR job has been stuck in the queue for 20 minutes" --dispatch
```
Let the diagnosis print — pause on it, it's citing the real `job_timeout=1000`
config and the real retry backoff. Then: "And this isn't simulated — CALL-E
placed a real call." Cut to the Twilio call log / recording, or narrate:
"I received this call live and confirmed it correctly asked about the
20-minute delay."

## 1:40-2:20 — Real run #2: fast-mmg (proves genericity)
Screen: same command, different repo:
```
python main.py --repo https://github.com/RolexAlexander/fast-mmg \
  "+16893994083" "My payment signature keeps getting rejected by the API"
```
"Same agent, zero code changes, a completely unrelated codebase — a payment
integration layer instead of an OCR queue." Let the diagnosis print — it
correctly cites the real RSA key/signature flow and env var names. Mention
plainly: "This one hit a real CALL-E account balance limit on dispatch,
which is an honest thing to show — the error was caught cleanly instead of
crashing," then show the clean error output.

## 2:20-2:50 — Safety
"Every call goes through a no-call preview first. A real call requires an
explicit --dispatch flag after a human reviews exactly what CALL-E is about
to say — the same safety pattern used across nearly every accepted
submission in CALL-E's own community repo, which I read before building
this."

## 2:50-3:00 — Close
"Point Callstack at any codebase, and it becomes a technical support agent
that actually knows the product. Repo and PR are linked below."

## Reminders
- Public YouTube/Vimeo upload, English audio.
- Under 3 minutes.
- This is "here's my project running," not a cinematic trailer.
