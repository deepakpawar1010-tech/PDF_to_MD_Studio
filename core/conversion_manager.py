"""
PDF_to_MD_Studio v1.0 - Conversion Manager
==========================================
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from core.constants import OUTPUT_EXTENSION
from core.config import get_config
from core.file_manager import FileManager
from core.gemini_engine import get_gemini_engine
from core.logger import get_logger
from core.marker_engine import get_marker_engine
from core.post_processor import run_cleanup
from core.session_manager import SessionManager
from core.zip_utils import create_zip_archive

logger = get_logger(__name__)


class ConversionManager:
    """Orchestrates the entire PDF to Markdown conversion workflow."""
    
    def __init__(self) -> None:
        self.marker_engine = get_marker_engine()
        self.gemini_engine = get_gemini_engine()
        self.file_manager = FileManager()
    
    def convert_single(
        self,
        input_path: Path,
        output_dir: Optional[Path] = None,
        progress_queue: Optional["queue.Queue"] = None,
        page_range: Optional[str] = None,
        engine_type: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Path]]:
        """
        Convert a single PDF. Supports both Gemini and Marker engines.

        Args:
            page_range: Optional page range value, e.g. "0-5,10,15-20".
            engine_type: "gemini" or "marker". If None, reads from config.
        """
        if output_dir is None:
            output_dir = get_config().get_output_dir()
        
        if isinstance(output_dir, Path) and output_dir.suffix:
            output_dir = output_dir.parent
        
        self.file_manager.ensure_dir(output_dir)
        
        temp_dir = self.file_manager.generate_unique_temp_dir()
        
        # Determine engine
        selected_engine = engine_type or get_config().get("engine", "gemini")
        if selected_engine == "gemini" and self.gemini_engine.is_available():
            active_engine = self.gemini_engine
            logger.info("Using Gemini engine for conversion")
        else:
            active_engine = self.marker_engine
            logger.info("Using Marker engine for conversion")
        
        try:
            extra_args = self._build_extra_args()
            if page_range:
                extra_args.extend(["--page_range", str(page_range)])
            
            if active_engine == self.gemini_engine:
                success, message, output_file = self.gemini_engine.convert_single(
                    input_path=input_path,
                    output_dir=temp_dir,
                    progress_queue=progress_queue,
                    page_range=page_range,
                )
            else:
                success, message, output_file = self.marker_engine.convert_single(
                    input_path=input_path,
                    output_dir=temp_dir,
                    extra_args=extra_args,
                    progress_queue=progress_queue,
                    page_range=page_range,
                )
            
            if not success or output_file is None:
                return False, message, None
            
            # Use the ACTUAL extension Marker produced (.md / .json / .html)
            # instead of assuming .md - required for JSON/HTML output formats.
            actual_ext = output_file.suffix
            final_output = output_dir / f"{input_path.stem}{actual_ext}"

            counter = 1
            while final_output.exists():
                final_output = output_dir / f"{input_path.stem}_{counter}{actual_ext}"
                counter += 1

            final_output = self.file_manager.move_file(output_file, final_output)
            self._copy_assets(temp_dir, final_output.parent, input_path.stem)
            
            message = self._maybe_auto_cleanup(final_output, message)
            
            self._record_conversion(input_path, final_output, success)
            
            return True, message, final_output
            
        finally:
            if get_config().get("auto_cleanup", True):
                self._safe_cleanup(temp_dir)
    
    def convert_batch(
        self,
        input_paths: List[Path],
        output_dir: Optional[Path] = None,
        progress_queue: Optional["queue.Queue"] = None,
        create_zip: bool = False,
    ) -> Tuple[bool, str, List[Path], Optional[Path]]:
        """Convert multiple PDFs."""
        if not input_paths:
            return False, "No files provided.", [], None
        
        if output_dir is None:
            output_dir = get_config().get_output_dir()
        
        if isinstance(output_dir, Path) and output_dir.suffix:
            output_dir = output_dir.parent
        
        self.file_manager.ensure_dir(output_dir)
        
        batch_temp = self.file_manager.generate_unique_temp_dir()
        batch_input = batch_temp / "input"
        batch_output = batch_temp / "output"
        
        try:
            batch_input.mkdir(parents=True, exist_ok=True)
            batch_output.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self._safe_cleanup(batch_temp)
            return False, f"Failed to create working directories: {e}", [], None
        
        output_files: List[Path] = []
        
        try:
            for file_path in input_paths:
                try:
                    shutil.copy2(str(file_path), str(batch_input / file_path.name))
                except Exception as e:
                    logger.warning(f"Failed to copy {file_path.name}: {e}")
            
            extra_args = self._build_extra_args()
            
            success, message, converted_files = self.engine.convert_batch(
                input_dir=batch_input,
                output_dir=batch_output,
                extra_args=extra_args,
                progress_queue=progress_queue,
            )
            
            if not converted_files:
                return False, message or "No files converted.", [], None
            
            for converted in converted_files:
                original_stem = converted.stem
                actual_ext = converted.suffix  # preserves .md / .json / .html
                final_path = output_dir / f"{original_stem}{actual_ext}"
                
                counter = 1
                final_dest = final_path
                while final_dest.exists():
                    final_dest = output_dir / f"{original_stem}_{counter}{actual_ext}"
                    counter += 1
                
                try:
                    moved = self.file_manager.move_file(converted, final_dest)
                    self._maybe_auto_cleanup(moved, "")
                    output_files.append(moved)
                except Exception as e:
                    logger.warning(f"Failed to move {converted.name}: {e}")
            
            self._copy_assets(batch_output, output_dir, None)
            
            zip_path: Optional[Path] = None
            if create_zip and output_files:
                try:
                    zip_path = create_zip_archive(
                        files=output_files,
                        output_dir=output_dir,
                        archive_name=None,
                    )
                except Exception as e:
                    logger.warning(f"Failed to create ZIP: {e}")
            
            SessionManager.set_batch_files([str(f) for f in output_files])
            if zip_path:
                SessionManager.set_zip_output_path(str(zip_path))
            
            success = len(output_files) > 0
            return success, message, output_files, zip_path
            
        finally:
            if get_config().get("auto_cleanup", True):
                self._safe_cleanup(batch_temp)
    
    def convert_uploaded(
        self,
        uploaded_file,
        output_dir: Optional[Path] = None,
        progress_queue: Optional["queue.Queue"] = None,
        page_range: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Path]]:
        """Convert an uploaded file."""
        temp_path = self.file_manager.save_uploaded_file(uploaded_file)
        
        try:
            return self.convert_single(
                input_path=temp_path,
                output_dir=output_dir,
                progress_queue=progress_queue,
                page_range=page_range,
            )
        finally:
            if get_config().get("auto_cleanup", True):
                self.file_manager.delete_file(temp_path)
    
    def _maybe_auto_cleanup(self, output_path: Path, message: str) -> str:
        """
        Automatically run the post-processor's cleanup fixes on a freshly
        converted Markdown file, right after conversion. Controlled by the
        "auto_post_process" config setting (default True). Only runs on
        actual Markdown output - JSON/HTML files are skipped since the
        cleanup fixes (misplaced numbers, stray bullets, math delimiters)
        are Markdown-specific.

        Appends a short summary of what was auto-fixed to the returned
        conversion message, so the person can see it happened without
        needing to separately open the Clean Up tab.
        """
        if not get_config().get("auto_post_process", True):
            return message

        if output_path.suffix.lower() != OUTPUT_EXTENSION.lower():
            return message

        try:
            with open(output_path, "r", encoding="utf-8") as f:
                original = f.read()
        except Exception as e:
            logger.warning(f"Auto-cleanup: couldn't read {output_path.name} for cleanup: {e}")
            return message

        try:
            cleaned, results = run_cleanup(original)
        except Exception as e:
            logger.warning(f"Auto-cleanup failed on {output_path.name}: {e}")
            return message

        total_fixes = sum(results.values())
        if total_fixes == 0:
            return message

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(cleaned)
        except Exception as e:
            logger.warning(f"Auto-cleanup: couldn't write cleaned content back to {output_path.name}: {e}")
            return message

        logger.info(f"Auto-cleanup applied to {output_path.name}: {results}")
        return f"{message} | Auto-cleaned: {total_fixes} fix(es) applied"

    def _build_extra_args(self) -> List[str]:
        """Build extra CLI arguments from user settings."""
        args: List[str] = []
        settings = get_config().get_all()
        
        if settings.get("ocr_enabled", False):
            args.append("--force_ocr")
        
        if not settings.get("preserve_images", True):
            args.append("--disable_image_extraction")
        
        output_format = settings.get("output_format", "markdown")
        if output_format:
            args.extend(["--output_format", str(output_format)])

        # CPU-side parallelism for initial PDF text/structure extraction -
        # doesn't touch GPU/VRAM, so it's free parallelism on top of whatever
        # the GPU stages are doing.
        pdftext_workers = settings.get("pdftext_workers", 4)
        if pdftext_workers:
            args.extend(["--pdftext_workers", str(pdftext_workers)])
        
        return args
    
    def _copy_assets(self, source_dir: Path, dest_dir: Path, stem_filter: Optional[str] = None) -> int:
        if not source_dir.exists() or not source_dir.is_dir():
            return 0
        
        if dest_dir.suffix:
            dest_dir = dest_dir.parent
        
        copied = 0
        asset_extensions = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
        
        for asset in source_dir.rglob("*"):
            if not asset.is_file():
                continue
            if asset.suffix.lower() not in asset_extensions:
                continue
            if stem_filter and stem_filter not in asset.name:
                continue
            
            try:
                dest = dest_dir / asset.name
                shutil.copy2(str(asset), str(dest))
                copied += 1
            except (OSError, shutil.Error):
                continue
        
        return copied
    
    def _record_conversion(self, input_path: Path, output_path: Path, success: bool) -> None:
        record = {
            "timestamp": datetime.now().isoformat(),
            "input_file": str(input_path),
            "output_file": str(output_path),
            "input_name": input_path.name,
            "output_name": output_path.name,
            "success": success,
        }
        SessionManager.add_conversion(record)
        SessionManager.set_output_path(str(output_path))
    
    def _safe_cleanup(self, path: Path) -> None:
        if not path or not path.exists():
            return
        
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
        except (OSError, shutil.Error) as e:
            logger.warning(f"Cleanup failed for {path}: {e}")


_conversion_manager: Optional["ConversionManager"] = None


def get_conversion_manager() -> "ConversionManager":
    global _conversion_manager
    if _conversion_manager is None:
        _conversion_manager = ConversionManager()
    return _conversion_manager