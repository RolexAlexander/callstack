"""Tariflow Support Agent -- CLI entrypoint.

Given a customer's technical support message, diagnoses the real cause
using grounded Tariflow-AI knowledge, then hands CALL-E a task to actually
phone the customer and walk them through it.

No-call preview is the default. A real call is only ever placed with an
explicit --dispatch flag, after the diagnosis and exact call task are
printed for human review -- matching the safety pattern used across the
CALL-E community's own accepted submissions (dry-run/preview default,
explicit human approval before a real-world phone call fires).

Usage:
    # Preview only -- no call placed, no CALL-E credentials even required.
    python main.py "+15550123456" "My 5MB customs document upload isn't showing up in the operation list"

    # Place the real call after reviewing the preview.
    python main.py "+15550123456" "..." --dispatch
"""

import argparse

from support_agent.calle_client import run_support_call
from support_agent.config import CALLE_API_KEY, GOOGLE_API_KEY, MOCK
from support_agent.diagnose import diagnose


def run(phone: str, customer_message: str, dispatch: bool) -> None:
    print(f"=== Customer message ===\n{customer_message}\n")

    result = diagnose(customer_message)
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
    parser = argparse.ArgumentParser(description="Tariflow Support Agent")
    parser.add_argument("phone", help="Customer phone number, E.164 format (e.g. +15550123456)")
    parser.add_argument("message", nargs="+", help="The customer's support message")
    parser.add_argument(
        "--dispatch",
        action="store_true",
        help="Actually place the call via CALL-E. Without this flag, only a no-call preview is printed.",
    )
    args = parser.parse_args()
    run(args.phone, " ".join(args.message), args.dispatch)
