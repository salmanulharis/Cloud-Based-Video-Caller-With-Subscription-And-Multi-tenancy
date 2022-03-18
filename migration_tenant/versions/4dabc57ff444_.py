"""empty message

Revision ID: 4dabc57ff444
Revises: acd72d29db05
Create Date: 2021-12-23 13:26:48.723050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4dabc57ff444'
down_revision = 'acd72d29db05'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('doctors', 'born')
    op.drop_column('doctors', 'place')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('doctors', sa.Column('place', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('doctors', sa.Column('born', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
