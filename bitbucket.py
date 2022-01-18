from flask import Flask
from flask import request
import json
import requests
import helpers
import datetime


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

    global bitbucket_url, bitbucket_ignore_comments
    bitbucket_url = d["bitbucket"]["server_url"]
    bitbucket_ignore_comments = d["bitbucket"]["ignore_comments"]


def get_event_name(event_key):
    """
    Converts event to friendly output
    """
    event_out = helpers.bitbucket_server_event_names.get(event_key)
    if event_out is None:
        raise KeyError('Unsupported event type!')
    return event_out

def get_event_action_text(event_key):
    """
    Converts event to friendly output
    """
    event_out = helpers.bitbucket_cloud_event_actions.get(event_key)
    if event_out is None:
        raise KeyError('Unsupported event type!')
    return event_out

def process_payload_server(hook_path, data):
    """
    Reads Bitbucket JSON payload and converts it into Mattermost friendly
    message attachement format
    TODO: Add option to return message as text only format
    """
    text_out = ""
    attachment_text = ""

    event_name = get_event_name(data["eventKey"])
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
    attachment_text = "**" + event_name + "**\n**Author**: " + actor
    if len(repo_name) > 1:
        attachment_text = "**Repository**: " + repo_name + "\n" + \
                           attachment_text
    if len(attach_extra) > 0:
        attachment_text += "\n" + attach_extra

    return send_simple_webhook(hook_path, text_out, attachment_text, success_color)

