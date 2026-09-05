from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from .database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(
        String(36),
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    filename = Column(
        String(255),
        nullable=True,
    )

    report_text = Column(
        Text,
        nullable=False,
    )

    analysis = Column(
        Text,
        nullable=False,
    )

    summary = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )