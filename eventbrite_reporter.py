import eventbrite_fetcher
import logging
import settings
import simplejson


def get_event_attendee_snippets(event_id):
    """ Get event attendee snippets for an event.
    """
    attendees = eventbrite_fetcher.get_event_attendees(event_id)
    snippets = [{
                    "name": "{0} {1}".format(a['profile']['first_name'], a['profile']['last_name']),
                    "email": a['profile'].get('email', 'NO EMAIL'),
                    "ticket_class_name": a['ticket_class_name']
                } for a in attendees]
    return snippets


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        output_text = get_event_attendee_snippets(settings.EVENTBRITE_TEST_EVENT_ID)
        print(simplejson.dumps(output_text, indent=2))
    except Exception as e:
        print "Error: {0}".format(e.message)
