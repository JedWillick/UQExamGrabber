import re
from datetime import datetime, time
from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .driver import UQDriver
from .env import Env


def day_to_int(day):
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


def duration_to_span(duration):
    i = (int(duration) / 60)
    return int(i + (i - 1))


def current_semester():
    month = datetime.now().month
    if 2 <= month < 6:
        return "S1"
    elif 6 <= month < 11:
        return "S2"
    else:
        return "S3"


def starttime_to_index(time):
    time = datetime.strptime(time, "%H:%M")
    hour = time.hour
    index = (hour - 7) + (hour - 8)
    if time.minute:
        index += 1
    return index


def current_year() -> str:
    return "odd" if datetime.now().year % 2 else "even"


def code_to_year(code: str) -> int:
    year = datetime.now().year
    if code == "odd" and year % 2 == 0:
        return year - 1
    if code == "even" and year % 2 == 1:
        return year + 1
    return year


def timetable(env: Env,
              out: Path | str = None,
              semester: str = None,
              year: str = None,
              time_size: int = 60,
              fetch: bool = True,
              inject: dict = None) -> Path:

    PALLET = ["#f8cbad", "#c6e0b4", "#bdd7ee", "#ffe699", "#e2a2f6", "#d9d9d9"]
    DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    semester = semester if semester else current_semester()
    year = year if year else current_year()
    out = Path(out if out else f"timetable-{code_to_year(year)}-{semester}.pdf").expanduser().resolve()

    data = {}
    if fetch:
        with UQDriver(env) as driver:
            driver.get(f"https://timetable.my.uq.edu.au/{year}/student")
            driver.wait.until(EC.presence_of_element_located((By.XPATH, "//script[contains(text(), 'data=')]")))
            data = driver.execute_script("return data.student.allocated;")

    if inject:
        data |= inject

    tt = [
        [
            re.findall(r"[^_]+", i["subject_code"])[0],
            i["activity_group_code"],
            day_to_int(i["day_of_week"]),
            starttime_to_index(i["start_time"]),
            re.findall(r"\S+", i["location"])[0] if i["location"] != "-" else "ONLINE",
            duration_to_span(i["duration"])
        ]
        for i in data.values() if i["semester"] == semester
    ]

    courses = list(set(tt[i][0] for i in range(len(tt))))

    doc = SimpleDocTemplate(str(out), pagesize=landscape(A4), topMargin=0, bottomMargin=0)

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
        ('INNERGRID', (1, 0), (-1, 0), grid_width, grid_color),
        ('FONT', (1, 0), (-1, 0), 'Helvetica-Bold', 14),

        # Hours
        ('VALIGN', (0, 1), (0, -1), 'TOP'),
        ('FONT', (0, 1), (0, -1), 'Helvetica-Bold', 14),
    ])

    for row in range(1, 11 * 2, 2):
        for col in range(0, 8):
            midcol = col + 1 if time_size == 60 else col
            table_style.add('LINEABOVE', (midcol, row), (midcol, -row), 1,  'rgb(191, 191, 191)')
            table_style.add('BOX', (col, row), (col, -row), grid_width, grid_color)

    # Borders
    table_style.add('BOX', (1, 1), (-1, -1), border_width, border_color)
    table_style.add('BOX', (1, 0), (-1, 0), border_width, border_color)
    table_style.add('BOX', (0, 1), (0, -1), border_width, border_color)

    data = [[''] + DAYS]

    for hour in range(8, 19):
        data.append([time(hour=hour).strftime("%H:%M")] + [''] * 7)
        if time_size == 60:
            data.append([''] * 8)
        else:
            data.append([time(hour=hour, minute=30).strftime("%H:%M")] + [''] * 7)

    for code, group, day, hour, location, duration in tt:
        data[hour][day] = f"{code}\n{location}\n{group}"
        for course, fill in zip(courses, PALLET):
            if course == code:
                table_style.add('BACKGROUND', (day, hour), (day, hour), fill)
                break

        table_style.add('SPAN', (day, hour), (day, hour + duration))
        table_style.add('BOX', (day, hour), (day, hour + duration), grid_width, grid_color)

    doc.build([Table(data, colWidths=100, rowHeights=(A4[0]//len(data))-1, style=table_style)])

    print(out.as_uri())
    return out
