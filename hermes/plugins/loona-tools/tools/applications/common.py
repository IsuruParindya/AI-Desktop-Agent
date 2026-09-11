import os


# Common Windows application locations.
APPLICATION_ROOTS = [
    os.path.expandvars(r"%ProgramFiles%"),
    os.path.expandvars(r"%ProgramFiles(x86)%"),
    os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
    os.path.expandvars(r"%APPDATA%"),
]


# Directories that should not be searched.
IGNORED_DIRECTORIES = {
    "node_modules",
    ".git",
    ".venv",
    "__pycache__",
    "cache",
    "caches",
    "temp",
    "tmp",
}


# Executable extensions we consider applications.
APPLICATION_EXTENSIONS = {
    ".exe",
}


def normalize_name(name):
    """Normalize an application name for matching."""

    name = os.path.splitext(name)[0]

    return (
        name
        .lower()
        .replace("-", " ")
        .replace("_", " ")
        .strip()
    )


def is_valid_application(path):
    """Check whether a path points to a valid application executable."""

    if not path:
        return False

    if not os.path.isfile(path):
        return False

    return os.path.splitext(path)[1].lower() in APPLICATION_EXTENSIONS


def is_ignored_directory(directory_name):
    """Check whether a directory should be skipped."""

    return directory_name.lower() in IGNORED_DIRECTORIES