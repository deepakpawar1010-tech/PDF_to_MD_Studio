"""
--------------------------------------------------------
PDF to Markdown Studio

PDF to Markdown Page

Author  : Deepak Pawar
Version : 1.1
--------------------------------------------------------
"""

from __future__ import annotations

import streamlit as st

from core.config import CONFIG
from core.constants import OUTPUT_FORMATS
from core.conversion_manager import ConversionManager
from core.ui_helpers import (
    horizontal_line,
    info_box,
    page_title,
    section_header,
)

# ==========================================================
# PAGE TITLE
# ==========================================================

page_title(
    "📄 PDF to Markdown",
    "Convert PDF files into high-quality Markdown using Marker OCR."
)

# ==========================================================
# INPUT METHOD
# ==========================================================

section_header("Input Method")

input_method = st.radio(
    "Choose how you want to provide PDFs",
    [
        "Upload PDFs",
        "Local Folder"
    ],
    horizontal=True
)

horizontal_line()

# ==========================================================
# PDF INPUT
# ==========================================================

uploaded_files = []
folder_path = ""

if input_method == "Upload PDFs":

    uploaded_files = st.file_uploader(
        "Upload one or more PDF files",
        type=["pdf"],
        accept_multiple_files=True,
    )

else:

    folder_path = st.text_input(
        "Folder Path",
        placeholder=r"C:\Books\Maths"
    )

horizontal_line()

# ==========================================================
# CONVERSION SETTINGS
# ==========================================================

section_header("Conversion Settings")

col1, col2 = st.columns(2)

with col1:

    force_ocr = st.checkbox(
        "Force OCR",
        value=CONFIG.force_ocr,
    )

    extract_images = st.checkbox(
        "Extract Images",
        value=CONFIG.extract_images,
    )

with col2:

    skip_existing = st.checkbox(
        "Skip Existing",
        value=CONFIG.skip_existing,
    )

    output_format = st.selectbox(
        "Output Format",
        OUTPUT_FORMATS,
        index=0,
    )

horizontal_line()

# ==========================================================
# OUTPUT
# ==========================================================

section_header("Output Folder")

output_folder = st.text_input(
    "Output Folder",
    value="outputs"
)

horizontal_line()

# ==========================================================
# FILE SUMMARY
# ==========================================================

section_header("Files")

if input_method == "Upload PDFs":

    if uploaded_files:

        st.success(f"{len(uploaded_files)} PDF(s) selected")

        for pdf in uploaded_files:

            size_mb = pdf.size / (1024 * 1024)

            st.write(
                f"📄 **{pdf.name}**  •  {size_mb:.2f} MB"
            )

    else:

        info_box("No PDF files selected.")

else:

    if folder_path:

        st.info(folder_path)

    else:

        info_box("No folder selected.")

horizontal_line()

# ==========================================================
# CONVERT
# ==========================================================

if st.button(
    "🚀 Convert PDFs",
    type="primary",
    use_container_width=True,
):

    if input_method == "Local Folder":

        st.warning(
            "Folder conversion will be added in Version 1.1."
        )

        st.stop()

    if len(uploaded_files) == 0:

        st.warning("Please upload at least one PDF.")

        st.stop()

    manager = ConversionManager()
    
    status = st.status(
        "🚀 Starting Marker...",
        expanded=True,
    )
    
    def update_progress(message: str):
        status.write(message)
        
    try:
        result = manager.convert(
            uploaded_files,
            progress_callback=update_progress,
        )
        
        if result.success:
            status.update(
                label="✅ Conversion Completed",
                state="complete",
            )
        else:
            status.update(
                label="❌ Conversion Failed",
                state="error",
            )
            
    except Exception as e:
        status.update(
            label="❌ Unexpected Error",
            state="error",
        )
        st.exception(e)
        st.stop()

    # --- Render final output ---

    if result.success:

        st.success("✅ Conversion Completed!")
        
        # Show the elapsed time / success message output by MarkerEngine
        st.info(result.message)

        st.write("### Session Folder")
        st.code(str(result.session_path))

        st.write("### Output Folder")
        st.code(str(result.output_path))

        st.write(
            f"### Markdown Files ({len(result.markdown_files)})"
        )

        if result.markdown_files:
            for md in result.markdown_files:
                st.write(f"📄 {md.name}")
        else:
            st.warning("No Markdown files were found.")

    else:

        st.error("Conversion Failed")
        st.code(result.message)