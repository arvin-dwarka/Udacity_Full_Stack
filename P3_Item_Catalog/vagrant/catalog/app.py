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

#login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.
        digits) for x in xrange(32))
    login_session['state'] = state
    return 'The current session state is %s' %login_session['state']

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output    


#app stuffs
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