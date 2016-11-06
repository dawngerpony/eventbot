#!/usr/bin/env python

import eventbot
import logging


def report_event_stats():
    """ Used by the Heroku scheduler to post a list of ticket sales into a number of channels on a daily basis.
    """
    log = logging.getLogger(__name__)
    if eventbot.slack_client.rtm_connect():
        log.info("eventbot is connected and running!")
        response = eventbot.handle_events_command()
        channels = ['eventbot-test', 'general']
        for channel in channels:
            eventbot.slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                text=response,
                as_user=True,
                unfurl_links=False
            )
    else:
        log.error("Connection failed. Invalid Slack token or bot ID?")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    report_event_stats()
