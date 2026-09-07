# 👕 FIT404

### BAD FIT NOT FOUND.

**FIT404** is a fashion-tech project built with Python and Streamlit that helps users analyse outfits, compare looks, organise a digital wardrobe, and generate context-aware outfit combinations from clothes they already own.

The project combines **explainable image-analysis techniques**, **CLIP zero-shot style classification**, and a **rule-based recommendation engine** while keeping the experience fast, visual, and easy to understand.

---

## ✨ Features

### 🔍 Analyze Fit

Upload an outfit photo and FIT404 generates a visual report containing:

- Dominant colour palette and approximate colour distribution
- **Colour Harmony** based on hue, saturation, luminance, and colour relationships
- **Visual Balance** using palette distribution and spatial image characteristics
- CLIP-assisted zero-shot style matching
- Style breakdown across multiple fashion directions
- Colour profile and styling observations
- Overall visual score

> The CLIP percentage represents a relative match among the style prompts considered by FIT404. It should not be interpreted as an objective probability that an outfit belongs to a particular style.

### ⚔️ Fit Battle

Upload two outfits and compare them using the same analysis pipeline.

FIT404 compares:

- Overall weighted score
- Colour harmony
- Visual balance

The battle score uses:

```text
58% Colour Harmony + 42% Visual Balance
```

Both outfits are evaluated using the same formula so the comparison remains consistent and explainable.

### 🗄️ Digital Wardrobe

Create a lightweight digital collection of clothes you already own.

Supported categories include:

- Tops
- Bottoms
- Footwear
- Outerwear
- Accessories

Wardrobe entries currently store the item's **name, category, and colour** in `data/wardrobe.json`.

### ✨ Build Fit

Build Fit generates outfits from the user's existing wardrobe rather than simply selecting pieces at random.

Each valid combination is evaluated using:

```text
42% Occasion Match
28% Colour Compatibility
18% Weather Suitability
12% Style Cohesion
```

Supported occasions:

- Casual Outing
- College
- Party
- Interview
- Formal Event

Supported weather contexts:

- Any Weather
- Hot
- Warm
- Cool
- Cold
- Rainy

FIT404 evaluates the available pieces, ranks compatible combinations, and selects from the strongest candidates. Outerwear and accessories are optional and are included only when appropriate for the selected context.

---

## 🧠 How Outfit Analysis Works

```text
Outfit Image
    │
    ▼
Lightweight Outfit-Region Crop
    │
    ├────────────────┐
    ▼                ▼
Dominant Palette    Spatial Image Features
    │                │
    ▼                ▼
Hue / Saturation    Left / Right Activity
Luminance / Share   Luminance / Saturation
    │                │
    └────────┬───────┘
             ▼
    Harmony + Balance
             │
             ├────────────► Overall Visual Score
             │
             ▼
        CLIP Style Match
             │
             ▼
         Outfit Report
```

The analysis is intentionally explainable. These scores are experimental indicators produced by FIT404's analysis methods rather than objective measurements of fashion quality.

---

## 🧩 How Build Fit Works

```text
Digital Wardrobe
      │
      ▼
Infer lightweight item traits
(formality, style, warmth, colour)
      │
      ▼
Generate valid combinations
      │
      ├──── Occasion Match
      ├──── Colour Compatibility
      ├──── Weather Suitability
      └──── Style Cohesion
      │
      ▼
Weighted Ranking
      │
      ▼
High-Quality Candidate Pool
      │
      ▼
Recommended Fit + Score Breakdown
```

The recommender works with the simple wardrobe format already used by FIT404. Users do not need to manually specify detailed fashion metadata for every item; lightweight traits are inferred from the item's name, category, and colour.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application and recommendation logic |
| Streamlit | Interactive web interface |
| Pillow | Image handling and colour processing |
| NumPy | Numerical and image analysis |
| PyTorch | CLIP inference runtime |
| Transformers | CLIP model and processor |
| Pytest | Automated testing |
| JSON | Lightweight wardrobe storage |

---

## 📁 Project Structure

```text
FIT404/
├── .streamlit/
│   └── config.toml
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── styles.css
├── assets/
├── data/
│   └── wardrobe.json
├── src/
│   ├── __init__.py
│   ├── analysis.py
│   ├── comparison.py
│   └── wardrobe.py
├── tests/
│   ├── test_analysis.py
│   ├── test_comparison.py
│   └── test_wardrobe.py
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd FIT404
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run FIT404

```bash
python -m streamlit run app/main.py
```

The first CLIP-powered style analysis may download `openai/clip-vit-base-patch32`. Once downloaded, the Hugging Face stack can reuse the locally cached model.

---

## 🧪 Testing

Run the automated tests with:

```bash
python -m pytest
```

Model loading is lazy, allowing the core colour-analysis, comparison, and recommendation tests to run without downloading CLIP during the unit-test suite.

---

## 📊 Current Capabilities

| Capability | Status |
|---|---|
| Outfit image upload | ✅ |
| Dominant colour extraction | ✅ |
| Colour harmony analysis | ✅ |
| Spatial visual balance analysis | ✅ |
| CLIP-assisted style classification | ✅ |
| Multi-style breakdown | ✅ |
| Fit Battle | ✅ |
| Digital Wardrobe | ✅ |
| Occasion-aware outfit generation | ✅ |
| Colour-aware outfit generation | ✅ |
| Weather-aware outfit generation | ✅ |
| Style-cohesion scoring | ✅ |
| Input validation | ✅ |
| Automated tests | ✅ |
| Clothing segmentation / detection | 🚧 Planned |
| Multi-user persistent wardrobe | 🚧 Planned |
| Dedicated fashion model | 🚧 Planned |

---

## ⚠️ Current Limitations

FIT404 is currently designed as a **local/single-user project**.

The wardrobe is stored in `data/wardrobe.json`. If the application is deployed publicly, that file becomes server-side storage rather than an independent wardrobe for every visitor. A multi-user deployment would therefore require user-scoped persistent storage.

Outfit-region detection is currently lightweight rather than full garment segmentation, so image composition and background elements can sometimes influence colour analysis.

Style classification is performed through zero-shot CLIP matching against a predefined set of fashion prompts rather than a fashion-specific model trained directly on FIT404 data.

---

## 🔮 Future Scope

Potential extensions include:

- Clothing and garment segmentation
- Garment and pattern recognition
- Automatic weather integration
- Richer editable wardrobe metadata
- User accounts and persistent cloud storage
- Save / like / dislike feedback for recommendations
- Recommendation learning from user preferences
- Fashion-specific embedding or classification models

---

## 🎯 Project Philosophy

FIT404 evaluates **clothing, colour relationships, styling, and image composition**. It is not intended to judge a person's body, attractiveness, or physical appearance.

The goal is to make outfit analysis and wardrobe recommendations **useful, explainable, and fun** without presenting subjective fashion choices as absolute facts.

---

## 👨‍💻 Author

**Aditya Kundliya**  
