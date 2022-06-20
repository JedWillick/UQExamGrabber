# UQ Tools

My collection of tools for scrapping [UQ](https://www.uq.edu.au/).

## Setup

```shell
pip install git+https://github.com/jedwillick/uqtools
uqtools --help
```

## Dependencies

- Chrome and [chromedriver](https://chromedriver.chromium.org/downloads)
- selenium, python-dotenv, reportlab, requests, lxml

## UQ Course Grade Calculator

Calculate what grade you will get and how much more you need to get with the given marks.

```shell
uqtools gr --help

uqtools gr csse2310,15,13.5,14,12.25  deco2500
```

## UQ Exam Grabber

Using Selenium and chromedriver, automatically log-in to [UQ library](https://www.library.uq.edu.au/exams/) and download all past exams for the specified
courses.

```shell
uqtools eg --help

uqtools eg csse2310 csse2010 comp3400
uqtools eg math1051 -o ~/Documents/uq-exams
```

## UQ Timetable

Scrap your allocated classes from [Allocate+](http://my.uq.edu.au/student-timetable) and output them in a prettier and cleaner PDF file.

```shell
uqtools tt --help

uqtools tt
uqtools tt -o tt.pdf
uqtools tt -r portrait --time-size 30 
```

### Injecting data

You can inject your own data in addition to that gathered from [Allocate+](http://my.uq.edu.au/student-timetable) by providing a json file with the `-i` flag

#### Template

```json
{
  "unique_key": {
    "semester": "S1",
    "subject_code": "Title",
    "activityType": "Activity",
    "day_of_week": "Sat",
    "start_time": "14:30",
    "location": "Home",
    "duration": 90
  }
}
```
