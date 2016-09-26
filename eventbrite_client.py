from eventbrite import Eventbrite
from datetime import datetime, tzinfo

import dateutil.parser
import os
import simplejson

EVENTBRITE_OAUTH_TOKEN = os.environ.get('EVENTBRITE_OAUTH_TOKEN', 'EVENTBRITE_OAUTH_TOKEN')


def calculate_days_remaining(event, current_datetime=None):
    # TODO calculate days remaining
    start_date = event['start']['utc']
    d0 = dateutil.parser.parse(start_date, ignoretz=True)
    if current_datetime is not None:
        d1 = dateutil.parser.parse(current_datetime, ignoretz=True)
    else:
        # d1 = datetime.utcnow()
        d1 = datetime.now()
    return (d0 - d1).days


class EventbriteFacade:

    client = None

    def __init__(self, eventbrite_client_lib=None):
        if eventbrite_client_lib is None:
            self.client = Eventbrite(EVENTBRITE_OAUTH_TOKEN)
        else:
            self.client = eventbrite_client_lib

    def get_event_snippets(self, statuses=['live']):
        user_events = self.client.get_user_events(id='me')
        user_events_snippets = [
            {
                'name': e['name']['text'],
                'id': e['id'],
                'status': e['status'],
                'days_remaining': calculate_days_remaining(e)
            } for e in user_events['events']
        ]
        output = [e for e in user_events_snippets if e['status'] in statuses]
        return output

ebclient = EventbriteFacade()

if __name__ == '__main__':
    # events_data = eventbrite_client.get_user_events(id='me')
    # output = [e['name']['text'] for e in events_data['events']]
    output_text = ebclient.get_event_snippets()
    print(simplejson.dumps(output_text, indent=2))
