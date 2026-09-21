"""
PDF_to_MD_Studio v1.0 - Core Constants
=====================================
Centralized constants for the entire application.
"""

import os
from pathlib import Path

# =============================================================================
# APPLICATION METADATA
# =============================================================================

APP_NAME = "TeXify Studio"
APP_VERSION = "2.0.0"
APP_AUTHOR = "TeXify Studio Team"
APP_DESCRIPTION = "High-precision PDF to Markdown conversion with 100% LaTeX math accuracy"
APP_URL = ""

# =============================================================================
# PATHS & DIRECTORIES
# =============================================================================

# Base project directory (parent of core/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Core directories
CORE_DIR = BASE_DIR / "core"
PAGES_DIR = BASE_DIR / "pages"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for dir_path in [OUTPUT_DIR, TEMP_DIR, LOGS_DIR, ASSETS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# =============================================================================
# MARKER EXECUTABLE
# =============================================================================

# Use marker_single.exe instead of marker.exe
MARKER_EXECUTABLE = "marker_single.exe"

# Marker command templates
MARKER_CMD_SINGLE = "{marker} {input} --output_dir {output_dir}"
MARKER_CMD_BATCH = "{marker} {input_dir} --output_dir {output_dir}"

# =============================================================================
# FILE EXTENSIONS
# =============================================================================

SUPPORTED_INPUT_EXTENSIONS = [".pdf"]
OUTPUT_EXTENSION = ".md"
ZIP_EXTENSION = ".zip"

# =============================================================================
# CONVERSION SETTINGS
# =============================================================================

DEFAULT_CONVERSION_TIMEOUT = 300  # seconds
MAX_FILE_SIZE_MB = 100  # Maximum individual file size
MAX_BATCH_SIZE = 50  # Maximum files in a batch conversion

# =============================================================================
# UI SETTINGS
# =============================================================================

PAGE_TITLE = f"{APP_NAME} v{APP_VERSION}"
PAGE_ICON = "⚡"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# Theme colors
PRIMARY_COLOR = "#6366F1"
BACKGROUND_COLOR = "#0B0F19"
SECONDARY_BACKGROUND = "#1E293B"
TEXT_COLOR = "#F8FAFC"

# =============================================================================
# LOGGING SETTINGS
# =============================================================================

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = "INFO"
LOG_FILE_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
LOG_FILE_BACKUP_COUNT = 3

# =============================================================================
# SESSION STATE KEYS
# =============================================================================

SESSION_KEYS = {
    "conversion_history": "conversion_history",
    "current_file": "current_file",
    "output_path": "output_path",
    "settings": "settings",
    "theme": "theme",
    "last_conversion_time": "last_conversion_time",
    "batch_files": "batch_files",
    "zip_output_path": "zip_output_path",
}

# =============================================================================
# SETTINGS DEFAULTS
# =============================================================================

DEFAULT_SETTINGS = {
    "engine": "gemini",
    "gemini_api_key": "",
    "gemini_model": "gemini-3.5-flash-lite",
    "output_format": "markdown",
    "preserve_images": True,
    "image_format": "png",
    "ocr_enabled": False,
    "language": "auto",
    "quality": "high",
    "timeout": DEFAULT_CONVERSION_TIMEOUT,
    "auto_cleanup": True,
    "dark_mode": True,
}

# =============================================================================
# MESSAGES & LABELS
# =============================================================================

MESSAGES = {
    "welcome": f"Welcome to {APP_NAME}! Upload a PDF to get started.",
    "upload_prompt": "Drag and drop your PDF file here or click to browse",
    "converting": "Converting your PDF to Markdown...",
    "success": "Conversion completed successfully!",
    "error": "An error occurred during conversion.",
    "no_file": "Please upload a PDF file first.",
    "invalid_file": "Invalid file type. Please upload a PDF file.",
    "file_too_large": f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB.",
}

# =============================================================================
# ABOUT PAGE CONTENT
# =============================================================================

ABOUT_CONTENT = f"""
## {APP_NAME} v{APP_VERSION}

{APP_DESCRIPTION}

### Features
- **Ultra-Fast Conversion**: Convert dense documents in seconds using Gemini Vision (or offline Marker)
- **100% Math Accuracy**: Flawless LaTeX formatting for formulas, subscripts, roots, and fractions
- **Mathpix-Style LaTeX Copy**: Select text or click any formula to copy real LaTeX (`$...$`) directly
- **Side-by-Side Studio**: Real-time 50:50 comparison between the original PDF and rendered output
- **Image & Diagram Extraction**: High-fidelity figure extraction and asset management

### Technology Stack
- **AI Engine**: Google Gemini Multimodal Vision (`gemini-3.5-flash-lite`) & Marker Engine
- **Frontend**: Streamlit with custom KaTeX & marked.js rendering
- **Language**: Python 3.12+

### License
MIT License
"""

# =============================================================================
# HELP TEXT
# =============================================================================

HELP_TEXT = {
    "marker_path": "Path to the marker_single.exe executable. Must be accessible in PATH or provide full path.",
    "output_dir": "Directory where converted Markdown files will be saved.",
    "timeout": "Maximum time (in seconds) to wait for conversion to complete.",
    "preserve_images": "Extract and save images from the PDF alongside the Markdown file.",
    "ocr": "Enable OCR for scanned PDFs (requires additional setup).",
    "quality": "Conversion quality: 'fast' for speed, 'high' for accuracy.",
}