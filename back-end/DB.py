import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import json

load_dotenv()  

db_config = {
    "host": os.getenv('DB_HOST'), 
    "user": os.getenv('DB_USER'),       
    "password":  os.getenv('DB_PASS'),      
    "database":  os.getenv('DB_NAME'), 
    "port": os.getenv('DB_PORT')        
}

URL_DATABASE = os.getenv('DATABASE_URL')

engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

def get_database_schema() -> str:
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Retrieve All Tables
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s", (db_config['database'],))
        tables = cursor.fetchall()

        # Initialize the schema dictionary
        database_schema = {}

        # Retrieve Schema Information for Each Table
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

        # Convert the Schema to JSON
        database_schema_json = json.dumps(database_schema, indent=4)
        return database_schema_json

    except mysql.connector.Error as e:
        print("Erro")
        return f"Error: {e}"
        

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()