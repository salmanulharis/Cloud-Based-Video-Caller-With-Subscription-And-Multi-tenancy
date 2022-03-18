import json
import os
import names
from app import db, bcrypt
from datetime import timedelta, date, datetime
from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import current_user, login_required
from app.models import Medicine, RandomLoader
from sqlalchemy import or_



autopopulate = Blueprint('autopopulate', __name__)

@login_required
@autopopulate.route('/generate_data', methods=['GET'])
def generate_data():
	# medicine = Medicine()
	# for i in range(100000):
	# 	medicine = Medicine()
	# 	name = names.get_full_name()
	# 	medicine.name = name
	# 	db.session.add(medicine)
	# 	db.session.commit()
	# 	print(i)

	return redirect(url_for('autopopulate.populate_data'))

@login_required
@autopopulate.route('/populate_data', methods=['GET'])
def populate_data():
	return render_template('autopopulate/autopopulate.html')

@login_required
@autopopulate.route('/get_populated_data', methods=['GET'])
def get_populated_data():
	name_list = []
	search = request.args['search_value']
	# medicines = Medicine.query.all()
	if search:
		print(datetime.now())
		# medicines = Medicine.query.filter(Medicine.name.contains(search)).limit(30)
		medicines = RandomLoader.query.filter(or_(
				RandomLoader.column1.contains(search),
				RandomLoader.column2.contains(search),
				RandomLoader.column3.contains(search),
				RandomLoader.column4.contains(search),
				RandomLoader.column5.contains(search),
				RandomLoader.column6.contains(search))).limit(20)
		print(datetime.now())
		for medicine in medicines:
			names = {'column1':medicine.column1,
					'column2':medicine.column2,
					'column3':medicine.column3,
					'column4':medicine.column4,
					'column5':medicine.column5,
					'column6':medicine.column6,
					}
			name_list.append(names)
	# if search:
	# 	for medicine in medicines:
	# 		if medicine.name.lower().startswith(search.lower()):
	# 			name_list.append(medicine.name)
	# print(name_list)
	return {'data': name_list}
