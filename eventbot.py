import logging
import os
import time

from jinja2 import Environment, PackageLoader
from slackclient import SlackClient
from eventbrite_client import get_event_snippets

# The bot's ID as an environment variable
BOT_ID = os.environ.get('BOT_ID', 'BOT_ID')
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN', 'SLACK_BOT_TOKEN')

# constants
AT_BOT = "<@" + BOT_ID + ">"
HELP_COMMAND = "help"
EVENTS_COMMAND = 'events'

READ_WEB_SOCKET_DELAY = 1  # 1 second delay between reading from firehose

# instantiate the Slack and Eventbrite clients
slack_client = SlackClient(SLACK_BOT_TOKEN)

env = Environment(loader=PackageLoader('eventbot', 'templates'))

SUPPORTED_COMMANDS = [
    {'name': 'events', 'description': 'list currently live events'},
    {'name': 'help', 'description': 'get help'}
]


def handle_command(command, channel):
    """ Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + HELP_COMMAND + \
               "* command for more information."
    if command.startswith(HELP_COMMAND):
        response = handle_help_command()
    elif command.startswith(EVENTS_COMMAND):
        response = handle_events_command()

    slack_client.api_call("chat.postMessage",
                          channel=channel,
                          text=response,
                          as_user=True,
                          unfurl_links=False
                          )


def handle_help_command():
    template = env.get_template('help.md')
    response = template.render(commands=SUPPORTED_COMMANDS)
    return response


def handle_events_command():
    """ Handle the 'events' command.
    """
    snippets = get_event_snippets()
    template = env.get_template('events_list.md')
    response = template.render(events=snippets)
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
    # Timer(30, report_event_stats).start()
    if slack_client.rtm_connect():
        log.info("eventbot is connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEB_SOCKET_DELAY)
    else:
        log.info("Connection failed. Invalid Slack token or bot ID?")


def report_event_stats():
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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
