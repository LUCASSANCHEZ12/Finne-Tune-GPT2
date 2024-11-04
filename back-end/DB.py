import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import json

# Load environment variables from a .env file
load_dotenv()  

# Database configuration using environment variables
db_config = {
    "host": os.getenv('DB_HOST'), 
    "user": os.getenv('DB_USER'),       
    "password":  os.getenv('DB_PASS'),      
    "database":  os.getenv('DB_NAME'), 
    "port": os.getenv('DB_PORT')        
}

# Database URL for SQLAlchemy
URL_DATABASE = os.getenv('DATABASE_URL')

# Create SQLAlchemy engine
engine = create_engine(URL_DATABASE)
# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base class for declarative class definitions
Base = declarative_base()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to check if an SQL query is safe
def is_sql_query_safe(sql_query):
    prohibited_phrases = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
        "EXEC", "--", ";", "/*", "*/", "@@", "@", "CREATE", "SHUTDOWN",
        "GRANT", "REVOKE"
    ]
    for phrase in prohibited_phrases:
        if phrase.lower() in sql_query.lower():
            return False
    return True

# Function to get the database schema as a JSON string
def get_database_schema() -> str:
    connection = None
    try:
        # Establish a connection to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Retrieve all tables in the database
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s", (db_config['database'],))
        tables = cursor.fetchall()

        # Initialize the schema dictionary
        database_schema = {}

        # Retrieve schema information for each table
        for table in tables:
            table_name = table['TABLE_NAME']

            # Get column details for each table
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = %s AND TABLE_SCHEMA = %s
            """, (table_name, db_config['database']))
            columns = cursor.fetchall()

            # Get primary key information
            cursor.execute(f"""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_NAME = %s AND CONSTRAINT_NAME = 'PRIMARY' AND TABLE_SCHEMA = %s
            """, (table_name, db_config['database']))
            primary_keys = cursor.fetchall()

            # Get foreign key information
            cursor.execute(f"""
                SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_NAME = %s AND TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL
            """, (table_name, db_config['database']))
            foreign_keys = cursor.fetchall()

            # Organize the table schema
            database_schema[table_name] = {
                "columns": columns,
                "primary_keys": [key["COLUMN_NAME"] for key in primary_keys],
                "foreign_keys": [
                    {
                        "referenced_table": key["REFERENCED_TABLE_NAME"],
                        "referenced_column": key["REFERENCED_COLUMN_NAME"]
                    } for key in foreign_keys
                ]
            }

        # Convert the schema to JSON
        database_schema_json = json.dumps(database_schema, indent=4)
        return database_schema_json

    except mysql.connector.Error as e:
        print("Error")
        return f"Error: {e}"
        
    finally:
        # Close the cursor and connection
        if connection.is_connected():
            cursor.close()
            connection.close()
