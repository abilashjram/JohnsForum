from flask import Flask, render_template, request, make_response, redirect, url_for
from models.dbSettings import db
from models.user import User
from models.topic import Topic
from models.comment import Comment
from tasks import get_random_num


import os
import uuid
import hashlib
import smartninja_redis


app = Flask(__name__)
db.create_all()

redis = smartninja_redis.from_url(os.getenv("REDIS_URL"))

def getUser():
    session_token = request.cookies.get("session_token")
    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None
    return user



#index page
@app.route("/")
def index():
    user = getUser()

    #get all topics
    topics = db.query(Topic).all()

    return render_template("index.html", user=user, topics=topics)


#login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # Process Request for displaying login page
        return render_template("login.html")
    else:
        # Process the login creds and redirect to welcome page
        username = request.form.get("username")
        password = request.form.get("password")

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = db.query(User).filter_by(username=username).first()

        if not user:
            # user does not exists so redirect to sign up page
            return render_template("signup.html")
        else:
            if password_hash == user.password_hash:
                session_token = str(uuid.uuid4())
                user.session_token = session_token

                db.add(user)
                db.commit()

                response = make_response(redirect(url_for('index')))
                response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

                return response
            else:
                return "Incorrect Password, Try again!!"

# User Sign up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        # Process Request for displaying sign up page
        return render_template("signup.html")
    else :
        # Process the completed user sign up form and store it in db
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        repeatPass = request.form.get("repeatpass")
        ## Check for password match
        if password != repeatPass:
            return "Passwords dont Match!!"

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        ## create user object
        user = User(username=username, email=email, password_hash=password_hash,
                    session_token=str(uuid.uuid4()), active=1)
        ## add user to db
        db.add(user)
        db.commit()
        ## set session token in cookie
        response = make_response(redirect(url_for('index')))
        response.set_cookie("session_token",user.session_token, httponly=True, samesite='Strict')

        return response


@app.route("/create-topic", methods=["GET", "POST"])
def topic_create():
    ##active user
    user = getUser()

    if request.method == "GET":
        csrf_token = str(uuid.uuid4())   # CSRF token
        redis.set(name=csrf_token, value=user.username)

        return render_template("topics_create.html", user=user , csrf_token=csrf_token)
    else:
        csrf = request.form.get("csrf")  ## get the csrf from html page
        csrf_obj = redis.get(name=csrf)

        if csrf_obj:
            redis_csrf_username = redis.get(name=csrf).decode()
            if redis_csrf_username and user.username == redis_csrf_username:

                title = request.form.get("title")
                text = request.form.get("text")

                topic = Topic.create(title=title, text=text, author=user)
                return redirect(url_for('index'))
            else :
                return "invalid token"
        else :
            return "invalid token"
@app.route("/topic/<topic_id>")
def topic_details(topic_id):

    get_random_num()
    topic = db.query(Topic).get(int(topic_id))
    comments = db.query(Comment).filter_by(topic=topic).all()

    return render_template("topic_details.html", topic=topic, comments=comments)


@app.route("/topic/<topic_id>/edit", methods=["GET", "POST"])
def topic_edit(topic_id):
    topic = db.query(Topic).get(int(topic_id))

    if request.method == "GET":
        return render_template("topic_edit.html", topic=topic)
    else:
        title = request.form.get("title")
        text = request.form.get("text")

        topic.title = title
        topic.text = text

        user = getUser()
        if not user:
            return redirect(url_for('login'))
        elif topic.author.id != user.id:
            return "You do not have Privilages to edit this topic"
        else:
            db.add(topic)
            db.commit()

        return redirect(url_for('topic_details', topic_id=topic_id))


@app.route("/topic/<topic_id>/create-comment", methods=["POST"])
def comment_create(topic_id):
    ## add CSRF validation here
    text = request.form.get("text")
    user = getUser()
    topic = db.query(Topic).get(int(topic_id))

    comment = Comment.create(text=text, author=user, topic=topic)

    return redirect(url_for('topic_details', topic_id=topic_id))


if __name__ == '__main__':
    app.run()
