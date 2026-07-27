from presidio_analyzer import AnalyzerEngine

# Create a single analyzer instance
analyzer = AnalyzerEngine()


def detect_pii(text: str) -> bool:
    """
    Detect whether the input text contains supported PII.
    Returns True if PII is found, otherwise False.
    """

    results = analyzer.analyze(
        text=text,
        language="en",
        entities=[
            "PHONE_NUMBER",
            "EMAIL_ADDRESS",
            "CREDIT_CARD",
        ],
    )

    return len(results) > 0