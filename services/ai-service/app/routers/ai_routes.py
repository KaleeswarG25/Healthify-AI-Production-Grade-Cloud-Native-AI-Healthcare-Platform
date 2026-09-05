from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.security import get_current_user
from app.schemas import (
    AnalyzeTextRequest,
    AnalyzeTextResponse,
    ChatRequest,
    ChatResponse,
)
from app.ai_engine import analyze_medical_report, answer_question
from app.pdf_parser import extract_text_from_pdf
from app.report_context import (
    create_analysis,
    get_analysis,
    get_user_analyses,
    delete_analysis,
)


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# ANALYZE TEXT
# ============================================================

@router.post(
    "/analyze-text",
    response_model=AnalyzeTextResponse,
)
async def analyze_text(
    request: AnalyzeTextRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze medical report text.

    The authenticated user's ID is taken from the JWT.
    The client cannot choose another user ID.
    """

    user_id = current_user["user_id"]

    if not request.report_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report text cannot be empty",
        )

    try:
        result = analyze_medical_report(request.report_text)

        analysis_id = create_analysis(
            db=db,
            user_id=user_id,
            report_text=request.report_text,
            analysis=result["analysis"],
            summary=result["summary"],
            filename=request.filename,
        )

        return AnalyzeTextResponse(
            analysis_id=analysis_id,
            analysis=result["analysis"],
            summary=result["summary"],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )


# ============================================================
# ANALYZE PDF
# ============================================================

@router.post(
    "/analyze-pdf",
    response_model=AnalyzeTextResponse,
)
async def analyze_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload and analyze a PDF medical report.
    """

    user_id = current_user["user_id"]

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    try:
        file_content = await file.read()

        # Basic upload protection.
        max_file_size = 10 * 1024 * 1024  # 10 MB

        if len(file_content) > max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="PDF file is too large. Maximum size is 10 MB.",
            )

        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded PDF is empty",
            )

        report_text = extract_text_from_pdf(file_content)

        if not report_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to extract text from PDF",
            )

        result = analyze_medical_report(report_text)

        analysis_id = create_analysis(
            db=db,
            user_id=user_id,
            report_text=report_text,
            analysis=result["analysis"],
            summary=result["summary"],
            filename=file.filename,
        )

        return AnalyzeTextResponse(
            analysis_id=analysis_id,
            analysis=result["analysis"],
            summary=result["summary"],
        )

    except HTTPException:
        raise

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF analysis failed: {str(exc)}",
        )


# ============================================================
# CHAT WITH ANALYSIS
# ============================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ask a question about a previously analyzed report.
    """

    user_id = current_user["user_id"]

    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    analysis = get_analysis(
        db=db,
        analysis_id=request.analysis_id,
    )

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    # Critical authorization check.
    if analysis.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this analysis",
        )

    try:
        response = answer_question(
            question=request.message,
            report_context=analysis.report_text,
            report_analysis=analysis.analysis,
        )

        return ChatResponse(
            response=response,
            analysis_id=analysis.id,
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )


# ============================================================
# ANALYSIS HISTORY
# ============================================================

@router.get("/history")
async def analysis_history(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return analysis history for the authenticated user.
    """

    user_id = current_user["user_id"]

    return {
        "analyses": get_user_analyses(
            db=db,
            user_id=user_id,
        )
    }


# ============================================================
# GET SINGLE ANALYSIS
# ============================================================

@router.get("/analysis/{analysis_id}")
async def get_single_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return a single analysis belonging to the authenticated user.
    """

    user_id = current_user["user_id"]

    analysis = get_analysis(
        db=db,
        analysis_id=analysis_id,
    )

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    if analysis.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this analysis",
        )

    return {
        "id": analysis.id,
        "filename": analysis.filename,
        "report_text": analysis.report_text,
        "analysis": analysis.analysis,
        "summary": analysis.summary,
        "created_at": analysis.created_at,
    }


# ============================================================
# DELETE ANALYSIS
# ============================================================

@router.delete("/analysis/{analysis_id}")
async def remove_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete an analysis belonging to the authenticated user.
    """

    user_id = current_user["user_id"]

    deleted = delete_analysis(
        db=db,
        analysis_id=analysis_id,
        user_id=user_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    return {
        "message": "Analysis deleted successfully",
        "analysis_id": analysis_id,
    }