import json
import os
import stripe
from app import db, bcrypt
from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import current_user, login_required
import stripe
from app.products.forms import ProductForm, AddressForm
from app.models import Products, Orders
from app.users.utils import save_picture


products = Blueprint('products', __name__)


@login_required
@products.route('/delivery_address', methods=['GET','POST'])
def delivery_address():
  form = AddressForm()
  return render_template('products/address.html', form=form)

@login_required
@products.route('/checkout_page', methods=['GET','POST'])
def checkout_page():
  products = Products.query.all()
  total = 0
  for product in products:
    total = total + product.price

  return render_template('products/checkout.html', products=products, total=total)

@login_required
@products.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
  orders = Orders()
  address_form = request.form
  address = dict(address_form)
  del address['csrf_token']
  del address['submit']

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

  products = Products.query.all()
  line_items=[]
  for product in products:
    price = product.price * 100
    product = stripe.Product.create(
      name=product.name,
    )
    price = stripe.Price.create(
      product=product.get('id'),
      unit_amount=price,
      currency='inr',
    )
    items = {
      'price':price.get('id'),
      'quantity':1,
    }
    stripe.InvoiceItem.create(
      customer=customer.id,
      price=price.id,
    )
    line_items.append(items)

  invoice = stripe.Invoice.create(
    customer=customer.id,
    auto_advance=True, # Auto-finalize this draft after ~1 hour
    collection_method='charge_automatically'
  )

  # payment_intent = stripe.PaymentIntent.create(
  #   amount=2000,
  #   currency="usd",
  #   payment_method_types=["card"],
  #   customer=customer.id
  # )

  session = stripe.checkout.Session.create(
    customer=customer.id,
    # payment_intent= payment_intent.id,
    payment_method_types=['card'],
    line_items=line_items,
    mode='payment',
    success_url=url_for('products.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
    cancel_url=url_for('products.cancel', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
  )

  orders.session_id = session.id
  orders.status = session.payment_status
  orders.address = json.dumps(address)
  orders.user_id = current_user.id
  db.session.add(orders)
  db.session.commit()

  return redirect(session.url, code=303)

@login_required
@products.route('/pay_again/<session_id>', methods=['GET','POST'])
def pay_again(session_id):
  session = stripe.checkout.Session.retrieve(session_id)
  return redirect(session.url, code=303)

@products.route('/success', methods=['GET','POST'])
def success():
  session_id = request.args.get('session_id')
  session = stripe.checkout.Session.retrieve(session_id)
  order = Orders.query.filter_by(session_id=session_id).first()
  order.status = session.payment_status
  db.session.commit()
  return render_template('products/success.html')

@products.route('/cancel', methods=['GET','POST'])
def cancel():
  session_id = request.args.get('session_id')
  return render_template('products/cancel.html', session_id=session_id)


@products.route('/add_product', methods=['GET','POST'])
def add_product():
  form = ProductForm()
  return render_template('products/add_product.html', form=form)

@products.route('/product_save', methods=['GET','POST'])
def product_save():
  form = ProductForm()
  key, secret_key, bucket, cf_url = os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY'), os.getenv('AWS_BUCKET_NAME'), os.getenv('CF_DISTRIBUTION_DOMAIN_NAME')
  product = Products()
  if form.validate_on_submit():
    product.name = form.name.data
    product.price = form.price.data
    product.description = form.description.data
    if form.product_image.data:
      # image_file = save_picture(form.product_image.data, key, secret_key, bucket)
      # product.image_file = image_file
      product.image_file = form.product_image.data
    db.session.add(product)
    db.session.commit()
    products = Products.query.all()
  return render_template('products/products.html', products=products)

@products.route('/show_products', methods=['GET','POST'])
def show_products():
  products = Products.query.all()
  total = 0
  for product in products:
    total = total + product.price
  return render_template('products/products.html', products=products, total=total)

@products.route('/webhook', methods=['POST'])
def webhook():
    endpoint_secret = 'whsec_VTqz3u0wNYPIeiMLT63gdMCi6H6bR2I2'
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
      payment_intent = event['data']['object']
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)

@login_required
@products.route('/order_list', methods=['GET','POST'])
def order_list():
  orders = Orders.query.filter_by(user_id=current_user.id)
  return render_template('products/orders.html', orders=orders)

