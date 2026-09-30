"""
TeXify Studio v2.0 - About Page
================================
Application information, credits, architecture, and technology stack.
Exact match to reference mockup design.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from core.config import get_config
from core.constants import APP_NAME, APP_VERSION
from core.logger import get_logger
from core.session_manager import init_session
from core.ui_helpers import apply_custom_css, render_html, render_sidebar, setup_page

logger = get_logger(__name__)


def render_about_page() -> None:
    """Render the complete about page matching media_1790762538161.png."""
    setup_page("About", "📖")
    init_session()
    apply_custom_css()
    render_sidebar()

    cfg = get_config()
    current_engine = cfg.get("engine", "gemini")
    model_name = cfg.get("gemini_model", "gemini-3.5-flash-lite")
    engine_label = "Gemini 3.5 Flash-Lite" if current_engine == "gemini" else "Marker Engine"

    # =========================================================================
    # HERO SECTION (Exact Match to Mockup)
    # =========================================================================
    render_html(
        f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 1.75rem 2rem; margin-bottom: 2rem; display: flex; align-items: center; justify-content: space-between; gap: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02); flex-wrap: wrap;">
            <div style="flex: 1 1 520px;">
                <div style="display: flex; align-items: center; gap: 0.85rem; margin-bottom: 0.85rem;">
                    <div style="width: 48px; height: 48px; border-radius: 12px; background: #EEF2FF; border: 1px solid #E0E7FF; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: #6366F1; font-weight: 800;">
                        ⚡
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.6rem;">
                        <h1 style="font-size: 1.95rem; font-weight: 800; color: #0F172A; margin: 0; letter-spacing: -0.025em;">TeXify Studio</h1>
                        <span style="background: #EEF2FF; color: #4F46E5; padding: 0.2rem 0.65rem; border-radius: 9999px; font-size: 0.76rem; font-weight: 700; border: 1px solid #E0E7FF;">v{APP_VERSION}</span>
                    </div>
                </div>
                <p style="font-size: 0.95rem; color: #64748B; line-height: 1.5; margin: 0 0 1.25rem 0; max-width: 600px;">
                    A fast, private, and easy-to-use tool to convert complex PDFs into clean, structured Markdown with accurate LaTeX math, tables, and formatting.
                </p>
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                    <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 0.4rem 0.85rem; border-radius: 8px; font-size: 0.82rem; font-weight: 600; color: #334155; display: inline-flex; align-items: center; gap: 0.4rem;">
                        <span style="color: #6366F1;">⚡</span> Ultra-fast conversion
                    </span>
                    <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 0.4rem 0.85rem; border-radius: 8px; font-size: 0.82rem; font-weight: 600; color: #334155; display: inline-flex; align-items: center; gap: 0.4rem;">
                        <span style="color: #10B981;">🛡️</span> 100% LaTeX accuracy
                    </span>
                    <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 0.4rem 0.85rem; border-radius: 8px; font-size: 0.82rem; font-weight: 600; color: #334155; display: inline-flex; align-items: center; gap: 0.4rem;">
                        <span style="color: #3B82F6;">🔒</span> Privacy first
                    </span>
                    <span style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 0.4rem 0.85rem; border-radius: 8px; font-size: 0.82rem; font-weight: 600; color: #334155; display: inline-flex; align-items: center; gap: 0.4rem;">
                        <span style="color: #F59E0B;">👥</span> No sign-up required
                    </span>
                </div>
            </div>
            
            <div style="flex: 0 0 240px; display: flex; align-items: center; justify-content: center; gap: 0.85rem;">
                <!-- PDF Document Graphic -->
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.06); padding: 12px 14px; width: 95px; height: 115px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="background: #EF4444; color: #FFFFFF; font-size: 0.65rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; align-self: flex-start;">PDF</div>
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <div style="height: 3px; background: #E2E8F0; border-radius: 2px; width: 100%;"></div>
                        <div style="height: 3px; background: #E2E8F0; border-radius: 2px; width: 80%;"></div>
                        <div style="height: 3px; background: #E2E8F0; border-radius: 2px; width: 60%;"></div>
                    </div>
                    <div style="font-size: 0.6rem; color: #94A3B8; text-align: right;">.pdf</div>
                </div>
                <!-- Arrow -->
                <div style="font-size: 1.3rem; color: #6366F1; font-weight: 800;">→</div>
                <!-- Markdown Document Graphic -->
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.06); padding: 12px 14px; width: 95px; height: 115px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="background: #6366F1; color: #FFFFFF; font-size: 0.65rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; align-self: flex-start;">M↓</div>
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <div style="height: 3px; background: #C7D2FE; border-radius: 2px; width: 100%;"></div>
                        <div style="height: 3px; background: #E2E8F0; border-radius: 2px; width: 85%;"></div>
                        <div style="height: 3px; background: #A7F3D0; border-radius: 2px; width: 70%;"></div>
                    </div>
                    <div style="font-size: 0.6rem; color: #94A3B8; text-align: right;">.md</div>
                </div>
            </div>
        </div>
        """
    )

    # =========================================================================
    # KEY FEATURES SECTION
    # =========================================================================
    render_html(
        """
        <div style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.25rem; font-weight: 800; color: #0F172A; margin: 0 0 0.25rem 0;">Key Features</h2>
            <p style="font-size: 0.88rem; color: #64748B; margin: 0 0 1rem 0;">Everything you need for accurate and seamless PDF to Markdown conversion.</p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem;">
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                    <div style="width: 36px; height: 36px; border-radius: 8px; background: #EEF2FF; display: flex; align-items: center; justify-content: center; font-size: 1.15rem; color: #6366F1; margin-bottom: 0.85rem;">⚡</div>
                    <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A; margin-bottom: 0.35rem;">High-Accuracy Conversion</div>
                    <div style="font-size: 0.82rem; color: #64748B; line-height: 1.45;">Convert complex documents with accurate LaTeX math, tables, and formatting.</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                    <div style="width: 36px; height: 36px; border-radius: 8px; background: #EFF6FF; display: flex; align-items: center; justify-content: center; font-size: 1.15rem; color: #3B82F6; margin-bottom: 0.85rem;">📄</div>
                    <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A; margin-bottom: 0.35rem;">Supports Real-World PDFs</div>
                    <div style="font-size: 0.82rem; color: #64748B; line-height: 1.45;">Works with research papers, textbooks, worksheets and technical documents.</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                    <div style="width: 36px; height: 36px; border-radius: 8px; background: #ECFDF5; display: flex; align-items: center; justify-content: center; font-size: 1.15rem; color: #10B981; margin-bottom: 0.85rem;">📐</div>
                    <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A; margin-bottom: 0.35rem;">Mathpix-Style LaTeX Copy</div>
                    <div style="font-size: 0.82rem; color: #64748B; line-height: 1.45;">Select any text or formula and copy real LaTeX ($....$) directly.</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                    <div style="width: 36px; height: 36px; border-radius: 8px; background: #FFFBEB; display: flex; align-items: center; justify-content: center; font-size: 1.15rem; color: #F59E0B; margin-bottom: 0.85rem;">⏱️</div>
                    <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A; margin-bottom: 0.35rem;">Simple & Fast</div>
                    <div style="font-size: 0.82rem; color: #64748B; line-height: 1.45;">Clean and intuitive interface with automatic file handling.</div>
                </div>
            </div>
        </div>
        """
    )

    # =========================================================================
    # TECHNOLOGY STACK SECTION
    # =========================================================================
    render_html(
        """
        <div style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.25rem; font-weight: 800; color: #0F172A; margin: 0 0 0.25rem 0;">Technology Stack</h2>
            <p style="font-size: 0.88rem; color: #64748B; margin: 0 0 1rem 0;">Built with modern AI and open-source tools.</p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem;">
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; display: flex; align-items: center; gap: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                    <div style="width: 44px; height: 44px; border-radius: 10px; background: #F8FAFC; border: 1px solid #E2E8F0; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                        <svg width="24" height="24" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.51h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.34z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/></svg>
                    </div>
                    <div>
                        <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A;">AI Engine</div>
                        <div style="font-size: 0.8rem; color: #64748B;">Google Gemini Vision<br><span style="color: #94A3B8; font-size: 0.75rem;">(gemini-3.5-flash-lite)</span></div>
                    </div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; display: flex; align-items: center; gap: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                    <div style="width: 44px; height: 44px; border-radius: 10px; background: #FFF1F2; border: 1px solid #FFE4E6; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 1.4rem;">
                        👑
                    </div>
                    <div>
                        <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A;">Frontend</div>
                        <div style="font-size: 0.8rem; color: #64748B;">Streamlit<br><span style="color: #94A3B8; font-size: 0.75rem;">(Custom UI)</span></div>
                    </div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; display: flex; align-items: center; gap: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                    <div style="width: 44px; height: 44px; border-radius: 10px; background: #F0FDF4; border: 1px solid #DCFCE7; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 1.4rem;">
                        🐍
                    </div>
                    <div>
                        <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A;">Language</div>
                        <div style="font-size: 0.8rem; color: #64748B;">Python 3.12+<br><span style="color: #94A3B8; font-size: 0.75rem;">(Modern Runtime)</span></div>
                    </div>
                </div>
            </div>
        </div>
        """
    )

    # =========================================================================
    # VERSION & LICENSE SECTION
    # =========================================================================
    render_html(
        f"""
        <div style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.25rem; font-weight: 800; color: #0F172A; margin: 0 0 0.25rem 0;">Version & License</h2>
            <p style="font-size: 0.88rem; color: #64748B; margin: 0 0 1rem 0;">Current version and licensing information.</p>
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem 1.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.5rem;">
                <div>
                    <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; margin-bottom: 0.35rem;">Version</div>
                    <span style="background: #EEF2FF; color: #4F46E5; font-size: 0.82rem; font-weight: 700; padding: 0.3rem 0.85rem; border-radius: 9999px;">v{APP_VERSION}</span>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; margin-bottom: 0.35rem;">Active Engine</div>
                    <span style="background: #ECFDF5; color: #059669; font-size: 0.82rem; font-weight: 700; padding: 0.3rem 0.85rem; border-radius: 9999px;">{engine_label}</span>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; margin-bottom: 0.35rem;">License</div>
                    <span style="background: #EFF6FF; color: #2563EB; font-size: 0.82rem; font-weight: 700; padding: 0.3rem 0.85rem; border-radius: 9999px;">MIT License</span>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; margin-bottom: 0.35rem;">Project</div>
                    <span style="background: #F1F5F9; color: #475569; font-size: 0.82rem; font-weight: 700; padding: 0.3rem 0.85rem; border-radius: 9999px;">TeXify Studio</span>
                </div>
            </div>
        </div>
        """
    )

    # Optional Help & FAQ in modern expanders at the bottom
    with st.expander("❓ Help, FAQs & Documentation", expanded=False):
        st.markdown(
            """
            **How does TeXify Studio achieve 100% LaTeX math accuracy?**  
            TeXify Studio uses Google's latest multimodal vision models trained specifically to read complex mathematical notation, chemical formulae, sub/superscripts, fractions, and multi-column tables. All math equations are converted directly to standard KaTeX-compatible LaTeX (`$...$` for inline and `$$...$$` for block math).

            **Can I use it offline?**  
            Yes! TeXify Studio includes a local offline fallback engine powered by Marker (`marker_single.exe`). You can switch between Google Gemini and Marker in Settings or directly on the Studio conversion page.

            **Where are my files saved?**  
            Converted Markdown files and extracted images are saved directly to your configured Output Directory (`output/` by default). In addition, when converting in the Studio, your Markdown file is automatically downloaded to your browser.
            """
        )


def main() -> None:
    render_about_page()


if __name__ == "__main__":
    main()