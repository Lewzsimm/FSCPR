import os
import urllib.parse
import requests

from flask import redirect, render_template, request, session, url_for, g
from functools import wraps

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code
# credit to cs50

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function
# credit to cs50
