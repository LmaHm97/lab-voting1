from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Week(db.Model):
    __tablename__ = 'weeks'

    id = db.Column(db.Integer, primary_key=True)

    # Human-readable week label, still unique
    week_id = db.Column(db.String(20), unique=True, nullable=False)  # e.g., "2025-W42"

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    presentations = db.relationship(
        'Presentation',
        backref='week',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'week_id': self.week_id,
            'created_at': self.created_at.isoformat(),
            'presentations': [p.to_dict() for p in self.presentations]
        }


class Presentation(db.Model):
    __tablename__ = 'presentations'

    id = db.Column(db.Integer, primary_key=True)

    # Proper FK to weeks.id
    week_db_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False, index=True)

    # Optional: if you also want to store the string week_id for convenience, keep it denormalized
    # (but then you must keep it in sync in your routes)
    # week_id = db.Column(db.String(20), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    presenter = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    vote_records = db.relationship('Vote', backref='presentation', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='presentation', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='presentation', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        avg_rating = 0
        if self.ratings:
            avg_rating = sum(r.rating for r in self.ratings) / len(self.ratings)

        return {
            'id': self.id,
            'week_id': self.week.week_id,     # read from related Week
            'title': self.title,
            'presenter': self.presenter,
            'votes': self.votes,
            'average_rating': round(avg_rating, 1),
            'rating_count': len(self.ratings),
            'comment_count': len(self.comments),
            'created_at': self.created_at.isoformat()
        }
