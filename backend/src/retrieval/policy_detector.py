# backend/src/retrieval/policy_detector.py

POLICIES = {
    "star comprehensive individual 2024": "Star Comprehensive",
    "star comprehensive": "Star Comprehensive",
    "star senior citizen": "Star Senior Citizen",
    "bajaj health guard family": "Bajaj Health Guard Family",
    "bajaj health guard": "Bajaj Health Guard Family",
    "hdfc ergo": "HDFC Ergo",
    "hdfc": "HDFC Ergo",
}


def detect_policy(question: str):
    """
    Detect the policy mentioned in the user's question.

    Returns the normalized policy name exactly as it exists
    in the indexed metadata.
    """

    q = question.lower().strip()

    # Match longer names first
    for key in sorted(POLICIES.keys(), key=len, reverse=True):
        if key in q:
            return POLICIES[key]

    return None