# Bitbucket Webhook bridge for Mattermost

This repository is contains a Python Flask application that accepts webhooks from [Bitbucket
Server](https://www.atlassian.com/software/bitbucket/server) and forwards them to the specified
channel in a [Mattermost](https://mattermost.com) server.
 
 **Import Notes**:
 * This application has only been tested with Bitbucket Server 5.10.1. 
 * This application is an example of how to bridge Bitbucket webhooks to Mattermost and is not 
 meant to be used in a production environment.
 
 # Supported Bitbucket Events
 
 The following events are supported and **tested** in the current version of this application:
 
* Pull request comment added
* Pull request comment deleted
* Pull request comment edited
* Pull request declined
* Pull request deleted
* Pull request merged
* Pull request modified
* Pull request opened
* Repository commit comment added
* Repository commit comment deleted
* Repository commit comment edited
* Repository forked
* Repository refs updated

## Setup the Flask Application

The following steps

1. Log into the machine that will host the Python Flask application;
2. Clone this repository to your machine: `git clone https://github.com/cvitter/mattermost-bitbucket-bridge.git`;
3. Make a copy of `config.sample`: `cp config.sample config.json`
4. Edit `config.json` to update the following fields as needed:
   * Application host address and port (generally debug should be left set to `false`;
   * Mattermost server_url and the user name or icon to override the webhook with if desired;
   * And the base url of your Bitbucket server.
5. Run the Flask application - there are a number of ways to run the application but I use the following command that runs the application headlessly and captures output into a log file for troubleshooting:

```
sudo python bitbucket.py >> bitbucket.log 2>&1 &
```



# Make this Project Better (Questions, Feedback, Pull Requests Etc.)

**Help!** If you like this project and want to make it even more awesome please contribute your ideas,
code, etc.

If you have any questions, feedback, suggestions, etc. please submit them via issues here: https://github.com/cvitter/mattermost-bitbucket-bridge/issues

If you find errors please feel to submit pull requests. Any help in improving this resource is appreciated!

# License
The content in this repository is Open Source material released under the MIT License. Please see the [LICENSE](LICENSE) file for full license details.

# Disclaimer

The code in this repository is not sponsored or supported by Mattermost, Inc.

# Authors
* Author: [Craig Vitter](https://github.com/cvitter)

# Contributors 
Please submit Issues and/or Pull Requests.
