from . import schemas

from .tools import (
    get_datetime,
    get_system_info,
    loona_search_files,
    loona_open_file,
    loona_open_file_by_query,
    loona_search_applications,
    loona_open_application,
    loona_close_application,
)


def register(ctx):
    ctx.register_tool(
        name="get_datetime",
        toolset="loona_tools",
        schema=schemas.GET_DATETIME,
        handler=get_datetime,
    )

    ctx.register_tool(
        name="get_system_info",
        toolset="loona_tools",
        schema=schemas.GET_SYSTEM_INFO,
        handler=get_system_info,
    )

    ctx.register_tool(
        name="loona_search_files",
        toolset="loona_tools",
        schema=schemas.LOONA_SEARCH_FILES,
        handler=loona_search_files,
    )

    ctx.register_tool(
        name="loona_open_file",
        toolset="loona_tools",
        schema=schemas.LOONA_OPEN_FILE,
        handler=loona_open_file,
    )

    ctx.register_tool(
        name="loona_open_file_by_query",
        toolset="loona_tools",
        schema=schemas.LOONA_OPEN_FILE_BY_QUERY,
        handler=loona_open_file_by_query,
    )

    ctx.register_tool(
        name="loona_search_applications",
        toolset="loona_tools",
        schema=schemas.LOONA_SEARCH_APPLICATIONS,
        handler=loona_search_applications,
    )

    ctx.register_tool(
        name="loona_open_application",
        toolset="loona_tools",
        schema=schemas.LOONA_OPEN_APPLICATION,
        handler=loona_open_application,
    )

    ctx.register_tool(
        name="loona_close_application",
        toolset="loona_tools",
        schema=schemas.LOONA_CLOSE_APPLICATION,
        handler=loona_close_application,
    )