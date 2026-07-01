import enum
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ShareRole(str, enum.Enum):
    viewer = "viewer"
    editor = "editor"

class ShelfShare(Base):
    __tablename__ = "shelf_shares"

    id = Column(Integer, primary_key=True, index=True)
    shelf_id = Column(Integer, ForeignKey("shelf.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(SAEnum(ShareRole), nullable=False, default=ShareRole.viewer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")
