# UQ Tools

My collection of tools for scrapping [UQ](https://www.uq.edu.au/).

## Setup

```shell
pip install git+https://github.com/jedwillick/uqtools
uqtools --help
```

## Dependencies

- Chrome and chromedriver <https://chromedriver.chromium.org/downloads>
- selenium, python-dotenv, reportlab

## UQ Exam Grabber

Using Selenium and chromedriver, automatically log-in to [UQ library](https://www.library.uq.edu.au/exams/) and download all past exams for the specified
courses.

```shell
uqtools eg --help

uqtools eg csse2310,csse2010,comp3400
uqtools eg math1051 -o ~/Documents/uq-exams
```

## UQ Timetable

Scrap your allocated classes from [Allocate+](http://my.uq.edu.au/student-timetable) and output them in a prettier and cleaner PDF or excel file.

```shell
uqtools tt --help

uqtools tt
uqtools tt -o tt.pdf
uqtools tt --time-size 30 --open
```
