import os
import secrets
import boto3
import stripe
import random
from app import db, bcrypt
from app.models import User, CallLog, Shipping, Plan
# from boto3.s3.key import Key
from PIL import Image
import pathlib
from flask import url_for, current_app
from flask_login import current_user

def save_picture(form_picture, aws_access_key_id, aws_secret_access_key, bucket_name):
	random_hex = secrets.token_hex(8)
	f_name, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(current_app.root_path, 'static/images', picture_fn)

	output_size = (125, 125)
	i = Image.open(form_picture)      # i is the new image with redused size
	i.thumbnail(output_size)
	i.save(picture_path)
	# form_picture.save(picture_path)

	upload_s3_file(picture_path, bucket_name, picture_fn, aws_access_key_id, aws_secret_access_key)
	os.remove(picture_path)
	
	return picture_fn

def delete_s3_file(filename, aws_access_key_id, aws_secret_access_key, bucket_name):
	s3_client = boto3.client(
		's3',
		aws_access_key_id=aws_access_key_id,
		aws_secret_access_key=aws_secret_access_key,
		# aws_session_token=SESSION_TOKEN
		)
	s3_client.delete_object(Bucket=bucket_name, Key=current_user.username + '/' + filename)

def upload_s3_file(filename, bucket_name, object_name, aws_access_key_id, aws_secret_access_key):
	s3_client = boto3.client(
		's3',
		aws_access_key_id=aws_access_key_id,
		aws_secret_access_key=aws_secret_access_key,
		# aws_session_token=SESSION_TOKEN
		)
	folder_name = current_user.username
	s3_client.put_object(Bucket=bucket_name, Key=(folder_name+'/'))
	response = s3_client.upload_file(filename, bucket_name, folder_name + '/' + object_name)

