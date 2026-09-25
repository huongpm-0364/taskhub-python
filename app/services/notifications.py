from fastapi import BackgroundTasks

from app.core import email
from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User


def notify_new_comment(background_tasks: BackgroundTasks, *, task: Task, comment: Comment, author: User) -> None:
    """Schedules an email to whoever should hear about a new comment on `task`.

    Runs after the response is sent (FastAPI BackgroundTasks), so posting a comment
    doesn't get slower just because notifying someone about it does. Notifies the
    task's assignee if there is one, falling back to the project owner; skips notifying
    people about their own comments.
    """
    recipient = task.assignee or task.project.owner
    if recipient is None or recipient.id == author.id:
        return
    background_tasks.add_task(
        email.send_email,
        to=recipient.email,
        subject=f"New comment on task #{task.id}: {task.title}",
        body=f"{author.username} commented: {comment.content}",
    )
