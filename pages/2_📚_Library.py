"""
PDF_to_MD_Studio v1.0 - Markdown Viewer Page
=============================================
Browse, preview, and manage converted Markdown files.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from core.config import get_config
from core.constants import OUTPUT_DIR, OUTPUT_EXTENSION
from core.file_manager import FileManager
from core.logger import get_logger
from core.session_manager import SessionManager, init_session
from core.ui_helpers import (
    apply_custom_css,
    download_button,
    page_header,
    render_markdown_with_math,
    render_sidebar,
    setup_page,
    show_error,
    show_info,
    show_warning,
)

logger = get_logger(__name__)


def render_file_browser() -> Path:
    """
    Render the file browser sidebar and return selected file.
    
    Returns:
        Path to selected file or None
    """
    with st.container(border=True):
        header_col, refresh_col = st.columns([4, 1])
        with header_col:
            st.markdown("**📁 Output Directory**")
        with refresh_col:
            if st.button("🔄", key="refresh_files", use_container_width=True, help="Refresh file list"):
                st.rerun()

        output_dir = get_config().get_output_dir()
        st.code(str(output_dir), language=None)

        files = FileManager.list_files(output_dir, [OUTPUT_EXTENSION, '.json', '.html'])

        if not files:
            st.info("No Markdown files found yet.")
            return None

        file_names = [f.name for f in files]
        selected_name = st.selectbox(
            "Select a file",
            options=file_names,
            index=0,
            key="file_selector",
            label_visibility="collapsed",
        )

        selected_file = output_dir / selected_name

        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            mime_map = {".md": "text/markdown", ".json": "application/json", ".html": "text/html"}
            download_button(
                str(selected_file),
                "Download",
                mime_map.get(selected_file.suffix.lower(), "text/plain"),
            )
        with col2:
            if st.button("🗑️ Delete", key="delete_file", use_container_width=True):
                if FileManager.delete_file(selected_file):
                    st.success(f"Deleted: {selected_name}")
                    st.rerun()
                else:
                    st.error("Failed to delete file")

    return selected_file


def render_file_preview(file_path: Path) -> None:
    """
    Render the Markdown file preview.
    
    Args:
        file_path: Path to the Markdown file
    """
    if not file_path or not file_path.exists():
        st.info("Select a file from the browser to view its contents.")
        return
    
    # File info
    info = FileManager.get_file_info(file_path)
    
    with st.container(border=True):
        st.markdown(f"**👁️ {info['name']}**")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Size", f"{info['size_mb']} MB")
        with col2:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    line_count = sum(1 for _ in f)
                st.metric("Lines", line_count)
            except:
                st.metric("Lines", "N/A")
        with col3:
            st.metric("Modified", info["modified"][:10])
        with col4:
            st.metric("Created", info["created"][:10])
    
    # Read content
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        show_error("Failed to read file", str(e))
        return

    file_ext = file_path.suffix.lower()

    # View mode tabs
    tab_rendered, tab_raw, tab_edit, tab_stats, tab_cleanup = st.tabs(
        ["🎨 Rendered", "📄 Raw", "✏️ Edit", "📊 Stats", "🧹 Clean Up"]
    )
    
    with tab_rendered:
        if file_ext == ".json":
            import json
            try:
                st.json(json.loads(content))
            except Exception:
                st.warning("Couldn't parse as JSON - showing raw text instead.")
                st.code(content, language="json")
        elif file_ext == ".html":
            import streamlit.components.v1 as components
            components.html(content, height=600, scrolling=True)
        else:
            render_markdown_with_math(content, height=650)
    
    with tab_raw:
        raw_language = {"json": "json", "html": "html"}.get(file_ext.lstrip("."), "markdown")
        st.code(content, language=raw_language)
        
        # Copy button workaround
        st.text_area(
            "Copy raw text",
            value=content,
            height=200,
            key="raw_copy_area",
            label_visibility="collapsed",
        )

    with tab_edit:
        st.caption(
            "Edit the converted content directly and save your corrections. "
            "Changes only get written to disk when you click Save."
        )

        editor_key = f"editor_content_{file_path}"
        saved_marker_key = f"editor_saved_baseline_{file_path}"

        if editor_key not in st.session_state:
            st.session_state[editor_key] = content
        if saved_marker_key not in st.session_state:
            st.session_state[saved_marker_key] = content

        edit_col, preview_col = st.columns(2)

        with edit_col:
            st.markdown("**Editor**")
            edited_content = st.text_area(
                "Editor",
                height=500,
                key=editor_key,
                label_visibility="collapsed",
            )

        has_unsaved_changes = edited_content != st.session_state[saved_marker_key]

        with preview_col:
            preview_label = "**Live Preview**"
            if has_unsaved_changes:
                preview_label += " 🟡 *(unsaved changes)*"
            st.markdown(preview_label)
            with st.container(height=500):
                if file_ext == ".json":
                    import json
                    try:
                        st.json(json.loads(edited_content))
                    except Exception:
                        st.code(edited_content, language="json")
                elif file_ext == ".html":
                    import streamlit.components.v1 as components
                    components.html(edited_content, height=470, scrolling=True)
                else:
                    render_markdown_with_math(edited_content, height=470)

        save_col, discard_col = st.columns(2)
        with save_col:
            if st.button(
                "💾 Save Changes",
                key=f"save_edit_{file_path}",
                type="primary",
                use_container_width=True,
                disabled=not has_unsaved_changes,
            ):
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(edited_content)
                    st.session_state[saved_marker_key] = edited_content
                    st.success(f"Saved changes to {file_path.name}")
                    st.rerun()
                except Exception as e:
                    show_error("Failed to save", str(e))
        with discard_col:
            if st.button(
                "↩️ Discard Changes",
                key=f"discard_edit_{file_path}",
                use_container_width=True,
                disabled=not has_unsaved_changes,
            ):
                del st.session_state[editor_key]
                st.rerun()
    
    with tab_stats:
        # Content statistics
        word_count = len(content.split())
        char_count = len(content)
        heading_count = content.count("#")
        link_count = content.count("](")
        image_count = content.count("![")
        code_block_count = content.count("```")
        
        st.markdown("#### Content Statistics")
        
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        with stats_col1:
            st.metric("Words", word_count)
            st.metric("Characters", char_count)
        with stats_col2:
            st.metric("Headings", heading_count)
            st.metric("Links", link_count)
        with stats_col3:
            st.metric("Images", image_count)
            st.metric("Code Blocks", code_block_count)
        
        # Structure analysis
        st.markdown("---")
        st.markdown("#### Document Structure")
        
        lines = content.split("\n")
        structure = []
        current_level = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                level = len(stripped) - len(stripped.lstrip("#"))
                title = stripped.lstrip("#").strip()
                structure.append(("heading", level, title))
            elif stripped.startswith("- ") or stripped.startswith("* "):
                structure.append(("list", 0, stripped[2:]))
            elif stripped.startswith("```"):
                structure.append(("code", 0, "Code block"))
        
        # Display structure
        if structure:
            for item_type, level, text in structure[:50]:  # Limit display
                indent = "  " * level
                if item_type == "heading":
                    st.markdown(f"{indent}**H{level}:** {text}")
                elif item_type == "list":
                    st.markdown(f"{indent}• {text[:60]}")
                elif item_type == "code":
                    st.markdown(f"{indent}`{text}`")
            
            if len(structure) > 50:
                st.markdown(f"*... and {len(structure) - 50} more elements*")
        else:
            st.info("No structured elements detected.")

    with tab_cleanup:
        st.caption(
            "Auto-fix common Marker conversion mistakes. Nothing is saved until you "
            "review the preview and click Save - your original file is never touched otherwise."
        )

        from core.post_processor import AVAILABLE_FIXES, run_cleanup

        enabled_ids = []
        for fix_id, label, _fn in AVAILABLE_FIXES:
            if st.checkbox(label, value=True, key=f"cleanup_{fix_id}"):
                enabled_ids.append(fix_id)

        if st.button("🔍 Preview Cleanup", key="preview_cleanup", type="primary"):
            cleaned, results = run_cleanup(content, enabled_ids)
            st.session_state["_cleanup_preview"] = cleaned
            st.session_state["_cleanup_results"] = results
            st.session_state["_cleanup_source_file"] = str(file_path)

        preview = st.session_state.get("_cleanup_preview")
        matches_current_file = st.session_state.get("_cleanup_source_file") == str(file_path)

        if preview and matches_current_file:
            results = st.session_state.get("_cleanup_results", {})
            total_fixes = sum(results.values())

            if total_fixes == 0:
                st.info("No issues found with the selected fixes - file already looks clean.")
            else:
                fix_labels = {fid: label for fid, label, _ in AVAILABLE_FIXES}
                summary = ", ".join(
                    f"{count}x {fix_labels.get(fid, fid)}" for fid, count in results.items() if count > 0
                )
                st.success(f"Found and fixed: {summary}")

                st.markdown("**Preview of cleaned version:**")
                with st.container(height=400):
                    st.code(preview, language="markdown")

                save_col, discard_col = st.columns(2)
                with save_col:
                    if st.button("💾 Save Cleaned Version", key="save_cleanup", type="primary", use_container_width=True):
                        try:
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(preview)
                            st.success(f"Saved cleaned version to {file_path.name}")
                            del st.session_state["_cleanup_preview"]
                            st.rerun()
                        except Exception as e:
                            show_error("Failed to save", str(e))
                with discard_col:
                    if st.button("❌ Discard", key="discard_cleanup", use_container_width=True):
                        del st.session_state["_cleanup_preview"]
                        st.rerun()


def render_batch_viewer() -> None:
    """
    Render the batch results viewer for recently converted files.
    """
    st.markdown("---")
    st.markdown("### 📦 Recent Batch Results")
    
    batch_files = SessionManager.get_batch_files()
    zip_path = SessionManager.get_zip_output_path()
    
    if not batch_files and not zip_path:
        st.info("No recent batch conversions. Use the PDF to MD page to convert multiple files.")
        return
    
    if zip_path and Path(zip_path).exists():
        st.markdown("#### ZIP Archive")
        download_button(zip_path, "Download Latest ZIP", "application/zip")
    
    if batch_files:
        st.markdown("#### Individual Files")
        
        # Create a dataframe-like view
        files_data = []
        for file_str in batch_files:
            file_path = Path(file_str)
            if file_path.exists():
                info = FileManager.get_file_info(file_path)
                files_data.append({
                    "Name": info["name"],
                    "Size (MB)": info["size_mb"],
                    "Modified": info["modified"][:19],
                    "Path": str(file_path),
                })
        
        if files_data:
            st.dataframe(
                files_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Path": st.column_config.TextColumn(width="large"),
                },
            )
            
            # Bulk actions
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Clear History", key="clear_batch", use_container_width=True):
                    SessionManager.clear_batch_files()
                    SessionManager.set_zip_output_path(None)
                    st.rerun()
            
            with col2:
                if st.button("📂 Open Output Folder", key="open_output", use_container_width=True):
                    output_dir = get_config().get_output_dir()
                    st.info(f"Output directory: `{output_dir}`")


def render_search() -> None:
    """
    Render the file search/filter interface.
    """
    st.markdown("---")
    st.markdown("### 🔍 Search Files")
    
    output_dir = get_config().get_output_dir()
    files = FileManager.list_files(output_dir, [OUTPUT_EXTENSION, '.json', '.html'])
    
    if not files:
        return
    
    search_term = st.text_input(
        "Search by filename",
        placeholder="Enter search term...",
        key="file_search",
    )
    
    if search_term:
        filtered = [f for f in files if search_term.lower() in f.name.lower()]
        
        if filtered:
            st.markdown(f"Found **{len(filtered)}** matching file(s):")
            
            for f in filtered:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"📄 {f.name}")
                with col2:
                    if st.button("View", key=f"view_{f.stem}", use_container_width=True):
                        # Set as selected in session and reload
                        st.session_state["file_selector"] = f.name
                        st.rerun()
        else:
            st.warning("No files match your search.")


def render_viewer_page() -> None:
    """Render the complete Document Library page."""
    setup_page("Library", "📚")
    init_session()
    render_sidebar()
    
    page_header("📚 Document Library", "Browse, inspect, and export your converted documents")
    
    # Two-column layout
    col_browser, col_preview = st.columns([1, 3])
    
    with col_browser:
        selected_file = render_file_browser()
    
    with col_preview:
        if selected_file:
            render_file_preview(selected_file)
        else:
            st.info(
                """
                ### Welcome to the Markdown Viewer
                
                Select a file from the browser on the left to preview its contents.
                
                You can view files in:
                - **Rendered** mode — See the formatted Markdown
                - **Raw** mode — View the source Markdown
                - **Stats** mode — Analyze document structure
                """
            )
    
    # Additional sections below
    render_batch_viewer()
    render_search()


def main() -> None:
    """Page entry point."""
    apply_custom_css()
    render_viewer_page()


if __name__ == "__main__":
    main()