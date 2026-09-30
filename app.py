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
from core.ui_helpers import apply_custom_css, render_html, render_sidebar, setup_page

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

    # =========================================================================
    # HERO SECTION (2-Column Layout matching media_1790760964862.png)
    # =========================================================================
    render_html(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; padding: 0.2rem 0 1rem 0; flex-wrap: wrap;">
            <div style="flex: 1 1 520px; max-width: 580px;">
                <div style="display: inline-flex; align-items: center; gap: 0.45rem; background: #EEF2FF; border: 1px solid #E0E7FF; padding: 0.28rem 0.85rem; border-radius: 9999px; margin-bottom: 0.85rem;">
                    <span style="color: #6366F1; font-size: 0.9rem; font-weight: 800;">⚡</span>
                    <span style="font-size: 0.78rem; font-weight: 700; color: #4F46E5;">Powered by {short_model if current_engine == 'gemini' else 'Marker Engine'}</span>
                </div>
                
                <h1 style="font-size: 2.75rem; font-weight: 900; line-height: 1.15; margin: 0 0 0.85rem 0; letter-spacing: -0.03em; color: #0F172A;">
                    Turn Complex PDFs into<br>
                    <span style="background: linear-gradient(135deg, #4338CA 0%, #6366F1 45%, #A855F7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Flawless Markdown</span>
                </h1>
                
                <p style="font-size: 0.98rem; color: #64748B; line-height: 1.55; margin: 0 0 1.25rem 0; max-width: 520px;">
                    High-precision document conversion with 100% accurate LaTeX math, side-by-side 50:50 comparison, instant Mathpix equation copying, and automatic download.
                </p>
                
                <div style="display: flex; gap: 0.45rem; flex-wrap: wrap;">
                    <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 0.35rem 0.75rem; border-radius: 8px; font-size: 0.78rem; font-weight: 600; color: #334155; box-shadow: 0 1px 3px rgba(0,0,0,0.03); display: inline-flex; align-items: center; gap: 0.35rem;">
                        🎯 100% LaTeX Precision
                    </span>
                    <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 0.35rem 0.75rem; border-radius: 8px; font-size: 0.78rem; font-weight: 600; color: #334155; box-shadow: 0 1px 3px rgba(0,0,0,0.03); display: inline-flex; align-items: center; gap: 0.35rem;">
                        ⚡ ~0.4s per page
                    </span>
                    <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 0.35rem 0.75rem; border-radius: 8px; font-size: 0.78rem; font-weight: 600; color: #334155; box-shadow: 0 1px 3px rgba(0,0,0,0.03); display: inline-flex; align-items: center; gap: 0.35rem;">
                        📋 Mathpix-Style Copy
                    </span>
                    <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 0.35rem 0.75rem; border-radius: 8px; font-size: 0.78rem; font-weight: 600; color: #334155; box-shadow: 0 1px 3px rgba(0,0,0,0.03); display: inline-flex; align-items: center; gap: 0.35rem;">
                        📥 Auto-Download
                    </span>
                    <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 0.35rem 0.75rem; border-radius: 8px; font-size: 0.78rem; font-weight: 600; color: #334155; box-shadow: 0 1px 3px rgba(0,0,0,0.03); display: inline-flex; align-items: center; gap: 0.35rem;">
                        🔒 AI Powered (Gemini)
                    </span>
                </div>
            </div>
            
            <div style="flex: 1 1 380px; max-width: 470px; min-width: 320px; position: relative; display: flex; align-items: center; justify-content: center; padding: 1.5rem 0.5rem;">
                <div style="position: absolute; width: 340px; height: 260px; background: radial-gradient(circle, rgba(168, 85, 247, 0.12) 0%, rgba(99, 102, 241, 0.08) 50%, transparent 75%); border-radius: 50%; pointer-events: none;"></div>
                
                <div style="position: absolute; top: -4px; right: 55px; width: 32px; height: 32px; border-radius: 50%; background: #F5F3FF; border: 1px solid #DDD6FE; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(168, 85, 247, 0.2); font-size: 1rem; color: #9333EA; z-index: 6;">
                    ✨
                </div>

                <div style="display: flex; align-items: center; justify-content: center; position: relative; width: 100%;">
                    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; box-shadow: 0 10px 25px rgba(0,0,0,0.06); padding: 13px 14px; width: 185px; transform: rotate(-3.5deg); position: relative; z-index: 1;">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                            <span style="background: #EF4444; color: #FFFFFF; font-size: 0.65rem; font-weight: 800; padding: 2px 7px; border-radius: 5px; letter-spacing: 0.04em;">PDF</span>
                            <div style="display: flex; flex-direction: column; gap: 3px; align-items: flex-end;">
                                <span style="width: 32px; height: 3px; background: #E2E8F0; border-radius: 2px;"></span>
                                <span style="width: 22px; height: 3px; background: #E2E8F0; border-radius: 2px;"></span>
                            </div>
                        </div>
                        
                        <div style="font-family: 'Times New Roman', serif; font-size: 1.15rem; font-style: italic; color: #0F172A; text-align: center; margin: 10px 0 8px 0; letter-spacing: 0.03em;">
                            ∫<sub>-∞</sub><sup>∞</sup> e<sup>-x²</sup> dx
                        </div>
                        
                        <div style="background: #F8FAFC; border: 1px solid #F1F5F9; border-radius: 8px; padding: 6px 4px 4px 4px; margin-top: 4px;">
                            <svg viewBox="0 0 140 60" style="width: 100%; height: 48px; display: block;">
                                <defs>
                                    <linearGradient id="pdfCurveGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stop-color="#3B82F6" stop-opacity="0.25"/>
                                        <stop offset="100%" stop-color="#3B82F6" stop-opacity="0.02"/>
                                    </linearGradient>
                                </defs>
                                <line x1="8" y1="52" x2="132" y2="52" stroke="#CBD5E1" stroke-width="1"/>
                                <line x1="70" y1="8" x2="70" y2="52" stroke="#CBD5E1" stroke-width="1" stroke-dasharray="2,2"/>
                                <path d="M 12 51 C 42 51, 54 14, 70 14 C 86 14, 98 51, 128 51 Z" fill="url(#pdfCurveGrad)"/>
                                <path d="M 12 51 C 42 51, 54 14, 70 14 C 86 14, 98 51, 128 51" fill="none" stroke="#3B82F6" stroke-width="1.8"/>
                            </svg>
                        </div>
                    </div>

                    <div style="width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg, #6366F1, #8B5CF6); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.45); color: #FFFFFF; font-size: 1.15rem; font-weight: bold; z-index: 5; margin: 0 -16px; border: 2px solid #FFFFFF; flex-shrink: 0;">
                        →
                    </div>

                    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; box-shadow: 0 16px 36px rgba(99,102,241,0.14); padding: 13px 14px; width: 205px; transform: rotate(3deg); position: relative; z-index: 3;">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                            <span style="background: #4F46E5; color: #FFFFFF; font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 5px;">Markdown</span>
                            <span style="background: #2563EB; color: #FFFFFF; font-size: 0.65rem; font-weight: 800; padding: 2px 6px; border-radius: 5px; font-family: monospace;">M↓</span>
                        </div>
                        
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; line-height: 1.5; color: #1E293B;">
                            <div style="font-weight: 700; color: #0F172A;"># Gaussian Integral</div>
                            <div style="color: #64748B; font-size: 0.64rem; margin: 2px 0; word-break: break-all;">\\int_{{-\\infty}}^{{\\infty}} e^{{-x^2}} dx</div>
                            
                            <div style="background: #F8FAFC; border: 1px solid #EEF2FF; border-radius: 6px; padding: 4px; margin: 4px 0;">
                                <svg viewBox="0 0 140 45" style="width: 100%; height: 32px; display: block;">
                                    <path d="M 12 40 C 42 40, 54 10, 70 10 C 86 10, 98 40, 128 40" fill="none" stroke="#6366F1" stroke-width="1.8"/>
                                </svg>
                            </div>
                            
                            <div style="color: #7C3AED; font-weight: 600; font-size: 0.63rem;">![plot](figure1.png)</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    )

    # =========================================================================
    # 3 MAIN WORKSPACE CARDS (Studio, Viewer, Settings)
    # =========================================================================
    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        with st.container(border=True):
            render_html(
                """
                <div style="padding: 0.25rem 0.1rem 0.4rem 0.1rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                        <div style="width: 42px; height: 42px; border-radius: 12px; background: #F5F3FF; display: flex; align-items: center; justify-content: center; font-size: 1.35rem; color: #7C3AED;">
                            ⚡
                        </div>
                        <span style="background: #EEF2FF; color: #6366F1; font-size: 0.7rem; font-weight: 700; padding: 0.22rem 0.65rem; border-radius: 9999px; letter-spacing: 0.04em;">
                            STUDIO
                        </span>
                    </div>
                    <h3 style="margin: 0 0 0.4rem 0; font-size: 1.18rem; font-weight: 800; color: #0F172A;">Conversion Studio</h3>
                    <p style="color: #64748B; font-size: 0.85rem; line-height: 1.48; min-height: 50px; margin: 0 0 0.75rem 0;">
                        Upload PDFs, convert in seconds, and review with 50:50 side-by-side comparison & Mathpix-style LaTeX copy.
                    </p>
                </div>
                """
            )
            if st.button("Launch Studio →", key="btn_studio", type="primary", use_container_width=True):
                st.switch_page("pages/1_⚡_Studio.py")

    with col2:
        with st.container(border=True):
            render_html(
                """
                <div style="padding: 0.25rem 0.1rem 0.4rem 0.1rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                        <div style="width: 42px; height: 42px; border-radius: 12px; background: #FFFBEB; display: flex; align-items: center; justify-content: center; font-size: 1.35rem; color: #D97706;">
                            📄
                        </div>
                        <span style="background: #FEF3C7; color: #D97706; font-size: 0.7rem; font-weight: 700; padding: 0.22rem 0.65rem; border-radius: 9999px; letter-spacing: 0.04em;">
                            VIEWER
                        </span>
                    </div>
                    <h3 style="margin: 0 0 0.4rem 0; font-size: 1.18rem; font-weight: 800; color: #0F172A;">Markdown Viewer</h3>
                    <p style="color: #64748B; font-size: 0.85rem; line-height: 1.48; min-height: 50px; margin: 0 0 0.75rem 0;">
                        Open or paste any Markdown file with KaTeX math rendering, in-document search, and Mathpix equation copy.
                    </p>
                </div>
                """
            )
            if st.button("Open Viewer →", key="btn_viewer", use_container_width=True):
                st.switch_page("pages/2_📜_Viewer.py")

    with col3:
        with st.container(border=True):
            render_html(
                """
                <div style="padding: 0.25rem 0.1rem 0.4rem 0.1rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                        <div style="width: 42px; height: 42px; border-radius: 12px; background: #EFF6FF; display: flex; align-items: center; justify-content: center; font-size: 1.35rem; color: #2563EB;">
                            ⚙️
                        </div>
                        <span style="background: #DBEAFE; color: #2563EB; font-size: 0.7rem; font-weight: 700; padding: 0.22rem 0.65rem; border-radius: 9999px; letter-spacing: 0.04em;">
                            CONFIG
                        </span>
                    </div>
                    <h3 style="margin: 0 0 0.4rem 0; font-size: 1.18rem; font-weight: 800; color: #0F172A;">Studio Settings</h3>
                    <p style="color: #64748B; font-size: 0.85rem; line-height: 1.48; min-height: 50px; margin: 0 0 0.75rem 0;">
                        Configure your Gemini API key, choose models, toggle dark/light theme, and adjust OCR preferences.
                    </p>
                </div>
                """
            )
            if st.button("Open Settings →", key="btn_settings", use_container_width=True):
                st.switch_page("pages/3_⚙️_Settings.py")

    # =========================================================================
    # BOTTOM WORKFLOW PIPELINE (3-Step Pipeline matching mockup)
    # =========================================================================
    with st.container(border=True):
        render_html(
            """
            <div style="padding: 0.35rem 0.35rem;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
                    <div style="display: flex; align-items: center; gap: 0.45rem;">
                        <span style="color: #6366F1; font-size: 1rem;">⚡</span>
                        <span style="font-size: 0.76rem; font-weight: 800; color: #6366F1; letter-spacing: 0.06em; text-transform: uppercase;">
                            3-STEP CONVERSION PIPELINE
                        </span>
                    </div>
                    <span style="background: #EEF2FF; color: #6366F1; font-size: 0.72rem; font-weight: 700; padding: 0.22rem 0.75rem; border-radius: 9999px;">
                        ⚡ Fast • Accurate • Automated
                    </span>
                </div>
                
                <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; flex-wrap: wrap;">
                    
                    <div style="flex: 1 1 240px; display: flex; align-items: flex-start; gap: 0.75rem;">
                        <div style="background: #EEF2FF; color: #6366F1; width: 22px; height: 22px; border-radius: 50%; font-weight: 800; font-size: 0.75rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 10px;">
                            1
                        </div>
                        <div style="background: #EFF6FF; color: #2563EB; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; flex-shrink: 0;">
                            📤
                        </div>
                        <div>
                            <div style="font-weight: 800; font-size: 0.94rem; color: #0F172A; margin-bottom: 0.2rem;">Drop Your PDF</div>
                            <div style="color: #64748B; font-size: 0.8rem; line-height: 1.45;">Upload worksheets, exam papers, textbooks, or scientific articles in the Studio.</div>
                        </div>
                    </div>

                    <div style="color: #CBD5E1; font-size: 1.3rem; font-weight: bold; padding: 0 0.2rem;">
                        →
                    </div>

                    <div style="flex: 1 1 240px; display: flex; align-items: flex-start; gap: 0.75rem;">
                        <div style="background: #EEF2FF; color: #6366F1; width: 22px; height: 22px; border-radius: 50%; font-weight: 800; font-size: 0.75rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 10px;">
                            2
                        </div>
                        <div style="background: #F5F3FF; color: #7C3AED; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; flex-shrink: 0;">
                            📑
                        </div>
                        <div>
                            <div style="font-weight: 800; font-size: 0.94rem; color: #0F172A; margin-bottom: 0.2rem;">AI Vision OCR & KaTeX</div>
                            <div style="color: #64748B; font-size: 0.8rem; line-height: 1.45;">Gemini extracts equations, fractions, matrices, and tables with 100% LaTeX fidelity.</div>
                        </div>
                    </div>

                    <div style="color: #CBD5E1; font-size: 1.3rem; font-weight: bold; padding: 0 0.2rem;">
                        →
                    </div>

                    <div style="flex: 1 1 240px; display: flex; align-items: flex-start; gap: 0.75rem;">
                        <div style="background: #EEF2FF; color: #6366F1; width: 22px; height: 22px; border-radius: 50%; font-weight: 800; font-size: 0.75rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 10px;">
                            3
                        </div>
                        <div style="background: #EFF6FF; color: #2563EB; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; flex-shrink: 0;">
                            ✅
                        </div>
                        <div>
                            <div style="font-weight: 800; font-size: 0.94rem; color: #0F172A; margin-bottom: 0.2rem;">Side-by-Side Review & Auto-Save</div>
                            <div style="color: #64748B; font-size: 0.8rem; line-height: 1.45;">Inspect original PDF vs Markdown, click any math to copy LaTeX, and auto-download .md.</div>
                        </div>
                    </div>

                </div>
            </div>
            """
        )

    # Activity Shelf (only shown when conversions exist in session)
    history = SessionManager.get_conversion_history()
    if history:
        with st.container(border=True):
            render_html(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="font-size: 0.82rem; font-weight: 700; color: #0F172A;">📊 Recent Activity in this Session</span>
                    <span style="font-size: 0.75rem; color: #64748B;">Saved in memory</span>
                </div>
                """
            )
            for record in history[:4]:
                status_icon = "✅" if record.get("success") else "❌"
                file_name = record.get("input_name", "Document.pdf")
                timestamp = record.get("timestamp", "")[:19].replace("T", " ")
                engine_used = record.get("engine", "gemini").capitalize()
                render_html(
                    f"""
                    <div style="padding: 0.45rem 0.7rem; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 7px; margin-bottom: 0.35rem; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="margin-right: 0.35rem;">{status_icon}</span>
                            <strong style="font-size: 0.85rem; color: #0F172A;">{file_name}</strong>
                            <span style="font-size: 0.72rem; color: #64748B; margin-left: 0.4rem;">({engine_used})</span>
                        </div>
                        <span style="color: #64748B; font-size: 0.75rem;">{timestamp}</span>
                    </div>
                    """
                )

    # Clean, tight SaaS footer
    render_html(
        f"""
        <div style="text-align: center; color: #94A3B8; font-size: 0.72rem; padding: 0.75rem 0 0.5rem 0; margin-top: 0.75rem; border-top: 1px solid #E2E8F0; opacity: 0.85;">
            <span>{APP_NAME} v{APP_VERSION} • High-Fidelity Math & Document Intelligence</span>
            <span style="margin: 0 0.4rem;">•</span>
            <span>Powered by <strong>Google Gemini Vision</strong> & <strong>Marker</strong></span>
        </div>
        """
    )


def main() -> None:
    initialize_app()
    render_home()


if __name__ == "__main__":
    main()
