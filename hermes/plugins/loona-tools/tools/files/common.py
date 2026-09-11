import difflib
import os
import re


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


def build_file_index():
    """Build and cache an index of files on D: and E:."""

    global _FILE_INDEX

    if _FILE_INDEX is not None:
        return _FILE_INDEX

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

    _FILE_INDEX = files_index

    return _FILE_INDEX


def _normalize_text(text):
    """Normalize text for filename matching."""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


def _get_keywords(text):
    """Extract useful keywords from text."""

    normalized = _normalize_text(text)

    return [
        word
        for word in normalized.split()
        if len(word) >= 2
    ]


def extract_episode_info(text):
    """
    Extract season and episode numbers from a TV filename/query.

    Supports formats such as:

        S01E08
        S1E8
        S01 E08
        Season 1 Episode 8
        Season 1 Ep 8
        S1 Episode 8
    """

    normalized = _normalize_text(text)

    season = None
    episode = None

    # ---------------------------------------------------------
    # S01E08 / S1E8
    # ---------------------------------------------------------

    match = re.search(
        r"\bs(\d{1,2})\s*e(\d{1,3})\b",
        normalized,
        re.IGNORECASE,
    )

    if match:

        season = int(match.group(1))
        episode = int(match.group(2))

        return season, episode

    # ---------------------------------------------------------
    # Season 1 Episode 8
    # Season 1 Ep 8
    # ---------------------------------------------------------

    match = re.search(
        r"\bseason\s*(\d{1,2})\s*(?:episode|ep)\s*(\d{1,3})\b",
        normalized,
        re.IGNORECASE,
    )

    if match:

        season = int(match.group(1))
        episode = int(match.group(2))

        return season, episode

    # ---------------------------------------------------------
    # S1 Episode 8
    # S01 Ep 08
    # ---------------------------------------------------------

    match = re.search(
        r"\bs(\d{1,2})\s*(?:episode|ep)\s*(\d{1,3})\b",
        normalized,
        re.IGNORECASE,
    )

    if match:

        season = int(match.group(1))
        episode = int(match.group(2))

        return season, episode

    return None, None


def remove_episode_info(text):
    """Remove TV season/episode information from a search query."""

    normalized = _normalize_text(text)

    patterns = [
        r"\bs\d{1,2}\s*e\d{1,3}\b",
        r"\bseason\s*\d{1,2}\s*(?:episode|ep)\s*\d{1,3}\b",
        r"\bs\d{1,2}\s*(?:episode|ep)\s*\d{1,3}\b",
    ]

    for pattern in patterns:

        normalized = re.sub(
            pattern,
            " ",
            normalized,
            flags=re.IGNORECASE,
        )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    ).strip()

    return normalized


def score_title(query, filename_stem):
    """Score a title independently from season/episode information."""

    query_normalized = _normalize_text(query)
    filename_normalized = _normalize_text(filename_stem)

    if not query_normalized or not filename_normalized:
        return 0

    if query_normalized == filename_normalized:
        return 1000

    if query_normalized in filename_normalized:
        return 900

    query_words = _get_keywords(query_normalized)
    filename_words = _get_keywords(filename_normalized)

    if not query_words:
        return 0

    matched_words = 0
    fuzzy_words = 0

    for query_word in query_words:

        if query_word in filename_words:
            matched_words += 1
            continue

        if any(
            query_word in filename_word
            or filename_word in query_word
            for filename_word in filename_words
        ):
            matched_words += 1
            continue

        best_similarity = max(
            (
                difflib.SequenceMatcher(
                    None,
                    query_word,
                    filename_word,
                ).ratio()
                for filename_word in filename_words
            ),
            default=0,
        )

        if best_similarity >= 0.75:
            fuzzy_words += 1

    total_words = len(query_words)

    if matched_words == total_words:
        return 850

    if matched_words + fuzzy_words == total_words:
        return 780

    if matched_words >= 2:
        return 650

    if matched_words == 1:
        return 500

    similarity = difflib.SequenceMatcher(
        None,
        query_normalized,
        filename_normalized,
    ).ratio()

    return round(similarity * 700)


def score_file(query, file_info):
    """
    Score a file against a query.

    TV episode queries receive special handling:
    season and episode numbers are treated as hard requirements.
    """

    query_normalized = _normalize_text(query)

    filename = file_info["name_lower"]
    stem = file_info["stem_lower"]
    extension = file_info["extension"]

    if not query_normalized:
        return 0

    query_season, query_episode = extract_episode_info(query)
    file_season, file_episode = extract_episode_info(stem)

    # =========================================================
    # TV EPISODE MATCHING
    # =========================================================

    if query_season is not None and query_episode is not None:

        # A file with explicit episode information must match
        # BOTH season and episode exactly.
        if file_season is not None and file_episode is not None:

            if (
                file_season != query_season
                or file_episode != query_episode
            ):
                return 0

        # If the query asks for an episode but the filename
        # contains no episode information, reject it.
        else:
            return 0

        # Remove episode information and compare only the title.
        query_title = remove_episode_info(query)
        file_title = remove_episode_info(stem)

        title_score = score_title(
            query_title,
            file_title,
        )

        if title_score == 0:
            return 0

        # Strong bonus because season + episode matched exactly.
        score = title_score + 200

    # =========================================================
    # NORMAL FILE / MOVIE MATCHING
    # =========================================================

    else:

        score = score_title(
            query,
            stem,
        )

    # ---------------------------------------------------------
    # Preferred extension bonus
    # ---------------------------------------------------------

    if extension in PREFERRED_EXTENSIONS:
        score += 25

    return score


def is_allowed_path(path):
    """Check whether a path is inside an allowed drive."""

    normalized_path = os.path.normcase(
        os.path.normpath(path)
    )

    for root in SEARCH_ROOTS:

        normalized_root = os.path.normcase(
            os.path.normpath(root)
        )

        try:

            if os.path.commonpath(
                [
                    normalized_path,
                    normalized_root,
                ]
            ) == normalized_root:

                return True

        except ValueError:
            continue

    return False