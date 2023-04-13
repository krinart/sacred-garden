FROM python:3.11.2

EXPOSE 8000

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# Prepare fixtures
#RUN make db

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]