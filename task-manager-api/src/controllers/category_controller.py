from flask import jsonify, request

from src.config.settings import DEFAULT_COLOR
from src.middlewares.error_handler import AppError
from src.models import category_model, task_model


def get_categories():
    result = []
    for category in category_model.list_categories():
        data = category.to_dict()
        data['task_count'] = task_model.count_by_category(category.id)
        result.append(data)
    return jsonify(result), 200


def create_category():
    data = request.get_json()
    if not data:
        raise AppError('Dados inválidos', 400)

    name = data.get('name')
    if not name:
        raise AppError('Nome é obrigatório', 400)

    category = category_model.create_category(
        name=name,
        description=data.get('description', ''),
        color=data.get('color', DEFAULT_COLOR),
    )
    return jsonify(category.to_dict()), 201


def update_category(cat_id):
    category = category_model.get_category(cat_id)
    if not category:
        raise AppError('Categoria não encontrada', 404)

    data = request.get_json() or {}
    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    if 'color' in data:
        category.color = data['color']

    category_model.save()
    return jsonify(category.to_dict()), 200


def delete_category(cat_id):
    category = category_model.get_category(cat_id)
    if not category:
        raise AppError('Categoria não encontrada', 404)
    category_model.delete_category(category)
    return jsonify({'message': 'Categoria deletada'}), 200
