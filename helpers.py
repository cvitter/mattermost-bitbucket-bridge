"""
Dictionary of supported Bitbucket events and output friendly format
"""
bitbucket_events = {
    "pr:comment:added": "Pull Request: Comment Added",
    "pr:comment:deleted": "Pull Request: Comment Deleted",
    "pr:comment:edited": "Pull Request: Comment Edited",
    "pr:opened": "Pull Request: Opened",
    "pr:declined": "Pull Request: Declined",
    "pr:deleted": "Pull Request: Deleted",
    "pr:merged": "Pull Request: Merged",
    "pr:modified": "Pull Request: Modified",
    "pr:unapproved": "Pull Request: Unapproved",
    "repo:refs_changed": "Repository: Updated",
    "repo:comment:added": "Repository: Commit Comment Added",
    "repo:comment:edited": "Repository: Commit Comment Edited",
    "repo:comment:deleted": "Repository: Commit Comment Deleted",
    "repo:forked": "Repository: Forked"
}
