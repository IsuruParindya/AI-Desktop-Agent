import json
import os

from .common import build_file_index, score_file


def loona_search_files(args: dict, **kwargs) -> str:
    """
    Search the user's D: and E: drives for local files.

    This tool is read-only.
    """

    query = str(
        args.get("query", "")
    ).strip()

    if not query:

        return json.dumps({
            "success": False,
            "error": "No search query was provided.",
            "results": [],
        })

    try:
        max_results = int(
            args.get("max_results", 10)
        )

    except (TypeError, ValueError):

        max_results = 10

    max_results = max(
        1,
        min(max_results, 20),
    )

    file_index = build_file_index()

    candidates = []

    for file_info in file_index:

        score = score_file(
            query,
            file_info,
        )

        if score <= 0:
            continue

        candidates.append(
            (
                score,
                file_info,
            )
        )

    candidates.sort(
        key=lambda item: (
            -item[0],
            item[1]["name_lower"],
        )
    )

    results = []
    seen_paths = set()

    for score, file_info in candidates:

        full_path = file_info["path"]

        normalized_path = os.path.normcase(
            os.path.normpath(full_path)
        )

        if normalized_path in seen_paths:
            continue

        seen_paths.add(normalized_path)

        results.append({
            "name": file_info["name"],
            "path": full_path,
            "match_score": score,
        })

        if len(results) >= max_results:
            break

    return json.dumps({
        "success": True,
        "query": query,
        "result_count": len(results),
        "results": results,
    })