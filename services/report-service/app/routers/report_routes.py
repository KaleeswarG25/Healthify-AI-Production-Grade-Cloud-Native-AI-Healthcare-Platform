import os
import uuid
from typing import Generator

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import MedicalReport
from app.s3 import BUCKET_NAME, s3_client
from app.schemas import (
    PresignedUrlResponse,
    ReportResponse,
    SaveReportRequest,
)
from app.security import get_current_user


router = APIRouter()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# GENERATE S3 UPLOAD URL
# ============================================================

@router.get(
    "/generate-upload-url",
    response_model=PresignedUrlResponse,
)
async def generate_upload_url(
    file_name: str = Query(...),
    content_type: str = Query(...),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    allowed_types = {
        "application/pdf": ".pdf",
        "image/jpeg": ".jpg",
        "image/png": ".png",
    }

    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, JPEG and PNG files are supported",
        )

    extension = allowed_types[content_type]

    safe_name = os.path.basename(file_name)

    file_key = (
        f"users/{user_id}/reports/"
        f"{uuid.uuid4()}{extension}"
    )

    try:
        upload_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file_key,
                "ContentType": content_type,
            },
            ExpiresIn=300,
        )

        return PresignedUrlResponse(
            upload_url=upload_url,
            file_key=file_key,
            expires_in=300,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to generate upload URL: {str(exc)}",
        )


# ============================================================
# SAVE REPORT METADATA
# ============================================================

@router.post(
    "/save-report",
    response_model=ReportResponse,
)
async def save_report(
    request: SaveReportRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user["user_id"]

    expected_prefix = f"users/{user_id}/reports/"

    if not request.file_key.startswith(expected_prefix):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid report ownership",
        )

    try:
        metadata = s3_client.head_object(
            Bucket=BUCKET_NAME,
            Key=request.file_key,
        )

        file_size = metadata.get("ContentLength", 0)

        max_size = 10 * 1024 * 1024

        if file_size > max_size:
            s3_client.delete_object(
                Bucket=BUCKET_NAME,
                Key=request.file_key,
            )

            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File exceeds the 10 MB limit",
            )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file does not exist",
        )

    report = MedicalReport(
        user_id=user_id,
        file_name=request.file_name,
        s3_url=f"s3://{BUCKET_NAME}/{request.file_key}",
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


# ============================================================
# GET USER REPORTS
# ============================================================

@router.get(
    "/reports",
    response_model=list[ReportResponse],
)
async def get_user_reports(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user["user_id"]

    reports = (
        db.query(MedicalReport)
        .filter(MedicalReport.user_id == user_id)
        .order_by(MedicalReport.uploaded_at.desc())
        .all()
    )

    return reports


# ============================================================
# DELETE REPORT
# ============================================================

@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user["user_id"]

    report = (
        db.query(MedicalReport)
        .filter(
            MedicalReport.id == report_id,
            MedicalReport.user_id == user_id,
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    try:
        s3_key = report.s3_url.split(
            f"s3://{BUCKET_NAME}/",
            1,
        )[1]

        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to delete S3 object: {str(exc)}",
        )

    db.delete(report)
    db.commit()

    return {
        "message": "Report deleted successfully",
        "report_id": report_id,
    }