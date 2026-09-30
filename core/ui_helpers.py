"""
PDF_to_MD_Studio v1.0 - UI Helpers
==================================
Streamlit-specific UI components, styling, and helper functions
for consistent interface across all pages.
"""

import textwrap
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple

import streamlit as st
from streamlit.errors import StreamlitAPIException

from core.constants import (
    APP_NAME,
    APP_VERSION,
    MESSAGES,
    PAGE_ICON,
    PRIMARY_COLOR,
)
from core.logger import get_logger

logger = get_logger(__name__)


def render_html(html_str: str) -> None:
    """
    Render raw HTML safely without Markdown parser converting leading spaces
    or empty newlines into code blocks.
    """
    clean_html = textwrap.dedent(html_str).strip()
    if hasattr(st, "html"):
        st.html(clean_html)
    else:
        st.markdown(clean_html, unsafe_allow_html=True)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

def setup_page(page_title: str, page_icon: str = PAGE_ICON, layout: str = "wide") -> None:
    """
    Configure Streamlit page settings.
    
    Args:
        page_title: Title for this specific page
        page_icon: Emoji icon for the page
        layout: Page layout ('wide' or 'centered')
    """
    try:
        st.set_page_config(
            page_title=f"{page_title} | {APP_NAME}",
            page_icon=page_icon,
            layout=layout,
            initial_sidebar_state="expanded",
        )
    except StreamlitAPIException:
        # Streamlit allows this only once and requires it before other UI calls.
        # The app can still render correctly if the page was already configured.
        pass


# =============================================================================
# CUSTOM STYLING
# =============================================================================

