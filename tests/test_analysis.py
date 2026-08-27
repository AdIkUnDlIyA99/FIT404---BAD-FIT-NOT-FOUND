from PIL import Image

from src.analysis import (
    analyze_outfit,
    calculate_color_harmony,
    calculate_visual_balance,
    extract_palette,
    classify_style,
    get_color_profile,
)


def create_test_image():
    """Create a simple image for testing."""
    return Image.new(
        "RGB",
        (100, 100),
        (40, 80, 160),
    )


def test_palette_extraction():
    """Check that palette extraction works."""

    image = create_test_image()

    palette, percentages = extract_palette(image)

    assert len(palette) > 0
    assert len(palette) == len(percentages)

    for color in palette:
        assert color.startswith("#")
        assert len(color) == 7


def test_color_harmony():
    """Check that harmony score is valid."""

    palette = [
        "#202020",
        "#808080",
        "#f0f0f0",
    ]

    score = calculate_color_harmony(palette)

    assert 0 <= score <= 100


def test_visual_balance():
    """Check that balance score is valid."""

    palette = [
        "#202020",
        "#808080",
        "#f0f0f0",
    ]

    score = calculate_visual_balance(palette)

    assert 0 <= score <= 100


def test_style_classification():
    """Check that a style is returned."""

    image = create_test_image()

    style, confidence, style_scores = classify_style(image)

    assert isinstance(style, str)
    assert len(style) > 0
    assert 0.0 <= confidence <= 1.0
    assert isinstance(style_scores, dict)


def test_color_profile():
    """Check that a color profile is returned."""

    palette = [
        "#202020",
        "#808080",
        "#f0f0f0",
    ]

    profile = get_color_profile(palette)

    assert isinstance(profile, str)
    assert len(profile) > 0


def test_complete_outfit_analysis():
    """Check the complete analysis report."""

    image = create_test_image()

    report = analyze_outfit(image)

    assert "palette" in report
    assert "color_harmony" in report
    assert "visual_balance" in report
    assert "style" in report
    assert "color_profile" in report
    assert "feedback" in report
    assert "detected_items" in report

    assert isinstance(report["palette"], list)
    assert isinstance(report["style"], str)
    assert isinstance(report["feedback"], list)
    assert isinstance(report["detected_items"], list)
