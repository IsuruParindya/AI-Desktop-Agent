"""
Compatibility layer for the Loona file tools.

The file-search system has been split into dedicated modules:

- index.py      → file indexing
- matching.py   → filename matching and scoring
- episodes.py   → season/episode handling
- paths.py      → path validation

This module re-exports those functions temporarily so existing
imports continue to work during the refactoring process.
"""

from .index import (
    SEARCH_ROOTS,
    IGNORED_DIRECTORIES,
    PREFERRED_EXTENSIONS,
    build_file_index,
)

from .matching import (
    _normalize_text,
    _get_keywords,
    score_title,
    score_file,
)

from .episodes import (
    extract_episode_info,
    remove_episode_info,
)

from .paths import (
    is_allowed_path,
)