def apply_custom_css() -> None:
    """
    Apply custom CSS styling to the Streamlit app.

    Reads the user's chosen theme (light/dark) from session state and builds
    the CSS palette accordingly, with explicit !important background overrides
    on Streamlit's own containers. This is necessary because .streamlit/config.toml
    is a static file read once at server startup - it CANNOT be changed live by
    a button click, so the actual light/dark switching has to happen entirely
    here in CSS, driven by session state, rather than via config.toml.
    """
    from core.session_manager import SessionManager

    theme = SessionManager.get_theme()  # "light" or "dark"

    if theme == "dark":
        palette = {
            "surface": "#0B0F19",
            "surface_alt": "#111827",
            "border": "rgba(255, 255, 255, 0.08)",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "text_muted": "#64748B",
            "sidebar_bg": "#070A10",
            "shadow_sm": "0 2px 8px rgba(0, 0, 0, 0.4)",
            "shadow_md": "0 8px 30px rgba(0, 0, 0, 0.6)",
            "code_bg": "#111827",
            "table_header_bg": "#111827",
        }
    else:
        palette = {
            "surface": "#FBFBFE",
            "surface_alt": "#FFFFFF",
            "border": "#E2E8F0",
            "text_primary": "#0F172A",
            "text_secondary": "#64748B",
            "text_muted": "#94A3B8",
            "sidebar_bg": "#FAFAFD",
            "shadow_sm": "0 1px 3px rgba(0, 0, 0, 0.04)",
            "shadow_md": "0 8px 24px rgba(0, 0, 0, 0.06)",
            "code_bg": "#F8FAFC",
            "table_header_bg": "#F1F5F9",
        }

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        :root {{
            --accent: {PRIMARY_COLOR};
            --accent-gradient: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
            --accent-soft: rgba(99, 102, 241, 0.08);
            --accent-soft-strong: rgba(99, 102, 241, 0.16);
            --surface: {palette["surface"]};
            --surface-alt: {palette["surface_alt"]};
            --border: {palette["border"]};
            --text-primary: {palette["text_primary"]};
            --text-secondary: {palette["text_secondary"]};
            --text-muted: {palette["text_muted"]};
            --radius-sm: 8px;
            --radius-md: 14px;
            --radius-lg: 20px;
            --shadow-sm: {palette["shadow_sm"]};
            --shadow-md: {palette["shadow_md"]};
            --shadow-hover: 0 10px 30px rgba(99, 102, 241, 0.25);
        }}

        [data-testid="stAppViewContainer"], .stApp, [data-testid="stHeader"] {{
            background-color: var(--surface) !important;
        }}
        [data-testid="stSidebar"] {{
            background-color: {palette["sidebar_bg"]} !important;
            border-right: 1px solid var(--border) !important;
        }}
        [data-testid="stSidebar"] [data-testid="stMetricValue"] {{
            color: var(--accent);
            font-weight: 800;
        }}

        html, body, [class*="css"] {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            color: var(--text-primary);
        }}

        code, pre, .stCodeBlock, .stCode {{
            font-family: 'JetBrains Mono', 'Courier New', monospace !important;
        }}

        /* Main container - tight, modern padding */
        .main .block-container,
        [data-testid="stMainBlockContainer"],
        [data-testid="block-container"] {{
            padding-top: 0.8rem !important;
            padding-bottom: 1.5rem !important;
            max-width: 1220px !important;
        }}

        /* Sidebar container - clean, sleek SaaS look */
        [data-testid="stSidebarContent"] {{
            padding-top: 1rem !important;
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
        }}

        /* Top Brand Header in Sidebar Navigation */
        [data-testid="stSidebarNav"]::before {{
            content: "⚡  TeXify Studio\\A LaTeX • Markdown • AI";
            white-space: pre-wrap;
            display: block;
            font-weight: 800;
            font-size: 1.05rem;
            color: #0F172A;
            padding: 0.15rem 0.5rem 0.85rem 0.5rem;
            margin-bottom: 0.6rem;
            border-bottom: 1px solid #E2E8F0;
            line-height: 1.25;
        }}

        /* Sidebar Navigation Labels - Exact Match to Design */
        [data-testid="stSidebarNav"] ul li:nth-child(1) a span,
        [data-testid="stSidebarNavLink"][href="/"] span,
        [data-testid="stSidebarNavLink"][href=""] span {{
            display: none !important;
        }}
        [data-testid="stSidebarNav"] ul li:nth-child(1) a::after,
        [data-testid="stSidebarNavLink"][href="/"]::after,
        [data-testid="stSidebarNavLink"][href=""]::after {{
            content: "🏠  Home" !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            color: inherit !important;
        }}

        [data-testid="stSidebarNav"] ul li:nth-child(2) a span {{
            display: none !important;
        }}
        [data-testid="stSidebarNav"] ul li:nth-child(2) a::after {{
            content: "⚡  Conversion Studio" !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            color: inherit !important;
        }}

        [data-testid="stSidebarNav"] ul li:nth-child(3) a span {{
            display: none !important;
        }}
        [data-testid="stSidebarNav"] ul li:nth-child(3) a::after {{
            content: "📄  Viewer" !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            color: inherit !important;
        }}

        [data-testid="stSidebarNav"] ul li:nth-child(4) a span {{
            display: none !important;
        }}
        [data-testid="stSidebarNav"] ul li:nth-child(4) a::after {{
            content: "⚙️  Settings" !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            color: inherit !important;
        }}

        [data-testid="stSidebarNav"] ul li:nth-child(5) a span {{
            display: none !important;
        }}
        [data-testid="stSidebarNav"] ul li:nth-child(5) a::after {{
            content: "📖  About" !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            color: inherit !important;
        }}

        /* Sleek modern sidebar navigation items */
        [data-testid="stSidebarNav"] {{
            padding-top: 0.25rem !important;
            margin-bottom: 0.4rem !important;
        }}
        [data-testid="stSidebarNavLink"] {{
            border-radius: 10px !important;
            padding: 0.52rem 0.85rem !important;
            margin-bottom: 0.2rem !important;
            color: #475569 !important;
            transition: all 0.15s ease !important;
        }}
        [data-testid="stSidebarNavLink"]::after {{
            color: #475569 !important;
        }}
        [data-testid="stSidebarNavLink"]:hover {{
            background-color: #F1F5F9 !important;
            color: #0F172A !important;
        }}
        [data-testid="stSidebarNavLink"]:hover::after {{
            color: #0F172A !important;
        }}
        [data-testid="stSidebarNavLink"][aria-current="page"] {{
            background: #EEF2FF !important;
            color: #4F46E5 !important;
            font-weight: 700 !important;
        }}
        [data-testid="stSidebarNavLink"][aria-current="page"]::after {{
            color: #4F46E5 !important;
            font-weight: 700 !important;
        }}

        /* Typography */
        h1, h2, h3 {{
            color: var(--text-primary) !important;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}
        h1 {{ font-weight: 800; }}
        p, li {{ color: var(--text-primary); }}
        .stCaptionContainer, [data-testid="stCaptionContainer"] {{
            color: var(--text-muted) !important;
        }}

        /* Buttons */
        .stButton > button {{
            border-radius: 10px !important;
            padding: 0.6rem 1.4rem !important;
            font-weight: 700 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            border: 1px solid #E2E8F0 !important;
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
        }}
        .stButton > button:hover {{
            background-color: #F8FAFC !important;
            border-color: #CBD5E1 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        }}
        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
            border: none !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
            font-weight: 700 !important;
        }}
        .stButton > button[kind="primary"]:hover {{
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5) !important;
            transform: translateY(-2px) !important;
        }}

        /* Bordered containers (st.container(border=True)) -> polished cards */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 14px !important;
            border: 1px solid #E2E8F0 !important;
            background-color: #FFFFFF !important;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03) !important;
            transition: all 0.2s ease !important;
        }}



        /* File uploader */
        [data-testid="stFileUploaderDropzone"] {{
            border: 2px dashed rgba(99, 102, 241, 0.4) !important;
            border-radius: var(--radius-md) !important;
            background: var(--surface-alt) !important;
            padding: 2.5rem 1rem !important;
            transition: all 0.25s ease;
        }}
        [data-testid="stFileUploaderDropzone"]:hover {{
            border-color: #6366F1 !important;
            background: rgba(99, 102, 241, 0.05) !important;
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.15);
        }}

        /* Alerts */
        .stSuccess, .stError, .stWarning, .stInfo {{
            border-radius: var(--radius-sm);
            padding: 0.9rem 1.1rem;
            border: 1px solid var(--border);
            box-shadow: var(--shadow-sm);
        }}

        /* Metrics */
        [data-testid="stMetric"] {{
            background: var(--surface-alt);
            border-radius: var(--radius-sm);
            padding: 0.9rem 1.1rem;
            border: 1px solid var(--border);
        }}
        [data-testid="stMetricValue"] {{
            font-weight: 800;
            color: var(--text-primary);
        }}
        [data-testid="stMetricLabel"] {{
            color: var(--text-secondary);
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            border-bottom: 1px solid var(--border);
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: var(--radius-sm) var(--radius-sm) 0 0;
            font-weight: 600;
            color: var(--text-secondary);
            padding: 0.6rem 1.2rem;
            transition: all 0.2s ease;
        }}
        .stTabs [aria-selected="true"] {{
            color: var(--accent) !important;
            border-bottom: 2px solid var(--accent);
            background: var(--accent-soft);
        }}

        /* Text inputs / selects */
        .stTextInput input, .stSelectbox [data-baseweb="select"], .stNumberInput input {{
            background-color: var(--surface) !important;
            color: var(--text-primary) !important;
            border-color: var(--border) !important;
        }}

        /* Progress bar */
        .stProgress > div > div {{
            background-color: var(--accent);
            border-radius: 6px;
        }}
        .stProgress > div {{
            border-radius: 6px;
            background-color: var(--border);
        }}

        /* Full width for iframes and custom HTML components */
        iframe, [data-testid="stCustomComponentV1"], [data-testid="stCustomComponentV1"] iframe {{
            width: 100% !important;
            min-width: 100% !important;
            display: block;
        }}

        /* Stage checklist panel */
        .conversion-panel {{
            background: var(--surface);
            border-radius: var(--radius-lg);
            padding: 1.5rem 1.75rem;
            margin: 1rem 0;
            border: 1px solid var(--border);
            box-shadow: var(--shadow-md);
        }}
        .conversion-panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        .conversion-panel-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-primary);
        }}
        .conversion-panel-timer {{
            font-size: 0.85rem;
            font-family: 'JetBrains Mono', monospace;
            color: var(--accent);
            background: var(--accent-soft);
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
        }}
        .stage-row {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.35rem 0;
            font-size: 0.9rem;
        }}
        .stage-row.pending {{ color: var(--text-muted); }}
        .stage-row.active {{ color: var(--text-primary); font-weight: 600; }}
        .stage-row.complete {{ color: #1ea672; }}
        .stage-icon {{ width: 1.4rem; text-align: center; }}
        .stage-label {{ flex: 1; }}
        .stage-pct {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            min-width: 3.5rem;
            text-align: right;
        }}
        .stage-mini-bar {{
            width: 60px;
            height: 4px;
            border-radius: 2px;
            background: var(--border);
            overflow: hidden;
        }}
        .stage-mini-bar-fill {{
            height: 100%;
            background: var(--accent);
            border-radius: 2px;
        }}

        /* Feature cards */
        .feature-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1.5rem;
            text-align: center;
            transition: all 0.2s ease;
            box-shadow: var(--shadow-sm);
        }}
        .feature-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-hover);
            border-color: var(--accent);
        }}

        .stCodeBlock {{
            border-radius: var(--radius-sm);
        }}

        /* Hide default Streamlit chrome */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stDeployButton {{display: none;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# SIDEBAR COMPONENTS
# =============================================================================

def render_sidebar() -> None:
    """
    Render the application sidebar with navigation and info.
    Call this on every page.
    """
    with st.sidebar:
        from core.session_manager import SessionManager
        from core.config import get_config

        cfg = get_config()
        engine_type = cfg.get("engine", "gemini")
        if engine_type == "gemini":
            model_name = cfg.get("gemini_model", "gemini-3.5-flash-lite")
            short_model = "Gemini 3.5 Flash-Lite" if "lite" in model_name else ("Gemini 3.5 Flash" if "3.5" in model_name else "Gemini Vision")
            status_card = f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 0.8rem 0.9rem; margin: 1.25rem 0 0.6rem 0; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span style="font-size: 0.68rem; font-weight: 700; color: #64748B; letter-spacing: 0.05em; text-transform: uppercase;">ACTIVE ENGINE</span>
                    <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #10B981; box-shadow: 0 0 6px #10B981;"></span>
                </div>
                <div style="font-size: 0.92rem; font-weight: 800; color: #0F172A;">{short_model}</div>
                <div style="font-size: 0.74rem; color: #64748B; margin-top: 0.2rem;">1,500 free pages/day</div>
                <div style="font-size: 0.74rem; color: #64748B; margin-top: 0.05rem;">~0.4s/page</div>
            </div>
            """
        else:
            status_card = """
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 0.8rem 0.9rem; margin: 1.25rem 0 0.6rem 0; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span style="font-size: 0.68rem; font-weight: 700; color: #94A3B8; letter-spacing: 0.05em; text-transform: uppercase;">ACTIVE ENGINE</span>
                    <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #10B981; box-shadow: 0 0 6px #10B981;"></span>
                </div>
                <div style="font-size: 0.92rem; font-weight: 800; color: #0F172A;">Marker Engine</div>
                <div style="font-size: 0.74rem; color: #64748B; margin-top: 0.2rem;">Local Offline Processing</div>
            </div>
            """

        render_html(status_card)

        history = SessionManager.get_conversion_history()
        if history:
            total = len(history)
            recent = len([h for h in history if h.get("success", False)])
            render_html(
                f"""
                <div style="padding: 0.35rem 0.65rem; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; font-size: 0.75rem; display: flex; justify-content: space-between; margin-bottom: 0.4rem;">
                    <span style="color: #64748B;">Session Activity:</span>
                    <strong style="color: #10B981;">{recent} / {total} converted</strong>
                </div>
                """
            )

        render_html(
            f"""
            <div style="text-align: center; color: #94A3B8; font-size: 0.72rem; padding-top: 0.4rem;">
                <p style="margin: 0; font-weight: 700; color: #64748B;">{APP_NAME} v{APP_VERSION}</p>
                <p style="margin: 0.15rem 0 0 0;">100% LaTeX Math Precision</p>
            </div>
            """
        )


# =============================================================================
# FILE UPLOAD COMPONENTS
# =============================================================================

def file_uploader_area(
    label: str = "Upload PDF",
    key: str = "file_uploader",
    accept_multiple: bool = False,
) -> Any:
    """
    Create a styled file upload area.
    
    Args:
        label: Label text
        key: Streamlit widget key
        accept_multiple: Allow multiple file uploads
        
    Returns:
        Uploaded file(s) or None
    """
    return st.file_uploader(
        label=label,
        type=["pdf"],
        accept_multiple_files=accept_multiple,
        key=key,
        label_visibility="collapsed",
        help="Supports PDF files up to 100MB",
    )


# =============================================================================
# PROGRESS & STATUS
# =============================================================================

def show_progress(
    status_text: str,
    progress_value: float,
    progress_bar: Optional[Any] = None,
    status_placeholder: Optional[Any] = None,
) -> Tuple[Any, Any]:
    """
    Display or update a progress indicator.
    
    Args:
        status_text: Current status message
        progress_value: Progress from 0.0 to 1.0
        progress_bar: Existing progress bar widget (optional)
        status_placeholder: Existing status text widget (optional)
        
    Returns:
        Tuple of (progress_bar, status_placeholder)
    """
    if progress_bar is None:
        progress_bar = st.progress(0.0)
    if status_placeholder is None:
        status_placeholder = st.empty()
    
    progress_bar.progress(min(progress_value, 1.0))
    status_placeholder.markdown(f"**{status_text}**")
    
    return progress_bar, status_placeholder


def render_stage_panel(
    placeholder: Any,
    stages_meta: List[dict],
    stage_state: dict,
    current_stage: Optional[str],
    overall: float,
    elapsed_str: str,
) -> None:
    """
    Render a clean, simple progress display: current stage label + icon,
    elapsed time, and a single progress bar. No checklist, no clutter.

    Args:
        placeholder: An st.empty() container to render into (so it updates
            in place rather than stacking new elements every frame).
        stages_meta: CONVERSION_STAGES list from core.marker_engine
            (each dict has key/label/icon, in pipeline order).
        stage_state: dict of {stage_key: percent_0_to_100} (unused here,
            kept in the signature for compatibility).
        current_stage: key of the currently active stage (or None)
        overall: overall progress, 0.0-1.0
        elapsed_str: pre-formatted elapsed time string, e.g. "1m 24s"
    """
    stage_meta = next((s for s in stages_meta if s["key"] == current_stage), None)
    icon = stage_meta["icon"] if stage_meta else "⏳"
    label = stage_meta["label"] if stage_meta else "Starting up..."
    overall_pct = int(min(max(overall, 0.0), 1.0) * 100)

    html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
        <span style="font-size: 0.95rem; font-weight: 600; color: #f0f0f5;">{icon} {label}</span>
        <span style="font-size: 0.85rem; font-family: 'Courier New', monospace; color: {PRIMARY_COLOR};">
            ⏱️ {elapsed_str} &nbsp;|&nbsp; {overall_pct}%
        </span>
    </div>
    """
    placeholder.markdown(html, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _render_pdf_page_image(pdf_path_str: str, page_num: int, dpi: int = 150) -> Optional[bytes]:
    """Render a single page of a PDF to PNG byte stream via PyMuPDF (fitz)."""
    try:
        import fitz
        doc = fitz.open(pdf_path_str)
        if 0 <= page_num < len(doc):
            pix = doc[page_num].get_pixmap(dpi=dpi)
            return pix.tobytes("png")
    except Exception as e:
        logger.error(f"Error rendering PDF page {page_num}: {e}")
    return None


def render_pdf_preview(pdf_path: Path, height: int = 750) -> None:
    """
    Render a PDF inline with 100% browser compatibility across Chrome, Edge, Safari, Firefox.
    Uses PyMuPDF (fitz) to render crisp, high-resolution page images.
    Features:
    - Continuous scroll mode (all pages rendered in scrollable container)
    - Single-page inspection mode with page jumper
    - Direct PDF download button
    - Completely eliminates Chromium iframe/data-URI blank screen blocking.
    """
    pdf_path_str = str(pdf_path)
    total_pages = 0
    try:
        import fitz
        doc = fitz.open(pdf_path_str)
        total_pages = len(doc)
    except Exception as e:
        logger.warning(f"Could not open PDF with fitz: {e}")

    if total_pages == 0:
        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button("📥 Download PDF", pdf_bytes, file_name=Path(pdf_path).name, mime="application/pdf")
        except Exception:
            st.warning("Unable to read PDF file.")
        return

    unique_key = f"pdf_prev_{Path(pdf_path).stem}"

    # PDF Control Bar
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.6, 1.0, 1.4], vertical_alignment="center")
    with ctrl_col1:
        view_mode = st.radio(
            "View Mode",
            options=["📜 Continuous", "📄 Single Page"],
            horizontal=True,
            label_visibility="collapsed",
            key=f"{unique_key}_mode",
        )
    with ctrl_col2:
        st.caption(f"**{total_pages}** page{'s' if total_pages > 1 else ''}")
    with ctrl_col3:
        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                "📥 Save PDF",
                data=pdf_bytes,
                file_name=Path(pdf_path).name,
                mime="application/pdf",
                key=f"{unique_key}_dl",
                use_container_width=True,
            )
        except Exception:
            pass

    # Render pages
    if view_mode == "📜 Continuous":
        with st.container(height=height):
            for i in range(total_pages):
                st.caption(f"📄 Page {i + 1} of {total_pages}")
                img_bytes = _render_pdf_page_image(pdf_path_str, i, dpi=150)
                if img_bytes:
                    st.image(img_bytes, use_container_width=True)
                else:
                    st.warning(f"Could not render page {i + 1}")
                if i < total_pages - 1:
                    st.divider()
    else:
        page_num = st.number_input(
            "Page",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1,
            key=f"{unique_key}_page_num",
            label_visibility="collapsed",
        )
        with st.container(height=height):
            img_bytes = _render_pdf_page_image(pdf_path_str, page_num - 1, dpi=160)
            if img_bytes:
                st.caption(f"📄 Page {page_num} of {total_pages}")
                st.image(img_bytes, use_container_width=True)
            else:
                st.warning(f"Could not render page {page_num}")


