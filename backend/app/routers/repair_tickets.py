"""Repair Tickets router for repair/service workflow management."""

from typing import Optional, Dict, Any, List
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import require_any_role, get_current_user
from app.models.user import User
from app.models.repair_ticket import RepairTicket
from app.schemas.repair_ticket import (
    RepairTicketCreate, RepairTicketUpdate, RepairTicketResponse, RepairTicketFilter,
)

router = APIRouter(prefix="/repair-tickets", tags=["Repair Tickets"])

read_role = require_any_role(["management", "project_manager", "sales", "warehouse", "technician"])
write_role = require_any_role(["management", "technician"])


@router.get("", response_model=list[RepairTicketResponse])
def list_repair_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    item_id: Optional[UUID] = None,
    assigned_to: Optional[UUID] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """List repair tickets with filtering."""
    query = db.query(RepairTicket).options(
        joinedload(RepairTicket.item),
        joinedload(RepairTicket.reported_by_user),
        joinedload(RepairTicket.assigned_to_user),
    )
    
    if status:
        query = query.filter(RepairTicket.status == status)
    if priority:
        query = query.filter(RepairTicket.priority == priority)
    if item_id:
        query = query.filter(RepairTicket.item_id == item_id)
    if assigned_to:
        query = query.filter(RepairTicket.assigned_to == assigned_to)
    if search:
        query = query.filter(RepairTicket.ticket_number.ilike(f"%{search}%"))
    
    tickets = query.offset(skip).limit(limit).all()
    return [RepairTicketResponse.model_validate(t) for t in tickets]


@router.post("", response_model=RepairTicketResponse, status_code=status.HTTP_201_CREATED)
def create_repair_ticket(
    ticket_data: RepairTicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Create a new repair ticket."""
    from app.utils.reference_numbers import generate_ticket_number
    
    ticket = RepairTicket(
        **ticket_data.model_dump(),
        ticket_number=generate_ticket_number(db),
        reported_by=current_user.id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return RepairTicketResponse.model_validate(ticket)


@router.get("/{ticket_id}", response_model=RepairTicketResponse)
def get_repair_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get a single repair ticket by ID."""
    ticket = db.query(RepairTicket).options(
        joinedload(RepairTicket.item),
        joinedload(RepairTicket.reported_by_user),
        joinedload(RepairTicket.assigned_to_user),
    ).filter(RepairTicket.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Repair ticket not found")
    
    return RepairTicketResponse.model_validate(ticket)


@router.put("/{ticket_id}", response_model=RepairTicketResponse)
def update_repair_ticket(
    ticket_id: UUID,
    update_data: RepairTicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Update a repair ticket."""
    ticket = db.query(RepairTicket).filter(RepairTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Repair ticket not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(ticket, key, value)
    
    db.commit()
    db.refresh(ticket)
    return RepairTicketResponse.model_validate(ticket)


@router.patch("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: UUID,
    status_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Update repair ticket status."""
    ticket = db.query(RepairTicket).filter(RepairTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Repair ticket not found")
    
    new_status = status_update.get("status")
    if new_status not in ["open", "in_progress", "on_hold", "resolved", "closed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    ticket.status = new_status
    if new_status == "resolved":
        ticket.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(ticket)
    return {"id": ticket.id, "status": ticket.status, "message": f"Status updated to {new_status}"}


@router.patch("/{ticket_id}/assign")
def assign_ticket(
    ticket_id: UUID,
    assign_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Assign a repair ticket to a technician."""
    ticket = db.query(RepairTicket).filter(RepairTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Repair ticket not found")
    
    assigned_to = assign_data.get("assigned_to")
    ticket.assigned_to = assigned_to
    ticket.status = "in_progress"
    
    db.commit()
    db.refresh(ticket)
    return {"id": ticket.id, "assigned_to": assigned_to, "status": ticket.status}


from datetime import datetime
