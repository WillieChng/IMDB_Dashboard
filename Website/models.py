from . import db
from flask_login import UserMixin #create user object inherited from UserMixin, Help user to login
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship

#User Table
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(15))

#Many-to-Many association tables (allow table to link each movie to multiple actors and each actor to appear in multiple movies)
movie_actors = db.Table(
    'movie_actors', 
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.movie_id'), primary_key=True),
    db.Column('actor_id', db.Integer, db.ForeignKey('actors.actor_id'), primary_key=True)
)

movie_genres = db.Table(
    'movie_genres',
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.movie_id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.genre_id'), primary_key=True)
)

movie_directors = db.Table(
    'movie_directors',
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.movie_id'), primary_key=True),
    db.Column('director_id', db.Integer, db.ForeignKey('directors.director_id'), primary_key=True)
)
    
#Movie Table
class Movie(db.Model):
    __tablename__ = 'movies'
    movie_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    overview = db.Column(db.String(1450))
    status = db.Column(db.String(255))
    release_year = db.Column(db.Integer)
    popularity = db.Column(db.Float)
    vote_average = db.Column(db.Float)
    vote_count = db.Column(db.Integer)
    adult = db.Column(db.Boolean)
    overview_sentiment = db.Column(db.Float)
    all_combined_keywords = db.Column(db.Text)
    Star1 = db.Column(db.String(255))
    Star2 = db.Column(db.String(255))
    Star3 = db.Column(db.String(255))
    Star4 = db.Column(db.String(255))
    
    #Relationships
    actors = relationship("Actor", secondary=movie_actors, back_populates="movies")
    genres = relationship("Genre", secondary=movie_genres, back_populates="movies")
    directors = relationship("Director", secondary=movie_directors, back_populates="movies")

#Actor Table
class Actor(db.Model):
    __tablename__ = 'actors'
    actor_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    
    #Relationship
    movies = relationship("Movie", secondary=movie_actors, back_populates="actors")
    
#Genre Table
class Genre(db.Model):
    __tablename__ = 'genres'
    genre_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    
    #Relationship
    movies = relationship("Movie", secondary=movie_genres, back_populates="genres")
    
#Director Table
class Director(db.Model):
    __tablename__ = 'directors'
    director_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    
    #Relationship
    movies = relationship("Movie", secondary=movie_directors, back_populates="directors")