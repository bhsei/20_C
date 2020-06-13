import flask_login
from flask import Flask, redirect,render_template,request,Blueprint

index_bp = Blueprint('index', __name__, url_prefix='/')

@index_bp.route('/', methods=['GET', 'POST'])
def add():
    print("index")
    return render_template('home.html', user=flask_login.current_user)