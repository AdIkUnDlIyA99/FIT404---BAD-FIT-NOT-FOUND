from src.analysis import analyze_outfit


# ═════════════════════════════════════════════
# OUTFIT COMPARISON
# ═════════════════════════════════════════════

def compare_outfits(outfit_a, outfit_b):
    """
    Analyze and compare two outfit images.

    Returns a dictionary containing:
    - individual reports
    - scores
    - winner
    - comparison summary
    """

    # Analyze both outfits using the same
    # analysis system.
    report_a = analyze_outfit(outfit_a)
    report_b = analyze_outfit(outfit_b)

    # ─────────────────────────────────────────
    # Calculate total scores
    # ─────────────────────────────────────────

    score_a = (
        report_a["color_harmony"]
        + report_a["visual_balance"]
    )

    score_b = (
        report_b["color_harmony"]
        + report_b["visual_balance"]
    )

    # ─────────────────────────────────────────
    # Determine winner
    # ─────────────────────────────────────────

    if score_a > score_b:
        winner = "Outfit A 🏆"

    elif score_b > score_a:
        winner = "Outfit B 🏆"

    else:
        winner = "It's a Tie 🤝"

    # ─────────────────────────────────────────
    # Generate comparison summary
    # ─────────────────────────────────────────

    if score_a > score_b:

        difference = score_a - score_b

        summary = (
            f"Outfit A scores higher overall by "
            f"{difference} points based on the "
            f"current color and visual-balance analysis."
        )

    elif score_b > score_a:

        difference = score_b - score_a

        summary = (
            f"Outfit B scores higher overall by "
            f"{difference} points based on the "
            f"current color and visual-balance analysis."
        )

    else:

        summary = (
            "Both outfits received the same overall "
            "score from the current analysis."
        )

    # ─────────────────────────────────────────
    # Return comparison
    # ─────────────────────────────────────────

    return {
        "outfit_a": report_a,
        "outfit_b": report_b,
        "score_a": score_a,
        "score_b": score_b,
        "winner": winner,
        "summary": summary,
    }
