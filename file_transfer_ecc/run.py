"""
run.py — Application Entry Point
=================================
Start the Flask development server:
    python run.py

Or using Flask CLI:
    flask --app run:app run --debug
"""

import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Ensure the uploads directory exists at startup
    upload_dir = app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=app.config.get("DEBUG", False),
    )
