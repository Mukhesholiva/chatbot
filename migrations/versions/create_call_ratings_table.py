"""create call ratings table

Revision ID: create_call_ratings_table
Revises: 
Create Date: 2024-03-31

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_call_ratings_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'call_ratings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('call_id', sa.String(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('submitted_by', sa.String(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('modified_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_call_ratings_call_id'), 'call_ratings', ['call_id'], unique=False)
    op.create_index(op.f('ix_call_ratings_id'), 'call_ratings', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_call_ratings_id'), table_name='call_ratings')
    op.drop_index(op.f('ix_call_ratings_call_id'), table_name='call_ratings')
    op.drop_table('call_ratings') 