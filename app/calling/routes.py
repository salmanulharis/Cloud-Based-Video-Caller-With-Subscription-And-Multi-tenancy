import random
import string
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt, opentok, opentok_api
from app.models import User, CallLog
# from app.calling.forms import 
# from app.calling.utils import save_picture, send_reset_email

from opentok import MediaModes

calling = Blueprint('calling', __name__)

@login_required
@calling.route('/optok', methods=['POST', 'GET'])
def optok():
	session = opentok.create_session(media_mode=MediaModes.routed)
	session_id = session.session_id

	call_key = ''.join((random.choice(string.ascii_lowercase) for x in range(10)))
	call_key = '-'.join([call_key[:3], call_key[3:7], call_key[7:]])

	call_pin = random.randint(0000000000, 9999999999)
	call_log = CallLog(session_id=session_id, call_pin=call_pin, call_key=call_key)
	db.session.add(call_log)
	db.session.commit()


	join_url = request.host + url_for('calling.optok_join', call_key=call_key)

	return render_template('optok.html', call_key=call_key, join_url=join_url, call_pin=call_pin)

# @login_required
@calling.route('/optok_join/<call_key>', methods=['POST', 'GET'])
def optok_join(call_key):
	call_log = CallLog.query.filter_by(call_key=call_key).first()

	if not current_user.is_authenticated:
		return redirect(url_for('calling.call_join', call_key=call_key))

	token = opentok.generate_token(call_log.session_id)
	join_url = request.host + url_for('calling.optok_join', call_key=call_key)

	return render_template('index.html', apiKey=opentok_api, session_id=call_log.session_id, 
		token=token, user=current_user.username, join_url=join_url, call_pin=call_log.call_pin)

@calling.route('/call_join/<call_key>', methods=['POST', 'GET'])
def call_join(call_key):
	call_log = CallLog.query.filter_by(call_key=call_key).first()
	
	if call_log and request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		if call_log.call_pin == password:
			token = opentok.generate_token(call_log.session_id)
			join_url = request.host + url_for('calling.optok_join', call_key=call_key)

			return render_template('index.html', apiKey=opentok_api, session_id=call_log.session_id, 
				token=token, user=username, join_url=join_url, call_pin=call_log.call_pin)
		else:
			flash('Incorrect password!', 'danger')
			return render_template('call_join.html')

	return render_template('call_join.html', call_key=call_key)