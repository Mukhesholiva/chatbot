from sqlalchemy.orm import Session
import uuid
from ..models.organization import Organization
from ..schemas.organization import OrganizationCreate, OrganizationUpdate
from datetime import datetime

class OrganizationService:
    @staticmethod
    def create_organization(db: Session, organization: OrganizationCreate, current_user_id: str):
        org_id = f"org_{uuid.uuid4().hex[:8]}"
        db_org = Organization(
            id=org_id,
            name=organization.name,
            code=organization.code,
            description=organization.description,
            status=organization.status,
            created_by=current_user_id,
            modified_by=current_user_id
        )
        db.add(db_org)
        db.commit()
        db.refresh(db_org)
        return db_org

    @staticmethod
    def get_organization(db: Session, org_id: str):
        return db.query(Organization).filter(Organization.id == org_id).first()

    @staticmethod
    def get_organization_by_code(db: Session, code: str):
        return db.query(Organization).filter(Organization.code == code).first()

    @staticmethod
    def get_organizations(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Organization).order_by(Organization.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_organization(
        db: Session, 
        org_id: str, 
        organization: OrganizationUpdate, 
        current_user_id: str
    ):
        db_org = OrganizationService.get_organization(db, org_id)
        if db_org:
            update_data = organization.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_org, field, value)
            db_org.modified_by = current_user_id
            db_org.modified_at = datetime.utcnow()
            db.commit()
            db.refresh(db_org)
        return db_org

    @staticmethod
    def delete_organization(db: Session, org_id: str):
        db_org = db.query(Organization).filter(Organization.id == org_id).first()
        if db_org:
            db.delete(db_org)
            db.commit()
            return True
        return False 