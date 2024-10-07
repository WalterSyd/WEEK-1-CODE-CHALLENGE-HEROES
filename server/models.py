from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # One-to-many relationship between heroes and powers
    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade="all, delete-orphan")

    # Add serialization rules
    serialize_rules = ('-hero_powers.hero', 'id', 'name', 'super_name')

    def __repr__(self):
        return f'<Hero {self.id}>'

class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # One-to-many relationship between powers and heroes
    hero_powers = db.relationship('HeroPower', back_populates='power', cascade="all, delete-orphan")

    # Add serialization rules (fixed)
    serialize_rules = ('-hero_powers.power', 'id', 'name', 'description')

    # Add validation for description
    @validates('description')
    def validates_power_description(self, key, description):
        # Check whether description is at least 20 characters
        if not description or len(description) < 20:
            raise ValueError("Your description must be at least 20 characters long.")
        return description

    def __repr__(self):
        return f'<Power {self.id}>'

class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # Many-to-one relationship with Hero
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    hero = db.relationship('Hero', back_populates='hero_powers')

    # Many-to-one relationship with Power
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)
    power = db.relationship('Power', back_populates='hero_powers')

    # Add serialization rules 
    serialize_rules = ('-hero', '-power')

    # Add validation for strength
    @validates('strength')
    def strength_validation(self, key, strength):
        if strength not in ['Strong', 'Weak', 'Average']:
            raise ValueError("Strength must be 'Strong', 'Weak', or 'Average'.")
        return strength

    def __repr__(self):
        return f'<HeroPower {self.id}>'
