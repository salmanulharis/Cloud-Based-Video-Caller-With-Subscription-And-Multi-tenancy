from flask import current_app as app
from app import db
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table
from flask import session, request, g
# from app.models import Tenant
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


class Tenantity():

    def __init__(subdomain):
        self.subdomain = subdomain

    def create(subdomain):
        db.session.execute('CREATE SCHEMA IF NOT EXISTS "{}";'.format(subdomain))
        db.session.commit()
        db.session.execute('SET search_path TO "{}";'.format(subdomain))
        db.session.commit()
        db.create_all(bind=None)


    def switch(subdomain):
        db.session.execute('set search_path to "{}"'.format(subdomain))
        session['subdomain'] = subdomain

    def switch_to_owner():
        subdomain = request.host.split('.')[0]
        Tenantity.switch(subdomain)