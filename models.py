from enum import unique
from sqlalchemy import Integer, String
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum
import uuid
from flask_login import UserMixin


# Initialize SQLAlchemy and Migrate
db = SQLAlchemy()

# Define an Enum for sports options
class SportType(enum.Enum):
    Football = "Football"
    Cricket = "Cricket"
    Basketball = "Basketball"


class User(db.Model, UserMixin):  # Add UserMixin here
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    sport = db.Column(db.Enum(SportType), nullable=False)
    league = db.Column(db.String(50), nullable=True)
    division = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    unique_id = db.Column(db.String(6), unique=True, default=lambda: str(uuid.uuid4().hex[:6]))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('teams', lazy=True))

    def __repr__(self):
        return f'<Team {self.name}>'


class Tryout(db.Model):
    __tablename__ = 'tryouts'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)  # Date and time of the tryout event
    location = db.Column(db.String(100), nullable=False)  # Location of the tryout
    description = db.Column(db.String(255), nullable=True)  # Optional description of the tryout
    deadline = db.Column(db.DateTime, nullable=False)  # Deadline for tryout applications
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    register_link = db.Column(db.String(500), nullable=False)

    # Relationship with the Team model
    team = db.relationship('Team', backref=db.backref('tryouts', lazy=True))

    def is_expired(self):
        """Returns True if the tryout application deadline has passed, False otherwise."""
        return datetime.now().date() > self.deadline

    def __repr__(self):
        return f'<Tryout {self.date} - {self.location} (Deadline: {self.deadline})>'

class Player(db.Model):
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    experience = db.Column(db.String(500), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(10),unique=True, nullable=False)

    def __repr__(self):
        return f'<Player {self.email}>'

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


