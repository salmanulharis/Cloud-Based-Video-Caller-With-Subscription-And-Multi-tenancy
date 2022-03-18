"""empty message

Revision ID: b6d016501d96
Revises: 9e28df1b2c30
Create Date: 2021-12-24 14:48:06.843474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6d016501d96'
down_revision = '9e28df1b2c30'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('doctors', sa.Column('place', sa.String(), nullable=True))
    op.add_column('doctors', sa.Column('born', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('doctors', 'born')
    op.drop_column('doctors', 'place')
    # ### end Alembic commands ###