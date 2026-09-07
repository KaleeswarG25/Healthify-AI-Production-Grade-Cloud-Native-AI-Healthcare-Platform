import uuid
from typing import Generator

from botocore.exceptions import ClientError
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

MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_FILE_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}


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
    file_name: str = Query(..., min_length=1, max_length=255),
    content_type: str = Query(...),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    if content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, JPEG and PNG files are supported",
        )

    extension = ALLOWED_FILE_TYPES[content_type]

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

    except ClientError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to generate upload URL",
        )

    return PresignedUrlResponse(
        upload_url=upload_url,
        file_key=file_key,
        expires_in=300,
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

    except ClientError as exc:
        error_code = exc.response.get(
            "Error",
            {}
        ).get("Code")

        if error_code in {"404", "NoSuchKey", "NotFound"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file does not exist",
            )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify uploaded file",
        )

    file_size = metadata.get("ContentLength", 0)

    if file_size <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    if file_size > MAX_FILE_SIZE:
        try:
            s3_client.delete_object(
                Bucket=BUCKET_NAME,
                Key=request.file_key,
            )
        except ClientError:
            pass

        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the 10 MB limit",
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
        .filter(
            MedicalReport.user_id == user_id
        )
        .order_by(
            MedicalReport.uploaded_at.desc()
        )
        .all()
    )

    return reports


# ============================================================
# DELETE REPORT
# ============================================================

@router.delete(
    "/reports/{report_id}"
)
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

    prefix = f"s3://{BUCKET_NAME}/"

    if not report.s3_url.startswith(prefix):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid stored S3 reference",
        )

    s3_key = report.s3_url[len(prefix):]

    try:
        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
        )

    except ClientError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to delete report from storage",
        )

    db.delete(report)
    db.commit()

    return {
        "message": "Report deleted successfully",
        "report_id": report_id,
    }