"""
--------------------------------------------------------
PDF to Markdown Studio

PDF to Markdown Page

Author  : Deepak Pawar
Version : 1.2
--------------------------------------------------------
"""

from __future__ import annotations

import streamlit as st

from core.config import CONFIG
from core.constants import OUTPUT_FORMATS
from core.conversion_manager import ConversionManager
from core.zip_utils import create_zip_from_dir
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
# OUTPUT DIRECTORY SETTINGS
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
        "🚀 Marker OCR",
        expanded=True,
    )

    # Dashboard Widgets inside the status container
    with status:
        current_file = st.empty()
        current_stage = st.empty()

        progress_bar = st.progress(0)
        progress_text = st.empty()

        elapsed_time = st.empty()

        activity = st.empty()
        
    activity_log = []

    def update_progress(event: dict | str):
        # Handle simple string messages from ConversionManager
        if isinstance(event, str):
            activity_log.append(event)
            activity.markdown(
                "### 📋 Activity\n\n"
                + "\n\n".join(activity_log[-6:])
            )
            return

        event_type = event.get("type")

        # -----------------------------
        # Conversion Started
        # -----------------------------

        if event_type == "start":

            current_file.markdown(
                f"### 📄 Current File\n\n**{event['file']}**"
            )

            return

        # -----------------------------
        # Stage Changed
        # -----------------------------

        if event_type == "stage":

            current_stage.markdown(
                f"### ⚙ Current Stage\n\n**{event['stage']}**"
            )

            return

        # -----------------------------
        # Progress
        # -----------------------------

        if event_type == "progress":
            
            # Ensure value is bounded between 0.0 and 1.0 for Streamlit
            percent_val = max(0.0, min(1.0, event["percent"] / 100.0))
            progress_bar.progress(percent_val)

            progress_text.markdown(
                f"### 📊 Progress\n\n"
                f"**{event['current']} / {event['total']}**"
            )

            return

        # -----------------------------
        # Stage Completed
        # -----------------------------

        if event_type == "stage_complete":

            activity_log.append(
                f"✅ {event['stage']} Completed"
            )

            activity.markdown(
                "### 📋 Activity\n\n"
                + "\n\n".join(activity_log[-6:])
            )

            return

        # -----------------------------
        # Markdown Saved
        # -----------------------------

        if event_type == "saved":

            activity_log.append(
                "💾 Markdown Saved"
            )

            activity.markdown(
                "### 📋 Activity\n\n"
                + "\n\n".join(activity_log[-6:])
            )

            return

        # -----------------------------
        # Completed
        # -----------------------------

        if event_type == "complete":

            progress_bar.progress(1.0)

            elapsed_time.markdown(
                f"### ⏱ Elapsed Time\n\n"
                f"**{event['elapsed']:.2f} minutes**"
            )

            status.update(
                label="✅ Conversion Completed",
                state="complete",
            )

            return

        # -----------------------------
        # Error
        # -----------------------------

        if event_type == "error":

            status.update(
                label="❌ Conversion Failed",
                state="error",
            )

            st.error(event["message"])

    try:
        result = manager.convert(
            uploaded_files,
            progress_callback=update_progress,
        )
            
    except Exception as e:
        status.update(
            label="❌ Unexpected Error",
            state="error",
        )
        st.exception(e)
        st.stop()

    # ==========================================================
    # RENDER FINAL OUTPUT & DOWNLOADS
    # ==========================================================

    if result.success:

        st.success("✅ Conversion Completed!")
        
        # Show the elapsed time / success message output by MarkerEngine
        st.info(result.message)

        # Generate ZIP in memory and offer bulk download
        zip_bytes = create_zip_from_dir(result.output_path)
        if zip_bytes:
            st.download_button(
                label="📦 Download All as ZIP",
                data=zip_bytes,
                file_name="converted_markdowns.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )

        horizontal_line()

        st.write(
            f"### Generated Files ({len(result.markdown_files)})"
        )

        if result.markdown_files:
            for md in result.markdown_files:
                
                # We use columns to put the file name on the left and the download button on the right
                col_file, col_btn = st.columns([3, 1])
                
                with col_file:
                    st.write(f"📄 **{md.name}**")
                
                with col_btn:
                    try:
                        # Read the file content for individual download
                        with open(md, "r", encoding="utf-8") as f:
                            md_content = f.read()
                            
                        # Streamlit requires a unique key for every button generated in a loop
                        st.download_button(
                            label="⬇️ Download",
                            data=md_content,
                            file_name=md.name,
                            mime="text/markdown",
                            key=f"btn_{md.name}",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error("Error reading file")
                        
        else:
            st.warning("No Markdown files were found.")

        horizontal_line()

        # Display raw paths for debugging/reference
        st.write("### Session Diagnostics")
        colA, colB = st.columns(2)
        with colA:
            st.caption("Session Folder")
            st.code(str(result.session_path))
        with colB:
            st.caption("Output Folder")
            st.code(str(result.output_path))

    else:

        st.error("Conversion Failed")
        st.code(result.message)