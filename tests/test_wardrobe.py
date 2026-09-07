import random

from src.wardrobe import (
    generate_outfit,
    score_color_pair,
    score_outfit_candidate,
)


def sample_wardrobe():
    return [
        {"id": 1, "name": "Black Oversized Graphic Tee", "category": "Top", "color": "Black"},
        {"id": 2, "name": "White Oxford Shirt", "category": "Top", "color": "White"},
        {"id": 3, "name": "Navy Polo Tshirt", "category": "Top", "color": "Navy Blue"},
        {"id": 4, "name": "Black Cargo Pants", "category": "Bottom", "color": "Black"},
        {"id": 5, "name": "Beige Chinos", "category": "Bottom", "color": "Beige"},
        {"id": 6, "name": "Black Formal Trousers", "category": "Bottom", "color": "Black"},
        {"id": 7, "name": "White Sneakers", "category": "Footwear", "color": "White"},
        {"id": 8, "name": "Grey Running Sneakers", "category": "Footwear", "color": "Grey"},
        {"id": 9, "name": "Black Formal Shoes", "category": "Footwear", "color": "Black"},
        {"id": 10, "name": "Brown Loafers", "category": "Footwear", "color": "Brown"},
        {"id": 11, "name": "Black Blazer", "category": "Outerwear", "color": "Black"},
        {"id": 12, "name": "Beige Hoodie", "category": "Outerwear", "color": "Beige"},
        {"id": 13, "name": "Silver Watch", "category": "Accessory", "color": "Silver"},
        {"id": 14, "name": "Brown Leather Belt", "category": "Accessory", "color": "Brown"},
        {"id": 15, "name": "Black Cap", "category": "Accessory", "color": "Black"},
    ]


def test_formal_event_uses_formal_core_pieces():
    outfit = generate_outfit(
        sample_wardrobe(),
        "Formal Event",
        "Any Weather",
        rng=random.Random(7),
    )

    assert "shirt" in outfit["Top"]["name"].lower()
    assert any(word in outfit["Bottom"]["name"].lower() for word in ("trouser", "chinos"))
    assert any(word in outfit["Footwear"]["name"].lower() for word in ("formal", "loafer", "chelsea"))
    assert outfit["match_score"] >= 70


def test_weather_changes_layering_behavior():
    wardrobe = sample_wardrobe()

    hot = generate_outfit(
        wardrobe,
        "College",
        "Hot",
        rng=random.Random(3),
    )
    cold = generate_outfit(
        wardrobe,
        "College",
        "Cold",
        rng=random.Random(3),
    )

    assert "Outerwear" not in hot
    assert "Outerwear" in cold


def test_candidate_score_exposes_all_components():
    items = [
        sample_wardrobe()[1],
        sample_wardrobe()[5],
        sample_wardrobe()[8],
        sample_wardrobe()[10],
    ]

    breakdown = score_outfit_candidate(items, "Interview", "Cool")

    assert set(breakdown) == {"occasion", "color", "weather", "cohesion", "total"}
    assert all(0 <= value <= 100 for value in breakdown.values())


def test_neutral_colors_are_compatible():
    assert score_color_pair("Black", "White") >= 85
    assert score_color_pair("Navy Blue", "White") >= 85


def test_missing_core_category_returns_none():
    wardrobe = [
        {"id": 1, "name": "White Tee", "category": "Top", "color": "White"},
        {"id": 2, "name": "Black Jeans", "category": "Bottom", "color": "Black"},
    ]

    assert generate_outfit(wardrobe, "College") is None
