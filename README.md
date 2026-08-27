# 👕 FIT404: BAD FIT NOT FOUND

### 

**FIT404** is a fashion-tech project built with Python that explores how computer vision and image analysis can be used to understand outfit colors, visual balance, and styling.

Along with single-outfit analysis, the project includes outfit comparison, a digital wardrobe, outfit generation, and context-based styling suggestions.

---

## ✨ Features

### 🔍 Outfit Analysis
Upload an outfit image and receive:

- Dominant color palette
- Color harmony score
- Visual balance score
- AI-assisted style classification
- Color profile
- Styling feedback

### ⚔️ Outfit Battle
Can't decide between two outfits?

Upload **Outfit A** and **Outfit B** and FIT404 compares their:

- Color harmony
- Visual balance
- Overall analysis score

The app then highlights the stronger result based on its current scoring system.

### 🗄️ Digital Wardrobe
Create a lightweight local wardrobe containing:

- Tops
- Bottoms
- Footwear
- Outerwear
- Accessories

Wardrobe information is stored locally using JSON.

### ✨ Outfit Generator
FIT404 can generate combinations using clothes already available in the digital wardrobe.

### 🎯 Occasion & Weather Mode
Get simple styling guidance based on:

- College
- Casual outings
- Parties
- Interviews
- Formal events

and conditions such as hot, warm, cool, cold, or rainy weather.

---

## 🧠 How Outfit Analysis Works

```text
            Outfit Image
                 │
                 ▼
         Image Preprocessing
                 │
                 ▼
       Dominant Color Extraction
                 │
                 ▼
        Color Characteristics
                 │
          ┌──────┴──────┐
          ▼             ▼
    Color Harmony   Visual Balance
          │             │
          └──────┬──────┘
                 ▼
        Style Classification
                 │
                 ▼
         Styling Feedback
                 │
                 ▼
          Outfit Report
```

The current analysis engine combines **image-processing heuristics with CLIP zero-shot style classification**.

Color analysis remains explainable, while CLIP provides AI-assisted style classification without a paid API.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web interface |
| Pillow | Image handling |
| NumPy | Image and numerical processing |
| OpenCV | Computer-vision development |
| Pandas | Data-processing utilities |
| scikit-learn | ML experimentation |
| Pytest | Automated testing |
| JSON | Local wardrobe storage |

The project is designed around **free and open-source tools**.

---

## 📁 Project Structure

```text
FIT404/
│
├── app/
│   ├── __init__.py
│   └── main.py
│
├── src/
│   ├── __init__.py
│   ├── analysis.py
│   ├── comparison.py
│   └── wardrobe.py
│
├── tests/
│   ├── test_analysis.py
│   └── test_comparison.py
│
├── assets/
├── data/
├── models/
├── notebooks/
│
├── requirements.txt
├── .gitignore
└── README.md
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

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run FIT404

```bash
python -m streamlit run app/main.py
```

Streamlit will launch the application in your browser.

---

## 🧪 Running Tests

Run:

```bash
python -m pytest
```

The automated tests currently cover core outfit analysis and comparison functionality.

---

## 🗺️ Development Status

| Feature | Status |
|---|---|
| Image Upload | ✅ |
| Dominant Color Extraction | ✅ |
| Color Harmony Analysis | ✅ |
| Visual Balance Analysis | ✅ |
| CLIP Style Classification | ✅ |
| Outfit Comparison | ✅ |
| Digital Wardrobe | ✅ |
| Outfit Generation | ✅ |
| Occasion Suggestions | ✅ |
| Manual Weather Context | ✅ |
| Clothing Detection Model | 🚧 Planned |
| Dedicated trained style classifier | 🚧 Planned |

---

## 🔮 Future Improvements

Future versions can explore:

- Clothing-item detection using computer vision
- A dedicated fine-tuned outfit-style classifier
- Clothing-specific color extraction
- Pattern and texture recognition
- Improved color-harmony models
- Smarter wardrobe recommendations
- Automatic weather integration

---

## ⚠️ Project Scope

FIT404 focuses on **clothing, colors, and visual styling**.

It is not designed to rate a person's body, attractiveness, or physical appearance. Current scores represent characteristics of the image/outfit according to the project's experimental analysis methods.

---

## 👨‍💻 Author

**Aditya Kundliya**

B.Tech Computer Science Engineering — Artificial Intelligence & Machine Learning

---

⭐ If you find FIT404 interesting, consider starring the repository!
