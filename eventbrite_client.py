from eventbrite import Eventbrite
from datetime import datetime, tzinfo

import dateutil.parser
import os
import simplejson

EVENTBRITE_OAUTH_TOKEN = os.environ.get('EVENTBRITE_OAUTH_TOKEN', 'EVENTBRITE_OAUTH_TOKEN')

eventbrite = Eventbrite(EVENTBRITE_OAUTH_TOKEN)


def __calculate_days_remaining(event, current_datetime=None):
    start_date = event['start']['utc']
    d0 = dateutil.parser.parse(start_date, ignoretz=True)
    if current_datetime is not None:
        d1 = dateutil.parser.parse(current_datetime, ignoretz=True)
    else:
        d1 = datetime.now()
    return (d0 - d1).days


def __calculate_quantity_sold(ticket_classes):
    return sum([int(tc['quantity_sold']) for tc in ticket_classes])


def get_event_snippets(statuses=['live'], client=None):
    """ Generate a set of 'snippets' for all the user's events for a
        set of status values (defaults to 'live' events).
    """
    client = eventbrite if client is None else client
    user_events = client.get_user_owned_events(id='me')
    # user_event_attendees = get_my_event_attendees
    user_events_snippets = [];
    for e in [e for e in user_events['events'] if e['status'] in statuses]:
        # event = client.get_event(id=e['id'])
        ticket_classes = client.get_event_ticket_classes(event_id=e['id'])
        user_events_snippets.append(
            {
                'name': e['name']['text'],
                'id': e['id'],
                'status': e['status'],
                'days_remaining': __calculate_days_remaining(e),
                'quantity_sold': __calculate_quantity_sold(ticket_classes['ticket_classes']),
                'capacity': e['capacity']
            }
        )
    return user_events_snippets


def get_my_event_attendees(client=None):
    """ Generate a set of 'snippets' for all the user's events for a
        set of status values (defaults to 'live' events).
    """
    client = eventbrite if client is None else client
    user_event_attendees = client.get_user_owned_event_attendees(id='me')
    return user_event_attendees

if __name__ == '__main__':
    # output_text = get_my_event_attendees()
    output_text = get_event_snippets()
    print(simplejson.dumps(output_text, indent=2))
