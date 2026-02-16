install:
	poetry install

lock:
	poetry lock

bot:
	python3 car_bot/bot/run.py

parsing:
	poetry run parsing

black:
	poetry run black .

isort:
	poetry run isort .

flake:
	poetry run flake8 --ignore=E501,W503 .
