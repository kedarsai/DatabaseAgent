from typing import List, Dict, Optional

# Define the available database tools
DATABASE_TOOLS = [
    {
        "name": "list_tables",
        "description": "Get a list of all tables in the database. Use this when the user wants to see what tables are available or asks about the database structure in general.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "examples": [
            "Show me all tables",
            "What tables are in the database?",
            "List all available tables",
            "What tables do we have?",
            "Show me the database structure"
        ],
        "keywords": ["list", "all tables", "show tables", "available tables", "database structure", "what tables"]
    },
    {
        "name": "get_table_schema",
        "description": "Get the schema (structure) of a specific table. Use this when the user wants to know about the columns, data types, or structure of a particular table.",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Name of the table to get schema for"
                }
            },
            "required": ["table_name"]
        },
        "examples": [
            "What's the structure of the vendors table?",
            "Show me the columns in customers table",
            "What fields are in the orders table?",
            "Describe the schema of vendors",
            "What's the layout of the customers table?"
        ],
        "keywords": ["structure", "schema", "columns", "fields", "layout", "describe", "what's in", "show columns"]
    },
    {
        "name": "profile_table",
        "description": "Get detailed profiling and statistics of a table. Use this when the user wants to see data quality metrics, statistics, or analysis of a specific table's contents.",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Name of the table to profile"
                }
            },
            "required": ["table_name"]
        },
        "examples": [
            "Give me statistics about the customers table",
            "Profile the vendors table",
            "Show me the data quality of orders",
            "What are the metrics for customers?",
            "Analyze the vendors table"
        ],
        "keywords": ["statistics", "profile", "metrics", "analyze", "data quality", "show stats", "give stats"]
    }
]

def get_tool_schemas() -> List[Dict]:
    """Get the schemas for all available tools"""
    return DATABASE_TOOLS

def get_tool_schema(tool_name: str) -> Optional[Dict]:
    """Get the schema for a specific tool"""
    for tool in DATABASE_TOOLS:
        if tool["name"] == tool_name:
            return tool
    return None 