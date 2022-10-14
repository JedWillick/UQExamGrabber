import math
import re
import sys
from datetime import datetime
from typing import List

import requests
from lxml import etree, html


def get_fully_qualified_semester(sem: int = None, year: int = None) -> str:
    """
    Converts a semester string to a fully qualified semester string.
    For summer semester enter 3 for the semester.
    Example output:
    "Semester 1, 2022"
    """
    today = datetime.now()
    if year is None:
        year = today.year

    if sem is None:
        month = today.month
        if 2 <= month < 6:
            sem = 1
        elif 6 <= month < 11:
            sem = 2
        else:
            sem = 3

    return f"Summer Semester, {year}" if sem == 3 else f"Semester {sem}, {year}"


def scrap_courses(courses: List[dict], qual_sem: str):
    """
    Scrap course information from UQ for the given semester
    and place it into the list of courses
    """
    with requests.Session() as s:
        s.headers.update({"User-Agent": "Mozilla/5.0"})
        for course in courses:
            page = s.get(
                "https://my.uq.edu.au/programs-courses/course.html?course_code="
                + course["code"],
            )
            tree = html.fromstring(page.text)
            profile = tree.xpath(
                f"//table[@class='offerings']//a[contains(.,'{qual_sem}')]"
                "/../..//a[@class='profile-available']"
            )
            if len(profile) == 0:
                print(
                    f"{course['code']} is not available for {qual_sem}.",
                    file=sys.stderr,
                )
                course["code"] = None
                continue
            profileUrl = profile[0].get("href").replace("section_1", "section_5")

            page = s.get(profileUrl)
            tree = html.fromstring(page.text)
            assessment = tree.xpath("//tbody/tr[*]/td[1]/a/br")
            course["assessment"] = [
                etree.tostring(a, encoding="unicode").replace("<br/>", "").strip()
                for a in assessment
            ]

            weights = tree.xpath("//tbody/tr[*]/td[3]")
            course["weights"] = [
                float(re.findall(rb"(\d+)", etree.tostring(w))[0]) for w in weights
            ]


def input_float(prompt: str, weight: float) -> float:
    """
    Prompts the user for a float.
    """
    s = input(prompt)
    if not s:
        return 0.0
    try:
        return float(s[:-1]) / 100 * weight if s[-1] == "%" else float(s)
    except ValueError:
        # Overwrite the same line and ask again
        print("Please enter a float or percentage.", end="\r")
        print("\x1b[1A\r\x1b[0K", end="\r")
        return input_float(prompt, weight)


def normalize_mark(mark: float, weight: float) -> float:
    """
    Ensure mark is between 0 and the weight.
    """
    if mark < 0:
        return 0
    if mark > weight:
        return weight
    return mark


def grade_scale(total: float) -> int:
    """
    Returns the grade scale for the given total.
    """
    total = round(total)
    if total < 20:
        return 1
    elif total < 45:
        return 2
    elif total < 50:
        return 3
    elif total < 65:
        return 4
    elif total < 75:
        return 5
    elif total < 85:
        return 6
    else:
        return 7


def print_marks(course: dict, prompt=False, pad=0) -> None:
    """
    Prompts the user for marks if required and prints the marks to stdout.
    """
    for i, assessment in enumerate(course["assessment"]):
        if prompt:
            print("\x1b[2K", end="\r")
            course["marks"].append(
                input_float(
                    f"{assessment:<{pad}} ({course['weights'][i]}): ",
                    course["weights"][i],
                )
            )
            print("\x1b[1A\r\x1b[0K", end="\r")

        course["marks"][i] = normalize_mark(course["marks"][i], course["weights"][i])
        print(f"{assessment:<{pad}} ({course['weights'][i]}): {course['marks'][i]}")


def grade(courses: List[dict], out=None, sem=None, year=None) -> int:
    """
    Grades the given courses.
    Example input:
    courses = [
        {
            "code": "csse2310",
            "marks": [15, 14.5, 13.95],
        },
        {
            "code": "csse2010",
            "marks": [],
        },
    ]
    "assessment" and "weights" will be added to the course dict once scrapped.
    """
    semString = get_fully_qualified_semester(sem, year)

    print("Scrapping course information...", end="\r")
    scrap_courses(courses, semString)
    print("\x1b[0K", end="\r")

    grades = []
    for course in courses:
        if course["code"] is None:
            continue
        print(f"== {course['code'].upper()} ==")
        pad = max(len(course) for course in course["assessment"]) + 1
        if len(course["marks"]) == 0:
            print_marks(course, prompt=True, pad=pad)
        else:
            expect = len(course["assessment"])
            actual = len(course["marks"])
            if actual < expect:
                course["marks"] += [0.0] * (expect - actual)
            else:
                course["marks"] = course["marks"][:expect]

            print_marks(course, pad=pad)

        total = math.fsum(course["marks"])
        print(f"{'Total':<{pad-1}} (100.0): {total}")
        scale = grade_scale(total)
        grades.append(scale)
        print(f"{'Current Grade':<{pad+3}} (7): {scale}")

        CUTOFFS = {1: 0, 2: 20, 3: 45, 4: 50, 5: 65, 6: 75, 7: 85}

        for i in range(scale + 1, 8):
            print(f"To get a {i} you need {CUTOFFS[i] - total:.2f} more percent")
        print()
    if grades:
        print(f"Overall Grade: {sum(grades) / len(grades):.2f}")
    return not grades
