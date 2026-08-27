import streamlit as st
import base64
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGO_FILE = PROJECT_ROOT / "assets" / "fit404_logo.png"
FOOTER_LOGO_FILE = PROJECT_ROOT / "assets" / "fit404_footer_logo.png"

from src.analysis import analyze_outfit
from src.comparison import compare_outfits

from src.wardrobe import (
    add_to_wardrobe,
    get_wardrobe,
    delete_item,
    generate_outfit,
)


# =============================================
# PAGE CONFIG
# =============================================

st.set_page_config(
    page_title="FIT404 — Bad Fit Not Found",
    page_icon=Image.open(LOGO_FILE),
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================
# LOAD CSS
# =============================================

CSS_FILE = (
    Path(__file__)
    .resolve()
    .parent
    / "styles.css"
)

if CSS_FILE.exists():

    css = CSS_FILE.read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )

else:

    st.error(
        f"CSS file not found: {CSS_FILE}"
    )


# =============================================
# HELPERS
# =============================================

def load_image(uploaded_file):

    if uploaded_file is None:
        return None

    return Image.open(
        uploaded_file
    ).convert("RGB")



def brand_logo(width=180, sidebar=False):
    """Render the FIT404 logo from the local assets folder."""
    if LOGO_FILE.exists():
        if sidebar:
            st.image(str(LOGO_FILE), width=115)
        else:
            st.image(str(LOGO_FILE), width=width)


