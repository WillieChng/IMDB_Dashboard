#Allow website folder to act as a "python package" in the representation of this file 
#It creates specific functions to be imported in main.py and models.py
#Function automatically run when imported from elsewhere
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path, environ
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_caching import Cache
import pymysql

db = SQLAlchemy() #db = database connection that used to interact with database
cache = Cache()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__) #name of the file, __init__.py
    
    #load environment variables from .env file
    load_dotenv()
    
    app.config['SECRET_KEY'] = environ.get('SECRET_KEY', 'KDJFASasldfgjsfdfs')
    app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URI', 'sqlite:///yourdatabase.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CACHE_TYPE'] = 'SimpleCache'  # Use SimpleCache for in-memory caching

    db.init_app(app) #Initialize flask app to the 
    cache.init_app(app)
    login_manager.init_app(app)
    
    #Initialize blueprint components to the app
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    # Initialize Flask-Login

    login_manager.login_view = 'auth.login'  # Set the login view


    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
   
   
    #define class/table (from models.py) before initializing db
    with app.app_context(): # Required for creating tables in the app context
        #create database/schema automatically if it doesnt exist
        create_database_if_not_exists()
        #create all tables within models
        db.create_all()
    
    return app

def create_database_if_not_exists():
    #Connect to MySQL server without specifying a database
    load_dotenv()
    
    connection = pymysql.connect(
        host=environ.get("DB_HOST"),
        user=environ.get("DB_USER"),
        password=environ.get("DB_PASSWORD")
    )
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {environ.get('DB_NAME')}")
    cursor.close()
    connection.close()