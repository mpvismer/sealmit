import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api import projects, artifacts, ai

# Create a new app that mounts the API and serves static files
app = FastAPI(title="SEALMit - ASIG Server")

# Include routers directly to preserve /api prefix
# (Mounting the main app would strip the /api prefix from the request path)
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(artifacts.router, prefix="/api/artifacts", tags=["artifacts"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

# Serve Static Files
# Go up one level from backend/ to root, then into frontend/dist
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

if os.path.exists(frontend_dist):
    # Mount assets directory explicitly
    assets_path = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    
    # Explicit root route
    @app.get("/")
    async def serve_root():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    # Catch-all route for SPA
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # If it's an API call that wasn't caught by the routers (shouldn't happen usually but good safety)
        if full_path.startswith("api/"):
            return {"error": "API path not found"}
            
        # Check if the requested file exists in dist (e.g. vite.svg, favicon.ico)
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Default to index.html for client-side routing
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def root():
        return {"message": "Frontend not built. Please run 'npm run build' in frontend directory."}

if __name__ == "__main__":
    import uvicorn
    # Running on 8083 to avoid conflict with previous stuck process
    uvicorn.run(app, host="0.0.0.0", port=8083)
