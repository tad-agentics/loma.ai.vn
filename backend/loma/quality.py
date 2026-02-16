"""
Quality scorer — at launch only length_reduction_pct (Tech Spec 3.3).
"""
from __future__ import annotations


def compute_length_reduction_pct(original: str, rewritten: str) -> int:
    """Returns percentage (0-100) by which output is shorter. Can be negative if output is longer."""
    if not original:
        return 0
    orig_len = len(original)
    new_len = len(rewritten)
    if orig_len == 0:
        return 0
    reduction = (orig_len - new_len) / orig_len * 100
    return int(round(reduction))


def score_rewrite(original_text: str, output_text: str) -> dict:
    """
    Returns dict with only shipped metric at launch: length_reduction_pct.
    Other metrics can be computed and stored internally later.
    """
    return {
        "length_reduction_pct": compute_length_reduction_pct(original_text, output_text),
    }
