import os
import random
import string
import stripe
import json
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt, opentok, opentok_api
from app.models import User, CallLog, Shipping, AWSCredentials, Subscription
from app.users.forms import RegistrationForm, LoginForm, ProfileForm, AWSForm, AddressForm
from app.users.utils import save_picture, delete_s3_file
from app.subscriptions.utils import create_subscription
from app.tenantity import Tenantity

from opentok import MediaModes


users = Blueprint('users', __name__)

@users.route('/add_address', methods=['GET','POST'])
def add_address():
    form = AddressForm()
    url = request.referrer
    return render_template('address.html', form=form, url=url, heading='Add Address', submit='Save Address')

@users.route('/edit_address', methods=['GET','POST'])
def edit_address():
    form = AddressForm()
    current_address = Shipping.query.filter_by(user_id=current_user.id).first()
    add = json.loads(current_address.address)

    form.fullname.data = add['fullname']
    form.phone.data = add['phone']
    form.pin_code.data = add['pin_code']
    form.state.data = add['state']
    form.city.data = add['city']
    form.building.data = add['building']

    url = request.referrer
    return render_template('address.html', form=form, url=url, heading='Edit Address', submit='Edit Address')

@users.route('/save_address', methods=['POST', 'GET'])
def save_address():
	shipping = Shipping()
	has_address = Shipping.query.filter_by(user_id=current_user.id).first()
	
	address_form = request.form
	address = dict(address_form)
	url = address['url']
	del address['csrf_token']
	del address['submit']
	del address['url']

	if has_address:
		has_address.user_id = current_user.id
		has_address.address = json.dumps(address)
	else:
		shipping.user_id = current_user.id
		shipping.address = json.dumps(address)
		db.session.add(shipping)
	db.session.commit()

	return redirect(url)

# @users.route('/show_address/', methods=['POST', 'GET'])
# def show_address():
# 	addresses = Shipping.query.filter_by(user_id=current_user.id)
# 	address_dict = {}
# 	for address in addresses:
# 		add = json.loads(address.address)
# 		address_dict[address.id] = add
# 	return render_template('show_address.html', addresses=address_dict, used_add=current_user.shipping_id)

# @users.route('/using_address/<address_id>')
# def using_address(address_id):
# 	print(dir(request))
# 	url = request.referrer
# 	current_user.shipping_id = address_id
# 	db.session.commit()
# 	return redirect(url)

@users.route('/register', methods=['POST', 'GET'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('users.home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password, image_file='default.png')
		Tenantity.create(form.username.data)
		Tenantity.switch('public')
		db.session.add(user)
		db.session.commit()

		flash(f'Your account has been created!', 'success')          #flash is a bootstrap thing imported through flask
		return redirect(url_for('users.login'))
	return render_template('register.html', title='Register', form=form)

@users.route('/login', methods=['POST', 'GET'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('users.home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')

			# if not Subscription.query.filter_by(user_id=current_user.id).first():
			# 	create_subscription(0, 'active')

			return redirect(next_page) if next_page else redirect(url_for('users.home'))
		else:
			flash('Login Unsuccesfull! please check email and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@users.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('users.login'))



@users.route('/home')
@users.route('/')
@login_required
def home():
	subs_history = Subscription.query.filter_by(user_id=current_user.id, status='active').first()
	if not subs_history:
		return redirect(url_for('subscriptions.sub_approve'))
	user = current_user.username
	return render_template('home.html', user=user, subs_history=subs_history)

@login_required
@users.route('/user_details', methods=['POST', 'GET'])
def user_details():
	user = current_user
	form = ProfileForm()

	#------------------AWS-----------------------#
	aws_cred = AWSCredentials.query.filter_by(user_id=current_user.id).first()
	aws_form = AWSForm()
	if aws_cred:
		aws_satus = aws_cred.cf_status
		if aws_satus:
			checked = 'checked'
			if aws_cred.aws_key and aws_cred.aws_secret and aws_cred.cf_url:
				aws_form.aws_key.data = aws_cred.aws_key
				aws_form.aws_secret_key.data = aws_cred.aws_secret
				aws_form.cf_url.data = aws_cred.cf_url
				aws_form.s3_bucket.data = aws_cred.s3_bucket
				key, secret_key, bucket, cf_url = aws_cred.aws_key, aws_cred.aws_secret, aws_cred.s3_bucket, aws_cred.cf_url
				cf_status = 'using private cloudfront data'
			else:
				cf_status = 'since there no data, using public cloudfront'
				key, secret_key, bucket, cf_url = os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY'), os.getenv('AWS_BUCKET_NAME'), os.getenv('CF_DISTRIBUTION_DOMAIN_NAME')
		else:
			checked = ''
			key, secret_key, bucket, cf_url = os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY'), os.getenv('AWS_BUCKET_NAME'), os.getenv('CF_DISTRIBUTION_DOMAIN_NAME')
			cf_status = 'using public cloudfront'
	else:
		checked = ''
		key, secret_key, bucket, cf_url = os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY'), os.getenv('AWS_BUCKET_NAME'), os.getenv('CF_DISTRIBUTION_DOMAIN_NAME')
		cf_status = 'using public cloudfront'

	# cf_url = os.getenv('CF_DISTRIBUTION_DOMAIN_NAME')
	filename = current_user.image_file
	pro_pic_link = cf_url + '/' + current_user.username + '/' + filename
	#------------------AWS-----------------------#

	if form.validate_on_submit():
		if form.photo.data:
			if current_user.image_file:
				delete_s3_file(current_user.image_file, key, secret_key, bucket)
			picture_file = save_picture(form.photo.data, key, secret_key, bucket)
			current_user.image_file = picture_file
		db.session.commit()
	return render_template('details.html', user=user.username, form=form, aws_form=aws_form, pro_pic_link=pro_pic_link,
		cf_status=cf_status, check=checked)


#------------------AWS-----------------------#
@users.route('/save_cf_details', methods=['POST', 'GET'])
def save_cf_details():
	aws_form = AWSForm()
	aws_cred = AWSCredentials.query.filter_by(user_id=current_user.id).first()
	if aws_form.validate_on_submit():
		aws_cred.aws_key = aws_form.aws_key.data
		aws_cred.aws_secret = aws_form.aws_secret_key.data
		aws_cred.cf_url = aws_form.cf_url.data
		aws_cred.s3_bucket = aws_form.s3_bucket.data
		db.session.commit()


	return redirect(url_for('users.user_details'))

@users.route('/aws_status_change', methods=['POST', 'GET'])
def aws_status_change():
	status = request.args.get('aws_check')
	aws_cred = AWSCredentials()
	user_aws_cred = AWSCredentials.query.filter_by(user_id=current_user.id).first()
	if status == 'true':
		if user_aws_cred:
			user_aws_cred.cf_status = True
		else:
			aws_cred.user_id = current_user.id
			aws_cred.cf_status = True
			db.session.add(aws_cred)
			# db.session.commit()
	else:
		user_aws_cred.cf_status = False
	db.session.commit()
	return status
#------------------AWS-----------------------#




