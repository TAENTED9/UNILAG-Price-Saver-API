"""Payment helper functions (placeholder implementation).

This module provides a minimal `create_payment_link` implementation so
the router can function during development and tests. Replace with the
real payment provider integration when available.
"""
from urllib.parse import quote_plus

def create_payment_link(amount: float, description: str) -> str:
    """Return a test payment link for the given amount and description.

    This is a placeholder implementation. It URL-encodes the description
    and returns a mock URL that a frontend or tests can follow.
    """
    safe_desc = quote_plus(description or "")
    return f"https://payments-local.example/pay?amount={amount}&desc={safe_desc}"
