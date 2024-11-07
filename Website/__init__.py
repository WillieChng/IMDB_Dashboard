#Allow website folder to act as a "python package" in the representation of this file 
#It creates specific functions to be imported in main.py and models.py
#Function automatically run when imported from elsewhere
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path, environ
from dotenv import load_dotenv
from flask_login import LoginManager

db = SQLAlchemy() #db = database connection that used to interact with database
db_name = "moviedb"

def create_app():
    app = Flask(__name__) #name of the file, __init__.py
    
    #load environment variables from .env file
    load_dotenv()
    
    app.config['SECRET_KEY'] = "KDJFASasldfgjsfdfs"
    
    #Add Database 
    app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URI') #sqlalchemy is stored within this location
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disables modification tracking, improving performance
    db.init_app(app) #Initialize flask app to the 
    
    #Initialize blueprint components to the app
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Set the login view
    login_manager.init_app(app)
    
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    #define class/table (from models.py) before initializing db
    # Import models and create tables if they do not exist
    from .models import User, Note
    with app.app_context(): # Required for creating tables in the app context
        #create database/schema automatically if it doesnt exist
        create_database_if_not_exists()
        #create all tables within models
        db.create_all()
    
    return app

def create_database_if_not_exists():
    #Connect to MySQL server without specifying a database
    import pymysql
    connection = pymysql.connect(
    #use .env to fill in host, user and password variable
        host=environ.get("host"), 
        user=environ.get("user"),
        password=environ.get("password")
    )
    
    with connection.cursor() as cursor:
        #Check if database exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
    connection.close()