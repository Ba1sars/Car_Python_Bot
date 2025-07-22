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