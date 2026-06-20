from datetime import timedelta

from flask import jsonify

from src.config.settings import HIGH_PRIORITY_THRESHOLD, RECENT_ACTIVITY_DAYS
from src.middlewares.error_handler import AppError
from src.models import category_model, task_model, user_model
from src.utils.time import naive_utcnow


def _completion_rate(done, total):
    return round((done / total) * 100, 2) if total > 0 else 0


def summary_report():
    by_status = task_model.counts_by_status()
    by_priority = task_model.counts_by_priority()

    now = naive_utcnow()
    overdue_list = [
        {
            'id': task.id,
            'title': task.title,
            'due_date': str(task.due_date),
            'days_overdue': (now - task.due_date).days,
        }
        for task in task_model.overdue_tasks()
    ]

    since = now - timedelta(days=RECENT_ACTIVITY_DAYS)

    user_stats = []
    for user_id, user_name, total, completed in task_model.user_productivity():
        total = total or 0
        completed = completed or 0
        user_stats.append({
            'user_id': user_id,
            'user_name': user_name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': _completion_rate(completed, total),
        })

    report = {
        'generated_at': str(now),
        'overview': {
            'total_tasks': task_model.count_total(),
            'total_users': user_model.count_users(),
            'total_categories': category_model.count_categories(),
        },
        'tasks_by_status': {
            'pending': by_status.get('pending', 0),
            'in_progress': by_status.get('in_progress', 0),
            'done': by_status.get('done', 0),
            'cancelled': by_status.get('cancelled', 0),
        },
        'tasks_by_priority': {
            'critical': by_priority.get(1, 0),
            'high': by_priority.get(2, 0),
            'medium': by_priority.get(3, 0),
            'low': by_priority.get(4, 0),
            'minimal': by_priority.get(5, 0),
        },
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': task_model.count_created_since(since),
            'tasks_completed_last_7_days': task_model.count_done_since(since),
        },
        'user_productivity': user_stats,
    }
    return jsonify(report), 200


def user_report(user_id):
    user = user_model.get_user(user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)

    tasks = task_model.list_by_user(user_id)
    counts = {'done': 0, 'pending': 0, 'in_progress': 0, 'cancelled': 0}
    overdue = 0
    high_priority = 0

    for task in tasks:
        if task.status in counts:
            counts[task.status] += 1
        if task.priority <= HIGH_PRIORITY_THRESHOLD:
            high_priority += 1
        if task.is_overdue():
            overdue += 1

    total = len(tasks)
    report = {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': counts['done'],
            'pending': counts['pending'],
            'in_progress': counts['in_progress'],
            'cancelled': counts['cancelled'],
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': _completion_rate(counts['done'], total),
        },
    }
    return jsonify(report), 200
