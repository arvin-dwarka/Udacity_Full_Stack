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

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Coktail App"


# Connect to Database and create database session
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
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Connect to Google OAuth API and generate a user login session.
    """

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(r'/var/www/appreview/client_secrets.json', scope='')
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
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    
    flash("you are now logged in as %s" % login_session['username'])
    output = 'Login Successful.'
    return output

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """
    Connect to FB Graph API and generate a user login session.
    """

    # Check state parameter to ensure we're logging in from the current state.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    # Validate request with Facebook to generate token
    app_id = json.loads(open(r'/var/www/appreview/fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open(r'fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # strip expire tag from access token
    token = result.split("&")[0]
    # Use token to get user info from API
    url = 'https://graph.facebook.com/v2.4/me?fields=name,id,email&%s' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    print url, "\n"
    print data, "\n"
    
    # Populate user data into login_session object
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout,
    # let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists in our application
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    flash("Now logged in as %s" % login_session['username'])
    output = 'Login Successful.'
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """
    Execute request to remove access from app.
    and to revoke access from token with Facebook
    """
    
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


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
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)