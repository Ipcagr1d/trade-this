import os
import requests
import urllib.parse
import re

from flask import redirect, render_template, request, session
from functools import wraps
from cs50 import SQL


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

# Adding personal touch password strength check using regex import re


def validate(password):
    password_ok = 0

    # Length check
    if len(password) < 8:
        password_ok = 0

    # Digit check
    elif re.search(r"\d", password) is None:
        password_ok = 0

    # Capital/Uppercase check
    elif re.search(r"[A-Z]", password) is None:
        password_ok = 0

    # Lowercase check
    elif re.search(r"[a-z]", password) is None:
        password_ok = 0

    else:
        password_ok = 1
        return password_ok


def positive_only(shares):
    valid = 1

    try:
        shares = int(shares)

        if shares < 1:
            valid = 0
            return apology("Please enter a positive integer")

    except ValueError:
        valid = 0
        return apology("Please enter a positive integer", 400)

        return valid
