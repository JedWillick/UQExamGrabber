from setuptools import setup

# Get the long description from the README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='uqeg',
    version='0.2.4',
    description='Downloads past exams from the University of Queensland Library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jedwillick/UQExamGrabber',
    author='Jed Willick',
    license='MIT License',
    # author_email='',

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Students',
        'Topic :: UQ :: Exam :: Answers',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='UQ, Exam, Answers',

    packages=['uqeg'],

    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires='>=3.8',

    install_requires=['selenium'],

    entry_points={
        'console_scripts': [
            'uqeg=uqeg.uqeg:main',
        ],
    },

    project_urls={
        'Source': 'https://github.com/jedwillick/UQExamGrabber',
        'Bug Reports': 'https://github.com/jedwillick/UQExamGrabber/issues',
        'UQ Exam Papers': 'https://www.library.uq.edu.au/exams/'
    }
)
