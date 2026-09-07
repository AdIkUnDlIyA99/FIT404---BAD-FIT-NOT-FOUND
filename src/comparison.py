"""Outfit-vs-outfit scoring for FIT404."""

from __future__ import annotations

from src.analysis import analyze_outfit


HARMONY_WEIGHT = 0.58
BALANCE_WEIGHT = 0.42


def calculate_outfit_score(report: dict) -> int:
    """Return the weighted visual score used by Fit Battle."""

    harmony = float(report.get("color_harmony", 0))
    balance = float(report.get("visual_balance", 0))

    return int(round(HARMONY_WEIGHT * harmony + BALANCE_WEIGHT * balance))


def compare_outfits(outfit_a, outfit_b) -> dict:
    """Analyze two outfit images and compare the same metrics shown in the UI."""

    report_a = analyze_outfit(outfit_a)
    report_b = analyze_outfit(outfit_b)

    score_a = calculate_outfit_score(report_a)
    score_b = calculate_outfit_score(report_b)

    if score_a > score_b:
        winner = "Outfit A 🏆"
        leading_label = "Outfit A"
        difference = score_a - score_b
    elif score_b > score_a:
        winner = "Outfit B 🏆"
        leading_label = "Outfit B"
        difference = score_b - score_a
    else:
        winner = "It's a Tie 🤝"
        leading_label = None
        difference = 0

    if leading_label:
        summary = (
            f"{leading_label} leads by {difference} point"
            f"{'s' if difference != 1 else ''} on FIT404's weighted visual score "
            f"({HARMONY_WEIGHT:.0%} color harmony + {BALANCE_WEIGHT:.0%} visual balance)."
        )
    else:
        summary = (
            "Both outfits receive the same weighted visual score "
            f"({HARMONY_WEIGHT:.0%} color harmony + {BALANCE_WEIGHT:.0%} visual balance)."
        )

    return {
        "outfit_a": report_a,
        "outfit_b": report_b,
        "score_a": score_a,
        "score_b": score_b,
        "winner": winner,
        "summary": summary,
        "weights": {
            "color_harmony": HARMONY_WEIGHT,
            "visual_balance": BALANCE_WEIGHT,
        },
    }
