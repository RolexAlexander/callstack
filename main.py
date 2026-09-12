"""Tariflow Support Agent -- CLI entrypoint.

Given a customer's technical support message, diagnoses the real cause
using grounded Tariflow-AI knowledge, then hands CALL-E a task to actually
phone the customer and walk them through it.

Usage:
    python main.py "+15550123456" "My 5MB customs document upload isn't showing up in the operation list"
"""

import sys

from support_agent.calle_client import run_support_call
from support_agent.config import CALLE_API_KEY, GOOGLE_API_KEY, MOCK
from support_agent.diagnose import diagnose


def run(phone: str, customer_message: str) -> None:
    if not MOCK:
        missing = [
            name
            for name, val in [("GOOGLE_API_KEY", GOOGLE_API_KEY), ("CALLE_API_KEY", CALLE_API_KEY)]
            if not val
        ]
        if missing:
            print(f"[warning] Missing: {', '.join(missing)}. Falling back to mock where needed.\n")

    print(f"=== Customer message ===\n{customer_message}\n")

    result = diagnose(customer_message)
    print(f"=== Internal diagnosis ===\n{result['diagnosis']}\n")
    print(f"=== Call task handed to CALL-E ===\n{result['call_task']}\n")

    print("=== Placing support call via CALL-E ===")
    call_result = run_support_call(phone, result["call_task"])
    print(call_result)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python main.py "<phone_e164>" "<customer message>"')
        sys.exit(1)
    run(sys.argv[1], " ".join(sys.argv[2:]))
