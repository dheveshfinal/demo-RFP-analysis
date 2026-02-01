# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from components.RFP_document import router as RFP_router

app = FastAPI()

# Enable CORS
# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(RFP_router)

# Root endpoint
@app.get("/")
def root():
    return {"message": "RFP Analysis API is running", "status": "healthy"}


# Run this if executing main.py directly
if __name__ == "__main__":
    import uvicorn
    # Use reload=False on Windows to avoid the spawn error
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False  # Set to False for Windows
    )