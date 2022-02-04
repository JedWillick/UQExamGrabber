import argparse
from pathlib import Path
from typing import Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def check_path(arg: Union[str, Path]) -> Path:
    p = Path(arg).expanduser().resolve()
    if not p.exists():
        p.mkdir(parents=True)
    elif not p.is_dir():
        raise argparse.ArgumentTypeError(f"{p} is not a directory")
    return p


def setup_argparse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download UQ exams")
    parser.add_argument("user", help="UQ username")
    parser.add_argument("pass_", metavar="pass",  help="UQ password")
    parser.add_argument("courses", type=lambda x: [course for course in x.split(",")],
                        help="List of courses to download")
    parser.add_argument("dir", nargs="?", type=Path, help="Base download directory (default: %(default)s)",
                        default=Path("~/Downloads/exams"))
    parser.add_argument("-t", "--timeout", type=int, default=5, help="Timeout delay (default: %(default)s)")
    parser.add_argument("-w", "--no-overwrite", action="store_false", dest="overwrite",
                        help="Don't overwrite existing files")
    parser.add_argument("-b", "--no-headless", action="store_false", dest="headless",
                        help="Don't use headless mode")
    return parser.parse_args()


def main() -> int:
    args = setup_argparse()
    args.dir = check_path(args.dir)

    for course in args.courses:
        download_path = args.dir / course

        options = webdriver.ChromeOptions()
        options.add_argument('--headless') if args.headless else None
        options.add_argument("--incognito")
        options.add_experimental_option('prefs', {
            "download.default_directory": str(download_path),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        })
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        with webdriver.Chrome(options=options) as driver:
            driver.implicitly_wait(args.timeout)
            driver.get("https://auth.uq.edu.au/")

            driver.find_element(By.ID, "username").send_keys(args.user)
            driver.find_element(By.ID, "password").send_keys(args.pass_, Keys.RETURN)

            if driver.current_url != "https://auth.uq.edu.au/idp/module.php/core/authenticate.php?as=uq":
                print("Failed to login!")
                return 1

            driver.get(f"https://www.library.uq.edu.au/exams/papers.php?stub={course}")

            if driver.execute_script("""return document.evaluate("//*[contains(text(),'not found any past exams')]",
                                     document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"""):
                print(f"{course} has no past exams")
                continue

            check_path(download_path)

            links = [exam.get_attribute("href") for exam in driver.find_elements(By.PARTIAL_LINK_TEXT, course.upper())]

            print(f"{course} @ {download_path.as_uri()}")

            for i, link in enumerate(links):
                print(f"Downloading {i + 1}/{len(links)} exams!", end="\r")

                filepath = download_path / link.split('/')[-1]
                filepath.unlink() if filepath.exists() and args.overwrite else None

                driver.get(link)

                while not filepath.exists():
                    pass  # Waiting for exam to download

            print()

    return 0
