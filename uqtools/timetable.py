import datetime
import re
from pathlib import Path
from typing import Union

from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .driver import UQDriver
from .env import Env


def day_to_int(day: str) -> int:
    if day == "Mon":
        return 1
    elif day == "Tue":
        return 2
    elif day == "Wed":
        return 3
    elif day == "Thu":
        return 4
    elif day == "Fri":
        return 5
    elif day == "Sat":
        return 6
    elif day == "Sun":
        return 7
    else:
        return -1


def current_semester() -> str:
    month = datetime.datetime.now().month
    if 2 <= month < 6:
        return "S1"
    elif 6 <= month < 11:
        return "S2"
    else:
        return "S3"


def starttime_to_index(time: datetime.datetime, lower: int) -> int:
    index = (4 * time.hour) - (4 * lower) + 2
    if time.minute == 15:
        index += 1
    elif time.minute == 30:
        index += 2
    elif time.minute == 45:
        index += 3
    return index


def current_year() -> str:
    return "odd" if datetime.datetime.now().year % 2 else "even"


def code_to_year(code: str) -> int:
    year = datetime.datetime.now().year
    if code == "odd" and year % 2 == 0:
        return year - 1
    if code == "even" and year % 2 == 1:
        return year + 1
    return year


def timetable(env: Env,
              out: Union[Path, str] = None,
              semester: str = None,
              year: str = None,
              time_size: int = 60,
              fetch: bool = True,
              inject: dict = None,
              orientation: str = "landscape") -> Path:

    PALLET = ["#f8cbad", "#c6e0b4", "#bdd7ee", "#ffe699", "#e2a2f6", "#d9d9d9"]
    DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    DEF_MIN = 8
    DEF_MAX = 18

    semester = semester if semester else current_semester()
    year = year if year else current_year()
    out = Path(out if out else f"timetable-{code_to_year(year)}-{semester}.pdf").expanduser().resolve()

    raw = {}
    if fetch:
        with UQDriver(env) as driver:
            driver.get(f"https://timetable.my.uq.edu.au/{year}/student")
            driver.wait.until(EC.presence_of_element_located((By.XPATH, "//script[contains(text(), 'data=')]")))
            raw = driver.execute_script("return data.student.allocated;")

    if inject:
        raw |= inject

    details = []
    for i in raw.values():
        if i["semester"] != semester:
            continue
        i["start_time"] = datetime.datetime.strptime(i["start_time"], "%H:%M")
        i["duration"] = int(i["duration"])
        details.append(i)

    lower = min(i["start_time"] for i in details).hour
    lower = lower if lower < DEF_MIN else DEF_MIN
    upper = max(i["start_time"] + datetime.timedelta(minutes=i["duration"]) for i in details)
    upper = upper.hour if upper.hour > DEF_MAX else DEF_MAX
    time_span = upper - lower + 1

    details = [
        [
            re.findall(r"[^_]+", i["subject_code"])[0],
            i["activity_group_code"],
            day_to_int(i["day_of_week"]),
            starttime_to_index(i["start_time"], lower),
            "ONLINE" if i["location"] == "-" else re.findall(r"\S*", i["location"])[0],
            (i["duration"] // 15) - 1,
        ]
        for i in details
    ]

    courses = list(set(details[i][0] for i in range(len(details))))

    if orientation == "portrait":
        days = DAYS[:-2]
        pagesize = portrait(A4)
        a4 = A4[::-1]
    else:
        days = DAYS
        pagesize = landscape(A4)
        a4 = A4

    doc = SimpleDocTemplate(
        str(out),
        pagesize=pagesize,
        topMargin=10,
        bottomMargin=10,
        leftMargin=10,
        rightMargin=10,
    )

    border_width = 2
    border_color = 'rgb(0, 0, 0)'

    grid_width = 1
    grid_color = 'rgb(0, 0, 0)'

    table_style = TableStyle([
        # Main Section
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (1, 0), (-1, -1), 'MIDDLE'),
        ('FONT', (1, 1), (-1, -1), 'Helvetica', 12),

        # Days
        ('INNERGRID', (1, 0), (-1, 1), grid_width, grid_color),
        ('FONT', (1, 0), (-1, 0), 'Helvetica-Bold', 14),

        # Hours
        ('VALIGN', (0, 1), (0, -1), 'TOP'),
        ('FONT', (0, 1), (0, -1), 'Helvetica-Bold', 14),
    ])

    for i in range(len(days)):
        table_style.add('SPAN', (i + 1, 0), (i + 1, 1))

    for row in range(0, time_span * 4, 2):
        for col in range(8):
            midcol = col + 1 if time_size == 60 else col
            table_style.add('LINEABOVE', (midcol, row + 2), (-midcol, row + 2), 1,  'rgb(191, 191, 191)')

    for row in range(1, time_span * 4, 4):
        for col in range(8):
            table_style.add('BOX', (col, row + 1), (col, -row), grid_width, grid_color)

    # Borders
    table_style.add('BOX', (1, 2), (-1, -1), border_width, border_color)
    table_style.add('BOX', (1, 0), (-1, 1), border_width, border_color)
    table_style.add('BOX', (0, 2), (0, -1), border_width, border_color)

    filler = [''] * (len(days) + 1)

    tt = [[''] + days] + [filler]

    for hour in range(lower, upper + 1):
        tt.append([datetime.time(hour=hour).strftime("%H:%M")] + filler[:-1])
        tt.append([*filler])
        if time_size == 30:
            tt.append([datetime.time(hour=hour, minute=30).strftime("%H:%M")] + filler[:-1])
        else:
            tt.append([*filler])
        tt.append([*filler])

    for code, group, day, hour, location, duration in details:
        text = code
        if location:
            text += "\n" + location
        if group:
            text += "\n" + group
        tt[hour][day] = text

        for course, fill in zip(courses, PALLET):
            if course == code:
                table_style.add('BACKGROUND', (day, hour), (day, hour), fill)
                break

        table_style.add('SPAN', (day, hour), (day, hour + duration))
        table_style.add('BOX', (day, hour), (day, hour + duration), grid_width, grid_color)

    table = Table(
        tt,
        colWidths=round(a4[1] / len(tt[0])) - 4,
        rowHeights=round(a4[0] / len(tt)) - 1,
        style=table_style
    )

    doc.build([table])
    print(out.as_uri())
    return out
