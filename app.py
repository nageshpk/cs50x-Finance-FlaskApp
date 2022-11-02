import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    user = session['user_id']
    with sqlite3.connect('finance.db') as con:
        cur = con.cursor()
        cur.execute("SELECT symbol, name, SUM(shares) as shares FROM transactions WHERE user_id = (?) GROUP BY symbol, name", (user,))
        user_data = []

    for data in cur.fetchall():
        user_data.append(list(data))
        
    for data in user_data:
        data.append((lookup(data[0])['price']))


    with sqlite3.connect('finance.db') as con:
        cur = con.cursor()
        cur.execute("SELECT cash FROM users WHERE id = ?", (user,))
        cash = cur.fetchall()[0][0]
    total = 0
    for data in user_data:
        total += data[2] * data[3]
    return render_template("index.html", data=user_data, cash=cash, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method=="POST":
        try:
            symbol = lookup(request.form.get("symbol"))
            shares = int(request.form.get("shares"))
            if not symbol:
                return apology("Enter a symbol")
            if shares < 0:
                return apology("Enter positive integer")

            if shares > 0:
                with sqlite3.connect('finance.db') as con:
                    cur = con.cursor()
                    cur.execute("SELECT cash FROM users WHERE id = (?)", (session["user_id"],))
                    cash = cur.fetchall()[0][0]
                price = symbol["price"]

                amount = shares * price
                if amount > cash:
                    return apology("Not enough cash", 405)

                with sqlite3.connect('finance.db') as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO transactions (user_id, name, symbol, price, transaction_date, shares) VALUES (?, ?, ?, ?, ?, ?)",
                            (session["user_id"], symbol['name'], symbol['symbol'], symbol['price'], datetime.now(), shares,))
                    cur.execute("UPDATE users SET cash = (?) WHERE id = (?)", (cash-amount, session['user_id'],))
                return redirect("/")
        except (ValueError, TypeError):
            return apology("Invalid symbol")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    with sqlite3.connect('finance.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM transactions WHERE user_id = (?)", (session['user_id'],))
        data = cur.fetchall()
    return render_template("history.html", data=data)


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
        with sqlite3.connect('finance.db') as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE username = (?)", (request.form.get("username"),))
            rows = cur.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        data = lookup(symbol)
        if not data:
            return apology("Enter valid symbol")
        return render_template("quoted.html", data=data)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # user reached route via "POST"
    if request.method == "POST":
        username = request.form.get("username")

        # check if username is not blank
        if not username:
            return apology("username is blank")

        # check if username already exists
        with sqlite3.connect('finance.db') as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) as count FROM users WHERE username = (?)", (username,))
        if (cur.fetchall()[0][0] > 0):
            return apology("username already exists")

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # check if passwords do not match
        if not password or password != confirmation:
            return apology("Passwords do not match")

        # generate hash for passwords
        hash = generate_password_hash(password)

        # insert into the databse
        with sqlite3.connect('finance.db') as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash,))

        flash("Registered successfully!")

        return render_template("login.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method=="POST":
        ...
        # check for symbol
        symbol = lookup(request.form.get("symbol"))
        if not symbol:
            return apology("Enter a valid symbol")

        # check for shares
        shares = request.form.get("shares")
        if not shares or int(shares) < 0:
            return apology("Enter a positive integer")

        # check how many shares user owns
        with sqlite3.connect('finance.db') as con:
            cur = con.cursor()
            cur.execute("SELECT SUM(shares) AS shares FROM transactions WHERE user_id = (?) AND symbol = (?) GROUP BY name, symbol", (session['user_id'], symbol['symbol'],))
            user_shares = cur.fetchall()[0][0]

        if int(shares) > user_shares :
            return apology("Not enough shares")

        # check current price of the share user wants to sell
        current_price = lookup(symbol['symbol'])['price']
        name = lookup(symbol['symbol'])['name']

        # check the cash owned by user
        with sqlite3.connect('finance.db') as con:
            cur = con.cursor()
            cur.execute("SELECT cash FROM users WHERE id = (?)", (session['user_id'],))
            cash = cur.fetchall()[0][0]
        updated_cash = cash + (int(shares) * current_price)

        with sqlite3.connect('finance.db') as con:
            cur = con.cursor()
            cur.execute("UPDATE users SET cash = (?) WHERE id = (?)", (updated_cash, session['user_id'],))
            cur.execute("INSERT INTO transactions (user_id, name, symbol, price, transaction_date, shares) VALUES (?, ?, ?, ?, ?, ?)", (session['user_id'], name, symbol['symbol'], current_price, datetime.now(), -(int(shares)),))
        return redirect("/")
    else:
        with sqlite3.connect('finance.db') as con:
            cur = con.cursor()
            cur.execute("SELECT DISTINCT symbol FROM transactions WHERE user_id = ?", (session['user_id'],))
            symbols = cur.fetchall()[0]
        return render_template("sell.html", options=symbols)
