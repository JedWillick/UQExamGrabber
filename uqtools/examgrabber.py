from pathlib import Path
from typing import Union

from selenium.webdriver.common.by import By

from .driver import UQDriver
from .env import Env


def check_path(path: Union[str, Path]) -> Path:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        p.mkdir(parents=True)
    elif not p.is_dir():
        raise FileExistsError(f"{p} is not a directory")
    return p


def exam_grabber(env: Env, courses: list[str], out, overwrite=True) -> int:
    out = check_path(out)

    for course in courses:
        download_path = out / f"{course}-exams"

        exp = {
            "prefs": {
                "download.default_directory": str(download_path),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True,
            }
        }

        with UQDriver(env, extra_exp=exp) as driver:
            driver.get(f"https://www.library.uq.edu.au/exams/papers.php?stub={course}")

            if not driver.find_elements_by_xpath("//div[@id='examResultsDescription']"):
                print(f"{course} has no past exams")
                continue

            check_path(download_path)

            links = [
                exam.get_attribute("href")
                for exam in driver.find_elements(By.PARTIAL_LINK_TEXT, course.upper())
            ]

            print(f"{course} @ {download_path.as_uri()}")

            for i, link in enumerate(links):
                print(f"Downloading {i + 1}/{len(links)} exams!", end="\r")

                filepath = download_path / link.split("/")[-1]
                filepath.unlink() if filepath.exists() and overwrite else None

                driver.get(link)

                while not filepath.exists():
                    pass  # Waiting for exam to download

            print()

    return 0
