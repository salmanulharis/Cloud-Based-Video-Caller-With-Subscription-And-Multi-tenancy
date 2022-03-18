import json
import os
import stripe
from app import db, bcrypt
from datetime import timedelta, date, datetime
from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import current_user, login_required
import stripe
from app.users.forms import AddressForm
from app.subscriptions.forms import SubProductForm
from app.models import Products, Orders, Plan, Subscription, Shipping, PaymentHistory, Invoice
from app.subscriptions.utils import get_product_id, get_price_id, create_price, create_stripe_cus, create_stripe_session, create_subscription, create_payment_history, cancel_prev_subs, delete_cancelled_sub, create_invoice
from app.utils import access_level


subscriptions = Blueprint('subscriptions', __name__)

@login_required
@subscriptions.route('/sub_approve', methods=['GET'])
def sub_approve():
    plans = Plan.query.all()
    subs_history = Subscription.query.filter_by(user_id=current_user.id, status='active' or 'trailing').first()
    return render_template('subscriptions/product.html', plans=plans, subs_history=subs_history)


@subscriptions.route('/sub_address/<plan_id>', methods=['GET','POST'])
def sub_address(plan_id):
    if plan_id == '0':
        cancel_prev_subs()
        delete_cancelled_sub()
        create_subscription(0, 'incomplete')
        return redirect(url_for('subscriptions.sub_success'))
    form = AddressForm()
    current_address = Shipping.query.filter_by(user_id=current_user.id).first()
    if current_address:
        add = json.loads(current_address.address)

        form.fullname.data = add['fullname']
        form.phone.data = add['phone']
        form.pin_code.data = add['pin_code']
        form.state.data = add['state']
        form.city.data = add['city']
        form.building.data = add['building']

    url = url_for('subscriptions.payment_options', plan_id=plan_id)
    return render_template('address.html', form=form, url=url, heading='Subscription Address', submit='Continue')

@login_required
@subscriptions.route('/payment_options/<plan_id>', methods=['GET'])
def payment_options(plan_id):
    delete_cancelled_sub()
    return render_template('subscriptions/payment_options.html', plan_id=plan_id)

@login_required
@subscriptions.route('/stripe_payment/<plan_id>', methods=['GET','POST'])
def stripe_payment(plan_id):
    shipping = Shipping.query.filter_by(user_id=current_user.id).first()
    plan = Plan.query.filter_by(id=plan_id).first()
    address = json.loads(shipping.address)
    customer_id = create_stripe_cus(address)
    price_id = create_price(plan)

    # incomplete_subscription = Subscription.query.filter_by(status='incomplete',user_id=current_user.id).first()
    # if incomplete_subscription:
    #     db.session.delete(incomplete_subscription)

    # cancel_prev_subs()
    subs_id = create_subscription(plan_id, 'incomplete')

    try:
        # stripe_checkout_session = create_stripe_session(customer_id,price_id,plan)
        stripe_checkout_session = create_stripe_session(customer_id,price_id)
        return redirect(stripe_checkout_session.url, code=303)
    except Exception as e:
        print(e)
        return "Server error", 500

@login_required
@subscriptions.route('/sub-success', methods=['GET', 'POST'])
def sub_success():
    session_id = request.args.get('session_id')
    if session_id:
        session = stripe.checkout.Session.retrieve(session_id)
        current_subscription = stripe.Subscription.retrieve(session.subscription)

    cancel_prev_subs()
    subscription = Subscription.query.filter_by(user_id=current_user.id, status='incomplete').first()
    if subscription:
        subscription.status = 'active'
        plan = Plan.query.filter_by(id=subscription.plan_id).first()
        if not plan.id == 0:
            payment_hist = create_payment_history(subscription, plan)
            invoice_id = create_invoice(payment_hist.id, subscription.id, plan)
    
    db.session.commit()
    
    return render_template('subscriptions/success.html')
    # return redirect(url_for('subscriptions.sub_approve'))

@login_required
@subscriptions.route('/sub-cancel', methods=['GET', 'POST'])
def sub_cancel():
    subscription = Subscription.query.filter_by(user_id=current_user.id, status='incomplete').first()
    return redirect(url_for('subscriptions.payment_options', plan_id=subscription.plan_id))
    # return render_template('subscriptions/cancel.html', plan_id=subscription.plan_id)

@login_required
@subscriptions.route('/orders', methods=['GET', 'POST'])
# @access_level(['Admin'])
def orders():
    subs = Subscription.query.filter_by(user_id=current_user.id)
    payment_history = []
    for sub in subs:
        history =  PaymentHistory.query.filter_by(subscription_id=sub.id).first()
        payment_history.append(history)

    return render_template('subscriptions/orders.html', payment_history=payment_history)

