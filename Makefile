run:
	DEBUG=1 python manage.py runserver

db:
	python manage.py flush --no-input
	python manage.py migrate
	python manage.py loaddata data/data.json

cbuild:
	docker-compose -f docker-compose.dev.yml build

crun:
	docker-compose -f docker-compose.dev.yml up -d

bprod:
	docker-compose -f docker-compose.prod.yml build

dpush:
	docker tag sacred-garden-api:latest krinart/sacred-garden-api:latest
	docker push krinart/sacred-garden-api

temp:
	DJANGO_ALLOWED_HOSTS=api.sacredgarden.love DJANGO_CORS_ALLOWED_ORIGINS=http://sacredgarden.love SQL_ENGINE=django.db.backends.postgresql SQL_USER=dbmasteruser SQL_PASSWORD="sv23t02i5G!" SQL_DATABASE=sacred_garden_api SQL_HOST=ls-94cc5541b25233f135fb50b7b3872d2974734af2.czralkya9hre.us-west-2.rds.amazonaws.com SQL_PORT=5432 /home/bitnami/sacred-garden/.venv/bin/gunicorn sacred_garden_server.wsgi --bind 0.0.0.0:8000 --workers 4
