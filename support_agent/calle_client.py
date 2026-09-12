"""Thin wrapper around the real calle-ai SDK.

Verified against the installed package's actual API surface before writing
this (see process-notes.md) -- `client.calls.create_and_wait(task=...,
recipient=..., result_schema=...)` returns a dict once CALL-E's own agent
has finished the call. Degrades to a clearly-labeled mock when
SUPPORT_MOCK=1 or no key is set, so the diagnosis pipeline can be verified
for free before spending real call credits.
"""

from calle import CalleClient

from support_agent.config import CALLE_API_KEY, MOCK

RESULT_SCHEMA = {
    "type": "object",
    "required": ["issue_resolved", "customer_sentiment", "summary"],
    "properties": {
        "issue_resolved": {"type": "boolean"},
        "customer_sentiment": {
            "type": "string",
            "enum": ["satisfied", "neutral", "frustrated", "escalation_needed"],
        },
        "summary": {"type": "string"},
        "follow_up_needed": {"type": "string"},
    },
}


def run_support_call(phone_e164: str, task: str) -> dict:
    """Place a real support call via CALL-E and wait for the structured result.

    Args:
        phone_e164: Customer phone number in E.164 format, e.g. "+15550123456".
        task: Natural-language instructions for CALL-E's own calling agent --
            what to explain, what to walk the customer through, and what to
            confirm before ending the call.

    Returns:
        The structured result dict (matching RESULT_SCHEMA) once the call
        completes, or a clearly-labeled mock result.
    """
    if MOCK or not CALLE_API_KEY:
        return {
            "mock": True,
            "issue_resolved": True,
            "customer_sentiment": "satisfied",
            "summary": (
                "MOCK MODE: no CALLE_API_KEY set / SUPPORT_MOCK=1. No real "
                "call was placed. Task that would have been sent to CALL-E:\n"
                f"{task}"
            ),
            "follow_up_needed": "",
        }

    client = CalleClient(api_key=CALLE_API_KEY)
    try:
        call = client.calls.create_and_wait(
            task=task,
            recipient={"phones": [phone_e164]},
            result_schema=RESULT_SCHEMA,
        )
        return call.get("structured_result", call)
    finally:
        client.close()
