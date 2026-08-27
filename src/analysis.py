from collections import Counter
from functools import lru_cache

from PIL import Image
import numpy as np
import torch

from transformers import CLIPModel, CLIPProcessor


# ═════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════

CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"

STYLE_LABELS = {
    "Formal": (
        "a formal outfit with a suit, blazer, dress shirt, "
        "tie, formal trousers or formal clothing"
    ),

    "Smart Casual": (
        "a smart casual outfit with a shirt, chinos, blazer, "
        "polo shirt or neat semi-formal clothing"
    ),

    "Casual": (
        "a casual everyday outfit with a t-shirt, jeans, "
        "casual shirt or simple everyday clothing"
    ),

    "Streetwear": (
        "a streetwear outfit with oversized clothing, hoodies, "
        "cargo pants, sneakers or urban fashion"
    ),

    "Sporty": (
        "a sporty athletic outfit with sportswear, track pants, "
        "jersey, gym clothing or athletic clothing"
    ),

    "Minimal": (
        "a minimalist outfit with simple clean clothing, "
        "neutral colors and very few visual elements"
    ),
}


# ═════════════════════════════════════════════
# MODEL LOADING
# ═════════════════════════════════════════════

@lru_cache(maxsize=1)
def load_style_model():
    """
    Load CLIP only once.

    The model is downloaded the first time FIT404
    uses style analysis and is then cached locally.
    """

    processor = CLIPProcessor.from_pretrained(
        CLIP_MODEL_NAME
    )

    model = CLIPModel.from_pretrained(
        CLIP_MODEL_NAME
    )

    model.eval()

    return processor, model


# ═════════════════════════════════════════════
# OUTFIT REGION
# ═════════════════════════════════════════════

def get_outfit_region(image):
    """
    Crop the image toward the clothing/body region.

    This reduces the influence of:
    - background
    - hair
    - face

    It is intentionally simple so FIT404 does not
    depend on another segmentation model yet.
    """

    width, height = image.size

    left = int(width * 0.08)
    right = int(width * 0.92)

    top = int(height * 0.30)
    bottom = height

    return image.crop(
        (
            left,
            top,
            right,
            bottom,
        )
    )


# ═════════════════════════════════════════════
# COLOR UTILITIES
# ═════════════════════════════════════════════

def rgb_to_hex(rgb):
    """Convert RGB tuple to HEX."""

    return "#{:02x}{:02x}{:02x}".format(
        *rgb
    )


def hex_to_rgb(hex_color):
    """Convert HEX color to RGB."""

    hex_color = hex_color.lstrip("#")

    return tuple(
        int(
            hex_color[i:i + 2],
            16,
        )
        for i in (0, 2, 4)
    )


def calculate_brightness(hex_color):
    """
    Calculate perceived color brightness.
    """

    r, g, b = hex_to_rgb(
        hex_color
    )

    return (
        0.299 * r
        + 0.587 * g
        + 0.114 * b
    )


# ═════════════════════════════════════════════
# DOMINANT COLOR EXTRACTION
# ═════════════════════════════════════════════

def extract_palette(image, number_of_colors=5):
    """
    Extract dominant outfit colors and their approximate share.
    """

    outfit_image = get_outfit_region(image)

    outfit_image = outfit_image.copy()
    outfit_image.thumbnail((300, 300))

    image_array = np.asarray(
        outfit_image.convert("RGB")
    )

    pixels = image_array.reshape(-1, 3)

    quantized_pixels = (
        pixels // 32
    ) * 32

    color_counts = Counter(
        map(tuple, quantized_pixels.tolist())
    )

    total_pixels = len(pixels)

    colors = []
    percentages = []

    for rgb, count in color_counts.most_common(
        number_of_colors
    ):

        adjusted_rgb = tuple(
            min(int(value) + 16, 255)
            for value in rgb
        )

        colors.append(
            rgb_to_hex(adjusted_rgb)
        )

        percentage = (
            count / total_pixels
        ) * 100

        percentages.append(
            round(percentage, 1)
        )

    return colors, percentages


# ═════════════════════════════════════════════
# COLOR HARMONY
# ═════════════════════════════════════════════

def calculate_color_harmony(
    palette
):
    """
    Estimate color harmony from brightness
    relationships in the dominant palette.
    """

    if not palette:
        return 0

    brightness_values = [
        calculate_brightness(color)
        for color in palette
    ]

    brightness_range = (
        max(brightness_values)
        - min(brightness_values)
    )

    ideal_range = 70

    difference = abs(
        brightness_range
        - ideal_range
    )

    score = (
        92
        - difference * 0.35
    )

    return max(
        50,
        min(
            95,
            int(score),
        ),
    )


# ═════════════════════════════════════════════
# VISUAL BALANCE
# ═════════════════════════════════════════════

def calculate_visual_balance(
    palette
):
    """
    Estimate visual balance based on
    dominant color diversity.
    """

    if not palette:
        return 0

    unique_colors = len(
        set(palette)
    )

    score = 90

    if unique_colors > 3:

        score -= (
            unique_colors - 3
        ) * 3

    return max(
        60,
        min(
            95,
            score,
        ),
    )


