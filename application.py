import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup_future, lookup_history, time_convert, make_report

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///app.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    """Show vitamin D status"""
    if request.method == "POST":
        lat = request.form.get("lat")
        lon = request.form.get("lon")
        user_input = int(request.form.get("radio"))

        if not lat or not lon:
            return apology("Server could not receive location")
        # call open weather api, func returns two arguments as tuple, the weather forecast and the midday for user's location which is needed to calc UV index historically
        # refactoring necessary
        api_response = lookup_future(lat, lon)
        api_forecast = api_response[0]
        user_midday = round(api_response[1])

        api_history = lookup_history(lat, lon, user_midday)

        if not api_forecast or not api_history:
            return apology("API not responding")

        # create report and save to db
        report = make_report(api_history, user_input)
        db.execute("INSERT INTO reports (user_id, report) VALUES (?, ?)", session.get("user_id"), report)

        return render_template("index.html", api_forecast=api_forecast, report=report)
    else:
        return render_template("index.html")


@app.route("/history")
@login_required
def history():
    """Show history of reports"""
    report_history = db.execute("SELECT report_date, report FROM reports WHERE user_id = ?", session.get("user_id"))
    return render_template("history.html", report_history=report_history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_name"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure all fields were submitted
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("All fields must be filled")

        # ensure password and confirmation match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("Passwords do not match")

        # Ensure username is not already taken
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) == 1:
            return apology("Username already taken")

        # TODO: Register user in db and hash pw
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))

        return render_template("login.html")
    # if route is requested via GET
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
