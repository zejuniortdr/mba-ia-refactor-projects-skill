from src.config.settings import DEFAULT_COLOR
from src.models.database import db
from src.utils.time import naive_utcnow


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(7), default=DEFAULT_COLOR)
    created_at = db.Column(db.DateTime, default=naive_utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': str(self.created_at),
        }


# ----- Data access -----

def list_categories():
    return Category.query.all()


def count_categories():
    return Category.query.count()


def get_category(category_id):
    return db.session.get(Category, category_id)


def create_category(name, description='', color=DEFAULT_COLOR):
    category = Category(name=name, description=description, color=color)
    db.session.add(category)
    db.session.commit()
    return category


def save():
    db.session.commit()


def delete_category(category):
    db.session.delete(category)
    db.session.commit()
