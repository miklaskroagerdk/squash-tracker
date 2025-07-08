import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

# Import the database manager
from external_database import ExternalDatabaseManager

# Create an instance of the database manager
db_manager = ExternalDatabaseManager()

# Print the database type and connection string
print(f"Database Type: {db_manager.db_type}")
print(f"Connection String: {db_manager.connection_string}")

# Test the connection
try:
    # Get the engine
    engine = db_manager.get_engine()
    
    # Execute a test query
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"Query result: {result.fetchone()}")
    
    print("Database connection successful!")
except Exception as e:
    print(f"Error connecting to database: {e}")
