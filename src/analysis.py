"""Core image-analysis logic for FIT404.

The scoring functions in this module are intentionally explainable heuristics.
CLIP is used only for zero-shot style labelling; the visual-quality scores do
not depend on a remote API or on CLIP being available.
"""

from __future__ import annotations

import colorsys
import logging
import os

# Keep Hugging Face/Transformers console output quiet without hiding real errors.
# The public CLIP model works without a token; authentication only raises rate limits.
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")


class _HFAuthNoiseFilter(logging.Filter):
    """Hide only the non-fatal unauthenticated Hub notice."""

    def filter(self, record):
        return "unauthenticated requests to the HF Hub" not in record.getMessage()


for _logger_name in ("huggingface_hub", "huggingface_hub.utils._http"):
    logging.getLogger(_logger_name).addFilter(_HFAuthNoiseFilter())

from collections import Counter
from functools import lru_cache
from math import exp

import numpy as np
from PIL import Image


# ═════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════

CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"

STYLE_LABELS = {
    "Formal": (
        "a formal outfit with a suit, blazer, dress shirt, tailored trousers, "
        "formal shoes or other structured formal clothing"
    ),
    "Business Casual": (
        "a business casual outfit with a collared shirt, chinos or tailored "
        "trousers, loafers, clean shoes or a light blazer"
    ),
    "Smart Casual": (
        "a smart casual outfit with a neat shirt, polo, chinos, jeans, overshirt, "
        "blazer or clean semi-formal clothing"
    ),
    "Casual": (
        "a casual everyday outfit with a t-shirt, jeans, casual shirt, sneakers "
        "or relaxed everyday clothing"
    ),
    "Streetwear": (
        "a streetwear outfit with oversized clothing, graphic t-shirts, hoodies, "
        "cargo pants, baggy jeans, sneakers or urban fashion"
    ),
    "Sporty": (
        "a sporty athletic outfit with sportswear, track pants, running shoes, "
        "jersey, gym clothing or athletic clothing"
    ),
    "Minimal": (
        "a minimalist outfit with simple clean silhouettes, neutral colors, "
        "limited branding and very few visual elements"
    ),
    "Preppy": (
        "a preppy outfit with polos, Oxford shirts, chinos, sweaters, loafers "
        "or clean collegiate styling"
    ),
    "Vintage": (
        "a vintage inspired outfit with retro clothing, classic denim, heritage "
        "pieces, muted tones or an older fashion aesthetic"
    ),
    "Grunge": (
        "a grunge inspired outfit with dark layers, loose clothing, denim, boots, "
        "graphic pieces or an intentionally rough alternative aesthetic"
    ),
}


# ═════════════════════════════════════════════
# MODEL LOADING
# ═════════════════════════════════════════════

@lru_cache(maxsize=1)
def load_style_model():
    """Load CLIP lazily and cache it for the life of the process.

    Importing ``transformers`` here instead of at module import time keeps the
    non-AI analysis and test suite usable on machines where the optional model
    stack has not been installed yet.
    """

    try:
        from transformers import CLIPModel, CLIPProcessor
        from transformers.utils import logging as transformers_logging
        transformers_logging.disable_progress_bar()
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "CLIP style analysis requires the 'transformers' package."
        ) from exc

    processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)
    model = CLIPModel.from_pretrained(CLIP_MODEL_NAME)
    model.eval()

    return processor, model


# ═════════════════════════════════════════════
# OUTFIT REGION
# ═════════════════════════════════════════════

def get_outfit_region(image: Image.Image) -> Image.Image:
    """Crop toward the body/clothing area without a segmentation model.

    This is deliberately lightweight. It reduces face/hair/background influence
    for typical portrait or mirror-selfie framing while keeping FIT404 free of a
    second heavyweight vision model.
    """

    width, height = image.size

    left = int(width * 0.08)
    right = int(width * 0.92)
    top = int(height * 0.30)
    bottom = height

    return image.crop((left, top, right, bottom))


# ═════════════════════════════════════════════
# COLOR UTILITIES
# ═════════════════════════════════════════════

