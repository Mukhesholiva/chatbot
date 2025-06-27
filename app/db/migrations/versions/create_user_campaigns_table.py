"""create user_campaigns table

Revision ID: create_user_campaigns
Revises: add_org_id_campaigns
Create Date: 2024-03-20

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_user_campaigns'
down_revision = 'add_org_id_campaigns'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'user_campaigns',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('user_id', sa.String(50), nullable=False),
        sa.Column('campaign_id', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(50), nullable=False),
        sa.Column('modified_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('modified_by', sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_campaigns_user_id'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], name='fk_user_campaigns_campaign_id')
    )
    
    # Create index for faster lookups
    op.create_index('idx_user_campaigns_user_id', 'user_campaigns', ['user_id'])
    op.create_index('idx_user_campaigns_campaign_id', 'user_campaigns', ['campaign_id'])

def downgrade():
    op.drop_index('idx_user_campaigns_campaign_id')
    op.drop_index('idx_user_campaigns_user_id')
    op.drop_table('user_campaigns') 