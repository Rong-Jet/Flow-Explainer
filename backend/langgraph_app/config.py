# Configuration for the langgraph agent
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in the backend directory
backend_dir = Path(__file__).resolve().parent.parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

# OpenAI API configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")  # Get from .env or environment variable
if not OPENAI_API_KEY:
    import warnings
    warning_message = """
    ⚠️ OPENAI_API_KEY not found in .env file or environment variables. ⚠️
    
    The application requires an OpenAI API key to function correctly.
    
    To set the API key:
    
    1. Get an API key from https://platform.openai.com/account/api-keys
    
    2. Option A: Create a .env file in the backend directory with:
       OPENAI_API_KEY="your-api-key-here"
       
       You can copy the .env.template file as a starting point:
       cp .env.template .env
    
    3. Option B: Set it as an environment variable:
       - Linux/macOS: export OPENAI_API_KEY="your-api-key-here"
       - Windows Command Prompt: set OPENAI_API_KEY=your-api-key-here
       - Windows PowerShell: $env:OPENAI_API_KEY="your-api-key-here"
    
    4. Restart the application
    """
    warnings.warn(warning_message)
    print(warning_message, file=sys.stderr)

DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "gpt-4-turbo")
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.1"))

# Agent configuration
MAX_ITERATIONS = 5
