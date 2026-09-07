"""Digital wardrobe storage and the FIT404 Build Fit V2 recommender."""

from __future__ import annotations

import colorsys
import json
import random
import re
from itertools import combinations, product
from pathlib import Path

from PIL import ImageColor


# ═════════════════════════════════════════════
# STORAGE CONFIGURATION
# ═════════════════════════════════════════════

DATA_FOLDER = Path(__file__).resolve().parent.parent / "data"
WARDROBE_FILE = DATA_FOLDER / "wardrobe.json"

VALID_CATEGORIES = {
    "Top",
    "Bottom",
    "Footwear",
    "Outerwear",
    "Accessory",
}


# ═════════════════════════════════════════════
# RECOMMENDATION PROFILES
# ═════════════════════════════════════════════

OCCASION_PROFILES = {
    "Casual Outing": {
        "target_formality": 1.4,
        "styles": {"casual", "streetwear", "minimal"},
        "prefer": {"tee", "tshirt", "jeans", "cargo", "sneaker", "overshirt", "denim"},
        "avoid": {"formal"},
        "outerwear_preference": 0.25,
        "accessory_preference": 0.35,
    },
    "College": {
        "target_formality": 1.7,
        "styles": {"casual", "smart casual", "preppy", "minimal"},
        "prefer": {"tee", "tshirt", "polo", "shirt", "jeans", "chinos", "sneaker", "overshirt"},
        "avoid": {"formal shoes"},
        "outerwear_preference": 0.30,
        "accessory_preference": 0.30,
    },
    "Party": {
        "target_formality": 2.5,
        "styles": {"smart casual", "streetwear", "minimal"},
        "prefer": {"shirt", "polo", "black", "blazer", "chelsea", "sneaker", "chain", "watch"},
        "avoid": {"running"},
        "outerwear_preference": 0.55,
        "accessory_preference": 0.80,
    },
    "Interview": {
        "target_formality": 4.0,
        "styles": {"formal", "business casual", "smart casual", "preppy"},
        "prefer": {"oxford", "formal shirt", "shirt", "trouser", "chinos", "formal shoes", "loafer", "chelsea", "blazer", "belt", "watch"},
        "avoid": {"graphic", "cargo", "baggy", "running", "hoodie", "cap", "chain"},
        "outerwear_preference": 0.55,
        "accessory_preference": 0.55,
    },
    "Formal Event": {
        "target_formality": 4.6,
        "styles": {"formal", "business casual"},
        "prefer": {"formal", "oxford", "shirt", "trouser", "formal shoes", "loafer", "chelsea", "blazer", "belt", "watch"},
        "avoid": {"tee", "tshirt", "graphic", "cargo", "baggy", "running", "hoodie", "cap", "chain"},
        "outerwear_preference": 0.90,
        "accessory_preference": 0.75,
    },
}

WEATHER_PROFILES = {
    "Any Weather": {"target_warmth": None, "outerwear_bias": 0.0},
    "Hot": {"target_warmth": 3.0, "outerwear_bias": -18.0},
    "Warm": {"target_warmth": 4.2, "outerwear_bias": -6.0},
    "Cool": {"target_warmth": 6.0, "outerwear_bias": 8.0},
    "Cold": {"target_warmth": 8.0, "outerwear_bias": 22.0},
    "Rainy": {"target_warmth": 5.5, "outerwear_bias": 12.0},
}


COLOR_ALIASES = {
    "black": (10, 10, 10),
    "white": (245, 245, 240),
    "grey": (128, 128, 128),
    "gray": (128, 128, 128),
    "silver": (185, 185, 190),
    "beige": (214, 196, 158),
    "cream": (245, 235, 205),
    "brown": (118, 78, 48),
    "tan": (190, 150, 100),
    "navy": (22, 35, 70),
    "navy blue": (22, 35, 70),
    "dark blue": (25, 55, 105),
    "blue": (45, 95, 180),
    "light blue": (125, 180, 220),
    "olive": (100, 110, 45),
    "olive green": (100, 110, 45),
    "green": (55, 130, 75),
    "red": (185, 55, 55),
    "maroon": (110, 35, 50),
    "burgundy": (120, 35, 55),
    "pink": (210, 110, 145),
    "purple": (115, 75, 155),
    "orange": (215, 125, 45),
    "yellow": (220, 190, 55),
}


# ═════════════════════════════════════════════
# STORAGE
# ═════════════════════════════════════════════

def initialize_wardrobe() -> None:
    """Create the data folder and wardrobe file when necessary."""

    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    if not WARDROBE_FILE.exists():
        with WARDROBE_FILE.open("w", encoding="utf-8") as file:
            json.dump([], file, indent=4)


