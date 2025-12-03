import os
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Read environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")