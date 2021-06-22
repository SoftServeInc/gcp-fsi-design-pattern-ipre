# Fulfillment service

The backend for the Google FSI Pattern project to provide functionality around financial advices, assets, transactions,
and more.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/pydanny/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## Libraries and tools

Main libraries and tools:

- `python 3.9` - a programming language that lets you work quickly and integrate systems more effectively;
- `MySQL` - a relational database for metadata;
- `Django` - web-framework that follows the model–template–views (MTV) architectural pattern, used as the main service
  library;
- `Django REST framework` - a toolkit for building API;
- `dj-rest-auth` - Authentication for Django Rest Framework;
- `gunicorn` - a WSGI HTTP Server.

For local development:

- `Swagger` - describes RESTful API on the `swagger/` endpoint;
- `pytest` - testing framework;
- `flake8` - tool for style guide enforcement;
- `isort` - a library to sort Python imports;
- `black` - the Python code formatter;
- `coverage`- a tool for measuring code coverage of Python programs;
- `pre-commit` - identifies simple issues and forces code style before commit;
- `debug_toolbar` - a configurable set of panels that display various debug information about the current
  request/response in local environment.

## Service setup

Set up the virtual environment (_anaconda_, _virtualenv_, etc.) and install requirements for
local (`requirements/local.txt`) or production (`requirements/production.txt`) purposes:

    $ pip install -r requirements/{local.txt/production.txt}

If you are using the local environment, you can install the pre-commit hook which will run `black`, `isort`, `flake8`
utils before commit:

    $ pre-commit install

### Settings

To run any command, you have to specify the list of environment variables.

Mandatory environment variables for local deployment:

- `DJANGO_SETTINGS_MODULE` - tells which configuration to use - production (`config.settings.production`)
  or for local purposes (`config.settings.local`);
- `DATABASE_URL` - MySQL address and credentials, must be provided in
  format `mysql://<user>:<password>@<host>:<port>/<db_name>`;
- `ML_SERVICE_URL` - the address of Portfolio Optimization service.

To run production deployment, you also have to specify additional variables:

- `DJANGO_ALLOWED_HOSTS` - A list of strings representing the host/domain names that backend can serve,
  e.g. `.example.com`;
- `DJANGO_SECRET_KEY` - used to provide cryptographic signing, and should be set to a unique, unpredictable value.

If you want to be able to access all data from admin page, you should also specify variables:
- `DJANGO_ADMIN_URL` - a string that will be used for the backend admin page, defaults to `admin/`;
- `GS_BUCKET_NAME` - a name of GCP bucket where the static files will be collected.

Optional variables:
- `DJANGO_SECURE_SSL_REDIRECT` - If `True`, the SecurityMiddleware redirects all non-HTTPS requests to HTTPS.

You can use `DJANGO_READ_DOT_ENV_FILE=True` variable if you want to read all the specified variables from the `.env`
file.

List of environment variables with examples for production usage:

- `DJANGO_SETTINGS_MODULE=config.settings.production`;
- `DJANGO_SECRET_KEY=222wWuBvHue7hFLDsRqYb4jwF5vXTeS8`;
- `DJANGO_ADMIN_URL=bwLER5KCdahVHksm/`;
- `DJANGO_ALLOWED_HOSTS=.run.app`;
- `GS_BUCKET_NAME=static-files-bucket`;
- `ML_SERVICE_URL=https://recommendation-engine.run.app`.
- `DATABASE_URL="mysql://user:password@/database?unix_socket=/tmp/gcp-project:location:database-name"`;
- `DJANGO_SECURE_SSL_REDIRECT=False`.

### Creating DB with schema

Create MySQL database:

    mysql$ create database <db_name>;

Create schema in the DB. To do that, use Django migrations feature which will define tables for all Django models.

To create a DB schema, run the command:

    $ python manage.py migrate

Also, each application contains `sql/` folder where dummy data is localed. Each application contains migration file
which fills DB with the dummy data.

### (Optional) Creating the superuser

Superuser can access `ADMIN_URL` and create/modify tables conveniently.

To create a superuser, run the command:

    $ DJANGO_SUPERUSER_PASSWORD=<password> python manage.py createsuperuser --no-input --email <email@email> --username <username>

### (Optional) Collecting static files

If you want to serve admin site, you should collect static files using command:

    $ python manage.py collectstatic --no-input

Don't forget to specify `GS_BUCKET_NAME` - it will be used to save the static files.

### (Optional) Testing

If you set up the local environment, you can run tests:

    $ pytest

Also, you can check code coverage and generate coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

### Deploying

1. To run the service in the local environment, you can use the built-in server:

       $ python manage.py runserver


2. To run the service in production, you can use `gunicorn`:

       $ gunicorn --bind :<port> config.wsgi:application


3. You can also use `Dockerfile` to run the application.

### Serving

At the start, the service contains 3 predefined users with some wallets, transactions, and purchased assets. You can log
in with these credentials to purchase a portfolio, serve home page, and more:

1. John Wick
    - username: `johnwick`;
    - password: `johnwick`;
    - wallets: `1`;
    - purchased assets: `5`;
    - ML UUID: `user-0000000000000001`.
2. Lyra King
    - username: `lyraking`;
    - password: `lyraking`;
    - wallets: `2`;
    - purchased assets: `7`;
    - ML UUID: `user-0000000000000501`.
3. Alex Ray
    - username: `alexray`;
    - password: `alexray`;
    - wallets: `1`;
    - purchased assets: `0`;
    - ML UUID: `user-0000000000000999`.

## Service structure

All Django settings and entry points are located in `config` folder:

- `settings` folder contains `local` and `production` Django settings;
- `urls.py` file contains endpoints for requests: `admin/` (or any other url which you can specify via environment
  variable), `api/v1/`, `swagger/` (for debug purposes).

All Django apps are located in `fulfillment_service/` folder:

- `users` - custom `User` model with additional fields;
- `wallets` - an application for manipulation with user's wallets and transactions;
- `assets` - an application that provides functionality around assets and metrics - to list user's assets, getting
  investment advice, detailed statistics of assets, purchase of assets.

## Endpoints

To access most of the endpoints, you have to log-in and receive token. The token should be specified for every request
in the header:

    Authorization: token <TOKEN>

1. User:

- `POST /api/v1/auth/login/` - checks provided credentials and returns token;
- `POST /api/v1/auth/logout/` - deletes Token object assigned to a user;
- `GET /api/v1/auth/user` - returns user fields;

2. Wallets:

- `GET /api/v1/wallets/` - returns a list of user's wallets;
- `POST /api/v1/wallets/` - creates a new wallet for the user;
- `GET /api/v1/wallets/expenses/stat/` - provides total purchases and sells by day for user;
- `POST /api/v1/wallets/<wallet_id>/topup/` - creates positive transaction for the specified wallet;
- `GET /api/v1/wallets/<wallet_id>/transactions/` - return a list transactions for the specified wallet.

3. Assets:

- `GET /api/v1/assets/` - returns purchased assets and metrics if exists;
- `POST /api/v1/assets/` - sells existing portfolio (if exists) and purchases the new one;
- `GET /api/v1/assets/advice/` - requests ML service to provide investment advice for the specified user with optional
  risk level;
- `GET /api/v1/assets/<asset_name>/stat/` - provides detailed info about an asset.
