from datetime import datetime, date
from . import db


class TodoItem(db.Model):
    __tablename__ = "todo_items"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    is_done = db.Column(db.Boolean, nullable=False, default=False)

    priority = db.Column(db.Integer, nullable=False, default=2)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)

    def is_overdue(self) -> bool:
        if self.due_date is None:
            return False
        return (not self.is_done) and (self.due_date < date.today())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description or "",
            "is_done": self.is_done,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "is_overdue": self.is_overdue(),
        }
