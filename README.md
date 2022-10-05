# bank_backend
## Running Development Servers
```
$ docker compose up
```

## Setup
```
$ docker compose exec web python manage.py makemigrations
$ docker compose exec web python manage.py migrate
$ docker compose exec web python manage.py createsuperuser
```
