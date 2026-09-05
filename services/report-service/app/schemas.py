from datetime import datetime

from pydantic import BaseModel


class PresignedUrlResponse(BaseModel):
    upload_url: str
    file_key: str
    expires_in: int


class SaveReportRequest(BaseModel):
    file_name: str
    file_key: str


class ReportResponse(BaseModel):
    id: int
    file_name: str
    s3_url: str
    user_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True