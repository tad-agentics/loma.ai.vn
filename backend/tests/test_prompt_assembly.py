"""Tests for loma.prompt_assembly — system prompt construction, cultural examples."""
from loma.prompt_assembly import (
    build_system_prompt,
    _select_cultural_examples,
    _INTENT_TO_CATEGORY,
    _load_prompts,
    INTENTS,
)


class TestBuildSystemPrompt:
    def test_returns_string(self):
        prompt = build_system_prompt(
            intent="general",
            tone="professional",
            language_mix={"vi_ratio": 0.5, "en_ratio": 0.5},
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_contains_persona(self):
        prompt = build_system_prompt(
            intent="general",
            tone="professional",
            language_mix={"vi_ratio": 0.0, "en_ratio": 1.0},
        )
        assert "Loma" in prompt or "rewriting" in prompt.lower()

    def test_all_tones_work(self):
        for tone in ("professional", "direct", "warm", "formal"):
            prompt = build_system_prompt(
                intent="general",
                tone=tone,
                language_mix={"vi_ratio": 0.5, "en_ratio": 0.5},
            )
            assert len(prompt) > 0

    def test_intent_specific_content(self):
        prompt_follow = build_system_prompt(
            intent="follow_up",
            tone="professional",
            language_mix={"vi_ratio": 0.5, "en_ratio": 0.5},
        )
        prompt_general = build_system_prompt(
            intent="general",
            tone="professional",
            language_mix={"vi_ratio": 0.5, "en_ratio": 0.5},
        )
        # Different intents should produce different prompts
        assert prompt_follow != prompt_general

    def test_platform_override_included(self):
        prompt_gmail = build_system_prompt(
            intent="general",
            tone="professional",
            language_mix={"vi_ratio": 0.0, "en_ratio": 1.0},
            platform="gmail",
        )
        prompt_none = build_system_prompt(
            intent="general",
            tone="professional",
            language_mix={"vi_ratio": 0.0, "en_ratio": 1.0},
        )
        # Gmail prompt should be longer due to platform override
        assert len(prompt_gmail) >= len(prompt_none)

    def test_vi_casual_output_language(self):
        prompt = build_system_prompt(
            intent="general",
            tone="professional",
            language_mix={"vi_ratio": 0.5, "en_ratio": 0.5},
            output_language="vi_casual",
        )
        assert "Vietnamese" in prompt

    def test_vi_formal_output_language(self):
        prompt = build_system_prompt(
            intent="general",
            tone="professional",
            language_mix={"vi_ratio": 0.5, "en_ratio": 0.5},
            output_language="vi_formal",
        )
        assert "Vietnamese" in prompt

    def test_vi_admin_output_language(self):
        prompt = build_system_prompt(
            intent="write_to_gov",
            tone="formal",
            language_mix={"vi_ratio": 1.0, "en_ratio": 0.0},
            output_language="vi_admin",
        )
        assert "công văn" in prompt.lower() or "Vietnamese" in prompt

    def test_code_switch_modifier(self):
        prompt = build_system_prompt(
            intent="general",
            tone="professional",
            language_mix={"vi_ratio": 0.4, "en_ratio": 0.6},
        )
        # Should be longer than pure English prompt due to code-switch modifier
        prompt_en = build_system_prompt(
            intent="general",
            tone="professional",
            language_mix={"vi_ratio": 0.0, "en_ratio": 1.0},
        )
        assert len(prompt) >= len(prompt_en)

    def test_entity_preservation(self):
        entities = [
            {"text": "Nguyen Van A", "label": "names"},
            {"text": "$5,000", "label": "money"},
        ]
        prompt = build_system_prompt(
            intent="general",
            tone="professional",
            language_mix={"vi_ratio": 0.5, "en_ratio": 0.5},
            entities=entities,
        )
        # Entity preservation modifier should be included if available
        assert isinstance(prompt, str)

    def test_unknown_intent_falls_back(self):
        """Unknown intent should fall back to general without crashing."""
        prompt = build_system_prompt(
            intent="nonexistent_intent_xyz",
            tone="professional",
            language_mix={"vi_ratio": 0.0, "en_ratio": 1.0},
        )
        assert len(prompt) > 0

    def test_unknown_tone_falls_back(self):
        """Unknown tone should fall back to professional."""
        prompt = build_system_prompt(
            intent="general",
            tone="nonexistent_tone",
            language_mix={"vi_ratio": 0.0, "en_ratio": 1.0},
        )
        assert len(prompt) > 0


class TestAllIntentsHavePromptFiles:
    def test_all_mapped_intents_have_files(self):
        _load_prompts()
        for intent in _INTENT_TO_CATEGORY:
            if intent in INTENTS:
                data = INTENTS[intent]
                assert "tones" in data, f"Intent '{intent}' missing 'tones' key"
                tones = data["tones"]
                assert "professional" in tones, f"Intent '{intent}' missing 'professional' tone"


class TestCulturalExamples:
    def test_general_returns_examples(self):
        examples = _select_cultural_examples("general")
        # May or may not return examples depending on pattern availability
        assert isinstance(examples, str)

    def test_ai_prompt_returns_empty(self):
        """ai_prompt has no cultural pattern categories."""
        examples = _select_cultural_examples("ai_prompt")
        assert examples == ""

    def test_vn_output_intents_return_empty(self):
        """Vietnamese output intents have no cultural pattern examples."""
        for intent in ("write_to_gov", "write_formal_vn", "write_report_vn", "write_proposal_vn"):
            examples = _select_cultural_examples(intent)
            assert examples == ""

    def test_unknown_intent_returns_empty(self):
        examples = _select_cultural_examples("nonexistent")
        assert examples == ""

    def test_deterministic_selection(self):
        """Same intent should always produce the same examples."""
        ex1 = _select_cultural_examples("follow_up")
        ex2 = _select_cultural_examples("follow_up")
        assert ex1 == ex2

    def test_code_switched_preference(self):
        """When code_switched=True, should prefer code-switched examples if available."""
        examples_cs = _select_cultural_examples("general", code_switched=True)
        examples_normal = _select_cultural_examples("general", code_switched=False)
        # Both should be valid strings
        assert isinstance(examples_cs, str)
        assert isinstance(examples_normal, str)


class TestIntentToCategoryMapping:
    def test_all_intents_mapped(self):
        expected_intents = {
            "request_senior", "ask_payment", "follow_up", "say_no",
            "cold_outreach", "give_feedback", "disagree", "escalate",
            "apologize", "ai_prompt", "general",
            "write_to_gov", "write_formal_vn", "write_report_vn", "write_proposal_vn",
        }
        assert set(_INTENT_TO_CATEGORY.keys()) == expected_intents

    def test_categories_are_lists(self):
        for intent, categories in _INTENT_TO_CATEGORY.items():
            assert isinstance(categories, list), f"Intent '{intent}' categories is not a list"
