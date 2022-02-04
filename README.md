# UQ Exam Grabber

Using Selenium and chromedriver, automatically log-in to [UQ library](https://www.library.uq.edu.au/exams/) and download all past exams for the specified
courses.

## Setup

```shell
git clone https://github.com/jedwillick/UQExamGrabber.git
cd UQExamGrabber
pip install . 
uqeg -h
```

### Examples

```shell
uqeg s1234567 password123 csse2310,csse2010,comp3400
uqeg s1234567 password123 csse2310,csse2010,comp3400 ~/Documents/uq-exams
```

## Dependencies

- Selenium (downloaded automatically through setup)
- Chrome and chromedriver <https://chromedriver.chromium.org/downloads>
