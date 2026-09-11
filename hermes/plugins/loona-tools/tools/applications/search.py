import json
import os

from .common import (
    APPLICATION_EXTENSIONS,
    APPLICATION_ROOTS,
    is_ignored_directory,
    is_valid_application,
    normalize_name,
)


def _build_application_index():
    """Find Windows application executables in common install locations."""

    applications = []
    seen_paths = set()

    for root in APPLICATION_ROOTS:

        if not root or not os.path.exists(root):
            continue

        for current_root, directories, files in os.walk(
            root,
            topdown=True,
            onerror=lambda error: None,
        ):

            directories[:] = [
                directory
                for directory in directories
                if not is_ignored_directory(directory)
            ]

            for filename in files:

                extension = os.path.splitext(
                    filename
                )[1].lower()

                if extension not in APPLICATION_EXTENSIONS:
                    continue

                path = os.path.join(
                    current_root,
                    filename,
                )

                normalized_path = os.path.normcase(
                    os.path.abspath(path)
                )

                if normalized_path in seen_paths:
                    continue

                if not is_valid_application(path):
                    continue

                seen_paths.add(normalized_path)

                applications.append({
                    "name": os.path.splitext(filename)[0],
                    "filename": filename,
                    "path": path,
                    "name_normalized": normalize_name(filename),
                })

    return applications


def loona_search_applications(args: dict, **kwargs) -> str:
    """
    Search for installed Windows applications by name.

    This only discovers executable applications.
    It does not launch anything.
    """

    query = str(
        args.get("query", "")
    ).strip()

    if not query:

        return json.dumps({
            "success": False,
            "action": "search_failed",
            "error": "No application name was provided.",
        })

    query_normalized = normalize_name(query)

    applications = _build_application_index()

    results = []

    for application in applications:

        name = application["name_normalized"]

        if query_normalized == name:

            score = 1000

        elif query_normalized in name:

            score = 900

        elif name in query_normalized:

            score = 850

        else:

            query_words = query_normalized.split()
            name_words = name.split()

            matched_words = sum(
                1
                for word in query_words
                if word in name_words
                or any(
                    word in name_word
                    for name_word in name_words
                )
            )

            if matched_words == 0:
                continue

            score = 500 + (
                matched_words * 100
            )

        results.append({
            "name": application["name"],
            "filename": application["filename"],
            "path": application["path"],
            "match_score": score,
        })

    results.sort(
        key=lambda item: item["match_score"],
        reverse=True,
    )

    return json.dumps({
        "success": True,
        "action": "search_completed",
        "query": query,
        "results": results[:10],
        "count": len(results),
    })