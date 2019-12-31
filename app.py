import os

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
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"
SESSION_TYPE = "filesystem"
socketio = SocketIO(app)
Session(app)

channels = []
users = []

channels.append("One")
channels.append("Two")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("nickname")
        channel = request.form.get("channel")
        # Checks whether a particuar username is in the channel, if so, response with an error message
        if name in users:
            flash("Nickname is already taken, please choose another nickname!")
            return redirect("/")
        # Checks whether user typed in a nickname
        if not name or name == "":
            flash("Please enter a nickname!")
            return redirect("/")
        if channel == None:
            flash("Please select a channel to enter!", "error")
            return redirect("/")
        users.append(name)
        session["user"] = name
        session["channel"] = channel
        return redirect(url_for("channel", c_name=channel))

    return render_template("index.html", channels=channels)


@app.route("/channels", methods=["GET"])
def channels_view():
    # Checks whether user has typed in a nickname
    if session.get("user"):
        nickname = session["user"]
        if request.args.get("ch"):
            new_channel = request.args.get("ch")
            session["channel"] = new_channel
            return redirect(url_for("channel", c_name=new_channel))
        else:
            return render_template("channels.html", channels=channels)
    else:
        flash("Please enter a nickname to use in chat!", "error")
        return redirect("/")


@app.route("/create_channel", methods=["GET", "POST"])
def create_channel():
    if request.method == "POST":
        new_channel = request.form.get("channel_name")
        if new_channel in channels:
            flash("The channel is already created!", "error")
            return redirect("/create_channel")
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
            "channel.html", channel=channel, nickname=name, users=users
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


if __name__ == "__main__":
    app.env = "development"
    app.debug = True
    app.run(port=80)