def get_wardrobe() -> list[dict]:
    """Load all clothing items from the wardrobe."""

    initialize_wardrobe()

    try:
        with WARDROBE_FILE.open("r", encoding="utf-8") as file:
            wardrobe = json.load(file)
        return wardrobe if isinstance(wardrobe, list) else []
    except (json.JSONDecodeError, FileNotFoundError, OSError):
        return []


def save_wardrobe(wardrobe: list[dict]) -> None:
    """Save the wardrobe to JSON using an atomic replace."""

    initialize_wardrobe()
    temporary = WARDROBE_FILE.with_suffix(".tmp")

    with temporary.open("w", encoding="utf-8") as file:
        json.dump(wardrobe, file, indent=4, ensure_ascii=False)

    temporary.replace(WARDROBE_FILE)


def _clean_text(value: str, *, maximum: int) -> str:
    value = re.sub(r"[\x00-\x1f\x7f]", " ", str(value))
    value = re.sub(r"\s+", " ", value).strip()
    return value[:maximum]


def add_to_wardrobe(item_name: str, category: str, color: str) -> dict:
    """Validate and add one clothing item."""

    if category not in VALID_CATEGORIES:
        raise ValueError(f"Unsupported wardrobe category: {category}")

    item_name = _clean_text(item_name, maximum=80)
    color = _clean_text(color, maximum=40)

    if not item_name or not color:
        raise ValueError("Item name and color are required.")

    wardrobe = get_wardrobe()
    existing_ids = [
        int(item.get("id", 0))
        for item in wardrobe
        if str(item.get("id", "")).isdigit()
    ]
    new_id = (max(existing_ids) if existing_ids else 0) + 1

    item = {
        "id": new_id,
        "name": item_name,
        "category": category,
        "color": color,
    }

    wardrobe.append(item)
    save_wardrobe(wardrobe)
    return item


def delete_item(item_id: int) -> bool:
    """Delete an item by ID and report whether anything changed."""

    wardrobe = get_wardrobe()
    updated = [item for item in wardrobe if item.get("id") != item_id]

    if len(updated) == len(wardrobe):
        return False

    save_wardrobe(updated)
    return True


def get_items_by_category(wardrobe: list[dict], category: str) -> list[dict]:
    return [item for item in wardrobe if item.get("category") == category]


# ═════════════════════════════════════════════
# ITEM UNDERSTANDING
# ═════════════════════════════════════════════

def _contains(name: str, keywords) -> bool:
    return any(keyword in name for keyword in keywords)


def infer_item_traits(item: dict) -> dict:
    """Infer lightweight fashion metadata from a wardrobe item's text.

    Users do not have to manually tag every piece. The inference is deterministic
    and transparent enough for a college-project recommender while remaining easy
    to replace with richer metadata or a trained model later.
    """

    name = str(item.get("name", "")).lower().strip()
    category = item.get("category", "")

    formality = {
        "Top": 1.5,
        "Bottom": 1.6,
        "Footwear": 1.5,
        "Outerwear": 1.9,
        "Accessory": 2.0,
    }.get(category, 1.5)

    formality_rules = (
        ({"formal"}, 2.0),
        ({"oxford"}, 1.7),
        ({"blazer"}, 1.7),
        ({"shirt"}, 1.1),
        ({"trouser"}, 1.4),
        ({"chinos"}, 0.9),
        ({"loafer"}, 1.4),
        ({"chelsea"}, 1.0),
        ({"watch", "belt"}, 0.7),
        ({"polo"}, 0.5),
        ({"linen"}, 0.2),
        ({"sneaker"}, -0.3),
        ({"running"}, -1.0),
        ({"cargo"}, -0.8),
        ({"baggy"}, -0.7),
        ({"graphic"}, -0.8),
        ({"hoodie"}, -0.8),
        ({"cap"}, -0.7),
        ({"tee", "tshirt"}, -0.7),
    )

    for keywords, adjustment in formality_rules:
        if _contains(name, keywords):
            formality += adjustment

    formality = max(0.0, min(5.0, formality))

    styles: set[str] = set()

    if _contains(name, {"formal", "oxford", "blazer", "trouser", "formal shoes", "loafer", "belt"}):
        styles.update({"formal", "business casual"})
    if _contains(name, {"shirt", "polo", "chinos", "loafer", "chelsea", "overshirt", "linen", "watch"}):
        styles.update({"smart casual", "preppy"})
    if _contains(name, {"tee", "tshirt", "jeans", "sneaker", "denim", "hoodie"}):
        styles.add("casual")
    if _contains(name, {"graphic", "oversized", "cargo", "baggy", "bomber", "chain", "cap"}):
        styles.add("streetwear")
    if _contains(name, {"running", "sport", "track", "jersey"}):
        styles.add("sporty")

    color_name = str(item.get("color", "")).lower()
    if _contains(color_name, {"black", "white", "grey", "gray", "beige", "navy", "brown", "cream"}) and "graphic" not in name:
        styles.add("minimal")

    if not styles:
        styles.add("casual")

    warmth = {
        "Top": 1.0,
        "Bottom": 1.4,
        "Footwear": 0.8,
        "Outerwear": 2.2,
        "Accessory": 0.1,
    }.get(category, 1.0)

    if _contains(name, {"hoodie"}):
        warmth += 1.3
    if _contains(name, {"jacket", "bomber"}):
        warmth += 0.9
    if _contains(name, {"blazer"}):
        warmth += 0.7
    if _contains(name, {"overshirt"}):
        warmth += 0.4
    if _contains(name, {"linen"}):
        warmth -= 0.5
    if _contains(name, {"boots", "chelsea"}):
        warmth += 0.4

    rain_score = 0.55
    if _contains(name, {"boots", "chelsea", "jacket", "bomber", "overshirt"}):
        rain_score += 0.18
    if _contains(name, {"linen", "running"}):
        rain_score -= 0.12

    return {
        "formality": formality,
        "styles": styles,
        "warmth": max(0.0, warmth),
        "rain_score": max(0.0, min(1.0, rain_score)),
        "name": name,
    }


