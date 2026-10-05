import sys
import os
from pathlib import Path

# Ensure application root directory is on Python path for Vercel Serverless
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.main import app

# Vercel serverless entrypoint
app = app