@login_required
@subscriptions.route('/show_invoice/<payment_history_id>', methods=['GET', 'POST'])
# @access_level(['User'])
def show_invoice(payment_history_id):
    invoice = Invoice.query.filter_by(payment_history_id=payment_history_id).first()
    return render_template('subscriptions/show_invoice.html', invoice=invoice)

@login_required
@subscriptions.route('/unsubscribe', methods=['GET', 'POST'])
def unsubscribe():
    # plan_history = .query.filter_by(user_id=current_user.id).first()
    db.session.delete(plan_history)

    subscription = Subscription.query.filter_by(user_id=current_user.id,status='complete').first()
    session = stripe.checkout.Session.retrieve(subscription.session_id)
    unsubscribe = stripe.Subscription.delete(session.subscription)
    subscription.status = unsubscribe.status
    db.session.commit()
    return redirect(request.referrer)




@subscriptions.route('/create-portal-session', methods=['GET', 'POST'])
def customer_portal():
    # For demonstration purposes, we're using the Checkout session to retrieve the customer ID.
    # Typically this is stored alongside the authenticated user in your database.
    checkout_session_id = 'cs_test_a12koA692OgwTB1SAq7fbqdomZOruoNsXwspyYAJKfaRfEFldnYGfxFvye'
    checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)
    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    return_url = 'http://127.0.0.1:5000/sub_products'
    portalSession = stripe.billing_portal.Session.create(
        customer=checkout_session.customer,
        return_url=return_url,
    )
    return redirect(portalSession.url, code=303)
@subscriptions.route('/webhook_sub', methods=['POST'])
def webhook_received():
    # Replace this endpoint secret with your endpoint's unique secret
    # If you are testing with the CLI, find the secret by running 'stripe listen'
    # If you are using an endpoint defined with the API or dashboard, look in your webhook settings
    # at https://dashboard.stripe.com/webhooks
    webhook_secret = 'whsec_VTqz3u0wNYPIeiMLT63gdMCi6H6bR2I2'
    request_data = json.loads(request.data)
    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']
    print('event ' + event_type)
    if event_type == 'checkout.session.completed':
        print('🔔 Payment succeeded!')
    elif event_type == 'customer.subscription.trial_will_end':
        print('Subscription trial will end')
    elif event_type == 'customer.subscription.created':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.updated':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.deleted':
        # handle subscription cancelled automatically based
        # upon your subscription settings. Or if the user cancels it.
        print('Subscription canceled: %s', event.id)
    return jsonify({'status': 'success'})


# @subscriptions.route('/delivery_address_sub', methods=['GET','POST'])
# def delivery_address_sub():
#   form = AddressForm()
#   return render_template('products/address.html', form=form)

# @subscriptions.route('/create_sub_product', methods=['GET','POST'])
# def create_sub_product():
#     form = SubProductForm()
#     return render_template('subscriptions/add_sub_product.html', form=form)


# @subscriptions.route('/save_sub_product', methods=['GET','POST'])
# def save_sub_product():
#     form = SubProductForm()
#     plan = Plan()
#     if form.validate_on_submit():
#         plan.name = form.name.data
#         plan.price = form.price.data
#         plan.duration = form.subscription.data
#         product_id = get_product_id(form.name.data)
#         plan.product_id = product_id
#         plan.price_id = get_price_id(product_id, form.price.data, form.subscription.data)
#     db.session.add(plan)
#     db.session.commit()

#     return redirect(url_for('subscriptions.sub_products'))

# @subscriptions.route('/create_customer/<price_id>', methods=['GET','POST'])
# def create_customer(price_id):
#     form = AddressForm()
#     return render_template('address.html', price_id=price_id, form=form)

# @login_required
# @subscriptions.route('/sub_address/<plan_id>', methods=['GET'])
# def sub_address(plan_id):
#     shipping = Shipping.query.filter_by(user_id=current_user.id).first()
#     if not shipping:
#         return redirect(url_for('users.add_address'))
#     address = json.loads(shipping.address)
#     return render_template('subscriptions/use_address.html', address=address, plan_id=plan_id)


# @login_required
# @subscriptions.route('/sub_address/<plan_id>', methods=['GET'])
# def sub_address(plan_id):
#     shipping = Shipping.query.filter_by(id=current_user.shipping_id).first()
#     selected_add = json.loads(shipping.address)
#     addresses = Shipping.query.filter_by(user_id=current_user.id)
#     address_dict = {}
#     for address in addresses:
#         add = json.loads(address.address)
#         address_dict[address.id] = add
#     return render_template('subscriptions/address.html', selected_add=selected_add, plan_id=plan_id, addresses=address_dict, used_add=current_user.shipping_id)
