import sys
import os
import shutil
import subprocess
import platform
from datetime import datetime
import ssl
import requests

from __version__ import __version__, __appname__, __author__, __internal_app_name__
from modules.platformModules import temp_dir, log_dir

try:
    from modules.platformModules import paddlex_dir
except:
    paddlex_dir = None

# How many sessions to retain on disk (1 STD + 1 DEBUG file each).
_LOG_SESSIONS_TO_KEEP = 5


# ---------------------------------------------------------------------------
# Timestamped stdout/stderr wrapper
# ---------------------------------------------------------------------------


class _TimestampedStream:
    """
    Wraps a writable file-like object and prepends [HH:MM:SS.mmm] to every
    new line, so print() calls in the log file are individually timestamped.

    Works correctly with Python's print() which may call write() once for
    the text and once for the newline separately.
    """

    def __init__(self, stream):
        self._stream = stream
        self._at_line_start = True

    def write(self, text: str) -> None:
        if not text:
            return

        segments = text.split("\n")
        out = []

        for i, seg in enumerate(segments):
            if i > 0:
                # A newline separates each segment.
                out.append("\n")
                self._at_line_start = True

            if seg:
                if self._at_line_start:
                    # %f gives microseconds — slice to milliseconds (12 chars).
                    ts = datetime.now().strftime("%H:%M:%S.%f")[:12]
                    out.append(f"[{ts}] {seg}")
                    self._at_line_start = False
                else:
                    out.append(seg)

        self._stream.write("".join(out))
        self._stream.flush()

    def flush(self) -> None:
        self._stream.flush()

    def fileno(self) -> int:
        # Required so os.dup2 and the logging module can resolve the fd.
        return self._stream.fileno()

    def __getattr__(self, name):
        return getattr(self._stream, name)


# ---------------------------------------------------------------------------
# Hardware info
# ---------------------------------------------------------------------------


def _get_hw_info() -> str:
    """
    Returns a formatted multi-line string with chip, RAM, storage, and OS.
    All lookups are wrapped in try/except so a single failure never crashes
    the log initialiser.
    """
    lines = []

    # --- Chip / CPU ---
    chip = ""
    try:
        # Works reliably on Intel Macs.
        chip = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            timeout=3,
        ).stdout.strip()
    except Exception:
        pass

    if not chip:
        # Apple Silicon: sysctl returns empty; use system_profiler instead.
        try:
            sp = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout
            for line in sp.splitlines():
                if "Chip:" in line or "Processor Name:" in line:
                    chip = line.split(":", 1)[-1].strip()
                    break
        except Exception:
            pass

    lines.append(f"  Chip    : {chip or 'Unknown'}")

    # --- RAM ---
    ram = "Unknown"
    try:
        mem_bytes = int(
            subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True,
                timeout=3,
            ).stdout.strip()
        )
        ram = f"{mem_bytes // (1024 ** 3)} GB"
    except Exception:
        pass
    lines.append(f"  RAM     : {ram}")

    # --- Storage (boot volume) ---
    storage = "Unknown"
    try:
        total, used, free = shutil.disk_usage("/")
        gb = 1024**3
        storage = f"{total // gb} GB total  |  " f"{used // gb} GB used  |  " f"{free // gb} GB free"
    except Exception:
        pass
    lines.append(f"  Storage : {storage}")

    # --- macOS version ---
    mac_ver = "Unknown"
    try:
        mac_ver = subprocess.run(
            ["sw_vers", "-productVersion"],
            capture_output=True,
            text=True,
            timeout=3,
        ).stdout.strip()
    except Exception:
        mac_ver = platform.mac_ver()[0] or "Unknown"
    lines.append(f"  OS      : macOS {mac_ver}  ({platform.machine()})")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Log pruning — keep the N most recent sessions
# ---------------------------------------------------------------------------


def _prune_logs(keep: int = _LOG_SESSIONS_TO_KEEP) -> None:
    """
    Removes the oldest session log pairs (STD + DEBUG) so that at most
    `keep - 1` complete sessions remain before the new one is written.

    STD logs are used as the session anchor because there is exactly one
    per run. The matching DEBUG log (same timestamp suffix) is removed at
    the same time.
    """
    if not os.path.exists(log_dir):
        return

    std_logs = sorted(
        [f for f in os.listdir(log_dir) if f.endswith(".log") and "-STD_" in f],
        key=lambda f: os.path.getmtime(os.path.join(log_dir, f)),
    )

    # Leave room for the new session that is about to be created.
    excess = std_logs[: max(0, len(std_logs) - (keep - 1))]

    for std_name in excess:
        for name in (std_name, std_name.replace("-STD_", "-DEBUG_")):
            path = os.path.join(log_dir, name)
            try:
                os.remove(path)
                print(f"[log pruner] Removed old log: {name}")
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Public initialiser — called once from mainGUI.py
# ---------------------------------------------------------------------------


def _init_log() -> None:
    """
    Sets up file logging for the current session.

    - Skipped entirely in spawned OCR worker processes (they manage their
      own fd redirection via the pipe in _ocr_worker_loop).
    - In frozen (.app) builds: prunes old logs, opens STD + DEBUG log files,
      redirects C-level fds 1/2, and wraps sys.stdout/stderr with
      _TimestampedStream so every print() carries HH:MM:SS.mmm.
    - In development: just prints session info to the terminal.
    """

    # The OCR worker is spawned with OCR_WORKER_PROCESS=1; it handles its
    # own stdout/stderr redirection via the pipe mechanism in OCRModules.py.
    if os.environ.get("OCR_WORKER_PROCESS") == "1":
        return

    log_path = None

    if getattr(sys, "frozen", False):
        _prune_logs(keep=_LOG_SESSIONS_TO_KEEP)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_path = os.path.join(
            log_dir,
            f"{__internal_app_name__}-{__version__}-STD_{timestamp}.log",
        )
        debug_log_path = os.path.join(
            log_dir,
            f"{__internal_app_name__}-{__version__}-DEBUG_{timestamp}.log",
        )

        log_file = open(log_path, "a", encoding="utf-8")

        # Redirect C-level fds so PaddleOCR's C++ output lands in the log.
        os.dup2(log_file.fileno(), 1)
        os.dup2(log_file.fileno(), 2)

        # Python-level wrapper adds per-line timestamps to all print() calls.
        stamped = _TimestampedStream(log_file)
        sys.stdout = stamped
        sys.stderr = stamped
        sys.__stdout__ = stamped
        sys.__stderr__ = stamped

        import logging

        logging.basicConfig(
            filename=debug_log_path,
            level=logging.DEBUG,
            force=True,
            # %(msecs)03d adds milliseconds to the logging timestamps.
            format="[APP] %(asctime)s.%(msecs)03d  %(levelname)-8s  %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Session header — readable in both the log file and the terminal.
    hw_info = _get_hw_info()
    sep = "=" * 48

    print(sep)
    print(f"  SESSION START : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  App           : {__appname__}  v{__version__}")
    print(f"  Author        : {__author__}")
    print("  --- Hardware ---")
    print(hw_info)
    print("  --- Paths ---")
    print(f"  Paddlex       : {paddlex_dir or '(dev mode — using default path)'}")
    print(f"  Temp          : {temp_dir}")
    print(f"  Logs          : {log_dir}")
    print(f"  Log file      : {log_path or '(dev mode — no file)'}")
    print("  --- Network ---")
    print("  SSL:", ssl.OPENSSL_VERSION)
    print("  HTTPS:", requests.get("https://example.com").status_code)
    print(sep)
