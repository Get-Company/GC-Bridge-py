from main import db
from datetime import datetime


# Make the Adressen class
class BridgeAdressenEntity(db.Model):
    __tablename__ = 'bridge_adressen_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    adrnr = db.Column(db.Integer(), nullable=False)

    # Address for billing and shipping
    # is set with the value from erp
    re_ansnr = db.Column(db.Integer(), nullable=False)
    li_ansnr = db.Column(db.Integer(), nullable=False)
    vat_id = db.Column(db.String(255), nullable=True)

    erp_ltz_aend = db.Column(db.DateTime(), default=datetime.now())
    anschriften = db.relationship("BridgeAnschriftenEntity", back_populates="adresse")
    ansprechpartner = db.relationship("BridgeAnsprechpartnerEntity", back_populates="adresse")

    def update(self, new):
        self.adrnr = new.adrnr
        self.re_ansnr = new.re_ansnr
        self.li_ansnr = new.li_ansnr
        self.vat_id = new.vat_id
        return True


def map_adressen_erp_to_bridge_db(dataset_adressen):
    """
    Maps the Dataset Adressen to the entity BridgeAdressenEntity
    :param dataset_adressen: dataset
    :return: object BridgeAdressenEntity
    """
    print("Map AdrNr: %s with re_ansnr:%s and li_ansnr:%s" % (
        dataset_adressen.Fields.Item("AdrNr").AsInteger,
        dataset_adressen.Fields.Item("ReAnsNr").AsInteger,
        dataset_adressen.Fields.Item("LiAnsNr").AsInteger,
    ))
    entity_adressen = BridgeAdressenEntity(
        # Integer
        adrnr=dataset_adressen.Fields.Item("AdrNr").AsInteger,
        # Integer
        re_ansnr=dataset_adressen.Fields.Item("ReAnsNr").AsInteger,
        li_ansnr=dataset_adressen.Fields.Item("LiAnsNr").AsInteger,
        vat_id=dataset_adressen.Fields.Item("UStId").AsString
    )
    return entity_adressen


# Make the Anschriften class
class BridgeAnschriftenEntity(db.Model):
    __tablename__ = 'bridge_anschriften_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    adrnr = db.Column(db.Integer(), nullable=False)
    ansnr = db.Column(db.Integer(), nullable=False)
    aspnr = db.Column(db.Integer(), nullable=False)
    na1 = db.Column(db.String(255), nullable=False)
    na2 = db.Column(db.String(255), nullable=False)
    na3 = db.Column(db.String(255), nullable=True)
    str = db.Column(db.String(255), nullable=True)
    plz = db.Column(db.CHAR(12), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    land = db.Column(db.Integer(), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    company = db.Column(db.String(255), nullable=True)

    erp_ltz_aend = db.Column(db.DateTime(), default=datetime.now())

    # Adresse
    adresse_id = db.Column(db.Integer(), db.ForeignKey('bridge_adressen_entity.id'))
    adresse = db.relationship("BridgeAdressenEntity", back_populates="anschriften")

    def update(self, new):
        self.adrnr = new.adrnr
        self.ansnr = new.ansnr
        self.aspnr = new.aspnr
        self.na1 = new.na1
        self.na2 = new.na2
        self.na3 = new.na3
        self.str = new.str
        self.plz = new.plz
        self.city = new.city
        self.land = new.land
        self.email = new.email
        self.company = new.company
        return True


def map_anschriften_erp_to_bridge_db(dataset_anschriften):
    """
    Maps the Dataset Adressen to the entity BridgeAnschriftenEntity
    :param dataset_anschriften: dataset_anschriften
    :return: object BridgeAdressenEntity
    """
    # Check for company
    if dataset_anschriften.Fields.Item("Na1").AsString == "Firma":
        company = dataset_anschriften.Fields.Item("Na2").AsString
    else:
        company = None

    entity_anschriften = BridgeAnschriftenEntity(
        # Integer
        adrnr=dataset_anschriften.Fields.Item("AdrNr").AsInteger,
        ansnr=dataset_anschriften.Fields.Item("AnsNr").AsInteger,
        aspnr=dataset_anschriften.Fields.Item("AspNr").AsInteger,
        na1=dataset_anschriften.Fields.Item("Na1").AsString,
        na2=dataset_anschriften.Fields.Item("Na2").AsString,
        na3=dataset_anschriften.Fields.Item("Na3").AsString,
        str=dataset_anschriften.Fields.Item("Str").AsString,
        plz=dataset_anschriften.Fields.Item("PLZ").AsString,
        city=dataset_anschriften.Fields.Item("Ort").AsString,
        land=dataset_anschriften.Fields.Item("Land").AsInteger,
        email=dataset_anschriften.Fields.Item("EMail1").AsString,
        company=company,
    )
    return entity_anschriften


# Make the Ansprechpartner class
class BridgeAnsprechpartnerEntity(db.Model):
    __tablename__ = 'bridge_ansprechpartner_entity'

    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True)
    adrnr = db.Column(db.Integer(), nullable=False)
    ansnr = db.Column(db.Integer(), nullable=False)
    aspnr = db.Column(db.Integer(), nullable=False)
    vna = db.Column(db.String(255), nullable=True)
    nna = db.Column(db.String(255), nullable=True)
    tit = db.Column(db.String(255), nullable=True)
    abt = db.Column(db.String(255), nullable=True)

    # Adresse
    adresse_id = db.Column(db.Integer(), db.ForeignKey('bridge_adressen_entity.id'))
    adresse = db.relationship("BridgeAdressenEntity", back_populates="ansprechpartner")

    def update(self, new):
        self.adrnr = new.adrnr
        self.ansnr = new.ansnr
        self.aspnr = new.aspnr
        self.vna = new.vna
        self.nna = new.nna
        self.tit = new.tit
        self.abt = new.abt
        return True


def map_ansprechpartner_erp_to_bridge_db(dataset_ansprechpartner):
    """
    Maps the Dataset Adressen to the entity BridgeansprechpartnerEntity
    :param dataset_ansprechpartner: dataset_ansprechpartner
    :return: object BridgeansprechpartnerEntity
    """
    entity_ansprechpartner = BridgeAnsprechpartnerEntity(
        adrnr=dataset_ansprechpartner.Fields.Item("AdrNr").AsInteger,
        ansnr=dataset_ansprechpartner.Fields.Item("AnsNr").AsInteger,
        aspnr=dataset_ansprechpartner.Fields.Item("AspNr").AsInteger,
        vna=dataset_ansprechpartner.Fields.Item("VNa").AsString,
        nna=dataset_ansprechpartner.Fields.Item("NNa").AsString,
        tit=dataset_ansprechpartner.Fields.Item("Tit").AsString,
        abt=dataset_ansprechpartner.Fields.Item("Abt").AsString
    )
    return entity_ansprechpartner
