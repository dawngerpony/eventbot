import eventbrite_reporter
import settings
import simplejson


def test_get_attendee_snippets():
    """ Test the get_attendee_snippets() function.
    """
    attendees = eventbrite_reporter.get_event_attendee_snippets(settings.EVENTBRITE_TEST_EVENT_ID)
    assert len(attendees) > 0
