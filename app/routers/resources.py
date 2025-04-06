from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.db.session import get_db
from app.schemas import resource as schemas
from app.schemas.resource import Resource, ResourceCreate
from app.models.models import Resource as DBResource, User
from app.core.security import get_current_user

router = APIRouter(
    
    tags=["🏨 Ресурсы"],
    responses={404: {"description": "Ресурс не найден"}}
)


@router.post(
    "/",
    summary="➕ Создать новый ресурс",
    response_model=schemas.Resource  # Указываем правильную модель ответа
)
def create_resource(
    resource: schemas.ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Создаем объект SQLAlchemy (не путать с Pydantic-схемой!)
    db_resource = DBResource(
        name=resource.name,
        type=resource.type,
        description=resource.description,
        owner_id=current_user.id
    )
    
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    
    # Теперь преобразуем в Pydantic-схему для ответа
    return schemas.Resource.from_orm(db_resource)
@router.get("/",summary="👀 Просмотреть ресурс",response_description="📋 Информация о ресурсе", response_model=List[Resource])
def read_resources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    resources = db.query(DBResource).offset(skip).limit(limit).all()
    return resources

@router.get("/{resource_id}", response_model=schemas.Resource)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    # Загружаем ресурс вместе с бронированиями
    resource = db.query(DBResource)\
                .options(joinedload(DBResource.bookings))\
                .filter(DBResource.id == resource_id)\
                .first()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Ресурс не найден")
    
    return resource

@router.put("/{resource_id}", response_model=Resource)
def update_resource(
    resource_id: int,
    resource: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_resource = db.query(DBResource).filter(DBResource.id == resource_id).first()
    if db_resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    if db_resource.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this resource")
    
    for key, value in resource.dict().items():
        setattr(db_resource, key, value)
    
    db.commit()
    db.refresh(db_resource)
    return db_resource

@router.delete("/{resource_id}")
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_resource = db.query(DBResource).filter(DBResource.id == resource_id).first()
    if db_resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    if db_resource.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this resource")
    
    db.delete(db_resource)
    db.commit()
    return {"message": "Resource deleted successfully"}