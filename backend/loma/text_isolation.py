"""
Text isolation — extract user-written segment from full field content (UX Spec 2.2).
Strategy A (Gmail DOM) is extension-side; this module implements Strategy B (heuristic) for plain text.
Used by spike and by API when client sends full field text with text_isolation_method.
"""
from __future__ import annotations

import re


def extract_user_text(text: str) -> tuple[str, str]:
    """
    Extract the user-written portion of text (above first boundary).
    Returns (user_text, method) where method is "heuristic_boundary" or "full_field".
    """
    if not text or not text.strip():
        return ("", "full_field")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    # Find first line index that starts a boundary (inclusive); everything before = user text
    boundary_at: int | None = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Quoted line: ">" at start
        if stripped.startswith(">"):
            boundary_at = i
            break
        # "On [date], [name] wrote:" pattern
        if re.search(r"^On\s+.+wrote\s*:$", stripped, re.IGNORECASE):
            boundary_at = i
            break
        # Forwarded message
        if "forwarded message" in stripped.lower() and "----------" in stripped:
            boundary_at = i
            break
        # "From: " email header
        if re.match(r"^From:\s+", stripped):
            boundary_at = i
            break
        # Signature markers: "---" or "-- " on its own or at line start
        if stripped in ("---", "--", "-- "):
            boundary_at = i
            break
        if re.match(r"^--\s*$", stripped):
            boundary_at = i
            break
        # "Best regards," / "Sincerely," / "Thanks," (common closings before signature)
        if re.match(r"^(Best regards|Sincerely|Thanks|Regards|Cheers),?\s*$", stripped, re.IGNORECASE):
            # Next line often has a name; treat this line as start of signature block
            boundary_at = i
            break

    if boundary_at is not None and boundary_at > 0:
        user_lines = lines[:boundary_at]
        user_text = "\n".join(user_lines).strip()
        return (user_text, "heuristic_boundary")
    # Also check for "\n-- \n" inline (signature in plain text)
    sig_index = text.find("\n-- \n")
    if sig_index > 0:
        return (text[:sig_index].strip(), "heuristic_boundary")
    sig_index = text.find("\n--\n")
    if sig_index > 0:
        return (text[:sig_index].strip(), "heuristic_boundary")
    return (text.strip(), "full_field")
