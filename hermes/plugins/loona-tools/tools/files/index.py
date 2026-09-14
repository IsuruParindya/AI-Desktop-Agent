import json
import os
import time


SEARCH_ROOTS = [
    "D:\\",
    "E:\\",
]


IGNORED_DIRECTORIES = {
    "$recycle.bin",
    "system volume information",
    "windowsapps",
    "node_modules",
    ".git",
    ".venv",
    "__pycache__",
}


PREFERRED_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".webm",
    ".mp3",
    ".wav",
    ".flac",
    ".pdf",
    ".docx",
    ".doc",
    ".xlsx",
    ".xls",
    ".pptx",
    ".ppt",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
}


_FILE_INDEX = None


INDEX_FILE = os.path.join(
    os.path.dirname(__file__),
    ".file_index.json",
)


def _scan_drives():
    """
    Scan the D: and E: drives and build the file index.
    """

    files_index = []

    for root in SEARCH_ROOTS:

        if not os.path.exists(root):
            continue

        for current_root, directories, files in os.walk(
            root,
            topdown=True,
            onerror=lambda error: None,
        ):

            directories[:] = [
                directory
                for directory in directories
                if directory.lower() not in IGNORED_DIRECTORIES
            ]

            for filename in files:

                full_path = os.path.join(
                    current_root,
                    filename,
                )

                name_without_extension = os.path.splitext(
                    filename
                )[0]

                files_index.append({
                    "name": filename,
                    "name_lower": filename.lower(),
                    "stem_lower": name_without_extension.lower(),
                    "path": full_path,
                    "extension": os.path.splitext(filename)[1].lower(),
                })

    return files_index


def _save_index(files_index):
    """
    Save the file index to disk.
    """

    try:

        with open(
            INDEX_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                files_index,
                file,
                ensure_ascii=False,
            )

    except (OSError, TypeError):
        pass


def _load_index():
    """
    Load the previously saved file index.
    """

    if not os.path.exists(INDEX_FILE):
        return None

    try:

        with open(
            INDEX_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

    except (
        OSError,
        ValueError,
        TypeError,
        json.JSONDecodeError,
    ):
        pass

    return None


def build_file_index():
    """
    Load the file index.

    The first run scans D: and E: and saves the index.
    Future Loona sessions load the saved index instead of
    scanning the drives again.
    """

    global _FILE_INDEX

    # Already loaded during this session.
    if _FILE_INDEX is not None:
        return _FILE_INDEX

    # Try the persistent index first.
    cached_index = _load_index()

    if cached_index is not None:

        _FILE_INDEX = cached_index

        return _FILE_INDEX

    # No saved index exists, so perform the initial scan.
    start_time = time.perf_counter()

    _FILE_INDEX = _scan_drives()

    _save_index(_FILE_INDEX)

    elapsed = time.perf_counter() - start_time

    print(
        f"[Loona] File index built: "
        f"{len(_FILE_INDEX)} files "
        f"in {elapsed:.2f}s"
    )

    return _FILE_INDEX


def refresh_file_index():
    """
    Completely rebuild the file index.

    Use this when files have been added, removed, or moved
    and Loona needs to update its index.
    """

    global _FILE_INDEX

    start_time = time.perf_counter()

    _FILE_INDEX = _scan_drives()

    _save_index(_FILE_INDEX)

    elapsed = time.perf_counter() - start_time

    print(
        f"[Loona] File index refreshed: "
        f"{len(_FILE_INDEX)} files "
        f"in {elapsed:.2f}s"
    )

    return _FILE_INDEX


def clear_file_index():
    """
    Remove the cached index from memory and disk.
    """

    global _FILE_INDEX

    _FILE_INDEX = None

    try:

        if os.path.exists(INDEX_FILE):
            os.remove(INDEX_FILE)

    except OSError:
        pass