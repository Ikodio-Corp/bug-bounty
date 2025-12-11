"""
Integrations Package - VCS, CI/CD, and Third-party Integrations

This package provides integrations with version control systems,
CI/CD platforms, payment processing, and email services.
"""

from .stripe_client import StripeClient
from .email_client import EmailClient
# from .github_app import (
#     GitHubApp,
#     GitHubAppConfig,
#     CheckStatus,
#     CheckConclusion,
#     create_github_app
# )
# from .gitlab_ci import (
#     GitLabCI,
#     GitLabConfig,
#     PipelineStatus,
#     JobStatus,
#     NoteType,
#     create_gitlab_ci
# )
# from .bitbucket import (
#     BitbucketIntegration,
#     BitbucketConfig,
#     BuildState,
#     PullRequestState,
#     create_bitbucket_integration
# )

__all__ = [
    # Existing
    "StripeClient",
    "EmailClient",
    # # GitHub
    # "GitHubApp",
    # "GitHubAppConfig",
    # "CheckStatus",
    # "CheckConclusion",
    # "create_github_app",
    # # GitLab
    # "GitLabCI",
    # "GitLabConfig",
    # "PipelineStatus",
    # "JobStatus",
    # "NoteType",
    # "create_gitlab_ci",
    # # Bitbucket
    # "BitbucketIntegration",
    # "BitbucketConfig",
    # "BuildState",
    # "PullRequestState",
    # "create_bitbucket_integration"
]
