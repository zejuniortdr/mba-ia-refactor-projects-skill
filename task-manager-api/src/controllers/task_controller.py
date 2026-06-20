from flask import jsonify, request

from src.middlewares.error_handler import AppError
from src.models import category_model, task_model, user_model
from src.utils.validators import (
    normalize_tags,
    parse_due_date,
    parse_int_param,
    validate_priority,
    validate_status,
    validate_title,
)


def _require_existing_user(user_id):
    if user_id and not user_model.get_user(user_id):
        raise AppError('Usuário não encontrado', 404)


def _require_existing_category(category_id):
    if category_id and not category_model.get_category(category_id):
        raise AppError('Categoria não encontrada', 404)


def get_tasks():
    tasks = task_model.list_tasks()
    result = []
    for task in tasks:
        data = task.to_dict_with_overdue()
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
        result.append(data)
    return jsonify(result), 200


def get_task(task_id):
    task = task_model.get_task(task_id)
    if not task:
        raise AppError('Task não encontrada', 404)
    return jsonify(task.to_dict_with_overdue()), 200


def create_task():
    data = request.get_json()
    if not data:
        raise AppError('Dados inválidos', 400)

    title = validate_title(data.get('title'))
    status = validate_status(data.get('status', 'pending'))
    priority = validate_priority(data.get('priority', 3))
    user_id = data.get('user_id')
    category_id = data.get('category_id')

    _require_existing_user(user_id)
    _require_existing_category(category_id)

    fields = {
        'title': title,
        'description': data.get('description', ''),
        'status': status,
        'priority': priority,
        'user_id': user_id,
        'category_id': category_id,
    }

    if data.get('due_date'):
        fields['due_date'] = parse_due_date(data['due_date'])
    if data.get('tags'):
        fields['tags'] = normalize_tags(data['tags'])

    task = task_model.create_task(**fields)
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = task_model.get_task(task_id)
    if not task:
        raise AppError('Task não encontrada', 404)

    data = request.get_json()
    if not data:
        raise AppError('Dados inválidos', 400)

    if 'title' in data:
        task.title = validate_title(data['title'])
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = validate_status(data['status'])
    if 'priority' in data:
        task.priority = validate_priority(data['priority'])
    if 'user_id' in data:
        _require_existing_user(data['user_id'])
        task.user_id = data['user_id']
    if 'category_id' in data:
        _require_existing_category(data['category_id'])
        task.category_id = data['category_id']
    if 'due_date' in data:
        task.due_date = parse_due_date(data['due_date']) if data['due_date'] else None
    if 'tags' in data:
        task.tags = normalize_tags(data['tags'])

    task_model.save()
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task = task_model.get_task(task_id)
    if not task:
        raise AppError('Task não encontrada', 404)
    task_model.delete_task(task)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    priority = parse_int_param(request.args.get('priority', ''), 'priority')
    user_id = parse_int_param(request.args.get('user_id', ''), 'user_id')

    tasks = task_model.search_tasks(
        query=query or None,
        status=status or None,
        priority=priority,
        user_id=user_id,
    )
    return jsonify([task.to_dict() for task in tasks]), 200


def task_stats():
    by_status = task_model.counts_by_status()
    total = task_model.count_total()
    done = by_status.get('done', 0)

    stats = {
        'total': total,
        'pending': by_status.get('pending', 0),
        'in_progress': by_status.get('in_progress', 0),
        'done': done,
        'cancelled': by_status.get('cancelled', 0),
        'overdue': len(task_model.overdue_tasks()),
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
    return jsonify(stats), 200
