import re
from typing import Dict, Optional


def extract_amount(text: str) -> Optional[float]:
    """
    Try to identify a likely transaction total
    from OCR extracted receipt text.
    """

    patterns = [
        r"total\s*[:\-]?\s*(?:rs\.?|lkr)?\s*([\d,]+(?:\.\d{1,2})?)",
        r"amount\s*[:\-]?\s*(?:rs\.?|lkr)?\s*([\d,]+(?:\.\d{1,2})?)",
        r"(?:rs\.?|lkr)\s*([\d,]+(?:\.\d{1,2})?)",
    ]

    lower_text = text.lower()

    for pattern in patterns:
        match = re.search(
            pattern,
            lower_text,
            re.IGNORECASE
        )

        if match:
            value = (
                match.group(1)
                .replace(",", "")
            )

            try:
                return float(value)

            except ValueError:
                pass

    return None


def extract_date(text: str) -> Optional[str]:
    """
    Detect common receipt date formats.
    """

    patterns = [
        r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",
        r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b",
        r"\b(\d{1,2}[.-]\d{1,2}[.-]\d{4})\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text
        )

        if match:
            return match.group(1)

    return None


def extract_merchant(text: str) -> Optional[str]:
    """
    Use the first meaningful OCR line as
    an initial merchant/store candidate.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    ignored_words = [
        "receipt",
        "invoice",
        "tax invoice",
        "bill",
    ]

    for line in lines:

        clean_line = line.lower()

        if any(
            word == clean_line
            for word in ignored_words
        ):
            continue

        if len(line) >= 3:
            return line[:100]

    return None


def suggest_category(
    merchant: Optional[str],
    text: str
) -> str:

    combined = (
        f"{merchant or ''} {text}"
    ).lower()

    category_rules = {
        "Food & Dining": [
            "restaurant",
            "cafe",
            "coffee",
            "food",
            "pizza",
            "burger",
        ],

        "Groceries": [
            "supermarket",
            "grocery",
            "keells",
            "cargills",
            "arpico",
        ],

        "Transport": [
            "fuel",
            "petrol",
            "diesel",
            "uber",
            "pickme",
            "taxi",
        ],

        "Shopping": [
            "store",
            "fashion",
            "clothing",
            "electronics",
        ],

        "Utilities": [
            "electricity",
            "water",
            "internet",
            "mobile",
            "telecom",
        ],

        "Healthcare": [
            "pharmacy",
            "hospital",
            "medical",
            "clinic",
        ],
    }

    for category, keywords in category_rules.items():

        if any(
            keyword in combined
            for keyword in keywords
        ):
            return category

    return "Other"


def parse_receipt_text(
    text: str
) -> Dict:

    merchant = extract_merchant(
        text
    )

    amount = extract_amount(
        text
    )

    date = extract_date(
        text
    )

    category = suggest_category(
        merchant,
        text
    )

    return {
        "merchant": merchant,
        "amount": amount,
        "date": date,
        "suggested_category": category,
        "raw_text": text
    }