"""
Prompt assembly — build_system_prompt from playbook (Loma_Prompt_Playbook_v1).
Loads prompts from backend/prompts/ (or env/path relative to package).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

# When deployed as Lambda, prompts live next to handler or in package
_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
if not _PROMPTS_DIR.exists():
    _PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "backend" / "prompts"

PERSONA: dict = {}
INTENTS: dict[str, dict] = {}
MODIFIERS: dict[str, dict] = {}
_CULTURAL_PATTERNS: list[dict] = []

# Map intent names to cultural pattern categories
_INTENT_TO_CATEGORY: dict[str, list[str]] = {
    "request_senior": ["request_senior", "greeting_opening"],
    "ask_payment": ["ask_payment"],
    "follow_up": ["follow_up"],
    "say_no": ["say_no"],
    "cold_outreach": ["cold_outreach"],
    "give_feedback": ["give_feedback"],
    "disagree": ["disagree"],
    "escalate": ["escalate"],
    "apologize": ["apologize"],
    "ai_prompt": [],  # AI prompts don't benefit from cultural pattern examples
    "general": ["general_professional", "greeting_opening"],
}

_MAX_EXAMPLES = 3


def _load_prompts() -> None:
    global PERSONA, INTENTS, MODIFIERS, _CULTURAL_PATTERNS
    if PERSONA:
        return
    persona_path = _PROMPTS_DIR / "system_persona.json"
    if persona_path.exists():
        PERSONA = json.loads(persona_path.read_text(encoding="utf-8"))
    intents_dir = _PROMPTS_DIR / "intents"
    if intents_dir.exists():
        for f in intents_dir.glob("*.json"):
            INTENTS[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    mod_dir = _PROMPTS_DIR / "modifiers"
    if mod_dir.exists():
        for f in mod_dir.glob("*.json"):
            MODIFIERS[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    # Load cultural patterns (cached at module level)
    _load_cultural_patterns()


def _load_cultural_patterns() -> None:
    """Load the Cultural Patterns JSON once. Searched in docs/ relative to project root."""
    global _CULTURAL_PATTERNS
    if _CULTURAL_PATTERNS:
        return
    root = Path(__file__).resolve().parent.parent.parent
    candidates = [
        root / "docs" / "Loma_Cultural_Patterns_v0.1.json",
        root / "backend" / "docs" / "Loma_Cultural_Patterns_v0.1.json",
    ]
    for path in candidates:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            _CULTURAL_PATTERNS = data.get("patterns", [])
            return


def _select_cultural_examples(intent: str, code_switched: bool | None = None) -> str:
    """Select up to _MAX_EXAMPLES cultural pattern examples for the given intent.

    Returns a formatted string block to inject into the system prompt, or empty string.
    """
    categories = _INTENT_TO_CATEGORY.get(intent, [])
    if not categories or not _CULTURAL_PATTERNS:
        return ""

    # Filter patterns matching this intent's categories
    matching = [p for p in _CULTURAL_PATTERNS if p.get("category") in categories]
    if not matching:
        return ""

    # Prefer code-switched examples when input is code-switched
    if code_switched is True:
        cs_matches = [p for p in matching if p.get("code_switched")]
        if cs_matches:
            matching = cs_matches

    # Select up to _MAX_EXAMPLES, deterministically seeded by intent for consistency
    rng = random.Random(intent)
    examples = rng.sample(matching, min(_MAX_EXAMPLES, len(matching)))

    # Format as few-shot examples
    lines = ["CULTURAL PATTERN EXAMPLES (for reference — apply the same transformation principles):"]
    for i, ex in enumerate(examples, 1):
        vi = ex.get("vietnamese_pattern", "")
        typical = ex.get("typical_translation", "")
        loma = ex.get("loma_mapping", "")
        note = ex.get("notes", "")
        lines.append(f"\nExample {i}:")
        lines.append(f"  Vietnamese: {vi}")
        lines.append(f"  Generic AI would write: {typical}")
        lines.append(f"  Loma writes: {loma}")
        if note:
            lines.append(f"  Why: {note}")

    return "\n".join(lines)


def build_system_prompt(
    intent: str,
    tone: str,
    language_mix: dict[str, float],
    platform: str | None = None,
    entities: list[dict] | None = None,
    output_language: str | None = None,
) -> str:
    """Assemble the full system prompt for a rewrite request (Tech Spec v1.5: output_language for Vietnamese)."""
    _load_prompts()
    parts = []

    # 1. Shared persona
    parts.append(PERSONA.get("system_prompt", "You are Loma, a professional English rewriting engine."))

    # 2. Intent-specific instructions + tone variant
    intent_data = INTENTS.get(intent, INTENTS.get("general", {}))
    tones = intent_data.get("tones", {})
    tone_key = tone if tone in tones else "professional"
    parts.append(tones.get(tone_key, "Produce clear, professional English."))

    # 2b. Cultural context (top-level field from intent JSON)
    cultural_ctx = intent_data.get("cultural_context", "")
    if cultural_ctx:
        parts.append(f"CULTURAL CONTEXT:\n{cultural_ctx}")

    # 2c. Few-shot cultural pattern examples from the pattern library
    vi_ratio = language_mix.get("vi_ratio", 0)
    code_switched = 0.1 < vi_ratio < 0.9
    examples_block = _select_cultural_examples(intent, code_switched=code_switched)
    if examples_block:
        parts.append(examples_block)

    # 2d. Vietnamese output (Tech Spec v1.5): when output_language is vi_*, instruct output language
    if output_language in ("vi_casual", "vi_formal", "vi_admin"):
        if output_language == "vi_admin":
            parts.append("Output in formal administrative Vietnamese (công văn style): correct structure, respectful register, proper legal/formal phrasing.")
        elif output_language == "vi_formal":
            parts.append("Output in formal Vietnamese: respectful, professional register suitable for email to superiors or official communication.")
        else:
            parts.append("Output in natural, collegial Vietnamese: appropriate for peers and informal professional contexts.")

    # 3. Code-switch modifier (vi_ratio between 0.1 and 0.9)
    if code_switched and "code_switch" in MODIFIERS:
        parts.append(MODIFIERS["code_switch"].get("instruction", ""))

    # 4. Entity preservation (Phase 2+)
    if entities and "entity_preservation" in MODIFIERS:
        entity_block = MODIFIERS["entity_preservation"].get("instruction", "")
        entity_list = ", ".join(f'{e.get("text", "")} ({e.get("label", "")})' for e in entities)
        entity_block = entity_block.replace("{entity_list}", entity_list)
        parts.append(entity_block)

    # 5. Platform override
    overrides = MODIFIERS.get("platform_overrides", {}).get("platforms", {})
    if platform and platform in overrides:
        parts.append(overrides[platform])

    return "\n\n".join(p for p in parts if p)
