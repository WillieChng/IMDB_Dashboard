from Website import create_app
from Website.views import create_dash_app

app = create_app()

#create dash app under the same Flask app
with app.app_context():
    dash_app = create_dash_app(app)

if __name__ == "__main__": #ensure that web app could only run at main.py
    app.run(debug=True)