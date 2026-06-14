from app import db

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dates = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    # Связь один-ко-многим: при удалении поездки удаляются и её вещи
    items = db.relationship('Item', backref='trip', cascade='all, delete-orphan', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_packed = db.Column(db.Boolean, default=False)