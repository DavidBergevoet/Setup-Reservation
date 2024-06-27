# Scheduler for test setup Corn #

You can schedule time for test setup corn


## Install steps ##

* Create Virtual environment

`python3 -m venv .venv`

* Activate virtual environment

`. .venv/bin/activate`

* Install neccesary packages

`pip install -r requirements.txt`

* Updating packages

    If a new package is installed, this command should be run
    
    `pip freeze > requirements.txt`

## Format code ##

To format python code to match the [PEP 8 standard](https://peps.python.org/pep-0008/), execute the following formatter in the root directory of the repository:

    autopep8 --in-place --recursive .