# ═════════════════════════════════════════════
# COLOR COMPATIBILITY
# ═════════════════════════════════════════════

def color_to_rgb(color_name: str) -> tuple[int, int, int] | None:
    """Resolve common wardrobe color names to RGB."""

    normalised = re.sub(r"\s+", " ", str(color_name).strip().lower())

    if normalised in COLOR_ALIASES:
        return COLOR_ALIASES[normalised]

    # Prefer the most specific alias contained in a descriptive value such as
    # "washed dark blue".
    for alias in sorted(COLOR_ALIASES, key=len, reverse=True):
        if alias in normalised:
            return COLOR_ALIASES[alias]

    try:
        return ImageColor.getrgb(normalised.replace(" ", ""))
    except (ValueError, TypeError):
        return None


def _rgb_hsv(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    h, s, v = colorsys.rgb_to_hsv(*(channel / 255 for channel in rgb))
    return h * 360.0, s, v


def _hue_distance(a: float, b: float) -> float:
    difference = abs(a - b) % 360.0
    return min(difference, 360.0 - difference)


def score_color_pair(color_a: str, color_b: str) -> float:
    """Score two named garment colors on a 0-100 compatibility scale."""

    rgb_a = color_to_rgb(color_a)
    rgb_b = color_to_rgb(color_b)

    if rgb_a is None or rgb_b is None:
        return 78.0

    hue_a, sat_a, val_a = _rgb_hsv(rgb_a)
    hue_b, sat_b, val_b = _rgb_hsv(rgb_b)

    neutral_a = sat_a < 0.18
    neutral_b = sat_b < 0.18

    if neutral_a and neutral_b:
        value_delta = abs(val_a - val_b)
        return 94.0 if value_delta >= 0.16 else 88.0

    if neutral_a or neutral_b:
        return 93.0

    hue_delta = _hue_distance(hue_a, hue_b)

    if hue_delta <= 38:
        score = 93.0  # analogous
    elif 105 <= hue_delta <= 135:
        score = 90.0  # triadic-ish
    elif 145 <= hue_delta <= 180:
        score = 92.0  # split/complementary
    elif hue_delta <= 62:
        score = 82.0
    else:
        score = 72.0

    score -= max(0.0, abs(sat_a - sat_b) - 0.50) * 14.0
    return max(58.0, min(96.0, score))


def score_color_cohesion(items: list[dict]) -> float:
    """Score the color relationships across all selected pieces."""

    if len(items) < 2:
        return 85.0

    category_weights = {
        "Top": 1.0,
        "Bottom": 1.0,
        "Footwear": 0.85,
        "Outerwear": 0.85,
        "Accessory": 0.35,
    }

    total = 0.0
    weight_total = 0.0

    for item_a, item_b in combinations(items, 2):
        pair_weight = (
            category_weights.get(item_a.get("category"), 0.7)
            * category_weights.get(item_b.get("category"), 0.7)
        )
        total += score_color_pair(item_a.get("color", ""), item_b.get("color", "")) * pair_weight
        weight_total += pair_weight

    return total / weight_total if weight_total else 80.0


# ═════════════════════════════════════════════
# OUTFIT SCORING
# ═════════════════════════════════════════════

def _occasion_score(items: list[dict], occasion: str) -> float:
    profile = OCCASION_PROFILES.get(occasion, OCCASION_PROFILES["Casual Outing"])
    core_items = [item for item in items if item.get("category") != "Accessory"]
    traits = [infer_item_traits(item) for item in core_items]

    category_weight = {
        "Top": 1.1,
        "Bottom": 1.0,
        "Footwear": 1.0,
        "Outerwear": 0.75,
    }
    weighted_formality = sum(
        trait["formality"] * category_weight.get(item.get("category"), 0.7)
        for item, trait in zip(core_items, traits)
    )
    weight_total = sum(
        category_weight.get(item.get("category"), 0.7)
        for item in core_items
    )
    average_formality = weighted_formality / max(weight_total, 1.0)
    formality_delta = abs(average_formality - profile["target_formality"])
    formality_score = max(35.0, 100.0 - formality_delta * 21.0)

    style_hits = sum(
        len(trait["styles"] & profile["styles"]) > 0
        for trait in traits
    )
    style_score = 62.0 + 38.0 * (style_hits / max(len(traits), 1))

    combined_name = " | ".join(str(item.get("name", "")).lower() for item in items)
    prefer_hits = sum(keyword in combined_name for keyword in profile["prefer"])
    avoid_hits = sum(keyword in combined_name for keyword in profile["avoid"])
    context_score = 76.0 + min(18.0, prefer_hits * 3.0) - min(38.0, avoid_hits * 8.0)

    has_outerwear = any(item.get("category") == "Outerwear" for item in items)
    has_accessory = any(item.get("category") == "Accessory" for item in items)

    if has_outerwear:
        context_score += (profile["outerwear_preference"] - 0.35) * 11.0
    elif profile["outerwear_preference"] >= 0.75:
        context_score -= 9.0

    if has_accessory:
        context_score += (profile["accessory_preference"] - 0.35) * 9.0
    elif profile["accessory_preference"] >= 0.70:
        context_score -= 6.0

    # Strong contextual penalties prevent a random-looking "formal" result.
    top_name = next((str(i.get("name", "")).lower() for i in items if i.get("category") == "Top"), "")
    bottom_name = next((str(i.get("name", "")).lower() for i in items if i.get("category") == "Bottom"), "")
    footwear_name = next((str(i.get("name", "")).lower() for i in items if i.get("category") == "Footwear"), "")

    if occasion == "Interview":
        if not _contains(top_name, {"shirt", "polo"}):
            context_score -= 24.0
        if _contains(bottom_name, {"cargo", "baggy"}):
            context_score -= 26.0
        if _contains(footwear_name, {"running"}):
            context_score -= 28.0
    elif occasion == "Formal Event":
        if "shirt" not in top_name:
            context_score -= 38.0
        if not _contains(bottom_name, {"trouser", "chinos"}):
            context_score -= 35.0
        if not _contains(footwear_name, {"formal", "loafer", "chelsea"}):
            context_score -= 35.0

    return max(
        20.0,
        min(100.0, 0.58 * formality_score + 0.24 * style_score + 0.18 * context_score),
    )


def _weather_score(items: list[dict], weather: str) -> float:
    profile = WEATHER_PROFILES.get(weather, WEATHER_PROFILES["Any Weather"])

    if profile["target_warmth"] is None:
        return 90.0

    traits = [infer_item_traits(item) for item in items]
    total_warmth = sum(trait["warmth"] for trait in traits)
    distance = abs(total_warmth - profile["target_warmth"])
    score = 100.0 - distance * 12.0

    has_outerwear = any(item.get("category") == "Outerwear" for item in items)
    if has_outerwear:
        score += profile["outerwear_bias"]
    elif profile["outerwear_bias"] > 10:
        score -= profile["outerwear_bias"] * 0.75

    if weather == "Rainy":
        rain_scores = [trait["rain_score"] for trait in traits]
        score = 0.72 * score + 28.0 * (sum(rain_scores) / max(len(rain_scores), 1))

    return max(25.0, min(100.0, score))


def _style_cohesion_score(items: list[dict], occasion: str) -> float:
    profile = OCCASION_PROFILES.get(occasion, OCCASION_PROFILES["Casual Outing"])
    style_sets = [infer_item_traits(item)["styles"] for item in items]

    if len(style_sets) < 2:
        return 85.0

    pair_scores = []
    for styles_a, styles_b in combinations(style_sets, 2):
        union = styles_a | styles_b
        overlap = styles_a & styles_b
        if not union:
            pair_scores.append(70.0)
        else:
            pair_scores.append(68.0 + 30.0 * (len(overlap) / len(union)))

    base = sum(pair_scores) / len(pair_scores)
    desired_hits = sum(bool(styles & profile["styles"]) for styles in style_sets)
    base += 6.0 * desired_hits / len(style_sets)

    return max(55.0, min(100.0, base))


def score_outfit_candidate(
    items: list[dict],
    occasion: str,
    weather: str = "Any Weather",
) -> dict[str, float]:
    """Return the explainable component scores for one candidate outfit."""

    occasion_score = _occasion_score(items, occasion)
    color_score = score_color_cohesion(items)
    weather_score = _weather_score(items, weather)
    cohesion_score = _style_cohesion_score(items, occasion)

    total = (
        0.42 * occasion_score
        + 0.28 * color_score
        + 0.18 * weather_score
        + 0.12 * cohesion_score
    )

    return {
        "occasion": round(occasion_score, 1),
        "color": round(color_score, 1),
        "weather": round(weather_score, 1),
        "cohesion": round(cohesion_score, 1),
        "total": round(total, 1),
    }


def _candidate_items(candidate) -> list[dict]:
    return [item for item in candidate if item is not None]


def _build_reason(occasion: str, weather: str, breakdown: dict[str, float]) -> str:
    context = f" for {occasion}"
    if weather != "Any Weather":
        context += f" in {weather.lower()} weather"

    strongest = max(
        ("occasion match", breakdown["occasion"]),
        ("color compatibility", breakdown["color"]),
        ("weather suitability", breakdown["weather"]),
        ("style cohesion", breakdown["cohesion"]),
        key=lambda item: item[1],
    )[0]

    return (
        f"FIT404 ranked this combination {breakdown['total']:.0f}/100{context}. "
        f"Its strongest signal is {strongest}, while the final score also weighs "
        "occasion, palette, weather and style cohesion together."
    )


def generate_outfit(
    wardrobe: list[dict],
    occasion: str,
    weather: str = "Any Weather",
    *,
    rng=None,
) -> dict | None:
    """Generate a context-aware outfit from the user's wardrobe.

    V2 evaluates every valid core combination plus optional outerwear/accessories,
    ranks candidates, then samples only from the near-best pool. This preserves a
    little variety without allowing a weak random combination to win.
    """

    tops = get_items_by_category(wardrobe, "Top")
    bottoms = get_items_by_category(wardrobe, "Bottom")
    footwear = get_items_by_category(wardrobe, "Footwear")
    outerwear = get_items_by_category(wardrobe, "Outerwear")
    accessories = get_items_by_category(wardrobe, "Accessory")

    if not tops or not bottoms or not footwear:
        return None

    occasion = occasion if occasion in OCCASION_PROFILES else "Casual Outing"
    weather = weather if weather in WEATHER_PROFILES else "Any Weather"

    outer_options = [None, *outerwear]
    accessory_options = [None, *accessories]

    ranked_candidates = []

    for candidate in product(
        tops,
        bottoms,
        footwear,
        outer_options,
        accessory_options,
    ):
        items = _candidate_items(candidate)
        breakdown = score_outfit_candidate(items, occasion, weather)
        ranked_candidates.append((breakdown["total"], candidate, breakdown))

    ranked_candidates.sort(key=lambda row: row[0], reverse=True)
    best_score = ranked_candidates[0][0]

    # Keep variation tightly constrained to recommendations close to the best fit.
    near_best = [
        row for row in ranked_candidates[:18]
        if row[0] >= best_score - 3.5
    ]

    random_source = rng if rng is not None else random
    if len(near_best) == 1:
        selected_score, selected, breakdown = near_best[0]
    else:
        floor = min(row[0] for row in near_best)
        weights = [(row[0] - floor + 1.0) ** 2 for row in near_best]
        selected_score, selected, breakdown = random_source.choices(
            near_best,
            weights=weights,
            k=1,
        )[0]

    top, bottom, shoes, layer, accessory = selected

    outfit = {
        "Top": top,
        "Bottom": bottom,
        "Footwear": shoes,
    }

    if layer is not None:
        outfit["Outerwear"] = layer
    if accessory is not None:
        outfit["Accessory"] = accessory

    outfit["match_score"] = int(round(selected_score))
    outfit["score_breakdown"] = breakdown
    outfit["reason"] = _build_reason(occasion, weather, breakdown)

    return outfit
