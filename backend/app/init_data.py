"""Initialize database with seed data."""

import logging
from sqlalchemy.orm import Session
from uuid import uuid4

from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.location import Location
from app.models.category import Category

logger = logging.getLogger(__name__)


def seed_locations(db: Session) -> None:
    """Create default locations if none exist."""
    if db.query(Location).first():
        return

    locations = [
        Location(id=uuid4(), code="WH-KL-01", name="Main Warehouse KL", location_type="warehouse", address="Kuala Lumpur", is_active=True),
        Location(id=uuid4(), code="REPAIR-01", name="Repair Center", location_type="repair_center", address="Kuala Lumpur", is_active=True),
        Location(id=uuid4(), code="OFFICE-TH", name="Thailand Office", location_type="office", address="Thailand", is_active=True),
        Location(id=uuid4(), code="WH-TH-01", name="Thailand Warehouse", location_type="warehouse", address="Thailand", is_active=True),
    ]
    db.add_all(locations)
    db.commit()
    logger.info(f"Created {len(locations)} default locations")


def seed_admin_user(db: Session) -> None:
    """Create default admin user if none exist."""
    if db.query(User).first():
        return

    admin = User(
        id=uuid4(),
        username="admin",
        email="admin@bigstarled.com.my",
        full_name="System Administrator",
        password_hash=get_password_hash("admin123"),
        role="management",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    logger.info("Created default admin user (username: admin, password: admin123)")


def seed_categories(db: Session) -> None:
    """Create default LED categories if none exist."""
    if db.query(Category).first():
        return

    categories = [
        Category(id=uuid4(), name="LED Module", inventory_type="product", description="LED display modules by pixel pitch"),
        Category(id=uuid4(), name="LED Cabinet", inventory_type="product", description="LED display cabinets and frames"),
        Category(id=uuid4(), name="Controller", inventory_type="product", description="LED display controllers"),
        Category(id=uuid4(), name="Power Supply", inventory_type="product", description="LED power supplies"),
        Category(id=uuid4(), name="Receiving Card", inventory_type="product", description="LED receiving cards"),
        Category(id=uuid4(), name="LCD Display", inventory_type="product", description="LCD displays and monitors"),
        Category(id=uuid4(), name="Media Player", inventory_type="product", description="Digital signage media players"),
        Category(id=uuid4(), name="LED Chip", inventory_type="raw_material", description="LED chips and diodes"),
        Category(id=uuid4(), name="IC Driver", inventory_type="raw_material", description="LED driver ICs"),
        Category(id=uuid4(), name="PCB Board", inventory_type="raw_material", description="Printed circuit boards"),
        Category(id=uuid4(), name="Cable & Connector", inventory_type="raw_material", description="Cables and connectors"),
        Category(id=uuid4(), name="Frame & Structure", inventory_type="raw_material", description="Aluminum frames and structures"),
        Category(id=uuid4(), name="Rental LED Panel", inventory_type="rental_item", description="Rental LED panels"),
        Category(id=uuid4(), name="Rental Controller", inventory_type="rental_item", description="Rental controllers"),
        Category(id=uuid4(), name="Rental Rigging", inventory_type="rental_item", description="Rental rigging equipment"),
    ]
    db.add_all(categories)
    db.commit()
    logger.info(f"Created {len(categories)} default categories")


def main() -> None:
    """Main initialization function."""
    logger.info("Initializing database...")
    init_db()
    db = SessionLocal()
    try:
        seed_locations(db)
        seed_admin_user(db)
        seed_categories(db)
        logger.info("Database initialization complete!")
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
