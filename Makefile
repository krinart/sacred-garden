db:
	rm db.sqlite3
	python manage.py migrate
	python manage.py loaddata data/data.json

dbuild:
	docker build . -t sacredgarden

drun:
	docker run -p 8080:8000 sacredgarden
