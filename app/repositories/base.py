from typing import Any, Generic, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository class providing generic CRUD operations for SQLAlchemy models."""

    def __init__(self, model: Type[ModelType], db: Session):
        """Initializes the repository with the specified model and db session.

        Args:
            model: The SQLAlchemy model class.
            db: The SQLAlchemy Session instance.
        """
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        """Retrieve a single record by its primary key ID.

        Args:
            id: The primary key of the record.

        Returns:
            The model instance if found, otherwise None.
        """
        return self.db.get(self.model, id)

    def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Retrieve multiple records with offset and limit pagination.

        Args:
            skip: The number of records to skip.
            limit: The maximum number of records to return.

        Returns:
            A list of model instances.
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: Any) -> ModelType:
        """Persist a new model instance in the database.

        Args:
            obj_in: The model instance or a dictionary of parameters to initialize the model.

        Returns:
            The created model instance.
        """
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        else:
            db_obj = obj_in
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: Any) -> ModelType:
        """Update fields of an existing model instance.

        Args:
            db_obj: The existing model instance from the database.
            obj_in: A dictionary of updates or a Pydantic model containing updates.

        Returns:
            The updated model instance.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # Pydantic support
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, id: Any) -> Optional[ModelType]:
        """Remove a record by its primary key.

        Args:
            id: The primary key of the record to remove.

        Returns:
            The removed model instance, or None if not found.
        """
        obj = self.db.get(self.model, id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
        return obj
