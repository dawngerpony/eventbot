SHELL := /bin/bash
VIRTUAL_ENV = $

# run locally using heroku
heroku-local:
	heroku local dev

deploy:
	git push heroku master
