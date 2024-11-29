# models.py
from sqlalchemy.schema import Index
from Website import db  # Use an absolute import
from flask_login import UserMixin

class Genre(db.Model):
    __tablename__ = 'genres'
    genre_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    extend_existing=True
    # Add index on genre_id
    __table_args__ = (
        Index('ix_genre_id', 'genre_id'),
    )

class Actor(db.Model):
    __tablename__ = 'actors'
    actor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    extend_existing=True
    __table_args__ = (
        Index('ix_actor_id', 'actor_id'),
    )

class Director(db.Model):
    __tablename__ = 'directors'
    director_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    extend_existing=True
    __table_args__ = (
        Index('ix_director_id', 'director_id'),
    )

class Movie(db.Model):
    __tablename__ = 'movies'
    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    overview = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=True)
    release_year = db.Column(db.Integer, nullable=True)
    popularity = db.Column(db.Float, nullable=True)
    vote_average = db.Column(db.Float, nullable=True)
    vote_count = db.Column(db.Integer, nullable=True)
    adult = db.Column(db.Boolean, nullable=True)
    overview_sentiment = db.Column(db.Float, nullable=True)
    all_combined_keywords = db.Column(db.Text, nullable=True)
    runtime = db.Column(db.Integer, nullable=True)
    production_countries = db.Column(db.String(500), nullable=True)
    Star1 = db.Column(db.String(100), nullable=True)
    Star2 = db.Column(db.String(100), nullable=True)
    Star3 = db.Column(db.String(100), nullable=True)
    Star4 = db.Column(db.String(100), nullable=True)
    extend_existing=True

    genres = db.relationship('Genre', secondary='movie_genres', backref=db.backref('movies', lazy='dynamic'))
    actors = db.relationship('Actor', secondary='movie_actors', backref=db.backref('movies', lazy='dynamic'))
    directors = db.relationship('Director', secondary='movie_directors', backref=db.backref('movies', lazy='dynamic'))
    
    # Declare an index for the movie_id column
    __table_args__ = (
        Index('ix_movie_id', 'movie_id'),
    )

# Association table for movies and genres
MovieGenre = db.Table('movie_genres',
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.movie_id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.genre_id'), primary_key=True),
    Index('ix_movie_genre_movie_id', 'movie_id'),  # Index on movie_id for faster lookups
    Index('ix_movie_genre_genre_id', 'genre_id'),  # Index on genre_id for faster lookups
    extend_existing=True
)

# Association table for movies and actors
MovieActor = db.Table('movie_actors',
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.movie_id'), primary_key=True),
    db.Column('actor_id', db.Integer, db.ForeignKey('actors.actor_id'), primary_key=True),
    Index('ix_movie_actor_movie_id', 'movie_id'),  # Index on movie_id for faster lookups
    Index('ix_movie_actor_actor_id', 'actor_id'),  # Index on actor_id for faster lookups
    extend_existing=True
)

# Association table for movies and directors
MovieDirector = db.Table('movie_directors',
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.movie_id'), primary_key=True),
    db.Column('director_id', db.Integer, db.ForeignKey('directors.director_id'), primary_key=True),
    Index('ix_movie_director_movie_id', 'movie_id'),  # Index on movie_id for faster lookups
    Index('ix_movie_director_director_id', 'director_id'),  # Index on director_id for faster lookups
    extend_existing=True
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    user_id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(150), nullable=False)   
    lastName = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    profile_picture = db.Column(db.String(150), nullable=True)
    user_favourites = db.relationship('Movie', secondary='user_favourites', backref=db.backref('favourited_by', lazy='dynamic'))
    user_recommendations = db.relationship('Movie', secondary='user_recommendations', backref=db.backref('recommended_to', lazy='dynamic'))

    def get_id(self):
        return (self.user_id)

# Association table for users and favorite movies
UserFavourite = db.Table('user_favourites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.movie_id'), primary_key=True),
    Index('ix_user_favourite_user_id', 'user_id'),  # Index on user_id for faster lookups
    Index('ix_user_favourite_movie_id', 'movie_id'),  # Index on movie_id for faster lookups
    extend_existing=True
)

# Association table for users and recommended movies
UserRecommendation = db.Table('user_recommendations',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.movie_id'), primary_key=True),
    Index('ix_user_recommendation_user_id', 'user_id'),  # Index on user_id for faster lookups
    Index('ix_user_recommendation_movie_id', 'movie_id'),  # Index on movie_id for faster lookups
    extend_existing=True
)