# standart Library
import requests
import os
import json
import logging
import time

# 3rd Party
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

# local Importing


env_path = Path(".")/'.env'
load_dotenv(dotenv_path=env_path)

# create logging object
# ---------------------------------------------------------------
logger = logging.getLogger(__name__)


# create Stack app
# ---------------------------------------------------------------

app = App(token=os.environ["SLACK_BOT_TOKEN"],
          signing_secret=["SIGNING_SECRET"])

slack_channel = os.environ["CHANNEL_ID"]

# -----------------------------------------------------------------
# Respond to /show_weather slash command
# ------------------------------------------------------------------


@app.command("/show_weather")
def open_model(ack, body, client):
    # acknowledge the slash command request
    ack()

    # call the view_open with build in client
    client.views_open(
        # pass the valid triggerd_id withing 3 seconds receiving it
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "submit_weather",
            "title": {
                "type": "plain_text",
                "text": "Weather Information"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "city_input",
                    "label": {
                        "type": "plain_text",
                        "text": "City"
                    },
                    "element": {
                        "type": "static_select",
                        "action_id": "city",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Mumbai"
                                },
                                "value": "Mumbai"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Kolkata"
                                },
                                "value": "kolkata"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Delhi"
                                },
                                "value": "Delhi"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Bengaluru"
                                },
                                "value": "Bengaluru"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Indore"
                                },
                                "value": "Indore"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Bhopal"
                                },
                                "value": "Bhopal"
                            },
                            # Add more city as needed
                        ]
                    }
                }
            ],
            "submit": {
                "type": "plain_text",
                "text": "Submit"
            }
        }
    )


# ----------------------------------------------------------------------------
# Send the message back to the Slack Channel
# ----------------------------------------------------------------------------


def slack_message(message, client):
    # send your message to slack
    # Id of the channel you want to send the messge to
    channel_id = f"{slack_channel}"
    try:  # call the chatPostMessage method using the WebClie
        result = client.chat_postMessage(
            channel=channel_id,
            text=f"*Successfully requested a report*: \n{message}",
        )
        logger.info(result)
    except SlackApiError as error_message:
        logger.error(error_message)


# ----------------------------------------------------------------------------
# show wheather
# ----------------------------------------------------------------------------


@app.view("submit_weather")
def submit_weather_handler(ack, body, logger, client):
    # Acknowledge the submission
    ack(response_action="clear")
    logger.info(body)
    # Get the city and country values from the submission
    # city = body["view"]["state"]["values"]["city_input"]["city"]["value"]
    city = body["view"]["state"]["values"]["city_input"]["city"]["selected_option"]["value"]

    # Make a request to the weather API
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    WEATHER_API_KEY = os.environ['WEATHER_API_KEY']
    weather_url = BASE_URL + "appid=" + WEATHER_API_KEY + "&q=" + city

    response = requests.get(weather_url).json()
    curr_temperature_fahrenheit = response['main']['temp']
    min_temperature_fahrenheit = response['main']['temp_min']
    max_temperature_fahrenheit = response['main']['temp_max']
    humidigy = response['main']['humidity']

    message = (f'Weather report of {city} is Current temperature {curr_temperature_fahrenheit} fahrenheit, min temperature is {min_temperature_fahrenheit} fahrenheit, max temperature  {max_temperature_fahrenheit} fahrenheit and humidity {humidigy}.')

    slack_message(message, client)


# ---------------------------------------------------------------------------
# start Your app
# ---------------------------------------------------------------------------


if __name__ == "__main__":

    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
