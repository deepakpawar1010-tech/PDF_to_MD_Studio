"""
PDF_to_MD_Studio v1.0 - Marker Conversion Engine
=================================================
Handles all interactions with the marker_single.exe executable.
Real-time, STAGE-AWARE progress via queue (thread-safe for Streamlit).

CHANGES IN THIS VERSION:
- Explicit GPU/device selection (TORCH_DEVICE + batch size env vars).
- Real stage tracking mapped to Marker/Surya's actual CLI output:
    Loading Models -> Layout -> Detecting Text Regions -> Recognizing
    Text (OCR) -> Tables -> Equations -> Finalizing
- Fixed a bug where the old elapsed-timer thread pushed a flat progress
  value every second, overwriting real stage progress and making the bar
  look inaccurate/jumpy. The timer now only sends heartbeat status text
  (never touches the progress value) and only while no real stage data
  has arrived yet (e.g. during model download/load).
- Progress queue messages are now dicts (richer info), NOT plain floats.
  See CONVERSION_STAGES / _parse_progress_line for the exact contract.
"""

import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import requests

from core.constants import MARKER_EXECUTABLE, OUTPUT_EXTENSION
from core.config import get_config
from core.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# STAGE DEFINITIONS
# =============================================================================
# Ordered list of pipeline stages, mapped to Marker/Surya's real CLI output.
# Each stage has a (weight_start, weight_end) range on the 0.0-1.0 overall bar.
# Stages MUST stay in pipeline order - later stages imply earlier ones are done.

CONVERSION_STAGES: List[Dict] = [
    {
        "key": "startup",
        "label": "Loading Models",
        "icon": "📦",
        "match": ["loaded", "loading model", "downloading"],
        "weight": (0.00, 0.08),
    },
    {
        "key": "layout",
        "label": "Analyzing Layout",
        "icon": "🧩",
        "match": ["recognizing layout"],
        "weight": (0.08, 0.30),
    },
    {
        "key": "bbox",
        "label": "Detecting Text Regions",
        "icon": "🔍",
        "match": ["detecting bboxes"],
        "weight": (0.30, 0.40),
    },
    {
        "key": "text",
        "label": "Recognizing Text (OCR)",
        "icon": "📝",
        "match": ["recognizing text"],
        "weight": (0.40, 0.75),
    },
    {
        "key": "tables",
        "label": "Recognizing Tables",
        "icon": "📊",
        "match": ["recognizing table", "table recognition"],
        "weight": (0.75, 0.85),
    },
    {
        "key": "equations",
        "label": "Processing Equations",
        "icon": "🧮",
        "match": ["recognizing equations", "texify inference"],
        "weight": (0.85, 0.92),
    },
    {
        "key": "finalize",
        "label": "Assembling Document",
        "icon": "📚",
        "match": ["writing", "postprocess", "saving output"],
        "weight": (0.92, 1.00),
    },
]

_STAGE_INDEX = {s["key"]: i for i, s in enumerate(CONVERSION_STAGES)}

# Marker ships TWO separate CLI entry points:
#   marker_single  -> converts exactly ONE file
#   marker         -> converts a whole FOLDER of files (real batch mode)
# Derive the batch executable name from MARKER_EXECUTABLE so this keeps
# working whether constants.py has "marker_single.exe" or "marker_single".
if "marker_single" in MARKER_EXECUTABLE:
    BATCH_MARKER_EXECUTABLE = MARKER_EXECUTABLE.replace("marker_single", "marker")
else:
    BATCH_MARKER_EXECUTABLE = "marker.exe" if MARKER_EXECUTABLE.endswith(".exe") else "marker"


