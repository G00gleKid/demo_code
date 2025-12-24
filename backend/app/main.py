from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import participants, meetings, assignments, settings as settings_router, auth, testing

app = FastAPI(
    title="Role Distribution API",
    description="API for agile team role assignment based on participant data",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(participants.router, prefix="/api/participants", tags=["participants"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["meetings"])
app.include_router(assignments.router, prefix="/api/assignments", tags=["assignments"])
app.include_router(settings_router.router)
app.include_router(testing.router, prefix="/api/testing", tags=["testing"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Role Distribution API is running"}
