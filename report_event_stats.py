#!/usr/bin/env python

import eventbot
import logging
import settings

log = logging.getLogger(__name__)


def report_event_stats():
    """ Used by the Heroku scheduler to post a list of ticket sales into a number of channels on a daily basis.
    """
    response = eventbot.handle_events_command(silent_if_none=True)
    channels = settings.SLACK_CHANNELS
    log.info("channels={}".format(channels))
    eventbot.post_message(response, channels)


def report_event_stats_old():
    """ Used by the Heroku scheduler to post a list of ticket sales into a number of channels on a daily basis.
    """
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
    log.info(settings.SLACK_CHANNELS)
    log.info(settings.EVENTBRITE_TEST_EVENT_ID)
    report_event_stats()
