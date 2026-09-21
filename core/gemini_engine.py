"""
PDF_to_MD_Studio v1.0 - Gemini Multimodal Vision Conversion Engine
===================================================================
High-speed, high-accuracy PDF to Markdown conversion using Google's
Gemini 2.5 Flash / 1.5 Flash multimodal vision API.
Converts dense math formulas into LaTeX $...$ with 100% accuracy in seconds.
"""

import io
import os
import re
import time
from pathlib import Path
from typing import List, Optional, Tuple

import fitz  # PyMuPDF
from google import genai
from google.genai import types

from core.config import get_config
from core.logger import get_logger

logger = get_logger(__name__)

GEMINI_CONVERSION_PROMPT = """You are an expert OCR and LaTeX conversion engine for educational and mathematical documents.
Convert this document page into clean, perfectly formatted Markdown.

Strict Formatting Rules:
1. Mathematical Formulas & Expressions:
   - ALL mathematical formulas, variables, expressions, fractions, powers, roots, and equations MUST be written in valid LaTeX code wrapped inside $ for inline math (e.g. $x^2 + y^2 = r^2$, ${}^nC_r$, $\\frac{n!}{(n-r)!}$, $\\ge 1$) or $$ for display/block equations.
   - Accurately preserve all subscripts and superscripts (e.g. ${}^nC_r$, ${}^nP_r$, $x_1$, $x^{-4}$, $T_{r+1}$).
   - Fractions must use \\frac{numerator}{denominator}.
2. Document Structure:
   - Accurately preserve headings, subheadings, question numbers (e.g. 1., 2.), and multiple-choice options (e.g. 1), 2), 3), 4) or A), B), C), D)).
   - Do NOT omit question numbers or move them to the end of sentences.
   - Format multiple-choice options clearly on separate lines or cleanly grouped.
   - Tables must be formatted as standard Markdown tables.
3. Clean Characters & Output:
   - Output ONLY the markdown text. Do NOT wrap the response in ```markdown or ``` fences.
   - Never output unicode replacement characters (U+FFFD ). For single variables or mathematical terms, wrap them in math delimiters (e.g. '$n$', '$x$').
"""


