"""
PDF_to_MD_Studio v1.0 - About Page
===================================
Application information, credits, help, and documentation.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from core.constants import (
    ABOUT_CONTENT,
    APP_NAME,
    APP_VERSION,
    HELP_TEXT,
    MESSAGES,
)
from core.logger import get_logger
from core.session_manager import init_session
from core.ui_helpers import (
    apply_custom_css,
    card,
    page_header,
    render_sidebar,
    setup_page,
)

logger = get_logger(__name__)


def render_about_section() -> None:
    """Render the main about content."""
    st.markdown(ABOUT_CONTENT)
    
    st.markdown("---")
    st.markdown("### 🎯 Key Features")
    
    features = [
        ("⚡ High-Speed Gemini Engine", "Convert dense, multi-page mathematical documents in seconds using Google's Gemini 3.5 Flash vision model."),
        ("🧮 100% LaTeX Math Accuracy", "Flawless formatting for formulas, subscripts, superscripts, combinations, fractions, and matrices ($...$ and $$...$$)."),
        ("📋 Mathpix-Style LaTeX Copy", "Highlight text or click any formula in the rendered preview to copy pure LaTeX source code directly to your clipboard."),
        ("🔍 50:50 Side-by-Side Studio", "Inspect your original PDF and rendered Markdown side-by-side with full column width and synchronized review."),
        ("📚 Document Library", "Browse, search, edit, and export your converted documents and extracted assets anytime."),
        ("🖥️ Offline Marker Fallback", "100% local, offline conversion fallback powered by the Marker engine."),
    ]
    
    for title, description in features:
        with st.expander(title, expanded=False):
            st.markdown(description)


def render_help_section() -> None:
    """Render the help and FAQ section."""
    st.markdown("---")
    st.markdown("### ❓ Help & FAQ")
    
    faqs = [
        (
            "How do I install marker_single.exe?",
            """
            Marker is a separate Python package. Install it via pip:
            ```bash
            pip install marker-pdf
            ```
            Ensure `marker_single.exe` is available in your system PATH, or specify the full path in Settings.
            """
        ),
        (
            "What PDF types are supported?",
            """
            PDF_to_MD_Studio supports all standard PDF files including:
            - Text-based PDFs (best results)
            - Scanned PDFs (with OCR enabled in Settings)
            - Multi-column layouts
            - Documents with tables and images
            
            Maximum file size: 100MB per file.
            """
        ),
        (
            "Where are my converted files saved?",
            """
            By default, files are saved to the `output/` directory in the application folder.
            You can change this in Settings → General → Output Directory.
            """
        ),
        (
            "How does batch conversion work?",
            """
            Upload multiple PDFs, enable "Create ZIP Archive", and click Convert All.
            The app will process each file and package results into a single ZIP download.
            """
        ),
        (
            "Can I customize the Markdown output?",
            """
            Yes! In Settings → Conversion you can adjust:
            - **Quality**: High (accuracy) vs Fast (speed)
            - **Language**: For better OCR results
            - **OCR**: Force OCR for scanned documents
            - **Images**: Choose to preserve or ignore images
            """
        ),
        (
            "The conversion failed. What should I check?",
            """
            1. Verify `marker_single.exe` is installed and accessible (check System Info in Settings)
            2. Ensure the PDF isn't corrupted or password-protected
            3. Check the timeout setting (large files may need more time)
            4. Review recent logs in Settings → System → Recent Logs
            5. Try enabling OCR for scanned documents
            """
        ),
    ]
    
    for question, answer in faqs:
        with st.expander(question, expanded=False):
            st.markdown(answer)


def render_credits_section() -> None:
    """Render credits and acknowledgments."""
    st.markdown("---")
    st.markdown("### 🙏 Credits")
    
    st.markdown(
        f"""
        **{APP_NAME}** is powered by leading AI and document technology:
        
        - **[Google Gemini Vision](https://ai.google.dev/)** — 
          Ultra-fast multimodal vision for dense mathematical OCR and LaTeX conversion
        
        - **[KaTeX](https://katex.org/)** — 
          The fastest math typesetting library for the web with Mathpix-style LaTeX copying
        
        - **[Marker](https://github.com/VikParuchuri/marker)** by Vik Paruchuri — 
          Local offline PDF-to-Markdown engine
        
        - **[Streamlit](https://streamlit.io/)** — 
          The web application framework powering the UI
        """
    )
    
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <p style="font-size: 1.2rem;">Made with ❤️ for the PDF-to-Markdown community</p>
            <p style="color: #666;">Version {version}</p>
        </div>
        """.format(version=APP_VERSION),
        unsafe_allow_html=True,
    )


def render_shortcuts_section() -> None:
    """Render keyboard shortcuts and tips."""
    st.markdown("---")
    st.markdown("### ⌨️ Tips & Shortcuts")
    
    tips = [
        "💡 **Drag & Drop**: You can drag PDF files directly onto the upload area",
        "💡 **Settings Auto-Save**: All settings are saved automatically—no manual save needed",
        "💡 **Batch ZIP**: Always enable ZIP for batch conversions to keep files organized",
        "💡 **Preview First**: Use the Markdown Viewer to check quality before downloading",
        "💡 **OCR for Scans**: Enable OCR in Settings for better results with scanned documents",
        "💡 **Temp Cleanup**: Use Settings → General → Clean Temp Files to free disk space",
        "💡 **Log Level**: Set to DEBUG in Settings for detailed troubleshooting information",
    ]
    
    for tip in tips:
        st.markdown(tip)


def render_about_page() -> None:
    """Render the complete about page."""
    setup_page("About", "📖")
    init_session()
    render_sidebar()
    
    page_header("📖 About", f"Learn more about {APP_NAME}")
    
    # Main content sections
    render_about_section()
    render_help_section()
    render_shortcuts_section()
    render_credits_section()


def main() -> None:
    """Page entry point."""
    apply_custom_css()
    render_about_page()


if __name__ == "__main__":
    main()