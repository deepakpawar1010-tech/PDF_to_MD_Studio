"""
PDF_to_MD_Studio v1.0 - File Manager
====================================
Handles all file system operations including uploads,
validation, cleanup, and path management.
"""

import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from core.constants import (
    MAX_BATCH_SIZE,
    MAX_FILE_SIZE_MB,
    OUTPUT_EXTENSION,
    SUPPORTED_INPUT_EXTENSIONS,
    TEMP_DIR,
    OUTPUT_DIR,
    ZIP_EXTENSION,
)
from core.config import get_config
from core.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """
    Centralized file operations manager.
    Handles uploads, validation, cleanup, and directory management.
    """
    
    @staticmethod
    def validate_file(file_path: Path) -> Tuple[bool, str]:
        """
        Validate a file for conversion.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path.exists():
            return False, f"File not found: {file_path}"
        
        if not file_path.is_file():
            return False, f"Path is not a file: {file_path}"
        
        # Check extension
        if file_path.suffix.lower() not in SUPPORTED_INPUT_EXTENSIONS:
            ext_list = ", ".join(SUPPORTED_INPUT_EXTENSIONS)
            return False, f"Unsupported file type '{file_path.suffix}'. Supported: {ext_list}"
        
        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            return False, f"File too large ({file_size_mb:.1f}MB). Maximum: {MAX_FILE_SIZE_MB}MB"
        
        return True, ""
    
    @staticmethod
    def validate_batch(files: List[Path]) -> Tuple[bool, str, List[Path]]:
        """
        Validate a batch of files.
        
        Args:
            files: List of file paths to validate
            
        Returns:
            Tuple of (all_valid, error_message, valid_files)
        """
        if len(files) > MAX_BATCH_SIZE:
            return False, f"Too many files ({len(files)}). Maximum: {MAX_BATCH_SIZE}", []
        
        valid_files = []
        errors = []
        
        for file_path in files:
            is_valid, error = FileManager.validate_file(file_path)
            if is_valid:
                valid_files.append(file_path)
            else:
                errors.append(f"{file_path.name}: {error}")
        
        if errors:
            error_msg = "Some files failed validation:\n" + "\n".join(errors)
            return False, error_msg, valid_files
        
        return True, "", valid_files
    
    @staticmethod
    def generate_output_path(input_path: Path, output_dir: Optional[Path] = None) -> Path:
        """
        Generate an output path for a converted file.
        
        Args:
            input_path: Original input file path
            output_dir: Optional custom output directory
            
        Returns:
            Path for the output Markdown file
        """
        if output_dir is None:
            output_dir = get_config().get_output_dir()
        
        # Ensure output_dir is actually a directory path, not a file path
        if output_dir.suffix:
            output_dir = output_dir.parent
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Use input filename with .md extension
        output_name = input_path.stem + OUTPUT_EXTENSION
        output_path = output_dir / output_name
        
        # Handle duplicates by appending timestamp
        if output_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{input_path.stem}_{timestamp}{OUTPUT_EXTENSION}"
            output_path = output_dir / output_name
        
        return output_path
    
    @staticmethod
    def generate_unique_temp_dir() -> Path:
        """
        Generate a unique temporary directory.
        
        Returns:
            Path to a new unique temp directory
        """
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_subdir = TEMP_DIR / f"conv_{timestamp}_{unique_id}"
        
        # Ensure parent exists and is a directory
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        
        # Safety check: ensure we're not overwriting a file
        if temp_subdir.exists() and temp_subdir.is_file():
            temp_subdir.unlink()
        
        temp_subdir.mkdir(parents=True, exist_ok=True)
        return temp_subdir
    
    @staticmethod
    def save_uploaded_file(uploaded_file, dest_dir: Optional[Path] = None) -> Path:
        """
        Save an uploaded file to disk.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            dest_dir: Optional destination directory
            
        Returns:
            Path to the saved file
        """
        if dest_dir is None:
            dest_dir = TEMP_DIR
        
        # Ensure dest_dir is a directory path
        if dest_dir.suffix:
            dest_dir = dest_dir.parent
        
        # Create directory using os.makedirs for reliability
        os.makedirs(str(dest_dir), exist_ok=True)
        
        # Sanitize filename - remove problematic characters for Windows
        original_name = uploaded_file.name
        safe_name = "".join(c for c in original_name if c.isalnum() or c in "._- ")
        safe_name = safe_name.strip()
        
        if not safe_name or safe_name.startswith('.'):
            safe_name = f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        if not safe_name.lower().endswith('.pdf'):
            safe_name += '.pdf'
        
        file_path = dest_dir / safe_name
        
        # Handle duplicates
        counter = 1
        original_path = file_path
        while file_path.exists():
            stem = original_path.stem
            suffix = original_path.suffix
            file_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        # Write file
        try:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            logger.info(f"Saved uploaded file: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            raise
    
    @staticmethod
    def cleanup_temp_files(max_age_hours: int = 24) -> int:
        """
        Remove temporary files older than specified hours.
        
        Args:
            max_age_hours: Maximum age of temp files in hours
            
        Returns:
            Number of files/directories removed
        """
        if not TEMP_DIR.exists():
            return 0
        
        removed_count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        for item in TEMP_DIR.iterdir():
            try:
                if item.stat().st_mtime < cutoff_time:
                    if item.is_file():
                        item.unlink()
                        removed_count += 1
                    elif item.is_dir():
                        shutil.rmtree(item)
                        removed_count += 1
            except (OSError, PermissionError):
                continue
        
        return removed_count
    
    @staticmethod
    def cleanup_all_temp() -> int:
        """
        Remove all temporary files and directories.
        
        Returns:
            Number of items removed
        """
        if not TEMP_DIR.exists():
            return 0
        
        removed_count = 0
        for item in TEMP_DIR.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                    removed_count += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    removed_count += 1
            except (OSError, PermissionError):
                continue
        
        return removed_count
    
    @staticmethod
    def ensure_dir(path: Path) -> Path:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            path: Directory path
            
        Returns:
            The directory path
        """
        # If path looks like a file (has extension), use parent
        if path.suffix:
            path = path.parent
        
        os.makedirs(str(path), exist_ok=True)
        return path
    
    @staticmethod
    def get_file_info(file_path: Path) -> dict:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file metadata
        """
        stat = file_path.stat()
        return {
            "name": file_path.name,
            "stem": file_path.stem,
            "suffix": file_path.suffix,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "path": str(file_path),
        }
    
    @staticmethod
    def list_files(directory: Path, extensions: Optional[List[str]] = None) -> List[Path]:
        """
        List files in a directory, optionally filtered by extension.
        
        Args:
            directory: Directory to scan
            extensions: Optional list of extensions to filter by
            
        Returns:
            List of file paths
        """
        if not directory.exists() or not directory.is_dir():
            return []
        
        files = [f for f in directory.iterdir() if f.is_file()]
        
        if extensions:
            files = [f for f in files if f.suffix.lower() in extensions]
        
        return sorted(files)
    
    @staticmethod
    def move_file(source: Path, destination: Path) -> Path:
        """
        Move a file, creating destination directory if needed.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            Final destination path
        """
        # Ensure destination parent is a directory, not a file
        dest_parent = destination.parent
        if dest_parent.suffix:
            dest_parent = dest_parent.parent
        
        os.makedirs(str(dest_parent), exist_ok=True)
        
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        
        return Path(shutil.move(str(source), str(destination)))
    
    @staticmethod
    def copy_file(source: Path, destination: Path) -> Path:
        """
        Copy a file, creating destination directory if needed.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            Final destination path
        """
        dest_parent = destination.parent
        if dest_parent.suffix:
            dest_parent = dest_parent.parent
        
        os.makedirs(str(dest_parent), exist_ok=True)
        return Path(shutil.copy2(str(source), str(destination)))
    
    @staticmethod
    def delete_file(file_path: Path) -> bool:
        """
        Safely delete a file.
        
        Args:
            file_path: Path to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return True
            return False
        except (OSError, PermissionError):
            return False
    
    @staticmethod
    def generate_zip_name() -> str:
        """
        Generate a unique ZIP archive name.
        
        Returns:
            ZIP filename string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:6]
        return f"pdf_to_md_batch_{timestamp}_{unique_id}{ZIP_EXTENSION}"