from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Week(db.Model):
    __tablename__ = "weeks"

    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    presentations = db.relationship(
        "Presentation",
        backref="week",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "week_id": self.week_id,
            "created_at": self.created_at.isoformat(),
            "presentations": [p.to_dict() for p in self.presentations],
        }


class Presentation(db.Model):
    __tablename__ = "presentations"

    id = db.Column(db.Integer, primary_key=True)
    week_db_id = db.Column(
        db.Integer,
        db.ForeignKey("weeks.id"),
        nullable=False,
        index=True,
    )

    title = db.Column(db.String(200), nullable=False)
    presenter = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    vote_records = db.relationship(
        "Vote", backref="presentation", lazy=True, cascade="all, delete-orphan"
    )
    ratings = db.relationship(
        "Rating", backref="presentation", lazy=True, cascade="all, delete-orphan"
    )
    comments = db.relationship(
        "Comment", backref="presentation", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        avg_rating = 0
        if self.ratings:
            avg_rating = sum(r.rating for r in self.ratings) / len(self.ratings)

        return {
            "id": self.id,
            "week_id": self.week.week_id,
            "title": self.title,
            "presenter": self.presenter,
            "votes": self.votes,
            "average_rating": round(avg_rating, 1),
            "rating_count": len(self.ratings),
            "comment_count": len(self.comments),
            "created_at": self.created_at.isoformat(),
        }


class Vote(db.Model):
    __tablename__ = "votes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), nullable=False, index=True)
    presentation_id = db.Column(
        db.Integer,
        db.ForeignKey("presentations.id"),
        nullable=False,
        index=True,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "presentation_id",
            name="uq_vote_user_presentation",
        ),
    )


class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    presentation_id = db.Column(
        db.Integer,
        db.ForeignKey("presentations.id"),
        nullable=False,
        index=True,
    )
    user_identifier = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "presentation_id",
            "user_identifier",
            name="_user_presentation_rating_uc",
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "presentation_id": self.presentation_id,
            "user_identifier": self.user_identifier,
            "rating": self.rating,
            "created_at": self.created_at.isoformat(),
        }


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    presentation_id = db.Column(
        db.Integer,
        db.ForeignKey("presentations.id"),
        nullable=False,
        index=True,
    )
    user_identifier = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100))
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "presentation_id": self.presentation_id,
            "user_identifier": self.user_identifier,
            "username": self.username or "Anonymous",
            "comment_text": self.comment_text,
            "created_at": self.created_at.isoformat(),
        }


__all__ = ["db", "Week", "Presentation", "Vote", "Rating", "Comment"]
