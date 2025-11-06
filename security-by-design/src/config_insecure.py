"""Insecure configuration examples (DO NOT COPY TO PROD)."""

API_KEY = "hard-coded-dev-key"  # Hard-coded secret
DEBUG = True  # Verbose error leaks internals

def verbose_error(e: Exception) -> str:
    # Returns raw exception string (may leak stack, internals)
    return f"Error occurred: {e!r}"
