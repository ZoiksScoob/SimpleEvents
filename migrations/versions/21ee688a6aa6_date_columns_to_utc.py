"""date columns to utc

Revision ID: 21ee688a6aa6
Revises: df4c786a55cc
Create Date: 2020-09-08 14:41:25.095573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21ee688a6aa6'
down_revision = 'df4c786a55cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('blacklist_tokens', 'blacklisted_on', new_column_name='blacklisted_on_utc')
    op.alter_column('users', 'registered_on', new_column_name='registered_on_utc')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('blacklist_tokens', 'blacklisted_on_utc', new_column_name='blacklisted_on')
    op.alter_column('users', 'registered_on_utc', new_column_name='registered_on')
    # ### end Alembic commands ###
