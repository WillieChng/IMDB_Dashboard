from Website import create_app

app = create_app()


if __name__ == "__main__": #ensure that web app could only run at main.py
    app.run(debug=True)