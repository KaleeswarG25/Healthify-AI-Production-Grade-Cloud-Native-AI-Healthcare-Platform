# ai-service/app/routers/ai_routes.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
import os

from app.schemas import (
    AnalyzeTextRequest, AnalyzeTextResponse,
    ChatRequest, ChatResponse
)
from app.ai_engine import analyze_medical_report, answer_question
from app.pdf_parser import extract_text_from_pdf
from app.report_context import (
    create_analysis, get_analysis, set_active_analysis,
    get_active_analysis, clear_session, get_user_analyses, active_sessions
)

router = APIRouter()

@router.post("/analyze-text", response_model=AnalyzeTextResponse)
async def analyze_text(request: AnalyzeTextRequest):
    """
    Analyze medical report text
    """
    try:
        # Get AI analysis
        result = analyze_medical_report(request.report_text)
        
        # Store in memory
        analysis_id = create_analysis(
            user_id=request.user_id,
            report_text=request.report_text,
            analysis=result["analysis"],
            summary=result["summary"],
            filename=request.filename
        )
        
        # Set as active for this user
        set_active_analysis(request.user_id, analysis_id)
        
        return {
            "analysis_id": analysis_id,
            "analysis": result["analysis"],
            "summary": result["summary"]
        }
        
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        raise HTTPException(status_code=503, detail="AI inference is temporarily unavailable") from e

@router.post("/analyze-pdf")
async def analyze_pdf(
    user_id: int = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload and analyze a PDF report
    """
    try:
        # Read file content
        content = await file.read()
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(content)
        
        if "Error" in extracted_text:
            raise HTTPException(status_code=400, detail=extracted_text)
        
        # Get AI analysis
        result = analyze_medical_report(extracted_text)
        
        # Store in memory
        analysis_id = create_analysis(
            user_id=user_id,
            report_text=extracted_text,
            analysis=result["analysis"],
            summary=result["summary"],
            filename=file.filename
        )
        
        # Set as active for this user
        set_active_analysis(user_id, analysis_id)
        
        return {
            "analysis_id": analysis_id,
            "filename": file.filename,
            "analysis": result["analysis"],
            "summary": result["summary"]
        }
        
    except Exception as e:
        print(f"❌ PDF Analysis error: {str(e)}")
        raise HTTPException(status_code=503, detail="AI inference is temporarily unavailable") from e

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat about a previously analyzed report
    """
    try:
        # Get the analysis
        analysis = get_analysis(request.analysis_id)
        
        if not analysis:
            raise HTTPException(
                status_code=404, 
                detail="Analysis not found or expired. Please analyze the report again."
            )
        
        # Verify user owns this analysis
        if analysis["user_id"] != request.user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Set as active for this user
        set_active_analysis(request.user_id, request.analysis_id)
        
        # Get AI response
        response = answer_question(
            question=request.message,
            report_context=analysis["report_text"],
            report_analysis=analysis["analysis"]
        )
        
        return {
            "response": response,
            "analysis_id": request.analysis_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        raise HTTPException(status_code=503, detail="AI inference is temporarily unavailable") from e

@router.get("/active/{user_id}")
async def get_active(user_id: int):
    """
    Get active analysis for a user
    """
    analysis = get_active_analysis(user_id)
    if analysis:
        return {
            "active": True,
            "analysis_id": active_sessions.get(user_id),
            "summary": analysis["summary"]
        }
    return {"active": False}

@router.get("/history/{user_id}")
async def get_history(user_id: int):
    """
    Get all analyses for a user
    """
    analyses = get_user_analyses(user_id)
    return analyses

@router.delete("/session/{user_id}")
async def clear_session_endpoint(user_id: int):
    """
    Clear user's active session
    """
    from app.report_context import clear_session
    clear_session(user_id)
    return {"message": "Session cleared"}

@router.get("/analysis/{analysis_id}")
async def get_analysis_by_id(analysis_id: str, user_id: int):
    """
    Get specific analysis by ID
    """
    analysis = get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": analysis_id,
        "filename": analysis.get("filename"),
        "analysis": analysis["analysis"],
        "summary": analysis["summary"],
        "created_at": analysis["created_at"]
    }