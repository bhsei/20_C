from project.models.model import User
from flask import Flask, redirect, url_for,render_template,request,Blueprint
record_bp = Blueprint('record', __name__, url_prefix='/record')