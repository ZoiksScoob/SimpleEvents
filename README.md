# SimpleEvents
A simple Event &amp; Ticket management web application by [Alex Brown](https://www.linkedin.com/in/alexander-jc-brown/)

These instructions assume you've pulled the lastest version of the respository.


## 1. Running The SimpleEvents API

#### 1.1. Creating The Database

Before running the server, the database needs to be setup. This is done using the Flask-Migrate extension. If there is already a database called `simple_events.db` in the `simple_events` folder then just the 2nd command needs of the below should be run to ensure the database is up to date, otherwise both of the below commands should be run in order in the command line:

    `python server/manage.py db init`

    `python server/manage.py db upgrade`


#### 1.2. Setting The Environment Variables

Then a secret key must be set in the environment, the environment variable that's expected is `SECRET_KEY`.

An optional environment variable is `AUTH_TOKEN_EXPIRY_SECONDS`, which sets how long tokens have before expiring. The defaults for which are set in the `config.py` file.


#### 1.3. Running

Once you've set the environment variables, the server can be run simply using the manager from the command line like so

    `python server/manage.py runserver`

The front end can be run simply with the following in the command line

    `python frontend/index.py


## 2. Developing The SimpleEvents API

#### 2.1. Setting Up A Virtual Environment

The required packages for this application to run are given in `requirements.txt`. An example of how to setup a virtual environment using `virtualenv` for this application is as follows:

1. Installing the virtual environment package can be done using pip on the command line.
    `pip install virtualenv`

2. Creating and activating the environment (on a windows machine) is then done with the 2 commands

    `python -m venv env`

    `source env/Scripts/activate`

3. Installing all needed packages 
    `pip install -r requirements.txt`


#### 2.2. Making Database Schema Changes

As the database is version controlled, each logically related set of changes to the database can be saved using the following command

    `python server/manage.py db upgrade --message`

    (`-m` can be used instead of `--message`)


## 3. Testing

#### 3.1 Testing The Server

The server in the backend can be test simplyby running the already written tests with the following command line command

    `python server/manage.py test`
