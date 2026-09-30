"""
TeXify Studio v2.0 - Main Application
======================================
Entry point for the TeXify Studio application.
High-precision PDF to Markdown conversion with 100% LaTeX math accuracy.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
os.environ["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + os.environ.get("PYTHONPATH", "")

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

    # Tight, modern SaaS Hero Section
    st.markdown(
        f"""
        <div style="text-align: center; padding: 0.5rem 0.5rem 0.75rem 0.5rem; max-width: 820px; margin: 0 auto;">
            <div style="display: inline-flex; align-items: center; gap: 0.4rem; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); padding: 0.25rem 0.8rem; border-radius: 9999px; margin-bottom: 0.65rem;">
                <span style="width: 7px; height: 7px; border-radius: 50%; background: #10B981; box-shadow: 0 0 6px #10B981; display: inline-block;"></span>
                <span style="font-size: 0.76rem; font-weight: 700; color: #818CF8; letter-spacing: 0.05em; text-transform: uppercase;">
                    ⚡ {APP_NAME} v{APP_VERSION} • MATH VISION AI
                </span>
            </div>
            <h1 style="font-size: 2.35rem; font-weight: 800; line-height: 1.16; margin: 0 0 0.5rem 0; letter-spacing: -0.03em;">
                Turn Complex PDFs into <span style="background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Flawless Markdown</span>
            </h1>
            <p style="font-size: 1.02rem; color: var(--text-secondary, #94A3B8); line-height: 1.5; margin: 0 auto 0.85rem auto; max-width: 680px;">
                High-precision document conversion with 100% accurate LaTeX math, side-by-side 50:50 comparison, instant Mathpix equation copying, and automatic download.
            </p>
            <div style="display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap;">
                <span style="background: var(--surface-alt, rgba(255,255,255,0.03)); border: 1px solid var(--border, rgba(255,255,255,0.08)); padding: 0.25rem 0.75rem; border-radius: 7px; font-size: 0.78rem; color: var(--text-secondary, #aaa);">
                    ⚡ Active AI: <strong style="color: {'#818CF8' if current_engine == 'gemini' else '#10B981'};">{short_model if current_engine == 'gemini' else 'Marker (Offline)'}</strong>
                </span>
                <span style="background: var(--surface-alt, rgba(255,255,255,0.03)); border: 1px solid var(--border, rgba(255,255,255,0.08)); padding: 0.25rem 0.75rem; border-radius: 7px; font-size: 0.78rem; color: var(--text-secondary, #aaa);">
                    🧮 LaTeX Math: <strong style="color: #10B981;">100% Precision ($...$)</strong>
                </span>
                <span style="background: var(--surface-alt, rgba(255,255,255,0.03)); border: 1px solid var(--border, rgba(255,255,255,0.08)); padding: 0.25rem 0.75rem; border-radius: 7px; font-size: 0.78rem; color: var(--text-secondary, #aaa);">
                    ⏱️ Speed: <strong style="color: #6366F1;">~0.4s / page</strong>
                </span>
                <span style="background: var(--surface-alt, rgba(255,255,255,0.03)); border: 1px solid var(--border, rgba(255,255,255,0.08)); padding: 0.25rem 0.75rem; border-radius: 7px; font-size: 0.78rem; color: var(--text-secondary, #aaa);">
                    📥 Auto-Download: <strong style="color: #EC4899;">Enabled</strong>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3 Main Workspaces (Studio, Viewer, Settings)
    col1, col2, col3 = st.columns(3, gap="small")

    with col1:
        with st.container(border=True):
            st.markdown(
                """
                <div style="padding: 0.2rem 0.1rem 0.4rem 0.1rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.5rem;">⚡</span>
                        <span style="background: rgba(99, 102, 241, 0.12); color: #818CF8; font-size: 0.7rem; font-weight: 700; padding: 0.18rem 0.55rem; border-radius: 9999px; letter-spacing: 0.04em;">STUDIO</span>
                    </div>
                    <h3 style="margin: 0 0 0.35rem 0; font-size: 1.15rem; font-weight: 700;">Conversion Studio</h3>
                    <p style="color: var(--text-secondary, #888); font-size: 0.85rem; line-height: 1.45; min-height: 48px; margin: 0 0 0.5rem 0;">
                        Upload PDFs, convert in seconds, and review with 50:50 side-by-side comparison & Mathpix-style LaTeX copy.
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
                <div style="padding: 0.2rem 0.1rem 0.4rem 0.1rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.5rem;">📜</span>
                        <span style="background: rgba(245, 158, 11, 0.12); color: #F59E0B; font-size: 0.7rem; font-weight: 700; padding: 0.18rem 0.55rem; border-radius: 9999px; letter-spacing: 0.04em;">VIEWER</span>
                    </div>
                    <h3 style="margin: 0 0 0.35rem 0; font-size: 1.15rem; font-weight: 700;">Markdown Viewer</h3>
                    <p style="color: var(--text-secondary, #888); font-size: 0.85rem; line-height: 1.45; min-height: 48px; margin: 0 0 0.5rem 0;">
                        Open or paste any Markdown file with KaTeX math rendering, in-document search, and Mathpix equation copy.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open Viewer →", key="btn_viewer", use_container_width=True):
                st.switch_page("pages/2_📜_Viewer.py")

    with col3:
        with st.container(border=True):
            st.markdown(
                """
                <div style="padding: 0.2rem 0.1rem 0.4rem 0.1rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.5rem;">⚙️</span>
                        <span style="background: rgba(139, 92, 246, 0.12); color: #8B5CF6; font-size: 0.7rem; font-weight: 700; padding: 0.18rem 0.55rem; border-radius: 9999px; letter-spacing: 0.04em;">CONFIG</span>
                    </div>
                    <h3 style="margin: 0 0 0.35rem 0; font-size: 1.15rem; font-weight: 700;">Studio Settings</h3>
                    <p style="color: var(--text-secondary, #888); font-size: 0.85rem; line-height: 1.45; min-height: 48px; margin: 0 0 0.5rem 0;">
                        Configure your Gemini API key, choose models, toggle dark/light theme, and adjust OCR preferences.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open Settings →", key="btn_settings", use_container_width=True):
                st.switch_page("pages/3_⚙️_Settings.py")

    # Workflow Section - Full width 3-step pipeline
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="padding: 0.25rem 0.25rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #818CF8; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.75rem;">
                    ⚡ 3-STEP CONVERSION PIPELINE
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.25rem;">
                    <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
                        <div style="background: rgba(99, 102, 241, 0.12); color: #818CF8; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.88rem; flex-shrink: 0;">1</div>
                        <div>
                            <div style="font-weight: 700; font-size: 0.92rem; color: var(--text-primary); margin-bottom: 0.2rem;">Drop Your PDF</div>
                            <div style="color: var(--text-secondary, #888); font-size: 0.82rem; line-height: 1.45;">Upload worksheets, exam papers, textbooks, or scientific articles in the Studio.</div>
                        </div>
                    </div>
                    <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
                        <div style="background: rgba(99, 102, 241, 0.12); color: #818CF8; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.88rem; flex-shrink: 0;">2</div>
                        <div>
                            <div style="font-weight: 700; font-size: 0.92rem; color: var(--text-primary); margin-bottom: 0.2rem;">AI Vision OCR & KaTeX</div>
                            <div style="color: var(--text-secondary, #888); font-size: 0.82rem; line-height: 1.45;">Gemini extracts equations, fractions, matrices, and tables with 100% LaTeX fidelity.</div>
                        </div>
                    </div>
                    <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
                        <div style="background: rgba(99, 102, 241, 0.12); color: #818CF8; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.88rem; flex-shrink: 0;">3</div>
                        <div>
                            <div style="font-weight: 700; font-size: 0.92rem; color: var(--text-primary); margin-bottom: 0.2rem;">Side-by-Side Review & Auto-Save</div>
                            <div style="color: var(--text-secondary, #888); font-size: 0.82rem; line-height: 1.45;">Inspect original PDF vs Markdown, click any math to copy LaTeX, and auto-download .md.</div>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Activity Shelf (only shown when conversions exist in session, avoiding empty gray box)
    history = SessionManager.get_conversion_history()
    if history:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="font-size: 0.82rem; font-weight: 700; color: var(--text-primary);">📊 Recent Activity in this Session</span>
                    <span style="font-size: 0.75rem; color: var(--text-muted);">Saved in memory</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for record in history[:4]:
                status_icon = "✅" if record.get("success") else "❌"
                file_name = record.get("input_name", "Document.pdf")
                timestamp = record.get("timestamp", "")[:19].replace("T", " ")
                engine_used = record.get("engine", "gemini").capitalize()
                st.markdown(
                    f"""
                    <div style="padding: 0.45rem 0.7rem; background: var(--surface-hover, rgba(255,255,255,0.03)); border: 1px solid var(--border, rgba(255,255,255,0.06)); border-radius: 7px; margin-bottom: 0.35rem; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="margin-right: 0.35rem;">{status_icon}</span>
                            <strong style="font-size: 0.85rem;">{file_name}</strong>
                            <span style="font-size: 0.72rem; color: var(--text-muted); margin-left: 0.4rem;">({engine_used})</span>
                        </div>
                        <span style="color: var(--text-muted); font-size: 0.75rem;">{timestamp}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Clean, tight SaaS footer
    st.markdown(
        f"""
        <div style="text-align: center; color: var(--text-muted); font-size: 0.72rem; padding: 0.75rem 0 0.5rem 0; margin-top: 0.75rem; border-top: 1px solid var(--border, rgba(255,255,255,0.06)); opacity: 0.8;">
            <span>{APP_NAME} v{APP_VERSION} • High-Fidelity Math & Document Intelligence</span>
            <span style="margin: 0 0.4rem;">•</span>
            <span>Powered by <strong>Google Gemini Vision</strong> & <strong>Marker</strong></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    initialize_app()
    render_home()


if __name__ == "__main__":
    main()
