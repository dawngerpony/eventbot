import eventbrite_reporter
import logging
import settings
import time

from jinja2 import Environment, PackageLoader
from slackclient import SlackClient
from eventbrite_fetcher import get_event_snippets

# constants
AT_BOT = "<@" + settings.BOT_ID + ">"

HELP_CMD = 'help'
EVENTS_CMD = 'events'
ATTENDEES_CMD = 'attendees'

READ_WEB_SOCKET_DELAY = 1  # 1 second delay between reading from firehose

log = logging.getLogger(__name__)

# instantiate the Slack and Eventbrite clients
slack_client = SlackClient(settings.SLACK_BOT_TOKEN)

env = Environment(loader=PackageLoader('eventbot', 'templates'))

SUPPORTED_COMMANDS = [
    {'name': EVENTS_CMD,    'description': 'list currently live events'},
    {'name': ATTENDEES_CMD, 'description': 'list attendees for the soonest event'},
    {'name': HELP_CMD,      'description': 'get help'}
]


def handle_command(command, channel):
    """ Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + HELP_CMD + \
               "* command for more information."
    if command.startswith(HELP_CMD):
        response = handle_help_command()
    elif command.startswith(EVENTS_CMD):
        response = handle_events_command()
    elif command.startswith(ATTENDEES_CMD):
        response = handle_attendees_command()

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


def handle_events_command(silent_if_none=False):
    """ Handle the 'events' command.
    """
    snippets = get_event_snippets()
    if silent_if_none and len(snippets) == 0:
        return ""
    if not silent_if_none and len(snippets) == 0:
        return "There are no live events."
    template = env.get_template('events_list.md')
    response_text = template.render(events=snippets)
    return response_text


def handle_attendees_command():
    """ Handle the 'attendees' command.
    """
    snippets = get_event_snippets()
    template = env.get_template('attendees_list.md')
    event_id = snippets[0]['id']
    attendees = eventbrite_reporter.get_event_attendee_snippets(event_id)
    response_text = template.render(event=snippets[0], attendees=attendees)
    return response_text


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


def post_message(message, channels):
    if message == '':
        log.info("No message to send.")
    elif slack_client.rtm_connect():
        log.info("eventbot is connected and running.")
        log.info("Posting message '{}' into channels '{}'".format(message, ', '.join(channels)))
        for channel in channels:
            slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                text=message,
                as_user=True,
                unfurl_links=False
            )
    else:
        error_msg = "Connection failed. Invalid Slack token or bot ID?"
        log.error(error_msg)
        raise Exception(error_msg)


def run():
    if slack_client.rtm_connect():
        log.info("eventbot is connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEB_SOCKET_DELAY)
    else:
        log.info("Connection failed. Invalid Slack token or bot ID?")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
