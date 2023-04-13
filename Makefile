run:
	DEBUG=1 python manage.py runserver

db:
	python manage.py flush --no-input
	python manage.py migrate
	python manage.py loaddata data/data.json

cbuild:
	docker-compose build

pg:
	docker-compose up -d

bprod:
	docker-compose -f docker-compose.prod.yml up -d --build
