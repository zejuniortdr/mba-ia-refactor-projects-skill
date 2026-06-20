import re
from datetime import datetime

from src.config.settings import (
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    VALID_ROLES,
    VALID_STATUSES,
)
from src.middlewares.error_handler import AppError

EMAIL_REGEX = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'


def validate_title(title):
    if not title:
        raise AppError('Título é obrigatório', 400)
    if len(title) < MIN_TITLE_LENGTH:
        raise AppError('Título muito curto', 400)
    if len(title) > MAX_TITLE_LENGTH:
        raise AppError('Título muito longo', 400)
    return title


def validate_status(status):
    if status not in VALID_STATUSES:
        raise AppError('Status inválido', 400)
    return status


def validate_priority(priority):
    try:
        priority = int(priority)
    except (TypeError, ValueError):
        raise AppError('Prioridade inválida', 400)
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise AppError(f'Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}', 400)
    return priority


def validate_role(role):
    if role not in VALID_ROLES:
        raise AppError('Role inválido', 400)
    return role


def validate_email(email):
    if not re.match(EMAIL_REGEX, email or ''):
        raise AppError('Email inválido', 400)
    return email


def validate_password(password):
    if not password:
        raise AppError('Senha é obrigatória', 400)
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AppError(f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres', 400)
    return password


def parse_due_date(value, message='Formato de data inválido. Use YYYY-MM-DD'):
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except (TypeError, ValueError):
        raise AppError(message, 400)


def normalize_tags(tags):
    if isinstance(tags, list):
        return ','.join(tags)
    return tags


def parse_int_param(value, field):
    """Converte query param para int, retornando 400 amigável se inválido."""
    if value in (None, ''):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise AppError(f'Parâmetro {field} inválido', 400)
