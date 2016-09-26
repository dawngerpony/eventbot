import eventbrite_client


def test_calculate_days_remaining_from_fixed_date():
    days = eventbrite_client.calculate_days_remaining({'start': {'utc': '2016-02-29T18:30:00Z'}}, '2016-02-19T18:30:00Z')
    assert days == 10


def test_calculate_days_remaining_from_now():
    days = eventbrite_client.calculate_days_remaining({'start': {'utc': '2016-02-29T18:30:00Z'}})
    assert days < -200
