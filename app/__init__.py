from flask import Flask
try:
    from config import Config
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'run')))
    from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    import os
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'webpage'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)

    db.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    from app import routes, models
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app
