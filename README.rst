Help Me
=======

A simple app for providing a simple help desk for users.

PREREQUISITES

Download and install Postgresql.

INSTALLATION

Set up database and user.
-Start the postgres server
-Open the psql console
-In your console run the following db commands (credentials found in settings.py)

CREATE DATABASE helpme;
CREATE USER django WITH PASSWORD 'password';
ALTER ROLE django SET client_encoding TO 'utf8';
ALTER ROLE django SET default_transaction_isolation TO 'read committed';
ALTER ROLE django SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE helpme TO django;

\q #exits the console

Create your virtual environment.
To install the package in the "develop" project, run the following command from the root of the repo:
> pip install -e .

This tells pip to install the package in the virtual environment but still keep things editable (by linking the package instead of copying it).

cd into the developer and run the Django project normally with 'manage.py runserver'
