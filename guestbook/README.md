# Guest Book application in Python 3

A simple [Flask](http://flask.pocoo.org/) application that may be useful
in various demos. It stores data in PostgreSQL database.


## How to install dependencies on Fedora:

```
#> dnf -y install python-flask python-tables
#> pip install dataset
```

## How to run the application

Let's say PostgreSQL is running and `guestbook` database is created, while
user `guestbook` may access this database and uses password `secretpassword`.
Then the application may be run like this:

```
export DB_PORT_5432_TCP_ADDR=localhost
export DB_PORT_5432_TCP_PORT=5432
export DB_ENV_POSTGRESQL_USER=guestbook
export DB_ENV_POSTGRESQL_PASSWORD=secretpasswor
export DB_ENV_POSTGRESQL_DATABASE=guestbook
./app.py
```

The application runs on localhost:5000 by default, so you may use your
favourite browser to access it.
