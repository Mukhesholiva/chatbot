from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from ..models.role import Role
from ..models.user_role import UserRole
from ..schemas.role import RoleCreate, RoleUpdate, UserRoleCreate

class RoleService:
    @staticmethod
    def get_role_by_id(db: Session, role_id: str) -> Optional[Role]:
        return db.query(Role).filter(Role.id == role_id).first()

    @staticmethod
    def get_role_by_name(db: Session, name: str, org_id: Optional[str] = None) -> Optional[Role]:
        query = db.query(Role).filter(Role.name == name)
        if org_id:
            query = query.filter(Role.org_id == org_id)
        return query.first()

    @staticmethod
    def get_roles_by_org(db: Session, org_id: str) -> List[Role]:
        return db.query(Role).filter(Role.org_id == org_id).all()

    @staticmethod
    def get_global_roles(db: Session) -> List[Role]:
        return db.query(Role).filter(Role.org_id.is_(None)).all()

    @staticmethod
    def get_all_roles(db: Session) -> List[Role]:
        return db.query(Role).all()

    @staticmethod
    def create_role(db: Session, role: RoleCreate, current_user_id: str) -> Role:
        db_role = Role(
            name=role.name,
            description=role.description,
            org_id=role.org_id,
            permissions=role.permissions,
            status=role.status,
            created_by=current_user_id,
            modified_by=current_user_id
        )
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role

    @staticmethod
    def update_role(db: Session, role_id: str, role_update: RoleUpdate, current_user_id: str) -> Optional[Role]:
        db_role = RoleService.get_role_by_id(db, role_id)
        if db_role:
            update_data = role_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_role, field, value)
            db_role.modified_by = current_user_id
            db_role.modified_at = datetime.utcnow()
            db.commit()
            db.refresh(db_role)
        return db_role

    @staticmethod
    def delete_role(db: Session, role_id: str) -> bool:
        db_role = RoleService.get_role_by_id(db, role_id)
        if db_role:
            db.delete(db_role)
            db.commit()
            return True
        return False

    @staticmethod
    def assign_role_to_user(db: Session, user_role: UserRoleCreate, assigned_by: str) -> UserRole:
        db_user_role = UserRole(
            user_id=user_role.user_id,
            role_id=user_role.role_id,
            assigned_by=assigned_by
        )
        db.add(db_user_role)
        db.commit()
        db.refresh(db_user_role)
        return db_user_role

    @staticmethod
    def remove_role_from_user(db: Session, user_id: str, role_id: str) -> bool:
        db_user_role = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        if db_user_role:
            db.delete(db_user_role)
            db.commit()
            return True
        return False

    @staticmethod
    def get_user_roles(db: Session, user_id: str) -> List[UserRole]:
        return db.query(UserRole).filter(UserRole.user_id == user_id).all()

    @staticmethod
    def get_role_users(db: Session, role_id: str) -> List[UserRole]:
        return db.query(UserRole).filter(UserRole.role_id == role_id).all() 