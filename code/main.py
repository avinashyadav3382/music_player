import os
from flask import Flask
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_login import LoginManager
from application.model import User
from application.api import *

app = None
ma = None  
api = None

def create_app():
    global app, ma
    app = Flask(__name__, template_folder="templates")

    if os.getenv('ENV', "development") == "production":
        raise Exception("Currently no production config is set up.")
    else:
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)

    #ma = Marshmallow(app)
    db.init_app(app)
    api = Api(app)
    app.app_context().push()

    return app, api

app , api_instance = create_app()

app.secret_key = 'testing@123'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return db.session.get(User, int(user_id))

# Import all the controllers so they are loaded
from application.controller import *

# Add all the resources to the api
api_instance.add_resource(SongsData, '/api/songs')
api_instance.add_resource(AlbumsData, '/api/albums')


if __name__ == '__main__':
    from application.model import *
    
    with app.app_context():
        db.create_all()

    admin = User.query.filter_by(username="admin").first()
    creator = User.query.filter_by(username="creator").first()
    user = User.query.filter_by(username="user").first()

    if not admin:
        admin = User(name="admin", email="admin@admin.com", username="admin", password="admin", role="admin")
        db.session.add(admin)
        db.session.commit()
    if not creator:
        creator = User(name="creator", email="creator@creator.com", username="creator", password="creator", role="creator")
        db.session.add(creator)
        db.session.commit()
    if not user:
        user = User(name="user", email="user@user.com", username="user", password="user", role="user")
        db.session.add(user)
        db.session.commit()

    app.run(debug=True)
