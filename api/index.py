import sys
import os

# Add the root directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import the FastAPI app instance
from backend.main import app
