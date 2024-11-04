#Allow website folder to act as a "python package" in the representation of this file 
#It creates specific functions to be imported in main.py and models.py
#Function automatically run when imported from elsewhere
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy() #db = database connection that used to interact with database

def create_app():
    app = Flask(__name__) #name of the file, __init__.py
    app.config['SECRET_KEY'] = "KDJFASasldfgjsfdfs"
    
    #Add Database 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost:3306/moviedb' #sqlalchemy is stored within this location
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disables modification tracking, improving performance
    db.init_app(app) #Initialize flask app to the 
    
    #Initialize blueprint components to the app
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    #define class/table (from models.py) before initializing db
    # Import models and create tables if they do not exist
    from .models import User, Note
    with app.app_context(): # Required for creating tables in the app context
        db.create_all()
    
    return app