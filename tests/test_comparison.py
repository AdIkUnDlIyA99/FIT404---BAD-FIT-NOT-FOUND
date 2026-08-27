from PIL import Image

from src.comparison import compare_outfits


def create_image(color):
    """
    Create a simple RGB image
    for comparison testing.
    """
    return Image.new(
        "RGB",
        (100, 100),
        color,
    )


def test_compare_outfits_returns_expected_fields():
    """
    Check that outfit comparison returns
    all required data.
    """

    outfit_a = create_image((30, 30, 30))
    outfit_b = create_image((220, 220, 220))

    result = compare_outfits(
        outfit_a,
        outfit_b,
    )

    assert "outfit_a" in result
    assert "outfit_b" in result
    assert "score_a" in result
    assert "score_b" in result
    assert "winner" in result
    assert "summary" in result


def test_comparison_scores_are_numbers():
    """
    Check that both comparison scores
    are numeric.
    """

    outfit_a = create_image((40, 80, 160))
    outfit_b = create_image((180, 120, 60))

    result = compare_outfits(
        outfit_a,
        outfit_b,
    )

    assert isinstance(
        result["score_a"],
        (int, float),
    )

    assert isinstance(
        result["score_b"],
        (int, float),
    )


def test_comparison_returns_winner():
    """
    Check that the comparison produces
    a readable winner result.
    """

    outfit_a = create_image((20, 20, 20))
    outfit_b = create_image((100, 150, 200))

    result = compare_outfits(
        outfit_a,
        outfit_b,
    )

    assert isinstance(
        result["winner"],
        str,
    )

    assert len(
        result["winner"]
    ) > 0


def test_same_images_can_tie():
    """
    Identical images should receive
    identical analysis scores.
    """

    outfit_a = create_image(
        (100, 100, 100)
    )

    outfit_b = create_image(
        (100, 100, 100)
    )

    result = compare_outfits(
        outfit_a,
        outfit_b,
    )

    assert (
        result["score_a"]
        == result["score_b"]
    )

    assert "Tie" in result["winner"]
