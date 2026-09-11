import json
import os
import subprocess
import time


def _get_processes_by_name(process_name):
    """Find running Windows processes by executable name."""

    result = subprocess.run(
        [
            "tasklist",
            "/FO",
            "CSV",
            "/NH",
        ],
        capture_output=True,
        text=True,
        shell=False,
    )

    if result.returncode != 0:
        return []

    process_name = process_name.lower()

    processes = []

    for line in result.stdout.splitlines():

        parts = [
            part.strip('"')
            for part in line.split('","')
        ]

        if len(parts) < 2:
            continue

        image_name = parts[0]
        pid = parts[1]

        if image_name.lower() != process_name:
            continue

        try:
            pid = int(pid)
        except ValueError:
            continue

        processes.append({
            "name": image_name,
            "pid": pid,
        })

    return processes


def _is_process_running(pid):
    """Check whether a Windows process is still running."""

    result = subprocess.run(
        [
            "tasklist",
            "/FI",
            f"PID eq {pid}",
            "/FO",
            "CSV",
            "/NH",
        ],
        capture_output=True,
        text=True,
        shell=False,
    )

    if result.returncode != 0:
        return False

    return str(pid) in result.stdout


def loona_open_application(args: dict, **kwargs) -> str:
    """
    Open a Windows application using a verified executable path.
    """

    path = str(
        args.get("path", "")
    ).strip()

    if not path:
        return json.dumps({
            "success": False,
            "action": "open_failed",
            "error": "No application path was provided.",
        })

    if not os.path.isfile(path):
        return json.dumps({
            "success": False,
            "action": "open_failed",
            "error": "Application executable was not found.",
            "path": path,
        })

    if os.path.splitext(path)[1].lower() != ".exe":
        return json.dumps({
            "success": False,
            "action": "open_failed",
            "error": "Only Windows executable applications are supported.",
            "path": path,
        })

    try:
        process = subprocess.Popen(
            [path],
            shell=False,
        )

        time.sleep(1)

        if process.poll() is not None:
            return json.dumps({
                "success": False,
                "action": "open_failed",
                "error": "The application process exited immediately.",
                "path": path,
            })

        return json.dumps({
            "success": True,
            "action": "application_opened",
            "path": path,
            "pid": process.pid,
        })

    except Exception as error:
        return json.dumps({
            "success": False,
            "action": "open_failed",
            "error": str(error),
            "path": path,
        })


def loona_close_application(args: dict, **kwargs) -> str:
    """
    Close a Windows application gracefully using its executable name.

    The application name must be an executable name such as:
    chrome.exe, notepad.exe, discord.exe.
    """

    process_name = str(
        args.get("process_name", "")
    ).strip()

    if not process_name:
        return json.dumps({
            "success": False,
            "action": "close_failed",
            "error": "No application process name was provided.",
        })

    if not process_name.lower().endswith(".exe"):
        process_name += ".exe"

    processes = _get_processes_by_name(
        process_name
    )

    if not processes:
        return json.dumps({
            "success": False,
            "action": "close_failed",
            "error": "The application is not currently running.",
            "process_name": process_name,
        })

    closed_processes = []

    for process in processes:

        pid = process["pid"]

        try:
            result = subprocess.run(
                [
                    "taskkill",
                    "/PID",
                    str(pid),
                ],
                capture_output=True,
                text=True,
                shell=False,
            )

            if result.returncode != 0:
                continue

            closed_processes.append(pid)

        except Exception:
            continue

    time.sleep(0.5)

    still_running = [
        process["pid"]
        for process in processes
        if _is_process_running(process["pid"])
    ]

    if still_running:
        return json.dumps({
            "success": False,
            "action": "close_failed",
            "error": (
                "The application could not be completely closed "
                "without force termination."
            ),
            "process_name": process_name,
            "closed_pids": closed_processes,
            "still_running": still_running,
        })

    return json.dumps({
        "success": True,
        "action": "application_closed",
        "process_name": process_name,
        "closed_pids": closed_processes,
    })