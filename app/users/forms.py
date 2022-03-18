from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from app.models import User

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Username is already taken, please choose other one.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Email is already exist!, please choose other one.')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me') #for remember password cookies
	submit = SubmitField('Login')

class ProfileForm(FlaskForm):
	photo = FileField('Update profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
	submit = SubmitField('Update Photo')

class AWSForm(FlaskForm):
	aws_key = StringField('AWS Access Key Id', validators=[DataRequired()])
	aws_secret_key = StringField('AWS Secret Access Key', validators=[DataRequired()])
	cf_url = StringField('Cloudfront Distribution Domain', validators=[DataRequired()])
	s3_bucket = StringField('S3 Bucket Name', validators=[DataRequired()])
	submit = SubmitField('Submit')

class AddressForm(FlaskForm):
	fullname = StringField('Full Name', validators=[DataRequired()])
	phone = IntegerField('Phone', validators=[DataRequired()])
	pin_code = IntegerField('Pin Code', validators=[DataRequired()])
	state = StringField('State', validators=[DataRequired()])
	city = StringField('City', validators=[DataRequired()])
	building = StringField('Building Name', validators=[DataRequired()])
	# submit = SubmitField('Save Address')
