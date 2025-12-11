run:
	python manage.py runserver

shell:
	python manage.py shell

migrate:
	python manage.py makemigrations
	python manage.py migrate

create_index:
	curl -X PUT "http://localhost:9200/$(index_name)" -H 'Content-Type: application/json' --data-binary @books_index_config.json

check_index:
	curl -X GET "http://localhost:9200/_cat/indices?v&s=index&h=index,status,docs.count,store.size"

delete_index:
	curl -X DELETE "http://localhost:9200/$(index_name)"