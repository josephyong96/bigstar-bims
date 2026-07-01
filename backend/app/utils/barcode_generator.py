"""Barcode and QR code generation utilities."""

import io

try:
    import qrcode
    HAS_QR = True
except ImportError:
    HAS_QR = False

try:
    from barcode import Code128
    from barcode.writer import ImageWriter
    HAS_BARCODE = True
except ImportError:
    HAS_BARCODE = False

from fastapi import HTTPException


def generate_qr_code(data: str) -> bytes:
    """Generate QR code image from data string."""
    if not HAS_QR:
        raise HTTPException(status_code=500, detail="QR code generation not available")

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


def generate_barcode(data: str) -> bytes:
    """Generate Code128 barcode image from data string."""
    if not HAS_BARCODE:
        raise HTTPException(status_code=500, detail="Barcode generation not available")

    buffer = io.BytesIO()
    code = Code128(data, writer=ImageWriter())
    code.write(buffer, options={"write_text": True, "module_height": 15})
    buffer.seek(0)
    return buffer.getvalue()


def generate_item_barcode(sku: str) -> bytes:
    """Generate barcode for an item SKU."""
    return generate_barcode(sku)


def generate_item_qrcode(item_id: str, base_url: str = "") -> bytes:
    """Generate QR code linking to an item."""
    data = f"{base_url}/items/{item_id}" if base_url else item_id
    return generate_qr_code(data)
