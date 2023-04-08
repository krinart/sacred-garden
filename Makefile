db:
	rm db.sqlite3
	python manage.py migrate
	python manage.py loaddata data/data.json
