import os
import urlparse
import json
import random
import httplib2
import requests
import string
from database_setup import Base, Category, Cocktails, User
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


app = Flask(__name__)

urlparse.uses_netloc.append("postgres")
# Gets DB variable from Heroku. If no DBURL is present, uses local appreview.db
dburl = urlparse.urlparse(os.getenv("DATABASE_URL", "/cocktailsdb"))
engine = create_engine('postgresql+psycopg2://%s/%s' % (dburl.netloc, dburl.path[1:]))

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template('app.html', categories=categories)

@app.route('/category/<int:category_id>/') 
@app.route('/category/<int:category_id>/cocktails/') 
def showCocktails(category_id): 
    """
    GET: Gets page of app listing for a particularly category.
    If user is logged in and has permission, then edit, add and delete buttons shown.
    """
    categories = session.query(Category).filter_by(id=category_id).one() 
    cocktails = session.query(Cocktails).filter_by( 
        category_id=category_id).all() 
    return render_template('cocktails.html', cocktails=cocktails)



@app.route('/category/JSON')
def JSONCategories():
    """ Return categories in JSON format """
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/category/<int:category_id>/cocktails/JSON')
def JSONCocktails(category_id):
    """ Return all apps from a category in JSON format """
    cocktails = session.query(Cocktails).filter_by(category_id=category_id).all()
    return jsonify(Cocktails=[i.serialize for i in cocktails])


@app.route('/category/<int:category_id>/cocktails/<int:cocktail_id>/JSON')
def JSONSingleCocktail(category_id, cocktail_id):
    """ Return details of a single app in JSON format """
    cocktail = session.query(Cocktails).filter_by(id=cocktail_id).one()
    return jsonify(Cocktail=cocktail.serialize)



if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)