from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from datetime import datetime
from werkzeug.security import generate_password_hash
from database import db

class Film(db.Model):
    __tablename__ = 'Films'
    FilmID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(255), nullable=False)
    Description = db.Column(db.Text)
    Duration = db.Column(db.Integer)
    ReleaseDate = db.Column(db.Date)
    Poster = db.Column(db.NVARCHAR(255))
    # Отношения
    showtimes = db.relationship('Showtime', backref='film', lazy=True)

class Hall(db.Model):
    __tablename__ = 'Halls'
    HallID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Capacity = db.Column(db.Integer, nullable=False)

    # Отношения
    showtimes = db.relationship('Showtime', backref='hall', lazy=True)

class Showtime(db.Model):
    __tablename__ = 'Showtimes'
    ShowtimeID = db.Column(db.Integer, primary_key=True)
    FilmID = db.Column(db.Integer, db.ForeignKey('Films.FilmID'), nullable=False)
    HallID = db.Column(db.Integer, db.ForeignKey('Halls.HallID'), nullable=False)
    DateTime = db.Column(db.DateTime, nullable=False)

    # Отношения
    tickets = db.relationship('Ticket', backref='showtime', lazy=True)

class Ticket(db.Model):
    __tablename__ = 'Tickets'
    TicketID = db.Column(db.Integer, primary_key=True)
    ShowtimeID = db.Column(db.Integer, db.ForeignKey('Showtimes.ShowtimeID'), nullable=False)
    SeatNumber = db.Column(db.Integer, nullable=False)
    Price = db.Column(db.Numeric(10, 2), nullable=False)
    # Add the UserId column with a foreign key reference to the Users table
    UserId = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=True)
    # Add the Status column with a default value
    Status = db.Column(db.String(50), nullable=False, default='Наличие')

    # Relationship (optional if you want backref from User model)
    user = db.relationship('User', backref='tickets', lazy=True)

class User(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    

