"""Browser launcher — open URLs in the default browser."""

from __future__ import annotations

import webbrowser

from app.log import get_logger


def open_browser(url: str, enabled: bool = True) -> None:
    if not enabled:
        return
    logger = get_logger("browser")
    try:
        webbrowser.open(url)
        logger.info("Opened browser: %s", url)
    except Exception as e:
        logger.warning("Failed to open browser: %s", e)
