from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int, owner_id: int) -> Category | None:
    return db.query(Category).filter(
        Category.id == category_id, Category.owner_id == owner_id
    ).first()


def get_categories(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> list[Category]:
    return db.query(Category).filter(Category.owner_id == owner_id).offset(skip).limit(limit).all()


def create_category(db: Session, data: CategoryCreate, owner_id: int) -> Category:
    category = Category(**data.model_dump(), owner_id=owner_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: Category, data: CategoryUpdate) -> Category:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category) -> None:
    db.delete(category)
    db.commit()
