from selenium import webdriver
from dateutil import parser as date_parser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import platform
import datetime
import time
import os, sys, sqlite3
from selenium.common.exceptions import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

# crededentials
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
    options = Options()
    options.headless = True
    if platform.system() == "Windows":
        binary = FirefoxBinary("C:\\Program Files\\Mozilla Firefox\\firefox.exe")
        return webdriver.Firefox(options=options, firefox_binary=binary,
                                   executable_path=r"C:\\geckodriver.exe")
    elif platform.system() == "Linux":
        return webdriver.Firefox(options=options)


def get_file(file):
    try:
        with open(f"{file}.txt", 'r') as file:
            return file.read().split("\n")
    except IOError:
        return []

def test_reserved(title):
    for book in reserved_list:
        if title == book:
            return True
    return False


def update_reserved_list(books):
    global reminder_list
    global reserved_list
    new_reservedlist = []
    for book in books:
        book_data = book.find_elements_by_tag_name("td")
        title = book_data[2].text
        extend = book_data[6].text
        enddate = book_data[4].text
        if extend == "Exemplar ist vorgemerkt":
            new_reservedlist.append(title)
            if not test_reserved(title):
                reminder_list.append([f"{title} vorg. für", f"{enddate}"])

    reserved_list = new_reservedlist
    with open("reserved.txt", "w") as file:
        for book in reserved_list:
            file.write(book + "\n")
    # get_reserved() -> update -> write
    # delete lines (books) that are no longer in the book_list
    # add books that are not in the reserved list -> notification with enddate
    # save to file
    pass


def set_ticktick_reminder(driver):

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

    time.sleep(2)
    global reminder_list
    for reminder in reminder_list:
        dateformat = reminder[1].split(" ")
        dateformat = dateformat[0] + " " + dateformat[1][:3] + "M"
        driver.find_elements_by_tag_name("textarea")[1].send_keys("#book", Keys.ENTER, reminder[0] + " " + dateformat, Keys.ENTER)
        print("reminded")
        time.sleep(2)


def get_all_books(driver):
    def get_books(driver):
        book_table = "//table[@summary='Ausgeliehene Medien']"
        wait_until_visible(driver=driver, xpath=book_table)

        table = driver.find_element_by_xpath(book_table)
        rows = table.find_elements_by_tag_name("tr")
        print(f"Recieved {len(rows)-1} books.")
        return rows[1:]

    global reminder_list
    driver.get(
        "https://www.slub-dresden.de/Shibboleth.sso/Login?target=https%3A%2F%2Fwww.slub-dresden.de%2Fkatalog%2Fmein-konto%2F%3F")

    username_field = driver.find_element_by_id('username')
    username_field.send_keys(config.slub_username)
    password_field = driver.find_element_by_id("password")
    password_field.send_keys(config.slub_password)
    driver.find_element_by_name("_eventId_proceed").click()

    reminded = get_file("reminded")

    books = get_books(driver)
    book_titles = [book.find_elements_by_tag_name("td")[2].text for book in books]
    for title in reminded:
        if title not in book_titles:
            reminded.remove(title)

    extended_ones = 0
    for book in books:
        book_data = book.find_elements_by_tag_name("td")
        print(book_data[2].text)

        if book_data[6].text == "":
            if book_data[2].text in reminded:
                reminded.remove(book_data[2].text)
            if test_reserved(book_data[2].text):
                reminder_list.append([f"n.m.v., {book_data[2].text} ({book_data[5].text}), ", f"{book_data[4].text}"])
            due_box = book_data[6].find_element_by_xpath(".//input[@type='checkbox']")
            due_days = int(due_box.get_attribute("data-days-to-due"))
            if due_days <= 3:
                due_box.click()
                select_button = "//div[@class='ui-dialog-buttonset']/button[1]"
                extended_ones += 1
                print("selected one more")
                time.sleep(1)
                try:
                    if EC.element_to_be_clickable((By.XPATH, select_button)):
                        driver.find_element_by_xpath(select_button).click()
                except NoSuchElementException:
                    pass
        elif book_data[6].text == "Maximale Anzahl an Verlängerungen erreicht.":
            try:
                if (datetime.datetime.strptime(book_data[4].find_element_by_xpath(".//span[@class='hidden']").get_attribute("textContent"), "%Y-%m-%d") - datetime.datetime.today()).days + 1 <= 14:
                    print(reminded)
                    if book_data[2].text not in reminded:
                        reminder_list.append([f"m.v.e. {book_data[2].text}", f"{book_data[4].text}"])
                        reminded.append(book_data[2].text)
            except ValueError:
                print("error")

    if extended_ones > 0:
        wait_until_clickable(driver, xpath="//input[@id='btnSubmitIssued']", duration=3)
        driver.find_element_by_xpath("//input[@id='btnSubmitIssued']").click()


    with open("reminded.txt", "w") as file:
        for book in reminded:
            file.write(book + "\n")

    print(reminded)
    return get_books(driver)


def get_status(text, counts):
    if text == "Maximale Anzahl an Verlängerungen erreicht.":
        return "Maximale verlängerungen"
    elif text == "":
        return f"{counts} mal verlängert"
    elif text == "Exemplar ist vorgemerkt":
        return "zurückbringen"


def print_all_books(books):
    for book in books:
        book_data = book.find_elements_by_tag_name("td")
        end_date = book_data[4].text
        name = book_data[2].text
        extend = get_status(book_data[6].text, book_data[5].text)

        print(end_date, name, extend)


reserved_list = get_file("reserved")
reminder_list = []
driver = set_driver()

books = get_all_books(driver)


print_all_books(books)

update_reserved_list(books)

print(reminder_list)
set_ticktick_reminder(driver)
driver.quit()

