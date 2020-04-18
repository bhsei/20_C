from project.models.model import User
from flask import Flask, redirect, url_for,render_template,request,Blueprint
project_bp = Blueprint('project', __name__, url_prefix='/project')
@project_bp.route('/hello/<name>')
def hello_name(name):
   return 'Hello %s!' % name