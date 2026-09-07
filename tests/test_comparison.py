from PIL import Image

import src.comparison as comparison


def create_image(color=(100, 100, 100)):
    return Image.new("RGB", (100, 100), color)


def test_weighted_score_matches_documented_formula():
    report = {
        "color_harmony": 90,
        "visual_balance": 70,
    }

    expected = round(
        comparison.HARMONY_WEIGHT * 90
        + comparison.BALANCE_WEIGHT * 70
    )

    assert comparison.calculate_outfit_score(report) == expected


def test_compare_outfits_returns_transparent_breakdown(monkeypatch):
    reports = iter(
        [
            {"color_harmony": 92, "visual_balance": 84},
            {"color_harmony": 75, "visual_balance": 88},
        ]
    )

    monkeypatch.setattr(
        comparison,
        "analyze_outfit",
        lambda _image: next(reports),
    )

    result = comparison.compare_outfits(create_image(), create_image())

    assert result["winner"] == "Outfit A 🏆"
    assert result["score_a"] > result["score_b"]
    assert result["weights"]["color_harmony"] == comparison.HARMONY_WEIGHT
    assert "58% color harmony" in result["summary"]
    assert "42% visual balance" in result["summary"]


def test_same_reports_tie(monkeypatch):
    monkeypatch.setattr(
        comparison,
        "analyze_outfit",
        lambda _image: {"color_harmony": 80, "visual_balance": 80},
    )

    result = comparison.compare_outfits(create_image(), create_image())

    assert result["score_a"] == result["score_b"]
    assert "Tie" in result["winner"]