def process_payload_cloud(hook_path, data, event_key):
    """
    Reads Bitbucket Cloud JSON payload and converts it into Mattermost friendly
    message attachement format
    TODO: Add option to return message as text only format
    """
    text = ""
    attachment = {}
    
    event_name = get_event_action_text(event_key)
    actor_name = data["actor"]["display_name"]
    actor_url = data["actor"]["links"]["html"]["href"]

    # Pull Requests and Pull Request Comments
    if event_key.startswith('pullrequest:'):
        if event_key.startswith('pullrequest:comment_'):
            comment_text = data["comment"]["content"]["raw"]
            if any(ext in comment_text for ext in bitbucket_ignore_comments):
                raise StandardError('Ignoring comment!')

        pr_id = str(data["pullrequest"]["id"])
        pr_title = data["pullrequest"]["title"]
        pr_description = data["pullrequest"]["description"]
        pr_author_name = data["pullrequest"]["author"]["display_name"]
        pr_author_url = data["pullrequest"]["author"]["links"]["html"]["href"]
        pr_author_icon_url = data["pullrequest"]["author"]["links"]["avatar"]["href"]
        pr_url = data["pullrequest"]["links"]["html"]["href"]

        text = event_name.format("[" + actor_name + "](" + actor_url + ")", "[#" + pr_id + "](" + pr_url + ")")
        
        color = ''
        if event_key == 'pullrequest:approved' or event_key == 'pullrequest:merged':
            color = 'good'
        elif event_key == 'pullrequest:unapproved' or event_key == 'pullrequest:declined' or event_key == 'pullrequest:deleted':
            color = 'danger'

        attachment = {
                "author_name": pr_author_name,
                "author_icon": pr_author_icon_url,
                "author_link": pr_author_url,
                "title": pr_title,
                "color": color,
                "title_link": pr_url,
                "fields": [
                    {
                        "short": False,
                        "title": "Description",
                        "value": pr_description
                    }
                ]
            }

        reviewers = []
        for participant in data["pullrequest"]["participants"]:
            if participant["role"] != 'REVIEWER':
                continue
            approved_icon = ':white_check_mark: ' if participant['approved'] else ''
            reviewers.append("{}[{}]({})".format(approved_icon, participant["user"]["display_name"], participant["user"]["links"]["html"]["href"]))
        if len(reviewers) > 0:
            attachment["fields"].append({
                        "short": False,
                        "title": "Reviewers",
                        "value": ", ".join(reviewers)
                    })

        if event_key.startswith('pullrequest:comment_'):
            if event_key == 'pullrequest:comment_deleted':
                attachment["fields"] = {}
            else:
                attachment["fields"] = [{
                            "short": False,
                            "title": "Comment",
                            "value": comment_text
                        }]                

    elif event_key.startswith('repo:commit_status_'):        
        commit_author_name = data["commit_status"]["commit"]["author"]["user"]["display_name"]
        commit_author_url = data["commit_status"]["commit"]["author"]["user"]["links"]["html"]["href"]
        commit_author_icon_url = data["commit_status"]["commit"]["author"]["user"]["links"]["avatar"]["href"]
        commit_title = data["commit_status"]["commit"]["message"]
        commit_url = data["commit_status"]["commit"]["links"]["html"]["href"]

        state = data["commit_status"]["state"]
        color = ''
        state_icon = ''
        state_action = 'passed'
        if state == 'SUCCESSFUL':
            color = 'good'
            state_icon = ':white_check_mark: '
        elif state == 'FAILED':
            color = 'danger'
            state_icon = ':no_entry: '
            state_action = 'failed'
        else:
            raise KeyError('Unsupported event state!')

        text = "{}[{}]({}) {}".format(state_icon, data["commit_status"]["name"], data["commit_status"]["url"], state_action)
        if len(data["commit_status"]["description"]):
            text += "\n{}".format(data["commit_status"]["description"])


        attachment = {
                "author_name": commit_author_name,
                "author_icon": commit_author_icon_url,
                "author_link": commit_author_url,
                "title": commit_title,
                "title_link": commit_url,
                "color": color
            }

    elif event_key.startswith('repo:push'):
        push_commit_date = data["push"]["changes"][0]["new"]["target"]["date"]
        push_commit_repository = data["repository"]["name"]
        push_commit_repository_url = data["repository"]["links"]["html"]["href"]

        # Following code strip the last +HH:MM(timezone offset) of date string and then convert
        # it to datetime object in pyhton.
        date_sub_string_index = push_commit_date.find('+')
        push_commit_date = push_commit_date[:date_sub_string_index]

        text = event_name.format("[" + push_commit_repository + "](" + push_commit_repository_url + ")","[" + actor_name + "](" + actor_url + ")")

        if data["push"]["changes"][0]["forced"]:
            text = text.replace("pushed", "**force pushed**")

        text += "\n"
        for commit in data["push"]["changes"][0]["commits"]:
            message = commit["message"].split('\n', 1)[0]
            author = commit["author"]["raw"].split('<', 1)[0].strip()
            link = "[" + commit["hash"] + "](" + commit["links"]["html"]["href"] + ")"
            text += "- " + message + " (" + link + " by " + author + ")\n"

        if data["push"]["changes"][0]["truncated"]:
            text += "- ...and more (truncated)\n"

        text += "\n"

        attachment = None

    # Assemble message data
    data = {
            'text': text,
            'username': mattermost_user,
            'icon_url': mattermost_icon,
            "attachments": [attachment]
        }
    return send_webhook_data(hook_path, data)

def send_webhook_data(hook_path, data):
    """
    Sends message data to the Mattermost server and hook configured
    """
    response = requests.post(
        mattermost_url + "hooks/" + hook_path,
        data = json.dumps(data),
        headers = {'Content-Type': 'application/json'}
    )
    return response

def send_simple_webhook(hook_path, text_out, attachment_text, attachment_color):
    """
    Assembles incoming text, creates JSON object for the response, and
    sends it on to the Mattermost server and hook configured
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

    return send_webhook_data(hook_path, data)


"""
------------------------------------------------------------------------------------------
Flask application below
"""
readConfig()

app = Flask(__name__)

@app.route( '/hooks/<hook_path>', methods = [ 'POST' ] )
def hooks(hook_path):

    event = request.headers.get('X-Event-Key')

    if event == "diagnostics:ping":
        request_id = request.headers.get('X-Request-Id')
        response = send_simple_webhook(hook_path, "diagnostics:ping", "Bitbucket is testing the connection to Mattermost: " + request_id, alert_color)
    else:
        if len(request.get_json()) > 0:
            data = request.get_json()
            if len(bitbucket_url) > 0:
                response = process_payload_server(hook_path, data)
            else:
                response = process_payload_cloud(hook_path, data, event)
    return ""

@app.route('/healthcheck')
def health():
    return 'OK'

if __name__ == '__main__':
   app.run(host = application_host, port = application_port, 
           debug = application_debug)
