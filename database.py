from app import db
from models import Category, FAQ, UserQuery, AdminUser
import logging

logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with tables"""
    try:
        db.create_all()
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        return False

def reset_database():
    """Reset database (drop and recreate all tables)"""
    try:
        db.drop_all()
        db.create_all()
        logger.info("Database reset successfully")
        return True
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        return False
