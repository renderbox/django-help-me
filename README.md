![Help Me CI](https://github.com/renderbox/django-help-me/workflows/Help%20Me%20CI/badge.svg)

![Help Me Develop](https://github.com/renderbox/django-help-me/workflows/Help%20Me%20Develop/badge.svg?branch=develop)

[![Documentation Status](https://readthedocs.org/projects/django-help-me/badge/?version=latest)](https://django-help-me.readthedocs.io/en/latest/?badge=latest)

# Help Me

A simple app for providing a simple help desk for users.

## Prerequisites

This package makes use of JSON fields so you'll need Download and install Postgresql.  This will change with Django 3.1+ and the universal JSON field.

## Installation

It is highly reconmended that you use a Virtual Environment before installing.

To install, just use pip

```shell
> pip install django-permafrost
```

If you plan to use our templates you will need to installe these additional pacakges too (they are included in the 'dev' extensions):

```shell
> pip install django-crispy-forms django-multiselectfield
```


## For developers

If you haven't already, you will need to 
Set up database and user.
-Start the postgres server
-Open the psql console
-In your console run the following db commands (credentials found in settings.py)

```shell
CREATE DATABASE helpme;
CREATE USER django WITH PASSWORD 'password';
ALTER ROLE django SET client_encoding TO 'utf8';
ALTER ROLE django SET default_transaction_isolation TO 'read committed';
ALTER ROLE django SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE helpme TO django;

\q #exits the console
```

We have a pre-build 'develop' project we work from included in this repo.  It's very basic and is used for testing in a consistent Django environment.

First, create your virtual environment.

To install the necessary packages for the "develop" project, run the following command from the root of the repo:

```shell
> pip install -e .[dev]
```

This tells pip to install the package in the virtual environment but still keep things editable (by linking the package instead of copying it).


cd into the developer and apply any migrations...

```shell
> ./manage.py migrate
```


Create your superuser account...

```shell
> ./manage.py createsuperuser
```


Optionally load fixtures...

```shell
> ./manage.py loaddata developer
```


run the Django project normally with 

```shell
> ./manage.py runserver
```
