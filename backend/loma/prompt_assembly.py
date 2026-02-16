"""
Prompt assembly — build_system_prompt from playbook (Loma_Prompt_Playbook_v1).
Loads prompts from backend/prompts/ (or env/path relative to package).
"""
from __future__ import annotations

import json
from pathlib import Path

# When deployed as Lambda, prompts live next to handler or in package
_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
if not _PROMPTS_DIR.exists():
    _PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "backend" / "prompts"

PERSONA: dict = {}
INTENTS: dict[str, dict] = {}
MODIFIERS: dict[str, dict] = {}


def _load_prompts() -> None:
    global PERSONA, INTENTS, MODIFIERS
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

    # 2b. Vietnamese output (Tech Spec v1.5): when output_language is vi_*, instruct output language
    if output_language in ("vi_casual", "vi_formal", "vi_admin"):
        if output_language == "vi_admin":
            parts.append("Output in formal administrative Vietnamese (công văn style): correct structure, respectful register, proper legal/formal phrasing.")
        elif output_language == "vi_formal":
            parts.append("Output in formal Vietnamese: respectful, professional register suitable for email to superiors or official communication.")
        else:
            parts.append("Output in natural, collegial Vietnamese: appropriate for peers and informal professional contexts.")

    # 3. Code-switch modifier (vi_ratio between 0.1 and 0.9)
    vi_ratio = language_mix.get("vi_ratio", 0)
    if 0.1 < vi_ratio < 0.9 and "code_switch" in MODIFIERS:
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
