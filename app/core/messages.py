"""Centralized user-facing error messages.

Kept in one file instead of as inline string literals scattered across routers and
services, so the same wording isn't retyped (and doesn't drift) in more than one place.
"""

# --- Not found ---
USER_NOT_FOUND = "User not found"
ASSIGNEE_NOT_FOUND = "Assignee not found"
PROJECT_NOT_FOUND = "Project not found"
TASK_NOT_FOUND = "Task not found"
TAG_NOT_FOUND = "Tag not found"
COMMENT_NOT_FOUND = "Comment not found"

# --- Auth ---
INCORRECT_USERNAME_OR_PASSWORD = "Incorrect username or password"
COULD_NOT_VALIDATE_CREDENTIALS = "Could not validate credentials"
INACTIVE_USER = "Inactive user"

# --- Permissions ---
ADMIN_ROLE_REQUIRED = "Admin role required"
PROJECT_MANAGER_REQUIRED = "Only the project's owner (or an admin) can perform this action"
TASK_MANAGER_REQUIRED = "Only the task's project manager (or an admin) can perform this action"
COMMENT_OWNER_OR_MANAGER_REQUIRED = (
    "Only the comment's author (or the task's project manager/admin) can perform this action"
)

# --- Conflicts ---
EMAIL_OR_USERNAME_ALREADY_REGISTERED = "Email or username already registered"
EMAIL_OR_USERNAME_ALREADY_TAKEN = "Email or username already taken"
TASK_ALREADY_BOOKMARKED = "Task already bookmarked"
PROJECT_HAS_TASKS_TEMPLATE = (
    "Project {project_id} still has {task_count} task(s); "
    "move or delete them before deleting the project."
)
