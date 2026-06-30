from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

# A generic CRUD factory. By passing a Model, a Create Schema, and an Update Schema,
# this class automatically generates the standard database operations (Create, Read, Update, Delete) 
# for that specific model, preventing us from having to rewrite this logic for every table.
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
       
        self.model = model

    def get(self, db: Session, id: int, owner_id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(
            self.model.id == id,
            self.model.owner_id == owner_id
        ).first()

    def get_multi(
        self, db: Session, owner_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).filter(
            self.model.owner_id == owner_id
        ).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType, owner_id: int) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int, owner_id: int) -> ModelType:
        obj = db.query(self.model).filter(
            self.model.id == id,
            self.model.owner_id == owner_id
        ).first()
        db.delete(obj)
        db.commit()
        return obj
