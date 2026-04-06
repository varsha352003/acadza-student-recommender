from fastapi import FastAPI

from app.routes import analyze, recommend


app = FastAPI(
    title="Acadza Student Recommender",
    version="1.0.0",
    description="Personalized learning recommendations and performance analysis for students",
)


# Include routers
app.include_router(analyze.router)
app.include_router(recommend.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Acadza Student Recommender API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
