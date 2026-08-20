"""
Convenience launcher — lets you start the app with `python run.py`
instead of remembering the uvicorn command.
"""

import uvicorn

from backend.config import PORT

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="localhost", port=PORT, reload=True)
