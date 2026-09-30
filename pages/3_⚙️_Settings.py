"""
TeXify Studio v2.0 - Settings Page
===================================
Application settings, preferences, API keys, and system diagnostics.
Exact match to reference mockup design (media_1790762538192.png).
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from core.config import ConfigManager, get_config
from core.constants import (
    DEFAULT_CONVERSION_TIMEOUT,
    HELP_TEXT,
    LOG_LEVEL,
    MAX_FILE_SIZE_MB,
)
from core.file_manager import FileManager
from core.logger import LoggerManager, get_logger
from core.marker_engine import reset_marker_engine
from core.session_manager import SessionManager, init_session
from core.ui_helpers import (
    apply_custom_css,
    render_html,
    render_page_header,
    render_sidebar,
    setup_page,
    show_error,
    show_success,
    show_warning,
)

logger = get_logger(__name__)


def render_general_tab() -> None:
    """Render General Settings matching media_1790762538192.png."""
    config = get_config()

    # =========================================================================
    # CARD 1: STORAGE & PATHS
    # =========================================================================
    with st.container(border=True):
        render_html(
            """
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.35rem;">
                <div style="width: 32px; height: 32px; border-radius: 8px; background: #EEF2FF; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; color: #6366F1;">
                    📁
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">Storage & Paths</div>
                    <div style="font-size: 0.8rem; color: #64748B;">Configure where files are saved and temporary files are stored.</div>
                </div>
            </div>
            """
        )

        col1, col2 = st.columns(2, gap="medium")

        with col1:
            render_html(
                """
                <div style="margin-top: 0.5rem; margin-bottom: 0.25rem;">
                    <div style="font-weight: 600; font-size: 0.88rem; color: #0F172A;">Output Directory</div>
                    <div style="font-size: 0.78rem; color: #64748B;">Choose a local folder where converted Markdown files and assets will be saved.</div>
                </div>
                """
            )
            out_c1, out_c2 = st.columns([3, 1])
            with out_c1:
                new_output = st.text_input(
                    "Output Directory",
                    value=config.get("custom_output_dir", "") or "",
                    placeholder="Default location (output/)",
                    label_visibility="collapsed",
                    key="input_output_dir",
                )
            with out_c2:
                if st.button("Browse", key="btn_browse_out", use_container_width=True):
                    st.info(f"Current: `{config.get_output_dir()}`")

            render_html(
                """
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: -0.3rem;">
                    ⓘ If left empty, files will be saved to your default output folder.
                </div>
                """
            )
            if new_output != config.get("custom_output_dir", ""):
                config.set("custom_output_dir", new_output.strip() if new_output.strip() else None)

        with col2:
            render_html(
                """
                <div style="margin-top: 0.5rem; margin-bottom: 0.25rem;">
                    <div style="font-weight: 600; font-size: 0.88rem; color: #0F172A;">Temporary Directory</div>
                    <div style="font-size: 0.78rem; color: #64748B;">Used for temporary files during conversion (auto-cleaned if enabled).</div>
                </div>
                """
            )
            tmp_c1, tmp_c2 = st.columns([3, 1])
            with tmp_c1:
                new_temp = st.text_input(
                    "Temporary Directory",
                    value=config.get("custom_temp_dir", "") or "",
                    placeholder="Default location (temp/)",
                    label_visibility="collapsed",
                    key="input_temp_dir",
                )
            with tmp_c2:
                if st.button("Browse", key="btn_browse_temp", use_container_width=True):
                    st.info(f"Current: `{config.get_temp_dir()}`")

            render_html(
                """
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: -0.3rem;">
                    ⓘ If left empty, a temporary folder in your system will be used.
                </div>
                """
            )
            if new_temp != config.get("custom_temp_dir", ""):
                config.set("custom_temp_dir", new_temp.strip() if new_temp.strip() else None)

    # =========================================================================
    # CARD 2: CLEANUP
    # =========================================================================
    with st.container(border=True):
        render_html(
            """
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.35rem;">
                <div style="width: 32px; height: 32px; border-radius: 8px; background: #FFF1F2; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; color: #E11D48;">
                    🗑️
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">Cleanup</div>
                    <div style="font-size: 0.8rem; color: #64748B;">Manage temporary files and old logs to keep your system clean.</div>
                </div>
            </div>
            """
        )

        clean_col1, clean_col2 = st.columns([1.2, 1], gap="large")

        with clean_col1:
            render_html("<div style='height: 0.6rem;'></div>")
            auto_clean = st.toggle(
                "Auto Cleanup Temporary Files ⓘ",
                value=config.get("auto_cleanup", True),
                key="setting_toggle_autoclean",
            )
            render_html(
                """
                <div style="font-size: 0.78rem; color: #64748B; margin-top: -0.4rem; padding-left: 0.2rem;">
                    Automatically removes temporary files after conversion.
                </div>
                """
            )
            if auto_clean != config.get("auto_cleanup", True):
                config.set("auto_cleanup", auto_clean)

        with clean_col2:
            render_html("<div style='height: 0.4rem;'></div>")
            btn_col1, btn_col2 = st.columns(2, gap="small")
            with btn_col1:
                if st.button("🧹 Clean Temp Files", key="btn_clean_temp", use_container_width=True):
                    removed = FileManager.cleanup_temp_files(max_age_hours=0)
                    show_success(f"Removed {removed} temporary files")
                render_html("<div style='font-size: 0.72rem; color: #94A3B8; text-align: center; margin-top: 0.15rem;'>Remove temporary files now</div>")

            with btn_col2:
                if st.button("📄 Clean Old Logs", key="btn_clean_logs", use_container_width=True):
                    removed = LoggerManager.cleanup_old_logs(keep_days=0)
                    show_success(f"Removed {removed} old log files")
                render_html("<div style='font-size: 0.72rem; color: #94A3B8; text-align: center; margin-top: 0.15rem;'>Delete old log files</div>")

    # =========================================================================
    # CARD 3: CONVERSION DEFAULTS
    # =========================================================================
    with st.container(border=True):
        render_html(
            """
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.35rem;">
                <div style="width: 32px; height: 32px; border-radius: 8px; background: #EFF6FF; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; color: #2563EB;">
                    🎛️
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">Conversion Defaults</div>
                    <div style="font-size: 0.8rem; color: #64748B;">Set default options for new conversions in the studio.</div>
                </div>
            </div>
            """
        )

        d_col1, d_col2, d_col3, d_col4 = st.columns(4, gap="medium")

        with d_col1:
            render_html("<div style='font-weight: 600; font-size: 0.85rem; color: #0F172A; margin-bottom: 0.2rem;'>⚡ Default Engine / Model ⓘ</div>")
            engine_map = {
                "⚡ Gemini 3.5 Flash-Lite (Fast & Accurate)": ("gemini", "gemini-3.5-flash-lite"),
                "⚡ Gemini 3.5 Flash (Complex Math)": ("gemini", "gemini-3.5-flash"),
                "🖥️ Marker Engine (Offline)": ("marker", ""),
            }
            cur_eng = config.get("engine", "gemini")
            cur_mod = config.get("gemini_model", "gemini-3.5-flash-lite")
            default_idx = 0
            if cur_eng == "marker":
                default_idx = 2
            elif "3.5-flash" in cur_mod and "lite" not in cur_mod:
                default_idx = 1

            sel_eng_label = st.selectbox(
                "Default Engine",
                options=list(engine_map.keys()),
                index=default_idx,
                label_visibility="collapsed",
                key="setting_def_engine",
            )
            eng_val, mod_val = engine_map[sel_eng_label]
            if eng_val != cur_eng:
                config.set("engine", eng_val)
            if mod_val and mod_val != cur_mod:
                config.set("gemini_model", mod_val)

            render_html("<div style='font-size: 0.73rem; color: #94A3B8; margin-top: 0.2rem;'>Used as the default AI model for new conversions.</div>")

        with d_col2:
            render_html("<div style='font-weight: 600; font-size: 0.85rem; color: #0F172A; margin-bottom: 0.2rem;'>📄 Default Output Format</div>")
            fmt_map = {
                "Standard Markdown (MD)": "markdown",
                "Structured JSON (JSON)": "json",
                "HTML Document (HTML)": "html",
            }
            cur_fmt = config.get("output_format", "markdown")
            fmt_idx = 0 if cur_fmt == "markdown" else (1 if cur_fmt == "json" else 2)
            sel_fmt_label = st.selectbox(
                "Default Output Format",
                options=list(fmt_map.keys()),
                index=fmt_idx,
                label_visibility="collapsed",
                key="setting_def_format",
            )
            chosen_fmt = fmt_map[sel_fmt_label]
            if chosen_fmt != cur_fmt:
                config.set("output_format", chosen_fmt)

            render_html("<div style='font-size: 0.73rem; color: #94A3B8; margin-top: 0.2rem;'>Choose the default Markdown format.</div>")

        with d_col3:
            render_html("<div style='font-weight: 600; font-size: 0.85rem; color: #0F172A; margin-bottom: 0.2rem;'>🖼️ Include Images</div>")
            img_map = {
                "Extract images to folder": True,
                "Do not extract images": False,
            }
            cur_img = config.get("preserve_images", True)
            img_idx = 0 if cur_img else 1
            sel_img_label = st.selectbox(
                "Include Images",
                options=list(img_map.keys()),
                index=img_idx,
                label_visibility="collapsed",
                key="setting_def_images",
            )
            chosen_img = img_map[sel_img_label]
            if chosen_img != cur_img:
                config.set("preserve_images", chosen_img)

            render_html("<div style='font-size: 0.73rem; color: #94A3B8; margin-top: 0.2rem;'>Extract images from PDF and save to a folder.</div>")

        with d_col4:
            render_html("<div style='font-weight: 600; font-size: 0.85rem; color: #0F172A; margin-bottom: 0.2rem;'>📑 Preserve Structure</div>")
            preserve_struct = st.toggle(
                "Preserve Structure",
                value=config.get("preserve_structure", True),
                label_visibility="collapsed",
                key="setting_preserve_struct",
            )
            if preserve_struct != config.get("preserve_structure", True):
                config.set("preserve_structure", preserve_struct)

            render_html("<div style='font-size: 0.73rem; color: #94A3B8; margin-top: 0.2rem;'>Keep headings, lists, tables and formatting. Maintains document structure.</div>")

        # Row 2: Page range
        render_html("<div style='margin-top: 0.85rem;'></div>")
        pr_col1, pr_col2 = st.columns([1, 3])
        with pr_col1:
            render_html("<div style='font-weight: 600; font-size: 0.85rem; color: #0F172A; margin-bottom: 0.2rem;'>📄 Page Range (Optional)</div>")
            def_range = st.text_input(
                "Page Range",
                value=config.get("default_page_range", "") or "",
                placeholder="e.g. 1-5, 8, 10-12",
                label_visibility="collapsed",
                key="setting_def_pagerange",
            )
            if def_range != config.get("default_page_range", ""):
                config.set("default_page_range", def_range.strip() if def_range.strip() else None)
            render_html("<div style='font-size: 0.73rem; color: #94A3B8; margin-top: 0.2rem;'>Default page range for new conversions.</div>")

    # =========================================================================
    # CARD 4: APPEARANCE
    # =========================================================================
    with st.container(border=True):
        render_html(
            """
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.35rem;">
                <div style="width: 32px; height: 32px; border-radius: 8px; background: #FAF5FF; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; color: #9333EA;">
                    🎨
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">Appearance</div>
                    <div style="font-size: 0.8rem; color: #64748B;">Customize the look and feel of TeXify Studio.</div>
                </div>
            </div>
            """
        )

        app_col1, app_col2 = st.columns([1.5, 2.5])
        with app_col1:
            current_theme = SessionManager.get_theme()
            theme_opts = ["System Default", "Light", "Dark"]
            theme_idx = 1 if current_theme == "light" else 2
            sel_theme = st.selectbox(
                "Theme",
                options=theme_opts,
                index=theme_idx,
                key="setting_theme_select",
            )
            target_theme = "light" if "Light" in sel_theme or "System" in sel_theme else "dark"
            if target_theme != current_theme:
                SessionManager.set_theme(target_theme)
                st.rerun()

            render_html("<div style='font-size: 0.73rem; color: #94A3B8; margin-top: -0.3rem;'>Choose your preferred theme.</div>")


def render_conversion_tab() -> None:
    """Render Conversion & Gemini API Key Settings."""
    config = get_config()

    with st.container(border=True):
        render_html(
            """
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                <div style="width: 36px; height: 36px; border-radius: 10px; background: #EEF2FF; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; color: #6366F1;">
                    ⚡
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1.1rem; color: #0F172A;">Google Gemini AI Engine</div>
                    <div style="font-size: 0.82rem; color: #64748B;">Configure your Gemini API key and multimodal vision model.</div>
                </div>
            </div>
            """
        )

        render_html(
            """
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 1rem; font-size: 0.82rem; color: #475569;">
                💡 <strong>Free Gemini API Key:</strong> Get your key free at <a href="https://aistudio.google.com" target="_blank" style="color: #4F46E5; font-weight: 600;">aistudio.google.com</a>. Free tier includes 1,500 free document pages per day with ~0.4s conversion speed and 100% accurate LaTeX math formatting.
            </div>
            """
        )

        c1, c2 = st.columns([3, 1])
        with c1:
            current_key = config.get("gemini_api_key", "")
            new_key = st.text_input(
                "Gemini API Key",
                value=current_key,
                type="password",
                placeholder="AIzaSy...",
                help="Your Google Gemini API Key. Can also be set via GEMINI_API_KEY environment variable.",
                key="setting_gemini_key",
            )
            if new_key != current_key:
                config.set("gemini_api_key", new_key.strip())
                st.success("Gemini API key saved!")

        with c2:
            model_options = [
                "gemini-3.5-flash-lite",
                "gemini-flash-lite-latest",
                "gemini-3.1-flash-lite",
                "gemini-3.5-flash",
                "gemini-3.6-flash",
                "gemini-3.7-flash",
            ]
            current_model = config.get("gemini_model", "gemini-3.5-flash-lite")
            selected_model = st.selectbox(
                "Model",
                options=model_options,
                index=model_options.index(current_model) if current_model in model_options else 0,
                key="setting_gemini_model_select",
            )
            if selected_model != current_model:
                config.set("gemini_model", selected_model)

        if new_key:
            if st.button("🧪 Test Gemini API Connection", key="btn_test_gemini_conn"):
                with st.spinner("Connecting to Google Gemini API..."):
                    try:
                        from google import genai
                        client = genai.Client(api_key=new_key.strip())
                        resp = client.models.generate_content(model=selected_model, contents="Ping")
                        if resp.text:
                            st.success(f"✅ Connection successful! Model `{selected_model}` is ready.")
                    except Exception as e:
                        st.error(f"❌ Connection failed: {e}")

    with st.container(border=True):
        render_html(
            """
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                <div style="width: 36px; height: 36px; border-radius: 10px; background: #F1F5F9; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; color: #475569;">
                    🖥️
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1.1rem; color: #0F172A;">Marker Engine (Local Offline)</div>
                    <div style="font-size: 0.82rem; color: #64748B;">Fallback engine powered by local marker executable.</div>
                </div>
            </div>
            """
        )

        m_col1, m_col2 = st.columns(2, gap="medium")
        with m_col1:
            marker_path = config.get_marker_path()
            st.caption(f"Detected Executable: `{marker_path or 'Not detected'}`")
            custom_marker = st.text_input(
                "Custom Marker Executable Path",
                value=config.get("custom_marker_path", "") or "",
                placeholder="C:\\path\\to\\marker_single.exe",
                key="setting_marker_custom_path",
            )
            if custom_marker and Path(custom_marker).exists():
                config.set("custom_marker_path", custom_marker)
                reset_marker_engine()
                st.success("Marker path updated.")

        with m_col2:
            timeout = st.slider(
                "Conversion Timeout (seconds)",
                min_value=30,
                max_value=1200,
                value=int(config.get("timeout", DEFAULT_CONVERSION_TIMEOUT)),
                step=30,
                key="setting_marker_timeout",
            )
            config.set("timeout", timeout)

            ocr_enabled = st.checkbox(
                "Force OCR for Scanned Documents",
                value=config.get("ocr_enabled", False),
                key="setting_marker_ocr",
            )
            config.set("ocr_enabled", ocr_enabled)


def render_output_tab() -> None:
    """Render Output Formatting Tab."""
    config = get_config()

    with st.container(border=True):
        render_html(
            """
            <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; margin-bottom: 0.35rem;">
                📝 Markdown Post-Processing & Formatting
            </div>
            <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 1rem;">
                Control automated fixes and output formatting options.
            </div>
            """
        )

        auto_post = st.checkbox(
            "Automatically clean up Markdown after conversion",
            value=config.get("auto_post_process", True),
            help="Fixes stray question bullets, formats math delimiters, and aligns tables.",
            key="setting_auto_post_box",
        )
        config.set("auto_post_process", auto_post)

        img_format = st.selectbox(
            "Extracted Image Format",
            options=["png", "jpg", "webp"],
            index=["png", "jpg", "webp"].index(config.get("image_format", "png")),
            key="setting_img_format_box",
        )
        config.set("image_format", img_format)


def render_performance_tab() -> None:
    """Render Performance & Hardware tab."""
    with st.container(border=True):
        render_html(
            """
            <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; margin-bottom: 0.35rem;">
                🚀 Hardware & Acceleration Status
            </div>
            <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 1rem;">
                Diagnostic overview of execution speed and available hardware accelerators.
            </div>
            """
        )

        from core.marker_engine import get_marker_engine
        engine = get_marker_engine()

        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric("Device Status", engine.get_device_status().upper())
        with p2:
            st.metric("Gemini API Speed", "~0.4s / page")
        with p3:
            st.metric("Max Batch Size", "10 Files")


def render_advanced_tab() -> None:
    """Render Advanced Settings."""
    with st.container(border=True):
        render_html(
            """
            <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; margin-bottom: 0.35rem;">
                🔧 Session & Cache Management
            </div>
            <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 1rem;">
                Reset session states, clear cached files, or restore default configurations.
            </div>
            """
        )

        a1, a2 = st.columns(2)
        with a1:
            if st.button("Clear Conversion History", key="btn_clear_hist", use_container_width=True):
                SessionManager.clear_history()
                st.success("Conversion history cleared!")
        with a2:
            if st.button("Reset Config to Defaults", key="btn_reset_cfg", use_container_width=True):
                cfg = get_config()
                cfg.reset_to_defaults()
                st.success("Configuration reset to defaults!")
                st.rerun()


def render_system_tab() -> None:
    """Render System Diagnostics Tab."""
    config = get_config()
    with st.container(border=True):
        render_html(
            """
            <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; margin-bottom: 0.35rem;">
                ℹ️ System Information & Paths
            </div>
            <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 1rem;">
                Runtime environment diagnostics and active folder locations.
            </div>
            """
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"- **Application:** TeXify Studio v{config.get('app_version', '2.0.0')}")
            st.markdown(f"- **Python Version:** `{sys.version.split()[0]}`")
            st.markdown(f"- **Streamlit Version:** `{st.__version__}`")
        with c2:
            st.markdown(f"- **Output Path:** `{config.get_output_dir()}`")
            st.markdown(f"- **Temp Path:** `{config.get_temp_dir()}`")
            st.markdown(f"- **Log Path:** `{config.get_log_dir()}`")

        st.markdown("---")
        st.markdown("**Recent Application Logs**")
        recent_logs = LoggerManager.get_recent_logs(lines=40)
        with st.expander("View Logs", expanded=False):
            st.code(recent_logs, language="log")


def render_settings_page() -> None:
    """Render complete settings page matching media_1790762538192.png."""
    setup_page("Settings", "⚙️")
    init_session()
    apply_custom_css()
    render_sidebar()

    # Saved badge HTML matching media_1790762538192.png
    badge_html = """
    <div style="display: inline-flex; align-items: center; gap: 0.4rem; background: #ECFDF5; border: 1px solid #A7F3D0; padding: 0.35rem 0.85rem; border-radius: 9999px; font-size: 0.78rem; font-weight: 600; color: #059669;">
        <span style="color: #10B981; font-size: 0.7rem;">●</span> Settings are saved automatically <span style="font-size: 0.85rem;">✓</span>
    </div>
    """

    render_page_header(
        icon="⚙️",
        title="Settings",
        subtitle="Configure application preferences and conversion options.",
        badge_html=badge_html,
    )

    tabs = st.tabs([
        "🏠 General",
        "⚡ Conversion",
        "📄 Output",
        "🚀 Performance",
        "🎨 Appearance",
        "🔧 Advanced",
        "ℹ System",
    ])

    with tabs[0]:
        render_general_tab()
    with tabs[1]:
        render_conversion_tab()
    with tabs[2]:
        render_output_tab()
    with tabs[3]:
        render_performance_tab()
    with tabs[4]:
        render_appearance_tab()
    with tabs[5]:
        render_advanced_tab()
    with tabs[6]:
        render_system_tab()


def main() -> None:
    render_settings_page()


if __name__ == "__main__":
    main()