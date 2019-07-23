from selenium import webdriver
from dateutil import parser as date_parser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import platform
import os, sys, sqlite3
# @todo refactor for .gitignore crededentials
import config

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
    # @todo test headless mode
    if platform.system() == "Windows":
        binary = FirefoxBinary("C:\\Program Files\\Mozilla Firefox\\firefox.exe")
        return webdriver.Firefox(firefox_binary=binary,
                                   executable_path=r"C:\\geckodriver.exe")
    elif platform.system() == "Linux":
        return webdriver.Firefox()


def get_status(text, counts):
    status = ""
    if text == "Maximale Anzahl an Verlängerungen erreicht.":
        return "Maximale verlängerungen"
    elif text == "":
        return f"{counts} mal verlängert"
    elif text == "Exemplar ist vorgemerkt":
        return "zurückbringen"


def get_reserved():
    try:
        with open("reserved.txt", 'r') as file:
            return file.readlines().split()
    except IOError:
        file = open("reserved.txt", 'w')
        file.close()
        return []


# @todo update reserve list method
# @body merge with get_reserved and add the method in the pipeline
def update_reserved_list(books):
    # get_reserved() -> update -> write
    # delete lines (books) that are no longer in the book_list
    # add books that are not in the reserved list -> notification with enddate
    # save to file
    pass


def set_ticktick_reminder(driver, msg, date):

    driver.get("https://www.ticktick.com/")

    driver.find_element_by_class_name("signin__1cfzZ").click()
    wait_until_visible(driver, xpath="//input[@id='username']")
    driver.find_element_by_xpath("//a[@title='Google']").click()
    username_field = "//input[@id='identifierId']"
    wait_until_visible(driver, xpath=username_field)
    driver.find_element_by_xpath(username_field).send_keys(config.google_username)
    driver.find_element_by_xpath("//span[@class='CwaK9']").click()
    pw_field = "//input[@type='password']"
    wait_until_visible(driver, xpath=pw_field)
    driver.find_element_by_xpath(pw_field).send_keys(config.google_password)
    driver.find_element_by_xpath("//span[@class='CwaK9']").click()

    task_list_content = "//div[@id='task-list-content']"
    wait_until_visible(driver, task_list_content)
    driver.find_element_by_xpath("//a[@projectid='today']").click()
    import time
    time.sleep(2)
    from selenium.webdriver.common.keys import Keys
    driver.find_elements_by_tag_name("textarea")[1].\
        send_keys("#book", Keys.ENTER, msg + " " + date, Keys.ENTER)


def get_all_books(driver):
    driver.get(
        "https://www.slub-dresden.de/Shibboleth.sso/Login?target=https%3A%2F%2Fwww.slub-dresden.de%2Fkatalog%2Fmein-konto%2F%3F")

    username_field = driver.find_element_by_id('username')
    username_field.send_keys(config.slub_username)
    password_field = driver.find_element_by_id("password")
    password_field.send_keys(config.slub_password)
    driver.find_element_by_name("_eventId_proceed").click()

    book_table = "//table[@summary='Ausgeliehene Medien']"
    wait_until_visible(driver=driver, xpath=book_table)

    #
    table = driver.find_element_by_xpath(book_table)
    rows = table.find_elements_by_tag_name("tr")
    print(f"Recieved {len(rows)-1} books.")

    # @todo Extend books 3 days before enddate
    return rows[1:]

def print_all_books(books):
    for book in books:
        book_data = book.find_elements_by_tag_name("td")
        end_date = book_data[4].text
        name = book_data[2].text
        extend = get_status(book_data[6].text, book_data[5].text)

        print(end_date, name, extend)

driver = set_driver()

books = get_all_books(driver)
print_all_books(books)

# update_reserved_list(books)

# todo notification for books where enddate = date + 14
# @ body notification for every book that:
#       14 days in advance (if it can no longer be extended, only not
#           reserved ones)


driver.close()

