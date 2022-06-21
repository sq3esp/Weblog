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

 
class Post(db.Model): # class for the posts table
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True) # id column
    title = db.Column(db.Text, nullable=False) # title column (obligatory)
    content = db.Column(db.Text, nullable=False) # content column (obligatory)
    date_posted = db.Column(db.Text, nullable=False,
                            default=datetime.now().strftime("%Y-%m-%d %H:%M:%S")) # date posted column is automatically generated
    latitude = db.Column(db.Float, nullable=True) # latitude column (optional)
    longitude = db.Column(db.Float, nullable=True) # longitude column (optional)

    def __init__(self, title, content, latitude, longitude): # constructor for the class
        self.title = title
        self.content = content
        self.latitude = latitude
        self.longitude = longitude


class User(db.Model): # class for the users table
    id = db.Column(db.Integer, primary_key=True) # id column
    password = db.Column(db.String(100)) # password column - hash of the password
    login = db.Column(db.String(1000)) # login column

    def __init__(self, login, password): # constructor for the class
        self.login = login
        self.password = password

 
db.create_all() # create the tables


@app.route("/")
def main():
    data = api.Api()
    posts = Post.query.all()
    posts.sort(key=lambda x: x.id, reverse=True) # sort the posts by id in descending order
    for post in posts:  # add weather to posts
        if post.latitude is not None and post.longitude is not None: # if the post has coordinates
            post.weather = api.get_weather(post.latitude, post.longitude) # add weather to the post
        else:
            post.weather = None
    return render_template('main.html', posts=posts, loggedIn=loggedIn, username=username, data=data)


@app.route('/favicon.ico')
def favicon():  # favicon for browser
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon') 


@app.route("/add", methods=["POST", "GET"]) 
def add():  # add post
    data = api.Api()
    if not loggedIn: # if the user is not logged in
        return render_template('unauthorized.html', data=data, loggedIn=loggedIn, username=username)
    underForm = " "
    if request.method == "POST": # if the user submitted the form
        title = request.form["title"]
        content = request.form["content"]
        checkbox = request.form.getlist("checkbox")
        if checkbox: # if the user checked the checkbox
            latitude = request.form["latitude"]
            longitude = request.form["longitude"]
        else:
            latitude = None
            longitude = None
        post = Post(title, content, latitude, longitude) # create a new post
        db.session.add(post) 
        try: # try to commit the changes to the database
            db.session.commit() # commit the changes to the database
            id = post.id # get the id of the post
            uploaded_file = request.files['file'] # get the file
            if uploaded_file.filename != '': # if the user uploaded a file
                uploaded_file.save("static/images/"+str(id)+".png") # save the file
            underForm = "Dodano pomyślnie"
        except Exception as e:
            print(e)
            underForm = "Podczas dodawania wystąpił błąd"

    return render_template("add.html", data=data, underForm=underForm, loggedIn=loggedIn, username=username)


@app.route('/login', methods=['POST', 'GET'])
def login(): # login page
    if request.method == 'POST': # if the user submitted the form
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first() # get the user with the given login
        hash = hashlib.sha256(password.encode('utf-8')).hexdigest() # hash the password
        if user and user.password == hash: # if the user exists and the password is correct
            global loggedIn
            loggedIn = True # set the loggedIn variable to True
            global username
            username = user.login   # set the username variable to the login of the user

    data = api.Api()
    return render_template('login.html', data=data, loggedIn=loggedIn, username=username)


@app.route('/signup', methods=['POST', 'GET'])
def signup(): # signup page (used to create a new user)
    data = api.Api() # get the data from the api
    if request.method == 'POST': # if the user submitted the form
        login = request.form['login']
        password = request.form['password']
        hash = hashlib.sha256(password.encode('utf-8')).hexdigest() # hash the password
        user = User(login, hash) # create a new user
        db.session.add(user)
        try:
            db.session.commit() # commit the changes to the database
            global loggedIn
            loggedIn = True # set the user as logged in
            global username
            username = user.login # set the username
            return redirect(url_for('login')) # redirect to the login page
        except Exception as e: # if the user already exists
            print(e)
            return render_template('signup.html', data = data, loggedIn=loggedIn, username=username, underForm="Podczas rejestracji wystąpił błąd, najprawdopodobnie użytkownik o takim loginie już istnieje")

    return render_template('signup.html', data = data, loggedIn=loggedIn, username=username)


@app.route('/logout')
def logout(): # logout page
    global loggedIn
    loggedIn = False # set the user as logged out
    global username
    username = None  # set the username to None
    return redirect(url_for('main')) # redirect to the main page


@app.route('/unauthorized')
def unauthorized(): # unauthorized page
    data = api.Api() # get the data from the api
    return render_template('unauthorized.html', data = data, loggedIn=loggedIn, username=username)


if __name__ == "__main__":
    app.run(debug=True)
