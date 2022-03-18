from datetime import datetime
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager
from flask_login import UserMixin
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	__tablename__ = 'user'
	__table_args__ = {'extend_existing': True, 'schema': 'public'}
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(100))
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	shipping_id = db.Column(db.Integer)
	aws_creds = db.relationship('AWSCredentials', backref='author', lazy=True)
	shipping = db.relationship('Shipping', backref='author', lazy=True)
	subscription = db.relationship('Subscription', backref='author', lazy=True)
	# Define the relationship to Role via UserRoles
	roles = db.relationship('Role', secondary='user_roles')

	def __repr__(self):
		return f"User('{ self.username }')"

# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    # user_role = db.relationship('UserRoles', backref='user_role', lazy=True)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id, ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey(Role.id, ondelete='CASCADE'))

class AWSCredentials(db.Model, UserMixin):
	__tablename__ = 'aws_cred'
	__table_args__ = {'extend_existing': True, 'schema': 'public'}
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
	cf_status = db.Column(db.Boolean) 
	aws_key = db.Column(db.String(120))
	aws_secret = db.Column(db.String(120))
	cf_url = db.Column(db.String(120))
	s3_bucket = db.Column(db.String(120))


class CallLog(db.Model, UserMixin):
	__tablename__ = 'call_log'
	__table_args__ = {'extend_existing': True, 'schema': 'public'}
	id = db.Column(db.Integer, primary_key=True)
	session_id = db.Column(db.String, unique=True)
	call_key = db.Column(db.String, unique=True)
	call_pin = db.Column(db.String, unique=True)

class Products(db.Model, UserMixin):
	__tablename__ = 'products'
	__table_args__ = {'extend_existing': True, 'schema': 'public'}
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	image_file = db.Column(db.String(100))
	price = db.Column(db.Integer)
	description = db.Column(db.String)
	# user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

class Plan(db.Model, UserMixin):
	__tablename__ = 'plan'
	__table_args__ = {'extend_existing': True, 'schema': 'public'}
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	price = db.Column(db.Integer)
	count = db.Column(db.Integer)
	duration = db.Column(db.String)
	subscription = db.relationship('Subscription', backref='plan', lazy=True)

	# is_active = db.Column(db.Boolean)

# class PlanHistory(db.Model, UserMixin):
# 	__tablename__ = 'plan_history'
# 	__table_args__ = {'extend_existing': True}
# 	id = db.Column(db.Integer, primary_key=True)
# 	plan_id = db.Column(db.Integer)
# 	start_date = db.Column(db.DateTime())
# 	end_date = db.Column(db.DateTime())
# 	subscription_id = db.Column(db.Integer)
# 	user_id = db.Column(db.Integer)
# 	insert_ts = db.Column(db.DateTime())
 
class Orders(db.Model, UserMixin):
	__tablename__ = 'orders'
	__table_args__ = {'extend_existing': True, 'schema': 'public'}
	id = db.Column(db.Integer, primary_key=True)
	# customer_id = db.Column(db.String)
	# payment_id = db.Column(db.String)
	session_id = db.Column(db.String)
	status = db.Column(db.String)
	address = db.Column(db.String)
	user_id = db.Column(db.Integer)
	# payment_type = db.Column(db.String)

class Shipping(db.Model, UserMixin):
	__tablename__ = 'shipping'
	__table_args__ = {'extend_existing': True, 'schema': 'public'}
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
	address = db.Column(db.String)
	# cus_id_stripe = db.Column(db.String)

class Subscription(db.Model, UserMixin):
	__tablename__ = 'subscription'
	__table_args__ = {'extend_existing': True, 'schema': 'public'}
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
	plan_id = db.Column(db.Integer, db.ForeignKey(Plan.id), nullable=False)
	status = db.Column(db.String)
	# trail_period_start = db.Column(db.DateTime())
	# trail_period_end = db.Column(db.DateTime())
	# next_billing_date = db.Column(db.DateTime())
	# next_billing_price = db.Column(db.Integer)
	subscribed = db.Column(db.DateTime())
	unsubscribed = db.Column(db.DateTime())
	payment_history = db.relationship('PaymentHistory', backref='author', lazy=True)


	# payment_option = db.Column(db.String)

class PaymentHistory(db.Model, UserMixin):
	__tablename__ = 'payment_history'
	__table_args__ = {'extend_existing': True, 'schema': 'public'}
	id = db.Column(db.Integer, primary_key=True)
	subscription_id = db.Column(db.Integer, db.ForeignKey(Subscription.id), nullable=False)
	price = db.Column(db.Integer)
	start_date = db.Column(db.DateTime())
	end_date = db.Column(db.DateTime())

class Invoice(db.Model, UserMixin):
	__tablename__ = 'invoice'
	__table_args__ = {'extend_existing': True, 'schema': 'public'}
	id = db.Column(db.Integer, primary_key=True)
	customer_data = db.Column(db.String)
	subscription_id = db.Column(db.Integer, db.ForeignKey(Subscription.id), nullable=False)
	payment_history_id = db.Column(db.Integer, db.ForeignKey(PaymentHistory.id), nullable=False)
	invoice_description = db.Column(db.String)
	invoice_amount = db.Column(db.Float)
	invoice_created = db.Column(db.DateTime())
	# invoice_paid = db.Column(db.DateTime())

class Medicine(db.Model, UserMixin):
	__tablename__ = 'medicine'
	__table_args__ = {'extend_existing': True, 'schema': 'public'}
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)


class Doctors(db.Model, UserMixin):
	__tablename__ = 'doctors'
	__table_args__ = {'extend_existing': True}
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	address = db.Column(db.String)
	place = db.Column(db.String)

class RandomLoader(db.Model, UserMixin):
	__tablename__ = 'random_loader'
	__table_args__ = {'extend_existing': True, 'schema': 'public'}
	id = db.Column(db.Integer, primary_key=True)
	column1 = db.Column(db.String)
	column2 = db.Column(db.String)
	column3 = db.Column(db.String)
	column4 = db.Column(db.String)
	column5 = db.Column(db.String)
	column6 = db.Column(db.String)










