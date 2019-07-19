from selenium import webdriver
from dateutil import parser as date_parser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import platform
import os, sys, sqlite3

def wait_until_clickable(driver, xpath=None, class_name=None,
                         duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver,
                      duration,
                      frequency).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    elif class_name:
        WebDriverWait(driver,
                      duration,
                      frequency).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))

def wait_until_visible(driver, xpath=None, class_name=None,
                       duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver,
                      duration,
                      frequency).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    elif class_name:
        WebDriverWait(driver,
                      duration,
                      frequency).until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))

def set_driver():
    if platform.system() == "Windows":
        binary = FirefoxBinary("C:\\Program Files\\Mozilla Firefox\\firefox.exe")
        return webdriver.Firefox(firefox_binary=binary,
                                   executable_path=r"C:\\geckodriver.exe")
    elif platform.system() == "Linux":
        return webdriver.Firefox()


# def start_db():
#     connection = sqlite3.connect("slub.db")
#     cursor = connection.cursor()
#     sql = "CREATE TABLE IF NOT EXISTS books("\
#         "barcode INTEGER PRIMARY KEY, title TEXT, author TEXT, enddate TEXT, \
#          extends INTEGER, comment TEXT)"
#     cursor.execute(sql)
#     connection.commit()
#     connection.close()
#
# start_db()


# @todo Add Notification
# @body database is too much, better would be a instant notficaiton system for example: telegram, google calendar, ticktick


driver = set_driver()

driver.get("https://www.slub-dresden.de/Shibboleth.sso/Login?target=https%3A%2F%2Fwww.slub-dresden.de%2Fkatalog%2Fmein-konto%2F%3F")

username_field = driver.find_element_by_id('username')
username_field.send_keys("4298969")
password_field = driver.find_element_by_id("password")
password_field.send_keys("4r4rt56freeJ/")
driver.find_element_by_name("_eventId_proceed").click()

book_table = "//table[@summary='Ausgeliehene Medien']"
wait_until_visible(driver=driver, xpath=book_table)

#book_list = driver.find_elements_by_tag_name("tbody")
#book_list.get_attribute
#print(len(book_list))

table = driver.find_element_by_xpath(book_table)
#tbody = table.find_elements_by_tag_name("tbody")
rows = table.find_elements_by_tag_name("tr")
print(len(rows))

def get_status(text, counts):
    status = ""
    if text == "Maximale Anzahl an Verlängerungen erreicht.":
        return "Maximale verlängerungen"
    elif text == "":
        return f"{counts} mal verlängert"
    elif text == "Exemplar ist vorgemerkt":
        return "zurückbringen"


for row in rows[1:]:
    #col = row.find_elements_by_tag_name("td")
    row_data = row.find_elements_by_tag_name("td")
    end_date = row_data[4].text
    name = row_data[2].text
    extend = get_status(row_data[6].text, row_data[5].text)

    print(end_date, name, extend)

driver.close()

