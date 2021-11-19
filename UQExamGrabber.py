import os
import shutil
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

USERNAME = input("Enter UQ username: ")
PASSWORD = input("Enter UQ password: ")
COURSES = input("Courses seperated by ',': ")
BASE_PATH = input("Enter base download path (if empty defaults to downloads): ")

if BASE_PATH == "":
    BASE_PATH = os.path.expanduser("~") + "\\Downloads\\"

REMOVE_EXISTING = True
TIMEOUT_DELAY = 5
BASE_URL = "https://www.library.uq.edu.au/exams/papers.php?stub="

for course in COURSES.split(","):
    course = course.strip()
    print(f"{course}: Fetching exams!")
    download_path = f"{BASE_PATH + course}"

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--incognito")
    options.add_argument('--hide-scrollbars')
    options.add_experimental_option('prefs', {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    })

    with webdriver.Chrome(options=options) as driver:
        driver.get("https://www.library.uq.edu.au/exams/papers.php?stub=" + course)

        try:
            element = WebDriverWait(driver, TIMEOUT_DELAY).until(EC.presence_of_element_located((By.ID, "username")))
        except TimeoutException:
            print(f"Timed out on:\n{driver.current_url}")
            exit(1)

        driver.find_element_by_id("username").send_keys(USERNAME)
        driver.find_element_by_id("password").send_keys(PASSWORD, Keys.RETURN)

        if driver.find_elements_by_class_name("sign-on__form-error"):
            print("Incorrect username or password!")
            exit(2)

        try: element = WebDriverWait(driver, TIMEOUT_DELAY).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='a']/a")))
        except TimeoutException:
            print(f"Timed out on:\n{driver.current_url}")
            continue

        if os.path.exists(download_path) and REMOVE_EXISTING:
            shutil.rmtree(download_path)

        if not os.path.exists(download_path):
            os.mkdir(download_path)

        links = [exam.get_attribute("href") for exam in driver.find_elements_by_xpath("//div[@class='a']/a")]
        for i, link in enumerate(links):
            print(f"{course}: Downloading {i + 1}/{len(links)} exams!")
            driver.get(link)
            sleep(1)

os.system("@ECHO OFF \ntaskkill /f /t /im chromedriver.exe")
exit(0)
