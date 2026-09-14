import difflib
import re

from .episodes import (
    extract_episode_info,
    remove_episode_info,
)


def _normalize_text(text):
    """
    Normalize text for comparison.

    Converts to lowercase, replaces non-alphanumeric characters
    with spaces, and collapses repeated whitespace.
    """

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text,
    )

    return " ".join(text.split())


def _get_keywords(text):
    """
    Extract meaningful keywords from normalized text.

    Returns a list so the matching process can preserve
    the original keyword-based scoring behaviour.
    """

    normalized = _normalize_text(text)

    return [
        word
        for word in normalized.split()
        if len(word) >= 2
    ]


def score_title(query, filename_stem):
    """
    Calculate how closely a filename matches the search query.

    Uses:
    - Exact title matching
    - Full query matching
    - Word matching
    - Partial word matching
    - Fuzzy word matching
    - Overall fuzzy matching
    """

    query_normalized = _normalize_text(query)
    filename_normalized = _normalize_text(filename_stem)

    if not query_normalized or not filename_normalized:
        return 0

    # ---------------------------------------------------------
    # Exact title match
    # ---------------------------------------------------------

    if query_normalized == filename_normalized:
        return 1000

    # ---------------------------------------------------------
    # Full query contained in filename
    # ---------------------------------------------------------

    if query_normalized in filename_normalized:
        return 900

    query_keywords = _get_keywords(query)
    filename_keywords = _get_keywords(filename_stem)

    if not query_keywords or not filename_keywords:
        return 0

    matched_count = 0
    fuzzy_count = 0

    # ---------------------------------------------------------
    # Word-by-word matching
    # ---------------------------------------------------------

    for query_word in query_keywords:

        best_similarity = 0
        exact_match = False
        partial_match = False

        for filename_word in filename_keywords:

            # Exact word match
            if query_word == filename_word:

                exact_match = True
                break

            # Partial word match
            if (
                query_word in filename_word
                or filename_word in query_word
            ):

                partial_match = True
                break

            # Fuzzy word similarity
            similarity = difflib.SequenceMatcher(
                None,
                query_word,
                filename_word,
            ).ratio()

            if similarity > best_similarity:
                best_similarity = similarity

        if exact_match or partial_match:

            matched_count += 1

        elif best_similarity >= 0.75:

            matched_count += 1
            fuzzy_count += 1

    total_keywords = len(query_keywords)

    # ---------------------------------------------------------
    # Strong keyword matches
    # ---------------------------------------------------------

    if matched_count == total_keywords:

        if fuzzy_count > 0:
            return 780

        return 850

    # ---------------------------------------------------------
    # Multiple keyword matches
    # ---------------------------------------------------------

    if matched_count >= 2:
        return 650

    # ---------------------------------------------------------
    # Single keyword match
    # ---------------------------------------------------------

    if matched_count == 1:
        return 500

    # ---------------------------------------------------------
    # Overall fuzzy matching
    # ---------------------------------------------------------

    similarity = difflib.SequenceMatcher(
        None,
        query_normalized,
        filename_normalized,
    ).ratio()

    return int(similarity * 700)


def score_file(query, file_info):
    """
    Calculate the final score for a file.

    Season and episode information are handled separately from
    the filename title.
    """

    filename_stem = file_info["stem_lower"]

    query_season, query_episode = extract_episode_info(
        query
    )

    filename_season, filename_episode = extract_episode_info(
        filename_stem
    )

    # ---------------------------------------------------------
    # Episode matching
    # ---------------------------------------------------------

    if query_season is not None:

        if filename_season != query_season:
            return 0

    if query_episode is not None:

        if filename_episode != query_episode:
            return 0

    # ---------------------------------------------------------
    # Remove episode information before title matching
    # ---------------------------------------------------------

    clean_query = remove_episode_info(query)

    clean_filename = remove_episode_info(
        filename_stem
    )

    score = score_title(
        clean_query,
        clean_filename,
    )

    # Episode-only queries can have an empty title after
    # removing the episode information.
    if score <= 0:

        if query_episode is not None:

            score = 500

        else:

            return 0

    # ---------------------------------------------------------
    # Episode match bonus
    # ---------------------------------------------------------

    if (
        query_season is not None
        or query_episode is not None
    ):

        score += 200

    # ---------------------------------------------------------
    # Preferred file format bonus
    # ---------------------------------------------------------

    preferred_extensions = {
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

    if file_info["extension"] in preferred_extensions:

        score += 25

    return score