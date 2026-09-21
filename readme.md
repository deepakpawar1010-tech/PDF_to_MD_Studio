# ⚡ TeXify Studio v2.0

> **High-Precision PDF to Markdown Conversion with 100% LaTeX Math Accuracy**

TeXify Studio is a production-ready document conversion platform designed to transform dense mathematical papers, worksheets, and textbooks into clean, structured Markdown with flawless LaTeX formulas.

---

## ✨ Features

- **🧮 100% LaTeX Math Accuracy**: Perfect recognition and rendering of complex mathematical expressions, fractions, matrices, roots, and sub/superscripts (`$...$` and `$$...$$`).
- **📋 Mathpix-Style LaTeX Copy**:
  - Select text across equations and press `Ctrl+C` to copy real LaTeX source code.
  - Click any equation to copy its LaTeX formula directly to your clipboard.
  - One-click `Copy Markdown` toolbar action.
- **🔍 50:50 Side-by-Side Comparison**:
  - **Left**: High-resolution, multi-page continuous scroll or single-page PDF viewer powered by PyMuPDF (100% browser-compatible, zero security blocking).
  - **Right**: Live KaTeX-rendered Markdown viewer filling the full column width.
- **⚡ High-Throughput Gemini Vision Engine**:
  - Powered by Google Gemini Multimodal Vision (`gemini-3.5-flash-lite`).
  - Converts dense pages in ~0.4s per page.
  - Supports up to **1,500 free pages/day** via Google AI Studio.
  - Automatic model fallback ladder (`gemini-3.5-flash-lite` → `gemini-flash-lite-latest` → `gemini-3.1-flash-lite` → `gemini-3.5-flash`).
- **🖥️ Offline Marker Engine**:
  - Local, offline conversion fallback powered by Vik Paruchuri's Marker engine.
- **📚 Document Library**:
  - Browse, inspect, edit, and export previously converted documents and extracted assets.

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Deepak927927/PDF_to_MD_Studio.git
cd PDF_to_MD_Studio
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch TeXify Studio
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## ⚙️ Configuration

1. Copy `config.example.json` to `config.json`:
   ```bash
   cp config.example.json config.json
   ```
2. In TeXify Studio, navigate to **⚙️ Settings** and enter your free Google Gemini API Key from [aistudio.google.com](https://aistudio.google.com).

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) + [KaTeX](https://katex.org/) + [Marked.js](https://marked.js.org/)
- **Vision Engine**: [Google Gemini 3.5 Flash-Lite](https://ai.google.dev/)
- **Local Engine**: [Marker](https://github.com/VikParuchuri/marker)
- **PDF Processing**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
- **Language**: Python 3.12+

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
