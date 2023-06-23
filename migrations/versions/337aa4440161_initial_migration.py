"""Initial migration

Revision ID: 337aa4440161
Revises: 
Create Date: 2023-06-22 14:05:24.722974

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '337aa4440161'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
    sa.Column('name', sa.String(length=8), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('user',
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('forename', sa.String(length=256), nullable=False),
    sa.Column('surname', sa.String(length=256), nullable=False),
    sa.Column('role_name', sa.String(length=8), nullable=False),
    sa.ForeignKeyConstraint(['role_name'], ['role.name'], ),
    sa.PrimaryKeyConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('role')
    # ### end Alembic commands ###
