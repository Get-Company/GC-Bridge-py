# A try with selenium

from main.src.Controller.ControllerObject import ControllerObject
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# SP-API Amazon Tutorial: https://youtu.be/bHBFElmWRNg?t=823

class AmazonController(ControllerObject):
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("user-data-dir=C:\\Users\\fbuchner.CLASSEI\\AppData\\Local\\Google\\Chrome\\User Data")
        self.driver = webdriver.Chrome("D:\htdocs\python\GC-Bridge\chrome\chromedriver_109.exe", options=self.options)
        self.username_id_field = 'ap_email'
        self.user_name = 'amazon@classei.de'
        self.password_id_field = 'ap_password'
        self.password = 'AENth7RYB$QLd+mXX(%E'
        self.submit_id_field = 'signInSubmit'

    def open_seller_central(self):
        # Open Urla
        self.driver.get("https://sellercentral.amazon.de/signin?ref_=scde_soa_wp_signin_n")
        # Find Login
        return True

    def fill_user(self):
        # Finden Sie die Elemente des Login-Formulars
        username = self.driver.find_element(By.ID, self.username_id_field)
        username.send_keys(self.user_name)
        return True

    def fill_password(self):
        # Finden Sie das Passwort-Feld
        password = self.driver.find_element(By.ID, self.password_id_field)
        password = self.driver.find_element(By.ID, self.password_id_field)
        password.send_keys(self.password)
        return True

    def click_submit(self):
        submit = self.driver.find_element(By.ID, self.submit_id_field)
        submit.click()

