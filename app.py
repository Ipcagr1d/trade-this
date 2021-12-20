import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, validate, positive_only

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tradethis.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

# # Make sure API key is set
# if not os.environ.get("API_KEY"):
# #set iur api ke for the stock quote engine
#     try:
#         os.environ["API_KEY"] = "pk_55396df1894c4e10a34a4fd8f682c227" 
#     except:
#         raise RuntimeError("API_KEY not set")

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    user_name = session["user_name"]

    # Display user initial cash
    user_cash = db.execute(
        "SELECT cash FROM users WHERE id = ?",
        session["user_id"]
    )

    # Display user stock portofolio
    user_stocks = db.execute(
        "SELECT symbol, SUM(shares) as shares, operation FROM user_stocks WHERE user_id = ? GROUP BY symbol HAVING (SUM(shares)) > 0",
        session["user_id"],
    )

    total_stocks = 0

    for stock in user_stocks:
        quote = lookup(stock["symbol"])
        stock["name"] = quote["name"]
        stock["price"] = quote["price"]
        stock["total"] = stock["price"] * stock["shares"]

        total_stocks += stock["total"]

    # Calculate portfolio value from any assets (Cash and stocks)
    total_portfolio = total_stocks + user_cash[0]["cash"]

    return render_template("index.html", user_stocks=user_stocks, user_cash=user_cash[0], total_portfolio=total_portfolio, user_name = user_name)


# @app.route("/account", methods=["GET", "POST"])
# @login_required
# def account():
#     """Change account password"""

#     # Personal touch adding a way to change your account password

#     if request.method == "POST":

#         # Variable assigment for easy usage
#         current_password = request.form.get("current_password")
#         password = request.form.get("new_password")
#         confirmation = request.form.get("confirmation")

#         # Form check ensure all required forms are filled
#         if not current_password:
#             return apology("Please enter your current password")

#         elif not new_password:
#             return apology("Enter your new password")

#         # Fetch user data
#         rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

#         # Password check
#         if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("current_password")):
#             return apology("invalid password", 403)

#          # Personal touch password validator
#         elif validate(password) != 1:
#             return apology("Password is weak, 8 characters with digits, uppercase and lowercase required")

#         elif not confirmation:
#             return apology("New password do not match")

#         elif password != confirmation:
#             return apology("New passwword do not match")

#         # Hash the new password
#         else:

#             hash = generate_password_hash(
#                 password, method="pbkdf2:sha256", salt_length=8)

#             db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, session["user_id"])

#             flash("Success!")
#             return render_template("account.html")

