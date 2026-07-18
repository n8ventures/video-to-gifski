import sys
import os
import shutil
import subprocess
import platform
from datetime import datetime
import ssl
import requests

from __version__ import __version__, __appname__, __author__, __internal_app_name__
from modules.platformModules import temp_dir, log_dir, config_dir, win, mac

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
import ctypes
import json
import os
import platform
import shutil
import string
import subprocess

if win:
    import winreg


def _run_powershell_json(command: str, timeout: int = 6):
    """
    Runs a PowerShell command that ends in `| ConvertTo-Json` and returns
    the parsed result. Returns None on any failure (missing powershell,
    timeout, empty output, malformed JSON, etc.) so callers can treat this
    as just another optional lookup.

    ConvertTo-Json returns a single JSON object (not a list) when there's
    only one result, and a list when there's more than one — this
    normalizes both into a list so callers don't have to special-case it.
    """
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        output = result.stdout.strip()
        if not output:
            return None
        parsed = json.loads(output)
        if isinstance(parsed, dict):
            return [parsed]
        return parsed
    except Exception:
        return None


def _get_hw_info_windows() -> str:
    """
    Windows equivalent of _get_hw_info_mac(). Returns a formatted
    multi-line string with CPU (name + core/thread counts), GPU(s), RAM,
    storage (every drive, not just the boot volume), and OS version/build.
    All lookups are wrapped in try/except so a single failure never
    crashes the log initialiser.

    Uses PowerShell's Get-CimInstance for CPU/GPU details rather than
    `wmic` — wmic has been deprecated since Windows 10 21H1 and is
    outright missing on some newer Windows 11 builds, while
    Get-CimInstance has been the supported path since PowerShell 3.0 and
    ships on every currently-supported Windows version.
    """
    lines = []

    # --- CPU ---
    chip = ""
    cores = threads = None
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
        ) as key:
            chip, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            chip = chip.strip()
    except Exception:
        pass

    if not chip:
        chip = os.environ.get("PROCESSOR_IDENTIFIER", "")

    cpu_info = _run_powershell_json(
        "Get-CimInstance Win32_Processor | "
        "Select-Object NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed | "
        "ConvertTo-Json"
    )
    if cpu_info:
        cpu0 = cpu_info[0]
        cores = cpu0.get("NumberOfCores")
        threads = cpu0.get("NumberOfLogicalProcessors")
        clock = cpu0.get("MaxClockSpeed")  # MHz
    else:
        clock = None

    if cores and threads:
        core_thread_str = f" ({cores}C/{threads}T"
        core_thread_str += f" @ {clock / 1000:.2f} GHz)" if clock else ")"
    else:
        # Fallback: os.cpu_count() only gives logical (thread) count, no
        # physical core split, but it's always available with zero deps.
        core_thread_str = f" ({os.cpu_count()} logical CPUs)" if os.cpu_count() else ""

    lines.append(f"  Chip    : {chip or 'Unknown'}{core_thread_str}")

    # --- GPU ---
    gpu_info = _run_powershell_json(
        "Get-CimInstance Win32_VideoController | " "Select-Object Name,DriverVersion,AdapterRAM | " "ConvertTo-Json"
    )
    if gpu_info:
        gpu_lines = []
        for gpu in gpu_info:
            name = gpu.get("Name", "Unknown GPU")
            driver = gpu.get("DriverVersion", "")
            vram_bytes = gpu.get("AdapterRAM")
            # Win32_VideoController.AdapterRAM is a 32-bit field and
            # commonly reports wrong/capped values (e.g. 4GB cards showing
            # as ~4294967295 or wrapping to a small number) on newer
            # drivers — treat it as "nice if accurate" rather than ground
            # truth, and just omit it when it looks obviously wrong.
            vram_str = ""
            if isinstance(vram_bytes, int) and 0 < vram_bytes < 64 * (1024**3):
                vram_str = f", {vram_bytes // (1024 ** 3)} GB VRAM"
            driver_str = f", driver {driver}" if driver else ""
            gpu_lines.append(f"{name}{vram_str}{driver_str}")
        lines.append(f"  GPU     : {' | '.join(gpu_lines)}")
    else:
        lines.append("  GPU     : Unknown")

    # --- RAM ---
    ram = "Unknown"
    try:

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        mem_status = MEMORYSTATUSEX()
        mem_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status)):
            ram = f"{mem_status.ullTotalPhys // (1024 ** 3)} GB"
    except Exception:
        pass

    # Optional: RAM speed, if available — physical memory modules can
    # report inconsistent/missing Speed on some systems, so this is
    # best-effort and appended only when present.
    ram_speed_info = _run_powershell_json("Get-CimInstance Win32_PhysicalMemory | Select-Object Speed | ConvertTo-Json")
    if ram_speed_info:
        speeds = {m.get("Speed") for m in ram_speed_info if m.get("Speed")}
        if speeds:
            ram += f" @ {'/'.join(str(s) for s in sorted(speeds))} MHz"

    lines.append(f"  RAM     : {ram}")

    # --- Storage (every drive, not just the boot volume) ---
    # GetLogicalDrives() returns a bitmask where bit 0 = A:, bit 1 = B:,
    # etc. — the standard low-level way to enumerate drive letters without
    # pulling in pywin32 as a dependency.
    storage_lines = []
    try:
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        gb = 1024**3
        for i, letter in enumerate(string.ascii_uppercase):
            if not (bitmask >> i) & 1:
                continue
            drive = f"{letter}:\\"
            try:
                total, used, free = shutil.disk_usage(drive)
                if total == 0:
                    continue  # empty optical/card readers report 0 total — skip
                storage_lines.append(f"{drive} {total // gb} GB total | {used // gb} GB used | {free // gb} GB free")
            except Exception:
                continue  # unready drive (e.g. empty DVD drive) — skip silently
    except Exception:
        pass

    if storage_lines:
        lines.append("  Storage :")
        for line in storage_lines:
            lines.append(f"    {line}")
    else:
        lines.append("  Storage : Unknown")

    # --- Windows version ---
    win_ver = "Unknown"
    try:
        release, version, _, _ = platform.win32_ver()
        win_ver = f"{release} (build {version})" if release else "Unknown"
    except Exception:
        pass

    # Optional: edition (Home/Pro/Enterprise) — nice extra detail, not
    # critical, so failure here shouldn't blank out win_ver above.
    edition = ""
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
        ) as key:
            edition, _ = winreg.QueryValueEx(key, "ProductName")
    except Exception:
        pass

    os_str = edition.strip() if edition else f"Windows {win_ver}"
    if edition and win_ver != "Unknown":
        os_str += f"  ({win_ver})"

    lines.append(f"  OS      : {os_str}  ({platform.machine()})")

    return "\n".join(lines)


def _get_hw_info_mac() -> str:
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


def _get_hw_info() -> str:
    if win:
        return _get_hw_info_windows()
    elif mac:
        return _get_hw_info_mac()
    return "  Unknown platform"


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
    print(f"  Temp          : {temp_dir}")
    print(f"  Config        : {config_dir}")
    print(f"  Logs          : {log_dir}")
    print(f"  Log file      : {log_path or '(dev mode — no file)'}")
    print("  --- Network ---")
    print("  SSL:", ssl.OPENSSL_VERSION)
    print("  HTTPS:", requests.get("https://example.com").status_code)
    print(sep)
