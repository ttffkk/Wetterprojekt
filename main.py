from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from web import routers
import os

app = FastAPI()

# API router
app.include_router(routers.router)

# Serve static files (Vue.js build)
static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "frontend"))

# Mount a static directory for assets like CSS, JS, images if they are in a subfolder
# For simplicity, we can assume they are in the root of the 'frontend' folder for now.
# If you have a 'dist/assets' folder, you'd mount that.
# app.mount("/assets", StaticFiles(directory=os.path.join(static_folder, "assets")), name="assets")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """
    Serve the frontend for all non-API routes.
    This allows Vue-router to handle the routing on the client side.
    """
    # Path to the index.html file
    index_path = os.path.join(static_folder, "index.html")

    # Sanitize and resolve the file path
    file_path = os.path.abspath(os.path.join(static_folder, full_path))

    # Check for path traversal attempts
    if not file_path.startswith(static_folder):
        return FileResponse(index_path)

    # Check if the requested path corresponds to an existing file in the static folder
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    # For any other path, return the main index.html to let the client-side router handle it
    return FileResponse(index_path)

# The root path should also serve the index.html
@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_folder, "index.html"))
