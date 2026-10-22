import sqlite3
import os


conn = None
cursor = None

database_name = "database.db"
database_path = os.path.join(os.path.dirname(__file__), "..", database_name)

# Establish a connection to the databse
def connect_to_database():
    global conn, cursor
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        return "Connected to SQLite database successfully", 0
    except Exception as e:
        return f"Error connecting to SQLite database: {e}", 1

# Close the connection to the database
def close_database_connection():
    if conn:
        conn.close()
        return "Database connection closed", 0
    return "No active database connection to close", 1

# Initialize the database and create the necessary tables
def initialize_database():
    # Establish what tables should be in the database, and what the tables should contain
    tables = {
        "users": {
            "id": "INTEGER PRIMARY KEY",
            "username": "TEXT NOT NULL",
            "password_hash": "TEXT NOT NULL",
            "created_at": "TEXT NOT NULL"
        }, 
        "sessions": {
            "user_id": "INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE",
            "token": "INTEGER PRIMARY KEY",
            "expires_at": "TEXT NOT NULL"
        }, 
        "chats": {
            "user_id": "INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE",
            "id": "INTEGER PRIMARY KEY",
            "title": "TEXT NOT NULL",
            "context_usage": "INTEGER NOT NULL",
            "created_at": "TEXT NOT NULL",
            "updated_at": "TEXT NOT NULL"
        }, 
        "messages": {
            "chat_id": "INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE",
            "id": "INTEGER PRIMARY KEY",
            "role": "TEXT NOT NULL",
            "content": "TEXT NOT NULL",
            "token_count": "INTEGER",
            "created_at": "TEXT NOT NULL"
        }
    }

    # Ensure a connection is established
    try:
        if conn and cursor:
            # Loop over each table, check if it exists, and create it if it doesn't
            for table in tables.keys():
                query = """
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name=?
                """
                cursor.execute(query, (table,))
                result = cursor.fetchone()
                if not result:
                    create_table(table, tables[table])
            return "Database initialized successfully", 0
        else:
            return "Cannot initialize database: Database connection is not established", 1
    except Exception as e:
        return f"Failed to initialize database: {e}", 1

# Create a table in the database
# The override feature is not really tested, and is not planned to be used much. Test before using
def create_table(table_name, contents, override=False):
    if conn and cursor:
        # Start query
        query = "CREATE TABLE "
        if (override):
            cursor.execute("DROP TABLE IF EXISTS ?;", (table_name,))
            query += f"{table_name}"
        else:
            query += f"IF NOT EXISTS {table_name}"

        # Build the columns
        column_definitions = []
        for col_name, col_type in contents.items():
            column_definitions.append(f"{col_name} {col_type}")
        query += "(" + ", ".join(column_definitions) + ");"

        
        # Execute the query to create the table
        cursor.execute(query)

        # Commit changes
        conn.commit()
    else:
        print("Could not create table: Database connection is not established")