# Import all the models, so that Base has them before being
# imported by Alembic
from ..db.base_class import Base  # noqa

# Import models in dependency order
from ..models.role import Role  # noqa
from ..models.user import User  # noqa
from ..models.user_role import UserRole  # noqa

# Import all models here that should be registered with SQLAlchemy
__all__ = ["Base", "User", "Role", "UserRole"] 