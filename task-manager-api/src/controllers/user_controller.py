from flask import jsonify, request

from src.middlewares.error_handler import AppError
from src.models import task_model, user_model
from src.utils.validators import validate_email, validate_password, validate_role


def get_users():
    users = user_model.list_users()
    task_counts = task_model.counts_by_user()
    result = []
    for user in users:
        data = user.to_dict()
        data['task_count'] = task_counts.get(user.id, 0)
        result.append(data)
    return jsonify(result), 200


def get_user(user_id):
    user = user_model.get_user(user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)

    data = user.to_dict()
    data['tasks'] = [task.to_dict() for task in task_model.list_by_user(user_id)]
    return jsonify(data), 200


def create_user():
    data = request.get_json()
    if not data:
        raise AppError('Dados inválidos', 400)

    name = data.get('name')
    if not name:
        raise AppError('Nome é obrigatório', 400)

    email = data.get('email')
    if not email:
        raise AppError('Email é obrigatório', 400)
    validate_email(email)

    password = validate_password(data.get('password'))
    role = validate_role(data.get('role', 'user'))

    if user_model.find_by_email(email):
        raise AppError('Email já cadastrado', 409)

    user = user_model.create_user(name, email, password, role)
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = user_model.get_user(user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)

    data = request.get_json()
    if not data:
        raise AppError('Dados inválidos', 400)

    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        validate_email(data['email'])
        existing = user_model.find_by_email(data['email'])
        if existing and existing.id != user_id:
            raise AppError('Email já cadastrado', 409)
        user.email = data['email']
    if 'password' in data:
        validate_password(data['password'])
        user.set_password(data['password'])
    if 'role' in data:
        user.role = validate_role(data['role'])
    if 'active' in data:
        user.active = data['active']

    user_model.save()
    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user = user_model.get_user(user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)

    task_model.delete_by_user(user_id)
    user_model.delete_user(user)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def get_user_tasks(user_id):
    user = user_model.get_user(user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)

    result = []
    for task in task_model.list_by_user(user_id):
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'created_at': str(task.created_at),
            'due_date': str(task.due_date) if task.due_date else None,
            'overdue': task.is_overdue(),
        })
    return jsonify(result), 200
