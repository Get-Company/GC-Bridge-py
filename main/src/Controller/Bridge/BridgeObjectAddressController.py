# Child Model
import bdb

from main.src.Controller.Bridge.BridgeObjectController import BridgeObjectController
# Entity for mapping and sync
from main.src.Entity.Bridge.Adressen.BridgeAdressenEntity import *
from main.src.Entity.Bridge.BridgeSynchronizeEntity import *
from main.src.Controller.ERP.ERPController import *
# Functions
import uuid


class BridgeObjectAddressController(BridgeObjectController):
    """
    This is a special case, since we need to crud Adressen, Anschriften and Ansprechpartner
    """

    # Initiate all variables to forward them to super.__init__
    def __init__(self):
        self.dataset = erp_get_dataset("Adressen")
        self.dataset_anschriften = erp_get_dataset("Anschriften")
        self.dataset_ansprechpartner = erp_get_dataset("Ansprechpartner")
        self.last_sync_date_field = "dataset_address_sync_date"
        self.dataset_field_ltzaend = "LtzAend"
        self.datetime_now = datetime.now()
        self.dataset_field_gspkz = "WShopAdrKz"
        self.dataset_field_gspkz_must_be = True
        self.dataset_field_title = "AdrNr"
        self.dataset_field_img = None
        self.img_file = None
        self.class_name = "A-BOAddressC"
        self.adrnr = None
        self.re_ansnr = None
        self.li_ansnr = None
        super().__init__(self.dataset,
                         self.last_sync_date_field,
                         self.dataset_field_ltzaend,
                         self.dataset_field_gspkz,
                         self.dataset_field_gspkz_must_be,
                         self.dataset_field_title,
                         self.dataset_field_img,
                         self.class_name)

    def quick_sync_test(self):

        ds_adr = erp_get_dataset_by_id(self.dataset, "Nr", "10026")

        self.dataset_save_to_db(ds_adr)

    def dataset_save_to_db(self, ds_adr):
        self.adrnr = ds_adr.Fields.Item("AdrNr").AsString

        # Get Anschriften Dataset
        dss_ans = erp_set_dataset_range(
            self.dataset_anschriften,
            "AdrNrAnsNr",
            self.adrnr,
            self.adrnr)
        dss_ans.ApplyRange()
        dss_ans.First()

        # Get Ansprechpartner Dataset
        dss_ansp = erp_set_dataset_range(
            self.dataset_ansprechpartner,
            "AdrNrAnsNrAspNr",
            self.adrnr,
            self.adrnr)
        dss_ansp.ApplyRange()
        dss_ansp.First()

        ntt_adr = map_adressen_erp_to_bridge_db(ds_adr)
        ntt_adr_in_db = BridgeAdressenEntity.query.filter_by(adrnr=ntt_adr.adrnr).first()

        if ntt_adr_in_db:
            print("Adresse in db. Update %s" % ntt_adr_in_db.adrnr)
            # No need for a db.session.add. The data in the session is automagically updated
            ntt_adr_in_db.update(ntt_adr)
            # Update Anschriften
            self.dataset_upsert_anschriften(dss_ans, ntt_adr_in_db)
            # Update Ansprechpartner
            self.dataset_upsert_ansprechpartner(dss_ansp, ntt_adr_in_db)
            db.session.add(ntt_adr_in_db)

        else:
            print("Adresse NOT in db. Create %s" % ntt_adr.adrnr)
            # Create Anschriften
            self.dataset_upsert_anschriften(dss_ans, ntt_adr)
            # Create Ansprechpartner
            self.dataset_upsert_ansprechpartner(dss_ansp, ntt_adr)
            db.session.add(ntt_adr)

        db.session.commit()
        return True

    def dataset_upsert_anschriften(self, dss_ans, ntt_adr):
        if erp_get_dataset_record_count(dss_ans) > 100:
            def write_text():
                with open('Anschriften.txt', 'a', encoding="utf-8") as f:
                    text = "Adresse %s hat insgesamt %s Anschriften\n" % (dss_ans.Fields.Item("AdrNr").AsString, erp_get_dataset_record_count(dss_ans))
                    f.write(text)
            return
        while not dss_ans.EOF:
            # TODO: Check if ans is NOT empty
            ntt_ans = map_anschriften_erp_to_bridge_db(dss_ans)

            ntt_ans_in_db = BridgeAnschriftenEntity.query \
                .filter_by(adrnr=ntt_adr.adrnr) \
                .filter_by(ansnr=ntt_ans.ansnr) \
                .first()

            if ntt_ans_in_db:
                print(
                    'Anschrift in db. Update %s:%s DS:"%s" = NTT:"%s"' % (
                        ntt_ans.adrnr,
                        ntt_ans.ansnr,
                        dss_ans.Fields.Item("Na2").AsString,
                        ntt_ans.na2))
                ntt_ans_in_db.update(ntt_ans)
                db.session.merge(ntt_ans_in_db)
            else:
                print("Anschrift NOT in db. Create %s:%s" % (
                    ntt_ans.adrnr, ntt_ans.ansnr))
                ntt_ans.adresse = ntt_adr
                db.session.add(ntt_ans)

            dss_ans.Next()

    def dataset_upsert_ansprechpartner(self, dss_ansp, ntt_adr):
        if erp_get_dataset_record_count(dss_ansp) > 100:
            def write_text():
                with open('Ansprechpartner.txt', 'a', encoding="utf-8") as f:
                    text = "Anschrift %s hat insgesamt %s Ansprechpartner\n" % (dss_ansp.Fields.Item("AdrNr").AsString, erp_get_dataset_record_count(dss_ansp))
                    f.write(text)
            return
        while not dss_ansp.EOF:
            # TODO: Check if ansp is NOT empty
            ntt_ansp = map_ansprechpartner_erp_to_bridge_db(dss_ansp)

            ntt_ansp_in_db = BridgeAnsprechpartnerEntity.query \
                .filter_by(adrnr=ntt_ansp.adrnr) \
                .filter_by(ansnr=ntt_ansp.ansnr) \
                .filter_by(aspnr=ntt_ansp.aspnr) \
                .first()

            if ntt_ansp_in_db:
                print("Ansprechpartner in db. Update %s:%s:%s" % (
                    ntt_adr.adrnr,
                    ntt_ansp_in_db.ansnr,
                    ntt_ansp_in_db.aspnr
                ))
                ntt_ansp_in_db.update(ntt_ansp)
                db.session.add(ntt_ansp_in_db)
            else:
                print("Ansprechpartner NOT in db. Create %s:%s:%s" % (
                    ntt_adr.adrnr,
                    ntt_ansp.ansnr,
                    ntt_ansp.aspnr
                ))
                ntt_ansp.adresse = ntt_adr
                db.session.add(ntt_ansp)

            dss_ansp.Next()
        return True