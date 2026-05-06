"""
/review router.
POST /review  — submit a GitHub URL or code snippet for review
GET  /review/{review_id}  — retrieve a previously stored report
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.auth import get_current_user
from app.agents.orchestrator import graph
from app.schemas.models import ReviewRequest, ReviewResponse
from app.utils.blob_storage import upload_report, download_report
import logging

router = APIRouter(prefix="/review", tags=["review"])
logger = logging.getLogger(__name__)


@router.post("", response_model=ReviewResponse)
async def submit_review(
    request: ReviewRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Submit code for multi-agent review.
    Requires a valid Entra ID Bearer token.
    """
    if not request.github_url and not request.code_snippet:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide either github_url or code_snippet.",
        )

    username = current_user.get("preferred_username", "unknown")
    logger.info(f"Review requested by {username} | url={request.github_url}")

    # Run the LangGraph pipeline
    try:
        final_state = await graph.ainvoke({
            "github_url":   request.github_url,
            "code_snippet": request.code_snippet,
            "language":     request.language,
            "raw_code":     "",
            "chunks":       [],
            "filename":     "",
            "security_issues": [],
            "logic_issues":    [],
            "quality_issues":  [],
            "report":          None,
        })
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Review pipeline failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Review pipeline encountered an error. Check server logs.",
        )

    report = final_state["report"]

    # Persist to Azure Blob Storage
    try:
        blob_url = upload_report(report.review_id, report.model_dump(mode="json"))
        report.blob_url = blob_url
    except Exception as e:
        logger.warning(f"Blob upload failed (non-fatal): {e}")

    return ReviewResponse(status="success", report=report)


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Retrieve a previously stored review report by its ID."""
    data = download_report(review_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No report found for review_id: {review_id}",
        )
    from app.schemas.models import ReviewReport
    return ReviewResponse(status="success", report=ReviewReport(**data))
