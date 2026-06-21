from werkzeug.security import generate_password_hash, check_password_hash

from src.models.database import db
from src.utils.time import naive_utcnow


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=naive_utcnow)

    def to_dict(self):
        """Serializa o usuário SEM expor o hash da senha."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def is_admin(self):
        return self.role == 'admin'


# ----- Data access -----

def list_users():
    return User.query.all()


def count_users():
    return User.query.count()


def get_user(user_id):
    return db.session.get(User, user_id)


def find_by_email(email):
    return User.query.filter_by(email=email).first()


def create_user(name, email, raw_password, role='user'):
    user = User(name=name, email=email, role=role)
    user.set_password(raw_password)
    db.session.add(user)
    db.session.commit()
    return user


def save():
    db.session.commit()


def delete_user(user):
    db.session.delete(user)
    db.session.commit()
