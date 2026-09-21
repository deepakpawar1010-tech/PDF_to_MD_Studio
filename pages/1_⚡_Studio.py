"""
PDF_to_MD_Studio v1.0 - PDF to Markdown Converter Page
=====================================================
Main conversion interface for single and batch PDF processing.
"""

import os
import queue
import sys
import threading
import time
from pathlib import Path
from typing import List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from core.config import get_config
from core.constants import MAX_BATCH_SIZE
from core.conversion_manager import get_conversion_manager
from core.file_manager import FileManager
from core.logger import get_logger
from core.session_manager import SessionManager, init_session
from core.ui_helpers import (
    apply_custom_css,
    display_file_info,
    download_button,
    file_uploader_area,
    page_header,
    render_markdown_with_math,
    render_pdf_preview,
    render_sidebar,
    setup_page,
    show_error,
    show_success,
    show_warning,
)
from core.marker_engine import CONVERSION_STAGES

logger = get_logger(__name__)


def _format_elapsed(elapsed: float) -> str:
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)
    return f"{mins}m {secs}s" if mins > 0 else f"{secs}s"


def run_conversion_with_progress(
    manager,
    input_path: Path,
    output_dir: Path,
    panel_placeholder,
    progress_bar,
    page_range: Optional[str] = None,
    engine_type: Optional[str] = None,
) -> Tuple[bool, str, Optional[Path]]:
    """
    Run conversion with queue-based, STAGE-AWARE progress updates.
    All Streamlit widget updates happen in main thread only.
    """
    progress_queue = queue.Queue()
    result_container = {
        "done": False,
        "success": False,
        "message": "",
        "output_path": None,
    }

    # Local UI state, updated as "stage" messages arrive
    ui_state = {
        "stage_state": {s["key"]: 0.0 for s in CONVERSION_STAGES},
        "current_stage": None,
        "overall": 0.0,
        "heartbeat_msg": "Starting up...",
    }

    def conversion_thread():
        try:
            success, message, output_path = manager.convert_single(
                input_path=input_path,
                output_dir=output_dir,
                progress_queue=progress_queue,
                page_range=page_range,
                engine_type=engine_type,
            )
            result_container["success"] = success
            result_container["message"] = message
            result_container["output_path"] = output_path
        except Exception as e:
            result_container["success"] = False
            result_container["message"] = f"Error: {str(e)}"
        finally:
            result_container["done"] = True
            try:
                progress_queue.put(("done", None), block=False)
            except Exception:
                pass

    thread = threading.Thread(target=conversion_thread, daemon=True)
    thread.start()

    start_time = time.time()

    def drain_queue():
        try:
            while True:
                msg_type, payload = progress_queue.get_nowait()
                if msg_type == "stage" and isinstance(payload, dict):
                    if "stages" in payload:
                        ui_state["stage_state"] = payload["stages"]
                    if "current_stage" in payload:
                        ui_state["current_stage"] = payload["current_stage"]
                    if "overall" in payload:
                        ui_state["overall"] = payload["overall"]
                    if "raw_line" in payload:
                        ui_state["heartbeat_msg"] = payload["raw_line"]
                elif msg_type == "heartbeat":
                    ui_state["heartbeat_msg"] = str(payload)
        except queue.Empty:
            pass

    def render():
        elapsed = time.time() - start_time
        overall = min(max(ui_state["overall"], 0.0), 1.0)
        pct = int(overall * 100)

        current_key = ui_state["current_stage"]
        if current_key:
            stage_meta = next((s for s in CONVERSION_STAGES if s["key"] == current_key), None)
            stage_label = stage_meta["label"] if stage_meta else "Processing..."
        else:
            stage_label = ui_state["heartbeat_msg"]

        progress_bar.progress(overall)
        panel_placeholder.markdown(
            f"**{pct}%** &nbsp;•&nbsp; {stage_label} &nbsp;•&nbsp; ⏱️ {_format_elapsed(elapsed)}"
        )

    while not result_container["done"]:
        drain_queue()
        render()
        time.sleep(0.2)

    drain_queue()
    render()

    thread.join(timeout=5)

    return (
        result_container["success"],
        result_container["message"],
        result_container["output_path"],
    )


