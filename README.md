# databench-backend


## Backend Requirements

* [Docker](https://www.docker.com/).
* [Docker Compose](https://docs.docker.com/compose/install/).
* [Poetry](https://python-poetry.org/) for Python package and environment management.
* [Pre-commit](https://pre-commit.com/) for Git commit checks

## Backend local development

* Start the stack with Docker Compose:
You need to have installed docker compose and docker

```bash
./scripts/rebuild.sh
```

While the backend waits for the database to be ready and configures everything. You can check the logs to monitor it.

To check the logs, run:

```bash
docker-compose logs
```

To check the logs of a specific service, add the name of the service, e.g.:

```bash
docker-compose logs backend
```
or 
```bash
docker-compose logs db
```

* Now you can open your browser and interact with these URLs:

Automatic interactive documentation with Swagger UI (from the OpenAPI backend): http://localhost:8082/docs

Flow of interaction with APIs:

* First step is registration of user
* After that you need to log in via api. Copy your token and go to right top side of swagger page
Then click authorize button and fill in jwt the form with this jwt. After these action you are ready to play with APIs


* Running test is easy. Just run in root of the project.

```bash
./scripts/test.sh
```

* How to see created check for unauthorized user? 
You need to create a check via API and copy `url` field from the response. Just send it to any person.
Example: http://localhost:8082/api/checks/de783fe1f06047a3b452f666035b54f6/show-public


## Backend local development, additional details

### General workflow

By default, the dependencies are managed with [Poetry](https://python-poetry.org/), go there and install it.

From `/payment_app` you can install all the dependencies with:

```console
$ poetry install
```


### Migrations

As during local development your app directory is mounted as a volume inside the container, 
you can also run the migrations with `alembic` commands inside the container and the migration code will be in your app directory (instead of being only inside the container). 
So you can add it to your git repository.

Make sure you create a "revision" of your models and that you "upgrade" your database with that revision every time you change them. As this is what will update the tables in your database. Otherwise, your application will have errors.

There is a utility script which generates a migration file and places it into your `alembic/versions` folder:
```bash
./scripts/alembic_revision.sh "Revision message goes here"
```

Alternatively, you can use the old approach with where one needs to execute several commands:
* Start an interactive session in the backend container:

```console
$ docker-compose exec backend bash
```

* If you created a new model in `./app/models/`, make sure to import it in `./app/db/base.py`, 
that Python module (`base.py`) that imports all the models will be used by Alembic.

* After changing a model (for example, adding a column), inside the container, create a revision, e.g.:

```console
$ alembic revision --autogenerate -m "Add column last_name to User model"
```

* Commit to the git repository the files generated in the alembic directory.

* After creating the revision, run the migration in the database (this is what will actually change the database):

```console
$ alembic upgrade head
```


If you don't want to start with the default models and want to remove them / modify them, from the beginning, 
without having any previous revision, you can remove the revision files 
(`.py` Python files) under `./alembic/versions/`. And then create a first migration as described above.


