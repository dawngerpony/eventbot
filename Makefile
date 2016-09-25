SHELL := /bin/bash

# run locally using heroku
heroku-local:
	heroku local web

deploy: test
	git push heroku master

test:
	export `heroku config -s`
	nose2
