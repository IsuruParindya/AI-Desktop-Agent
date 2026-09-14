import ctypes
import json
import time

from .common import (
    get_processes_by_name,
    is_process_running,
)


user32 = ctypes.windll.user32

WM_CLOSE = 0x0010


def _get_window_process_id(hwnd):
    """Get the process ID that owns a Windows window."""

    process_id = ctypes.c_ulong()

    user32.GetWindowThreadProcessId(
        hwnd,
        ctypes.byref(process_id),
    )

    return process_id.value


def _get_visible_windows():
    """Get all visible top-level Windows application windows."""

    windows = []

    enum_windows_proc = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.c_void_p,
        ctypes.c_void_p,
    )

    def enum_window(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            windows.append(hwnd)

        return True

    callback = enum_windows_proc(enum_window)

    user32.EnumWindows(
        callback,
        0,
    )

    return windows


def _get_window_title(hwnd):
    """Get the title of a Windows application window."""

    length = user32.GetWindowTextLengthW(hwnd)

    if length <= 0:
        return ""

    buffer = ctypes.create_unicode_buffer(length + 1)

    user32.GetWindowTextW(
        hwnd,
        buffer,
        length + 1,
    )

    return buffer.value.strip()


def _send_close_message(hwnd):
    """Ask a Windows application window to close normally."""

    return bool(
        user32.PostMessageW(
            hwnd,
            WM_CLOSE,
            0,
            0,
        )
    )


def _find_matching_windows(processes, window_title):
    """
    Find visible windows belonging to the target processes.

    If window_title is provided, only windows whose titles
    contain that text are returned.
    """

    target_pids = {
        process["pid"]
        for process in processes
    }

    window_title = window_title.strip().lower()

    matches = []

    for hwnd in _get_visible_windows():

        pid = _get_window_process_id(hwnd)

        if pid not in target_pids:
            continue

        title = _get_window_title(hwnd)

        if not title:
            continue

        if window_title and (
            window_title not in title.lower()
        ):
            continue

        matches.append({
            "hwnd": hwnd,
            "pid": pid,
            "title": title,
        })

    return matches


def loona_close_application(args: dict, **kwargs) -> str:
    """
    Close a Windows application or a specific application window
    gracefully.

    When window_title is provided, only the matching window is
    closed. Other instances of the same application remain open.

    Force termination is never used.
    """

    process_name = str(
        args.get("process_name", "")
    ).strip()

    window_title = str(
        args.get("window_title", "")
    ).strip()

    if not process_name:
        return json.dumps({
            "success": False,
            "action": "close_failed",
            "error": (
                "No application process name "
                "was provided."
            ),
        })

    if not process_name.lower().endswith(".exe"):
        process_name += ".exe"

    processes = get_processes_by_name(
        process_name
    )

    if not processes:
        return json.dumps({
            "success": False,
            "action": "close_failed",
            "error": (
                "The application is not "
                "currently running."
            ),
            "process_name": process_name,
        })

    matching_windows = _find_matching_windows(
        processes,
        window_title,
    )

    if not matching_windows:
        return json.dumps({
            "success": False,
            "action": "close_failed",
            "error": (
                "No matching application window "
                "was found."
            ),
            "process_name": process_name,
            "window_title": window_title,
        })

    close_requests = []

    for window in matching_windows:

        if _send_close_message(
            window["hwnd"]
        ):
            close_requests.append(window)

    if not close_requests:
        return json.dumps({
            "success": False,
            "action": "close_failed",
            "error": (
                "The application window could "
                "not be closed gracefully."
            ),
            "process_name": process_name,
            "window_title": window_title,
        })

    # Give Windows time to process WM_CLOSE.
    time.sleep(1.0)

    still_running = []

    for window in close_requests:

        if user32.IsWindow(
            window["hwnd"]
        ):
            still_running.append({
                "pid": window["pid"],
                "title": window["title"],
            })

    if still_running:
        return json.dumps({
            "success": False,
            "action": "close_failed",
            "error": (
                "The targeted application window "
                "did not close after the graceful "
                "close request."
            ),
            "process_name": process_name,
            "window_title": window_title,
            "close_requests": close_requests,
            "still_running": still_running,
        })

    return json.dumps({
        "success": True,
        "action": "application_closed",
        "process_name": process_name,
        "window_title": window_title,
        "closed_windows": close_requests,
    })