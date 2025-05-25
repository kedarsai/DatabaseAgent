from database import DatabaseConnection
from utils import format_table_schema, format_table_profile, format_table_list
from llm import LLMHandler
import json

class DatabaseAgent:
    def __init__(self):
        self.db = DatabaseConnection()
        self.llm = LLMHandler()

    def check_database_connection(self):
        """Check if the database connection is working"""
        return self.db.test_connection()

    def get_database_tables(self):
        """Get list of all tables in the database"""
        tables = self.db.list_tables()
        if not tables:
            print("No tables found or error occurred while fetching tables.")
        return format_table_list(tables)

    def get_table_schema(self, table_name):
        """Get and display the schema of a specific table"""
        schema = self.db.get_table_schema(table_name)
        if not schema:
            print(f"Could not retrieve schema for table '{table_name}'")
        return format_table_schema(schema)

    def profile_table(self, table_name):
        """Profile and display table statistics"""
        profile = self.db.profile_table(table_name)
        if not profile:
            print(f"Could not profile table '{table_name}'")
        return format_table_profile(profile)

    def process_question(self, question: str):
        """Process a natural language question about the database"""
        # First, get list of tables
        tables = self.db.list_tables()
        if not tables:
            print("No tables available to process the question.")
            return

        # Use LLM to determine which operation to perform
        result = self.llm.process_question(question, tables)
        if not result:
            print("Could not determine which operation to perform.")
            return

        # Execute the selected operation
        tool_name = result["tool_name"]
        parameters = json.loads(result["parameters"])

        if tool_name == "list_tables":
            return self.get_database_tables()
        elif tool_name == "get_table_schema":
            return self.get_table_schema(parameters["table_name"])
        elif tool_name == "profile_table":
            return self.profile_table(parameters["table_name"])
        else:
            print(f"Unknown operation: {tool_name}")

def main():
    # Create an instance of the agent
    agent = DatabaseAgent()
    
    # Test the database connection
    print("Testing database connection...")
    if agent.check_database_connection():
        print("Agent successfully connected to the database!")
        
        # Example questions
        questions = [
            "Show me all the tables in the database",
            "What's the structure of the vendors table?",
            "Give me statistics about the customers table",
            "Profile the vendors table"
        ]
        
        # Process each question
        for question in questions:
            print("-----------------question---------------")
            print(f"\nProcessing question: {question}")
            agent.process_question(question)
    else:
        print("Agent failed to connect to the database.")

if __name__ == "__main__":
    main()
