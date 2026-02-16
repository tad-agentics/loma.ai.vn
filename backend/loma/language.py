"""
Vietnamese detection and language mix (Tech Spec 3.1).
Code-switch aware: ≥3 diacritics or ≥2 function words => contains Vietnamese.
"""
import re

# Vietnamese-specific diacritics (unique to Vietnamese)
VI_CHARS = re.compile(
    r"[ăắằẳẵặâấầẩẫậđêếềểễệôốồổỗộơớờởỡợưứừửữự]",
    re.IGNORECASE,
)

# Vietnamese function words (high-signal, low false-positive)
VI_FUNCTION_WORDS = re.compile(
    r"\b(ơi|ạ|nhé|nha|đã|đang|sẽ|chưa|rồi|cái|của|cho|với|được|không|này|đó|thì|mà|là|và|hay|hoặc|nhưng|nếu|vì|để)\b",
    re.IGNORECASE,
)


def contains_vietnamese(text: str) -> bool:
    """True if text contains Vietnamese (≥3 diacritics or ≥2 function words)."""
    if not text or len(text) < 10:
        return False
    vi_char_matches = len(VI_CHARS.findall(text))
    if vi_char_matches >= 3:
        return True
    vi_word_matches = len(VI_FUNCTION_WORDS.findall(text))
    if vi_word_matches >= 2:
        return True
    return False


def compute_language_mix(text: str) -> dict[str, float]:
    """Returns {"vi_ratio": 0.0-1.0, "en_ratio": 0.0-1.0}."""
    words = [w for w in text.split() if len(w) > 1]
    total = len(words)
    if total == 0:
        return {"vi_ratio": 0.0, "en_ratio": 0.0}
    vi_count = 0
    for word in words:
        if VI_CHARS.search(word) or VI_FUNCTION_WORDS.search(word):
            vi_count += 1
    vi_ratio = round(vi_count / total * 100) / 100
    en_ratio = round((total - vi_count) / total * 100) / 100
    return {"vi_ratio": vi_ratio, "en_ratio": en_ratio}
