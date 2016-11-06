""" Integration tests for the eventbot module.
"""

import eventbot


def test_handle_events_command():
    """ Test the handle_events_command() function.
    """
    response_text = eventbot.handle_events_command()
    assert "Manage events at https://www.eventbrite.co.uk/myevents/" in response_text
