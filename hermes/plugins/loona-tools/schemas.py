GET_DATETIME = {
    "name": "get_datetime",
    "description": "Gets the current date, time, and timezone directly from the user's Windows PC.",
    "parameters": {
        "type": "object",
        "properties": {
            "include_timezone": {
                "type": "boolean",
                "description": "Whether to include the timezone information.",
                "default": True,
            }
        },
        "required": [],
    },
}


GET_SYSTEM_INFO = {
    "name": "get_system_info",
    "description": "Gets basic hardware and operating system information directly from the user's Windows PC, including CPU, RAM, GPU, Windows version, architecture, and disk space.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}


LOONA_SEARCH_FILES = {
    "name": "loona_search_files",
    "description": (
        "Searches the user's LOCAL Windows PC for files on the D: and E: drives. "
        "Use this when the user asks to find, locate, or search for a local file, "
        "movie, video, document, song, image, or other file. "
        "Do NOT use web search for local PC file requests. "
        "Supports partial names and small spelling mistakes."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The name or keywords of the local file the user wants to find. "
                    "For example: 'World War Z', 'Avngers', 'thesis', or 'vacation'."
                ),
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of matching files to return.",
                "default": 10,
            },
        },
        "required": ["query"],
    },
}


LOONA_SEARCH_APPLICATIONS = {
    "name": "loona_search_applications",
    "description": (
        "Searches the user's Windows PC for installed applications. "
        "Use this when the user asks to find, locate, or identify an "
        "application installed on their PC. "
        "Do not use web search for installed application requests."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The name of the Windows application to find. "
                    "Examples: Chrome, VS Code, Discord, VLC, Spotify."
                ),
            },
        },
        "required": ["query"],
    },
}

LOONA_OPEN_APPLICATION = {
    "name": "loona_open_application",
    "description": (
        "Opens a Windows application using a verified executable path "
        "returned by loona_search_applications."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": (
                    "The full executable path of the application "
                    "returned by loona_search_applications."
                ),
            },
        },
        "required": ["path"],
    },
}


LOONA_CLOSE_APPLICATION = {
    "name": "loona_close_application",
    "description": (
        "Closes a running Windows application by its executable process name. "
        "Use this when the user asks to close an application. "
        "Do not use force termination."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "process_name": {
                "type": "string",
                "description": (
                    "The executable process name of the application. "
                    "Examples: chrome.exe, discord.exe, notepad.exe."
                ),
            },
        },
        "required": ["process_name"],
    },
}


LOONA_OPEN_FILE = {
    "name": "loona_open_file",
    "description": (
        "Opens a specific LOCAL file on the user's Windows PC. "
        "Use this when an exact local file path is already known. "
        "Do NOT use web search for local files."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The exact local Windows file path.",
            },
        },
        "required": ["path"],
    },
}


LOONA_OPEN_FILE_BY_QUERY = {
    "name": "loona_open_file_by_query",
    "description": (
        "OPENS a LOCAL file on the user's Windows PC by searching the D: and E: "
        "drives and opening the best matching result. "
        "Use this when the user asks to open, launch, play, or view a local "
        "file, movie, video, song, document, image, or other file by name. "
        "Examples: 'open World War Z', 'play Avengers', 'open my thesis', "
        "'open that video'. "
        "This is specifically for files stored on the user's PC. "
        "Do NOT use web search for these requests."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The name or keywords of the local file, movie, video, song, "
                    "document, image, or other file the user wants to open."
                ),
            },
        },
        "required": ["query"],
    },
}