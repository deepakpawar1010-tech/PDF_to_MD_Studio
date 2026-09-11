"""
PDF_to_MD_Studio v1.0 - Worksheet Splitter Page
===============================================
Split uploaded textbook PDFs into worksheet-wise PDFs using extractable
WORKSHEET headings or CUQ fallback markers.
"""

from pathlib import Path

import streamlit as st

from core.file_manager import FileManager
from core.logger import get_logger
from core.session_manager import init_session
from core.ui_helpers import (
    apply_custom_css,
    file_uploader_area,
    page_header,
    render_sidebar,
    setup_page,
    show_error,
    show_info,
    show_success,
)
from core.zip_utils import create_zip_archive
from core.worksheet_splitter.service import split_pdfs

logger = get_logger(__name__)


def _heading_rows(headings: list) -> list[dict[str, str | int]]:
    return [
        {
            "Type": heading.kind,
            "Number": heading.number,
            "Page": heading.page_number,
            "Detected Text": heading.text,
        }
        for heading in headings
    ]


def _candidate_rows(candidates: list) -> list[dict[str, str | int]]:
    return [
        {
            "Worksheet": candidate.worksheet_name,
            "Page": candidate.page_number,
            "Trigger": candidate.trigger_text,
            "Reason": candidate.reason,
        }
        for candidate in candidates
    ]


def _safe_key(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in value)


def _download_file_button(file_path: Path, label: str, key: str, mime: str = "application/pdf") -> None:
    try:
        data = file_path.read_bytes()
        st.download_button(
            label=label,
            data=data,
            file_name=file_path.name,
            mime=mime,
            key=key,
            use_container_width=True,
        )
    except Exception as error:
        show_error("Download failed", str(error))


def _render_result(result: dict, batch_key: str) -> list[Path]:
    st.markdown(f"### {result['pdf_name']}")

    if result.get("error"):
        show_error(f"Failed to process {result['pdf_name']}", result['error'])
        return []

    headings = result.get("headings", [])
    candidates = result.get("candidates", [])
    saved_files = result.get("saved_files", [])
    output_dir = result.get("output_dir")

    if headings:
        st.markdown("**Detected Worksheet/Synopsis Headings**")
        st.dataframe(_heading_rows(headings), use_container_width=True, hide_index=True)
    else:
        show_info("No extractable worksheet/synopsis headings were found. Using CUQ fallback if available.")

    if candidates:
        st.markdown("**Detected Worksheet Starts**")
        st.dataframe(_candidate_rows(candidates), use_container_width=True, hide_index=True)
    else:
        show_info("No worksheet candidates were found in this PDF.")

    if saved_files:
        show_success(
            f"Saved {len(saved_files)} worksheet PDF(s)",
            f"Output folder: {output_dir}",
        )

        zip_path = create_zip_archive(
            saved_files,
            output_dir=output_dir,
            archive_name=f"{Path(result['pdf_name']).stem}_worksheets.zip",
        )

        top_col1, top_col2 = st.columns([3, 2])
        with top_col1:
            st.caption(f"Output folder: {output_dir}")
        with top_col2:
            if zip_path and zip_path.exists():
                _download_file_button(
                    zip_path,
                    "📦 Download ZIP",
                    key=f"zip_{batch_key}_{_safe_key(result['pdf_name'])}",
                    mime="application/zip",
                )

        cols = st.columns(min(len(saved_files), 4))
        for index, saved_file in enumerate(saved_files):
            with cols[index % len(cols)]:
                _download_file_button(
                    saved_file,
                    f"⬇ Download {saved_file.name}",
                    key=f"pdf_{batch_key}_{_safe_key(result['pdf_name'])}_{index}",
                )
    else:
        show_info("No worksheet PDFs were created for this file.")

    return saved_files


def render_page() -> None:
    setup_page("Worksheet Splitter", "🧩")
    init_session()
    render_sidebar()

    page_header("🧩 Worksheet Splitter", "Split textbook PDFs into worksheet-wise PDFs using WORKSHEET or CUQ detection.")

    uploaded_files = file_uploader_area(
        label="Upload worksheet PDFs",
        key="worksheet_splitter_uploader",
        accept_multiple=True,
    )

    if not uploaded_files:
        st.info("Upload one or more textbook PDFs to detect and split worksheets.")
        return

    st.markdown(f"**{len(uploaded_files)} file(s) selected**")

    file_manager = FileManager()
    saved_paths: list[Path] = []
    invalid_messages: list[str] = []

    for uploaded_file in uploaded_files:
        temp_path = file_manager.save_uploaded_file(uploaded_file)
        is_valid, error = file_manager.validate_file(temp_path)
        if is_valid:
            saved_paths.append(temp_path)
            st.markdown(f"✅ {uploaded_file.name}")
        else:
            invalid_messages.append(f"❌ {uploaded_file.name}: {error}")
            file_manager.delete_file(temp_path)

    for message in invalid_messages:
        st.markdown(message)

    if not saved_paths:
        show_error("No valid files", "None of the uploaded PDFs passed validation.")
        return

    st.markdown("---")
    if st.button("🧩 Split Worksheets", type="primary", use_container_width=True):
        with st.spinner("Detecting worksheet starts and generating PDF files..."):
            results = split_pdfs(saved_paths)

        all_saved_files: list[Path] = []
        st.markdown("---")
        batch_key = str(abs(hash("|".join(path.name for path in saved_paths))))
        for result in results:
            all_saved_files.extend(_render_result(result, batch_key=batch_key))
            st.markdown("---")

        if len(all_saved_files) > 1:
            batch_zip_dir = all_saved_files[0].parent.parent if all_saved_files else None
            batch_zip = create_zip_archive(
                all_saved_files,
                output_dir=batch_zip_dir,
                archive_name="worksheet_splitter_batch.zip",
            )
            if batch_zip and batch_zip.exists():
                st.markdown("## Batch Download")
                _download_file_button(
                    batch_zip,
                    "📦 Download All Worksheets ZIP",
                    key=f"all_zip_{batch_key}",
                    mime="application/zip",
                )

    for temp_path in saved_paths:
        file_manager.delete_file(temp_path)


def main() -> None:
    apply_custom_css()
    render_page()


if __name__ == "__main__":
    main()