"""Projects router for project management and stock allocation."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import require_any_role, get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.serial_number import SerialNumber
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])

read_role = require_any_role(["management", "project_manager", "sales", "warehouse", "technician"])
write_role = require_any_role(["management", "project_manager"])


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    status: Optional[str] = None,
    client_name: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """List projects with filtering."""
    query = db.query(Project).options(
        joinedload(Project.created_by_user),
    )
    
    if status:
        query = query.filter(Project.status == status)
    if client_name:
        query = query.filter(Project.client_name.ilike(f"%{client_name}%"))
    if search:
        query = query.filter(
            (Project.project_code.ilike(f"%{search}%")) |
            (Project.name.ilike(f"%{search}%"))
        )
    
    projects = query.offset(skip).limit(limit).all()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Create a new project."""
    existing = db.query(Project).filter(Project.project_code == project_data.project_code).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Project code already exists: {project_data.project_code}")
    
    project = Project(**project_data.model_dump(), created_by=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get a single project by ID."""
    project = db.query(Project).options(
        joinedload(Project.created_by_user),
    ).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    update_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Update a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Delete a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return None


@router.get("/{project_id}/stock")
def get_project_stock(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get stock allocated to a specific project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    from app.models.stock import Stock
    from app.models.item import Item
    from app.models.location import Location
    
    stocks = db.query(Stock).filter(Stock.project_id == project_id).all()
    
    return {
        "project_id": project_id,
        "project_code": project.project_code,
        "project_name": project.name,
        "items": [
            {
                "item_id": s.item_id,
                "quantity": s.quantity,
                "reserved": s.reserved_quantity,
            }
            for s in stocks
        ],
    }
