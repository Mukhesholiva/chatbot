"""add org_id to campaigns

Revision ID: add_org_id_campaigns
Revises: 
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_org_id_campaigns'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add org_id column
    op.add_column('campaigns',
        sa.Column('org_id', sa.String(50), nullable=True)
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_campaigns_org_id',
        'campaigns', 'organizations',
        ['org_id'], ['id']
    )

def downgrade():
    # Remove foreign key first
    op.drop_constraint('fk_campaigns_org_id', 'campaigns', type_='foreignkey')
    
    # Remove column
    op.drop_column('campaigns', 'org_id') 