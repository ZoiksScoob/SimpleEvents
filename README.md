# SimpleEvents
A simple Event &amp; Ticket management web application


### Developing SimpleEvents

#### Setting Up A Virtual Environment

The required packages for this application to run are given in `requirements.txt`. An example of how to setup a virtual environment using `virtualenv` for this application is as follows:

1. Installing the virtual environment package can be done using pip on the command line.
    `pip install virtualenv`

2. Creating and activating the environment (on a windows machine) is then done with the 2 commands

    `python -m venv env`

    `source env/Scripts/activate`

3. Installing all needed packages 
    `pip install -r requirements.txt`


#### Readying The Application For Running

Before running the server, the database needs to be setup. This is done using the Flask-Migrate extension. The commands to execute in order are

    `python manage.py db init`

    `python manage.py db upgrade`

Once this is done, and the database is created (in the simple_events folder), the application can be started with the following command

    `python manage.py runserver`


#### Making Database Schema Changes

As the database is version controlled, each logically related set of changes to the database can be saved using the following command

    `python manage.py db upgrade --message`

    (`-m` can be used instead of `--message`)
