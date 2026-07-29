"""
PDF_to_MD_Studio v1.0 - About Page
===================================
Application information, credits, help, and documentation.
"""

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
        ("📄 Single File Conversion", "Convert individual PDFs with full control over output settings and preview results before downloading."),
        ("📦 Batch Processing", "Process multiple PDFs simultaneously with automatic ZIP packaging for easy distribution."),
        ("🤖 AI-Powered Engine", "Leverages the Marker library for intelligent text extraction, layout preservation, and structure recognition."),
        ("🖼️ Image Preservation", "Automatically extracts and preserves images from PDFs, maintaining visual context in your Markdown output."),
        ("📜 Markdown Viewer", "Built-in preview with raw/rendered modes, content statistics, and document structure analysis."),
        ("⚙️ Flexible Configuration", "Customize output directories, conversion quality, OCR settings, and appearance preferences."),
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
        """
        **PDF to Markdown Studio** is built on top of excellent open-source projects:
        
        - **[Marker](https://github.com/VikParuchuri/marker)** by Vik Paruchuri — 
          The core PDF-to-Markdown conversion engine
        
        - **[Streamlit](https://streamlit.io/)** — 
          The web application framework powering the UI
        
        - **Python Community** — 
          For the countless libraries that make this possible
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