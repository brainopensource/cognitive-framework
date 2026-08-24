"""Platform detection and capability discovery (W3D-04).

Discovers OS, WSL version, user namespaces, bubblewrap presence and version,
and qualifies sandbox enforcement without denying purely based on OS/WSL name.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ...ports.event_store import Result

__all__ = [
    "PlatformCapabilities",
    "discover_platform",
]


@dataclass(frozen=True, slots=True)
class PlatformCapabilities:
    """Discovered facts about the execution host."""

    os_name: str
    system: str
    release: str
    architecture: str
    is_wsl: bool
    wsl_version: int | None  # 1, 2, or None if not WSL
    has_user_namespaces: bool
    bwrap_path: str | None
    bwrap_version: str | None
    enforcement: str  # "full" | "partial" | "unavailable"
    blockers: tuple[str, ...]

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "osName": self.os_name,
            "system": self.system,
            "release": self.release,
            "architecture": self.architecture,
            "isWsl": self.is_wsl,
            "wslVersion": self.wsl_version,
            "hasUserNamespaces": self.has_user_namespaces,
            "bwrapPath": self.bwrap_path,
            "bwrapVersion": self.bwrap_version,
            "enforcement": self.enforcement,
            "blockers": list(self.blockers),
        }


def _detect_wsl() -> tuple[bool, int | None]:
    """Detect if running under WSL and whether it is WSL1 or WSL2."""
    rel = platform.release().lower()
    uname = platform.uname()
    version_str = uname.version.lower()
    
    is_wsl = "microsoft" in rel or "wsl" in rel or "microsoft" in version_str
    if not is_wsl:
        return False, None
        
    # WSL2 uses standard Linux kernel with microsoft-standard-WSL2 in release
    if "wsl2" in rel or "microsoft-standard" in rel:
        return True, 2
    if "microsoft" in rel and "microsoft-standard" not in rel:
        return True, 1
    try:
        proc_ver = Path("/proc/version").read_text(encoding="utf-8").lower()
        if "wsl2" in proc_ver or "microsoft-standard" in proc_ver:
            return True, 2
    except OSError:
        pass
        
    return True, 1


def _check_user_namespaces() -> bool:
    """Check if unprivileged user namespaces are available."""
    clone_file = Path("/proc/sys/kernel/unprivileged_userns_clone")
    if clone_file.exists():
        try:
            val = clone_file.read_text(encoding="utf-8").strip()
            if val == "0":
                return False
        except OSError:
            pass
            
    try:
        res = subprocess.run(
            ["unshare", "--user", "true"],
            check=False,
            capture_output=True,
            timeout=2,
        )
        if res.returncode == 0:
            return True
    except (OSError, subprocess.SubprocessError):
        pass

    bwrap = shutil.which("bwrap")
    if bwrap:
        try:
            res = subprocess.run(
                [bwrap, "--unshare-user", "--ro-bind", "/usr", "/usr", "--", "/bin/true"],
                check=False,
                capture_output=True,
                timeout=2,
            )
            if res.returncode == 0:
                return True
        except (OSError, subprocess.SubprocessError):
            pass
            
    return False


def _check_bwrap() -> tuple[str | None, str | None]:
    """Find bubblewrap path and version."""
    path = shutil.which("bwrap")
    if not path:
        return None, None
    try:
        res = subprocess.run(
            [path, "--version"],
            check=False,
            capture_output=True,
            timeout=2,
            text=True,
        )
        ver = res.stdout.strip() or "unknown"
        return path, ver
    except (OSError, subprocess.SubprocessError):
        return path, "unknown"


def discover_platform() -> PlatformCapabilities:
    """Discover platform containment capabilities factually."""
    os_name = os.name
    system = platform.system()
    release = platform.release()
    arch = platform.machine()
    
    is_wsl, wsl_version = _detect_wsl()
    bwrap_path, bwrap_ver = _check_bwrap()
    has_userns = _check_user_namespaces()
    
    blockers: list[str] = []
    
    if system != "Linux":
        blockers.append(f"OS {system} is not supported for native bubblewrap containment")
    if is_wsl and wsl_version == 1:
        blockers.append("WSL1 lacks Linux namespace isolation support; upgrade to WSL2")
    if not bwrap_path:
        blockers.append("bubblewrap (bwrap) executable was not found on PATH")
    elif not has_userns:
        blockers.append("Unprivileged user namespaces are unavailable or restricted")
        
    if not blockers:
        enforcement = "full"
    elif bwrap_path and has_userns:
        enforcement = "partial"
    else:
        enforcement = "unavailable"
        
    return PlatformCapabilities(
        os_name=os_name,
        system=system,
        release=release,
        architecture=arch,
        is_wsl=is_wsl,
        wsl_version=wsl_version,
        has_user_namespaces=has_userns,
        bwrap_path=bwrap_path,
        bwrap_version=bwrap_ver,
        enforcement=enforcement,
        blockers=tuple(blockers),
    )
