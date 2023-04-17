FROM python:3.11.2-alpine

EXPOSE 8000

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
COPY ./requirements-prod.txt .
RUN pip install -r requirements.txt
RUN pip install -r requirements-prod.txt

# copy project
COPY . .

# Prepare fixtures
#RUN make db

# Defined in docker-compose
CMD ["gunicorn", "sacred_garden_server.wsgi:application", "--bind", "0.0.0.0:8000"]
