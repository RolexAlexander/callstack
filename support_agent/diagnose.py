"""Diagnosis step: given a customer's support message and a codebase's
ingested technical context, produce (a) an internal diagnosis and (b) a
natural-language call task for CALL-E's own calling agent to execute.

The context is now always passed in (from repo_ingest.ingest_codebase),
not imported as a fixed constant -- this is what makes the agent work on
any codebase, not just one it was demoed on.
"""

from google import genai

from support_agent.config import GOOGLE_API_KEY, TEXT_MODEL

DIAGNOSIS_PROMPT = """You are the internal diagnosis engine for this product's technical support system. \
You have been given real, current knowledge of exactly how the product works -- use it, don't guess.

{context}

A customer has raised this issue:
\"\"\"{customer_message}\"\"\"

Do two things:

1. DIAGNOSIS: Identify the most likely real technical cause, citing the specific mechanism \
from the knowledge base above (an exact function, endpoint, limit, or config value if one is \
relevant). If multiple causes are plausible, name the most likely one and one alternative to \
rule out. If the knowledge base genuinely doesn't cover this issue, say so plainly rather than \
inventing a mechanism that isn't there.

2. CALL_TASK: Write clear, natural-language instructions for a calling agent who will phone \
this customer to walk them through the issue. It must be warm and direct, explain the real \
cause in plain language (not jargon-for-jargon's-sake), give a specific concrete next step, \
and confirm with the customer whether the issue is resolved before ending the call.

Respond in exactly this format:

DIAGNOSIS:
<your diagnosis>

CALL_TASK:
<the task text to hand to the calling agent>
"""


def diagnose(customer_message: str, codebase_context: str) -> dict:
    """Returns {"diagnosis": str, "call_task": str}."""
    prompt = DIAGNOSIS_PROMPT.format(context=codebase_context, customer_message=customer_message)

    client = genai.Client(api_key=GOOGLE_API_KEY)
    response = client.models.generate_content(model=TEXT_MODEL, contents=prompt)
    text = response.text or ""

    diagnosis, _, rest = text.partition("CALL_TASK:")
    diagnosis = diagnosis.replace("DIAGNOSIS:", "").strip()
    call_task = rest.strip()

    if not call_task:
        # Fall back gracefully if the model didn't follow the format exactly,
        # rather than silently dropping the whole response.
        call_task = text.strip()

    return {"diagnosis": diagnosis, "call_task": call_task}
