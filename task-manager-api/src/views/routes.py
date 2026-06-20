from flask import Blueprint, jsonify

from src.controllers import (
    auth_controller,
    category_controller,
    report_controller,
    task_controller,
    user_controller,
)

task_bp = Blueprint('tasks', __name__)
user_bp = Blueprint('users', __name__)
report_bp = Blueprint('reports', __name__)

# --- Task routes ---
task_bp.add_url_rule('/tasks', view_func=task_controller.get_tasks, methods=['GET'])
task_bp.add_url_rule('/tasks/search', view_func=task_controller.search_tasks, methods=['GET'])
task_bp.add_url_rule('/tasks/stats', view_func=task_controller.task_stats, methods=['GET'])
task_bp.add_url_rule('/tasks/<int:task_id>', view_func=task_controller.get_task, methods=['GET'])
task_bp.add_url_rule('/tasks', view_func=task_controller.create_task, methods=['POST'])
task_bp.add_url_rule('/tasks/<int:task_id>', view_func=task_controller.update_task, methods=['PUT'])
task_bp.add_url_rule('/tasks/<int:task_id>', view_func=task_controller.delete_task, methods=['DELETE'])

# --- User & auth routes ---
user_bp.add_url_rule('/users', view_func=user_controller.get_users, methods=['GET'])
user_bp.add_url_rule('/users/<int:user_id>', view_func=user_controller.get_user, methods=['GET'])
user_bp.add_url_rule('/users', view_func=user_controller.create_user, methods=['POST'])
user_bp.add_url_rule('/users/<int:user_id>', view_func=user_controller.update_user, methods=['PUT'])
user_bp.add_url_rule('/users/<int:user_id>', view_func=user_controller.delete_user, methods=['DELETE'])
user_bp.add_url_rule('/users/<int:user_id>/tasks', view_func=user_controller.get_user_tasks, methods=['GET'])
user_bp.add_url_rule('/login', view_func=auth_controller.login, methods=['POST'])

# --- Report & category routes ---
report_bp.add_url_rule('/reports/summary', view_func=report_controller.summary_report, methods=['GET'])
report_bp.add_url_rule('/reports/user/<int:user_id>', view_func=report_controller.user_report, methods=['GET'])
report_bp.add_url_rule('/categories', view_func=category_controller.get_categories, methods=['GET'])
report_bp.add_url_rule('/categories', view_func=category_controller.create_category, methods=['POST'])
report_bp.add_url_rule('/categories/<int:cat_id>', view_func=category_controller.update_category, methods=['PUT'])
report_bp.add_url_rule('/categories/<int:cat_id>', view_func=category_controller.delete_category, methods=['DELETE'])


def register_routes(app):
    """Registra as rotas raiz/health e todos os blueprints de domínio."""

    @app.route('/health')
    def health():
        from src.utils.time import naive_utcnow
        return jsonify({'status': 'ok', 'timestamp': str(naive_utcnow())})

    @app.route('/')
    def index():
        return jsonify({'message': 'Task Manager API', 'version': '1.0'})

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)
