"""
TeXify Studio v2.0 - Main Application
======================================
Entry point for the TeXify Studio application.
High-precision PDF to Markdown conversion with 100% LaTeX math accuracy.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from core.constants import APP_NAME, APP_VERSION, PAGE_ICON
from core.config import get_config
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

    cfg = get_config()
    current_engine = cfg.get("engine", "gemini")
    current_model = cfg.get("gemini_model", "gemini-3.5-flash-lite")
    short_model = "Gemini 3.5 Flash-Lite" if "lite" in current_model else ("Gemini 3.5 Flash" if "3.5" in current_model else "Gemini Vision")

    # Hero Section
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2.5rem 1rem 2rem 1rem; max-width: 820px; margin: 0 auto;">
            <div style="display: inline-flex; align-items: center; gap: 0.5rem; background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.28); padding: 0.35rem 0.95rem; border-radius: 9999px; margin-bottom: 1.25rem;">
                <span style="font-size: 0.82rem; font-weight: 700; color: #818CF8; letter-spacing: 0.04em; text-transform: uppercase;">
                    ⚡ {APP_NAME} v{APP_VERSION}
                </span>
            </div>
            <h1 style="font-size: 2.85rem; font-weight: 800; line-height: 1.15; margin-bottom: 1rem; letter-spacing: -0.03em;">
                Turn Complex PDFs into <span style="background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Flawless Markdown</span>
            </h1>
            <p style="font-size: 1.15rem; color: var(--text-secondary, #94A3B8); line-height: 1.6; margin-bottom: 1.5rem;">
                High-precision document conversion with 100% accurate LaTeX math ($...$), side-by-side 50:50 comparison, and Mathpix-style equation copying.
            </p>
            <div style="display: flex; justify-content: center; gap: 0.75rem; flex-wrap: wrap;">
                <span style="background: var(--surface-alt, rgba(255,255,255,0.04)); border: 1px solid var(--border, rgba(255,255,255,0.1)); padding: 0.35rem 0.85rem; border-radius: 8px; font-size: 0.82rem; color: var(--text-secondary, #aaa);">
                    ⚡ Active Engine: <strong style="color: {'#818CF8' if current_engine == 'gemini' else '#10B981'};">{short_model if current_engine == 'gemini' else 'Marker (Offline)'}</strong>
                </span>
                <span style="background: var(--surface-alt, rgba(255,255,255,0.04)); border: 1px solid var(--border, rgba(255,255,255,0.1)); padding: 0.35rem 0.85rem; border-radius: 8px; font-size: 0.82rem; color: var(--text-secondary, #aaa);">
                    🧮 LaTeX Math: <strong style="color: #10B981;">$ ... $ & $$ ... $$</strong>
                </span>
                <span style="background: var(--surface-alt, rgba(255,255,255,0.04)); border: 1px solid var(--border, rgba(255,255,255,0.1)); padding: 0.35rem 0.85rem; border-radius: 8px; font-size: 0.82rem; color: var(--text-secondary, #aaa);">
                    ⏱️ Speed: <strong style="color: #6366F1;">~0.5s / page</strong>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # 3 Main Workspaces (Studio, Library, Settings)
    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        with st.container(border=True):
            st.markdown(
                """
                <div style="padding: 0.5rem 0.25rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                        <span style="font-size: 2rem;">⚡</span>
                        <span style="background: rgba(99, 102, 241, 0.12); color: #818CF8; font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 9999px;">STUDIO</span>
                    </div>
                    <h3 style="margin-top: 0; margin-bottom: 0.4rem; font-size: 1.2rem;">Conversion Studio</h3>
                    <p style="color: var(--text-secondary, #888); font-size: 0.88rem; line-height: 1.5; min-height: 48px;">
                        Upload PDFs, convert in seconds, and review with side-by-side 50:50 comparison & Mathpix-style LaTeX copy.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Launch Studio →", key="btn_studio", type="primary", use_container_width=True):
                st.switch_page("pages/1_⚡_Studio.py")

    with col2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="padding: 0.5rem 0.25rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                        <span style="font-size: 2rem;">📚</span>
                        <span style="background: rgba(245, 158, 11, 0.12); color: #F59E0B; font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 9999px;">LIBRARY</span>
                    </div>
                    <h3 style="margin-top: 0; margin-bottom: 0.4rem; font-size: 1.2rem;">Document Library</h3>
                    <p style="color: var(--text-secondary, #888); font-size: 0.88rem; line-height: 1.5; min-height: 48px;">
                        Explore previously converted documents, inspect rendered formulas, edit content, and export files.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open Library →", key="btn_library", use_container_width=True):
                st.switch_page("pages/2_📚_Library.py")

    with col3:
        with st.container(border=True):
            st.markdown(
                """
                <div style="padding: 0.5rem 0.25rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                        <span style="font-size: 2rem;">⚙️</span>
                        <span style="background: rgba(139, 92, 246, 0.12); color: #8B5CF6; font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 9999px;">CONFIG</span>
                    </div>
                    <h3 style="margin-top: 0; margin-bottom: 0.4rem; font-size: 1.2rem;">Studio Settings</h3>
                    <p style="color: var(--text-secondary, #888); font-size: 0.88rem; line-height: 1.5; min-height: 48px;">
                        Configure your Gemini API key, choose models, toggle dark/light theme, and adjust OCR preferences.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open Settings →", key="btn_settings", use_container_width=True):
                st.switch_page("pages/3_⚙️_Settings.py")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Two column layout: How It Works + Recent Activity
    guide_col, history_col = st.columns([1, 1], gap="medium")

    with guide_col:
        st.markdown("### 🚀 Quick Workflow")
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; flex-direction: column; gap: 0.9rem; padding: 0.25rem;">
                    <div style="display: flex; gap: 0.8rem; align-items: flex-start;">
                        <div style="background: rgba(99, 102, 241, 0.15); color: #818CF8; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; flex-shrink: 0;">1</div>
                        <div>
                            <strong style="font-size: 0.95rem;">Drag & Drop PDF</strong>
                            <p style="color: var(--text-secondary, #888); font-size: 0.83rem; margin: 0.15rem 0 0 0;">Upload any math worksheet, textbook chapter, or research paper in the Studio.</p>
                        </div>
                    </div>
                    <div style="display: flex; gap: 0.8rem; align-items: flex-start;">
                        <div style="background: rgba(99, 102, 241, 0.15); color: #818CF8; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; flex-shrink: 0;">2</div>
                        <div>
                            <strong style="font-size: 0.95rem;">Sub-Second AI Conversion</strong>
                            <p style="color: var(--text-secondary, #888); font-size: 0.83rem; margin: 0.15rem 0 0 0;">Gemini 3.6 Flash converts dense mathematical pages in seconds with 100% accurate LaTeX.</p>
                        </div>
                    </div>
                    <div style="display: flex; gap: 0.8rem; align-items: flex-start;">
                        <div style="background: rgba(99, 102, 241, 0.15); color: #818CF8; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; flex-shrink: 0;">3</div>
                        <div>
                            <strong style="font-size: 0.95rem;">50:50 Review & Mathpix Copy</strong>
                            <p style="color: var(--text-secondary, #888); font-size: 0.83rem; margin: 0.15rem 0 0 0;">Compare original PDF and Markdown side-by-side; select text or click any formula to copy LaTeX (<code>$...$</code>).</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with history_col:
        st.markdown("### 📊 Recent Activity")
        with st.container(border=True):
            history = SessionManager.get_conversion_history()
            if history:
                for record in history[:4]:
                    status_icon = "✅" if record.get("success") else "❌"
                    file_name = record.get("input_name", "Document.pdf")
                    timestamp = record.get("timestamp", "")[:19].replace("T", " ")
                    engine_used = record.get("engine", "gemini").capitalize()
                    st.markdown(
                        f"""
                        <div style="padding: 0.55rem 0.75rem; background: var(--surface-hover, rgba(255,255,255,0.03)); border: 1px solid var(--border, rgba(255,255,255,0.06)); border-radius: 8px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="margin-right: 0.35rem;">{status_icon}</span>
                                <strong style="font-size: 0.88rem;">{file_name}</strong>
                                <span style="font-size: 0.72rem; color: var(--text-muted, #777); margin-left: 0.4rem;">({engine_used})</span>
                            </div>
                            <span style="color: var(--text-muted, #666); font-size: 0.75rem;">{timestamp}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    """
                    <div style="text-align: center; padding: 2rem 1rem; color: var(--text-muted, #888);">
                        <p style="font-size: 1.5rem; margin-bottom: 0.5rem;">📂</p>
                        <p style="font-size: 0.9rem; margin: 0;">No conversions recorded yet.</p>
                        <p style="font-size: 0.78rem; color: var(--text-muted, #666);">Converted documents will appear here.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="text-align: center; color: var(--text-muted, #666); font-size: 0.78rem; padding: 1.5rem 0 1rem 0; border-top: 1px solid var(--border, rgba(255,255,255,0.06));">
            <p style="margin: 0.25rem 0;">Built with Streamlit • Powered by <strong>Google Gemini Vision</strong> & <strong>Marker</strong></p>
            <p style="margin: 0.25rem 0;">{APP_NAME} v{APP_VERSION} • High-Fidelity Math & Document Intelligence</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    initialize_app()
    render_home()


if __name__ == "__main__":
    main()