# ═════════════════════════════════════════════
# AI STYLE CLASSIFICATION
# ═════════════════════════════════════════════

def classify_style(image):
    """
    Classify the outfit using CLIP zero-shot
    image-text similarity.

    Returns:
        style name
        confidence
        all style probabilities
    """

    processor, model = (
        load_style_model()
    )

    outfit_image = get_outfit_region(
        image
    )

    style_names = list(
        STYLE_LABELS.keys()
    )

    style_descriptions = list(
        STYLE_LABELS.values()
    )

    inputs = processor(
        text=style_descriptions,
        images=outfit_image,
        return_tensors="pt",
        padding=True,
    )

    with torch.no_grad():

        outputs = model(
            **inputs
        )

    logits = (
        outputs.logits_per_image[0]
    )

    probabilities = torch.softmax(
        logits,
        dim=0,
    )

    probabilities = (
        probabilities.cpu().numpy()
    )

    best_index = int(
        np.argmax(probabilities)
    )

    style = style_names[
        best_index
    ]

    confidence = float(
        probabilities[best_index]
    )

    style_scores = {}

    for name, probability in zip(
        style_names,
        probabilities,
    ):

        style_scores[name] = round(
            float(probability) * 100,
            1,
        )

    return (
        style,
        confidence,
        style_scores,
    )


# ═════════════════════════════════════════════
# COLOR PROFILE
# ═════════════════════════════════════════════

def get_color_profile(
    palette
):
    """
    Describe the overall color tone.
    """

    if not palette:

        return (
            "No dominant colors detected."
        )

    brightness_values = [
        calculate_brightness(color)
        for color in palette
    ]

    average_brightness = (
        sum(brightness_values)
        / len(brightness_values)
    )

    if average_brightness < 70:

        return (
            "Dark-toned palette"
        )

    elif average_brightness > 180:

        return (
            "Light-toned palette"
        )

    return (
        "Balanced-toned palette"
    )


# ═════════════════════════════════════════════
# FEEDBACK
# ═════════════════════════════════════════════

def generate_feedback(
    style,
    palette,
    color_harmony,
    visual_balance,
):
    """
    Generate styling observations based on
    the detected style and color analysis.
    """

    feedback = []

    # ── Color harmony ────────────────────────

    if color_harmony >= 80:

        feedback.append(
            "The outfit has a cohesive color palette."
        )

    elif color_harmony >= 65:

        feedback.append(
            "The outfit has moderate color contrast."
        )

    else:

        feedback.append(
            "A neutral clothing element could help "
            "balance the stronger color variation."
        )

    # ── Visual balance ───────────────────────

    if visual_balance >= 80:

        feedback.append(
            "The dominant colors are visually balanced."
        )

    else:

        feedback.append(
            "Reducing the number of competing colors "
            "could create a cleaner look."
        )

    # ── Style specific feedback ──────────────

    if style == "Formal":

        feedback.append(
            "The outfit reads as formal and structured."
        )

    elif style == "Smart Casual":

        feedback.append(
            "The outfit balances polished and relaxed elements."
        )

    elif style == "Streetwear":

        feedback.append(
            "The outfit has a relaxed urban/streetwear character."
        )

    elif style == "Sporty":

        feedback.append(
            "The outfit has a strong athletic or sporty character."
        )

    elif style == "Minimal":

        feedback.append(
            "The outfit follows a clean and understated visual direction."
        )

    else:

        feedback.append(
            "The outfit has a relaxed everyday style."
        )

    return feedback


# ═════════════════════════════════════════════
# COMPLETE ANALYSIS
# ═════════════════════════════════════════════

def analyze_outfit(image):
    """
    Run the complete FIT404 analysis.
    """

    # ── Color analysis ───────────────────────

    palette, palette_percentages = extract_palette(
        image
    )

    color_harmony = (
        calculate_color_harmony(
            palette
        )
    )

    visual_balance = (
        calculate_visual_balance(
            palette
        )
    )

    color_profile = (
        get_color_profile(
            palette
        )
    )

    # ── AI style analysis ────────────────────

    try:

        (
            style,
            style_confidence,
            style_scores,
        ) = classify_style(
            image
        )

    except Exception:

        # Keeps FIT404 usable even if the
        # model cannot be downloaded/loaded.

        style = "Style unavailable"

        style_confidence = 0.0

        style_scores = {}

    # ── Feedback ─────────────────────────────

    feedback = generate_feedback(
        style,
        palette,
        color_harmony,
        visual_balance,
    )

    return {

        "palette":
            palette,

        "palette_percentages":
            palette_percentages,

        "color_harmony":
            color_harmony,

        "visual_balance":
            visual_balance,

        "style":
            style,

        "style_confidence":
            style_confidence,

        "style_scores":
            style_scores,

        "color_profile":
            color_profile,

        "feedback":
            feedback,

        "detected_items":
            [],

    }
