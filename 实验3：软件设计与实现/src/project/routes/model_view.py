from project.models.model import User
from flask import Flask, redirect, url_for,render_template,request,Blueprint
## 登录的路由和逻辑都在这页了
model_bp = Blueprint('model', __name__, url_prefix='/model')