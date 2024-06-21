install:
	poetry install

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

test-start:
	poetry run flask --app page_analyzer.app --debug run --port 7000

make lint:
	poetry run flake8