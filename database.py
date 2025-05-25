import os
from dotenv import load_dotenv
import pyodbc

class DatabaseConnection:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get database configuration from environment variables
        self.server = os.getenv('DB_SERVER', 'localhost')
        self.database = os.getenv('DB_NAME', 'master')
        self.trusted_connection = os.getenv('DB_TRUSTED_CONNECTION', 'yes')
        
        # Connection string for Windows Authentication
        self.connection_string = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'Trusted_Connection={self.trusted_connection};'
            f'Connection Timeout=30;'
            f'TrustServerCertificate=yes;'
        )
        
        self.connection = None

    def connect(self):
        """Establish connection to the database"""
        try:
            self.connection = pyodbc.connect(self.connection_string)
            return True
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            return False

    def disconnect(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def test_connection(self):
        """Test the database connection"""
        if self.connect():
            print("Successfully connected to the database!")
            self.disconnect()
            return True
        return False 