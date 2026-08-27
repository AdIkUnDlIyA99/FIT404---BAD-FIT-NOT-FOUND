import json
from pathlib import Path
from random import choice


# ═════════════════════════════════════════════
# STORAGE CONFIGURATION
# ═════════════════════════════════════════════

DATA_FOLDER = Path(__file__).resolve().parent.parent / "data"

WARDROBE_FILE = DATA_FOLDER / "wardrobe.json"


# ═════════════════════════════════════════════
# INITIALIZE STORAGE
# ═════════════════════════════════════════════

def initialize_wardrobe():
    """
    Create the data folder and wardrobe file
    if they don't already exist.
    """

    DATA_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not WARDROBE_FILE.exists():

        with open(
            WARDROBE_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                [],
                file,
                indent=4,
            )


# ═════════════════════════════════════════════
# LOAD WARDROBE
# ═════════════════════════════════════════════

def get_wardrobe():
    """
    Load all clothing items from the wardrobe.
    """

    initialize_wardrobe()

    try:

        with open(
            WARDROBE_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            wardrobe = json.load(file)

        return wardrobe

    except (
        json.JSONDecodeError,
        FileNotFoundError,
    ):

        return []


# ═════════════════════════════════════════════
# SAVE WARDROBE
# ═════════════════════════════════════════════

def save_wardrobe(wardrobe):
    """
    Save the wardrobe to the JSON file.
    """

    initialize_wardrobe()

    with open(
        WARDROBE_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            wardrobe,
            file,
            indent=4,
        )


# ═════════════════════════════════════════════
# ADD ITEM
# ═════════════════════════════════════════════

def add_to_wardrobe(
    item_name,
    category,
    color,
):
    """
    Add a new clothing item to the wardrobe.

    Returns the newly created item.
    """

    wardrobe = get_wardrobe()

    # Generate a simple unique ID
    if wardrobe:

        new_id = max(
            item["id"]
            for item in wardrobe
        ) + 1

    else:

        new_id = 1

    item = {
        "id": new_id,
        "name": item_name.strip(),
        "category": category,
        "color": color.strip(),
    }

    wardrobe.append(item)

    save_wardrobe(wardrobe)

    return item


# ═════════════════════════════════════════════
# DELETE ITEM
# ═════════════════════════════════════════════

def delete_item(item_id):
    """
    Delete an item using its ID.

    Returns True if an item was deleted.
    """

    wardrobe = get_wardrobe()

    updated_wardrobe = [
        item
        for item in wardrobe
        if item["id"] != item_id
    ]

    if len(updated_wardrobe) == len(wardrobe):
        return False

    save_wardrobe(updated_wardrobe)

    return True


# ═════════════════════════════════════════════
# CATEGORY FILTER
# ═════════════════════════════════════════════

def get_items_by_category(
    wardrobe,
    category,
):
    """
    Return all items belonging to a category.
    """

    return [
        item
        for item in wardrobe
        if item["category"] == category
    ]


# ═════════════════════════════════════════════
# OUTFIT GENERATOR
# ═════════════════════════════════════════════

def generate_outfit(
    wardrobe,
    occasion,
):
    """
    Generate a simple outfit from the user's wardrobe.

    The current generator focuses on having
    compatible clothing categories available.
    """

    tops = get_items_by_category(
        wardrobe,
        "Top",
    )

    bottoms = get_items_by_category(
        wardrobe,
        "Bottom",
    )

    footwear = get_items_by_category(
        wardrobe,
        "Footwear",
    )

    outerwear = get_items_by_category(
        wardrobe,
        "Outerwear",
    )

    accessories = get_items_by_category(
        wardrobe,
        "Accessory",
    )

    # A basic outfit requires a top,
    # bottom and footwear.
    if not tops or not bottoms or not footwear:
        return None

    selected_top = choice(tops)
    selected_bottom = choice(bottoms)
    selected_footwear = choice(footwear)

    outfit = {
        "Top": selected_top,
        "Bottom": selected_bottom,
        "Footwear": selected_footwear,
    }

    # Add outerwear occasionally if available.
    if outerwear:

        outfit["Outerwear"] = choice(
            outerwear
        )

    # Add an accessory occasionally if available.
    if accessories:

        outfit["Accessory"] = choice(
            accessories
        )

    # Add an explanation to the generated result.
    outfit["reason"] = (
        f"This outfit was generated for "
        f"'{occasion}' using items available "
        f"in your wardrobe."
    )

    return outfit
