FROM python:3.10

ENV VAR1=10

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

RUN python -m pip install --upgrade pip

RUN pip install pipenv

WORKDIR /usr/src/app

COPY . .

RUN pipenv install --dev --system --deploy
