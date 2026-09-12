"""Health-check route for service monitoring and local setup verification."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return the current API service status."""
    return {"status": "ok", "service": "AI Document Screening System"}
