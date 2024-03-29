"""remove billing and shipping

Revision ID: 69f91fcfee9c
Revises: 2a2333875395
Create Date: 2023-06-28 15:43:29.674086

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '69f91fcfee9c'
down_revision = '2a2333875395'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_bridge_customer_entity_billing_address_id_bridge_cust_c902', 'bridge_customer_entity', type_='foreignkey')
    op.drop_constraint('fk_bridge_customer_entity_shipping_address_id_bridge_cus_fc1c', 'bridge_customer_entity', type_='foreignkey')
    op.drop_index('uq_bridge_customer_entity_billing_address_id', table_name='bridge_customer_entity')
    op.drop_index('uq_bridge_customer_entity_shipping_address_id', table_name='bridge_customer_entity')
    op.drop_column('bridge_customer_entity', 'billing_address_id')
    op.drop_column('bridge_customer_entity', 'shipping_address_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bridge_customer_entity', sa.Column('shipping_address_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('bridge_customer_entity', sa.Column('billing_address_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('fk_bridge_customer_entity_shipping_address_id_bridge_cus_fc1c', 'bridge_customer_entity', 'bridge_customer_address_entity', ['shipping_address_id'], ['id'])
    op.create_foreign_key('fk_bridge_customer_entity_billing_address_id_bridge_cust_c902', 'bridge_customer_entity', 'bridge_customer_address_entity', ['billing_address_id'], ['id'])
    op.create_index('uq_bridge_customer_entity_shipping_address_id', 'bridge_customer_entity', ['shipping_address_id'], unique=False)
    op.create_index('uq_bridge_customer_entity_billing_address_id', 'bridge_customer_entity', ['billing_address_id'], unique=False)
    # ### end Alembic commands ###
