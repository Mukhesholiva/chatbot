from sqlalchemy.orm import Session
import logging
from .session import SessionLocal
from ..services.user_service import UserService
from ..schemas.user import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test database connection and create a test user."""
    db = SessionLocal()
    try:
        # Create a test user
        test_user = UserCreate(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            mobile_number="+1234567890",
            role="test_user",
            organization_id="test_org_001",
            status="active"
        )
        
        # Try to create the user
        created_user = UserService.create_user(db, test_user)
        logger.info(f"Test user created successfully with ID: {created_user.id}")
        
        # Clean up - delete the test user
        UserService.delete_user(db, created_user.id)
        logger.info("Test user deleted successfully")
        
        logger.info("Database connection test completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Error during database test: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_connection() 