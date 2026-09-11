import json
import os

from .common import (
    extract_episode_info,
    is_allowed_path,
)
from .search import loona_search_files


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


def loona_open_file_by_query(args: dict, **kwargs) -> str:
    """
    Find and open the best matching local file.

    TV episode requests receive strict season/episode matching.
    """

    query = str(
        args.get("query", "")
    ).strip()

    if not query:

        return json.dumps({
            "success": False,
            "action": "search_failed",
            "error": "No file name was provided.",
        })

    # ---------------------------------------------------------
    # Detect TV episode request
    # ---------------------------------------------------------

    season, episode = extract_episode_info(query)

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    search_result = json.loads(
        loona_search_files({
            "query": query,
            "max_results": 10,
        })
    )

    if not search_result.get("success"):

        return json.dumps({
            "success": False,
            "action": "search_failed",
            "query": query,
            "error": search_result.get(
                "error",
                "File search failed.",
            ),
        })

    results = search_result.get(
        "results",
        [],
    )

    # ---------------------------------------------------------
    # Nothing found
    # ---------------------------------------------------------

    if not results:

        return json.dumps({
            "success": False,
            "action": "not_found",
            "query": query,
            "error": (
                f"No local file matching '{query}' "
                "was found on D: or E:."
            ),
        })

    # ---------------------------------------------------------
    # TV episode filtering
    # ---------------------------------------------------------

    if season is not None and episode is not None:

        episode_results = []

        for result in results:

            file_season, file_episode = extract_episode_info(
                result.get("name", "")
            )

            if (
                file_season == season
                and file_episode == episode
            ):
                episode_results.append(result)

        results = episode_results

        if not results:

            return json.dumps({
                "success": False,
                "action": "not_found",
                "query": query,
                "error": (
                    f"No local file for Season {season}, "
                    f"Episode {episode} was found."
                ),
            })

    # ---------------------------------------------------------
    # Sort strongest match first
    # ---------------------------------------------------------

    results.sort(
        key=lambda item: item.get(
            "match_score",
            0,
        ),
        reverse=True,
    )

    best_match = results[0]

    # ---------------------------------------------------------
    # Safety threshold
    # ---------------------------------------------------------

    if best_match.get(
        "match_score",
        0,
    ) < 450:

        return json.dumps({
            "success": False,
            "action": "confirmation_required",
            "query": query,
            "message": (
                "A weak local filename match was found. "
                "Do not open it automatically."
            ),
            "best_match": best_match,
        })

    # ---------------------------------------------------------
    # Check for competing matches
    # ---------------------------------------------------------

    if len(results) > 1:

        second_match = results[1]

        score_difference = (
            best_match.get("match_score", 0)
            - second_match.get("match_score", 0)
        )

        # If two results are very close, don't guess.
        if score_difference < 50:

            return json.dumps({
                "success": False,
                "action": "multiple_matches",
                "query": query,
                "message": (
                    "Multiple local files are strong matches. "
                    "Do not open one automatically."
                ),
                "matches": results[:5],
            })

    # ---------------------------------------------------------
    # Open selected file
    # ---------------------------------------------------------

    open_result = json.loads(
        loona_open_file({
            "path": best_match["path"],
        })
    )

    if not open_result.get("success"):

        return json.dumps({
            "success": False,
            "action": "open_failed",
            "query": query,
            "selected_file": best_match,
            "error": open_result.get(
                "error",
                "The file could not be opened.",
            ),
        })

    # ---------------------------------------------------------
    # Successful result
    # ---------------------------------------------------------

    return json.dumps({
        "success": True,
        "action": "opened",
        "query": query,
        "file": best_match["name"],
        "path": best_match["path"],
        "message": (
            f"Successfully opened '{best_match['name']}'."
        ),
    })