#     else:
#         return render_template(account.html)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # Initialize error handler
    errormessage = " "

    # POST request
    if request.method == "POST":

        # Variable assignment for easy usage
        shares = request.form.get("shares")
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        # Must fill symbol
        if not request.form.get("symbol") or lookup(request.form.get("symbol"))is None:
            errormessage = "Symbol is not valid"
            return render_template("buy.html", errormessage = errormessage)

        symbol = request.form.get("symbol")
        price = lookup(symbol)

        # Reject negative amount of shares & data types other than int
        try:
            shares = int(shares)
            if shares < 1:
                errormessage = "You must enter a positive integer"
                return render_template("buy.html", errormessage = errormessage)

        # Ensure integer is always entered
        except ValueError:
            errormessage = "You must enter a postive integer"
            return render_template("buy.html", errormessage = errormessage)

        # Shares price is number of shares times price per share
        shares_price = shares * price["price"]

        # Check if user cash is enough if enough proceed
        if user_cash < (shares_price):
            errormessage = "Not enough funds"
            return render_template("buy.html", errormessage = errormessage)

        else:
            db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", shares_price, session["user_id"],)
            db.execute("INSERT INTO user_stocks (user_id, symbol, shares, price, operation) VALUES (?, ?, ?, ?, ?)",session["user_id"], symbol.upper(), shares, price["price"], "buy",)

            # Imitate alert from staff website
            flash("Transaction Success!")
            return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Show user database as a log via table
    user_stocks = db.execute("SELECT * FROM user_stocks WHERE user_id = ?", session["user_id"])

    return render_template("history.html", user_stocks=user_stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # Initialize error-handler
    errormessage=" "
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            errormessage = "Please enter your username"
            return render_template("login.html", errormessage = errormessage)

        # Ensure password was submitted
        elif not request.form.get("password"):
            errormessage = "Please enter your password"
            return render_template("login.html", errormessage = errormessage)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            errormessage = "Invalid username and/or password"
            return render_template("login.html", errormessage = errormessage)

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # Initialize error handling
    errormessage = " "

    # Do a post request to look for symbol in lookup then display
    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))

        # Symbol must be filled
        if quote is None or not request.form.get("symbol"):
            errormessage = "Symbol not found"
            return render_template("quote.html", errormessage = errormessage)

        else:
            return render_template(
                "quoted.html",
                name=quote["name"],
                symbol=quote["symbol"],
                price=quote["price"],)

    # Render quote template when clicking via GET (link or redirect)
    else:
        return render_template("quote.html")
        

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Error handler initialization
    errormessage = " "

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Username must be filled
        if not username:
            errormessage = "Username is missing"
            return render_template("register.html", errormessage = errormessage)

        # Username must not exist
        elif len(rows) >= 1:
            errormessage = "Username already exist"
            return render_template("register.html", errormessage = errormessage)

        # Password must be filled
        elif not password:
            errormessage = "Password is missing"
            return render_template("register.html", errormessage = errormessage)

        # Password confirmation must be filled
        elif not confirmation:
            errormessage = "Please confirm your password"
            return render_template("register.html", errormessage = errormessage)

        # Personal touch password validator
        elif validate(password) != 1:
            errormessage = "Password is weak, 8 characters with digits, uppercase, and lowercase is required"
            return render_template("register.html",errormessage = errormessage)

        # Password confirmation must match password
        elif not password == confirmation:
            errormessage = "Password do not match"
            return render_template("register.html", errormessage = errormessage)

        else:
            # Generate password hash
            hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)

            # Add new user to database
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

            # Redirect to index
            # Alert
            flash("Registrasion Success!")
            return redirect("/")

    # User reached register via GET
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Initialize error handler
    errormessage = " "

    if request.method == "POST":

        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        # Ensure prequisites are correctly set
        # Making sure shares value is a postive integer
        if positive_only(shares) == 0:
            errormessage = "Please enter a positive integer"
            return render_template("sell.html", errormessage = errormessage)

        if not symbol:
            errormessage = "Symbol is missing"
            return render_template("sell.html", errormessage = errormessage)

        # Execute database to check for stocks
        stocks = db.execute("SELECT SUM(shares) as shares FROM user_stocks WHERE user_id = ? AND symbol = ?;",session["user_id"],symbol,)[0]

        # Make sure shares does not exceed what user have
        if shares > stocks["shares"]:
            errormessage = "You don't have that much shares"
            return render_template("sell.html", errormessage = errormessage)
        price = lookup(symbol)["price"]
        shares_value = price * shares

        # Insert sell activity to user database
        db.execute("INSERT INTO user_stocks (user_id, symbol, shares, price, operation) VALUES(?, ?, ?, ?, ?)",session["user_id"],symbol.upper(),-shares,price,"sell",)

        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?",shares_value,session["user_id"],)

        # flash alert and redirect to index
        flash("Transaction Success!")
        return redirect("/")

    else:
        stocks = db.execute("SELECT symbol FROM user_stocks WHERE user_id = ? GROUP BY symbol",session["user_id"],)
        return render_template("sell.html", stocks=stocks)

@app.route("/about", methods=["GET", "POST"])
def about():
    """render about page"""
    return render_template("about.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

