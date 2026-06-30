from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Activity(Base):
    
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    action_type = Column(String(50), nullable=False)
    
    description = Column(String(255), nullable=False)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
