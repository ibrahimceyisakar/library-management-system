from fastapi import FastAPI, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from app.routes import books, patrons, checkouts, auth
from app.database.database import engine, recreate_database
from app.management_commands.create_superuser import create_superuser
from app.models import models

# Recreate database tables
# recreate_database()
# Create superuser
# create_superuser(
#     email="superuser@example.com",
#     password="admin123"
# )

# Configure OAuth2 security scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    title="Library Management API",
    description="A comprehensive library management system with role-based access control",
    version="1.0.0",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # Hide schemas by default
        "docExpansion": "none"  # Collapse all operations by default
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, tags=["authentication"])
app.include_router(books.router, tags=["books"])
app.include_router(patrons.router, tags=["patrons"])
app.include_router(checkouts.router, tags=["checkouts"])

# Global security
app.swagger_ui_oauth2_redirect_url = "/docs/oauth2-redirect"
app.swagger_ui_parameters = {
    "defaultModelsExpandDepth": -1,
    "docExpansion": "none"
}

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
def health_check():
    return {"status": "healthy"}

# Add security definitions
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Library Management API",
        version="1.0.0",
        description="A comprehensive library management system with role-based access control",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {}
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
