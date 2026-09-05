from typing import Optional

from sqlalchemy.orm import Session

from app.models import Analysis


def create_analysis(
    db: Session,
    user_id: int,
    report_text: str,
    analysis: str,
    summary: str,
    filename: Optional[str] = None,
) -> str:
    import uuid

    analysis_id = str(uuid.uuid4())

    record = Analysis(
        id=analysis_id,
        user_id=user_id,
        filename=filename,
        report_text=report_text,
        analysis=analysis,
        summary=summary,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return analysis_id


def get_analysis(
    db: Session,
    analysis_id: str,
) -> Optional[Analysis]:
    return (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id)
        .first()
    )


def get_user_analyses(
    db: Session,
    user_id: int,
) -> list:
    records = (
        db.query(Analysis)
        .filter(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
        .all()
    )

    return [
        {
            "id": record.id,
            "filename": record.filename,
            "summary": record.summary,
            "created_at": record.created_at.isoformat(),
        }
        for record in records
    ]


def delete_analysis(
    db: Session,
    analysis_id: str,
    user_id: int,
) -> bool:
    record = (
        db.query(Analysis)
        .filter(
            Analysis.id == analysis_id,
            Analysis.user_id == user_id,
        )
        .first()
    )

    if not record:
        return False

    db.delete(record)
    db.commit()

    return True