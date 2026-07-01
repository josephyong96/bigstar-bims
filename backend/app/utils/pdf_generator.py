"""PDF generation utilities for purchase orders and other documents."""

from io import BytesIO
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    Image, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_po_pdf(purchase_order) -> bytes:
    """Generate a PDF for a purchase order."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#16213e'),
        spaceAfter=12,
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
    )
    
    # Header
    elements.append(Paragraph("PURCHASE ORDER", title_style))
    elements.append(Spacer(1, 10))
    
    # PO Info
    po_info = [
        [Paragraph("<b>PO Number:</b>", normal_style), Paragraph(purchase_order.po_number, normal_style)],
        [Paragraph("<b>Date:</b>", normal_style), Paragraph(str(purchase_order.created_at.strftime("%Y-%m-%d")), normal_style)],
        [Paragraph("<b>Status:</b>", normal_style), Paragraph(purchase_order.status.upper(), normal_style)],
    ]
    po_table = Table(po_info, colWidths=[40 * mm, 60 * mm])
    po_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(po_table)
    elements.append(Spacer(1, 20))
    
    # Supplier Info
    elements.append(Paragraph("Supplier Information", heading_style))
    supplier_data = [
        [Paragraph("<b>Supplier Name:</b>", normal_style), Paragraph(purchase_order.supplier_name, normal_style)],
    ]
    if purchase_order.notes:
        supplier_data.append([Paragraph("<b>Notes:</b>", normal_style), Paragraph(purchase_order.notes, normal_style)])
    
    supplier_table = Table(supplier_data, colWidths=[40 * mm, 120 * mm])
    supplier_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(supplier_table)
    elements.append(Spacer(1, 20))
    
    # Items Table
    elements.append(Paragraph("Order Items", heading_style))
    
    table_data = [
        [Paragraph("<b>#</b>", normal_style),
         Paragraph("<b>Item</b>", normal_style),
         Paragraph("<b>Quantity</b>", normal_style),
         Paragraph("<b>Unit Price</b>", normal_style),
         Paragraph("<b>Total</b>", normal_style)],
    ]
    
    total = 0
    for i, item in enumerate(purchase_order.po_items, 1):
        item_total = item.quantity * float(item.unit_price)
        total += item_total
        table_data.append([
            Paragraph(str(i), normal_style),
            Paragraph(item.item_name or str(item.item_id), normal_style),
            Paragraph(str(item.quantity), normal_style),
            Paragraph(f"${float(item.unit_price):.2f}", normal_style),
            Paragraph(f"${item_total:.2f}", normal_style),
        ])
    
    # Add total row
    table_data.append([
        Paragraph("", normal_style),
        Paragraph("", normal_style),
        Paragraph("", normal_style),
        Paragraph("<b>Grand Total:</b>", normal_style),
        Paragraph(f"<b>${total:.2f}</b>", normal_style),
    ])
    
    items_table = Table(table_data, colWidths=[15 * mm, 75 * mm, 25 * mm, 30 * mm, 30 * mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -2), 1, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#16213e')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 30))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )
    elements.append(Paragraph("Generated by BIMS - Bigstar Inventory Management System", footer_style))
    
    # Build PDF
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def generate_do_pdf(delivery_order) -> bytes:
    """Generate a PDF for a delivery order."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#16213e'),
        spaceAfter=12,
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
    )
    
    elements.append(Paragraph("DELIVERY ORDER", title_style))
    elements.append(Spacer(1, 10))
    
    do_info = [
        [Paragraph("<b>DO Number:</b>", normal_style), Paragraph(delivery_order.do_number, normal_style)],
        [Paragraph("<b>Date:</b>", normal_style), Paragraph(str(delivery_order.created_at.strftime("%Y-%m-%d")), normal_style)],
        [Paragraph("<b>Status:</b>", normal_style), Paragraph(delivery_order.status.upper(), normal_style)],
        [Paragraph("<b>Priority:</b>", normal_style), Paragraph(delivery_order.priority.upper(), normal_style)],
    ]
    do_table = Table(do_info, colWidths=[40 * mm, 60 * mm])
    do_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(do_table)
    elements.append(Spacer(1, 20))
    
    # Project Info
    elements.append(Paragraph("Project Information", heading_style))
    project_data = [
        [Paragraph("<b>Project:</b>", normal_style), Paragraph(delivery_order.project_name or str(delivery_order.project_id), normal_style)],
    ]
    project_table = Table(project_data, colWidths=[40 * mm, 120 * mm])
    project_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(project_table)
    elements.append(Spacer(1, 20))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )
    elements.append(Paragraph("Generated by BIMS - Bigstar Inventory Management System", footer_style))
    
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
