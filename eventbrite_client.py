from eventbrite import Eventbrite

import os
import simplejson

EVENTBRITE_OAUTH_TOKEN = os.environ.get('EVENTBRITE_OAUTH_TOKEN', 'EVENTBRITE_OAUTH_TOKEN')


class EventbriteClient():

    def __init__(self):
        self.eventbrite_client = Eventbrite(EVENTBRITE_OAUTH_TOKEN)

    def get_event_snippets(self, statuses=['live']):
        user_events = self.eventbrite_client.get_user_events(id='me')
        user_events_snippets = [
            {
                'name': e['name']['text'],
                'id': e['id'],
                'status': e['status']
            } for e in user_events['events']
        ]
        output = [e for e in user_events_snippets if e['status'] in statuses]
        return output

ebclient = EventbriteClient()

if __name__ == '__main__':
    # events_data = eventbrite_client.get_user_events(id='me')
    # output = [e['name']['text'] for e in events_data['events']]
    data = ebclient.get_event_snippets()
    print(simplejson.dumps(data, indent=2))
