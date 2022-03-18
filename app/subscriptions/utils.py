import stripe
import json

from flask_login import current_user, login_required
from app.models import Products, Orders, Plan, Subscription, Shipping, PaymentHistory, Invoice#, PlanHistory
from app import db, bcrypt
from datetime import timedelta, date, datetime
from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify


def get_product_id(name):
	product = stripe.Product.create(name=name)
	return product.id

def get_price_id(product_id, price, interval):
	price = stripe.Price.create(
			  unit_amount=price,
			  currency="inr",
			  recurring={"interval": interval},
			  product=product_id,
			)
	return price.id

def create_stripe_cus(address):
	customer = stripe.Customer.create(
		address={
			'city':address['city'],
			'country': 'IN',
			'line1': address['building'],
			'line2': None,
			'postal_code': address['pin_code'],
			'state': address['state'],
		},
		name=address['fullname'],
		phone=address['phone'],
		email=current_user.email,
	)
	return customer.id

def create_price(plan):
	product = stripe.Product.create(name=plan.name)
	price = stripe.Price.create(
			  unit_amount=plan.price * 100,
			  currency="inr",
			  recurring={"interval": plan.duration},
			  product=product.id,
			)
	return price.id

# def create_stripe_session(customer_id, price_id, plan):
def create_stripe_session(customer_id, price_id):
	stripe_checkout_session = stripe.checkout.Session.create(
		customer=customer_id,
		payment_method_types=['card'],
		line_items=[
		    {
		        'price': price_id,
		        'quantity': 1,
		    },
		],
		mode='subscription',
		success_url=url_for('subscriptions.sub_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
		cancel_url=url_for('subscriptions.sub_cancel', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
	)
	# subscription_id = save_subscription(stripe_checkout_session.id, plan, payment_option='stripe')
	return stripe_checkout_session


def create_subscription(plan_id,status):
	subscription = Subscription()
	subscription.plan_id = plan_id
	subscription.user_id = current_user.id
	subscription.status = status
	subscription.subscribed = datetime.now()
	subscription.unsubscribed = None
	db.session.add(subscription)
	db.session.commit()
	return subscription.id

def create_payment_history(subscription, plan):
	if plan.duration == 'day':
		days=1
	elif plan.duration == 'month':
		days=30

	payment_history = PaymentHistory()
	payment_history.subscription_id = subscription.id
	payment_history.price = plan.price
	payment_history.start_date = datetime.now()
	payment_history.end_date = datetime.now() + timedelta(days=plan.count * days)
	db.session.add(payment_history)
	db.session.commit()
	return payment_history

def cancel_prev_subs():
	subscription = Subscription.query.filter_by(status='active' or 'trailing',user_id=current_user.id).first()
	if subscription:
		subscription.status = 'cancelled'
		subscription.unsubscribed = datetime.now()
		payment_history = PaymentHistory.query.filter_by(subscription_id=subscription.id).first()
		if payment_history:
			print('exact')
			payment_history.end_date = datetime.now()
	return 'Success'

def delete_cancelled_sub():
	incomplete_subscription = Subscription.query.filter_by(status='incomplete',user_id=current_user.id).first()
	if incomplete_subscription:
		db.session.delete(incomplete_subscription)
		db.session.commit()

def create_invoice(payment_history_id, subscription_id, plan):
	invoice = Invoice()
	shipping = Shipping.query.filter_by(user_id=current_user.id).first()
	address = {'address':json.loads(shipping.address)}

	invoice.customer_data = json.dumps(address)
	invoice.subscription_id = subscription_id
	invoice.payment_history_id = payment_history_id
	invoice.invoice_description = 'very good invoice'
	invoice.invoice_amount = plan.price
	invoice.invoice_created = datetime.now()
	db.session.add(invoice)
	db.session.commit()
	return invoice.id


# def create_plan_history(subscription):
# 	plan_history = PlanHistory()
# 	current_plan_history = PlanHistory.query.filter_by(user_id=current_user.id).first()
# 	if current_plan_history:
# 		current_plan_history.subscription_id = subscription.id
# 		current_plan_history.plan_id = subscription.plan_id
# 	else:
# 		plan_history.plan_id = subscription.plan_id
# 		plan_history.subscription_id = subscription.id
# 		plan_history.user_id = current_user.id
# 		db.session.add(plan_history)
# 	db.session.commit()


# def save_subscription(session_id, plan, payment_option):
# 	subscription = Subscription()
# 	subscription_exist = Subscription.query.filter_by(session_id=session_id).first()
# 	if plan.duration == 'day':
# 		days=1
# 	elif plan.duration == 'month':
# 		days=30

# 	if not subscription_exist:
# 		subscription.session_id = session_id
# 		subscription.status = 'incomplete'
# 		subscription.user_id = current_user.id
# 		subscription.plan_id = plan.id
# 		subscription.payment_option = payment_option
# 		subscription.valid_to = date.today() + timedelta(days=days)
# 		db.session.add(subscription)
# 		db.session.commit()


