from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rightmove_id = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.String(50))
    address = db.Column(db.Text)
    description = db.Column(db.Text)
    bedrooms = db.Column(db.String(10))
    bathrooms = db.Column(db.String(10))
    property_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Property {self.rightmove_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'rightmove_id': self.rightmove_id,
            'price': self.price,
            'address': self.address,
            'description': self.description,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'property_type': self.property_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 