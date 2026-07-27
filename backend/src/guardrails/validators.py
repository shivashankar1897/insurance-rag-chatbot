import re

from src.guardrails.pii import detect_pii


INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"forget (everything|your rules)",
    r"you are now",
    r"act as",
    r"jailbreak",
    r"pretend you",
    r"override (your|all) (instructions|rules)",
    r"disregard your",
]

OUT_OF_SCOPE = [
    r"(write|create) (code|script|essay)",
    r"what is the (capital|population) of",
    r"(weather|stock price|bitcoin)",
    r"(recipe|cook|food)",
]

AADHAAR = r"\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b"

MAX_QUESTION_LENGTH = 2000


def check_input(question: str):

    pii = detect_pii(question)

    if pii or re.search(AADHAAR, question):

        return (
            False,
            "pii",
            "Your question contains personal information. Please remove it and ask again.",
        )

    for pattern in INJECTION_PATTERNS:

        if re.search(pattern, question.lower()):

            return (
                False,
                "injection",
                "Please ask a question about your insurance policy.",
            )

    for pattern in OUT_OF_SCOPE:

        if re.search(pattern, question.lower()):

            return (
                False,
                "out_of_scope",
                "I can only answer questions about your insurance policy.",
            )

    if len(question) > MAX_QUESTION_LENGTH:

        return (
            False,
            "too_long",
            "Please ask one specific question at a time.",
        )

    return True, None, None