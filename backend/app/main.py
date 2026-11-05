from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.routers import auth, destinations, favorites, notifications, reviews, users
from app.schemas.common import ErrorResponse
from app.seed.seed_data import seed_destinations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if not existing and seed destination mock data
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_destinations(db)
        finally:
            db.close()
    except Exception as e:
        print(f"Warning during startup database initialization: {e}")
    yield
    # Shutdown logic if any


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Production-ready REST API for Wanderly Travel Discovery Platform with PostgreSQL and JWT Authentication.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

# CORS Middleware for Web, Android Emulator, and Desktop
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.APP_ENV == "development" else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=exc.detail if isinstance(exc.detail, str) else "Request failed",
            errors=[str(exc.detail)],
        ).model_dump(),
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        msg = f"{field}: {error['msg']}" if field else error["msg"]
        error_messages.append(msg)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            success=False,
            message="Validation error: Please check your input",
            errors=error_messages,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            message="An unexpected internal server error occurred",
            errors=[str(exc)] if settings.DEBUG else [],
        ).model_dump(),
    )


# Health check endpoints
@app.get("/health", tags=["Health"], summary="Root health check")
@app.get(f"{settings.API_V1_PREFIX}/health", tags=["Health"], summary="API v1 health check")
def health_check():
    return {
        "success": True,
        "message": "Wanderly API is healthy and operational",
        "env": settings.APP_ENV,
        "version": "1.0.0",
    }


# Include Routers under API_V1_PREFIX
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(destinations.router, prefix=settings.API_V1_PREFIX)
app.include_router(favorites.router, prefix=settings.API_V1_PREFIX)
app.include_router(reviews.router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)
