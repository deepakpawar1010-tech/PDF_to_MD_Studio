"""
PDF_to_MD_Studio v1.0 - Main Application
========================================
Entry point for the Streamlit application.
Handles initialization, routing, and global setup.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from core.constants import APP_NAME, APP_VERSION, PAGE_ICON
from core.logger import LoggerManager, get_logger
from core.session_manager import SessionManager, init_session
from core.ui_helpers import apply_custom_css, render_sidebar, setup_page

logger = get_logger(__name__)


def initialize_app() -> None:
    LoggerManager.initialize()
    init_session()
    apply_custom_css()
    logger.info(f"{APP_NAME} v{APP_VERSION} started")
    SessionManager.set("_current_page", "home")


def render_home() -> None:
    setup_page("Home", PAGE_ICON)
    init_session()
    render_sidebar()

    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem 1rem;">
            <h1 style="font-size: 3rem; margin-bottom: 1rem;">{PAGE_ICON} {APP_NAME}</h1>
            <p style="font-size: 1.3rem; color: #aaa; max-width: 700px; margin: 0 auto;">
                Convert PDFs to Markdown and split textbook PDFs into worksheet-wise files from one place.
            </p>
            <p style="font-size: 1rem; color: #666; margin-top: 1rem;">Version {APP_VERSION}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div style="text-align: center; padding: 1.5rem;">
                <h2 style="font-size: 2.5rem;">📄</h2>
                <h3>Single File</h3>
                <p style="color: #888;">Convert individual PDFs to Markdown with full control over settings and output.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Convert Single PDF →", key="btn_single", use_container_width=True):
            st.switch_page("pages/1_📄_PDF_to_MD.py")

    with col2:
        st.markdown(
            """
            <div style="text-align: center; padding: 1.5rem;">
                <h2 style="font-size: 2.5rem;">📜</h2>
                <h3>View Results</h3>
                <p style="color: #888;">Preview and download your converted Markdown files.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("View Results →", key="btn_viewer", use_container_width=True):
            st.switch_page("pages/2_📜_Markdown_Viewer.py")

    with col3:
        st.markdown(
            """
            <div style="text-align: center; padding: 1.5rem;">
                <h2 style="font-size: 2.5rem;">⚙️</h2>
                <h3>Configure</h3>
                <p style="color: #888;">Customize conversion settings, output paths, and preferences.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Settings →", key="btn_settings", use_container_width=True):
            st.switch_page("pages/3_⚙️_Settings.py")

    with col4:
        st.markdown(
            """
            <div style="text-align: center; padding: 1.5rem;">
                <h2 style="font-size: 2.5rem;">🧩</h2>
                <h3>Worksheet Splitter</h3>
                <p style="color: #888;">Upload textbook PDFs and split them into worksheet-wise PDF files.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Splitter →", key="btn_splitter", use_container_width=True):
            st.switch_page("pages/5_🧩_Worksheet_Splitter.py")

    st.markdown("---")
    st.markdown("## 🚀 Quick Start")
    st.markdown(
        """
        1. **Upload a PDF** — Go to the PDF to MD page to convert documents to Markdown.
        2. **Split Worksheets** — Use the Worksheet Splitter page for textbook worksheet PDFs.
        3. **Download** — Preview and download your outputs from the relevant page.
        """
    )

    st.markdown("## 📊 Recent Activity")
    history = SessionManager.get_conversion_history()
    if history:
        for record in history[:5]:
            status_icon = "✅" if record.get("success") else "❌"
            st.markdown(
                f"""
                <div style="padding: 0.75rem; background-color: #1e1e2e; border-radius: 8px; margin: 0.5rem 0;">
                    {status_icon} <strong>{record.get('input_name', 'Unknown')}</strong>
                    <span style="color: #666; float: right;">{record.get('timestamp', '')[:19]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No conversions yet. Upload a PDF to get started!")

    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #555; font-size: 0.8rem; padding: 1rem 0;">
            <p>Built with Streamlit • Powered by Marker and PyMuPDF</p>
            <p>PDF to Markdown Studio v1.0</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    initialize_app()
    render_home()


if __name__ == "__main__":
    main()