def rgb_to_hex(rgb) -> str:
    """Convert an RGB tuple to HEX."""

    return "#{:02x}{:02x}{:02x}".format(*rgb)


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a HEX color to RGB."""

    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def hex_to_hsv(hex_color: str) -> tuple[float, float, float]:
    """Return hue (degrees), saturation and value for a HEX color."""

    r, g, b = hex_to_rgb(hex_color)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return h * 360.0, s, v


def calculate_brightness(hex_color: str) -> float:
    """Calculate perceived luminance on a 0-255 scale."""

    r, g, b = hex_to_rgb(hex_color)
    return 0.299 * r + 0.587 * g + 0.114 * b


def circular_hue_distance(hue_a: float, hue_b: float) -> float:
    """Smallest distance between two hue angles in degrees (0-180)."""

    delta = abs(hue_a - hue_b) % 360.0
    return min(delta, 360.0 - delta)


def _normalised_weights(
    count: int,
    percentages: list[float] | tuple[float, ...] | None,
) -> list[float]:
    if count <= 0:
        return []

    if percentages and len(percentages) >= count:
        raw = [max(0.0, float(value)) for value in percentages[:count]]
        total = sum(raw)
        if total > 0:
            return [value / total for value in raw]

    return [1.0 / count] * count


def _gaussian_score(value: float, center: float, spread: float) -> float:
    return exp(-((value - center) ** 2) / (2 * spread**2))


# ═════════════════════════════════════════════
# DOMINANT COLOR EXTRACTION
# ═════════════════════════════════════════════

def extract_palette(
    image: Image.Image,
    number_of_colors: int = 5,
) -> tuple[list[str], list[float]]:
    """Extract dominant outfit colors and their approximate image share."""

    outfit_image = get_outfit_region(image).copy()
    outfit_image.thumbnail((300, 300), Image.Resampling.LANCZOS)

    image_array = np.asarray(outfit_image.convert("RGB"))
    pixels = image_array.reshape(-1, 3)

    if len(pixels) == 0:
        return [], []

    # 32-value buckets keep the palette stable without bringing in k-means.
    quantized_pixels = (pixels // 32) * 32
    color_counts = Counter(map(tuple, quantized_pixels.tolist()))
    total_pixels = len(pixels)

    colors: list[str] = []
    percentages: list[float] = []

    for rgb, count in color_counts.most_common(max(1, number_of_colors)):
        adjusted_rgb = tuple(min(int(value) + 16, 255) for value in rgb)
        colors.append(rgb_to_hex(adjusted_rgb))
        percentages.append(round((count / total_pixels) * 100, 1))

    return colors, percentages


# ═════════════════════════════════════════════
# COLOR HARMONY V2
# ═════════════════════════════════════════════

def _pair_harmony(color_a: str, color_b: str) -> float:
    hue_a, sat_a, _ = hex_to_hsv(color_a)
    hue_b, sat_b, _ = hex_to_hsv(color_b)

    brightness_a = calculate_brightness(color_a)
    brightness_b = calculate_brightness(color_b)
    brightness_delta = abs(brightness_a - brightness_b)

    neutral_a = sat_a < 0.16
    neutral_b = sat_b < 0.16

    # Neutrals are deliberately forgiving: black/white/grey combinations and
    # neutral + accent palettes are common, coherent outfit strategies.
    if neutral_a and neutral_b:
        relation_score = 92.0 if brightness_delta >= 25 else 86.0
    elif neutral_a or neutral_b:
        relation_score = 91.0
    else:
        hue_delta = circular_hue_distance(hue_a, hue_b)

        # Reward several established palette relationships instead of assuming
        # that only low contrast or only complementary colors are harmonious.
        analogous = 0.98 * _gaussian_score(hue_delta, 25, 26)
        triadic = 0.94 * _gaussian_score(hue_delta, 120, 23)
        split_complementary = 0.91 * _gaussian_score(hue_delta, 150, 20)
        complementary = 1.00 * _gaussian_score(hue_delta, 180, 18)

        relation_strength = max(
            analogous,
            triadic,
            split_complementary,
            complementary,
        )
        relation_score = 58.0 + 39.0 * relation_strength

        # Extremely different saturation levels can make two strong chromatic
        # colors read less cohesive even if their hues are theoretically related.
        relation_score -= max(0.0, abs(sat_a - sat_b) - 0.45) * 16.0

    # Contrast should exist, but maximum black-vs-white contrast is not required.
    if brightness_delta < 12:
        contrast_score = 78.0
    elif brightness_delta <= 105:
        contrast_score = 94.0
    elif brightness_delta <= 165:
        contrast_score = 87.0
    else:
        contrast_score = 80.0

    return 0.78 * relation_score + 0.22 * contrast_score


def calculate_color_harmony(
    palette: list[str],
    percentages: list[float] | tuple[float, ...] | None = None,
) -> int:
    """Estimate color harmony from hue, saturation and luminance relationships.

    ``percentages`` is optional for backwards compatibility. When supplied, the
    dominant colors contribute more to the final score than tiny accent colors.
    """

    if not palette:
        return 0

    if len(palette) == 1:
        _, saturation, _ = hex_to_hsv(palette[0])
        return 88 if saturation < 0.16 else 84

    weights = _normalised_weights(len(palette), percentages)

    weighted_total = 0.0
    pair_weight_total = 0.0

    for i in range(len(palette)):
        for j in range(i + 1, len(palette)):
            pair_weight = weights[i] * weights[j]
            weighted_total += _pair_harmony(palette[i], palette[j]) * pair_weight
            pair_weight_total += pair_weight

    score = weighted_total / pair_weight_total if pair_weight_total else 82.0

    saturations = [hex_to_hsv(color)[1] for color in palette]
    neutral_share = sum(
        weight
        for saturation, weight in zip(saturations, weights)
        if saturation < 0.16
    )
    vivid_share = sum(
        weight
        for saturation, weight in zip(saturations, weights)
        if saturation > 0.68
    )
    chromatic_count = sum(saturation >= 0.16 for saturation in saturations)
    dominant_share = max(weights)

    # A neutral anchor often helps an outfit; excessive single-color dominance is
    # only lightly penalised because monochrome outfits can still work very well.
    score += min(3.0, neutral_share * 4.0)
    score -= max(0.0, dominant_share - 0.78) * 18.0

    # Three or more highly saturated colors can technically form a hue scheme yet
    # still compete strongly in clothing. This keeps V2 from over-rewarding every
    # mathematically valid triadic/complementary palette.
    if chromatic_count >= 3 and vivid_share > 0.65:
        score -= (vivid_share - 0.65) * 20.0
        score -= (chromatic_count - 2) * 2.0

    return int(round(max(45.0, min(98.0, score))))


# ═════════════════════════════════════════════
# VISUAL BALANCE V2
# ═════════════════════════════════════════════

def _palette_distribution_score(
    palette: list[str],
    percentages: list[float] | tuple[float, ...] | None,
) -> float:
    if not palette:
        return 0.0

    weights = _normalised_weights(len(palette), percentages)
    dominant_share = max(weights)

    if len(weights) == 1:
        diversity_score = 90.0
    else:
        entropy = -sum(weight * np.log(weight) for weight in weights if weight > 0)
        effective_colors = float(np.exp(entropy))
        # 2-3 effective dominant colors is a useful centre, but intentionally
        # keep monochrome and richer palettes in a respectable range.
        diversity_score = 96.0 - abs(effective_colors - 2.7) * 7.0

    if dominant_share <= 0.72:
        dominance_score = 96.0
    else:
        dominance_score = 96.0 - (dominant_share - 0.72) * 38.0

    # Extremely flat palettes can be coherent, so there is no harsh penalty.
    if dominant_share < 0.24:
        dominance_score -= (0.24 - dominant_share) * 30.0

    return max(60.0, min(98.0, 0.55 * diversity_score + 0.45 * dominance_score))


def _spatial_balance_score(image: Image.Image) -> float:
    outfit = get_outfit_region(image).copy()
    outfit.thumbnail((240, 320), Image.Resampling.BILINEAR)

    array = np.asarray(outfit.convert("RGB"), dtype=np.float32)
    if array.size == 0 or array.shape[1] < 4:
        return 80.0

    luminance = (
        0.299 * array[:, :, 0]
        + 0.587 * array[:, :, 1]
        + 0.114 * array[:, :, 2]
    )
    saturation_proxy = array.max(axis=2) - array.min(axis=2)

    midpoint = array.shape[1] // 2
    left_lum = luminance[:, :midpoint]
    right_lum = luminance[:, midpoint:]
    left_sat = saturation_proxy[:, :midpoint]
    right_sat = saturation_proxy[:, midpoint:]

    luminance_difference = abs(float(left_lum.mean()) - float(right_lum.mean())) / 255.0
    saturation_difference = abs(float(left_sat.mean()) - float(right_sat.mean())) / 255.0

    def activity(region: np.ndarray) -> float:
        if min(region.shape[:2]) < 2:
            return float(region.std())
        horizontal = np.abs(np.diff(region, axis=1)).mean()
        vertical = np.abs(np.diff(region, axis=0)).mean()
        return float(region.std() + 0.55 * horizontal + 0.55 * vertical)

    left_activity = activity(left_lum)
    right_activity = activity(right_lum)
    activity_difference = abs(left_activity - right_activity) / max(
        left_activity,
        right_activity,
        1.0,
    )

    score = (
        100.0
        - 34.0 * luminance_difference
        - 24.0 * saturation_difference
        - 34.0 * activity_difference
    )

    return max(55.0, min(99.0, score))


def calculate_visual_balance(
    palette: list[str],
    percentages: list[float] | tuple[float, ...] | None = None,
    image: Image.Image | None = None,
) -> int:
    """Estimate visual balance from color distribution and left/right activity.

    Older FIT404 versions only counted the number of palette colors. V2 keeps an
    explainable palette component and, when an image is supplied, also compares
    spatial luminance/saturation/detail across the outfit crop.
    """

    if not palette:
        return 0

    distribution = _palette_distribution_score(palette, percentages)

    if image is None:
        return int(round(distribution))

    spatial = _spatial_balance_score(image)
    score = 0.55 * distribution + 0.45 * spatial

    return int(round(max(55.0, min(98.0, score))))


# ═════════════════════════════════════════════
# AI STYLE CLASSIFICATION
# ═════════════════════════════════════════════

def classify_style(image: Image.Image):
    """Classify an outfit using CLIP zero-shot image-text similarity.

    The returned confidence is a *relative style match among FIT404's prompts*,
    not a calibrated probability that the outfit objectively belongs to a class.
    """

    try:
        import torch
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("CLIP style analysis requires the 'torch' package.") from exc

    processor, model = load_style_model()
    outfit_image = get_outfit_region(image)

    style_names = list(STYLE_LABELS.keys())
    style_descriptions = list(STYLE_LABELS.values())

    inputs = processor(
        text=style_descriptions,
        images=outfit_image,
        return_tensors="pt",
        padding=True,
    )

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits_per_image[0]
    probabilities = torch.softmax(logits, dim=0).cpu().numpy()

    best_index = int(np.argmax(probabilities))
    style = style_names[best_index]
    confidence = float(probabilities[best_index])

    style_scores = {
        name: round(float(probability) * 100, 1)
        for name, probability in zip(style_names, probabilities)
    }

    return style, confidence, style_scores


# ═════════════════════════════════════════════
# COLOR PROFILE
# ═════════════════════════════════════════════

def get_color_profile(
    palette: list[str],
    percentages: list[float] | tuple[float, ...] | None = None,
) -> str:
    """Describe the overall luminance and saturation direction of the palette."""

    if not palette:
        return "No dominant colors detected."

    weights = _normalised_weights(len(palette), percentages)
    brightness = sum(
        calculate_brightness(color) * weight
        for color, weight in zip(palette, weights)
    )
    saturation = sum(
        hex_to_hsv(color)[1] * weight
        for color, weight in zip(palette, weights)
    )

    if brightness < 75:
        tone = "Dark"
    elif brightness > 180:
        tone = "Light"
    else:
        tone = "Mid-tone"

    if saturation < 0.20:
        character = "neutral"
    elif saturation < 0.48:
        character = "muted"
    else:
        character = "vivid"

    return f"{tone} · {character} palette"


# ═════════════════════════════════════════════
# FEEDBACK
# ═════════════════════════════════════════════

def generate_feedback(
    style: str,
    palette: list[str],
    color_harmony: int,
    visual_balance: int,
) -> list[str]:
    """Generate concise styling observations from the current analysis."""

    feedback: list[str] = []

    if color_harmony >= 88:
        feedback.append("The dominant colors form a very cohesive palette.")
    elif color_harmony >= 76:
        feedback.append("The color relationships are cohesive with controlled contrast.")
    elif color_harmony >= 64:
        feedback.append("The palette mixes workable colors but carries stronger contrast.")
    else:
        feedback.append(
            "A neutral anchor or one repeated color could make the palette feel more connected."
        )

    if visual_balance >= 88:
        feedback.append("Color weight and left-right visual activity are very well balanced.")
    elif visual_balance >= 76:
        feedback.append("The outfit reads as visually balanced without feeling overly uniform.")
    else:
        feedback.append(
            "One side or color group is carrying more visual weight; simplifying one element could help."
        )

    style_feedback = {
        "Formal": "The outfit reads structured and strongly formal.",
        "Business Casual": "The outfit reads polished without becoming fully formal.",
        "Smart Casual": "The outfit balances relaxed pieces with a cleaner, polished direction.",
        "Streetwear": "The outfit has a relaxed urban/streetwear character.",
        "Sporty": "The outfit has a clear athletic or performance-inspired character.",
        "Minimal": "The outfit follows a clean, understated visual direction.",
        "Preppy": "The outfit leans clean and collegiate with a polished everyday feel.",
        "Vintage": "The outfit carries a noticeable retro or heritage-inspired direction.",
        "Grunge": "The outfit reads intentionally relaxed, layered and alternative.",
        "Casual": "The outfit has a relaxed everyday style.",
    }

    feedback.append(
        style_feedback.get(
            style,
            "Style classification is unavailable, but the color analysis remains active.",
        )
    )

    return feedback


# ═════════════════════════════════════════════
# COMPLETE ANALYSIS
# ═════════════════════════════════════════════

def analyze_outfit(
    image: Image.Image,
    *,
    include_style: bool = True,
) -> dict:
    """Run the complete FIT404 V2 analysis."""

    palette, palette_percentages = extract_palette(image)

    color_harmony = calculate_color_harmony(
        palette,
        palette_percentages,
    )
    visual_balance = calculate_visual_balance(
        palette,
        palette_percentages,
        image=image,
    )
    color_profile = get_color_profile(
        palette,
        palette_percentages,
    )

    if include_style:
        try:
            style, style_confidence, style_scores = classify_style(image)
        except Exception:
            # FIT404 still provides its explainable image analysis if CLIP is not
            # installed, cannot download, or cannot load on the current machine.
            style = "Style unavailable"
            style_confidence = 0.0
            style_scores = {}
    else:
        style = "Style analysis skipped"
        style_confidence = 0.0
        style_scores = {}

    feedback = generate_feedback(
        style,
        palette,
        color_harmony,
        visual_balance,
    )

    overall_score = int(round(0.58 * color_harmony + 0.42 * visual_balance))

    return {
        "palette": palette,
        "palette_percentages": palette_percentages,
        "color_harmony": color_harmony,
        "visual_balance": visual_balance,
        "overall_score": overall_score,
        "style": style,
        "style_confidence": style_confidence,
        "style_scores": style_scores,
        "color_profile": color_profile,
        "feedback": feedback,
        "detected_items": [],
        "analysis_version": "2.0",
    }
