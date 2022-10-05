## Prerequisites
Before getting started you should have the following installed and running:
- [X] Docker - [instructions](https://docs.docker.com/engine/install/)
- [X] Docker Compose - [instructions](https://docs.docker.com/compose/install/)

## Running Development Server
```
$ docker compose up
```

## Setup
```
$ docker compose exec web python manage.py makemigrations
$ docker compose exec web python manage.py migrate
$ docker compose exec web python manage.py createsuperuser
```