class GeminiEngine:
    """Engine for converting PDFs to Markdown using Gemini Multimodal Vision."""

    def __init__(self) -> None:
        self._cancelled = False

    def get_api_key(self) -> Optional[str]:
        """Retrieve API key from config or environment variable."""
        cfg = get_config()
        key = cfg.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
        if key and key.strip():
            return key.strip()
        return None

    def is_available(self) -> bool:
        """Check if Gemini engine is configured with an API key."""
        return bool(self.get_api_key())

    def get_status_message(self) -> str:
        if self.is_available():
            cfg = get_config()
            model = cfg.get("gemini_model", "gemini-3.6-flash")
            return f"Gemini Engine Ready ({model})"
        return "Gemini API Key missing. Please set your key in Settings or enter it above."

    def cancel(self) -> None:
        self._cancelled = True

    def _parse_page_range(self, page_range: Optional[str], total_pages: int) -> List[int]:
        """Parse page range string (e.g. '0-3,5,8-10') into a list of 0-based page indices."""
        if not page_range or not page_range.strip():
            return list(range(total_pages))

        pages = set()
        parts = page_range.strip().split(",")
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                try:
                    start_s, end_s = part.split("-", 1)
                    start = int(start_s.strip())
                    end = int(end_s.strip())
                    for p in range(start, end + 1):
                        if 0 <= p < total_pages:
                            pages.add(p)
                except ValueError:
                    pass
            else:
                try:
                    p = int(part)
                    if 0 <= p < total_pages:
                        pages.add(p)
                except ValueError:
                    pass

        result = sorted(list(pages))
        return result if result else list(range(total_pages))

    def _call_with_retry(
        self,
        client: genai.Client,
        model_name: str,
        img_bytes: bytes,
        page_num: int,
        progress_queue: Optional["queue.Queue"] = None,
        max_retries: int = 5,
    ) -> str:
        """
        Call Gemini API with automatic exponential backoff and fallback models
        to handle transient 503 (high demand) and 429 (quota / rate limit) errors.
        """
        fallback_models = [
            model_name,
            "gemini-3.5-flash-lite",
            "gemini-flash-lite-latest",
            "gemini-3.1-flash-lite",
            "gemini-3.5-flash",
            "gemini-3.8-flash",
        ]
        candidate_models = []
        for m in fallback_models:
            if m not in candidate_models:
                candidate_models.append(m)

        last_error = None
        for attempt in range(1, max_retries + 1):
            if self._cancelled:
                raise RuntimeError("Conversion cancelled.")

            current_model = candidate_models[min(attempt - 1, len(candidate_models) - 1)]

            try:
                response = client.models.generate_content(
                    model=current_model,
                    contents=[
                        types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                        GEMINI_CONVERSION_PROMPT,
                    ],
                )
                return response.text or ""

            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                is_quota = "quota" in err_str or "429" in err_str or "resource_exhausted" in err_str
                is_transient = is_quota or any(kw in err_str for kw in ["503", "unavailable", "demand", "timeout", "overloaded"])

                if not is_transient or attempt == max_retries:
                    raise last_error

                # If quota exceeded on this model, switch immediately to next candidate model
                if is_quota and attempt < len(candidate_models):
                    next_model = candidate_models[attempt]
                    msg = f"Quota limit reached for {current_model}. Switching to {next_model}..."
                    logger.warning(f"Page {page_num + 1}: {msg}")
                    if progress_queue is not None:
                        try:
                            progress_queue.put(("heartbeat", msg), block=False)
                        except Exception:
                            pass
                    time.sleep(1.0)
                    continue

                # For 503/server demand: exponential backoff (2s, 4s, 8s...)
                wait_time = min(2 ** attempt + 1.0, 15.0)
                msg = f"Gemini busy (503). Retrying page {page_num + 1} in {int(wait_time)}s (attempt {attempt}/{max_retries})..."
                logger.warning(f"Page {page_num + 1}: {msg} ({e})")

                if progress_queue is not None:
                    try:
                        progress_queue.put(("heartbeat", msg), block=False)
                    except Exception:
                        pass

                time.sleep(wait_time)

        raise last_error if last_error else RuntimeError(f"Failed to convert page {page_num + 1}")

    def convert_single(
        self,
        input_path: Path,
        output_dir: Path,
        progress_queue: Optional["queue.Queue"] = None,
        page_range: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Path]]:
        """
        Convert a single PDF using Gemini Multimodal Vision API.
        Renders each page and converts to Markdown with LaTeX math.
        """
        self._cancelled = False
        api_key = self.get_api_key()

        if not api_key:
            return False, "Gemini API key is required. Please add it in Settings.", None

        if not input_path.exists():
            return False, f"Input file not found: {input_path}", None

        cfg = get_config()
        model_name = cfg.get("gemini_model", "gemini-3.6-flash")

        try:
            client = genai.Client(api_key=api_key)
        except Exception as e:
            return False, f"Failed to initialize Gemini client: {e}", None

        start_time = time.time()
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            doc = fitz.open(str(input_path))
            total_doc_pages = len(doc)
            pages_to_process = self._parse_page_range(page_range, total_doc_pages)
            num_pages = len(pages_to_process)

            if num_pages == 0:
                doc.close()
                return False, "No valid pages to process in the specified page range.", None

            page_markdowns: List[str] = []

            for idx, page_num in enumerate(pages_to_process):
                if self._cancelled:
                    doc.close()
                    return False, "Conversion cancelled.", None

                # Emit progress update
                if progress_queue is not None:
                    overall = idx / num_pages
                    elapsed = time.time() - start_time
                    payload = {
                        "overall": overall,
                        "current_stage": "text",
                        "current_stage_label": f"Converting Page {page_num + 1} of {total_doc_pages}",
                        "current_stage_icon": "⚡",
                        "stage_percent": (idx / num_pages) * 100.0,
                        "stages": {"text": (idx / num_pages) * 100.0},
                        "raw_line": f"Gemini processing page {page_num + 1}...",
                        "elapsed": elapsed,
                    }
                    try:
                        progress_queue.put(("stage", payload), block=False)
                    except Exception:
                        pass

                # Render page to high-res PNG image (150 DPI for crisp formula recognition)
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")

                # Call Gemini API with automatic retry and backoff for 503/429
                try:
                    text = self._call_with_retry(
                        client=client,
                        model_name=model_name,
                        img_bytes=img_bytes,
                        page_num=page_num,
                        progress_queue=progress_queue,
                        max_retries=5,
                    )
                    # Strip any accidental ```markdown ... ``` wrapper
                    clean_text = text.strip()
                    if clean_text.startswith("```markdown"):
                        clean_text = clean_text[len("```markdown"):].strip()
                    elif clean_text.startswith("```"):
                        clean_text = clean_text[3:].strip()
                    if clean_text.endswith("```"):
                        clean_text = clean_text[:-3].strip()

                    page_markdowns.append(clean_text)

                    # Small courtesy delay between pages to avoid burst rate limits
                    time.sleep(0.5)

                except Exception as api_err:
                    logger.error(f"Gemini API error on page {page_num + 1}: {api_err}")
                    doc.close()
                    return False, f"Gemini API error on page {page_num + 1}: {api_err}", None

            doc.close()

            # Combine page markdowns with clear page separation
            combined_md = "\n\n---\n\n".join(page_markdowns)

            output_file = output_dir / f"{input_path.stem}.md"
            output_file.write_text(combined_md, encoding="utf-8")

            elapsed = time.time() - start_time
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            elapsed_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

            # Emit 100% completion
            if progress_queue is not None:
                payload = {
                    "overall": 1.0,
                    "current_stage": "finalize",
                    "current_stage_label": "Conversion Complete",
                    "current_stage_icon": "✅",
                    "stage_percent": 100.0,
                    "stages": {"finalize": 100.0},
                    "raw_line": f"Completed in {elapsed_str}",
                    "elapsed": elapsed,
                }
                try:
                    progress_queue.put(("stage", payload), block=False)
                except Exception:
                    pass

            return True, f"Done in {elapsed_str} (Gemini Flash) | {output_file.name}", output_file

        except Exception as e:
            elapsed = time.time() - start_time
            return False, f"Gemini conversion error: {str(e)}", None


_gemini_engine_instance: Optional[GeminiEngine] = None


def get_gemini_engine() -> GeminiEngine:
    global _gemini_engine_instance
    if _gemini_engine_instance is None:
        _gemini_engine_instance = GeminiEngine()
    return _gemini_engine_instance
