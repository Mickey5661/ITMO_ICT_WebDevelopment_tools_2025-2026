from sqlalchemy.orm import Session
from app.models.tag import Tag
from app.schemas.tag import TagCreate


def get_tag(db: Session, tag_id: int) -> Tag | None:
    return db.query(Tag).filter(Tag.id == tag_id).first()


def get_tag_by_name(db: Session, name: str) -> Tag | None:
    return db.query(Tag).filter(Tag.name == name).first()


def get_tags(db: Session, skip: int = 0, limit: int = 100) -> list[Tag]:
    return db.query(Tag).offset(skip).limit(limit).all()


def create_tag(db: Session, data: TagCreate) -> Tag:
    tag = Tag(name=data.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag: Tag) -> None:
    db.delete(tag)
    db.commit()
