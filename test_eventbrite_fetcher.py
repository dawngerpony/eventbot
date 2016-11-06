import eventbrite_fetcher
import simplejson


def test_calculate_days_remaining_from_fixed_date():
    """ Test the test_calculate_days_remaining() function from a fixed date.
    """
    days = eventbrite_fetcher.__calculate_days_remaining({'start': {'utc': '2016-02-29T18:30:00Z'}}, '2016-02-19T18:30:00Z')
    assert days == 10


def test_calculate_days_remaining_from_now():
    """ Test the test_calculate_days_remaining() function from now.
    """
    days = eventbrite_fetcher.__calculate_days_remaining({'start': {'utc': '2016-02-29T18:30:00Z'}})
    assert days < -200
