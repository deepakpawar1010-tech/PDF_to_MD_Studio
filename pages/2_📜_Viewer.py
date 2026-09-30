"""
TeXify Studio v2.0 - Markdown & KaTeX Viewer
============================================
Client-side Markdown document viewer with 100% KaTeX math rendering,
Mathpix-style LaTeX copy, in-document search, and live editing.
Zero server storage required — open any file directly from your computer!
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from core.config import get_config
from core.constants import APP_NAME, OUTPUT_DIR, OUTPUT_EXTENSION, PAGE_ICON
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
    show_success,
    show_warning,
)

logger = get_logger(__name__)


def extract_math_formulas(text: str):
    """Extract all inline and display math formulas from markdown text."""
    display_matches = re.findall(r"\$\$([\s\S]*?)\$\$", text)
    inline_matches = re.findall(r"(?<!\$)\$([^$\n]+?)\$(?!\$)", text)
    return display_matches, inline_matches


def render_viewer_page() -> None:
    """Render the complete Markdown & KaTeX Document Viewer."""
    setup_page("Viewer", "📜")
    init_session()
    render_sidebar()

    page_header(
        "📜 Markdown & KaTeX Viewer",
        "Open, inspect, search, and edit any Markdown document with 100% KaTeX math rendering and Mathpix copy",
    )

    # Top file-loading options
    load_tab1, load_tab2, load_tab3 = st.tabs([
        "📂 Open Local File",
        "📋 Paste Markdown",
        "🕒 Recent Session Files",
    ])

    loaded_content: Optional[str] = None
    loaded_filename: str = "document.md"

    with load_tab1:
        uploaded_doc = st.file_uploader(
            "Drag and drop any Markdown (.md) file from your computer",
            type=["md", "txt", "markdown"],
            key="viewer_file_uploader",
            help="Your file is processed securely in your browser session with zero server storage.",
        )
        if uploaded_doc is not None:
            try:
                loaded_content = uploaded_doc.read().decode("utf-8", errors="replace")
                loaded_filename = uploaded_doc.name
            except Exception as e:
                show_error("Failed to read file", str(e))

    with load_tab2:
        pasted_text = st.text_area(
            "Paste Markdown or LaTeX text here",
            height=160,
            placeholder="# Sample Document\n\nSolve the equation: $$x^2 + 5x + 6 = 0$$\n\nThe roots are $x = -2$ and $x = -3$.",
            key="viewer_pasted_text",
        )
        if pasted_text.strip():
            # If user entered pasted text, and no file was explicitly uploaded in tab 1
            if uploaded_doc is None:
                loaded_content = pasted_text
                loaded_filename = "pasted_document.md"

    with load_tab3:
        # Check if any converted files exist in output/
        output_dir = get_config().get_output_dir()
        existing_files = FileManager.list_files(output_dir, [OUTPUT_EXTENSION, ".json", ".html"]) if output_dir.exists() else []
        if existing_files:
            file_options = [f.name for f in existing_files]
            chosen_file = st.selectbox(
                "Select a recently converted file from this session",
                options=file_options,
                key="viewer_session_file_selector",
            )
            if chosen_file and uploaded_doc is None and not pasted_text.strip():
                try:
                    fpath = output_dir / chosen_file
                    with open(fpath, "r", encoding="utf-8") as f:
                        loaded_content = f.read()
                    loaded_filename = chosen_file
                except Exception as e:
                    show_error("Could not load session file", str(e))
        else:
            st.info("No recent session files found on the server. You can drag and drop your downloaded `.md` files in the 'Open Local File' tab anytime!")

    if not loaded_content:
        st.markdown("---")
        st.info("👆 **Get started:** Upload any `.md` file, paste Markdown text above, or select a recent file.")
        return

    # Document Metrics Bar
    st.markdown("---")
    disp_matches, in_matches = extract_math_formulas(loaded_content)
    total_formulas = len(disp_matches) + len(in_matches)
    char_count = len(loaded_content)
    line_count = len(loaded_content.splitlines())

    meta_col1, meta_col2, meta_col3, meta_col4, meta_col5 = st.columns([2.5, 1, 1, 1.2, 1.3])
    with meta_col1:
        st.markdown(f"**📄 Document:** `{loaded_filename}`")
    with meta_col2:
        st.caption(f"📏 **{line_count:,}** lines")
    with meta_col3:
        st.caption(f"🔤 **{char_count:,}** chars")
    with meta_col4:
        st.caption(f"🧮 **{total_formulas}** formulas")
    with meta_col5:
        st.download_button(
            "📥 Download .md",
            data=loaded_content,
            file_name=loaded_filename,
            mime="text/markdown",
            key="btn_download_viewer_doc",
            use_container_width=True,
        )

    # Document Views
    view_tab_render, view_tab_raw, view_tab_edit, view_tab_formulas = st.tabs([
        "🎨 Rendered View",
        "📄 Raw Markdown",
        "✏️ Live Editor",
        "🧮 Formula Inspector",
    ])

    with view_tab_render:
        render_markdown_with_math(loaded_content, height=800)

    with view_tab_raw:
        st.code(loaded_content, language="markdown", line_numbers=True)

    with view_tab_edit:
        st.caption("Edit the Markdown below. Changes will immediately update your download and preview.")
        edited_content = st.text_area(
            "Markdown Editor",
            value=loaded_content,
            height=500,
            key=f"editor_{loaded_filename}",
            label_visibility="collapsed",
        )
        if st.button("🔄 Update & Preview Changes", type="primary", key="btn_apply_edits"):
            st.session_state["edited_override"] = edited_content
            st.rerun()

    with view_tab_formulas:
        st.markdown(f"### 🧮 Detected Formulas ({total_formulas})")
        if total_formulas == 0:
            st.info("No LaTeX formulas ($...$ or $$...$$) detected in this document.")
        else:
            if disp_matches:
                st.markdown("#### Display Formulas (`$$ ... $$`)")
                for idx, eq in enumerate(disp_matches):
                    with st.container(border=True):
                        st.latex(eq)
                        st.code(f"$${eq}$$", language="latex")

            if in_matches:
                st.markdown("#### Inline Formulas (`$ ... $`)")
                # Show in a clean table or list
                sample_inline = in_matches[:40]
                for idx, eq in enumerate(sample_inline):
                    with st.container(border=True):
                        eq_col1, eq_col2 = st.columns([1, 2])
                        with eq_col1:
                            try:
                                st.latex(eq)
                            except Exception:
                                st.code(eq)
                        with eq_col2:
                            st.code(f"${eq}$", language="latex")
                if len(in_matches) > 40:
                    st.caption(f"Showing first 40 of {len(in_matches)} inline formulas.")


def main() -> None:
    """Page entry point."""
    apply_custom_css()
    render_viewer_page()


if __name__ == "__main__":
    main()