def render_markdown_with_math(content: str, height: int = 700) -> None:
    """
    Render Markdown with high-fidelity LaTeX math support using marked.js + KaTeX.
    Features:
    - Mathpix-like LaTeX copying: selecting text with equations and copying (Ctrl+C)
      copies pure LaTeX ($...$ and $$...$$) to clipboard via built-in copy-tex.
    - Click-to-copy: clicking on any equation copies its LaTeX formula immediately.
    - Math protection: prevents marked.js from corrupting underscores/asterisks in math.
    - Theme-adaptive: seamless dark and light mode rendering.
    - One-click 'Copy Full Markdown' action bar.
    """
    import streamlit.components.v1 as components
    import json as json_module

    content_json = json_module.dumps(content)

    widget_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/mhchem.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>

        <style>
            :root {{
                color-scheme: light dark;
                --bg: #0F172A;
                --text: #E2E8F0;
                --border: #334155;
                --card-bg: #1E293B;
                --accent: #6366F1;
                --accent-hover: #4F46E5;
                --accent-light: rgba(99, 102, 241, 0.15);
            }}

            @media (prefers-color-scheme: light) {{
                :root {{
                    --bg: #FFFFFF;
                    --text: #1E293B;
                    --border: #E2E8F0;
                    --card-bg: #F8FAFC;
                    --accent: #6366F1;
                    --accent-hover: #4F46E5;
                    --accent-light: rgba(99, 102, 241, 0.08);
                }}
            }}

            *, *:before, *:after {{
                box-sizing: border-box;
            }}

            html, body {{
                width: 100% !important;
                max-width: 100% !important;
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                color: var(--text);
                background: transparent;
                line-height: 1.65;
            }}

            #md-math-root {{
                width: 100% !important;
                max-width: 100% !important;
                padding: 0.5rem 0.75rem 2rem 0.75rem;
                box-sizing: border-box;
            }}

            #md-math-content {{
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box;
            }}

            /* Top toolbar */
            .viewer-toolbar {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 0.75rem;
                padding: 0.5rem 0.85rem;
                background: var(--card-bg);
                border: 1px solid var(--border);
                border-radius: 8px;
                margin-bottom: 1.25rem;
                position: sticky;
                top: 0;
                z-index: 100;
                backdrop-filter: blur(8px);
                width: 100%;
                box-sizing: border-box;
            }}
            .viewer-tip {{
                font-size: 0.82rem;
                color: var(--text);
                opacity: 0.9;
                display: flex;
                align-items: center;
                gap: 0.4rem;
                flex: 1 1 auto;
            }}
            .viewer-tip strong {{
                color: var(--accent);
            }}
            .toolbar-btn {{
                background: var(--accent);
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 0.4rem 0.85rem;
                font-size: 0.8rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                white-space: nowrap;
                flex-shrink: 0;
            }}
            .toolbar-btn:hover {{
                background: var(--accent-hover);
                transform: translateY(-1px);
            }}

            /* Content typography */
            #md-math-content h1, #md-math-content h2, #md-math-content h3, #md-math-content h4 {{
                color: var(--text);
                font-weight: 700;
                margin-top: 1.4em;
                margin-bottom: 0.5em;
                letter-spacing: -0.01em;
            }}
            #md-math-content h1 {{ font-size: 1.8rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }}
            #md-math-content h2 {{ font-size: 1.4rem; }}
            #md-math-content h3 {{ font-size: 1.15rem; }}
            #md-math-content p, #md-math-content li {{
                font-size: 0.95rem;
                color: var(--text);
            }}
            #md-math-content table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1.25rem 0;
            }}
            #md-math-content th, #md-math-content td {{
                border: 1px solid var(--border);
                padding: 0.55rem 0.85rem;
                text-align: left;
            }}
            #md-math-content th {{
                background: var(--card-bg);
                font-weight: 600;
            }}
            #md-math-content code {{
                background: var(--card-bg);
                padding: 0.15rem 0.45rem;
                border-radius: 4px;
                font-family: 'JetBrains Mono', 'Courier New', monospace;
                font-size: 0.88em;
                border: 1px solid var(--border);
            }}
            #md-math-content pre {{
                background: var(--card-bg);
                padding: 1rem;
                border-radius: 8px;
                overflow-x: auto;
                border: 1px solid var(--border);
            }}
            #md-math-content img {{
                max-width: 100%;
                border-radius: 6px;
            }}
            #md-math-content hr {{
                border: 0;
                height: 1px;
                background: var(--border);
                margin: 2rem 0;
            }}

            /* KaTeX equations & Mathpix copy styling */
            .katex-display {{
                overflow-x: auto;
                overflow-y: hidden;
                padding: 0.4rem 0;
                margin: 0.8rem 0;
            }}
            .katex {{
                cursor: pointer;
                border-radius: 4px;
                padding: 1px 3px;
                transition: background 0.15s ease, box-shadow 0.15s ease;
            }}
            .katex:hover {{
                background: var(--accent-light) !important;
                box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.35);
            }}

            /* Toast notification */
            #copy-toast {{
                visibility: hidden;
                min-width: 240px;
                background-color: #1E1B4B;
                color: #E0E7FF;
                border: 1px solid #6366F1;
                text-align: center;
                border-radius: 8px;
                padding: 10px 16px;
                position: fixed;
                z-index: 99999;
                bottom: 20px;
                right: 20px;
                font-size: 13px;
                font-weight: 600;
                box-shadow: 0 10px 25px rgba(0,0,0,0.4);
                opacity: 0;
                transition: opacity 0.25s, visibility 0.25s, transform 0.25s;
                transform: translateY(12px);
                pointer-events: none;
            }}
            #copy-toast.show {{
                visibility: visible;
                opacity: 1;
                transform: translateY(0);
            }}
        </style>
    </head>
    <body>
        <div class="viewer-toolbar">
            <div class="viewer-tip">
                <span>💡</span> <span>Select text or click any formula to copy <strong>LaTeX ($...$)</strong> like Mathpix</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                <div style="display: inline-flex; align-items: center; gap: 0.35rem; background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 0.25rem 0.6rem;">
                    <span style="font-size: 0.8rem; opacity: 0.6;">🔍</span>
                    <input id="doc-search-box" type="text" placeholder="Search in doc..." oninput="handleDocSearch(this.value)" style="background: transparent; border: none; color: var(--text); font-size: 0.8rem; outline: none; width: 130px;" />
                    <span id="search-counter" style="font-size: 0.72rem; color: var(--text); opacity: 0.6; min-width: 35px; text-align: right;"></span>
                </div>
                <button id="btn-copy-all" class="toolbar-btn" onclick="copyFullDocument()">📋 Copy Markdown</button>
            </div>
        </div>

        <div id="md-math-root">
            <div id="md-math-content"></div>
        </div>

        <div id="copy-toast">Copied to clipboard!</div>

        <script>
            const rawContent = {content_json};

            // 1. Math protection: isolate $$...$$ and $...$ before marked.js parses
            const mathPlaceholders = [];
            let protectedText = rawContent.replace(/\\$\\$([\\s\\S]*?)\\$\\$/g, function(match) {{
                mathPlaceholders.push(match);
                return '@@MATH_BLOCK_' + (mathPlaceholders.length - 1) + '@@';
            }});
            protectedText = protectedText.replace(/\\$([^$\\n]+?)\\$/g, function(match) {{
                mathPlaceholders.push(match);
                return '@@MATH_INLINE_' + (mathPlaceholders.length - 1) + '@@';
            }});

            // 2. Parse Markdown
            let parsedHtml = marked.parse(protectedText);

            // 3. Restore math expressions intact
            parsedHtml = parsedHtml.replace(/@@MATH_BLOCK_(\\d+)@@/g, function(_, idx) {{
                return mathPlaceholders[parseInt(idx, 10)];
            }});
            parsedHtml = parsedHtml.replace(/@@MATH_INLINE_(\\d+)@@/g, function(_, idx) {{
                return mathPlaceholders[parseInt(idx, 10)];
            }});

            const contentEl = document.getElementById('md-math-content');
            contentEl.innerHTML = parsedHtml;

            // 4. Render math with KaTeX
            renderMathInElement(contentEl, {{
                delimiters: [
                    {{left: '$$', right: '$$', display: true}},
                    {{left: '$', right: '$', display: false}},
                    {{left: '\\\\(', right: '\\\\)', display: false}},
                    {{left: '\\\\[', right: '\\\\]', display: true}}
                ],
                throwOnError: false
            }});

            // 5. In-document Search Handler
            function handleDocSearch(term) {{
                const container = document.getElementById('md-math-content');
                const counter = document.getElementById('search-counter');
                
                // Clear previous highlights
                const existingMarks = container.querySelectorAll('.doc-search-highlight');
                existingMarks.forEach(function(m) {{
                    const parent = m.parentNode;
                    parent.replaceChild(document.createTextNode(m.textContent), m);
                    parent.normalize();
                }});
                
                if (!term || term.trim().length === 0) {{
                    counter.textContent = '';
                    return;
                }}
                
                const query = term.trim().toLowerCase();
                let count = 0;
                
                function highlightInNode(node) {{
                    if (node.nodeType === Node.TEXT_NODE) {{
                        const val = node.nodeValue;
                        const lower = val.toLowerCase();
                        let idx = lower.indexOf(query);
                        if (idx !== -1) {{
                            const frag = document.createDocumentFragment();
                            let lastIdx = 0;
                            while (idx !== -1) {{
                                count++;
                                frag.appendChild(document.createTextNode(val.substring(lastIdx, idx)));
                                const mark = document.createElement('mark');
                                mark.className = 'doc-search-highlight';
                                mark.style.backgroundColor = 'rgba(234, 179, 8, 0.45)';
                                mark.style.color = 'inherit';
                                mark.style.borderRadius = '3px';
                                mark.style.padding = '0 2px';
                                mark.appendChild(document.createTextNode(val.substring(idx, idx + query.length)));
                                frag.appendChild(mark);
                                lastIdx = idx + query.length;
                                idx = lower.indexOf(query, lastIdx);
                            }}
                            frag.appendChild(document.createTextNode(val.substring(lastIdx)));
                            node.parentNode.replaceChild(frag, node);
                        }}
                    }} else if (node.nodeType === Node.ELEMENT_NODE && node.tagName !== 'SCRIPT' && node.tagName !== 'STYLE' && node.className !== 'doc-search-highlight') {{
                        Array.from(node.childNodes).forEach(highlightInNode);
                    }}
                }}
                
                highlightInNode(container);
                counter.textContent = count > 0 ? (count + (count === 1 ? ' match' : ' matches')) : '0 found';
                
                const firstMark = container.querySelector('.doc-search-highlight');
                if (firstMark) {{
                    firstMark.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                }}
            }}

            // 6. Mathpix-like Copy Handler: Intercept selection copy (Ctrl+C / Right click -> Copy)
            // Replaces rendered KaTeX elements with pure LaTeX code ($...$ / $$...$$)
            (function setupCopyTex() {{
                const copyDelimiters = {{
                    inline: ['$', '$'],
                    display: ['$$', '$$']
                }};

                function replaceKatexWithTex(fragment) {{
                    const htmlOnly = fragment.querySelectorAll('.katex-mathml + .katex-html');
                    for (let i = 0; i < htmlOnly.length; i++) {{
                        const el = htmlOnly[i];
                        if (el.parentNode) el.parentNode.removeChild(el);
                    }}

                    const mathmlElements = fragment.querySelectorAll('.katex-mathml');
                    for (let j = 0; j < mathmlElements.length; j++) {{
                        const mathml = mathmlElements[j];
                        const annotation = mathml.querySelector('annotation');
                        if (annotation) {{
                            const tex = annotation.innerHTML;
                            const isDisplay = mathml.closest('.katex-display') !== null;
                            const delims = isDisplay ? copyDelimiters.display : copyDelimiters.inline;
                            const replacement = document.createTextNode(delims[0] + tex + delims[1]);
                            if (mathml.parentNode) {{
                                mathml.parentNode.replaceChild(replacement, mathml);
                            }}
                        }}
                    }}
                    return fragment;
                }}

                function getClosestKatex(el) {{
                    const curr = el instanceof Element ? el : el.parentElement;
                    return curr ? curr.closest('.katex') : null;
                }}

                document.addEventListener('copy', function(e) {{
                    const sel = window.getSelection();
                    if (!sel.isCollapsed && e.clipboardData) {{
                        const range = sel.getRangeAt(0);
                        const startKatex = getClosestKatex(range.startContainer);
                        if (startKatex) range.setStartBefore(startKatex);
                        const endKatex = getClosestKatex(range.endContainer);
                        if (endKatex) range.setEndAfter(endKatex);

                        const cloned = range.cloneContents();
                        if (cloned.querySelector('.katex-mathml')) {{
                            const textWithTex = replaceKatexWithTex(cloned).textContent;
                            e.clipboardData.setData('text/plain', textWithTex);
                            e.preventDefault();
                            showToast('📋 Copied with LaTeX math preserved!');
                        }}
                    }}
                }});
            }})();

            // 6. Click-to-copy individual formulas
            document.addEventListener('click', function(e) {{
                const katexEl = e.target.closest('.katex');
                if (katexEl) {{
                    const annotation = katexEl.querySelector('annotation');
                    if (annotation) {{
                        const tex = annotation.innerHTML;
                        const isDisplay = katexEl.closest('.katex-display') !== null;
                        const formatted = isDisplay ? '$$' + tex + '$$' : '$' + tex + '$';
                        copyStringToClipboard(formatted, '📋 Copied LaTeX: ' + formatted);
                    }}
                }}
            }});

            // 7. Utility: Copy full document
            function copyFullDocument() {{
                copyStringToClipboard(rawContent, '📋 Copied full Markdown with LaTeX!');
            }}

            function copyStringToClipboard(text, successMsg) {{
                if (navigator.clipboard && navigator.clipboard.writeText) {{
                    navigator.clipboard.writeText(text).then(function() {{
                        showToast(successMsg);
                    }}).catch(function() {{
                        fallbackCopy(text, successMsg);
                    }});
                }} else {{
                    fallbackCopy(text, successMsg);
                }}
            }}

            function fallbackCopy(text, successMsg) {{
                const ta = document.createElement('textarea');
                ta.value = text;
                ta.style.position = 'fixed';
                ta.style.opacity = '0';
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                showToast(successMsg);
            }}

            function showToast(msg) {{
                const toast = document.getElementById('copy-toast');
                toast.textContent = msg;
                toast.className = 'show';
                clearTimeout(window._toastTimer);
                window._toastTimer = setTimeout(function() {{
                    toast.className = '';
                }}, 2500);
            }}
        </script>
    </body>
    </html>
    """

    import base64
    import streamlit as st

    b64_html = base64.b64encode(widget_html.encode("utf-8")).decode("utf-8")
    st.markdown(
        f'<iframe src="data:text/html;base64,{b64_html}" '
        f'width="100%" height="{height}" '
        f'style="border: 1px solid var(--border, rgba(255,255,255,0.1)); border-radius: 8px; width: 100%; min-width: 100%; display: block;" '
        f'frameborder="0"></iframe>',
        unsafe_allow_html=True,
    )


def trigger_auto_download(content: str, filename: str) -> None:
    """
    Trigger automatic client-side browser download of the converted Markdown file
    using a base64 data-URL / blob download iframe.
    """
    import base64
    import json
    import streamlit.components.v1 as components

    b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    safe_filename = json.dumps(filename)

    dl_html = f"""
    <!DOCTYPE html>
    <html>
    <body>
    <script>
        (function() {{
            try {{
                const b64 = "{b64_content}";
                const filename = {safe_filename};
                const byteCharacters = atob(b64);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {{
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }}
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], {{ type: 'text/markdown;charset=utf-8' }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                setTimeout(function() {{
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }}, 1500);
            }} catch (e) {{
                console.error("Auto-download trigger failed:", e);
            }}
        }})();
    </script>
    </body>
    </html>
    """
    components.html(dl_html, height=0, width=0)


def show_success(message: str, details: Optional[str] = None) -> None:
    """
    Display a success message.
    
    Args:
        message: Main success message
        details: Optional additional details
    """
    if details:
        st.success(f"✅ {message}\n\n*{details}*")
    else:
        st.success(f"✅ {message}")


def show_error(message: str, details: Optional[str] = None) -> None:
    """
    Display an error message.
    
    Args:
        message: Main error message
        details: Optional additional details or traceback
    """
    if details:
        st.error(f"❌ {message}\n\n```\n{details}\n```")
    else:
        st.error(f"❌ {message}")


def show_warning(message: str) -> None:
    """Display a warning message."""
    st.warning(f"⚠️ {message}")


def show_info(message: str) -> None:
    """Display an info message."""
    st.info(f"ℹ️ {message}")


# =============================================================================
# FILE DISPLAY
# =============================================================================

def display_markdown_preview(file_path: str, max_lines: Optional[int] = None) -> None:
    """
    Display a Markdown file with syntax highlighting.
    
    Args:
        file_path: Path to the Markdown file
        max_lines: Optional limit on lines to display
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if max_lines:
            lines = content.split("\n")
            content = "\n".join(lines[:max_lines])
            if len(lines) > max_lines:
                content += f"\n\n... *(showing {max_lines} of {len(lines)} lines)*"
        
        st.markdown("### 📄 Preview")
        
        # Show in a code block for raw view
        with st.expander("Raw Markdown", expanded=False):
            st.code(content, language="markdown")
        
        # Rendered view
        st.markdown("---")
        st.markdown(content)
        
    except Exception as e:
        show_error("Failed to load preview", str(e))


