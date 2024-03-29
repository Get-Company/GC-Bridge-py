from main import db
from datetime import datetime


class BridgeSynchronizeEntity(db.Model):
    __tablename__ = 'bridge_synchronize_entity'
    id = db.Column(db.Integer(), primary_key=True, nullable=False, unique=True)
    dataset_category_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now().replace(microsecond=0))
    dataset_product_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now().replace(microsecond=0))
    dataset_customers_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now().replace(microsecond=0))
    dataset_tax_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now().replace(microsecond=0))
    dataset_order_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now().replace(microsecond=0))
    # SW6 Fields
    sw6_category_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now().replace(microsecond=0))
    sw6_product_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now().replace(microsecond=0))
    sw6_customers_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now().replace(microsecond=0))
    sw6_order_sync_date = db.Column(db.DateTime(), nullable=True, default=datetime.now().replace(microsecond=0))
    # Loop True or false
    loop_continue = db.Column(db.Boolean, nullable=True)

    """ Get the first row since everything will be stored there """
    def get_entity_by_id_1(self):
        """Returns the entity with id 1."""
        return self.query.filter_by(id=1).first()

    def get_dataset_category_sync_date(self):
        """Returns the dataset_category_sync_date for the entity with id 1."""
        return self.get_entity_by_id_1().dataset_category_sync_date

    def set_dataset_category_sync_date(self, value):
        """Sets the value of dataset_category_sync_date for the entity with id=1"""
        entity = self.get_entity_by_id_1()
        entity.dataset_category_sync_date = value

        return entity

    def get_dataset_product_sync_date(self):
        """Returns the dataset_product_sync_date for the entity with id 1."""
        return self.get_entity_by_id_1().dataset_product_sync_date

    def set_dataset_product_sync_date(self, value):
        """Sets the value of dataset_product_sync_date for the entity with id=1"""
        entity = self.get_entity_by_id_1()
        entity.dataset_product_sync_date = value

        return entity

    def get_dataset_customers_sync_date(self):
        """Returns the dataset_customers_sync_date for the entity with id 1."""
        return self.get_entity_by_id_1().dataset_customers_sync_date

    def set_dataset_customers_sync_date(self, value):
        """Sets the value of dataset_customers_sync_date for the entity with id=1"""
        entity = self.get_entity_by_id_1()
        entity.dataset_customers_sync_date = value

        return entity

    def get_dataset_tax_sync_date(self):
        """Returns the dataset_tax_sync_date for the entity with id 1."""
        return self.get_entity_by_id_1().dataset_tax_sync_date

    def set_dataset_tax_sync_date(self, value):
        """Sets the value of dataset_tax_sync_date for the entity with id=1"""
        entity = self.get_entity_by_id_1()
        entity.dataset_tax_sync_date = value

        return entity

    def get_dataset_order_sync_date(self):
        """Returns the dataset_order_sync_date for the entity with id 1."""
        return self.get_entity_by_id_1().dataset_order_sync_date

    def set_dataset_order_sync_date(self, value):
        """Sets the value of dataset_order_sync_date for the entity with id=1"""
        entity = self.get_entity_by_id_1()
        entity.dataset_order_sync_date = value

        return entity

    def get_sw6_category_sync_date(self):
        """Returns the sw6_category_sync_date for the entity with id 1."""
        return self.get_entity_by_id_1().sw6_category_sync_date

    def set_sw6_category_sync_date(self, value):
        """Sets the value of sw6_category_sync_date for the entity with id=1"""
        entity = self.get_entity_by_id_1()
        entity.sw6_category_sync_date = value

        return entity

    def get_sw6_product_sync_date(self):
        """Returns the sw6_product_sync_date for the entity with id 1."""
        return self.get_entity_by_id_1().sw6_product_sync_date

    def set_sw6_product_sync_date(self, value):
        """Sets the value of sw6_product_sync_date for the entity with id=1"""
        entity = self.get_entity_by_id_1()
        entity.sw6_product_sync_date = value

        return entity

    def get_sw6_customers_sync_date(self):
        """Returns the sw6_customers_sync_date for the entity with id 1."""
        return self.get_entity_by_id_1().sw6_customers_sync_date

    def set_sw6_customers_sync_date(self, value):
        """Sets the value of sw6_customers_sync_date for the entity with id=1"""
        entity = self.get_entity_by_id_1()
        entity.sw6_customers_sync_date = value

        return entity

    def get_sw6_order_sync_date(self):
        """Returns the sw6_order_sync_date for the entity with id 1."""
        return self.get_entity_by_id_1().sw6_order_sync_date

    def set_sw6_order_sync_date(self, value):
        """Sets the value of sw6_order_sync_date for the entity with id=1"""
        entity = self.get_entity_by_id_1()
        entity.sw6_order_sync_date = value

        return entity

    def get_loop_continue(self):
        """Returns the loop_continue value for the entity with id 1."""
        return self.get_entity_by_id_1().loop_continue

    def set_loop_continue(self, value):
        """Sets the value of loop_continue for the entity with id=1"""
        entity = self.get_entity_by_id_1()
        entity.loop_continue = value

        return entity
    
    def commit(self):
        """Commits the changes to the database."""
        db.session.add(self)
        db.session.commit()
        db.session.close()

    def __repr__(self):
        # text = f"BridgeCustomerEntity: {self.id} - {self.erp_nr}"
        # return text
        return f"BridgeCustomerEntity: id {self.id}"



