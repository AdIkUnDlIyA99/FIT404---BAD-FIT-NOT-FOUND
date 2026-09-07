from PIL import Image, ImageDraw

from src.analysis import (
    analyze_outfit,
    calculate_color_harmony,
    calculate_visual_balance,
    extract_palette,
    get_color_profile,
)


def create_test_image(color=(40, 80, 160)):
    return Image.new("RGB", (160, 220), color)


def test_palette_extraction():
    palette, percentages = extract_palette(create_test_image())

    assert palette
    assert len(palette) == len(percentages)
    assert all(color.startswith("#") and len(color) == 7 for color in palette)
    assert all(0 <= percentage <= 100 for percentage in percentages)


def test_color_harmony_is_bounded_and_uses_percentages():
    palette = ["#101010", "#eeeeee", "#d0b080"]

    balanced = calculate_color_harmony(palette, [45, 35, 20])
    dominant = calculate_color_harmony(palette, [92, 5, 3])

    assert 0 <= balanced <= 100
    assert 0 <= dominant <= 100
    assert balanced >= dominant


def test_visual_balance_responds_to_spatial_asymmetry():
    balanced_image = create_test_image((90, 90, 90))

    asymmetric_image = Image.new("RGB", (200, 260), "black")
    draw = ImageDraw.Draw(asymmetric_image)
    draw.rectangle((100, 0, 199, 259), fill="white")

    balanced_palette, balanced_percentages = extract_palette(balanced_image)
    asymmetric_palette, asymmetric_percentages = extract_palette(asymmetric_image)

    balanced_score = calculate_visual_balance(
        balanced_palette,
        balanced_percentages,
        image=balanced_image,
    )
    asymmetric_score = calculate_visual_balance(
        asymmetric_palette,
        asymmetric_percentages,
        image=asymmetric_image,
    )

    assert 0 <= balanced_score <= 100
    assert 0 <= asymmetric_score <= 100
    assert balanced_score > asymmetric_score


def test_color_profile():
    profile = get_color_profile(
        ["#202020", "#808080", "#f0f0f0"],
        [50, 30, 20],
    )

    assert isinstance(profile, str)
    assert "palette" in profile.lower()


def test_complete_outfit_analysis_without_loading_clip():
    report = analyze_outfit(create_test_image(), include_style=False)

    expected = {
        "palette",
        "palette_percentages",
        "color_harmony",
        "visual_balance",
        "overall_score",
        "style",
        "color_profile",
        "feedback",
        "detected_items",
        "analysis_version",
    }

    assert expected.issubset(report)
    assert report["analysis_version"] == "2.0"
    assert report["style"] == "Style analysis skipped"
    assert 0 <= report["overall_score"] <= 100
