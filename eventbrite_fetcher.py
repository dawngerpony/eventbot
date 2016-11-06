import eventbrite
from datetime import datetime

import dateutil.parser
import logging
import requests
import settings
import simplejson

eventbrite_sdk_client = eventbrite.Eventbrite(settings.EVENTBRITE_OAUTH_TOKEN)


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


def get_event_snippets(statuses=['live']):
    """ Generate a set of 'snippets' for all the user's events for a
        set of status values (defaults to 'live' events).
    """
    snippets = []
    user_events = get_user_owned_events()
    for e in [e for e in user_events['events'] if e['status'] in statuses]:
        ticket_classes = eventbrite_sdk_client.get_event_ticket_classes(event_id=e['id'])
        snippets.append(
            {
                'name': e['name']['text'],
                'id': e['id'],
                'status': e['status'],
                'start': e['start'],
                'days_remaining': __calculate_days_remaining(e),
                'quantity_sold': __calculate_quantity_sold(ticket_classes['ticket_classes']),
                'capacity': e['capacity']
            }
        )
    return snippets


def get_event_attendees(event_id):
    first_page_data = eventbrite_sdk_client.get_event_attendees(event_id=event_id)
    if 'error' in first_page_data:
        raise Exception(simplejson.dumps(first_page_data))
    assert 'page_count' in first_page_data.get('pagination', {}), simplejson.dumps(first_page_data)
    page_count = first_page_data['pagination']['page_count']
    object_count = first_page_data['pagination']['object_count']
    logging.debug(first_page_data['pagination'])
    if page_count > 1:
        batch_urls = []
        for i in range(page_count):
            batch_urls.append({
                "method": "GET",
                "relative_url": "/events/{0}/attendees/?page={1}".format(event_id, i+1)
            })
        data = get_batch(batch_urls)
        attendees = []
        i = 1
        for page in data:
            logging.debug("Processing page {0}".format(i))
            attendees += page['attendees']
            i += 1
    else:
        attendees = first_page_data['attendees']
    assert len(attendees) == object_count, "len(attendees)={0}, object_count={1}".format(len(attendees), object_count)
    debug("Number of attendees", len(attendees))
    return attendees


def get_user_owned_events():
    data = eventbrite_sdk_client.get_user_owned_events(id='me')
    if 'error' in data:
        raise Exception(simplejson.dumps(data))
    assert 'page_count' in data.get('pagination', {}), simplejson.dumps(data)
    if data['pagination']['page_count'] > 1:
        raise Exception("There are {0} pages of data".format(data['page_count']))
    return data


def get_user_owned_event_attendees():
    """ Generate a set of 'snippets' for all the user's events for a
        set of status values (defaults to 'live' events).
    """
    first_page_data = eventbrite_sdk_client.get_user_owned_event_attendees(id='me')
    if 'error' in first_page_data:
        raise Exception(simplejson.dumps(first_page_data))
    assert 'page_count' in first_page_data.get('pagination', {}), simplejson.dumps(first_page_data)
    page_count = first_page_data['pagination']['page_count']
    logging.debug(first_page_data['pagination'])
    if page_count > 1:
        batch_urls = []
        for i in range(page_count+1):
            batch_urls.append({
                "method": "GET",
                "relative_url": "/users/me/owned_event_attendees/?page={0}".format(i+1)
            })
            # logging.debug(simplejson.dumps(batch_urls, indent=2))
        data = get_batch(batch_urls)
        attendees = []
        for page in data:
            attendees.append(page['attendees'])
    else:
        attendees = first_page_data['attendees']
    return attendees


def debug(text, data):
    logging.debug("{0}: {1}".format(text, simplejson.dumps(data)))


def get_batch(batch_urls):
    endpoint_url = "{0}batch/".format(eventbrite.utils.EVENTBRITE_API_URL)
    logging.debug("Batch URLs: {0}".format(simplejson.dumps(batch_urls)))
    post_data = {"batch": simplejson.dumps(batch_urls)}
    response = requests.post(
        endpoint_url,
        data=simplejson.dumps(post_data),
        headers=eventbrite_sdk_client.headers
    )
    if response.status_code != 200:
        raise Exception(response.content)
    if 'error' in response:
        raise Exception(simplejson.dumps(response.content))
    response_data = response.json()
    debug("Number of responses received", len(response_data))
    # debug("response_data", response_data)
    assert_len(response_data, batch_urls, "response_data/batch_urls")
    # responses = [simplejson.loads(item['body']) for item in response_data]
    responses = []
    for item in response_data:
        responses.append(simplejson.loads(item['body']))
    debug("Number of responses processed", len(responses))
    assert_len(responses, response_data, "responses/response_data")
    return responses


def assert_len(x, y, text):
    assert len(x) == len(y), "{0}: len(x)={1}, len(y)={2}".format(text, len(x), len(y))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        # output_text = get_user_owned_event_attendees()
        output_text = get_event_attendees(settings.EVENTBRITE_TEST_EVENT_ID)
        print(simplejson.dumps(output_text, indent=2))
    except Exception as e:
        print "Error: {0}".format(e.message)
