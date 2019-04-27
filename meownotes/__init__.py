#!/usr/bin/env python3
from flask import Flask, request, redirect, render_template, session, flash, send_from_directory, url_for, send_file
import random

app = Flask(__name__)

# Landing page - either shows login/sign-up or redirects to dashboard
@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/cat")
def cat():
    # append a random number to the end of the cat image url
    # to prevent caching (otherwise same photo always shown)
    cat = "https://cataas.com/cat" + "?" +str(random.randint(1,101))
    return render_template("/cat.html", cat=cat)


if __name__ == "__main__":
    app.run(debug=True)
