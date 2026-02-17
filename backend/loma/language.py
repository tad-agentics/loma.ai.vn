"""
Vietnamese detection and language mix (Tech Spec 3.1).
Code-switch aware: ≥3 diacritics or ≥2 function words => contains Vietnamese.

Improvements over v1:
- Romanized Vietnamese detection (no diacritics): common bigrams and trigrams
  that are unambiguously Vietnamese even without diacritics.
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

# Romanized Vietnamese bigrams/trigrams — patterns that are unambiguously Vietnamese
# even without diacritics. Each must appear as a word boundary match.
# These catch users who type without Vietnamese keyboard.
_ROMANIZED_VI_PATTERNS = re.compile(
    r"\b("
    # Common greeting/address patterns
    r"anh oi|chi oi|em oi"
    r"|xin chao|cam on|xin loi"
    # Common function word pairs (unambiguous when combined)
    r"|duoc khong|chua duoc|khong duoc"
    r"|nhu the|nhu vay|tai sao"
    r"|the nao|lam sao|bao nhieu"
    # Business Vietnamese without diacritics
    r"|thanh toan|hoa don|bao cao|de xuat|dong y"
    r"|gioi thieu|hop tac|phan tich|danh gia"
    r"|xin phep|gui anh|gui chi|nho anh|nho chi"
    # Politeness markers
    r"|vang a|cam on anh|cam on chi"
    r"|mong anh|mong chi"
    r")\b",
    re.IGNORECASE,
)

# Single romanized words that are strong Vietnamese signals (low false-positive with English)
_ROMANIZED_VI_WORDS = re.compile(
    r"\b(khong|chua|duoc|nhung|hoac|vay|gui|xin|moi)\b",
    re.IGNORECASE,
)


def contains_vietnamese(text: str) -> bool:
    """True if text contains Vietnamese (≥3 diacritics or ≥2 function words or romanized patterns)."""
    if not text or len(text) < 10:
        return False

    # Check 1: Vietnamese diacritics (strongest signal)
    vi_char_matches = len(VI_CHARS.findall(text))
    if vi_char_matches >= 3:
        return True

    # Check 2: Vietnamese function words with diacritics
    vi_word_matches = len(VI_FUNCTION_WORDS.findall(text))
    if vi_word_matches >= 2:
        return True

    # Check 3: Romanized Vietnamese bigrams/trigrams (no diacritics)
    romanized_bigram_matches = len(_ROMANIZED_VI_PATTERNS.findall(text))
    if romanized_bigram_matches >= 1:
        return True

    # Check 4: Multiple romanized Vietnamese single words (need ≥3 to avoid false positives)
    romanized_word_matches = len(_ROMANIZED_VI_WORDS.findall(text))
    if romanized_word_matches >= 3:
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
