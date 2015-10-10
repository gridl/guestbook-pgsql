# Guest Book Python application using Nulecule

This repository contains a simple [Flask](http://flask.pocoo.org/)-based guest book application with
[Nulecule specification](https://github.com/projectatomic/nulecule).
The application is mainly meant to experiment with the Nulecule in practice on a simple
Python 3 application that stores entries into PostgreSQL database.

Nulecule specification provides a standard way of defining
multi-container application's configuration without need to distribute
instructions to end-user. In other words, when packaging container-based
application with Nulecule, the only thing end-user needs to specify is
the necessary values and provider (kubernetes, docker or OpenShift).

## Content of this registry

* `guestbook/` - a simple Flask application (python 3) that stores information
  into PostgreSQL database using [python-dataset](https://dataset.readthedocs.org/en/latest/)
* `guestbook-atomicapp/` - Nulecule specification for guestbook app
* `postgresql-centos7-atomicapp/` - Nulecule specification for
  `centos/postgresql-94-centos7` image available in docker.io


## PostgreSQL docker container using Nulecule specification

PostgreSQL database image is already available in docker.io as
`centos/postgresql-94-centos7`. When running that image in docker, we need to
specify username, password and database name using environment variables.
In pure-docker world or kubernetes, user would read the documentation and
either write kubernetes configuration or run rather complicated docker
command using several `-e` parameters.

With Nulecule, user is only asked for necessary information interactively
or writes the values into prepared `answers.conf` sample file. That way
user doesn't need to read any documentation.

Since Nulecule is distributed inside container as well, we need to build
the docker image first:

```
cd postgresql-centos7-atomicapp
docker build -t projectatomic/postgresql-centos7-atomicapp:latest .
```

For more information about how this Nulecule, refer to the following files:

* `postgresql-centos7-atomicapp/Nulecule` -- Nulecule specification of the
  PostgreSQL container image
* `postgresql-centos7-atomicapp/Dockerfile` -- Dockerfile that is used to
  package the specification as docker container image
* `postgresql-centos7-atomicapp/artifacts` -- description of how the application
  can be run (see kubernetes or docker directories' content for more information)

Let's just shortly look at a part of the Nulecule specification that makes
the parameters of PostgreSQL image be specified easier:

```
...
    params:
      - name: db_user
        description: Database User
      - name: db_pass
        description: Database Password
      - name: db_name
        description: Database Name
...
```

If we wanted to run the PostgreSQL as Nulecule application, we would do it
this way:

```
atomic run projectatomic/postgresql-centos7-atomicapp
```

Without `answers.conf` file in the current directory, user is interactively
asked for database name, username and password.

And alternative way is to create the `answers.conf` file in a new directory, like this:

```
mkdir postgresql-atomicapp
cd postgresql-atomicapp
cat >answers.conf <<EOF
[general]
namespace = default
provider = docker

[postgresql-atomicapp]
db_user = guestbook
db_pass = secret-password
db_name = guestbook
EOF;
```

## Packaging Python 3 application using Nulecule specification

First, we need to create an application container. We'll use a Python 3.4 docker
image available in docker.io as `centos/python-34-centos7`. This image allows
to use [source-to-image](https://github.com/openshift/source-to-image/) utility,
which allows easily to take an application from git repository or as in the
following case from local source:

```
s2i build `pwd`/guestbook  docker.io/centos/python-34-centos7 guestbook

```

A new docker image called `guestbook` is then created as a layered image, that
contains guestbook app as well.

The application is created so that it takes the following environment
variables to connect to a database:

* `DB_PORT_5432_TCP_ADDR` -- IP address of the PostgreSQL database
* `DB_PORT_5432_TCP_PORT` -- port on which the PostgreSQL database is available on
* `DB_ENV_POSTGRESQL_USER` -- database user that is used to access the database in the application
* `DB_ENV_POSTGRESQL_PASSWORD` -- database password
* `DB_ENV_POSTGRESQL_DATABASE` -- database name

With the variables above we are able to run both the containers (database and application) with pure docker (without Nulecule) like this:

```
docker run --rm --name postgresql -e POSTGRESQL_USER=guestbook \
       -e POSTGRESQL_PASSWORD=secret -e POSTGRESQL_DATABASE=guestbook \
       docker.io/centos/postgresql-94-centos7
docker run --rm -p 5000:5000 --link postgresql:db guestbook
```

However, we don't want to make it that complicated to users, so let's package
the Nulecule specification for the application, while that one will reference
already created database application, that is packaged as docker container
`projectatomic/postgresql-centos7-atomicapp`:

```
cd guestbook-atomicapp/
docker build -t projectatomic/guestbook-atomicapp:latest .
```
(for more information about the Nulecule spec, Dockerfile and artifacts for docker and kubernetes providers, refer to files `Dockerfile`, `Nulecule` and `artifacts` directory in `guestbook-atomicapp/`)

Then, with already prepared `answers.conf`, which may be the same as above, we can run the while application like this:

```
atomict run projectatomic/guestbook-atomicapp
```

That will first run the PostgreSQL container and then also the guestbook
container. And you can test the running application by opening
`http://localhost:5000` in your favourite browser.


## Some hints

Even when the containers are being run in correct order, the postgresql database is not ready to accept connections immediately. So the guestbook application needs to be resilient for the case when it cannot connect to the database:

```
le not db and tries < 10:
    try:
        db = dataset.connect('postgresql://{username}:{password}@{host}:{port}/{dbname}'.format(
                              host=os.environ.get('DB_PORT_5432_TCP_ADDR'),
                              port=os.environ.get('DB_PORT_5432_TCP_PORT'),
                              username=os.environ.get('DB_ENV_POSTGRESQL_USER'),
                              password=os.environ.get('DB_ENV_POSTGRESQL_PASSWORD'),
                              dbname=os.environ.get('DB_ENV_POSTGRESQL_DATABASE')))
    except sqlalchemy.exc.OperationalError:
        time.sleep(2)

if not db:
    print('Error: could not connect to DB: {host}:{port}'.format(
          host=os.environ.get('DB_PORT_5432_TCP_ADDR'),
          port=os.environ.get('DB_PORT_5432_TCP_PORT')))
    exit(1)
```
