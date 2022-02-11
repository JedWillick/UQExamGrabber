import re
from datetime import datetime, time
from pathlib import Path
from subprocess import Popen

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

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
    x = int(duration)
    if x == 60:
        return 1
    elif x == 90:
        return 2
    elif x == 120:
        return 3


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


class Timetable:
    PALLET = ['rgb(248, 203, 173)', 'rgb(198, 224, 180)', 'rgb(189, 215, 238)', 'rgb(255, 230, 153)', 'rgb(226, 162, 246)',
              'rgb(217, 217, 217)']

    def __init__(self, env: Env, semester=None, year=None) -> None:
        self.env = env

        self.semester = semester if semester else current_semester()
        self.year = year if year else current_year()

        self.timetable = self.get_timetable()
        self.courses = list(set(self.timetable[i][0] for i in range(len(self.timetable))))

    def get_timetable(self):
        with UQDriver(self.env) as driver:
            driver.get(f"https://timetable.my.uq.edu.au/{self.year}/student")
            data = driver.execute_script("return data.student.allocated;")

        timetable = [
            [
                re.findall(r"[^_]+", i["subject_code"])[0],
                i["activity_group_code"],
                day_to_int(i["day_of_week"]),
                starttime_to_index(i["start_time"]),
                re.findall(r"\S+", i["location"])[0] if i["location"] != "-" else "ONLINE",
                duration_to_span(i["duration"])
            ]
            for i in data.values() if i["semester"] == self.semester
        ]
        return timetable

    def write(self, out=None, excel=False, time_size=60, open=False):
        out = out if out else f"timetable-{datetime.now().year}-{self.semester}{'.xlsx' if excel else '.pdf'}"
        print(excel)
        self.write_excel(out, time_size) if excel else self.write_pdf(out, time_size)

        if open:
            Popen([Path(f"./{out}")], shell=True)

    def write_pdf(self, out, time_size=60):

        doc = SimpleDocTemplate(out, pagesize=landscape(A4), topMargin=0, bottomMargin=0)

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

        data = [['', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]

        for hour in range(8, 19):
            data.append([time(hour=hour).strftime("%H:%M")] + [''] * 7)
            if time_size == 60:
                data.append([''] * 8)
            else:
                data.append([time(hour=hour, minute=30).strftime("%H:%M")] + [''] * 7)

        for code, group, day, hour, location, duration in self.timetable:
            data[hour][day] = f"{code}\n{location}\n{group}"
            for course, fill in zip(self.courses, self.PALLET):
                if course == code:
                    table_style.add('BACKGROUND', (day, hour), (day, hour), fill)
                    break

            table_style.add('SPAN', (day, hour), (day, hour + duration))
            table_style.add('BOX', (day, hour), (day, hour + duration), grid_width, grid_color)

        doc.build([Table(data, colWidths=100, rowHeights=(A4[0]//len(data))-1, style=table_style)])

    def write_excel(self, out, time_size=60):
        ...
