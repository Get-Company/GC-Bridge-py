from main import db
from datetime import datetime
# Categories Products Relation many - to - many
from main.src.Entity.Bridge.Product.BridgeProductEntity import product_category


# Make the category class
class BridgeCategoryEntity(db.Model):
    __tablename__ = 'bridge_category_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    erp_nr = db.Column(db.Integer(), nullable=False)
    api_id = db.Column(db.CHAR(36), nullable=False)
    erp_nr_parent = db.Column(db.Integer(), nullable=True)
    api_idparent = db.Column(db.CHAR(36), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.CHAR(), nullable=True)
    erp_ltz_aend = db.Column(db.DateTime(), default=datetime.now())
    # Translation for Category
    translations = db.relationship('BridgeCategoryTranslationEntity', backref='category')
    # Products Relation many-to-many

    def __repr__(self):
        return f"Category {self.title}({self.erp_nr}) was created"

    # Categories Products Relation many - to - many
    products = db.relationship(
        'BridgeProductEntity',
        secondary=product_category,
        back_populates='categories',
        lazy='dynamic')

    def update_entity(self, entity):
        self.erp_nr = entity.erp_nr
        if entity.api_id:
            self.api_id = entity.api_id
        try:
            parent = self.query.\
                filter_by(erp_nr=entity.erp_nr_parent).\
                first()
            if parent:
                self.erp_nr_parent = parent.erp_nr
                self.api_idparent = parent.api_id
        except:
            print("No parent with id: %s found. Maybe its the super category with no parent" % entity.erp_nr_parent)

        self.title = entity.title
        self.image = entity.image
        self.description = entity.description
        return True


# Make the translation class
class BridgeCategoryTranslationEntity(db.Model):
    __tablename__ = 'bridge_category_translation_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    language_iso = db.Column(db.String(5), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.CHAR(), nullable=True)
    erp_ltz_aend = db.Column(db.DateTime(), default=datetime.now())
    # Translation for Category
    category_id = db.Column(db.Integer, db.ForeignKey('bridge_category_entity.id'))

    def __repr__(self):
        return f"Category translation {self.title} was created"


def map_category_erp_to_bridge_db(dataset, img=None, language_array=None):
    """
    Maps the fields from ERP to the Bridge db-translates to
    :param dataset: object Dataset
    :param img: string The img filename or 0
    :param language_array: Array of languages iso (de-DE)
    :return: object Entity
    """
    # Mapping the Entity
    entity = BridgeCategoryEntity(
        erp_nr=dataset.Fields.Item("Nr").AsString,
        api_id=0,
        erp_nr_parent=dataset.Fields.Item("ParentNr").AsString,
        api_idparent=0,
        title=dataset.Fields.Item("Bez").AsString,
        image=img,
        description=dataset.Fields.Item("Info").Text
    )


    # Check if we got an array of language codes
    if isinstance(language_array, list):  # isinstance checks if array is list
        for lang in language_array:
            # Translating the Entity with the value lang
            translation = BridgeCategoryTranslationEntity(
                language_iso=lang,
                title=dataset.Fields.Item("Bez").AsString,
                image=img,
                description=dataset.Fields.Item("Info").Text,
                category=entity
            )
        entity.translations.append(translation)

    else:
        # Translating the Entity with the value lang
        translation = BridgeCategoryTranslationEntity(
            language_iso="de-DE",
            title=dataset.Fields.Item("Bez").AsString,
            image=img,
            description=dataset.Fields.Item("Info").Text,
            category=entity
        )
        entity.translations.append(translation)
    return entity



