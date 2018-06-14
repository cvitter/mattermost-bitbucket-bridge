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
