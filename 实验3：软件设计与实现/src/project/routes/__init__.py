from .login_view import login_bp,login_manager
from .project_view import project_bp
from .model_view import model_bp
from .record_view import record_bp
import flask_login
def init_app(app):
    app.register_blueprint(login_bp)
    login_manager.init_app(app)
    app.register_blueprint(project_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(record_bp)
