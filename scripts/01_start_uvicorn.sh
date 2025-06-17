#!/bin/bash
# Start the FastAPI server using uvicorn
# For development use --reload flag
# For production use --workers flag (commented out by default)

uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload # --workers 4
