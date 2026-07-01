"""Utility functions for generating reference numbers."""

from datetime import datetime

from sqlalchemy.orm import Session


def generate_po_number(db: Session) -> str:
    """Generate a unique purchase order number: PO-YYYYMMDD-XXXX"""
    from app.models.purchase_order import PurchaseOrder
    
    date_prefix = datetime.utcnow().strftime("PO-%Y%m%d")
    
    # Find the latest PO number for today
    latest = db.query(PurchaseOrder).filter(
        PurchaseOrder.po_number.like(f"{date_prefix}%")
    ).order_by(PurchaseOrder.po_number.desc()).first()
    
    if latest:
        # Extract the sequence number and increment
        seq = int(latest.po_number.split("-")[-1]) + 1
    else:
        seq = 1
    
    return f"{date_prefix}-{seq:04d}"


def generate_do_number(db: Session) -> str:
    """Generate a unique delivery order number: DO-YYYYMMDD-XXXX"""
    from app.models.delivery_order import DeliveryOrder
    
    date_prefix = datetime.utcnow().strftime("DO-%Y%m%d")
    
    latest = db.query(DeliveryOrder).filter(
        DeliveryOrder.do_number.like(f"{date_prefix}%")
    ).order_by(DeliveryOrder.do_number.desc()).first()
    
    if latest:
        seq = int(latest.do_number.split("-")[-1]) + 1
    else:
        seq = 1
    
    return f"{date_prefix}-{seq:04d}"


def generate_ticket_number(db: Session) -> str:
    """Generate a unique repair ticket number: RT-YYYYMMDD-XXXX"""
    from app.models.repair_ticket import RepairTicket
    
    date_prefix = datetime.utcnow().strftime("RT-%Y%m%d")
    
    latest = db.query(RepairTicket).filter(
        RepairTicket.ticket_number.like(f"{date_prefix}%")
    ).order_by(RepairTicket.ticket_number.desc()).first()
    
    if latest:
        seq = int(latest.ticket_number.split("-")[-1]) + 1
    else:
        seq = 1
    
    return f"{date_prefix}-{seq:04d}"
