def format_table_schema(schema):
    """Format and display table schema information"""
    if not schema:
        return None
        
    print(f"\nSchema for table '{schema['table_name']}':")
    print("-" * 80)
    print(f"{'Column Name':<20} {'Data Type':<15} {'Nullable':<10} {'Primary Key':<12} {'Foreign Key':<12} {'Identity':<10}")
    print("-" * 80)
    
    for column in schema['columns']:
        print(f"{column['name']:<20} "
              f"{column['data_type']:<15} "
              f"{'Yes' if column['is_nullable'] else 'No':<10} "
              f"{'Yes' if column['is_primary_key'] else 'No':<12} "
              f"{'Yes' if column['is_foreign_key'] else 'No':<12} "
              f"{'Yes' if column['is_identity'] else 'No':<10}")
    print("-" * 80)
    return schema

def format_table_profile(profile):
    """Format and display table profile information"""
    if not profile:
        return None
        
    print(f"\nProfile for table '{profile['table_name']}':")
    print(f"Total Rows: {profile['total_rows']}")
    print("\nColumn Statistics:")
    print("-" * 100)
    print(f"{'Column':<20} {'Type':<12} {'Null %':<10} {'Unique %':<10} {'Min':<15} {'Max':<15} {'Avg':<15}")
    print("-" * 100)
    
    for col in profile['columns']:
        # Format min, max, avg values based on data type
        min_val = str(col['min_value'])[:15] if col['min_value'] is not None else 'N/A'
        max_val = str(col['max_value'])[:15] if col['max_value'] is not None else 'N/A'
        avg_val = f"{col['avg_value']:.2f}" if col['avg_value'] is not None else 'N/A'
        
        print(f"{col['name']:<20} "
              f"{col['data_type']:<12} "
              f"{col['null_percentage']:>6.2f}%  "
              f"{col['unique_percentage']:>6.2f}%  "
              f"{min_val:<15} "
              f"{max_val:<15} "
              f"{avg_val:<15}")
    print("-" * 100)
    return profile

def format_table_list(tables):
    """Format and display list of tables"""
    if not tables:
        return None
        
    print("\nDatabase Tables:")
    print("-" * 50)
    for table in tables:
        print(f"Table: {table['schema']}.{table['name']}")
        print(f"Row Count: {table['row_count']}")
        print("-" * 50)
    return tables 