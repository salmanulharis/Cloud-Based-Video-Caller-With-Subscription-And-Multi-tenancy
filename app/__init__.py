import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
# from flask_mail import Mail
from app.config import Config
from flask_admin import Admin
from flask_migrate import Migrate
from opentok import OpenTok
import stripe

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
migrate = Migrate()
opentok = OpenTok('47344281', 'a31d1885cb3e9f04869ab66ab128dba12eaa7e29')
opentok_api = '47344281'

#-------------- stripe ---------------------------------------#
stripe_keys = {
    "secret_key": os.getenv('STRIPE_SECRET_KEY'),
    "publishable_key": os.getenv('STRIPE_PUBLISHABLE_KEY'),
}
stripe.api_key = stripe_keys["secret_key"]

#-------------- stripe ---------------------------------------#


# mail = Mail()
# admins = Admin()

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)

	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	migrate.init_app(app, db)
	# mail.init_app(app)
	# admins.init_app(app)

	from app.users.routes import users
	from app.calling.routes import calling
	from app.products.routes import products
	from app.subscriptions.routes import subscriptions
	from app.autopopulate.routes import autopopulate
	from app.errors.handlers import errors
	app.register_blueprint(users)
	app.register_blueprint(calling)
	app.register_blueprint(products)
	app.register_blueprint(subscriptions)
	app.register_blueprint(autopopulate)
	app.register_blueprint(errors)



	return app