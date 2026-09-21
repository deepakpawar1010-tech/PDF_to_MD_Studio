"""
PDF_to_MD_Studio v1.0 - ZIP Utilities
====================================
Handles creation and management of ZIP archives for batch conversions.
"""

import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from core.constants import APP_NAME, OUTPUT_DIR, ZIP_EXTENSION
from core.config import get_config
from core.logger import get_logger

logger = get_logger(__name__)


class ZipManager:
    """
    Manages ZIP archive creation for converted files.
    """
    
    @staticmethod
    def create_archive(
        files: List[Path],
        output_dir: Optional[Path] = None,
        archive_name: Optional[str] = None,
        include_source_info: bool = True,
    ) -> Optional[Path]:
        """
        Create a ZIP archive containing the specified files.
        
        Args:
            files: List of file paths to include
            output_dir: Directory for the ZIP file
            archive_name: Optional custom archive name
            include_source_info: Include a manifest file with source info
            
        Returns:
            Path to created ZIP file, or None if failed
        """
        if not files:
            logger.warning("No files provided for ZIP archive")
            return None
        
        # Determine output directory
        if output_dir is None:
            output_dir = get_config().get_output_dir()
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate archive name
        if archive_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"pdf_to_md_batch_{timestamp}{ZIP_EXTENSION}"
        
        # Ensure proper extension
        if not archive_name.endswith(ZIP_EXTENSION):
            archive_name += ZIP_EXTENSION
        
        zip_path = output_dir / archive_name
        
        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                # Add manifest if requested
                if include_source_info:
                    manifest = ZipManager._generate_manifest(files)
                    zf.writestr("_manifest.txt", manifest)
                
                # Add each file
                for file_path in files:
                    if not file_path.exists():
                        logger.warning(f"File not found, skipping: {file_path}")
                        continue
                    
                    # Use relative path in archive for clean structure
                    arcname = file_path.name
                    zf.write(file_path, arcname)
                    logger.debug(f"Added to ZIP: {arcname}")
                
                # Also include any associated asset files (images)
                for file_path in files:
                    asset_files = ZipManager._find_assets(file_path)
                    for asset in asset_files:
                        if asset.exists():
                            zf.write(asset, asset.name)
                            logger.debug(f"Added asset to ZIP: {asset.name}")
            
            logger.info(f"ZIP archive created: {zip_path} ({len(files)} files)")
            return zip_path
            
        except (OSError, zipfile.BadZipFile) as e:
            logger.error(f"Failed to create ZIP archive: {e}")
            # Clean up partial file
            if zip_path.exists():
                zip_path.unlink()
            return None
    
    @staticmethod
    def _generate_manifest(files: List[Path]) -> str:
        """
        Generate a manifest text describing archive contents.
        
        Args:
            files: List of files in the archive
            
        Returns:
            Manifest text content
        """
        lines = [
            f"{APP_NAME} - Batch Conversion Manifest",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Files: {len(files)}",
            "",
            "Contents:",
            "-" * 30,
        ]
        
        for i, file_path in enumerate(files, 1):
            size_kb = file_path.stat().st_size / 1024 if file_path.exists() else 0
            lines.append(f"{i}. {file_path.name} ({size_kb:.1f} KB)")
        
        lines.extend([
            "",
            "Generated with marker_single.exe",
            "https://github.com/VikParuchuri/marker",
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def _find_assets(md_file: Path) -> List[Path]:
        """
        Find associated asset files (images) for a markdown file.
        
        Args:
            md_file: Path to the markdown file
            
        Returns:
            List of associated asset file paths
        """
        assets = []
        if not md_file.exists():
            return assets
        
        parent_dir = md_file.parent
        stem = md_file.stem
        
        # Common image extensions
        image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"]
        
        # Look for files with matching stem prefix
        for ext in image_extensions:
            # Pattern: filename_*.ext or filename-*.ext
            for candidate in parent_dir.glob(f"{stem}*{ext}"):
                if candidate != md_file:
                    assets.append(candidate)
        
        # Also check for a dedicated assets/images directory
        for subdir_name in ["assets", "images", "img"]:
            asset_dir = parent_dir / subdir_name
            if asset_dir.exists() and asset_dir.is_dir():
                for ext in image_extensions:
                    assets.extend(asset_dir.glob(f"*{ext}"))
        
        return assets
    
    @staticmethod
    def extract_archive(
        zip_path: Path,
        extract_dir: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Extract a ZIP archive to a directory.
        
        Args:
            zip_path: Path to the ZIP file
            extract_dir: Optional extraction directory
            
        Returns:
            Path to extraction directory, or None if failed
        """
        if not zip_path.exists() or not zip_path.is_file():
            logger.error(f"ZIP file not found: {zip_path}")
            return None
        
        if extract_dir is None:
            extract_dir = zip_path.parent / zip_path.stem
        
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)
            
            logger.info(f"ZIP extracted to: {extract_dir}")
            return extract_dir
            
        except (OSError, zipfile.BadZipFile) as e:
            logger.error(f"Failed to extract ZIP: {e}")
            return None
    
    @staticmethod
    def list_archive_contents(zip_path: Path) -> List[str]:
        """
        List contents of a ZIP archive without extracting.
        
        Args:
            zip_path: Path to the ZIP file
            
        Returns:
            List of filenames in the archive
        """
        if not zip_path.exists():
            return []
        
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                return zf.namelist()
        except zipfile.BadZipFile:
            return []
    
    @staticmethod
    def get_archive_size(zip_path: Path) -> float:
        """
        Get the size of a ZIP archive in MB.
        
        Args:
            zip_path: Path to the ZIP file
            
        Returns:
            Size in megabytes
        """
        if not zip_path.exists():
            return 0.0
        
        return round(zip_path.stat().st_size / (1024 * 1024), 2)


# Convenience functions for direct use
def create_zip_archive(
    files: List[Path],
    output_dir: Optional[Path] = None,
    archive_name: Optional[str] = None,
) -> Optional[Path]:
    """
    Create a ZIP archive from a list of files.
    
    Args:
        files: Files to include
        output_dir: Output directory
        archive_name: Custom archive name
        
    Returns:
        Path to created ZIP file
    """
    return ZipManager.create_archive(files, output_dir, archive_name)


def extract_zip_archive(
    zip_path: Path,
    extract_dir: Optional[Path] = None,
) -> Optional[Path]:
    """
    Extract a ZIP archive.
    
    Args:
        zip_path: ZIP file path
        extract_dir: Extraction directory
        
    Returns:
        Path to extraction directory
    """
    return ZipManager.extract_archive(zip_path, extract_dir)