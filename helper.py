import logging
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def get_user_or_404(db: Session, model: Any, user_id: int):
    """Fetch a user by id or raise a 404."""
    user = db.get(model, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def commit_and_refresh(db: Session, instance: Any) -> Any:
    """Commit changes and refresh the instance."""
    db.commit()
    db.refresh(instance)
    return instance


def apply_updates(instance: Any, update_model: Any) -> Any:
    """Apply partial updates from a Pydantic model to an ORM instance."""
    for key, value in update_model.model_dump(exclude_unset=True).items():
        setattr(instance, key, value)
    return instance