def display_file_info(file_info: dict) -> None:
    """
    Display file metadata in a nice format.
    
    Args:
        file_info: Dictionary from FileManager.get_file_info()
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("File Name", file_info["name"])
    with col2:
        st.metric("Size", f"{file_info['size_mb']} MB")
    with col3:
        st.metric("Type", file_info["suffix"].upper())


# =============================================================================
# BUTTON HELPERS
# =============================================================================

def download_button(
    file_path: str,
    label: str = "Download",
    mime_type: str = "text/markdown",
) -> None:
    """
    Create a download button for a file.
    
    Args:
        file_path: Path to the file to download
        label: Button label
        mime_type: MIME type for the file
    """
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        
        file_name = Path(file_path).name
        
        st.download_button(
            label=f"⬇️ {label}",
            data=data,
            file_name=file_name,
            mime=mime_type,
            use_container_width=True,
        )
    except Exception as e:
        show_error("Download failed", str(e))


def action_button(
    label: str,
    on_click: Callable,
    key: str,
    disabled: bool = False,
    type_: str = "secondary",
) -> None:
    """
    Create a styled action button.
    
    Args:
        label: Button text
        on_click: Callback function
        key: Streamlit widget key
        disabled: Whether button is disabled
        type_: Button type ('primary' or 'secondary')
    """
    st.button(
        label=label,
        on_click=on_click,
        key=key,
        disabled=disabled,
        type=type_,
        use_container_width=True,
    )


# =============================================================================
# LAYOUT HELPERS
# =============================================================================

def card(title: str, content: str, icon: str = "") -> None:
    """
    Display content in a card-like container.
    
    Args:
        title: Card title
        content: Card content (markdown supported)
        icon: Optional emoji icon
    """
    st.markdown(
        f"""
        <div style="background-color: #1e1e2e; border-radius: 12px; 
                    padding: 1.5rem; margin: 1rem 0; border: 1px solid #2a2a3e;">
            <h4>{icon} {title}</h4>
            <p>{content}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def divider() -> None:
    """Display a styled divider."""
    st.markdown(
        """
        <div style="border-top: 1px solid #2a2a3e; margin: 1.5rem 0;"></div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: Optional[str] = None) -> None:
    """
    Display a consistent page header.
    
    Args:
        title: Page title
        subtitle: Optional subtitle
    """
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(f"*{subtitle}*")
    st.markdown("---")


# =============================================================================
# FORM HELPERS
# =============================================================================

def settings_toggle(
    label: str,
    key: str,
    default: bool = False,
    help_text: Optional[str] = None,
) -> bool:
    """
    Create a settings toggle with consistent styling.
    
    Args:
        label: Toggle label
        key: Session state key
        default: Default value
        help_text: Optional help tooltip
        
    Returns:
        Current toggle value
    """
    return st.toggle(
        label=label,
        key=key,
        value=st.session_state.get(key, default),
        help=help_text,
    )


def settings_select(
    label: str,
    options: List[str],
    key: str,
    default: Optional[str] = None,
    help_text: Optional[str] = None,
) -> str:
    """
    Create a settings dropdown with consistent styling.
    
    Args:
        label: Dropdown label
        options: List of options
        key: Session state key
        default: Default selected option
        help_text: Optional help tooltip
        
    Returns:
        Selected option
    """
    current = st.session_state.get(key, default or options[0])
    if current not in options:
        current = options[0]
    
    return st.selectbox(
        label=label,
        options=options,
        index=options.index(current),
        key=key,
        help=help_text,
    )


def settings_number(
    label: str,
    key: str,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    default: int = 0,
    help_text: Optional[str] = None,
) -> int:
    """
    Create a number input for settings.
    
    Args:
        label: Input label
        key: Session state key
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        default: Default value
        help_text: Optional help tooltip
        
    Returns:
        Current value
    """
    return st.number_input(
        label=label,
        min_value=min_value,
        max_value=max_value,
        value=st.session_state.get(key, default),
        key=key,
        help=help_text,
    )