class MarkerEngine:
    """Engine for converting PDFs to Markdown using marker_single.exe."""

    def __init__(self) -> None:
        self.marker_path: Optional[str] = None
        self._available: bool = False
        self._cancelled: bool = False

        self.batch_marker_path: Optional[str] = None
        self._batch_available: bool = False

        # Stage-tracking state (reset per conversion call)
        self._stage_state: Dict[str, float] = {}
        self._current_stage_key: Optional[str] = None
        self._last_overall: float = 0.0
        self._state_lock = threading.Lock()

        self._validate_marker()
        self._validate_batch_marker()

    def _validate_marker(self) -> bool:
        """Resolve a usable marker executable without eagerly booting the CLI."""
        custom = get_config().get("custom_marker_path")
        if custom:
            p = Path(custom)
            if p.exists() and p.is_file():
                self.marker_path = str(p)
                self._available = True
                return True

        direct_path = shutil.which(MARKER_EXECUTABLE)
        if direct_path:
            self.marker_path = direct_path
            self._available = True
            return True

        which_path = shutil.which(MARKER_EXECUTABLE)
        if which_path:
            self.marker_path = which_path
            self._available = True
            return True

        for path_dir in os.environ.get("PATH", "").split(os.pathsep):
            if not path_dir.strip():
                continue
            candidate = Path(path_dir) / MARKER_EXECUTABLE
            if candidate.exists() and candidate.is_file():
                self.marker_path = str(candidate)
                self._available = True
                return True

        scripts_dir = Path(sys.executable).parent / "Scripts"
        candidate = scripts_dir / MARKER_EXECUTABLE
        if candidate.exists() and candidate.is_file():
            self.marker_path = str(candidate)
            self._available = True
            return True

        candidate = Path(sys.executable).parent / MARKER_EXECUTABLE
        if candidate.exists() and candidate.is_file():
            self.marker_path = str(candidate)
            self._available = True
            return True

        logger.warning(f"Marker executable '{MARKER_EXECUTABLE}' not found anywhere")
        self._available = False
        self.marker_path = MARKER_EXECUTABLE
        return False

    def is_available(self) -> bool:
        return self._available

    def _validate_batch_marker(self) -> bool:
        """
        Resolve the 'marker' (folder-batch) executable - a SEPARATE binary
        from marker_single. Mirrors _validate_marker()'s search strategy.
        """
        custom = get_config().get("custom_batch_marker_path")
        if custom:
            p = Path(custom)
            if p.exists() and p.is_file():
                self.batch_marker_path = str(p)
                self._batch_available = True
                return True

        which_path = shutil.which(BATCH_MARKER_EXECUTABLE)
        if which_path:
            self.batch_marker_path = which_path
            self._batch_available = True
            return True

        for path_dir in os.environ.get("PATH", "").split(os.pathsep):
            if not path_dir.strip():
                continue
            candidate = Path(path_dir) / BATCH_MARKER_EXECUTABLE
            if candidate.exists() and candidate.is_file():
                self.batch_marker_path = str(candidate)
                self._batch_available = True
                return True

        scripts_dir = Path(sys.executable).parent / "Scripts"
        candidate = scripts_dir / BATCH_MARKER_EXECUTABLE
        if candidate.exists() and candidate.is_file():
            self.batch_marker_path = str(candidate)
            self._batch_available = True
            return True

        candidate = Path(sys.executable).parent / BATCH_MARKER_EXECUTABLE
        if candidate.exists() and candidate.is_file():
            self.batch_marker_path = str(candidate)
            self._batch_available = True
            return True

        logger.warning(
            f"Batch marker executable '{BATCH_MARKER_EXECUTABLE}' not found. "
            f"Batch conversion needs the 'marker' CLI (separate from marker_single) "
            f"installed by the marker-pdf package."
        )
        self._batch_available = False
        self.batch_marker_path = BATCH_MARKER_EXECUTABLE
        return False

    def is_batch_available(self) -> bool:
        return self._batch_available

    def get_batch_status_message(self) -> str:
        if self._batch_available:
            return f"Batch marker ready: {self.batch_marker_path}"
        return (
            f"Batch executable '{BATCH_MARKER_EXECUTABLE}' not found. "
            f"This is a separate CLI command from marker_single - reinstall/repair "
            f"with 'pip install --force-reinstall marker-pdf' if missing, or set "
            f"a custom path in Settings."
        )

    def cancel(self) -> None:
        self._cancelled = True

    def get_status_message(self) -> str:
        if self._available:
            return f"Marker ready: {self.marker_path}"
        return f"Marker not found. Install: pip install marker-pdf"

    # ------------------------------------------------------------------
    # Device / environment handling
    # ------------------------------------------------------------------

    def _build_env(self, device_override: Optional[str] = None) -> dict:
        """
        Build the environment dict passed to the marker subprocess.
        Reads device + batch-size settings from config.json, with sane
        defaults. Makes GPU usage explicit instead of relying on silent
        auto-detection, and lets you tune batch sizes to avoid CUDA OOM
        on smaller GPUs.
        """
        cfg = get_config()

        device = device_override or cfg.get("device", "cuda")
        recognition_batch = str(cfg.get("recognition_batch_size", 8))
        detector_batch = str(cfg.get("detector_batch_size", 4))

        env = os.environ.copy()
        env["TORCH_DEVICE"] = device
        env["RECOGNITION_BATCH_SIZE"] = recognition_batch
        env["DETECTOR_BATCH_SIZE"] = detector_batch

        logger.info(
            f"Marker device config -> TORCH_DEVICE={device}, "
            f"RECOGNITION_BATCH_SIZE={recognition_batch}, "
            f"DETECTOR_BATCH_SIZE={detector_batch}"
        )
        return env

    def get_device_status(self) -> str:
        """Best-effort diagnostic: can torch in THIS env see a CUDA GPU."""
        try:
            import torch
            if torch.cuda.is_available():
                return f"CUDA available ({torch.cuda.get_device_name(0)})"
            return "CUDA not available - will run on CPU"
        except ImportError:
            return "torch not installed in this environment"
        except Exception as e:
            return f"Could not determine device status: {e}"

    @staticmethod
    def _extension_for_format(output_format: str) -> str:
        """Map Marker's --output_format value to the file extension it produces."""
        return {
            "markdown": ".md",
            "json": ".json",
            "html": ".html",
        }.get(output_format, ".md")

    # ------------------------------------------------------------------
    # Stage tracking
    # ------------------------------------------------------------------

    def _reset_stage_state(self) -> None:
        with self._state_lock:
            self._stage_state = {s["key"]: 0.0 for s in CONVERSION_STAGES}
            self._current_stage_key = None
            self._last_overall = 0.0

    def _compute_overall(self) -> float:
        total = 0.0
        for s in CONVERSION_STAGES:
            start, end = s["weight"]
            pct = self._stage_state.get(s["key"], 0.0) / 100.0
            total += (end - start) * pct
        return min(max(total, 0.0), 1.0)

    def _emit_stage_update(
        self,
        progress_queue: Optional["queue.Queue"],
        raw_line: str,
        elapsed: float,
    ) -> None:
        if progress_queue is None:
            return

        with self._state_lock:
            overall = self._compute_overall()
            overall = max(overall, self._last_overall)  # never go backwards
            self._last_overall = overall

            current_key = self._current_stage_key
            current_pct = self._stage_state.get(current_key, 0.0) if current_key else 0.0
            current_meta = CONVERSION_STAGES[_STAGE_INDEX[current_key]] if current_key else None

            payload = {
                "overall": overall,
                "current_stage": current_key,
                "current_stage_label": current_meta["label"] if current_meta else "Starting...",
                "current_stage_icon": current_meta["icon"] if current_meta else "⏳",
                "stage_percent": current_pct,
                "stages": dict(self._stage_state),
                "raw_line": raw_line[:150],
                "elapsed": elapsed,
            }

        try:
            progress_queue.put(("stage", payload), block=False)
        except Exception:
            pass

    def _mark_all_complete(self, progress_queue: Optional["queue.Queue"], elapsed: float) -> None:
        with self._state_lock:
            self._stage_state = {s["key"]: 100.0 for s in CONVERSION_STAGES}
            self._current_stage_key = CONVERSION_STAGES[-1]["key"]
            self._last_overall = 1.0
        self._emit_stage_update(progress_queue, "Conversion complete", elapsed)

    def _stream_output(
        self,
        process: subprocess.Popen,
        progress_queue: Optional["queue.Queue"],
        start_time: float,
    ) -> Tuple[str, str, bool]:
        """
        Stream output from marker process.
        Puts progress updates into queue (NEVER calls Streamlit directly).
        """
        stdout_lines: List[str] = []
        stderr_lines: List[str] = []
        stop_event = threading.Event()

        # Heartbeat thread: only nudges status text while NO real stage
        # data has arrived yet (e.g. still downloading/loading models).
        # It never touches the progress bar value, so it can't overwrite
        # real stage progress.
        heartbeat_thread = self._start_heartbeat(progress_queue, start_time, stop_event)

        def read_stream(stream, lines_list):
            try:
                for line in iter(stream.readline, ''):
                    if not line or self._cancelled:
                        break
                    line = line.rstrip('\n').rstrip('\r')
                    lines_list.append(line)
                    elapsed = time.time() - start_time
                    self._parse_progress_line(line, progress_queue, elapsed)
            except Exception:
                pass

        t1 = threading.Thread(target=read_stream, args=(process.stdout, stdout_lines))
        t2 = threading.Thread(target=read_stream, args=(process.stderr, stderr_lines))
        t1.start()
        t2.start()

        process.wait()

        stop_event.set()
        heartbeat_thread.join(timeout=2)
        t1.join(timeout=5)
        t2.join(timeout=5)

        return "\n".join(stdout_lines), "\n".join(stderr_lines), self._cancelled

    def _start_heartbeat(
        self,
        progress_queue: Optional["queue.Queue"],
        start_time: float,
        stop_event: threading.Event,
    ) -> threading.Thread:
        """
        Background thread that keeps the UI feeling alive during long gaps
        with no CLI output (e.g. first-run model downloads). Sends a
        "heartbeat" message type (status text only) - NEVER a "stage"
        message - so it can never overwrite real progress values.
        """
        def heartbeat_loop():
            while not stop_event.is_set():
                with self._state_lock:
                    has_stage = self._current_stage_key is not None
                if not has_stage and progress_queue is not None:
                    elapsed = time.time() - start_time
                    mins = int(elapsed // 60)
                    secs = int(elapsed % 60)
                    if mins < 1:
                        msg = f"Starting up... ({secs}s)"
                    else:
                        msg = f"Still starting up - first run may download models ({mins}m {secs}s)"
                    try:
                        progress_queue.put(("heartbeat", msg), block=False)
                    except Exception:
                        pass
                stop_event.wait(timeout=1.0)

        t = threading.Thread(target=heartbeat_loop, daemon=True)
        t.start()
        return t

    def _parse_progress_line(
        self,
        line: str,
        progress_queue: Optional["queue.Queue"],
        elapsed: float,
    ) -> None:
        """Parse a single line of Marker/Surya output and update stage state."""
        lower = line.lower()

        matched_idx: Optional[int] = None
        for i, stage in enumerate(CONVERSION_STAGES):
            if any(kw in lower for kw in stage["match"]):
                matched_idx = i
                break

        percent_match = re.search(r"(\d+)%", line)

        with self._state_lock:
            if matched_idx is not None:
                stage = CONVERSION_STAGES[matched_idx]
                key = stage["key"]

                for prior in CONVERSION_STAGES[:matched_idx]:
                    self._stage_state[prior["key"]] = max(self._stage_state.get(prior["key"], 0.0), 100.0)

                if percent_match:
                    pct = min(float(percent_match.group(1)), 100.0)
                    self._stage_state[key] = max(self._stage_state.get(key, 0.0), pct)
                else:
                    self._stage_state[key] = min(self._stage_state.get(key, 0.0) + 20.0, 95.0)

                self._current_stage_key = key
            else:
                if any(kw in lower for kw in ["processing", "converting", "analyzing", "extracting"]):
                    if self._current_stage_key is None:
                        self._stage_state["startup"] = min(self._stage_state.get("startup", 0.0) + 5.0, 95.0)
                else:
                    return

        self._emit_stage_update(progress_queue, line, elapsed)

    # ------------------------------------------------------------------
    # Conversion
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Persistent server mode (marker_server) - avoids reloading models
    # on every conversion. Opt-in, falls back to subprocess if unavailable.
    # ------------------------------------------------------------------

    def get_server_url(self) -> str:
        return get_config().get("server_url", "http://localhost:8001")

    def is_server_mode_enabled(self) -> bool:
        return bool(get_config().get("use_server_mode", False))

    def check_server_available(self) -> bool:
        """Quick check whether marker_server is up and responding."""
        try:
            resp = requests.get(self.get_server_url(), timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    def get_server_status(self) -> str:
        if not self.is_server_mode_enabled():
            return "Server mode disabled (using subprocess)"
        if self.check_server_available():
            return f"✅ Connected to marker_server at {self.get_server_url()}"
        return (
            f"❌ Can't reach marker_server at {self.get_server_url()}. "
            f"Start it with: marker_server --port 8001"
        )

    def _convert_single_via_server(
        self,
        input_path: Path,
        output_dir: Path,
        page_range: Optional[str] = None,
        progress_queue: Optional["queue.Queue"] = None,
    ) -> Tuple[bool, str, Optional[Path]]:
        """
        Convert via the persistent marker_server instead of a fresh subprocess.
        Models stay loaded in the server process, avoiding per-run reload cost.

        NOTE: marker_server is a single blocking request/response - there's no
        official progress callback, so we show a heartbeat (elapsed time) via
        the queue instead of real stage percentages.
        """
        cfg = get_config()
        output_format = cfg.get("output_format", "markdown")
        start_time = time.time()
        stop_event = threading.Event()

        def heartbeat_loop():
            while not stop_event.is_set():
                elapsed = time.time() - start_time
                mins, secs = int(elapsed // 60), int(elapsed % 60)
                msg = f"Converting via server... ({mins}m {secs}s)" if mins else f"Converting via server... ({secs}s)"
                if progress_queue is not None:
                    try:
                        progress_queue.put(("heartbeat", msg), block=False)
                    except Exception:
                        pass
                stop_event.wait(timeout=1.0)

        hb_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        hb_thread.start()

        try:
            payload = {
                "filepath": str(input_path),
                "output_format": output_format,
            }
            if page_range:
                payload["page_range"] = page_range
            if cfg.get("ocr_enabled", False):
                payload["force_ocr"] = True

            resp = requests.post(
                f"{self.get_server_url()}/marker",
                data=__import__("json").dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=None,
            )
            stop_event.set()
            hb_thread.join(timeout=2)

            if resp.status_code != 200:
                return False, f"Server returned HTTP {resp.status_code}: {resp.text[:200]}", None

            data = resp.json()

            # Check for an explicit server-side failure first - this is
            # different from "response shape we didn't expect".
            if data.get("success") is False:
                error_detail = data.get("error", "No error detail provided by server.")
                stop_event.set()
                return False, f"marker_server reported an error: {error_detail}", None

            # Defensive parsing - response key names aren't 100% guaranteed
            # documented, so try the likely candidates for the requested format.
            content = None
            for key in ("markdown", "html", "output", "text"):
                if key in data and data[key]:
                    content = data[key]
                    break
            if content is None and output_format == "json" and "children" in data:
                content = __import__("json").dumps(data, indent=2)

            if content is None:
                logger.warning(f"Unexpected marker_server response shape: {list(data.keys())}")
                return False, (
                    f"Converted via server but couldn't find output content in the response. "
                    f"Response keys were: {list(data.keys())}. Please report this so the parsing can be fixed."
                ), None

            ext = self._extension_for_format(output_format)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{input_path.stem}{ext}"
            output_file.write_text(content, encoding="utf-8")

            # Save any base64 images if present and image extraction is enabled
            if cfg.get("preserve_images", True) and isinstance(data.get("images"), dict):
                import base64
                for img_name, img_data in data["images"].items():
                    try:
                        if "," in img_data:
                            img_data = img_data.split(",", 1)[1]  # strip data: URI prefix
                        img_bytes = base64.b64decode(img_data)
                        safe_name = Path(img_name).name or f"{img_name}.png"
                        (output_dir / safe_name).write_bytes(img_bytes)
                    except Exception as e:
                        logger.warning(f"Failed to save image {img_name}: {e}")

            self._mark_all_complete(progress_queue, time.time() - start_time)

            elapsed = time.time() - start_time
            mins, secs = int(elapsed // 60), int(elapsed % 60)
            return True, f"Done in {mins}m {secs}s (server mode) | {output_file.name}", output_file

        except requests.exceptions.ConnectionError:
            stop_event.set()
            return False, (
                f"Couldn't connect to marker_server at {self.get_server_url()}. "
                f"Make sure it's running: marker_server --port 8001"
            ), None
        except Exception as e:
            stop_event.set()
            return False, f"Server conversion error: {e}", None
        finally:
            stop_event.set()

    def convert_single(
        self,
        input_path: Path,
        output_dir: Path,
        extra_args: Optional[List[str]] = None,
        progress_queue: Optional["queue.Queue"] = None,
        device: Optional[str] = None,
        page_range: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Path]]:
        """Convert a single PDF. NO TIMEOUT."""
        self._cancelled = False
        self._reset_stage_state()

        # Server mode: use the persistent marker_server instead of a fresh
        # subprocess, IF it's enabled AND actually reachable. Falls back to
        # subprocess automatically if the server isn't running.
        if self.is_server_mode_enabled():
            if self.check_server_available():
                return self._convert_single_via_server(
                    input_path=input_path,
                    output_dir=output_dir,
                    page_range=page_range,
                    progress_queue=progress_queue,
                )
            else:
                logger.warning(
                    "Server mode enabled but marker_server unreachable - "
                    "falling back to subprocess for this conversion."
                )

        if not self.is_available():
            return False, self.get_status_message(), None

        if not input_path.exists():
            return False, f"Input file not found: {input_path}", None

        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [self.marker_path, str(input_path), "--output_dir", str(output_dir)]
        if extra_args:
            cmd.extend(extra_args)

        env = self._build_env(device_override=device)

        logger.info(f"Starting conversion: {input_path.name} (device={env.get('TORCH_DEVICE')})")
        logger.debug(f"Command: {' '.join(cmd)}")

        start_time = time.time()

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env,
            )

            stdout, stderr, was_cancelled = self._stream_output(process, progress_queue, start_time)

            elapsed = time.time() - start_time
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            elapsed_str = f"{mins}m {secs}s"

            if was_cancelled:
                try:
                    if sys.platform == "win32":
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)
                    else:
                        process.kill()
                except Exception:
                    pass
                return False, "Conversion cancelled.", None

            if process.returncode != 0:
                error_msg = self._parse_error(stderr, stdout)
                if env.get("TORCH_DEVICE") == "cuda" and re.search(
                    r"CUDA|out of memory|MemoryError", error_msg, re.IGNORECASE
                ):
                    error_msg += (
                        "\n\nHint: This looks like a GPU memory error. Try lowering "
                        "'recognition_batch_size' / 'detector_batch_size' in Settings, "
                        "or switch device to 'cpu' for this file."
                    )
                return False, f"Failed after {elapsed_str}\n\nError: {error_msg}", None

            self._mark_all_complete(progress_queue, elapsed)

            output_file = self._find_output_file(output_dir, input_path.stem)

            if output_file and output_file.exists():
                return True, f"Done in {elapsed_str} | {output_file.name}", output_file

            files_in_output = sorted(
                [f for f in output_dir.rglob("*") if f.is_file()],
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )
            if files_in_output:
                fallback = files_in_output[0]
                return True, f"Done in {elapsed_str} | {fallback.name}", fallback

            return False, f"No output after {elapsed_str}", None

        except Exception as e:
            elapsed = time.time() - start_time
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            return False, f"Error after {mins}m {secs}s: {str(e)}", None

    def convert_batch(
        self,
        input_dir: Path,
        output_dir: Path,
        extra_args: Optional[List[str]] = None,
        progress_queue: Optional["queue.Queue"] = None,
        device: Optional[str] = None,
    ) -> Tuple[bool, str, List[Path]]:
        """
        Convert a whole folder of PDFs. NO TIMEOUT.

        IMPORTANT: this uses the 'marker' CLI (folder-batch mode), which is a
        DIFFERENT executable from marker_single. They're both installed by
        the marker-pdf package but marker_single only accepts a single file.
        """
        self._cancelled = False
        self._reset_stage_state()

        if not self.is_batch_available():
            return False, self.get_batch_status_message(), []

        if not input_dir.exists() or not input_dir.is_dir():
            return False, f"Input directory not found: {input_dir}", []

        output_dir.mkdir(parents=True, exist_ok=True)

        # Conservative worker count by default - each worker holds its own
        # copy of models in VRAM, so more workers = more GPU memory used.
        # On small-VRAM cards (e.g. 4GB), keep this low to avoid CUDA OOM.
        workers = str(get_config().get("batch_workers", 1))

        cmd = [
            self.batch_marker_path,
            str(input_dir),
            "--output_dir", str(output_dir),
            "--workers", workers,
        ]
        if extra_args:
            cmd.extend(extra_args)

        env = self._build_env(device_override=device)

        logger.info(
            f"Starting batch: {input_dir} (device={env.get('TORCH_DEVICE')}, workers={workers})"
        )
        logger.debug(f"Command: {' '.join(cmd)}")

        start_time = time.time()

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env,
            )

            stdout, stderr, was_cancelled = self._stream_output(process, progress_queue, start_time)

            elapsed = time.time() - start_time
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)

            if was_cancelled:
                process.kill()
                return False, "Batch cancelled.", []

            output_files = list(output_dir.rglob(f"*{self._extension_for_format(get_config().get('output_format', 'markdown'))}"))

            if process.returncode == 0 and output_files:
                self._mark_all_complete(progress_queue, elapsed)
                return True, f"Batch done in {mins}m {secs}s | {len(output_files)} files", output_files

            error_msg = self._parse_error(stderr, stdout)
            if env.get("TORCH_DEVICE") == "cuda" and re.search(
                r"CUDA|out of memory|MemoryError", error_msg, re.IGNORECASE
            ):
                error_msg += (
                    "\n\nHint: This looks like a GPU memory error. Try lowering "
                    "'recognition_batch_size' / 'detector_batch_size' in Settings, "
                    "or switch device to 'cpu' for this batch."
                )
            return False, f"Batch failed after {mins}m {secs}s: {error_msg}", output_files

        except Exception as e:
            elapsed = time.time() - start_time
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            return False, f"Batch error after {mins}m {secs}s: {str(e)}", []

    def _find_output_file(self, output_dir: Path, input_stem: str) -> Optional[Path]:
        expected_ext = self._extension_for_format(get_config().get("output_format", "markdown"))

        nested_match = output_dir / input_stem / f"{input_stem}{expected_ext}"
        if nested_match.exists():
            return nested_match

        direct_match = output_dir / f"{input_stem}{expected_ext}"
        if direct_match.exists():
            return direct_match

        matches = list(output_dir.rglob(f"*{expected_ext}"))
        if matches:
            return max(matches, key=lambda p: p.stat().st_mtime)

        # Last-resort fallback: also try the default .md, in case output_format
        # config and the actual marker run were somehow out of sync
        if expected_ext != OUTPUT_EXTENSION:
            fallback_matches = list(output_dir.rglob(f"*{OUTPUT_EXTENSION}"))
            if fallback_matches:
                return max(fallback_matches, key=lambda p: p.stat().st_mtime)

        return None

    def _parse_error(self, stderr: str, stdout: str) -> str:
        combined = f"{stderr}\n{stdout}".strip()
        if not combined:
            return "No output from marker."

        patterns = [
            r"Error:\s*(.+)",
            r"Exception:\s*(.+)",
            r"Failed to\s*(.+)",
            r"Permission denied",
            r"File not found",
            r"ModuleNotFoundError",
            r"CUDA.*error",
            r"torch.*error",
            r"out of memory",
            r"MemoryError",
            r"download.*failed",
            r"connection.*error",
            r"No such option",
        ]

        for pattern in patterns:
            match = re.search(pattern, combined, re.IGNORECASE)
            if match:
                return match.group(0)[:200]

        lines = [l.strip() for l in combined.split("\n") if l.strip()]
        if lines:
            return lines[-1][:300]

        return "Unknown error"

    def get_version(self) -> str:
        if not self.is_available():
            return "Not available"
        try:
            result = subprocess.run(
                [self.marker_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except Exception as e:
            return f"Error: {e}"

    def get_help(self) -> str:
        if not self.is_available():
            return "Not available"
        try:
            result = subprocess.run(
                [self.marker_path, "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"Error: {e}"


_marker_engine: Optional[MarkerEngine] = None


def get_marker_engine() -> MarkerEngine:
    global _marker_engine
    if _marker_engine is None:
        _marker_engine = MarkerEngine()
    return _marker_engine

def reset_marker_engine() -> None:
    global _marker_engine
    _marker_engine = None