run:
	DEBUG=1 python manage.py runserver

db:
	rm db.sqlite3
	python manage.py migrate
	python manage.py loaddata data/data.json

dbuild:
	docker build . -t sacredgarden

drun:
	docker run -p 8000:8000 sacredgarden

cbuild:
	docker-compose build

crun:
	docker-compose up -d
