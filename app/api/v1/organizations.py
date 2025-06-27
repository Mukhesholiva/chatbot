from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...db.session import get_db
from ...schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse
)
from ...services.organization_service import OrganizationService
from ...models.user import User
from .auth import get_current_active_user

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if organization with code already exists
    existing_org = OrganizationService.get_organization_by_code(db, organization.code)
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization with this code already exists"
        )
    
    return OrganizationService.create_organization(
        db=db,
        organization=organization,
        current_user_id=current_user.id
    )

@router.get("", response_model=List[OrganizationResponse])
@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    organizations = OrganizationService.get_organizations(db, skip=skip, limit=limit)
    return organizations

@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific organization by ID.
    """
    organization = OrganizationService.get_organization(db, organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return organization

@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: str,
    organization: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if organization exists
    existing_org = OrganizationService.get_organization(db, organization_id)
    if not existing_org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # If code is being updated, check if new code already exists
    if organization.code and organization.code != existing_org.code:
        code_exists = OrganizationService.get_organization_by_code(db, organization.code)
        if code_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization with this code already exists"
            )
    
    updated_org = OrganizationService.update_organization(
        db=db,
        org_id=organization_id,
        organization=organization,
        current_user_id=current_user.id
    )
    return updated_org

@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if organization exists
    existing_org = OrganizationService.get_organization(db, organization_id)
    if not existing_org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    OrganizationService.delete_organization(db, organization_id)
    return None 