import requests
import os
from dotenv import dotenv_values

from flask import Flask, request

import dialogflow
from google.api_core.exceptions import InvalidArgument

import twilio
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

google_config = dotenv_values('google_creds.env')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'private_key.json'
DIALOGFLOW_PROJECT_ID = google_config['DIALOGFLOW_PROJECT_ID']
DIALOGFLOW_LANGUAGE_CODE = google_config['DIALOGFLOW_LANGUAGE_CODE']
SESSION_ID = 'me'

session_client = dialogflow.SessionsClient()
session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)

@app.route('/chatbot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False

    text_input = dialogflow.types.TextInput(text=incoming_msg, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)

    try:
        dflow_response = session_client.detect_intent(session=session, query_input=query_input)
    except InvalidArgument:
        raise
    
    q_res = dflow_response.query_result

    ret_msg = "Query text: {}\nDetected intent: {}\nDetected intent confidence: {}\nFulfillment text: {}".format(q_res.query_text, 
                                            q_res.intent.display_name, 
                                            q_res.intent_detection_confidence, 
                                            q_res.fulfillment_text)
    msg.body(ret_msg)
    return str(resp)


if __name__ == '__main__':
    app.run()