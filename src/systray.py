import logging
import os
import platform
import sys
import threading
import time
from pathlib import Path

from localize import t

logger = logging.getLogger("deadlock-rpc")

def _bundle_dir() -> Path:
    """Return the directory containing bundled data files."""
    meipass = getattr(sys, "_MEIPASS", None)
    return Path(meipass) if meipass else Path(__file__).parent

def create_tray_icon(app):
    """Create and run the system tray icon."""
    try:
        import pystray
        from PIL import Image
    except ImportError:
        logger.warning(
            "pystray or Pillow not installed. Install with: pip install pystray Pillow"
        )
        return None

    icon_path = _bundle_dir() / "favicon.ico"
    if icon_path.exists():
        logger.info("Tray icon: %s", icon_path)
        image = Image.open(icon_path)
    else:
        logger.warning("favicon.ico not found, using fallback icon")
        image = Image.new("RGB", (64, 64), color=(139, 92, 246))  # purple square

    def get_status_text():
        phase = app.state.phase.name.replace("_", " ").title()
        hero = app.state.hero_display_name or t("tray.no_hero")
        mode = app.state.mode_display() if app.state.is_in_match else t("tray.no_mode")
        return (
            f"{t('tray.phase_label', phase=phase)}\n"
            f"{t('tray.hero_label', hero=hero)}\n"
            f"{t('tray.mode_label', mode=mode)}"
        )

    def on_status(icon, item):
        """Show current status as a notification."""
        status = get_status_text()
        try:
            icon.notify(status, t("tray.status_title"))
        except Exception:
            logger.info("Status:\n%s", status)

    def on_open_log(icon, item):
        """Open the log file."""
        meipass = getattr(sys, "_MEIPASS", None)
        base = Path(sys.executable).parent if meipass else Path(__file__).parent
        log_file = base / "logs" / "deadlock_rpc.log"
        if log_file.exists():
            if platform.system() == "Windows":
                os.startfile(str(log_file))
            elif platform.system() == "Darwin":
                os.system(f'open "{log_file}"')
            else:
                os.system(f'xdg-open "{log_file}"')

    def on_quit(icon, item):
        """Quit the application."""
        logger.info(t("tray.quit") + " requested from tray")
        app.running = False
        icon.stop()

    # Build menu
    menu = pystray.Menu(
        pystray.MenuItem(t("tray.title"), None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(t("tray.status"), on_status),
        pystray.MenuItem(t("tray.open_log"), on_open_log),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(t("tray.quit"), on_quit),
    )

    icon = pystray.Icon(
        name="deadlock-rpc",
        icon=image,
        title=t("tray.title"),
        menu=menu,
    )

    # update tooltip
    def update_tooltip():
        while app.running:
            try:
                phase = app.state.phase.name.replace("_", " ").title()
                hero = app.state.hero_display_name
                if hero:
                    icon.title = t("tray.tooltip", hero=hero, phase=phase)
                else:
                    icon.title = t("tray.tooltip_no_hero", phase=phase)
            except Exception:
                pass
            time.sleep(5)

    tooltip_thread = threading.Thread(target=update_tooltip, daemon=True, name="tooltip")
    tooltip_thread.start()

    return icon