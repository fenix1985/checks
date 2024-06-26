"""added models

Revision ID: d8aedfc53506
Revises: 
Create Date: 2024-05-04 14:45:26.668655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd8aedfc53506'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('hashed_password', sa.String(length=256), nullable=False),
    sa.Column('create_date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('check',
    sa.Column('check_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('token', sa.String(length=50), nullable=False),
    sa.Column('url', sa.String(length=256), nullable=False),
    sa.Column('type', postgresql.ENUM('CASH', 'CASHLESS', name='payment_type'), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('check_id'),
    sa.UniqueConstraint('token')
    )
    op.create_table('productcheck',
    sa.Column('check_detail_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('check_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['check_id'], ['check.check_id'], ),
    sa.PrimaryKeyConstraint('check_detail_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('productcheck')
    op.drop_table('check')
    op.drop_table('user')
    # ### end Alembic commands ###
