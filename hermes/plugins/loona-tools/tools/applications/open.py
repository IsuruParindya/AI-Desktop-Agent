import json
import os
import subprocess
import time


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
            "error": (
                "Only Windows executable applications "
                "are supported."
            ),
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
                "error": (
                    "The application process "
                    "exited immediately."
                ),
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