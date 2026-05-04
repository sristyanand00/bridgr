from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True) # Matches Firebase UID
    email = Column(String, unique=True, index=True)
    name = Column(String)
    quiz_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    target_role = Column(String, nullable=False)
    match_score = Column(Integer, nullable=False)
    feasibility_score = Column(JSON, nullable=True)
    skill_gaps = Column(JSON, nullable=True) # Missing required skills
    matched_skills = Column(JSON, nullable=True)
    roadmap_inputs = Column(JSON, nullable=True) # Data used to generate the roadmap
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    roadmap = relationship("Roadmap", back_populates="analysis", uselist=False, cascade="all, delete-orphan")


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, unique=True)
    target_role = Column(String, nullable=False)
    total_days = Column(Integer, nullable=False)
    phases = Column(JSON, nullable=False)
    summary = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="roadmaps")
    analysis = relationship("Analysis", back_populates="roadmap")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    sender = Column(String, nullable=False) # "user" or "coach"
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="chat_messages")

# Update User model to include chat_messages relationship
User.chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")

