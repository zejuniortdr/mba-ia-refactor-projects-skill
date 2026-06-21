from sqlalchemy import func
from sqlalchemy.orm import joinedload

from src.config.settings import DEFAULT_PRIORITY, DONE_STATUSES
from src.models.database import db
from src.models.user_model import User
from src.utils.time import naive_utcnow


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=naive_utcnow)
    updated_at = db.Column(db.DateTime, default=naive_utcnow, onupdate=naive_utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def is_overdue(self):
        """True se a task passou do prazo e ainda não foi concluída/cancelada."""
        if not self.due_date:
            return False
        return self.due_date < naive_utcnow() and self.status not in DONE_STATUSES

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
        }

    def to_dict_with_overdue(self):
        data = self.to_dict()
        data['overdue'] = self.is_overdue()
        return data


# ----- Data access -----

def list_tasks():
    """Lista tasks com user/category carregados (evita N+1)."""
    return Task.query.options(
        joinedload(Task.user), joinedload(Task.category)
    ).all()


def get_task(task_id):
    return db.session.get(Task, task_id)


def list_by_user(user_id):
    return Task.query.filter_by(user_id=user_id).all()


def search_tasks(query=None, status=None, priority=None, user_id=None):
    q = Task.query
    if query:
        q = q.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%'),
            )
        )
    if status:
        q = q.filter(Task.status == status)
    if priority is not None:
        q = q.filter(Task.priority == priority)
    if user_id is not None:
        q = q.filter(Task.user_id == user_id)
    return q.all()


def create_task(**fields):
    task = Task(**fields)
    db.session.add(task)
    db.session.commit()
    return task


def save():
    db.session.commit()


def delete_task(task):
    db.session.delete(task)
    db.session.commit()


def delete_by_user(user_id):
    """Remove as tasks de um usuário (sem commit — quem orquestra confirma)."""
    Task.query.filter_by(user_id=user_id).delete()


# ----- Aggregations (mantêm SQL fora dos controllers) -----

def count_total():
    return Task.query.count()


def counts_by_user():
    rows = db.session.query(Task.user_id, func.count(Task.id)).group_by(Task.user_id).all()
    return {user_id: count for user_id, count in rows}


def count_by_category(category_id):
    return Task.query.filter_by(category_id=category_id).count()


def counts_by_status():
    rows = db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
    return {status: count for status, count in rows}


def counts_by_priority():
    rows = db.session.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
    return {priority: count for priority, count in rows}


def overdue_tasks():
    """Tasks vencidas e não concluídas, resolvido em uma única query."""
    return Task.query.filter(
        Task.due_date.isnot(None),
        Task.due_date < naive_utcnow(),
        Task.status.notin_(DONE_STATUSES),
    ).all()


def count_created_since(since):
    return Task.query.filter(Task.created_at >= since).count()


def count_done_since(since):
    return Task.query.filter(Task.status == 'done', Task.updated_at >= since).count()


def user_productivity():
    """Total e concluídas por usuário em uma única query (sem N+1)."""
    done_expr = func.sum(
        db.case((Task.status == 'done', 1), else_=0)
    )
    rows = (
        db.session.query(
            User.id, User.name, func.count(Task.id), done_expr
        )
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id, User.name)
        .all()
    )
    return rows
