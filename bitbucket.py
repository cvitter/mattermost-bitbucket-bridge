from flask import Flask
from flask import request
import json
import requests
from pyxtension.Json import Json

__doc__ = """\
bitbucket.py

"""

def readConfig():
    d = json.load( open('config.json') )
    
    global application_host, application_port, application_debug
    application_host = d["application"]["host"]
    application_port = d["application"]["port"]
    application_debug = d["application"]["debug"]
    
    global error_color, alert_color, success_color
    error_color = d["colors"]["error"]
    alert_color = d["colors"]["alert"]
    success_color = d["colors"]["success"]
    
    global mattermost_url, mattermost_user, mattermost_icon
    mattermost_url = d["mattermost"]["server_url"]
    mattermost_user = d["mattermost"]["post_user_name"]
    mattermost_icon = d["mattermost"]["post_user_icon"]


def createReponseObject( response_type_val, text_content, attachement_content, status_number ):
    """
    """
    if len( attachement_content ) > 0:
        data = {
            "response_type": response_type_val,
            "text": text_content,
            "attachments" : [ attachement_content ]
        }
    else:
        data = {
            "response_type": response_type_val,
            "text": text_content
        }

    responseObj = app.response_class(
        response = json.dumps( data ),
        status = status_number,
        mimetype = 'application/json'
    )
    return responseObj

def send_webhook( hook_path, text_out, attachment_text, attachment_color ):
    if len(attachment_text) > 0:
        attach_dict = { 
            "color": attachment_color, 
            "text": attachment_text
        }
        data = {
            'text': text_out,
            'username': mattermost_user,
            'icon_url': mattermost_icon,
            "attachments" : [ attach_dict ]
        }
    else:
        data = {
            'text': text_out,
            'username': mattermost_user,
            'icon_url': mattermost_icon,
        }       
   
    response = requests.post(
        mattermost_url + "hooks/" + hook_path,
        data = json.dumps(data),
        headers = {'Content-Type': 'application/json'}
    )
    
    return response

"""
------------------------------------------------------------------------------------------
Flask application below
"""

readConfig()

app = Flask(__name__)
 
@app.route( '/hooks/<hook_path>', methods = [ 'POST' ] )
def hooks(hook_path):
    
    request_id = request.headers.get('X-Request-Id')
    event = request.headers.get('X-Event-Key')

    if event == "diagnostics:ping":
        response = send_webhook( hook_path, "diagnostics:ping", "Bitbucket is testing the connection to Mattermost: " + request_id, alert_color )
    else:
        if len( request.get_json() ) > 0:
            data = request.get_json()
            print data
            
    
    return ""

 
if __name__ == '__main__':
   app.run(host = application_host, port = application_port, debug = application_debug)