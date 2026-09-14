import os
import subprocess


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

    return (
        os.path.splitext(path)[1].lower()
        in APPLICATION_EXTENSIONS
    )


def is_ignored_directory(directory_name):
    """Check whether a directory should be skipped."""

    return directory_name.lower() in IGNORED_DIRECTORIES


def get_processes_by_name(process_name):
    """
    Find running Windows processes by executable name.
    """

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


def is_process_running(pid):
    """
    Check whether a Windows process is still running.
    """

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