def logo_data_uri():
    """Return the local logo as an embeddable data URI for precise positioning."""
    if not LOGO_FILE.exists():
        return ""
    encoded = base64.b64encode(LOGO_FILE.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def footer_logo_data_uri():
    """Return the compact horizontal footer logo as a data URI."""
    if not FOOTER_LOGO_FILE.exists():
        return ""
    encoded = base64.b64encode(FOOTER_LOGO_FILE.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def hero():
    logo_uri = logo_data_uri()

    st.html(
        f"""
        <div class="oc-hero fit404-logo-hero">
            <img class="fit404-center-logo" src="{logo_uri}" alt="FIT404 logo">
        </div>
        """
    )


def section_header(title):
    """Render a large split-colour section heading."""
    words = title.split(" ", 1)
    accent = words[0]
    rest = words[1] if len(words) > 1 else ""

    st.html(
        f"""
        <div class="oc-section">
            <div class="oc-section-title">
                <span class="oc-section-accent">{accent}</span>
                {f'<span class="oc-section-light"> {rest}</span>' if rest else ''}
            </div>
            <div class="oc-section-underline"></div>
        </div>
        """
    )


def show_palette(
    palette
):

    if not palette:

        st.info(
            "No palette detected."
        )

        return

    swatches = ""

    for color in palette:

        swatches += f"""
        <div class="oc-swatch-wrap">

            <div
                class="oc-swatch"
                style="
                    background:{color};
                "
            >
            </div>

            <div class="oc-swatch-code">
                {color.upper()}
            </div>

        </div>
        """

    st.html(
        f"""
        <div class="oc-palette">
            {swatches}
        </div>
        """
    )


def metric_card(
    label,
    value,
    progress=None
):

    progress_html = ""

    if progress is not None:

        progress_html = f"""
        <div class="oc-progress">

            <div
                class="oc-progress-fill"
                style="
                    width:{progress}%;
                "
            >
            </div>

        </div>
        """

    return f"""
    <div class="oc-metric">

        <div class="oc-metric-label">
            {label}
        </div>

        <div class="oc-metric-value">
            {value}
        </div>

        {progress_html}

    </div>
    """


def show_analysis_report(report):

    style = report.get(
        "style",
        "Unknown"
    )

    confidence = report.get(
        "style_confidence",
        0
    )

    harmony = report.get(
        "color_harmony",
        0
    )

    balance = report.get(
        "visual_balance",
        0
    )

    style_scores = report.get(
        "style_scores",
        {}
    )

    palette = report.get(
        "palette",
        []
    )

    palette_percentages = report.get(
        "palette_percentages",
        []
    )


    # =========================================
    # STYLE HERO
    # =========================================

    st.html(
        f"""
        <div class="fi-style-hero">

            <div class="fi-style-label">
                DETECTED STYLE
            </div>

            <div class="fi-style-value">
                {style.upper()}
            </div>

            <div class="fi-confidence">
                {confidence:.0%} CONFIDENCE
            </div>

        </div>
        """
    )


    # =========================================
    # SCORES
    # =========================================

    harmony_caption = (
        "Excellent"
        if harmony >= 85
        else
        "Very Good"
        if harmony >= 75
        else
        "Balanced"
    )

    balance_caption = (
        "Excellent"
        if balance >= 85
        else
        "Very Good"
        if balance >= 75
        else
        "Balanced"
    )

    st.html(
        f"""
        <div class="fi-two-grid">

            <div class="fi-score-card">

                <div class="fi-score-title">
                    COLOR HARMONY
                </div>

                <div class="fi-score-number">
                    {harmony}%
                </div>

                <div class="fi-bar-track">

                    <div
                        class="fi-bar-fill"
                        style="width:{harmony}%"
                    >
                    </div>

                </div>

                <div class="fi-score-caption">
                    {harmony_caption}
                </div>

            </div>


            <div class="fi-score-card">

                <div class="fi-score-title">
                    VISUAL BALANCE
                </div>

                <div class="fi-score-number">
                    {balance}%
                </div>

                <div class="fi-bar-track">

                    <div
                        class="fi-bar-fill"
                        style="width:{balance}%"
                    >
                    </div>

                </div>

                <div class="fi-score-caption">
                    {balance_caption}
                </div>

            </div>

        </div>
        """
    )


    # =========================================
    # STYLE BREAKDOWN
    # =========================================

    if style_scores:

        rows = ""

        sorted_styles = sorted(
            style_scores.items(),
            key=lambda item:
                item[1],
            reverse=True,
        )

        for style_name, score in sorted_styles:

            rows += f"""
            <div class="fi-style-row">

                <div class="fi-style-row-name">
                    {style_name}
                </div>

                <div class="fi-bar-track">

                    <div
                        class="fi-bar-fill"
                        style="width:{score}%"
                    >
                    </div>

                </div>

                <div class="fi-style-row-score">
                    {score:.1f}%
                </div>

            </div>
            """

        st.html(
            f"""
            <div class="fi-panel">

                <div class="fi-section-title">
<span class="fi-section-name">
                        STYLE BREAKDOWN
                    </span>

                </div>

                {rows}

            </div>
            """
        )


    # =========================================
    # COLOR PALETTE
    # =========================================

    palette_cards = ""

    palette_strip = ""

    for index, color in enumerate(
        palette
    ):

        if index < len(
            palette_percentages
        ):

            percentage = (
                palette_percentages[index]
            )

        else:

            percentage = 0

        palette_cards += f"""
        <div class="fi-color-card">

            <div
                class="fi-color-box"
                style="
                    background:{color};
                "
            >
            </div>

            <div class="fi-color-code">
                {color.upper()}
            </div>

            <div class="fi-color-percentage">
                {percentage:.1f}%
            </div>

        </div>
        """

        palette_strip += f"""
        <div
            style="
                width:{percentage}%;
                background:{color};
            "
        >
        </div>
        """


    st.html(
        f"""
        <div class="fi-panel">

            <div class="fi-section-title">
<span class="fi-section-name">
                    COLOR PALETTE
                </span>

            </div>

            <div class="fi-palette-grid">
                {palette_cards}
            </div>

            <div class="fi-palette-strip">
                {palette_strip}
            </div>

        </div>
        """
    )


    # =========================================
    # KEY INSIGHTS
    # =========================================

    if style == "Formal":

        best_occasion = (
            "Business / Formal"
        )

        vibe = (
            "Confident · Professional"
        )

    elif style == "Smart Casual":

        best_occasion = (
            "College / Dinner"
        )

        vibe = (
            "Polished · Relaxed"
        )

    elif style == "Streetwear":

        best_occasion = (
            "Casual / Social"
        )

        vibe = (
            "Urban · Expressive"
        )

    elif style == "Sporty":

        best_occasion = (
            "Active / Casual"
        )

        vibe = (
            "Dynamic · Comfortable"
        )

    else:

        best_occasion = (
            "Everyday"
        )

        vibe = (
            "Relaxed · Versatile"
        )


    average_score = int(
        (
            harmony
            +
            balance
        )
        / 2
    )

    if average_score >= 85:

        strength = "Strong"

    elif average_score >= 70:

        strength = "Balanced"

    else:

        strength = "Experimental"


    st.html(
        f"""
        <div class="fi-panel">

            <div class="fi-section-title">
<span class="fi-section-name">
                    KEY INSIGHTS
                </span>

            </div>

            <div class="fi-insight-grid">

                <div class="fi-insight">

                    <div class="fi-insight-label">
                        Best Occasion
                    </div>

                    <div class="fi-insight-value">
                        {best_occasion}
                    </div>

                </div>


                <div class="fi-insight">

                    <div class="fi-insight-label">
                        Vibe
                    </div>

                    <div class="fi-insight-value">
                        {vibe}
                    </div>

                </div>


                <div class="fi-insight">

                    <div class="fi-insight-label">
                        Fit Strength
                    </div>

                    <div class="fi-insight-value">
                        {strength}
                    </div>

                </div>

            </div>

        </div>
        """
    )


    # =========================================
    # FIT NOTES
    # =========================================

    feedback = report.get(
        "feedback",
        []
    )

    note_icons = [
        "✓",
        "★",
        "◎",
        "→",
    ]

    notes_html = ""

    for index, note in enumerate(
        feedback
    ):

        icon = note_icons[
            index % len(note_icons)
        ]

        notes_html += f"""
        <div class="fi-note">

            <div class="fi-note-icon">
                {icon}
            </div>

            <div>

                <div class="fi-note-main">
                    {note}
                </div>

                <div class="fi-note-sub">
                    Generated from the current
                    outfit's visual characteristics.
                </div>

            </div>

        </div>
        """


    st.html(
        f"""
        <div class="fi-panel">

            <div class="fi-section-title">
<span class="fi-section-name">
                    FIT NOTES
                </span>

            </div>

            {notes_html}

        </div>
        """
    )


# =============================================
# SIDEBAR
# =============================================

with st.sidebar:

    sidebar_logo_uri = logo_data_uri()
    st.html(
        f"""
        <div class="fit404-sidebar-logo-wrap">
            <img class="fit404-sidebar-logo" src="{sidebar_logo_uri}" alt="FIT404 — Bad Fit Not Found">
        </div>
        """
    )

    page = st.radio(
        "Navigation",
        [
            "Analyze Fit",
            "Fit Battle",
            "Wardrobe",
            "Build Fit",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.html(
        """
        <div class="oc-muted">

            Computer vision
            meets personal style.

            <br><br>

        </div>
        """
    )


# =============================================
# ANALYZE FIT
# =============================================

if page == "Analyze Fit":

    section_header("Drop The Fit")

    # Upload card
    st.html(
        """
        <div class="upload-hero">

            <div class="upload-plus">
                +
            </div>

            <div class="upload-title">
                DROP A LOOK.
            </div>

            <div class="upload-subtitle">
                Upload a clear outfit photo to unlock your fit report.
            </div>

        </div>
        """
    )

    uploaded_file = st.file_uploader(
        "Upload Outfit",
        type=[
            "jpg",
            "jpeg",
            "png"
        ],
        label_visibility="collapsed",
        key="main_outfit_upload",
    )

    # =========================================
    # RUN ANALYSIS AFTER IMAGE IS UPLOADED
    # =========================================

    if uploaded_file is not None:

        image = load_image(
            uploaded_file
        )

        st.write("")

        left, right = st.columns(
            [0.95, 1.25],
            gap="large",
        )

        # -------------------------------------
        # IMAGE
        # -------------------------------------

        with left:

            st.html(
                """
                <div class="oc-eyebrow">
                    YOUR FIT
                </div>
                """
            )

            st.image(
                image,
                use_container_width=True,
            )

        # -------------------------------------
        # ANALYSIS
        # -------------------------------------

        with right:

            st.html(
                """
                <div class="oc-eyebrow">
                    FIT INTELLIGENCE
                </div>
                """
            )

            with st.spinner(
                "Reading the fit..."
            ):

                report = analyze_outfit(
                    image
                )

            show_analysis_report(
                report
            )


# =============================================
# FIT BATTLE
# =============================================

elif page == "Fit Battle":

    section_header("Fit Battle")

    st.html(
        """
        <div class="oc-muted">
            Two fits enter.
            One leaves with the stronger
            visual score.
        </div>
        """
    )

    st.write("")

    col_a, center, col_b = (
        st.columns(
            [1, 0.18, 1],
            gap="medium",
        )
    )

    with col_a:

        with st.container(border=True):

            st.markdown(
                """
                <div class="oc-eyebrow battle-look-label">
                    LOOK A
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.html(
                """
                <div class="battle-upload-hero">
                    <div class="battle-upload-plus">+</div>
                    <div class="battle-upload-title">DROP A LOOK.</div>
                    <div class="battle-upload-subtitle">
                        Upload the first outfit to enter the battle.
                    </div>
                </div>
                """
            )

            file_a = st.file_uploader(
                "Look A",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                ],
                key="battle_a",
                label_visibility=
                    "collapsed",
            )

    with center:

        st.html(
            """
            <div
                style="
                    text-align:center;
                    font-weight:900;
                    font-size:1.5rem;
                    margin-top:4rem;
                    color:#c8ff32;
                "
            >
                VS
            </div>
            """
        )

    with col_b:

        with st.container(border=True):

            st.html(
                """
                <div class="oc-eyebrow battle-look-label">
                    LOOK B
                </div>
                """
            )

            st.html(
                """
                <div class="battle-upload-hero">
                    <div class="battle-upload-plus">+</div>
                    <div class="battle-upload-title">DROP A LOOK.</div>
                    <div class="battle-upload-subtitle">
                        Upload the second outfit to challenge it.
                    </div>
                </div>
                """
            )

            file_b = st.file_uploader(
                "Look B",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                ],
                key="battle_b",
                label_visibility=
                    "collapsed",
            )

    if file_a and file_b:

        image_a = load_image(
            file_a
        )

        image_b = load_image(
            file_b
        )

        image_col_a, image_col_b = (
            st.columns(2)
        )

        with image_col_a:

            st.image(
                image_a,
                use_container_width=True,
            )

        with image_col_b:

            st.image(
                image_b,
                use_container_width=True,
            )

        with st.spinner(
            "Judging the battle..."
        ):

            result = compare_outfits(
                image_a,
                image_b,
            )

        section_header("Battle Result")

        st.html(
            f"""
            <div class="oc-style-card">

                <div class="oc-style-label">
                    WINNER
                </div>

                <div class="oc-style-name">
                    {
                        result["winner"]
                    }
                </div>

            </div>
            """
        )

        a = result["outfit_a"]
        b = result["outfit_b"]

        st.html(
            f"""
            <div class="oc-metric-grid">

                {
                    metric_card(
                        "Look A Harmony",
                        f'''
                        {
                            a[
                                "color_harmony"
                            ]
                        }%
                        '''
                    )
                }

                {
                    metric_card(
                        "Look B Harmony",
                        f'''
                        {
                            b[
                                "color_harmony"
                            ]
                        }%
                        '''
                    )
                }

            </div>
            """
        )

        st.html(
            f"""
            <div class="oc-feedback">
                {
                    result["summary"]
                }
            </div>
            """
        )


# =============================================
# WARDROBE
# =============================================

elif page == "Wardrobe":

    section_header("Digital Wardrobe")

    st.html(
        """
        <div class="oc-muted">
            Keep your pieces organized.
            Your wardrobe stays local.
        </div>
        """
    )

    st.write("")

    with st.expander(
        "ADD NEW PIECE",
        expanded=True,
    ):

        name = st.text_input(
            "Piece name",
            placeholder=
                "Black oversized tee"
        )

        category = st.selectbox(
            "Category",
            [
                "Top",
                "Bottom",
                "Footwear",
                "Outerwear",
                "Accessory",
            ],
        )

        color = st.text_input(
            "Color",
            placeholder="Black"
        )

        if st.button(
            "ADD TO WARDROBE"
        ):

            if (
                name.strip()
                and
                color.strip()
            ):

                add_to_wardrobe(
                    name,
                    category,
                    color,
                )

                st.success(
                    "Piece added."
                )

                st.rerun()

            else:

                st.warning(
                    "Add a name and color."
                )

    wardrobe = get_wardrobe()

    section_header(f"Pieces / {len(wardrobe)}"
    )

    if not wardrobe:

        st.html(
            """
            <div class="oc-card">
                Your wardrobe is empty.
            </div>
            """
        )

    else:

        for item in wardrobe:

            col_item, col_delete = st.columns(
            [10, 1],
            gap="small"
            )

            with col_item:

                st.html(
                    f"""
                    <div class="oc-card">

                        <div class="oc-eyebrow">
                            {item["category"].upper()}
                        </div>

                        <div style="
                            font-size: 1.35rem;
                            font-weight: 900;
                            margin-top: 0.25rem;
                            margin-bottom: 0.35rem;
                        ">
                            {item["name"]}
                        </div>

                        <div class="oc-muted">
                            {item["color"]}
                        </div>

                    </div>
                    """
                )

            with col_delete:

                if st.button(
                    "×",
                    key=f'delete_{item["id"]}',
                    help="Remove item"
                ):
                    delete_item(
                        item["id"]
                    )

                    st.rerun()


# =============================================
# BUILD FIT
# =============================================

elif page == "Build Fit":

    section_header("Build A Fit")

    wardrobe = get_wardrobe()

    if not wardrobe:

        st.warning(
            "Add pieces to your wardrobe first."
        )

    else:

        occasion = st.selectbox(
            "Occasion",
            [
                "Casual Outing",
                "College",
                "Party",
                "Interview",
                "Formal Event",
            ],
        )

        if st.button(
            "GENERATE THE FIT"
        ):

            outfit = generate_outfit(
                wardrobe,
                occasion,
            )

            if outfit:

                st.html(
                    """
                    <div class="oc-eyebrow">
                        GENERATED LOOK
                    </div>
                    """
                )

                for (
                    category,
                    item
                ) in outfit.items():

                    if category == "reason":
                        continue

                    st.html(
                        f"""
                        <div
                            class="oc-card"
                            style="
                                margin-bottom:
                                    0.7rem;
                            "
                        >

                            <div
                                class="
                                    oc-eyebrow
                                "
                            >
                                {category}
                            </div>

                            <div
                                style="
                                    font-size:
                                        1.25rem;
                                    font-weight:
                                        900;
                                "
                            >
                                {
                                    item[
                                        "name"
                                    ]
                                }
                            </div>

                            <div
                                class="
                                    oc-muted
                                "
                            >
                                {
                                    item[
                                        "color"
                                    ]
                                }
                            </div>

                        </div>
                        """
                    )

                st.html(
                    f"""
                    <div class="oc-feedback">
                        {
                            outfit.get(
                                "reason",
                                ""
                            )
                        }
                    </div>
                    """
                )

            else:

                st.warning(
                    "You need at least a top, bottom and footwear."
                )


# =============================================
# FOOTER
# =============================================

footer_logo_uri = footer_logo_data_uri()

st.html(
    f"""
    <div class="oc-footer">

        <div class="oc-footer-brand">
            <img class="fit404-footer-logo" src="{footer_logo_uri}" alt="FIT404 — Bad Fit Not Found">
        </div>

        <div class="oc-footer-socials">

            <a
                href="https://www.instagram.com/bhukkad_kutta/"
                target="_blank"
                rel="noopener noreferrer"
                class="oc-social-icon"
                title="Instagram"
            >
                <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGcgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZjRmNGVmIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHJlY3QgeD0iMyIgeT0iMyIgd2lkdGg9IjE4IiBoZWlnaHQ9IjE4IiByeD0iNSIvPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjQiLz48Y2lyY2xlIGN4PSIxNy41IiBjeT0iNi41IiByPSIxIiBmaWxsPSIjZjRmNGVmIiBzdHJva2U9Im5vbmUiLz48L2c+PC9zdmc+" alt="Instagram">
            </a>

            <a
                href="https://www.linkedin.com/in/aditya-kundliya-3ba57b371/"
                target="_blank"
                rel="noopener noreferrer"
                class="oc-social-icon"
                title="LinkedIn"
            >
                <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGcgZmlsbD0iI2Y0ZjRlZiI+PHJlY3QgeD0iMyIgeT0iOSIgd2lkdGg9IjQiIGhlaWdodD0iMTIiIHJ4PSIuNSIvPjxjaXJjbGUgY3g9IjUiIGN5PSI1IiByPSIyIi8+PHBhdGggZD0iTTEwIDloNHYxLjdjLjktMS4zIDIuMi0yLjEgNC4xLTIuMSAzLjIgMCAzLjkgMi4xIDMuOSA1LjJWMjFoLTR2LTYuM2MwLTEuNSAwLTMtMS45LTNzLTIuMSAxLjUtMi4xIDIuOVYyMWgtNFY5eiIvPjwvZz48L3N2Zz4=" alt="LinkedIn">
            </a>

        </div>

    </div>
    """
)
