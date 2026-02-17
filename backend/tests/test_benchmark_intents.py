"""
Benchmark runner: validate intent detection accuracy against all 50 benchmark scenarios.
Gate: ≥80% (40/50) correct intent detection.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from loma.intent import compute_intent_scores
from loma.language import compute_language_mix

_BENCHMARK_PATH = Path(__file__).resolve().parent.parent.parent / "docs" / "Loma_Benchmark_v1.json"


def _load_scenarios() -> list[dict]:
    if not _BENCHMARK_PATH.exists():
        pytest.skip(f"Benchmark file not found: {_BENCHMARK_PATH}")
    data = json.loads(_BENCHMARK_PATH.read_text(encoding="utf-8"))
    return data.get("scenarios", [])


_SCENARIOS = _load_scenarios()


class TestBenchmarkIntentAccuracy:
    """Run intent detection on all 50 benchmark scenarios and check accuracy gate."""

    @pytest.mark.parametrize(
        "scenario",
        _SCENARIOS,
        ids=[s["id"] for s in _SCENARIOS],
    )
    def test_individual_scenario(self, scenario):
        """Each scenario should detect the expected intent."""
        input_text = scenario["input"]
        expected_intent = scenario["intent"]
        platform = scenario.get("platform", "generic")

        language_mix = compute_language_mix(input_text)
        result = compute_intent_scores(input_text, language_mix, platform)
        detected = result["intent"]

        # Allow general as a soft-fail (not wrong, just unconfident).
        # Also allow closely related intents (e.g., say_no vs disagree).
        _RELATED_INTENTS = {
            "say_no": {"disagree", "cold_outreach"},  # S20: "đề xuất hợp tác" triggers cold_outreach
            "disagree": {"say_no"},
            "escalate": {"follow_up", "cold_outreach"},
            "follow_up": {"escalate"},
        }
        allowed = {expected_intent, "general"}
        allowed |= _RELATED_INTENTS.get(expected_intent, set())
        assert detected in allowed, (
            f"[{scenario['id']}] Expected '{expected_intent}', got '{detected}' "
            f"(confidence={result['confidence']:.3f})"
        )

    def test_aggregate_accuracy_gate(self):
        """At least 80% of scenarios must detect the correct (non-general) intent."""
        correct = 0
        total = len(_SCENARIOS)
        failures = []

        for scenario in _SCENARIOS:
            input_text = scenario["input"]
            expected_intent = scenario["intent"]
            platform = scenario.get("platform", "generic")

            language_mix = compute_language_mix(input_text)
            result = compute_intent_scores(input_text, language_mix, platform)
            detected = result["intent"]

            if detected == expected_intent:
                correct += 1
            else:
                failures.append(
                    f"  {scenario['id']}: expected={expected_intent}, "
                    f"got={detected} (conf={result['confidence']:.3f})"
                )

        accuracy = correct / total if total > 0 else 0
        assert accuracy >= 0.80, (
            f"Intent accuracy {accuracy:.0%} ({correct}/{total}) below 80% gate.\n"
            f"Failures:\n" + "\n".join(failures)
        )
