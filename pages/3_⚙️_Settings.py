"""
PDF_to_MD_Studio v1.0 - Settings Page
======================================
Application settings, configuration, and preferences management.
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
    DEFAULT_SETTINGS,
    HELP_TEXT,
    LOG_LEVEL,
    MAX_BATCH_SIZE,
    MAX_FILE_SIZE_MB,
)
from core.file_manager import FileManager
from core.logger import LoggerManager, get_logger
from core.marker_engine import reset_marker_engine
from core.session_manager import SessionManager, init_session
from core.ui_helpers import (
    apply_custom_css,
    card,
    page_header,
    render_sidebar,
    setup_page,
    show_error,
    show_info,
    show_success,
    show_warning,
    settings_number,
    settings_select,
    settings_toggle,
)

logger = get_logger(__name__)


def render_general_settings() -> None:
    """Render general application settings section."""
    st.markdown("### 🏠 General")
    
    config = get_config()
    
    # Output directory
    st.markdown("#### Output Directory")
    current_output = config.get_output_dir()
    st.markdown(f"Current: `{current_output}`")
    
    new_output = st.text_input(
        "Custom Output Directory (leave empty for default)",
        value=config.get("custom_output_dir", ""),
        key="setting_output_dir",
        help="Full path to a custom output directory",
    )
    
    if new_output and Path(new_output).exists():
        config.set("custom_output_dir", new_output)
        st.success(f"Output directory updated: {new_output}")
    elif new_output:
        st.warning("Directory does not exist. Using default.")
        config.set("custom_output_dir", None)
    
    # Temp directory
    st.markdown("#### Temporary Directory")
    current_temp = config.get_temp_dir()
    st.markdown(f"Current: `{current_temp}`")
    
    new_temp = st.text_input(
        "Custom Temp Directory (leave empty for default)",
        value=config.get("custom_temp_dir", ""),
        key="setting_temp_dir",
        help="Full path to a custom temp directory",
    )
    
    if new_temp and Path(new_temp).exists():
        config.set("custom_temp_dir", new_temp)
    elif new_temp:
        st.warning("Directory does not exist. Using default.")
        config.set("custom_temp_dir", None)
    
    # Auto cleanup
    st.markdown("#### Cleanup")
    auto_cleanup = settings_toggle(
        "Auto Cleanup Temporary Files",
        key="setting_auto_cleanup",
        default=config.get("auto_cleanup", True),
        help_text="Automatically remove temporary files after conversion",
    )
    config.set("auto_cleanup", auto_cleanup)
    
    # Manual cleanup buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Clean Temp Files", key="clean_temp", use_container_width=True):
            removed = FileManager.cleanup_temp_files(max_age_hours=0)
            show_success(f"Removed {removed} temp items")
    
    with col2:
        if st.button("🧹 Clean Old Logs", key="clean_logs", use_container_width=True):
            removed = LoggerManager.cleanup_old_logs(keep_days=0)
            show_success(f"Removed {removed} old log files")


def render_conversion_settings() -> None:
    """Render conversion-specific settings section."""
    st.markdown("### ⚙️ Conversion")
    
    config = get_config()

    # Engine Selection
    st.markdown("#### Primary Engine")
    current_engine = config.get("engine", "gemini")
    engine_options = ["⚡ Gemini Flash (Fast & Exact Math)", "🖥️ Marker (Local Offline)"]
    selected_label = st.radio(
        "Default Conversion Engine",
        options=engine_options,
        index=0 if current_engine == "gemini" else 1,
        key="setting_default_engine",
        help="Gemini Flash converts documents in seconds with 100% LaTeX math accuracy. Marker runs locally on your GPU/CPU.",
    )
    new_engine = "gemini" if "Gemini" in selected_label else "marker"
    config.set("engine", new_engine)

    # Gemini Settings Card
    st.markdown("#### ⚡ Gemini Engine Settings")
    st.caption("Free tier available at [aistudio.google.com](https://aistudio.google.com) (1,500 free conversions/day).")
    
    current_key = config.get("gemini_api_key", "")
    new_key = st.text_input(
        "Gemini API Key",
        value=current_key,
        type="password",
        key="setting_gemini_api_key",
        help="Your Google Gemini API Key. Can also be set via GEMINI_API_KEY environment variable.",
    )
    if new_key != current_key:
        config.set("gemini_api_key", new_key.strip())
        st.success("Gemini API key saved!")

    model_options = [
        "gemini-3.5-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-3.8-flash",
    ]
    current_model = config.get("gemini_model", "gemini-3.5-flash-lite")
    selected_model = st.selectbox(
        "Gemini Model",
        options=model_options,
        index=model_options.index(current_model) if current_model in model_options else 0,
        key="setting_gemini_model",
        help="Gemini 3.5 Flash-Lite is recommended for ultra-fast conversion, 1,500 free pages/day, and 100% accurate LaTeX math.",
    )
    if selected_model != current_model:
        config.set("gemini_model", selected_model)

    if new_key:
        if st.button("🧪 Test Gemini API Connection", key="btn_test_gemini"):
            try:
                from google import genai
                client = genai.Client(api_key=new_key.strip())
                resp = client.models.generate_content(model=selected_model, contents="Ping")
                if resp.text:
                    st.success(f"✅ Connection successful! Model `{selected_model}` is ready.")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")

    st.markdown("---")
    
    # Marker path
    st.markdown("#### 🖥️ Marker Executable Settings")
    marker_path = config.get_marker_path()
    st.markdown(f"Detected: `{marker_path}`")
    
    custom_marker = st.text_input(
        "Custom Marker Path (leave empty for auto-detect)",
        value=config.get("custom_marker_path", ""),
        key="setting_marker_path",
        help=HELP_TEXT["marker_path"],
    )
    
    if custom_marker and Path(custom_marker).exists():
        config.set("custom_marker_path", custom_marker)
        reset_marker_engine()
        show_success("Marker path updated and engine reset")
    elif custom_marker:
        show_warning("Marker executable not found at specified path")
    
    # Timeout
    st.markdown("#### Timeout")
    timeout = settings_number(
        "Conversion Timeout (seconds)",
        key="setting_timeout",
        min_value=30,
        max_value=3600,
        default=config.get("timeout", DEFAULT_CONVERSION_TIMEOUT),
        help_text="Maximum time to wait for a single conversion",
    )
    config.set("timeout", timeout)
    
    # Quality
    st.markdown("#### Quality")
    quality = settings_select(
        "Conversion Quality",
        options=["high", "fast"],
        key="setting_quality",
        default=config.get("quality", "high"),
        help_text="High = better accuracy, Fast = quicker conversion",
    )
    config.set("quality", quality)
    
    # Language
    st.markdown("#### Language")
    language = settings_select(
        "Document Language",
        options=["auto", "en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko", "ru", "ar"],
        key="setting_language",
        default=config.get("language", "auto"),
        help_text="Language for OCR and text processing",
    )
    config.set("language", language)
    
    # OCR
    ocr_enabled = settings_toggle(
        "Enable OCR",
        key="setting_ocr",
        default=config.get("ocr_enabled", False),
        help_text="Force OCR for all documents (slower but more accurate for scanned PDFs)",
    )
    config.set("ocr_enabled", ocr_enabled)


def render_output_settings() -> None:
    """Render output format settings section."""
    st.markdown("### 📝 Output Format")
    
    config = get_config()

    # Output format - this is the actual --output_format flag Marker's CLI accepts
    output_format = settings_select(
        "Output Format",
        options=["markdown", "json", "html"],
        key="setting_output_format",
        default=config.get("output_format", "markdown"),
        help_text=(
            "markdown = .md files (readable, editable). "
            "json = structured block-level document tree (good for programmatic use). "
            "html = rendered HTML output."
        ),
    )
    config.set("output_format", output_format)

    if output_format != "markdown":
        st.info(
            f"Output files will be saved as `.{('json' if output_format == 'json' else 'html')}` "
            f"instead of `.md`. The Markdown Viewer page currently only lists `.md` files, "
            f"so {output_format.upper()} outputs will appear directly in your output folder "
            f"but not in that viewer yet."
        )

    # Auto-cleanup toggle
    st.markdown("#### Auto Cleanup")
    auto_post_process = settings_toggle(
        "Automatically clean up Markdown after conversion",
        key="setting_auto_post_process",
        default=config.get("auto_post_process", True),
        help_text=(
            "Runs the same fixes as the Clean Up tab (misplaced question numbers, "
            "stray bullets, math delimiters) automatically right after each conversion, "
            "so you don't need to run it manually in the Markdown Viewer. "
            "Only applies to Markdown output, not JSON/HTML."
        ),
    )
    config.set("auto_post_process", auto_post_process)
    
    # Preserve images
    preserve_images = settings_toggle(
        "Preserve Images",
        key="setting_preserve_images",
        default=config.get("preserve_images", True),
        help_text="Extract and save images alongside Markdown files",
    )
    config.set("preserve_images", preserve_images)
    
    # Image format
    if preserve_images:
        image_format = settings_select(
            "Image Output Format",
            options=["png", "jpg", "webp"],
            key="setting_image_format",
            default=config.get("image_format", "png"),
            help_text="Format for extracted images",
        )
        config.set("image_format", image_format)


def render_appearance_settings() -> None:
    """Render UI appearance settings section."""
    st.markdown("### 🎨 Appearance")
    
    config = get_config()
    
    # Theme
    current_theme = SessionManager.get_theme()
    theme = st.radio(
        "Theme",
        options=["Dark", "Light"],
        index=0 if current_theme == "dark" else 1,
        horizontal=True,
        key="setting_theme",
    )
    
    new_theme = "dark" if theme == "Dark" else "light"
    if new_theme != current_theme:
        SessionManager.set_theme(new_theme)
        st.rerun()
    
    # Log level
    st.markdown("#### Logging")
    log_level = settings_select(
        "Log Level",
        options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        key="setting_log_level",
        default=config.get("log_level", LOG_LEVEL),
        help_text="Detail level for application logs",
    )
    config.set("log_level", log_level)
    LoggerManager.set_level(log_level)


def render_performance_settings() -> None:
    """Render GPU/performance settings section."""
    st.markdown("### 🚀 Performance (GPU)")

    from core.marker_engine import get_marker_engine

    config = get_config()
    engine = get_marker_engine()

    st.markdown("#### Persistent Server Mode")
    st.caption(
        "Uses marker_server (a persistent background process) instead of launching a fresh "
        "subprocess for every conversion. Models stay loaded in memory, avoiding reload overhead "
        "(can be minutes per conversion). Start it first with: `marker_server --port 8001`"
    )

    use_server_mode = settings_toggle(
        "Use Persistent Server Mode",
        key="setting_use_server_mode",
        default=config.get("use_server_mode", False),
        help_text="Requires marker_server running separately. Falls back to normal mode automatically if unreachable.",
    )
    config.set("use_server_mode", use_server_mode)

    if use_server_mode:
        server_url = st.text_input(
            "Server URL",
            value=config.get("server_url", "http://localhost:8001"),
            key="setting_server_url",
        )
        config.set("server_url", server_url)
        st.markdown(f"**Status:** {engine.get_server_status()}")
        st.info(
            "⚠️ Server mode shows a simple elapsed-time spinner instead of the stage-by-stage "
            "progress bar, since marker_server doesn't provide progress callbacks."
        )

    st.markdown(f"**Detected:** {engine.get_device_status()}")

    device_choice = settings_select(
        "Compute Device",
        options=["cuda", "cpu"],
        key="setting_device",
        default=config.get("device", "cuda"),
        help_text="cuda = use your GPU (faster, needs CUDA-enabled torch). cpu = force CPU (slower, always works).",
    )
    config.set("device", device_choice)

    st.markdown("#### Batch Sizes")
    st.caption(
        "Lower these if you hit CUDA out-of-memory errors, especially on GPUs with less VRAM. "
        "Raise them if you have VRAM to spare and want faster conversions."
    )

    recognition_batch = settings_number(
        "Recognition Batch Size",
        key="setting_recognition_batch",
        min_value=1,
        max_value=64,
        default=config.get("recognition_batch_size", 8),
        help_text="Batch size for text recognition (OCR). Lower = less VRAM, slower.",
    )
    config.set("recognition_batch_size", recognition_batch)

    detector_batch = settings_number(
        "Detector Batch Size",
        key="setting_detector_batch",
        min_value=1,
        max_value=32,
        default=config.get("detector_batch_size", 4),
        help_text="Batch size for layout/text detection. Lower = less VRAM, slower.",
    )
    config.set("detector_batch_size", detector_batch)

    st.markdown("#### CPU Parallelism")
    st.caption(
        "Controls parallel workers for the initial PDF text/structure extraction step - "
        "this runs on CPU, not GPU, so raising it doesn't affect VRAM usage. Safe to raise "
        "on multi-core CPUs even with a weak GPU."
    )
    pdftext_workers = settings_number(
        "PDF Text Extraction Workers",
        key="setting_pdftext_workers",
        min_value=1,
        max_value=32,
        default=config.get("pdftext_workers", 4),
        help_text="Parallel CPU workers for initial text/structure extraction (--pdftext_workers).",
    )
    config.set("pdftext_workers", pdftext_workers)

    st.markdown("#### Batch Conversion Workers")
    st.caption(
        "Number of PDFs processed in parallel during batch conversion. Each worker loads its "
        "own copy of the models into VRAM - keep this LOW on GPUs with less than 8GB VRAM."
    )
    batch_workers = settings_number(
        "Batch Workers",
        key="setting_batch_workers",
        min_value=1,
        max_value=16,
        default=config.get("batch_workers", 1),
        help_text="Parallel PDF conversions during batch mode.",
    )
    config.set("batch_workers", batch_workers)


def render_advanced_settings() -> None:
    """Render advanced settings section."""
    st.markdown("### 🔧 Advanced")
    
    config = get_config()
    
    # Max file size
    max_size = settings_number(
        "Max File Size (MB)",
        key="setting_max_size",
        min_value=1,
        max_value=500,
        default=config.get("max_file_size", MAX_FILE_SIZE_MB),
        help_text="Maximum individual file size for upload",
    )
    config.set("max_file_size", max_size)
    
    # Max batch size
    max_batch = settings_number(
        "Max Batch Size",
        key="setting_max_batch",
        min_value=1,
        max_value=100,
        default=config.get("max_batch_size", MAX_BATCH_SIZE),
        help_text="Maximum files in a single batch conversion",
    )
    config.set("max_batch_size", max_batch)
    
    # Config file location
    st.markdown("---")
    st.markdown("#### Configuration File")
    config_file = ConfigManager._config_file
    st.markdown(f"Location: `{config_file}`")
    
    if config_file.exists():
        with open(config_file, "r") as f:
            st.code(f.read(), language="json")
    
    # Reset settings
    st.markdown("---")
    st.markdown("#### Danger Zone")
    
    if st.button("🔄 Reset All Settings to Defaults", key="reset_settings", type="secondary"):
        config.reset_to_defaults()
        SessionManager.reset_settings()
        reset_marker_engine()
        show_success("All settings reset to defaults")
        st.rerun()
    
    if st.button("🗑️ Clear All History", key="clear_history", type="secondary"):
        SessionManager.clear_history()
        SessionManager.clear_batch_files()
        show_success("All history cleared")


def render_system_info() -> None:
    """Render system information section."""
    st.markdown("### ℹ️ System Information")
    
    from core.marker_engine import get_marker_engine
    
    config = get_config()
    engine = get_marker_engine()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Application")
        st.markdown(f"- **Version:** {config.get('app_version', '1.0.0')}")
        st.markdown(f"- **Marker Available:** {'✅ Yes' if engine.is_available() else '❌ No'}")
        st.markdown(f"- **Marker Path:** `{engine.marker_path or 'Not found'}`")
        st.markdown(f"- **Marker Version:** `{engine.get_version()}`")
        st.markdown(f"- **Batch Marker Available:** {'✅ Yes' if engine.is_batch_available() else '❌ No'}")
        st.markdown(f"- **Batch Marker Path:** `{engine.batch_marker_path or 'Not found'}`")
        st.markdown(f"- **Device:** {engine.get_device_status()}")
    
    with col2:
        st.markdown("#### Directories")
        st.markdown(f"- **Output:** `{get_config().get_output_dir()}`")
        st.markdown(f"- **Temp:** `{get_config().get_temp_dir()}`")
        st.markdown(f"- **Logs:** `{get_config().get_log_dir()}`")
    
    # Recent logs
    st.markdown("---")
    st.markdown("#### Recent Logs")
    
    recent_logs = LoggerManager.get_recent_logs(lines=50)
    with st.expander("View Logs", expanded=False):
        st.code(recent_logs, language="log")


def render_settings_page() -> None:
    """Render the complete settings page."""
    setup_page("Settings", "⚙️")
    init_session()
    render_sidebar()
    
    page_header("⚙️ Settings", "Configure application preferences and conversion options")
    
    # Settings tabs
    tab_general, tab_conversion, tab_output, tab_performance, tab_appearance, tab_advanced, tab_system = st.tabs([
        "🏠 General",
        "⚙️ Conversion",
        "📝 Output",
        "🚀 Performance",
        "🎨 Appearance",
        "🔧 Advanced",
        "ℹ️ System",
    ])
    
    with tab_general:
        render_general_settings()
    
    with tab_conversion:
        render_conversion_settings()
    
    with tab_output:
        render_output_settings()
    
    with tab_performance:
        render_performance_settings()
    
    with tab_appearance:
        render_appearance_settings()
    
    with tab_advanced:
        render_advanced_settings()
    
    with tab_system:
        render_system_info()
    
    # Save indicator
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 0.8rem;">
            <p>💾 Settings are saved automatically</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Page entry point."""
    apply_custom_css()
    render_settings_page()


if __name__ == "__main__":
    main()