def handle_single_conversion(
    uploaded_file,
    pre_saved_path: Path,
    page_range: Optional[str] = None,
    engine_type: Optional[str] = None,
) -> None:
    """Handle single file conversion using pre-saved temp file."""
    manager = get_conversion_manager()

    panel_placeholder = st.empty()
    progress_bar = st.progress(0.0)

    try:
        success, message, output_path = run_conversion_with_progress(
            manager=manager,
            input_path=pre_saved_path,
            output_dir=None,
            panel_placeholder=panel_placeholder,
            progress_bar=progress_bar,
            page_range=page_range,
            engine_type=engine_type,
        )

        panel_placeholder.empty()
        progress_bar.empty()
        
        if success and output_path:
            show_success("Conversion Complete!", message)
            
            st.markdown("### 📄 Result")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                file_info = FileManager.get_file_info(Path(output_path))
                display_file_info(file_info)
            
            with col2:
                download_button(output_path, "Download Markdown")
            
            st.markdown("---")
            st.markdown("### 🔍 Compare: Original PDF vs Converted Output")
            st.caption("Side-by-side 50:50 view: Original PDF on the left, Rendered Markdown with LaTeX math on the right.")

            compare_col_pdf, compare_col_output = st.columns(2, gap="medium")

            with compare_col_pdf:
                st.markdown("**📄 Original PDF**")
                render_pdf_preview(pre_saved_path, height=750)

            with compare_col_output:
                st.markdown(f"**📝 Converted Output** (`{Path(output_path).suffix}`)")
                try:
                    with open(output_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    out_ext = Path(output_path).suffix.lower()
                    tab_rendered, tab_raw = st.tabs(["🎨 Rendered", "📄 Raw"])

                    with tab_rendered:
                        if out_ext == ".json":
                            with st.container(height=750):
                                import json
                                try:
                                    st.json(json.loads(content))
                                except Exception:
                                    st.code(content, language="json")
                        elif out_ext == ".html":
                            import streamlit.components.v1 as components
                            components.html(content, height=750, scrolling=True)
                        else:
                            render_markdown_with_math(content, height=750)

                    with tab_raw:
                        with st.container(height=750):
                            raw_lang = {".json": "json", ".html": "html"}.get(out_ext, "markdown")
                            st.code(content, language=raw_lang)

                except Exception as e:
                    show_warning(f"Preview unavailable: {e}")
            
            SessionManager.set_current_file(uploaded_file.name)
            
        else:
            show_error("Conversion Failed", message)
            
    except Exception as e:
        panel_placeholder.empty()
        progress_bar.empty()
        logger.error(f"Single conversion error: {e}")
        show_error("Conversion Failed", str(e))


def run_batch_conversion_with_progress(
    manager,
    input_paths: List[Path],
    output_dir: Path,
    create_zip: bool,
    panel_placeholder,
    progress_bar,
) -> Tuple[bool, str, List[Path], Optional[Path]]:
    """Run batch conversion with queue-based, STAGE-AWARE progress updates."""
    progress_queue = queue.Queue()
    result_container = {
        "done": False,
        "success": False,
        "message": "",
        "output_files": [],
        "zip_path": None,
    }

    ui_state = {
        "stage_state": {s["key"]: 0.0 for s in CONVERSION_STAGES},
        "current_stage": None,
        "overall": 0.0,
        "heartbeat_msg": "Starting up...",
    }

    def conversion_thread():
        try:
            success, message, output_files, zip_path = manager.convert_batch(
                input_paths=input_paths,
                output_dir=output_dir,
                progress_queue=progress_queue,
                create_zip=create_zip,
            )
            result_container["success"] = success
            result_container["message"] = message
            result_container["output_files"] = output_files
            result_container["zip_path"] = zip_path
        except Exception as e:
            result_container["success"] = False
            result_container["message"] = f"Error: {str(e)}"
        finally:
            result_container["done"] = True
            try:
                progress_queue.put(("done", None), block=False)
            except Exception:
                pass

    thread = threading.Thread(target=conversion_thread, daemon=True)
    thread.start()

    start_time = time.time()

    def drain_queue():
        try:
            while True:
                msg_type, payload = progress_queue.get_nowait()
                if msg_type == "stage":
                    ui_state["stage_state"] = payload["stages"]
                    ui_state["current_stage"] = payload["current_stage"]
                    ui_state["overall"] = payload["overall"]
                elif msg_type == "heartbeat":
                    ui_state["heartbeat_msg"] = payload
        except queue.Empty:
            pass

    def render():
        elapsed = time.time() - start_time
        overall = min(max(ui_state["overall"], 0.0), 1.0)
        pct = int(overall * 100)

        current_key = ui_state["current_stage"]
        if current_key:
            stage_meta = next((s for s in CONVERSION_STAGES if s["key"] == current_key), None)
            stage_label = stage_meta["label"] if stage_meta else "Processing..."
        else:
            stage_label = ui_state["heartbeat_msg"]

        progress_bar.progress(overall)
        panel_placeholder.markdown(
            f"**{pct}%** &nbsp;•&nbsp; {stage_label} &nbsp;•&nbsp; ⏱️ {_format_elapsed(elapsed)}"
        )

    while not result_container["done"]:
        drain_queue()
        render()
        time.sleep(0.2)

    drain_queue()
    render()

    thread.join(timeout=5)

    return (
        result_container["success"],
        result_container["message"],
        result_container["output_files"],
        result_container["zip_path"],
    )


def handle_batch_conversion(uploaded_files, pre_saved_paths: List[Path]) -> None:
    """Handle batch conversion using pre-saved temp files."""
    if not pre_saved_paths:
        show_warning("No valid files for batch conversion.")
        return
    
    manager = get_conversion_manager()

    panel_placeholder = st.empty()
    progress_bar = st.progress(0.0)

    create_zip = SessionManager.get("create_zip", True)

    try:
        success, message, output_files, zip_path = run_batch_conversion_with_progress(
            manager=manager,
            input_paths=pre_saved_paths,
            output_dir=None,
            create_zip=create_zip,
            panel_placeholder=panel_placeholder,
            progress_bar=progress_bar,
        )

        panel_placeholder.empty()
        progress_bar.empty()
        
        if success and output_files:
            show_success(
                f"Batch Conversion Complete!",
                f"Converted {len(output_files)} files successfully."
            )
            
            st.markdown("### 📋 Results")
            
            results_data = []
            for output_file in output_files:
                info = FileManager.get_file_info(output_file)
                results_data.append({
                    "File": info["name"],
                    "Size": f"{info['size_mb']} MB",
                    "Path": str(output_file),
                })
            
            st.dataframe(
                results_data,
                use_container_width=True,
                hide_index=True,
            )
            
            if zip_path and Path(zip_path).exists():
                st.markdown("---")
                st.markdown("### 📦 Batch Archive")
                download_button(zip_path, "Download ZIP Archive", "application/zip")
            
            st.markdown("---")
            st.markdown("### ⬇️ Individual Files")
            
            cols = st.columns(min(len(output_files), 4))
            for i, output_file in enumerate(output_files):
                with cols[i % len(cols)]:
                    download_button(str(output_file), f"Download")
            
        else:
            show_error("Batch Conversion Failed", message)
            
    except Exception as e:
        panel_placeholder.empty()
        progress_bar.empty()
        logger.error(f"Batch conversion error: {e}")
        show_error("Batch Conversion Failed", str(e))


def render_conversion_page() -> None:
    """Render the main PDF to Markdown conversion studio."""
    setup_page("Studio", "⚡")
    init_session()
    render_sidebar()
    
    page_header("⚡ Conversion Studio", "Convert PDFs to clean Markdown with 100% LaTeX math accuracy")
    
    st.markdown("### Select Conversion Mode & Engine")
    
    mode_col, engine_col, format_col, images_col = st.columns([1.5, 1.8, 1, 1])

    with mode_col:
        mode = st.radio(
            "Conversion Mode",
            options=["Single File", "Batch Processing"],
            horizontal=True,
            label_visibility="collapsed",
            key="conversion_mode",
        )

    with engine_col:
        config = get_config()
        current_engine = config.get("engine", "gemini")
        engine_options = ["⚡ Gemini Flash (Fast & Exact)", "🖥️ Marker (Local Offline)"]
        engine_index = 0 if current_engine == "gemini" else 1
        selected_engine_label = st.selectbox(
            "Engine",
            options=engine_options,
            index=engine_index,
            key="quick_engine_select",
            label_visibility="collapsed",
            help="Gemini Flash converts in seconds with 100% LaTeX math accuracy. Marker runs locally on your GPU/CPU.",
        )
        selected_engine = "gemini" if "Gemini" in selected_engine_label else "marker"
        if selected_engine != current_engine:
            config.set("engine", selected_engine)

    with format_col:
        format_options = ["markdown", "json", "html"]
        current_format = config.get("output_format", "markdown")
        selected_format = st.selectbox(
            "Output Format",
            options=format_options,
            index=format_options.index(current_format) if current_format in format_options else 0,
            key="quick_output_format",
            label_visibility="collapsed",
            help="Choose the output format for this conversion (also changes the default in Settings).",
        )
        if selected_format != current_format:
            config.set("output_format", selected_format)

    with images_col:
        current_extract = config.get("preserve_images", True)
        extract_images = st.checkbox(
            "🖼️ Images",
            value=current_extract,
            key="quick_extract_images",
            help="Turn off to skip image extraction entirely - faster, and skips writing image files to disk.",
        )
        if extract_images != current_extract:
            config.set("preserve_images", extract_images)

    # API key prompt banner if Gemini is selected without key
    import os
    if selected_engine == "gemini" and not config.get("gemini_api_key") and not os.environ.get("GEMINI_API_KEY"):
        st.info("💡 **Gemini API Key Required:** Please enter your free Gemini API key below to use high-speed conversion (get one free at [aistudio.google.com](https://aistudio.google.com)).")
        api_key_col1, api_key_col2 = st.columns([3, 1])
        with api_key_col1:
            api_key_val = st.text_input("Gemini API Key", type="password", key="quick_api_key_input", label_visibility="collapsed", placeholder="Paste your Gemini API key here...")
        with api_key_col2:
            if st.button("Save Key", key="btn_save_quick_api_key", use_container_width=True):
                if api_key_val and api_key_val.strip():
                    config.set("gemini_api_key", api_key_val.strip())
                    st.success("API key saved!")
                    st.rerun()
    
    st.markdown("---")
    
    if mode == "Single File":
        st.markdown("### Upload PDF File")
        
        uploaded_file = file_uploader_area(
            label="Upload PDF",
            key="single_uploader",
            accept_multiple=False,
        )
        
        if uploaded_file is not None:
            file_manager = FileManager()
            temp_path = file_manager.save_uploaded_file(uploaded_file)
            
            try:
                is_valid, error = file_manager.validate_file(temp_path)
                
                if is_valid:
                    info = file_manager.get_file_info(temp_path)
                    display_file_info(info)
                    
                    st.markdown("---")

                    page_range_input = st.text_input(
                        "Page Range (optional)",
                        value="",
                        placeholder="e.g. 0-5,10,15-20 - leave empty to convert all pages",
                        key="single_page_range",
                        help="Skip pages you don't need - each skipped page skips its entire OCR/layout/text cost, speeding up conversion.",
                    )

                    if st.button("🚀 Convert to Markdown", type="primary", use_container_width=True):
                        with st.spinner("Processing..."):
                            handle_single_conversion(
                                uploaded_file,
                                temp_path,
                                page_range=page_range_input.strip() or None,
                                engine_type=selected_engine,
                            )
                else:
                    show_error("Invalid File", error)
            
            finally:
                if get_config().get("auto_cleanup", True):
                    file_manager.delete_file(temp_path)
    
    else:
        st.markdown("### Upload Multiple PDF Files")
        
        uploaded_files = file_uploader_area(
            label="Upload PDFs",
            key="batch_uploader",
            accept_multiple=True,
        )
        
        if uploaded_files:
            st.markdown(f"**{len(uploaded_files)} file(s) selected**")
            
            file_manager = FileManager()
            saved_paths = []
            valid_files = []
            invalid_messages = []
            
            for uploaded_file in uploaded_files:
                temp_path = file_manager.save_uploaded_file(uploaded_file)
                is_valid, error = file_manager.validate_file(temp_path)
                
                if is_valid:
                    saved_paths.append(temp_path)
                    valid_files.append(uploaded_file)
                    st.markdown(f"✅ {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
                else:
                    invalid_messages.append(f"❌ {uploaded_file.name}: {error}")
                    file_manager.delete_file(temp_path)
            
            if invalid_messages:
                for msg in invalid_messages:
                    st.markdown(msg)
            
            if saved_paths:
                st.markdown("---")
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    create_zip = st.toggle(
                        "Create ZIP Archive",
                        value=True,
                        help="Package all converted files into a single ZIP download",
                    )
                    SessionManager.set("create_zip", create_zip)
                
                with col2:
                    if st.button("🚀 Convert All", type="primary", use_container_width=True):
                        with st.spinner("Processing batch..."):
                            handle_batch_conversion(valid_files, saved_paths)
                
                SessionManager.set("pending_cleanup", [str(p) for p in saved_paths])
            else:
                show_error("No Valid Files", "None of the uploaded files passed validation.")
    
    pending = SessionManager.get("pending_cleanup", [])
    if pending:
        file_manager = FileManager()
        for path_str in pending:
            file_manager.delete_file(Path(path_str))
        SessionManager.set("pending_cleanup", [])
    
    st.markdown("---")
    st.markdown("### 🕐 Recent Conversions")
    
    history = SessionManager.get_conversion_history()
    
    if history:
        for record in history[:10]:
            status_icon = "✅" if record.get("success") else "❌"
            with st.container():
                cols = st.columns([4, 1])
                with cols[0]:
                    st.markdown(
                        f"{status_icon} **{record.get('input_name', 'Unknown')}** → "
                        f"`{record.get('output_name', 'N/A')}`"
                    )
                with cols[1]:
                    st.markdown(
                        f"<span style='color: #666; font-size: 0.8rem;'>"
                        f"{record.get('timestamp', '')[:19]}</span>",
                        unsafe_allow_html=True,
                    )
    else:
        st.info("No conversions yet. Upload a PDF to get started!")


def main() -> None:
    """Page entry point."""
    apply_custom_css()
    render_conversion_page()


if __name__ == "__main__":
    main()
