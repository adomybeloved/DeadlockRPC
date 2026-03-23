"""Auto-update checker for DeadlockRPC.
Checks GitHub for a newer release on startup and prompts the user to update."""

from __future__ import annotations

import logging
import os
import platform
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

GITHUB_REPO = "Jelloge/Deadlock-Rich-Presence"
CURRENT_VERSION = "1.5"

# Whether we're running as a PyInstaller binary
_FROZEN = getattr(sys, "_MEIPASS", None) is not None


def _parse_version(tag: str) -> tuple[int, ...]:
    """'v1.4.1' -> (1, 4, 1)"""
    cleaned = tag.lstrip("vV").strip()
    parts = []
    for p in cleaned.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            break
    return tuple(parts) or (0,)


def check_for_update() -> dict | None:
    """Returns release info dict if a newer version exists, else None."""
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        release = resp.json()

        remote_tag = release.get("tag_name", "")
        if _parse_version(remote_tag) > _parse_version(CURRENT_VERSION):
            return release
        return None
    except Exception as e:
        logger.debug("Update check failed: %s", e)
        return None


def _find_asset(release: dict, suffix: str) -> dict | None:
    """Find a release asset by file extension."""
    for asset in release.get("assets", []):
        if asset["name"].lower().endswith(suffix):
            return asset
    return None


def _find_binary_asset(release: dict) -> dict | None:
    """Find the right binary asset for this platform."""
    if platform.system() == "Windows":
        # Look for the .zip first, fall back to bare .exe
        return _find_asset(release, "windows-x86_64.zip") or _find_asset(release, ".exe")
    else:
        return _find_asset(release, "linux-x86_64.zip")


# -- Prompts --

def _prompt_windows(release: dict) -> bool:
    """Native Windows Yes/No dialog."""
    tag = release.get("tag_name", "?")
    try:
        import ctypes
        MB_YESNO = 0x04
        MB_ICONINFORMATION = 0x40
        IDYES = 6
        result = ctypes.windll.user32.MessageBoxW(
            0,
            f"A new version of DeadlockRPC is available ({tag}).\n\nUpdate now?",
            "DeadlockRPC Update",
            MB_YESNO | MB_ICONINFORMATION,
        )
        return result == IDYES
    except Exception:
        return False


def _prompt_linux(release: dict) -> bool:
    """Try zenity, then kdialog, then terminal input."""
    tag = release.get("tag_name", "?")
    msg = f"A new version of DeadlockRPC is available ({tag}).\n\nUpdate now?"

    for cmd in [
        ["zenity", "--question", "--title=DeadlockRPC Update", "--text", msg],
        ["kdialog", "--yesno", msg, "--title", "DeadlockRPC Update"],
    ]:
        try:
            return subprocess.run(cmd, timeout=60).returncode == 0
        except FileNotFoundError:
            continue

    # Terminal fallback
    try:
        answer = input(f"DeadlockRPC {tag} is available. Update now? [y/N] ").strip().lower()
        return answer in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


# Update methods

