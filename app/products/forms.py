from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, IntegerField, FileField, TextField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from app.models import User

class ProductForm(FlaskForm):
	name = StringField('Product Name', validators=[DataRequired()])
	product_image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
	price = IntegerField('Price', validators=[DataRequired()])
	description = TextAreaField('Description', validators=[DataRequired()])
	submit = SubmitField('Add Product')

class AddressForm(FlaskForm):
	fullname = StringField('Full Name', validators=[DataRequired()])
	phone = IntegerField('Phone', validators=[DataRequired()])
	pin_code = IntegerField('Pin Code', validators=[DataRequired()])
	state = StringField('State', validators=[DataRequired()])
	city = StringField('City', validators=[DataRequired()])
	building = StringField('Building Name', validators=[DataRequired()])
	submit = SubmitField('Proceed to payment')