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

### Installation ###

To install autopep8, use the following command: 

    pip install autopep8

To format python code to match the [PEP 8 standard](https://peps.python.org/pep-0008/), execute the following formatter in the root directory of the repository:

    autopep8 --in-place --recursive .

## Configuration file ##

For the application to run, you will need a configuration file called: config.json

An example of such a file is listed in config.json.example. The `title_image` is the path to the image of that specific setup, which needs to be placed in the `static/title_images/` directory. Only the name of that file needs to be entered, since the application will only look in the title_images directory.
