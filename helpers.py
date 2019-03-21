"""
Dictionary of supported Bitbucket events and output friendly format
"""
bitbucket_server_event_names = {
    "pr:comment:added": "Pull Request: Comment Added",
    "pr:comment:deleted": "Pull Request: Comment Deleted",
    "pr:comment:edited": "Pull Request: Comment Edited",
    "pr:opened": "Pull Request: Opened",
    "pr:declined": "Pull Request: Declined",
    "pr:deleted": "Pull Request: Deleted",
    "pr:merged": "Pull Request: Merged",
    "pr:modified": "Pull Request: Modified",
    "pr:approved": "Pull Request: Approved",
    "pr:unapproved": "Pull Request: Unapproved",
    "repo:refs_changed": "Repository: Updated",
    "repo:comment:added": "Repository: Commit Comment Added",
    "repo:comment:edited": "Repository: Commit Comment Edited",
    "repo:comment:deleted": "Repository: Commit Comment Deleted",
    "repo:commit_comment_created": "Repository: Commit Comment Added",
    "repo:forked": "Repository: Forked"
}

bitbucket_cloud_event_actions = {
    "pullrequest:created": "{} created pull request {}",
    "pullrequest:updated": "{} updated pull request {}",
    "pullrequest:approved": ":thumbsup: {} approved pull request {}",
    "pullrequest:unapproved": "{} unapproved pull request {}",
    "pullrequest:merged": ":tada: {} merged pull request {}",
    "pullrequest:declined": "{} declined pull request {}",
    "pullrequest:deleted": "{} deleted pull request {}",
    "pullrequest:comment_created": "{} added a comment to pull request {}",
    "pullrequest:comment_updated": "{} updated a comment to pull request {}",
    "pullrequest:comment_deleted": "{} deleted a comment to pull request {}",
    "repo:push": "{} Repository: Code changes pushed by: {}"
}
