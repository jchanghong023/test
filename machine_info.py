"""Print machine information using only the Python standard library.

Windows and Linux/WSL are supported; macOS collection is best-effort.
All collectors retain their fields with "Unknown" values when unavailable.
"""

import ctypes
import os
import platform
import shutil
import subprocess
import sys


UNKNOWN = "Unknown"


def _command_output(*args):
    """Read a system command without displaying its diagnostics."""
    return subprocess.run(
        args,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        errors="replace",
        timeout=5,
    ).stdout.strip()


def collect_cpu() -> dict:
    """Return the CPU model and logical core count."""
    result = {"model": UNKNOWN, "cores": UNKNOWN}
    try:
        result["cores"] = os.cpu_count() or UNKNOWN
    except Exception:
        pass
    try:
        system = platform.system()
        model = ""
        if system == "Windows":
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
            ) as key:
                model = winreg.QueryValueEx(key, "ProcessorNameString")[0]
        elif system == "Linux":
            with open("/proc/cpuinfo", encoding="utf-8", errors="replace") as cpuinfo:
                for line in cpuinfo:
                    key, separator, value = line.partition(":")
                    if separator and key.strip() in ("model name", "Hardware"):
                        model = value.strip()
                        break
        elif system == "Darwin":
            model = _command_output("/usr/sbin/sysctl", "-n", "machdep.cpu.brand_string")
        result["model"] = model.strip() or platform.processor().strip() or UNKNOWN
    except Exception:
        pass
    return result


def collect_memory() -> dict:
    """Return total and available physical memory in bytes."""
    result = {"total": UNKNOWN, "available": UNKNOWN}
    try:
        system = platform.system()
        if system == "Windows":
            class MemoryStatus(ctypes.Structure):
                _fields_ = [
                    ("length", ctypes.c_uint32),
                    ("memory_load", ctypes.c_uint32),
                    ("total_physical", ctypes.c_uint64),
                    ("available_physical", ctypes.c_uint64),
                    ("total_page_file", ctypes.c_uint64),
                    ("available_page_file", ctypes.c_uint64),
                    ("total_virtual", ctypes.c_uint64),
                    ("available_virtual", ctypes.c_uint64),
                    ("available_extended_virtual", ctypes.c_uint64),
                ]

            status = MemoryStatus()
            status.length = ctypes.sizeof(status)
            query = ctypes.WinDLL("kernel32", use_last_error=True).GlobalMemoryStatusEx
            query.argtypes = [ctypes.POINTER(MemoryStatus)]
            query.restype = ctypes.c_int
            if query(ctypes.byref(status)):
                result["total"] = status.total_physical
                result["available"] = status.available_physical
        elif system == "Linux":
            values = {}
            with open("/proc/meminfo", encoding="ascii") as meminfo:
                for line in meminfo:
                    key, separator, value = line.partition(":")
                    if separator:
                        parts = value.split()
                        if parts and parts[-1] == "kB":
                            values[key] = int(parts[0]) * 1024
            result["total"] = values.get("MemTotal", UNKNOWN)
            if "MemAvailable" in values:
                result["available"] = values["MemAvailable"]
            elif "MemFree" in values:
                result["available"] = max(
                    0,
                    values["MemFree"]
                    + values.get("Buffers", 0)
                    + values.get("Cached", 0)
                    + values.get("SReclaimable", 0)
                    - values.get("Shmem", 0),
                )
        elif system == "Darwin":
            result["total"] = int(_command_output("/usr/sbin/sysctl", "-n", "hw.memsize"))
            lines = _command_output("/usr/bin/vm_stat").splitlines()
            page_size = int(lines[0].split("page size of ")[1].split()[0])
            pages = {}
            for line in lines[1:]:
                key, separator, value = line.partition(":")
                if separator:
                    pages[key.strip()] = int(value.strip().rstrip("."))
            if "Pages free" in pages:
                result["available"] = page_size * sum(
                    pages.get(key, 0)
                    for key in ("Pages free", "Pages inactive", "Pages speculative")
                )
    except Exception:
        pass
    return result


def collect_disk() -> dict:
    """Return disk capacity and free bytes for the current drive's root."""
    result = {"path": UNKNOWN, "total": UNKNOWN, "available": UNKNOWN}
    try:
        result["path"] = os.path.abspath(os.sep)
        usage = shutil.disk_usage(result["path"])
        result["total"] = usage.total
        result["available"] = usage.free
    except Exception:
        pass
    return result


def collect_os() -> dict:
    """Return the operating system's name and version."""
    result = {"name": UNKNOWN, "version": UNKNOWN}
    try:
        result["name"] = platform.system() or UNKNOWN
        result["version"] = platform.version() or UNKNOWN
    except Exception:
        pass
    return result


def collect_hostname() -> str:
    try:
        return platform.node() or UNKNOWN
    except Exception:
        return UNKNOWN


def collect_arch() -> str:
    try:
        return platform.machine() or UNKNOWN
    except Exception:
        return UNKNOWN


def _format_size(value):
    if not isinstance(value, (int, float)):
        return UNKNOWN
    if value >= 1024 ** 3:
        return f"{value / 1024 ** 3:.2f} GB"
    if value >= 1024 ** 2:
        return f"{value / 1024 ** 2:.2f} MB"
    return f"{value} bytes"


def format_output(data: dict) -> str:
    """Render every required section, including unavailable values."""
    cpu = data.get("cpu", {})
    memory = data.get("memory", {})
    disk = data.get("disk", {})
    system = data.get("os", {})
    return "\n".join(
        [
            "CPU",
            f"  Model: {cpu.get('model', UNKNOWN)}",
            f"  Cores (logical): {cpu.get('cores', UNKNOWN)}",
            "Memory",
            f"  Total: {_format_size(memory.get('total'))}",
            f"  Available: {_format_size(memory.get('available'))}",
            "Disk",
            f"  Path: {disk.get('path', UNKNOWN)}",
            f"  Total: {_format_size(disk.get('total'))}",
            f"  Available: {_format_size(disk.get('available'))}",
            "OS",
            f"  Name: {system.get('name', UNKNOWN)}",
            f"  Version: {system.get('version', UNKNOWN)}",
            f"Hostname: {data.get('hostname', UNKNOWN)}",
            f"Architecture: {data.get('architecture', UNKNOWN)}",
        ]
    )


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv:
        print("Usage: python machine_info.py", file=sys.stderr)
        return 2
    data = {
        "cpu": collect_cpu(),
        "memory": collect_memory(),
        "disk": collect_disk(),
        "os": collect_os(),
        "hostname": collect_hostname(),
        "architecture": collect_arch(),
    }
    print(format_output(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
