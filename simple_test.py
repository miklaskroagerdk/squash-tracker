import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print environment variables
print(f"DB_TYPE: {os.getenv('DB_TYPE')}")
print(f"DB_CONNECTION_STRING: {os.getenv('DB_CONNECTION_STRING')}")
