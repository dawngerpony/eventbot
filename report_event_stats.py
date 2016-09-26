#!/usr/bin/env python

import logging

from eventbot import slack_client, handle_events_command


def run():
    log = logging.getLogger(__name__)
    if slack_client.rtm_connect():
        log.info("eventbot is connected and running!")
        response = handle_events_command()
        channels = ['eventbot-test', 'general']
        for channel in channels:
            slack_client.api_call("chat.postMessage",
                                  channel=channel,
                                  text=response,
                                  as_user=True,
                                  unfurl_links=False
                                  )
    else:
        log.error("Connection failed. Invalid Slack token or bot ID?")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