def _download_asset(asset: dict, dest_dir: Path, suffix: str = "") -> Path:
    """Download a release asset to dest_dir. Returns the downloaded file path."""
    url = asset["browser_download_url"]
    logger.info("Downloading %s ...", asset["name"])

    resp = requests.get(url, timeout=120, stream=True)
    resp.raise_for_status()

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix, dir=dest_dir)
    with os.fdopen(tmp_fd, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return Path(tmp_path)


def _extract_exe_from_zip(zip_path: Path, dest_dir: Path) -> Path:
    """Extract the .exe from a release zip and return its path."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        exe_names = [n for n in zf.namelist() if n.lower().endswith(".exe")]
        if not exe_names:
            raise FileNotFoundError("No .exe found inside the zip")
        exe_name = exe_names[0]
        # Extract to a flat temp file (zip may have subfolders like DeadlockRPC/DeadlockRPC.exe)
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".exe", dir=dest_dir)
        with zf.open(exe_name) as src, os.fdopen(tmp_fd, "wb") as dst:
            dst.write(src.read())
        return Path(tmp_path)


def _update_binary_windows(release: dict) -> bool:
    """Download new release asset and create a batch script to swap + restart."""
    asset = _find_binary_asset(release)
    if not asset:
        logger.warning("No Windows binary found in release assets.")
        return False

    current_exe = Path(sys.executable)
    tmp_path = None

    try:
        is_zip = asset["name"].lower().endswith(".zip")
        dl_suffix = ".zip" if is_zip else ".exe"
        tmp_path = _download_asset(asset, current_exe.parent, suffix=dl_suffix)

        if is_zip:
            # Extract the exe from the zip, then clean up the zip
            extracted = _extract_exe_from_zip(tmp_path, current_exe.parent)
            os.unlink(tmp_path)
            tmp_path = extracted

        logger.info("Download complete. Restarting...")

        # Batch script waits for us to exit, replaces the exe, relaunches
        bat_path = current_exe.parent / "_update.bat"
        bat_path.write_text(
            f'@echo off\r\n'
            f'timeout /t 2 /nobreak >nul\r\n'
            f'move /y "{tmp_path}" "{current_exe}"\r\n'
            f'start "" "{current_exe}"\r\n'
            f'del "%~f0"\r\n',
            encoding="utf-8",
        )

        subprocess.Popen(
            ["cmd", "/c", str(bat_path)],
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return True

    except Exception as e:
        logger.error("Update failed: %s", e)
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        return False


def _extract_binary_from_zip(zip_path: Path, dest_dir: Path) -> Path:
    """Extract the binary from a release zip (Linux). Returns extracted path."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        # Look for the DeadlockRPC binary (no extension)
        candidates = [n for n in zf.namelist()
                      if "deadlockrpc" in n.lower() and not n.lower().endswith((".zip", ".json", ".ico"))
                      and not n.endswith("/")]
        if not candidates:
            # Fallback: first file that isn't a config/icon/directory
            candidates = [n for n in zf.namelist()
                          if not n.lower().endswith((".json", ".ico", ".zip")) and not n.endswith("/")]
        if not candidates:
            raise FileNotFoundError("No binary found inside the zip")
        name = candidates[0]
        # Extract to a flat temp file (zip may have subfolders like DeadlockRPC/DeadlockRPC)
        tmp_fd, tmp_path = tempfile.mkstemp(dir=dest_dir)
        with zf.open(name) as src, os.fdopen(tmp_fd, "wb") as dst:
            dst.write(src.read())
        return Path(tmp_path)


def _update_binary_linux(release: dict) -> bool:
    """Download new binary and replace the current one."""
    asset = _find_binary_asset(release)
    if not asset:
        logger.warning("No Linux binary found in release assets.")
        return False

    current_exe = Path(sys.executable)
    tmp_path = None

    try:
        is_zip = asset["name"].lower().endswith(".zip")
        dl_suffix = ".zip" if is_zip else ""
        tmp_path = _download_asset(asset, current_exe.parent, suffix=dl_suffix)

        if is_zip:
            extracted = _extract_binary_from_zip(tmp_path, current_exe.parent)
            os.unlink(tmp_path)
            tmp_path = extracted

        os.chmod(tmp_path, 0o755)

        logger.info("Download complete. Restarting...")

        # Shell script waits for us to exit, replaces the binary, relaunches
        sh_path = current_exe.parent / "_update.sh"
        sh_path.write_text(
            f'#!/bin/sh\n'
            f'sleep 2\n'
            f'mv -f "{tmp_path}" "{current_exe}"\n'
            f'chmod +x "{current_exe}"\n'
            f'"{current_exe}" &\n'
            f'rm -f "$0"\n',
        )
        os.chmod(sh_path, 0o755)

        subprocess.Popen(
            ["sh", str(sh_path)],
            start_new_session=True,
        )
        return True

    except Exception as e:
        logger.error("Update failed: %s", e)
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        return False


def _update_git() -> bool:
    """For users running from source: git pull and restart."""
    repo_dir = Path(__file__).parent.parent
    if not (repo_dir / ".git").exists():
        logger.warning("Not a git repo and not a binary — can't auto-update.")
        return False

    try:
        logger.info("Running git pull...")
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            logger.error("git pull failed: %s", result.stderr.strip())
            return False

        if "Already up to date" in result.stdout:
            logger.info("Already up to date.")
            return False

        logger.info("Updated. Restarting...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
        return True

    except Exception as e:
        logger.error("Update failed: %s", e)
        return False


# -- Entry point --

def check_and_prompt() -> None:
    """Check for update, prompt user, apply if accepted."""
    logger.debug("Checking for updates...")
    release = check_for_update()

    if release is None:
        logger.debug("No update available.")
        return

    tag = release.get("tag_name", "?")
    logger.info("New version available: %s (current: %s)", tag, CURRENT_VERSION)

    is_windows = platform.system() == "Windows"

    accepted = _prompt_windows(release) if is_windows else _prompt_linux(release)

    if not accepted:
        logger.info("Update skipped.")
        return

    if _FROZEN:
        # Running as a PyInstaller binary — download and replace
        if is_windows:
            success = _update_binary_windows(release)
        else:
            success = _update_binary_linux(release)
        if success:
            sys.exit(0)
    else:
        # Running from source — git pull
        _update_git()
