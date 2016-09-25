import logging
import os
import time

from jinja2 import Template
from jinja2 import Environment, PackageLoader
from slackclient import SlackClient

from eventbrite_client import ebclient

# The bot's ID as an environment variable
BOT_ID = os.environ.get('BOT_ID', 'BOT_ID')
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN', 'SLACK_BOT_TOKEN')

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
EVENTS_COMMAND = 'events'

READ_WEB_SOCKET_DELAY = 1  # 1 second delay between reading from firehose

# instantiate the Slack and Eventbrite clients
slack_client = SlackClient(SLACK_BOT_TOKEN)

env = Environment(loader=PackageLoader('eventbot', 'templates'))


def handle_command(command, channel):
    """ Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    elif command.startswith(EVENTS_COMMAND):
        if command.startswith(EVENTS_COMMAND + " list"):
            response = handle_events_list()

    slack_client.api_call("chat.postMessage",
                          channel=channel,
                          text=response,
                          as_user=True,
                          unfurl_links=False
    )


def handle_events_list():
    """ Handle the 'events list' command.
    """
    snippets = ebclient.get_event_snippets()
    event_names = [e['name'] for e in snippets]
    # template = Template("*Live events:*\n{{ names }}")
    template = env.get_template('events_list.md')
    response = template.render(names=event_names)
    # response = "*Live events:*\n{}".format("\n".join(event_names))
    return response


def parse_slack_output(slack_rtm_output):
    """ The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


def run():
    log = logging.getLogger(__name__)
    if slack_client.rtm_connect():
        log.info("eventbot is connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEB_SOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
