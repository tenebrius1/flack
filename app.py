import os
from datetime import datetime
import json

from flask import (
    Flask,
    render_template,
    session,
    request,
    redirect,
    url_for,
    jsonify,
    flash,
)
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"
SESSION_TYPE = "filesystem"
socketio = SocketIO(app)
Session(app)


class Message:
    def __init__(self, author, message):
        self.author = author
        self.message = message


class Channel:
    def __init__(self, index, name):
        self.index = index
        self.name = name
        self.messages = []
        self.users = []

    def add_message(self, message: Message):
        self.messages.append(message)

    def add_user(self, user):
        self.users.append(user)


g_channels = ["One", "Two"]
channels = []
users = []
limit = 100
now = datetime.now()  # current date and time
time = now.strftime("%H:%M")

channels.append(Channel(index=0, name="One"))
channels.append(Channel(index=1, name="Two"))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("nickname")
        channel = int(request.form.get("channel"))
        channel_name = channels[channel].name
        # Checks whether a particuar username is in the channel, if so, response with an error message
        if name in users:
            flash("Nickname is already taken, please choose another nickname!", "error")
            return redirect("/")
        # Checks whether user typed in a nickname
        if not name or name == "":
            flash("Please enter a nickname!", "error")
            return redirect("/")
        users.append(name)
        session["user"] = name
        session["channel"] = channel
        return redirect(url_for("channel", c_name=channel_name))

    return render_template("index.html", channels=channels)


@app.route("/channels", methods=["GET"])
def channels_view():
    # Checks whether user has typed in a nickname
    if session.get("user"):
        nickname = session["user"]
        if request.args.get("ch"):
            new_channel = int(request.args.get("ch"))
            session["channel"] = new_channel
            c_name = channels[new_channel].name
            return redirect(url_for("channel", c_name=c_name))
        else:
            return render_template("channels.html", channels=channels)
    else:
        flash("Please enter a nickname to use in chat!", "error")
        return redirect("/")


@app.route("/create_channel", methods=["GET", "POST"])
def create_channel():
    if request.method == "POST":
        new_channel_name = request.form.get("channel_name")
        if new_channel_name in g_channels:
            flash("The channel is already created!", "error")
            return redirect("/create_channel")
        g_channels.append(new_channel_name)
        new_channel = Channel(index=len(channels), name=new_channel_name)
        channels.append(new_channel)
        flash("Channel created successfully", "success")
        return redirect("/channels")

    return render_template("create_channel.html")


@app.route("/<c_name>", methods=["GET"])
def channel(c_name):
    if session.get("user"):
        name = session["user"]
        channel = session["channel"]
        return render_template(
            "channel.html", channel=channels[channel], nickname=name, time=time
        )

    else:
        flash("Please enter a nickname to use in chat!", "error")
        return redirect("/")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """
    Clears the session
    """
    session.clear()
    return redirect("/")


@socketio.on("connect")
def join():
    nickname = session["user"]
    current_channel = session["channel"]
    join_room(current_channel)
    if nickname not in users:
        users.append(nickname)
    if nickname not in channels[current_channel].users:
        channels[current_channel].users.append(nickname)
    nickname_array = json.dumps(channels[current_channel].users)
    emit("current_user_list", {"users": nickname_array}, room=current_channel)


@socketio.on("new_message")
def new_message(data):
    user = session["user"]
    channel = int(session["channel"])
    text = data["msg"]
    msg = Message(user, text)
    channels[channel].add_message(msg)
    if len(channels[channel].messages) >= limit:
        del channels[channel].messages[0]
    emit("write_message", {"nickname": user, "message": text}, room=channel)

@socketio.on("disconnect")
def leave():
    user = session["user"]
    channel = int(session["channel"])
    users.remove(user)
    channels[channel].users.remove(user)
    leave_room(channel)
    print("here")
    emit('removed', {"nickname": user}, room=channel)


if __name__ == "__main__":
    app.env = "development"
    app.debug = True
    socketio.run(app, port=80)
