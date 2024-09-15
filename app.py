from flask import Flask, render_template, request, redirect, url_for
import time
from dish import Dish

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
active_user = None

dishes = []

@app.route('/')
def index():
    return render_template('index.html',
                           dishes=dishes)