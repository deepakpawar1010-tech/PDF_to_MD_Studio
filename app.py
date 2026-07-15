from __future__ import annotations

import streamlit as st

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="PDF to Markdown Studio",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- SIDEBAR ---------------- #

st.sidebar.title("📄 PDF to Markdown Studio")

st.sidebar.markdown("---")

st.sidebar.success("Version 1.0")

st.sidebar.markdown(
"""
### Modules

- 📄 PDF to Markdown
- ⚙ Settings
"""
)

# ---------------- HOME PAGE ---------------- #

st.title("📄 PDF to Markdown Studio")

st.markdown(
"""
Convert one or multiple PDFs into high-quality Markdown using **Marker OCR**.

---

### Features

- Upload multiple PDFs
- OCR support
- Batch Conversion
- Markdown Preview
- Download Markdown
- Download ZIP

"""
)

st.info("Select **PDF to Markdown** from the sidebar to begin.")