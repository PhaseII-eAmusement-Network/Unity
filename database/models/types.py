import datetime
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    ForeignKey,
    Text,
    JSON,
    DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class Team(Base):
    __tablename__ = "team"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    owner: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default={})
    applications = relationship("Application", back_populates="team_rel")
    members = relationship("TeamMember", back_populates="team_member_rel")

class TeamMember(Base):
    __tablename__ = "team_member"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    team: Mapped[int] = mapped_column(
        Integer, ForeignKey("team.id"), nullable=False
    )
    team_member_rel = relationship("Team", back_populates="members")

class Application(Base):
    __tablename__ = "application"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team: Mapped[int] = mapped_column(
        Integer, ForeignKey("team.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    oauth_enable: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default={})
    team_rel = relationship("Team", back_populates="applications")
    webhooks = relationship("Webhook", back_populates="application_rel")

class Webhook(Base):
    __tablename__ = "webhook"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    app_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("application.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    event: Mapped[str] = mapped_column(String(255), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default={})
    application_rel = relationship("Application", back_populates="webhooks")
    registrations = relationship("Registration", back_populates="webhook_rel")

class Registration(Base):
    __tablename__ = "registration"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    webhook_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("webhook.id"), nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    arcade_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    endpoint: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    webhook_rel = relationship("Webhook", back_populates="registrations")

class WebhookLog(Base):
    __tablename__ = "webhook_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    webhook_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("webhook.id"), nullable=False
    )
    registration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("registration.id"), nullable=False
    )
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    response_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
    webhook = relationship("Webhook")
    registration = relationship("Registration")