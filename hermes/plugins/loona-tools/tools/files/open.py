import json
import os
import time
import ctypes

from .paths import is_allowed_path


def _restore_hermes_window():
    """
    Restore focus to the Hermes console after Windows launches the file.
    This prevents the newly opened application from hiding the final response.
    """
    try:
        user32 = ctypes.windll.user32

        # Give Windows a moment to finish launching the associated application.
        time.sleep(0.15)

        # Find the console window that owns this Python process.
        console_window = user32.GetConsoleWindow()

        if console_window:
            user32.ShowWindow(console_window, 5)  # SW_SHOW
            user32.SetForegroundWindow(console_window)

    except Exception:
        # Focus restoration is only a UI convenience.
        # Never make file opening fail because of it.
        pass


def loona_open_file(args: dict, **kwargs) -> str:
    """
    Open a specific local file on Windows.

    Only files on the allowed D: and E: drives can be opened.
    """

    path = str(args.get("path", "")).strip()

    if not path:
        return json.dumps({
            "success": False,
            "error": "No file path was provided.",
        })

    path = os.path.abspath(path)

    # ---------------------------------------------------------
    # Security check
    # ---------------------------------------------------------

    if not is_allowed_path(path):
        return json.dumps({
            "success": False,
            "error": (
                "For safety, Loona can only open files "
                "from the D: or E: drives."
            ),
            "path": path,
        })

    # ---------------------------------------------------------
    # Verify file exists
    # ---------------------------------------------------------

    if not os.path.isfile(path):
        return json.dumps({
            "success": False,
            "error": "The requested file does not exist.",
            "path": path,
        })

    # ---------------------------------------------------------
    # Open using Windows
    # ---------------------------------------------------------

    try:
        os.startfile(path)

        # Restore Hermes so its final response remains visible.
        _restore_hermes_window()

        return json.dumps({
            "success": True,
            "action": "opened",
            "message": "The file was opened successfully.",
            "path": path,
        })

    except OSError as error:
        return json.dumps({
            "success": False,
            "action": "open_failed",
            "error": (
                f"Windows could not open the file: {error}"
            ),
            "path": path,
        })