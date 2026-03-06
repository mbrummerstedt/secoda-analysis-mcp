from typing import Annotated, Optional

from pydantic import Field

from core.client import call_tool
from core.config import INTEGRATION_ID as _DEFAULT_INTEGRATION_ID


# --------------------------------
# Entity and Utility Tools
# --------------------------------


def run_sql(
    query: Annotated[str, Field(description="The SQL query to execute")],
    integration_id: Annotated[Optional[str], Field(description="The Secoda integration ID for the data warehouse connection. Defaults to the INTEGRATION_ID environment variable if set.")] = _DEFAULT_INTEGRATION_ID,
    truncate_length: Annotated[Optional[float], Field(ge=1, description="Maximum characters for text fields in results. Set to None for full numeric results")] = 150
) -> str:
    """
    Run a SQL query on the data warehouse directly via Secoda.

    Always use LIMIT on exploratory queries. Apply all date filters and conditions
    in the SQL itself, not in search queries.

    Args:
        query: The SQL query to execute
        integration_id: The Secoda integration ID for the warehouse connection.
            Defaults to the INTEGRATION_ID environment variable if set.
        truncate_length: Maximum characters for text fields in results (default: 150).
            Set to None for full numeric results.

    Returns:
        Query results with text fields truncated to specified length
    """
    # Convert float parameters to int
    if truncate_length is not None:
        truncate_length = int(truncate_length)

    return call_tool("run_sql", {"query": query, "integration_id": integration_id, "truncate_length": truncate_length})


def retrieve_entity(
    entity_id: Annotated[str, Field(description="The ID of the entity to retrieve")],
    truncate_length: Annotated[Optional[float], Field(ge=1, description="Maximum characters for text fields in results. Often useful to set to None when you need full descriptions/definitions")] = 150
) -> str:
    """
    Retrieve an entity from the database.
    
    Args:
        entity_id: The ID of the entity to retrieve
        truncate_length: Maximum characters for text fields in results (default: 150)
            Often useful to set to None when you need full descriptions/definitions
    
    Returns:
        Entity details with text fields truncated to specified length
    """
    # Convert float parameters to int
    if truncate_length is not None:
        truncate_length = int(truncate_length)
    
    return call_tool("retrieve_entity", {"entity_id": entity_id, "truncate_length": truncate_length})


def entity_lineage(
    entity_id: Annotated[str, Field(description="The ID of the entity to get lineage for")],
    truncate_length: Annotated[Optional[float], Field(ge=1, description="Maximum characters for text fields in results")] = 150
) -> str:
    """
    Retrieve the lineage of an entity.
    
    Args:
        entity_id: The ID of the entity to get lineage for
        truncate_length: Maximum characters for text fields in results (default: 150)
    
    Returns:
        Entity lineage with text fields truncated to specified length
    """
    # Convert float parameters to int
    if truncate_length is not None:
        truncate_length = int(truncate_length)
    
    return call_tool("entity_lineage", {"entity_id": entity_id, "truncate_length": truncate_length})


def glossary(
    truncate_length: Annotated[Optional[float], Field(ge=1, description="Maximum characters for text fields in results")] = 150
) -> str:
    """
    Retrieve the glossary.
    
    Args:
        truncate_length: Maximum characters for text fields in results (default: 150)
    
    Returns:
        Glossary with text fields truncated to specified length
    """
    # Convert float parameters to int
    if truncate_length is not None:
        truncate_length = int(truncate_length)
    
    return call_tool("glossary", {"truncate_length": truncate_length})


# --------------------------------
# Registration
# --------------------------------


def register_tools(mcp):
    """Register all entity and utility tools with the MCP server."""
    mcp.tool()(run_sql)
    mcp.tool()(retrieve_entity)
    mcp.tool()(entity_lineage)
    mcp.tool()(glossary)


