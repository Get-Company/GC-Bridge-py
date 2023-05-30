"""empty message

Revision ID: ccba055641c9
Revises: 7bbc4a39c88e
Create Date: 2023-05-22 09:27:20.720997

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ccba055641c9'
down_revision = '7bbc4a39c88e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f('uq_bridge_customer_entity_email'), 'bridge_customer_entity', ['email'])
    op.create_foreign_key(op.f('fk_bridge_price_entity_product_id_bridge_product_entity'), 'bridge_price_entity', 'bridge_product_entity', ['product_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_bridge_price_entity_product_id_bridge_product_entity'), 'bridge_price_entity', type_='foreignkey')
    op.drop_constraint(op.f('uq_bridge_customer_entity_email'), 'bridge_customer_entity', type_='unique')
    # ### end Alembic commands ###
