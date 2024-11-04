from flask import Blueprint, render_template

views = Blueprint('views', __name__) #define blueprint

@views.route('/testing.html')
def testing():
    #pass html page and variables with values
    return render_template("testing.html", text="Hi, my name is", user="ALi", boolean=True) 

@views.route('/') #root function
def index():
    return render_template("homepage.html")

@views.route('/basic.html')
def homepage():
    return render_template("basic.html")

@views.route('/favourites.html')
def favourtie_page():
    return render_template("favourites.html")

@views.route('/settings.html')
def settings_page():
    return render_template("settings.html")