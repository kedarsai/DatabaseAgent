import os
from dotenv import load_dotenv
import pyodbc
from collections import defaultdict

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

    def list_tables(self):
        """List all tables in the current database"""
        if not self.connection:
            if not self.connect():
                return []

        try:
            cursor = self.connection.cursor()
            # Query to get all user tables
            query = """
            SELECT 
                t.name AS TableName,
                s.name AS SchemaName,
                p.rows AS RowCounts
            FROM 
                sys.tables t
            INNER JOIN      
                sys.indexes i ON t.object_id = i.object_id
            INNER JOIN 
                sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
            INNER JOIN 
                sys.schemas s ON t.schema_id = s.schema_id
            WHERE 
                t.is_ms_shipped = 0
            GROUP BY 
                t.name, s.name, p.rows
            ORDER BY 
                t.name;
            """
            
            cursor.execute(query)
            tables = cursor.fetchall()
            
            # Format the results
            table_list = []
            for table in tables:
                table_info = {
                    'name': table.TableName,
                    'schema': table.SchemaName,
                    'row_count': table.RowCounts
                }
                table_list.append(table_info)
            
            return table_list
            
        except Exception as e:
            print(f"Error listing tables: {str(e)}")
            return []
        finally:
            cursor.close()

    def get_table_schema(self, table_name):
        """Get the schema information for a specific table"""
        if not self.connection:
            if not self.connect():
                return None

        try:
            cursor = self.connection.cursor()
            # Query to get column information
            query = """
            SELECT 
                c.name AS ColumnName,
                t.name AS DataType,
                c.max_length AS MaxLength,
                c.precision AS Precision,
                c.scale AS Scale,
                c.is_nullable AS IsNullable,
                CASE WHEN pk.column_id IS NOT NULL THEN 1 ELSE 0 END AS IsPrimaryKey,
                CASE WHEN fk.parent_column_id IS NOT NULL THEN 1 ELSE 0 END AS IsForeignKey,
                CASE WHEN c.is_identity = 1 THEN 1 ELSE 0 END AS IsIdentity,
                c.column_id AS ColumnOrder
            FROM 
                sys.columns c
            INNER JOIN 
                sys.types t ON c.user_type_id = t.user_type_id
            LEFT JOIN 
                (SELECT ic.column_id, ic.object_id
                 FROM sys.index_columns ic
                 INNER JOIN sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id
                 WHERE i.is_primary_key = 1) pk 
                ON c.object_id = pk.object_id AND c.column_id = pk.column_id
            LEFT JOIN 
                sys.foreign_key_columns fk ON c.object_id = fk.parent_object_id AND c.column_id = fk.parent_column_id
            WHERE 
                c.object_id = OBJECT_ID(?)
            ORDER BY 
                c.column_id;
            """
            
            cursor.execute(query, (table_name,))
            columns = cursor.fetchall()
            
            if not columns:
                print(f"Table '{table_name}' not found or no columns available.")
                return None
            
            # Format the results
            schema_info = {
                'table_name': table_name,
                'columns': []
            }
            
            for col in columns:
                column_info = {
                    'name': col.ColumnName,
                    'data_type': col.DataType,
                    'max_length': col.MaxLength,
                    'precision': col.Precision,
                    'scale': col.Scale,
                    'is_nullable': bool(col.IsNullable),
                    'is_primary_key': bool(col.IsPrimaryKey),
                    'is_foreign_key': bool(col.IsForeignKey),
                    'is_identity': bool(col.IsIdentity),
                    'column_order': col.ColumnOrder
                }
                schema_info['columns'].append(column_info)
            
            return schema_info
            
        except Exception as e:
            print(f"Error getting table schema: {str(e)}")
            return None
        finally:
            cursor.close()

    def profile_table(self, table_name):
        """Profile a table with various data quality metrics"""
        if not self.connection:
            if not self.connect():
                return None

        try:
            cursor = self.connection.cursor()
            schema = self.get_table_schema(table_name)
            if not schema:
                return None

            profile_data = {
                'table_name': table_name,
                'total_rows': 0,
                'columns': []
            }

            # Get total row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            profile_data['total_rows'] = cursor.fetchone()[0]

            # Profile each column
            for column in schema['columns']:
                col_name = column['name']
                col_type = column['data_type']
                
                # Initialize column profile
                col_profile = {
                    'name': col_name,
                    'data_type': col_type,
                    'null_count': 0,
                    'null_percentage': 0,
                    'unique_count': 0,
                    'unique_percentage': 0,
                    'min_value': None,
                    'max_value': None,
                    'avg_value': None,
                    'distinct_values': 0
                }

                # Get null count and percentage
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as null_count,
                        COUNT(DISTINCT {col_name}) as distinct_count
                    FROM {table_name}
                    WHERE {col_name} IS NULL
                """)
                null_stats = cursor.fetchone()
                col_profile['null_count'] = null_stats.null_count
                col_profile['null_percentage'] = (null_stats.null_count / profile_data['total_rows']) * 100 if profile_data['total_rows'] > 0 else 0
                col_profile['distinct_values'] = null_stats.distinct_count

                # Get unique count and percentage
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT {col_name}) as unique_count
                    FROM {table_name}
                """)
                unique_count = cursor.fetchone().unique_count
                col_profile['unique_count'] = unique_count
                col_profile['unique_percentage'] = (unique_count / profile_data['total_rows']) * 100 if profile_data['total_rows'] > 0 else 0

                # Get min, max, and avg for numeric columns
                if col_type in ('int', 'bigint', 'decimal', 'numeric', 'float', 'real', 'money', 'smallmoney'):
                    cursor.execute(f"""
                        SELECT 
                            MIN({col_name}) as min_val,
                            MAX({col_name}) as max_val,
                            AVG(CAST({col_name} as float)) as avg_val
                        FROM {table_name}
                    """)
                    numeric_stats = cursor.fetchone()
                    col_profile['min_value'] = numeric_stats.min_val
                    col_profile['max_value'] = numeric_stats.max_val
                    col_profile['avg_value'] = numeric_stats.avg_val

                # Get min and max for string columns
                elif col_type in ('varchar', 'nvarchar', 'char', 'nchar', 'text', 'ntext'):
                    cursor.execute(f"""
                        SELECT 
                            MIN({col_name}) as min_val,
                            MAX({col_name}) as max_val
                        FROM {table_name}
                    """)
                    string_stats = cursor.fetchone()
                    col_profile['min_value'] = string_stats.min_val
                    col_profile['max_value'] = string_stats.max_val

                # Get min and max for date columns
                elif col_type in ('datetime', 'date', 'datetime2', 'datetimeoffset', 'smalldatetime'):
                    cursor.execute(f"""
                        SELECT 
                            MIN({col_name}) as min_val,
                            MAX({col_name}) as max_val
                        FROM {table_name}
                    """)
                    date_stats = cursor.fetchone()
                    col_profile['min_value'] = date_stats.min_val
                    col_profile['max_value'] = date_stats.max_val

                profile_data['columns'].append(col_profile)

            return profile_data

        except Exception as e:
            print(f"Error profiling table: {str(e)}")
            return None
        finally:
            cursor.close() 