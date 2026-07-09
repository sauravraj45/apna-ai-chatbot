"""Health check endpoint -- used by Railway and uptime monitors."""

from fastapi import APIRouter

from app.database.session import check_db_connection
from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])

SERVICE_VERSION = "1.0.0"


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Report service and database health. Does not require authentication."""
    db_ok = await check_db_connection()
    return HealthResponse(
        status="ok" if db_ok else "degraded",
        database="connected" if db_ok else "unreachable",
        version=SERVICE_VERSION,
    )
