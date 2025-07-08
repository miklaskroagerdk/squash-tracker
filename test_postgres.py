import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection string
db_connection_string = os.getenv('DB_CONNECTION_STRING')
print(f"Connection string: {db_connection_string}")

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(db_connection_string)
    
    # Create a cursor
    cur = conn.cursor()
    
    # Execute a test query
    cur.execute("SELECT version();")
    
    # Get the result
    version = cur.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
    print("PostgreSQL connection successful!")
except Exception as e:
    print(f"Error connecting to PostgreSQL: {e}")
