"""Tariflow Support Agent -- CLI entrypoint.

Given ANY codebase (a local path or a git URL) and a customer's technical
support message, ingests the real codebase, diagnoses the real cause, then
hands CALL-E a task to actually phone the customer and walk them through
it. This is designed to spin up on any product's codebase, not just one.

No-call preview is the default. A real call is only ever placed with an
explicit --dispatch flag, after the diagnosis and exact call task are
printed for human review.

Usage:
    # Preview only -- no call placed, no CALL-E credentials even required.
    python main.py --repo https://github.com/RolexAlexander/LightOnOCR-Server \\
        "+15550123456" "My OCR job has been stuck in the queue for 20 minutes"

    # After reviewing the preview, place the real call:
    python main.py --repo https://github.com/RolexAlexander/LightOnOCR-Server \\
        "+15550123456" "My OCR job has been stuck in the queue for 20 minutes" --dispatch
"""

import argparse

from support_agent.calle_client import run_support_call
from support_agent.config import CALLE_API_KEY, GOOGLE_API_KEY, MOCK
from support_agent.diagnose import diagnose
from support_agent.repo_ingest import ingest_codebase


def run(repo: str, phone: str, customer_message: str, dispatch: bool) -> None:
    print(f"=== Ingesting codebase: {repo} ===")
    context = ingest_codebase(repo)
    print(f"({len(context)} characters of real codebase context ingested)\n")

    print(f"=== Customer message ===\n{customer_message}\n")

    result = diagnose(customer_message, context)
    print(f"=== Internal diagnosis ===\n{result['diagnosis']}\n")
    print(f"=== Call task that would be handed to CALL-E ===\n{result['call_task']}\n")

    if not dispatch:
        print(
            "=== No-call preview (default) ===\n"
            "No real call was placed. Review the diagnosis and call task above, then "
            "re-run with --dispatch to actually place the call via CALL-E.\n"
        )
        return

    if not MOCK:
        missing = [
            name
            for name, val in [("GOOGLE_API_KEY", GOOGLE_API_KEY), ("CALLE_API_KEY", CALLE_API_KEY)]
            if not val
        ]
        if missing:
            print(f"[warning] Missing: {', '.join(missing)}. Falling back to mock where needed.\n")

    print("=== --dispatch set: placing the real support call via CALL-E ===")
    call_result = run_support_call(phone, result["call_task"])
    print(call_result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Codebase-grounded technical support agent")
    parser.add_argument(
        "--repo",
        required=True,
        help="Local path or git URL of the codebase to ground diagnosis in",
    )
    parser.add_argument("phone", help="Customer phone number, E.164 format (e.g. +15550123456)")
    parser.add_argument("message", nargs="+", help="The customer's support message")
    parser.add_argument(
        "--dispatch",
        action="store_true",
        help="Actually place the call via CALL-E. Without this flag, only a no-call preview is printed.",
    )
    args = parser.parse_args()
    run(args.repo, args.phone, " ".join(args.message), args.dispatch)
