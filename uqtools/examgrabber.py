import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Union

from selenium.webdriver.common.by import By

from .driver import UQDriver
from .env import Env


def check_path(path: Union[str, Path]) -> Path:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        p.mkdir(parents=True)
    elif not p.is_dir():
        raise NotADirectoryError(f"{p} is not a directory")
    return p


def exam_grabber(
    env: Env,
    courses: List[str],
    baseOutDir: Union[str, Path] = ".",
    force=False,
    max_exams=0,
) -> int:
    baseOutDir = check_path(baseOutDir)

    with (
        TemporaryDirectory() as tmpDir,
        UQDriver(
            env,
            extra_exp={
                "prefs": {
                    "download.default_directory": tmpDir,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "plugins.always_open_pdf_externally": True,
                }
            },
        ) as driver,
    ):
        for course in courses:
            outDir = baseOutDir / f"{course}-exams"

            driver.get(f"https://www.library.uq.edu.au/exams/papers.php?stub={course}")

            if not driver.find_elements(
                By.XPATH, "//div[@id='examResultsDescription']"
            ):
                print(f"{course} has no past exams")
                continue

            check_path(outDir)

            links = [
                exam.get_attribute("href")
                for exam in driver.find_elements(By.PARTIAL_LINK_TEXT, course.upper())
            ]
            if max_exams:
                links = links[:max_exams]

            uri = outDir.as_uri()
            len_ = len(links)
            for i, link in enumerate(links, start=1):
                print(f"{course} {i}/{len_} @ {uri}", end="\r")

                file: Path = outDir / link.split("/")[-1]
                if file.exists():
                    if not force:
                        continue
                    file.unlink()

                driver.get(link)

                tmpFile = Path(tmpDir) / file.name

                while not tmpFile.exists():
                    pass  # Waiting for exam to download

                shutil.move(tmpFile, file)
            print()

    return 0
