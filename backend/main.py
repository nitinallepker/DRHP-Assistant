from fastapi import FastAPI
from api.workspaces import router as workspaces_router
from api.sections import router as sections_router
from api.reviews import router as reviews_router
from api.improvements import router as improvements_router
from api.transformations import router as transformations_router
from database.connection import Base, engine
from fastapi.middleware.cors import CORSMiddleware

# Create SQLite tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI DRHP Operating System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(workspaces_router, prefix="/api")
app.include_router(sections_router, prefix="/api")
app.include_router(reviews_router, prefix="/api")
app.include_router(improvements_router, prefix="/api")
app.include_router(transformations_router, prefix="/api")


@app.get("/")
def home():
    return {
        "message": "AI DRHP Operating System is running."
    }
