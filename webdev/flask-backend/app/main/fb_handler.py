from flask import current_app
from letor_get_weights import get_weights
import requests

def send_message(recipient_id, message_text):
    inputs = message_text.split(" ", 1)
    if len(inputs) == 2:
        state, health = inputs
        query_weights = get_weights(state, str(health))
        # get elasticsearch results
        message = {
            "text": "(Placeholder)"
        }
    else:
        message = {
            "text": "Please enter a valid query (e.g. FL diabetes)."
        }

    # Send response
    uri = "https://graph.facebook.com/v2.6/me/messages"
    params = {
        "access_token": current_app.config['FB_ACCESS_TOKEN']
    }
    data = {
        "recipient": {
            "id": recipient_id
        },
        "message": message
    }
    r = requests.post(uri, params=params, json=data)
