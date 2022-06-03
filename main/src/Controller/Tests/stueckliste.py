from main.src.Controller.ERP.ERPController import *


def get_stueckliste_direct():
    erp_connect()
    dataset_stueckliste = erp_get_dataset('ArtikelStueckliste')
    basic_set = erp_get_dataset_by_id(dataset_stueckliste, 'SlArtNr', '*900000')

    print('%s\n---' % basic_set.Fields('SlArtNr').AsString)
    while not basic_set.EOF:
        if basic_set.Fields('SlArtNr').AsString != '*900000':
            return False

        print("%s - %s %s - %s " % (
            basic_set.Fields('ArtNr').AsString,
            basic_set.Fields('Mge').AsString,
            basic_set.Fields('Einh').AsString,
            basic_set.Fields('Preis').AsString,
        ))

        basic_set.Next()


    erp_close()

