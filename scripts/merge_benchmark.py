#!/usr/bin/env python3
"""
Merge competitor benchmark data (Gemini, Claude, Copilot) into the main results file.
Calculates weighted scores, rankings, and overall winner for each scenario.
"""

import json
import sys

WEIGHTS = {
    "cultural_accuracy": 0.3,
    "structural_completeness": 0.25,
    "tone_calibration": 0.2,
    "entity_preservation": 0.15,
    "conciseness": 0.1,
}

def weighted_score(score_dict):
    """Calculate weighted total score (max 2.0)."""
    total = 0.0
    for criterion, weight in WEIGHTS.items():
        total += score_dict.get(criterion, 0) * weight
    return round(total, 2)

def main():
    # Load main results
    with open("docs/Loma_Benchmark_v1_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Load competitor data
    competitors = {}
    for name in ["gemini", "claude", "copilot"]:
        path = f"docs/benchmark_{name}.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                arr = json.load(f)
            competitors[name] = {item["id"]: item for item in arr}
            print(f"  Loaded {len(arr)} scenarios from {path}")
        except FileNotFoundError:
            print(f"  WARNING: {path} not found, skipping {name}")
        except json.JSONDecodeError as e:
            print(f"  ERROR: {path} has invalid JSON: {e}")
            sys.exit(1)

    # Track overall results (5-way)
    win_counts = {"loma": 0, "chatgpt": 0, "gemini": 0, "claude": 0, "copilot": 0, "tie": 0}

    # Track head-to-head results (Loma vs each)
    h2h = {
        comp: {"loma_wins": 0, "opponent_wins": 0, "ties": 0}
        for comp in ["chatgpt", "gemini", "claude", "copilot"]
    }

    # Merge into each scenario
    for scenario in data["scenarios"]:
        sid = scenario["id"]

        # Add competitor outputs and scores
        for name, lookup in competitors.items():
            if sid in lookup:
                item = lookup[sid]
                scenario[f"{name}_output"] = item.get(f"{name}_output", "")
                scenario[f"{name}_score"] = item.get(f"{name}_score", {})

        # Calculate weighted scores for all competitors
        scores = {}
        for comp in ["loma", "chatgpt", "gemini", "claude", "copilot"]:
            score_key = f"{comp}_score"
            if score_key in scenario and scenario[score_key]:
                scores[comp] = weighted_score(scenario[score_key])

        # Determine 5-way winner (highest weighted score)
        if scores:
            max_score = max(scores.values())
            winners = [comp for comp, s in scores.items() if s == max_score]

            if len(winners) == 1:
                scenario["winner"] = winners[0]
                win_counts[winners[0]] += 1
            else:
                scenario["winner"] = "tie"
                win_counts["tie"] += 1

            # Add rankings with scores
            scenario["rankings"] = dict(sorted(scores.items(), key=lambda x: -x[1]))

        # Head-to-head: Loma vs each competitor
        loma_score = scores.get("loma", 0)
        scenario["head_to_head"] = {}
        for comp in ["chatgpt", "gemini", "claude", "copilot"]:
            comp_score = scores.get(comp, 0)
            if loma_score > comp_score:
                scenario["head_to_head"][comp] = "loma_wins"
                h2h[comp]["loma_wins"] += 1
            elif comp_score > loma_score:
                scenario["head_to_head"][comp] = f"{comp}_wins"
                h2h[comp]["opponent_wins"] += 1
            else:
                scenario["head_to_head"][comp] = "tie"
                h2h[comp]["ties"] += 1

    # Update meta
    data["meta"]["purpose"] = "5-way benchmark: Loma vs ChatGPT vs Gemini vs Claude vs Copilot across 50 Vietnamese business communication scenarios."
    data["meta"]["competitors"] = {
        "loma": {
            "prompt": "[Auto-detected intent + tone + system persona + cultural patterns — full pipeline]",
            "description": "Loma's specialized Vietnamese cultural transformation pipeline"
        },
        "chatgpt": {
            "prompt": "Rewrite this professionally in English:",
            "model": "GPT-4o"
        },
        "gemini": {
            "prompt": "Rewrite this professionally in English:",
            "model": "Gemini 2.0 Pro"
        },
        "claude": {
            "prompt": "Rewrite this professionally in English:",
            "model": "Claude 3.5 Sonnet"
        },
        "copilot": {
            "prompt": "Rewrite this professionally in English:",
            "model": "Microsoft Copilot (GPT-4o)"
        }
    }
    data["meta"]["overall_results"] = win_counts
    data["meta"]["head_to_head"] = {
        comp: {
            "loma_wins": h2h[comp]["loma_wins"],
            f"{comp}_wins": h2h[comp]["opponent_wins"],
            "ties": h2h[comp]["ties"]
        }
        for comp in ["chatgpt", "gemini", "claude", "copilot"]
    }

    # Remove old single-competitor fields from meta
    if "chatgpt_prompt" in data["meta"]:
        del data["meta"]["chatgpt_prompt"]
    if "loma_prompt" in data["meta"]:
        del data["meta"]["loma_prompt"]

    # Write merged file
    with open("docs/Loma_Benchmark_v1_results.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n=== 5-Way Benchmark Results ===")
    print(f"  Loma wins:    {win_counts['loma']}")
    print(f"  ChatGPT wins: {win_counts['chatgpt']}")
    print(f"  Gemini wins:  {win_counts['gemini']}")
    print(f"  Claude wins:  {win_counts['claude']}")
    print(f"  Copilot wins: {win_counts['copilot']}")
    print(f"  Ties:         {win_counts['tie']}")
    print(f"\n  Total: {sum(win_counts.values())} scenarios")
    print(f"\n  Loma win rate: {win_counts['loma']}/{sum(win_counts.values())} = {win_counts['loma']/sum(win_counts.values())*100:.1f}%")

    # Print head-to-head results
    print("\n=== Head-to-Head: Loma vs Each ===")
    for comp in ["chatgpt", "gemini", "claude", "copilot"]:
        r = h2h[comp]
        total = r["loma_wins"] + r["opponent_wins"] + r["ties"]
        print(f"  vs {comp:10s}: Loma {r['loma_wins']}W / {r['ties']}T / {r['opponent_wins']}L  (win rate {r['loma_wins']/total*100:.0f}%)")

    # Print per-competitor average scores
    comp_totals = {c: [] for c in ["loma", "chatgpt", "gemini", "claude", "copilot"]}
    for scenario in data["scenarios"]:
        for comp in comp_totals:
            if f"{comp}_score" in scenario and scenario[f"{comp}_score"]:
                comp_totals[comp].append(weighted_score(scenario[f"{comp}_score"]))

    print("\n=== Average Weighted Scores ===")
    for comp in ["loma", "claude", "gemini", "chatgpt", "copilot"]:
        scores = comp_totals[comp]
        if scores:
            avg = sum(scores) / len(scores)
            print(f"  {comp:10s}: {avg:.3f} / 2.000  ({len(scores)} scenarios)")

if __name__ == "__main__":
    main()
