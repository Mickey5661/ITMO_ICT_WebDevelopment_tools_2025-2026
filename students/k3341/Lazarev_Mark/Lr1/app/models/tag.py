from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Tag(Base):
    """Тег для задачи (срочно, важно, review и т.д.)."""
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    
    task_associations: Mapped[list["TaskTag"]] = relationship("TaskTag", back_populates="tag")
