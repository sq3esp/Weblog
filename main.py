from flask import Flask, render_template, send_from_directory, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import scripts.api as api
from datetime import datetime
import hashlib


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SECRET_KEY'] = 'secret!!!!!123'
db = SQLAlchemy(app)

loggedIn = False
username = ""


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.Text, nullable=False,
                            default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    def __init__(self, title, content, latitude, longitude):
        self.title = title
        self.content = content
        self.latitude = latitude
        self.longitude = longitude


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100))
    login = db.Column(db.String(1000))

    def __init__(self, login, password):
        self.login = login
        self.password = password


db.create_all()


@app.route("/")
def main():
    lat, lon = api.get_location()
    weather = api.get_weather(lat, lon)
    quote = api.get_random_quote()
    posts = Post.query.all()
    posts.sort(key=lambda x: x.id, reverse=True)
    for post in posts:  # add weather to posts
        if post.latitude is not None and post.longitude is not None:
            post.weather = api.get_weather(post.latitude, post.longitude)
        else:
            post.weather = None
    for post in posts:
        print(post.weather)
    return render_template('main.html', lat=lat, lon=lon, city=weather[0], icon=weather[1], temperature=weather[2], description=weather[3], quote=quote[0], author=quote[1], posts=posts, loggedIn=loggedIn, username=username)


@app.route('/favicon.ico')
def favicon():  # favicon for browser

    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/add", methods=["POST", "GET"])
def add():  # add post
    if not loggedIn:
        lat, lon = api.get_location()
        weather = api.get_weather(lat, lon)
        quote = api.get_random_quote()
        return render_template('unauthorized.html', lat=lat, lon=lon, city=weather[0], icon=weather[1], temperature=weather[2], description=weather[3], quote=quote[0], author=quote[1], loggedIn=loggedIn, username=username)
    underForm = " "
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        checkbox = request.form.getlist("checkbox")
        if checkbox:
            latitude = request.form["latitude"]
            longitude = request.form["longitude"]
        else:
            latitude = None
            longitude = None
        post = Post(title, content, latitude, longitude)
        db.session.add(post)
        try:
            db.session.commit()
            id = post.id
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                uploaded_file.save("static/images/"+str(id)+".png")
            underForm = "Dodano pomyślnie"
        except Exception as e:
            print(e)
            underForm = "Podczas dodawania wystąpił błąd"

    lat, lon = api.get_location()
    weather = api.get_weather(lat, lon)
    quote = api.get_random_quote()
    return render_template("add.html", lat=lat, lon=lon, city=weather[0], icon=weather[1], temperature=weather[2], description=weather[3], quote=quote[0], author=quote[1], underForm=underForm, loggedIn=loggedIn, username=username)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first()
        hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        if user and user.password == hash:
            global loggedIn
            loggedIn = True
            global username
            username = user.login

    lat, lon = api.get_location()
    weather = api.get_weather(lat, lon)
    quote = api.get_random_quote()
    return render_template('login.html', lat=lat, lon=lon, city=weather[0], icon=weather[1], temperature=weather[2], description=weather[3], quote=quote[0], author=quote[1], loggedIn=loggedIn, username=username)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        # add user to database
        user = User(login, hash)
        db.session.add(user)
        try:
            db.session.commit()
            global loggedIn
            loggedIn = True
            global username
            username = user.login
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            lat, lon = api.get_location()
            weather = api.get_weather(lat, lon)
            quote = api.get_random_quote()
            return render_template('signup.html', lat=lat, lon=lon, city=weather[0], icon=weather[1], temperature=weather[2], description=weather[3], quote=quote[0], author=quote[1], loggedIn=loggedIn, username=username, underForm="Podczas rejestracji wystąpił błąd")

    lat, lon = api.get_location()
    weather = api.get_weather(lat, lon)
    quote = api.get_random_quote()
    return render_template('signup.html', lat=lat, lon=lon, city=weather[0], icon=weather[1], temperature=weather[2], description=weather[3], quote=quote[0], author=quote[1], loggedIn=loggedIn, username=username)


@app.route('/logout')
def logout():
    global loggedIn
    loggedIn = False
    global username
    username = None
    return redirect(url_for('main'))


@app.route('/unauthorized')
def unauthorized():
    lat, lon = api.get_location()
    weather = api.get_weather(lat, lon)
    quote = api.get_random_quote()
    return render_template('unauthorized.html', lat=lat, lon=lon, city=weather[0], icon=weather[1], temperature=weather[2], description=weather[3], quote=quote[0], author=quote[1], loggedIn=loggedIn, username=username)


if __name__ == "__main__":
    app.run(debug=True)
