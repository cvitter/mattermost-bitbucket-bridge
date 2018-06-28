from flask import Flask
from flask import request
import json
import requests
import helpers


def readConfig():
    """
    Reads config.json to get configuration settings
    """
    d = json.load(open('config.json'))

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

    global bitbucket_url
    bitbucket_url = d["bitbucket"]["server_url"]


def get_event_type(event_key):
    """
    Converts event to friendly output
    TODO: Need to add error handler for unsupported events
    """
    event_out = helpers.bitbucket_events.get(event_key)
    return event_out


def process_payload(hook_path, request_id, data):
    """
    Reads Bitbucket JSON payload and converts it into Mattermost friendly
    message attachement format
    TODO: Add option to return message as text only format
    """
    text_out = ""
    attachment_text = ""

    event = get_event_type(data["eventKey"])
    actor = "[" + data["actor"]["name"] + \
            " (" + data["actor"]["emailAddress"] + ")](" + bitbucket_url + \
            "users/" + data["actor"]["name"] + ")"

    attach_extra = ""
    # Pull Requests and Pull Request Comments
    if data["eventKey"].startswith('pr:'):
        pr_id = str(data["pullRequest"]["id"])
        pr_title = data["pullRequest"]["title"]
        repo_name = data["pullRequest"]["toRef"]["repository"]["name"]
        proj_key = data["pullRequest"]["toRef"]["repository"]["project"]["key"]
        url = bitbucket_url + "projects/" + proj_key + "/repos/" + \
              repo_name + "/pull-requests/" + pr_id

        if data["eventKey"].startswith("pr:comment:"):
            attach_extra = "**Comment**: [" + data["comment"]["text"] + \
                           "](" + url + ")"
        else:
            attach_extra = "[" + pr_id + " : " + pr_title + "](" + url + ")"

    # Commits - Push (Add, Update), Comment, etc.
    if data["eventKey"].startswith('repo:'):
        repo_name = data["repository"]["name"]
        proj_key = data["repository"]["project"]["key"]
        url = bitbucket_url + "projects/" + proj_key + "/repos/" + \
              repo_name

        # Comment added, updated, deleted
        if data["eventKey"].startswith("repo:comment:"):
            url += "/commits/" +  data["commit"]
            attach_extra = "**Comment**: [" + data["comment"]["text"] + \
                           "](" + url + ")"

        if data["eventKey"] == "repo:refs_changed":
            specific_event = "**Action**: " + data["changes"][0]["type"] + \
                             " - " + data["changes"][0]["ref"]["displayId"] + \
                             " (" + data["changes"][0]["ref"]["type"] + ")"
            url += "/commits/" +  data["changes"][0]["toHash"]
            attach_extra = specific_event + "\n[Commit: " + \
                           data["changes"][0]["toHash"] + "](" + url + ")"

    # Assemble the final attachment text to return and pass
    # to the send_webhook function
    attachment_text = "**" + event + "**\n**Author**: " + actor
    if len(repo_name) > 1:
        attachment_text = "**Repository**: " + repo_name + "\n" + \
                           attachment_text
    if len(attach_extra) > 0:
        attachment_text += "\n" + attach_extra

    return send_webhook(hook_path, text_out, attachment_text, success_color)


def send_webhook(hook_path, text_out, attachment_text, attachment_color):
    """
    Assembles incoming text, creates JSON object for the response, and
    sends if on to the Mattermost server and hook configured
    """
    if len(attachment_text) > 0:
        attach_dict = {
            "color": attachment_color,
            "text": attachment_text
        }
        data = {
            'text': text_out,
            'username': mattermost_user,
            'icon_url': mattermost_icon,
            "attachments": [attach_dict]
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
        response = send_webhook(hook_path, "diagnostics:ping", 
                                "Bitbucket is testing the connection " + \
                                "to Mattermost: " + request_id, 
                                alert_color)
    else:
        if len(request.get_json()) > 0:
            data = request.get_json()
            response = process_payload(hook_path, request_id, data)
    return ""

if __name__ == '__main__':
   app.run(host = application_host, port = application_port, 
           debug = application_debug)
