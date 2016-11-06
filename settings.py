# settings.py
from os.path import join, dirname
from dotenv import load_dotenv

import os

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

EVENTBRITE_OAUTH_TOKEN = os.environ.get('EVENTBRITE_OAUTH_TOKEN')
EVENTBRITE_TEST_EVENT_ID = os.environ.get('EVENTBRITE_TEST_EVENT_ID')
