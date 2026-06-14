from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    trips = db.relationship('Trip', backref='user', cascade='all, delete-orphan', lazy=True)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Чья поездка
    name = db.Column(db.String(100), nullable=False)
    dates = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    items = db.relationship('Item', backref='trip', cascade='all, delete-orphan', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_packed = db.Column(db.Boolean, default=False)