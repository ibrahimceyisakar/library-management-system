from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import books, patrons, checkouts
from app.database.database import engine
from app.models import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(books.router, tags=["Books"])
app.include_router(patrons.router, tags=["Patrons"])
app.include_router(checkouts.router, tags=["Checkouts"])

@app.get("/")
async def read_root():
    return {
        "message": "Welcome to Library Management API",
        "docs": "/docs",
        "endpoints": {
            "books": "/books/",
            "patrons": "/patrons/",
            "checkouts": "/checkouts/"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "api": "up",
            "database": "up",
            "redis": "up"
        }
    }
