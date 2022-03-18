from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, IntegerField, FileField, TextField, TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from app.models import User

class SubProductForm(FlaskForm):
	name = StringField('Product Name', validators=[DataRequired()])
	price = FloatField('Price', validators=[DataRequired()])
	subscription = SelectField(u'Subscription for?', choices=[('day', 'Daily'), ('week', 'Weekly'), ('month', 'Monthly'), ('year', 'Yearly')])
	submit = SubmitField('Add Product')