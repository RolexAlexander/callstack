"""Thin wrapper around the real calle-ai SDK.

Verified against the installed package's actual API surface before writing
this (see process-notes.md) -- `client.calls.create_and_wait(task=...,
recipient=..., result_schema=...)` returns a dict once CALL-E's own agent
has finished the call. Degrades to a clearly-labeled mock when
SUPPORT_MOCK=1 or no key is set, so the diagnosis pipeline can be verified
for free before spending real call credits.
"""

from calle import CalleClient
from calle.errors import CalleAPIError

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
        structured = call.get("structured_result")
        if structured is not None:
            return structured
        # Structured extraction can come back None even on a real, completed
        # call (e.g. the model couldn't confidently fill the schema) -- fall
        # back to the call's own top-level fields instead of returning None
        # and losing all visibility into what actually happened.
        return {
            "status": call.get("status"),
            "summary": call.get("summary"),
            "task_completed": call.get("task_completed"),
            "failure_code": call.get("failure_code"),
            "failure_message": call.get("failure_message"),
            "raw": call,
        }
    except CalleAPIError as exc:
        # e.g. an unsupported region/language combination for this number --
        # a real, expected rejection, not a crash.
        return {
            "status": "error",
            "error_code": exc.code,
            "error": str(exc),
            "details": exc.details,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}
    finally:
        client.close()
