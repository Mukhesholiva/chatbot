# Import base class first
from ..db.base_class import Base

# Import models in dependency order
from .role import Role
from .user import User
from .user_role import UserRole

# Import all models here to ensure they are registered with SQLAlchemy
__all__ = ["Base", "User", "Role", "UserRole"]

# Import all models here for Alembic
from ..db.base import Base