import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routers import quiz_agent, qa_agent, grading_agent, kb_agent

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(qa_agent.router)
app.include_router(quiz_agent.router)
app.include_router(grading_agent.router)
app.include_router(kb_agent.router)

# Serve static assets (JS, CSS, images) from the Vue build output
app.mount("/assets", StaticFiles(directory="../frontend/dist/assets"), name="assets")

# Serve index.html at root
@app.get("/")
async def read_index():
    return FileResponse("../frontend/dist/index.html")

@app.get("/health")
def health_check():
    return {"status": "ok"}
