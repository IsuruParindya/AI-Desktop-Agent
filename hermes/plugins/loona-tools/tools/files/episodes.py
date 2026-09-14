import re


def extract_episode_info(text):
    """
    Extract season and episode information from text.

    Supports:
    - S01E08
    - S1E8
    - S01 E08
    - Season 1 Episode 8
    - Season 1 Ep 8
    - S1 Episode 8
    - 2nd Episode
    - 2nd Ep

    Returns:
        tuple[int | None, int | None]
    """

    text = str(text)

    # Normalize text for easier matching.
    normalized = re.sub(
        r"[^a-zA-Z0-9]+",
        " ",
        text,
    ).strip().lower()

    # ---------------------------------------------------------
    # Season + Episode formats
    # ---------------------------------------------------------

    patterns = [
        # S01E08 / S1E8 / S01 E08
        (
            r"\bs(\d+)\s*e(\d+)\b",
            True,
        ),

        # Season 1 Episode 8
        # Season 1 Ep 8
        (
            r"\bseason\s*(\d+)\s*(?:episode|ep)\s*(\d+)\b",
            True,
        ),

        # S1 Episode 8
        # S1 Ep 8
        (
            r"\bs(\d+)\s*(?:episode|ep)\s*(\d+)\b",
            True,
        ),
    ]

    for pattern, has_season in patterns:

        match = re.search(
            pattern,
            normalized,
            re.IGNORECASE,
        )

        if match:

            return (
                int(match.group(1)),
                int(match.group(2)),
            )

    # ---------------------------------------------------------
    # Episode-only formats
    # ---------------------------------------------------------

    episode_only_patterns = [
        # 2nd Episode
        # 2nd Ep
        r"\b(\d+)(?:st|nd|rd|th)\s*(?:episode|ep)\b",

        # Episode 2
        # Ep 2
        r"\b(?:episode|ep)\s*(\d+)\b",
    ]

    for pattern in episode_only_patterns:

        match = re.search(
            pattern,
            normalized,
            re.IGNORECASE,
        )

        if match:

            return (
                None,
                int(match.group(1)),
            )

    # No episode information found.
    return (
        None,
        None,
    )


def remove_episode_info(text):
    """
    Remove season/episode information from text.

    This allows the remaining title to be scored separately.
    """

    normalized = re.sub(
        r"[^a-zA-Z0-9]+",
        " ",
        str(text),
    ).strip().lower()

    patterns = [
        # S01E08
        r"\bs\d+\s*e\d+\b",

        # Season 1 Episode 8
        # Season 1 Ep 8
        r"\bseason\s*\d+\s*(?:episode|ep)\s*\d+\b",

        # S1 Episode 8
        # S1 Ep 8
        r"\bs\d+\s*(?:episode|ep)\s*\d+\b",

        # 2nd Episode / 2nd Ep
        r"\b\d+(?:st|nd|rd|th)\s*(?:episode|ep)\b",

        # Episode 2 / Ep 2
        r"\b(?:episode|ep)\s*\d+\b",
    ]

    for pattern in patterns:

        normalized = re.sub(
            pattern,
            " ",
            normalized,
            flags=re.IGNORECASE,
        )

    return " ".join(normalized.split())