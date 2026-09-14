import os

ALLOWED_ROOTS = [
    os.path.normcase(os.path.normpath("D:\\")),
    os.path.normcase(os.path.normpath("E:\\")),
]

def is_allowed_path(path):
    """
    Check whether a path is located on an allowed drive.

    Loona's local file tools are restricted to the D: and E: drives.
    """

    try:
        normalized_path = os.path.normcase(
            os.path.normpath(
                os.path.abspath(path)
            )
        )

        for root in ALLOWED_ROOTS:

            try:
                common_path = os.path.commonpath([
                    normalized_path,
                    root,
                ])

            except ValueError:
                continue

            if common_path == root:
                return True

        return False

    except (OSError, ValueError):
        return False