from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    ID       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    phone    = db.Column(db.String(20),  unique=True, nullable=False)
    email    = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role     = db.Column(db.String(20),  default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts          = db.relationship('Post',          backref='author',  lazy=True)
    weather_searches = db.relationship('WeatherSearch', backref='user',   lazy=True)
    rate_limits    = db.relationship('RateLimit',     backref='user',    lazy=True)

    def set_password(self, raw):
        self.password = bcrypt.generate_password_hash(raw).decode('utf-8')

    def check_password(self, raw):
        return bcrypt.check_password_hash(self.password, raw)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f"<User {self.username}>"


class Post(db.Model):
    __tablename__ = 'posts'
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200), nullable=False)
    content    = db.Column(db.Text,        nullable=False)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.ID'), nullable=False)

    def __repr__(self):
        return f'<Post {self.title}>'


class WeatherSearch(db.Model):
    """Stores every weather lookup a user makes."""
    __tablename__ = 'weather_searches'
    id          = db.Column(db.Integer, primary_key=True)
    city        = db.Column(db.String(100))
    country     = db.Column(db.String(100))
    zip_code    = db.Column(db.String(20))
    latitude    = db.Column(db.Float)
    longitude   = db.Column(db.Float)
    # today result stored as JSON string
    weather_json   = db.Column(db.Text)
    forecast_json  = db.Column(db.Text)
    search_type    = db.Column(db.String(20), default='today')  # 'today' or 'forecast'
    searched_at    = db.Column(db.DateTime, default=datetime.utcnow)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.ID'), nullable=False)

    def __repr__(self):
        return f'<WeatherSearch {self.city} by user {self.user_id}>'


class RateLimit(db.Model):
    """Tracks API usage per user per day."""
    __tablename__ = 'rate_limits'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.ID'), nullable=False)
    date       = db.Column(db.Date, default=datetime.utcnow().date)
    call_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<RateLimit user={self.user_id} date={self.date} calls={self.call_count}>'