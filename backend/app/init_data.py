"""Initialize database with seed data."""

import logging
from uuid import uuid4

logger = logging.getLogger(__name__)


def seed_data(db_session) -> None:
    """Seed initial data if tables are empty."""
    try:
        from app.core.security import get_password_hash
        from app.models.user import User
        from app.models.location import Location
        from app.models.category import Category

        # Seed admin user
        if not db_session.query(User).first():
            admin = User(
                id=uuid4(),
                username="admin",
                email="admin@bigstarled.com.my",
                full_name="System Administrator",
                password_hash=get_password_hash("admin123"),
                role="management",
                is_active=True,
            )
            db_session.add(admin)
            db_session.commit()
            logger.info("Created admin user (admin / admin123)")

        # Seed locations
        if not db_session.query(Location).first():
            locations = [
                Location(id=uuid4(), code="WH-KL-01", name="Main Warehouse KL", location_type="warehouse", address="Kuala Lumpur", is_active=True),
                Location(id=uuid4(), code="REPAIR-01", name="Repair Center", location_type="repair_center", address="Kuala Lumpur", is_active=True),
                Location(id=uuid4(), code="OFFICE-TH", name="Thailand Office", location_type="office", address="Thailand", is_active=True),
                Location(id=uuid4(), code="WH-TH-01", name="Thailand Warehouse", location_type="warehouse", address="Thailand", is_active=True),
            ]
            db_session.add_all(locations)
            db_session.commit()
            logger.info(f"Created {len(locations)} locations")

        # Seed categories
        if not db_session.query(Category).first():
            categories = [
                Category(id=uuid4(), name="LED Module", inventory_type="product", description="LED display modules"),
                Category(id=uuid4(), name="LED Cabinet", inventory_type="product", description="LED display cabinets"),
                Category(id=uuid4(), name="Controller", inventory_type="product", description="LED controllers"),
                Category(id=uuid4(), name="Power Supply", inventory_type="product"),
                Category(id=uuid4(), name="Receiving Card", inventory_type="product"),
                Category(id=uuid4(), name="LCD Display", inventory_type="product"),
                Category(id=uuid4(), name="Media Player", inventory_type="product"),
                Category(id=uuid4(), name="LED Chip", inventory_type="raw_material"),
                Category(id=uuid4(), name="IC Driver", inventory_type="raw_material"),
                Category(id=uuid4(), name="PCB Board", inventory_type="raw_material"),
                Category(id=uuid4(), name="Cable & Connector", inventory_type="raw_material"),
                Category(id=uuid4(), name="Frame & Structure", inventory_type="raw_material"),
                Category(id=uuid4(), name="Rental LED Panel", inventory_type="rental_item"),
                Category(id=uuid4(), name="Rental Controller", inventory_type="rental_item"),
                Category(id=uuid4(), name="Rental Rigging", inventory_type="rental_item"),
            ]
            db_session.add_all(categories)
            db_session.commit()
            logger.info(f"Created {len(categories)} categories")

    except Exception as e:
        db_session.rollback()
        logger.error(f"Seed data error: {e}")
        raise
