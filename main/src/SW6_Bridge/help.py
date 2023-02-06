import sys
from termcolor import colored


class Helper:
    def __init__(self):
        pass

    def upload_all_new_customer_from_shopware_to_bridge(self):
        print(
        """
        Holt sich ein Zugangstoken von der Shopware 6 API, indem er eine POST-Anfrage an die Authentifizierungs-URL mit der Client-ID, dem Client-Geheimnis und dem Grant-Typ sendet.

        Ruft die API auf, um Informationen über alle Kunden in Shopware 6 zu erhalten und speichert ihre IDs und Namen in der customer_ids in Datenbank.

        Fragt die vorhandenen Kunden-IDs in der Datenbank ab und vergleicht sie mit den IDs in customer_ids.

        Für jeden neuen Kunden, der in Shopware 6 gefunden wird, holt der Code die Kundeninformationen und Adressen durch API-Aufrufe ab und speichert die Informationen in einer customer_data-Liste.

        Schließlich erstellt es ein Customer und CustomerAddress-Objekt für jeden neuen Kunden und fügt sie der Datenbank mithilfe der SQLAlchemy-Sitzung hinzu.
        """
        )


    def sync_all_changed_customers_from_SW_to_bridge(self):
        print(
        """
        Es holt sich dann die Shopware-API-Endpunkte und die Authentifizierungsinformationen aus einer Konfigurationsdatei.

        Es sendet eine Anfrage an die Shopware-API, um alle Kundendaten abzurufen.

        Es erstellt eine Datenbank-Sitzung, um eine Verbindung zu einer lokalen MySQL-Datenbank "shopware" herzustellen.

        Es iteriert dann durch die vom API abgerufenen Kundendaten und überprüft, ob bereits ein Kunde mit dem gleichen "api_id" in der lokalen Datenbank vorhanden ist.

        Wenn der Kunde vorhanden ist, überprüft es, ob die aktualisierte Zeit aus dem API neuer ist als die aktualisierte Zeit in der Datenbank. Wenn ja, fügt es die API-ID des Kunden zu einer Liste der zu aktualisierenden Kunden hinzu.

        Nach dem Loop aktualisiert der Code das "sw6_customers_sync_date" in der Tabelle "Synchronize" in der Datenbank.

        Wenn es Kunden zum Aktualisieren gibt, protokolliert es eine Meldung mit der Anzahl gefundener Kunden und holt sich die detaillierten Informationen für jeden Kunden, einschließlich ihres Namens, ihrer E-Mail-Adresse, ihrer Standard-Rechnungs- und Lieferadressen-IDs und Adressen.

        Es überprüft dann Updates für die Kundenadressen, indem es die API-Adress-IDs mit den Adress-IDs in der lokalen Datenbank vergleicht. Wenn die Adresse in der Datenbank nicht vorhanden ist, erstellt es eine neue Adresse.
        """
        )


    def sync_selected_customers_from_BRIDGE_to_sw_WITH_SYNC_CHECK(self):
        print(
        """
        Dieser Code führt eine Abfrage in Datenbank aus, um Kundendaten abzurufen. 
        
        Es filtert die Kunden anhand einer bestimmten Datumsspanne und einer ERP-Nummer-Range und extrahiert dann die API-IDs aller gefundenen Kunden. 
        
        Am Ende wird eine Methode namens "init_sync_BRIDGE_to_SW" aufgerufen, um die gefundenen Kunden zu synchronisieren.
        """
        )

    def sync_selected_customers_from_BRIDGE_to_sw_WITHOUT_SYNC_CHECK_NIIIIX_CHECKEN_DIESE(self):
        print(
        """
        Dieser Code-Abschnitt führt eine Abfrage in einer SQL-Datenbank aus, um Kundendaten abzurufen. 
        
        Es filtert die Kunden anhand einer ERP-Nummer-Range und extrahiert dann die API-IDs aller gefundenen Kunden. 
        
        Am Ende wird eine Methode namens "init_sync_BRIDGE_to_SW" aufgerufen, um die gefundenen Kunden zu synchronisieren.
        
        """


        )



    def help(self):
        methods = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__")]
        print(colored("\nAvailable methods:", "green"))
        for method in methods:
            print(colored("- " + method + ":", "yellow"), end=" ")
            print(colored(getattr(self, method).__doc__, "cyan"))

atti_hilfe = Helper()