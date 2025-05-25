from database import DatabaseConnection

class DatabaseAgent:
    def __init__(self):
        self.db = DatabaseConnection()

    def check_database_connection(self):
        """Check if the database connection is working"""
        return self.db.test_connection()

def main():
    # Create an instance of the agent
    agent = DatabaseAgent()
    
    # Test the database connection
    print("Testing database connection...")
    if agent.check_database_connection():
        print("Agent successfully connected to the database!")
    else:
        print("Agent failed to connect to the database.")

if __name__ == "__main__":
    main()
