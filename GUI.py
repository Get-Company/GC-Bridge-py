import sys
from datetime import datetime, timedelta

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QLabel
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import QThread, pyqtSignal
from main.gcbridge import main
from main.src.Controller.ERP.ERPCustomerController import ERPCustomerController
from main.src.Controller.ERP.ERPOrderController import ERPOrderController
from main.src.Controller.SW5_2.SW5_2CustomerObjectController import SW5_2CustomerObjectController
from main.src.Controller.SW5_2.SW5_2OrderObjectController import SW5_2OrderObjectController
from main.src.Entity.Bridge.Customer.BridgeCustomerEntity import BridgeCustomerEntity
from main.src.Entity.ERP.ERPConnectionEntity import ERPConnectionEntity
from main.src.Entity.SW5_2.SW5_2CustomerObjectEntity import SW5_2CustomerObjectEntity
from main.src.Entity.SW5_2.SW5_2OrderObjectEntity import SW5_2OrderObjectEntity





class WriteStream:
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, text):
        self.text_edit.append(text)

    def flush(self):
        pass


class WorkerThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        erp_obj = ERPConnectionEntity(mandant="58")
        erp_obj.connect()

        yesterday = datetime.today() - timedelta(days=1)
        orders = SW5_2OrderObjectEntity().get_open_orders_by_startdate(startdate=yesterday)
        for order in orders["data"]:
            customer = SW5_2CustomerObjectEntity().get_customer(order["customerId"])
            # Atti
            SW5_2CustomerObjectController().get_new_customer(customer)
            # Flo
            # SW5_2CustomerObjectController().sync_customer(customer=customer["data"])
            customer_double = SW5_2CustomerObjectEntity().get_all_customers_by_adrnr(adrnr=customer["data"]["number"])
            if customer_double["total"] > 1:
                print("Kein Sync! Doppelter Kunde:")
                # SW5_2CustomerObjectController().delete_duplicates_by_adrnr(adrnr=customer["data"]["number"])
            else:
                print("Super, alles ok")
                ERPCustomerController(erp_obj=erp_obj).sync_ranged(start=customer["data"]["number"],end=customer["data"]["number"])

                # Write back the new customer_number
                print("Forward Customer Number", customer["data"]["id"])
                bridge_customer = BridgeCustomerEntity().query.filter_by(api_id=customer["data"]["id"]).one_or_none()

                sw5_customer = SW5_2CustomerObjectEntity()
                # number_added = sw5_customer.set_customer_number_by_id(customer_id=bridge_customer.api_id, number=bridge_customer.erp_nr)
                # print(number_added)

            order_details = SW5_2OrderObjectEntity().get_order_by_id(order["id"])
            order_data = SW5_2OrderObjectController().get_orders(order_details)
            SW5_2OrderObjectController().insert_order_data(order_data)

        bestellungen = ERPOrderController(erp_obj=erp_obj)
        bestellungen.get_new_orders()
        bestellungen.create_new_orders_in_erp()

        erp_obj.close()



class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GC-Bridge (FlAt)")
        self.setGeometry(100, 100, 400, 400)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)

        self.description_label = QLabel(self)
        self.description_label.setGeometry(10, 10, 380, 50)
        self.description_label.setText("Dieses Programm ist für die Synchronisierung von Shop und Büro+ verantwortlich.\nDas Programm kann gestartet, gestoppt und neu gestartet werden.\nBei Fehlern wenden Sie sich bitte an Florian oder Attila.")
        self.description_label.setStyleSheet("color: white")

        self.start_button = QPushButton("Bestellungen holen", self)
        self.start_button.setGeometry(50, 80, 100, 30)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setGeometry(160, 80, 100, 30)

        self.restart_button = QPushButton("Neu starten", self)
        self.restart_button.setGeometry(270, 80, 100, 30)

        self.console_textbox = QTextEdit(self)
        self.console_textbox.setGeometry(10, 120, 380, 270)
        self.console_textbox.setStyleSheet("color: black")

        self.start_button.clicked.connect(self.start_process)
        self.stop_button.clicked.connect(self.stop_process)
        self.restart_button.clicked.connect(self.restart_process)

        self.worker_thread = WorkerThread(parent=self)
        self.worker_thread.finished.connect(self.update_textbox)

    def start_process(self):
        self.console_textbox.append("Prozess gestartet.")
        self.worker_thread.start()

    def stop_process(self):
        self.console_textbox.append("Prozess gestoppt.")

    def restart_process(self):
        self.console_textbox.append("Prozess neu gestartet.")

    def update_textbox(self, orders):
        self.console_textbox.append(orders)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    app.setStyle('Fusion')
    window.show()
    sys.exit(app.exec_())
