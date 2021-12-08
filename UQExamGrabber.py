import os

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
    BASE_PATH = os.path.join(os.path.expanduser("~"), "Downloads")

OVERWRITE = True
TIMEOUT_DELAY = 5

for course in COURSES.split(","):
    course = course.strip()
    download_path = os.path.join(BASE_PATH, course)

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
        driver.get("https://auth.uq.edu.au/")

        try:
            WebDriverWait(driver, TIMEOUT_DELAY).until(EC.presence_of_element_located((By.ID, "username")))
        except TimeoutException:
            print(f"Timed out on:\n{driver.current_url}")
            exit(1)

        driver.find_element_by_id("username").send_keys(USERNAME)
        driver.find_element_by_id("password").send_keys(PASSWORD, Keys.RETURN)

        if driver.find_elements_by_class_name("sign-on__form-error"):
            print("Incorrect username or password!")
            exit(2)

        print(f"{course}: Fetching exams!")
        driver.get(f"https://www.library.uq.edu.au/exams/papers.php?stub={course}")

        try:
            WebDriverWait(driver, TIMEOUT_DELAY).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, course)))
        except TimeoutException:
            print(f"Timed out on:\n{driver.current_url}")
            continue

        if not os.path.exists(download_path):
            os.mkdir(download_path)

        links = [exam.get_attribute("href") for exam in driver.find_elements_by_partial_link_text(course)]

        print(f"{course}: Downloading exams to {download_path}")

        for i, link in enumerate(links):
            print(f"{course}: Downloading {i + 1}/{len(links)} exams!")

            filepath = os.path.join(download_path, link.split('/')[-1])

            if os.path.exists(filepath) and OVERWRITE:
                os.remove(filepath)

            driver.get(link)

            while not os.path.exists(filepath):
                pass  # Waiting for exam to download

os.system("@ECHO OFF \ntaskkill /f /t /im chromedriver.exe")
exit(0)
