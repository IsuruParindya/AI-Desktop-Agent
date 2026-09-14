import json
import os

from .paths import is_allowed_path


def loona_open_file(args: dict, **kwargs) -> str:
    """
    Open a specific local file on Windows.

    Only files on the allowed D: and E: drives can be opened.
    """

    path = str(
        args.get("path", "")
    ).strip()

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