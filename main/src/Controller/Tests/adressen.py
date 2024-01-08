from main.src.Entity.ERP.ERPAdressenEntity import ERPAdressenEntity
from main.src.Entity.ERP.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity
from main.src.Entity.ERP.ERPAnschriftenEntity import ERPAnschriftenEntity
from main.src.Entity.ERP.ERPConnectionEntity import ERPConnectionEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity
from main.src.Entity.Bridge.Customer.BridgeCustomerAddressEntity import BridgeCustomerAddressEntity
from main import db

erp_obj = ERPConnectionEntity()

def save_address_to_db():
    # Get Address
    erp_add_ntt = ERPAdressenEntity(erp_obj=erp_obj, id_value='10026')

    # Get Anschrift
    erp_ans_ntt = ERPAnschriftenEntity(erp_obj=erp_obj)
    erp_ans_ntt.find_('AdrNrAnsNr', [erp_add_ntt.get_('AdrNr'), erp_add_ntt.get_('LiAnsNr')])

    # Get Ansprechpartner
    erp_ansp_ntt = ERPAnsprechpartnerEntity(erp_obj=erp_obj)
    erp_ansp_ntt.find_('AdrNrAnsNrAspNr'), erp_add_ntt.get_('AdrNr'), erp_ans_ntt.get_('AnsNr'), erp_ans_ntt.get_('AspNr')


    bridge_customer_entity = BridgeCustomerEntity().map_erp_to_db(erp_add_ntt)
    bridge_address_entity = BridgeCustomerAddressEntity.map_erp_to_db(erp_ans_ntt)
    bridge_contact_entity = BridgeCustomerAddressEntity.map_erp_to_db(erp_ansp_ntt)

    bridge_customer_entity.addresses = [bridge_address_entity]
    bridge_address_entity.contacts = [bridge_contact_entity]

    db.session.add(bridge_contact_entity)

    db.session.commit()