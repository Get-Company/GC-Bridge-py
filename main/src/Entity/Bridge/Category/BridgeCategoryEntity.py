import uuid

from main import db
from datetime import datetime
# Categories Products Relation many - to - many
from main.src.Entity.Bridge.Product.BridgeProductEntity import product_category
from main.src.Entity.ERP.ERPArtikelKategorieEntity import *
from main.src.Entity.Bridge.Media.BridgeMediaEntity import media_cat

from slugify import slugify


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
    description = db.Column(db.Text(), nullable=True)
    erp_ltz_aend = db.Column(db.DateTime(), default=datetime.datetime.now())
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
    # Translation for Category
    translations = db.relationship('BridgeCategoryTranslationEntity', backref='category')

    # Products Relation many-to-many

    def __repr__(self):
        # return f"Category {self.title}({self.erp_nr}) was created with id:{self.id} and API-ID:{self.api_id}"
        return f"Category {self.title} id:{self.id} erp_nr:{self.erp_nr}"

    # Categories Products Relation many - to - many
    products = db.relationship(
        'BridgeProductEntity',
        secondary=product_category,
        back_populates='categories',
        lazy='dynamic')

    # Media Relation many - to - many
    medias = db.relationship(
        'BridgeMediaEntity',
        secondary=media_cat,
        back_populates="categories"
    )

    def map_erp_to_db(self, erp_category: ERPArtikelKategorieEntity):
        self.erp_nr = erp_category.get_('Nr'),
        self.erp_nr_parent = erp_category.get_('ParentNr'),
        self.api_idparent = 0,
        self.title = erp_category.get_('Bez'),
        self.image = None,
        self.description = erp_category.get_('Info'),
        self.erp_ltz_aend = erp_category.get_('LtzAend').replace(tzinfo=None),
        # Always keep api_ids
        if not self.api_id:
            self.api_id = uuid.uuid4().hex

        return self

    def update_entity(self, entity):
        self.erp_nr = entity.erp_nr

        try:
            parent = self.query. \
                filter_by(erp_nr=entity.erp_nr_parent). \
                first()
            print(self.title,"has parent:", parent.title)
            if parent:
                self.erp_nr_parent = parent.erp_nr
                self.api_idparent = parent.api_id
        except:
            print("No parent with id: %s found. Maybe its the super category with no parent" % entity.erp_nr_parent)

        self.title = entity.title
        self.image = entity.image
        self.description = entity.description
        self.erp_ltz_aend = entity.erp_ltz_aend
        return True

    def get_parent_category_title(self, slugify=True):
        # Make it websafe
        parent = self.query.filter_by(api_id=self.api_idparent).one_or_none()
        if parent:
            if slugify:
                parent_title = self.slugify(parent.title)
                return parent_title # Get the name
            else:
                return parent.title
        return False

    def get_category_title(self, slugify=True):
        if slugify:
            category_title = self.slugify(self.title)
            return category_title
        else:
            return self.title

    def slugify(self, name):
        regex_pattern = r'[^-a-zA-Z0-9_/]+'  # Search for Chars we want to keep
        umlaute = [
            ['Ä', 'AE'],
            ['ä', 'ae'],
            ['Ö', 'OE'],
            ['ö', 'oe'],
            ['Ü', 'UE'],
            ['ü', 'ue']
        ]
        slug = slugify(
            name,
            regex_pattern=regex_pattern,
            replacements=umlaute,
            lowercase=False)  # Do the magic

        return slug




# Make the translation class
class BridgeCategoryTranslationEntity(db.Model):
    __tablename__ = 'bridge_category_translation_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    language_iso = db.Column(db.String(5), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    erp_ltz_aend = db.Column(db.DateTime(), default=datetime.datetime.now())
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
