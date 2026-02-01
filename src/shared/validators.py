import re


def validate_phone_number(phone: str) -> str:
    cleaned = re.sub(r"[^\d+]", "", phone)
    if not re.match(r"^\+?\d{10,15}$", cleaned):
        raise ValueError(f"Invalid phone number: {phone}")
    return cleaned


def validate_email(email: str) -> str:
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        raise ValueError(f"Invalid email: {email}")
    return email.lower()
