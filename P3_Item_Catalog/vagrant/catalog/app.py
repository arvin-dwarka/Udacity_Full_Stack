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

# Login functions
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
        oauth_flow = flow_from_clientsecrets(r'client_secrets.json', scope='')
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
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    
    flash("You are now logged in as %s" % login_session['username'])
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
    app_id = json.loads(open(r'fb_client_secrets.json', 'r').read())[
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

    flash("You are now logged in as %s" % login_session['username'])
    output = 'Login Successful.'
    return output

@app.route('/gdisconnect')
def gdisconnect():
    """
    Execute request to remove access from app.
    and to revoke access from token with Google
    """

    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session.get('credentials')
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

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
    return "You have been logged out"

# Disconnect based on provider 
@app.route('/disconnect') 
def disconnect(): 
    """
    Execute disconnect from app based on current provider.
    Provides error message if logged out user attempts disconnect.
    """

    if 'provider' in login_session: 
        if login_session['provider'] == 'google': 
            gdisconnect() 
            del login_session['gplus_id'] 
            del login_session['credentials'] 
        if login_session['provider'] == 'facebook': 
            fbdisconnect() 
            del login_session['facebook_id'] 
        del login_session['username'] 
        del login_session['email'] 
        del login_session['picture'] 
        del login_session['user_id'] 
        del login_session['provider'] 
        flash("You have successfully been logged out.") 
        return redirect(url_for('showCategories')) 
    else: 
        flash("You were not logged in") 
        return redirect(url_for('showCategories')) 

def createUser(login_session):
    """ Helper to create User object in the database """
    
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """ Query database for user info"""
    
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """ Get user ID from provided e-mail address """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Main logic
# Show all available categories
@app.route('/')
@app.route('/category/')
def showCategories():
    """
    Lists out all categories to rendered page
    """
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session:
        return render_template('public_app.html', categories=categories)
    else:
        return render_template('app.html', categories=categories)

# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    """
    GET: Opens new category page if user is logged in.
    POST: Creates new category and commits to the database.
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new_category = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(new_category)
        flash('New Category %s Successfully Created' % new_category.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('new_category.html')

# Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    """
    GET: Opens category edit page for category_id if user is logged in.
    POST: Modifies category based on form and commits to the database.
    """
    edit_cat = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('login')
    if edit_cat.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('Unauthorized!" \
               "Create your own categories by logging in!');}</script>" \
                "<body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            edit_cat.name = request.form['name']
            flash('Category Successfully Edited: %s' % edit_cat.name)
            return redirect(url_for('showCategories'))
    else:
        return render_template('edit_category.html', category=edit_cat)

# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    """
    GET: Gets delete category page for category_id if user is logged in.
    POST: Deletes category from database and commits change.
    """
    del_cat = session.query(Category).filter_by(id=category_id).one() 
    if 'username' not in login_session: 
        return redirect('/login') 
    if del_cat.user_id != login_session['user_id']: 
        return "<script>function myFunction() {alert('You are not authorized to delete this category. " \
               "Please create your own category in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(del_cat) 
        flash('%s Successfully Deleted' % del_cat.name) 
        session.commit() 
        return redirect(url_for('showCategories', category_id=category_id)) 
    else: 
        return render_template('delete_category.html', category=del_cat) 

# Show all cocktails within a category
@app.route('/category/<int:category_id>/') 
@app.route('/category/<int:category_id>/cocktails/') 
def showCocktails(category_id): 
    """
    GET: Gets a list of cocktails within a category.
    If user is logged in and has permission, then edit, add and 
    delete buttons shown.
    """
    category = session.query(Category).filter_by(id=category_id).one() 
    cocktails = session.query(Cocktails).filter_by( 
        category_id=category_id).all()
    user = getUserInfo(category.user_id)
    if 'username' not in login_session or user.id !=  login_session['user_id']:
        return render_template('public_cocktails.html', category=category, 
            cocktails=cocktails, user=user)
    else:
        return render_template('cocktails.html', category=category, 
            cocktails=cocktails, user=user)

# Create new cocktails drinks
@app.route('/category/<int:category_id>/apps/new/', methods=['GET', 'POST']) 
def newCocktail(category_id): 
    """
    GET: Renders new cocktail page if user is logged in.
    POST: Creates new app and commits to the database. 
    """
    if 'username' not in login_session: 
        return redirect('/login') 
    category = session.query(Category).filter_by(id=category_id).one() 
    if login_session['user_id'] != category.user_id: 
        return "<script>function myFunction() {alert('You are not authorized to add apps to this category. " \
               "Please create your own category in order to add apps.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        new_cocktail = Cocktails(name=request.form['name'], 
            description=request.form['description'],
            price=request.form['price'],
            category_id=category_id,
            user_id=login_session['user_id'])
        session.add(new_cocktail)
        session.commit()
        flash("New cocktail: %s successfully created" %new_cocktail.name)
        return redirect(url_for('showCocktails', category_id=category_id))
    else:
        return render_template('new_cocktail.html', category_id=category_id)

# Edit a cocktail
@app.route('/category/<int:category_id>/cocktails/<int:cocktails_id>/edit', methods=['GET', 'POST']) 
def editCocktail(category_id, cocktails_id): 
    """
    GET: Opens edit page for cocktail_id if user is logged in.
    POST: Modifies cocktail based on form and commits to the database.
    """
    if 'username' not in login_session: 
        return redirect('/login') 
    edit_cocktail = session.query(Cocktails).filter_by(id=cocktails_id).one() 
    category = session.query(Category).filter_by(id=category_id).one() 
    if login_session['user_id'] != category.user_id: 
        return "<script>function myFunction() {alert('You are not authorized to edit apps in this category. " \
               "Please create your own category in order to edit apps.');}</script><body onload='myFunction()''>"
    if request.method == 'POST': 
        if request.form['name']: 
            edit_cocktail.name = request.form['name'] 
        if request.form['description']: 
            edit_cocktail.description = request.form['description'] 
        else:
            edit_cocktail.description = ''
        if request.form['price']: 
            edit_cocktail.price = request.form['price'] 
        else:
            edit_cocktail.price = ''
        session.add(edit_cocktail) 
        session.commit() 
        flash('%s successfully edited' %edit_cocktail.name) 
        return redirect(url_for('showCocktails', category_id=category_id)) 
    else: 
        return render_template('edit_cocktail.html', category_id=category_id, 
            cocktails_id=cocktails_id, cocktail=edit_cocktail) 

# Delete a cocktail
@app.route('/category/<int:category_id>/cocktails/<int:cocktails_id>/delete', methods=['GET', 'POST']) 
def deleteCocktail(category_id, cocktails_id): 
    """
    GET: Redenders delete page for a cocktail if user is logged in.
    POST: Deletes cocktail from database and commits change.
    """
    if 'username' not in login_session: 
        return redirect('/login') 
    category = session.query(Category).filter_by(id=category_id).one() 
    del_cocktail = session.query(Cocktails).filter_by(id=cocktails_id).one() 
    if login_session['user_id'] != category.user_id: 
        return "<script>function myFunction() {alert('You are not authorized to delete apps from this category. " \
               "Please create your own category in order to delete apps.');}</script><body onload='myFunction()''>"
    if request.method == 'POST': 
        session.delete(del_cocktail) 
        session.commit() 
        flash('%s successfully deleted' %del_cocktail.name) 
        return redirect(url_for('showCocktails', category_id=category_id)) 
    else: 
        return render_template('delete_cocktail.html', cocktail=del_cocktail) 

# Make JSON data available for all categories
@app.route('/category/JSON')
def JSONCategories():
    """
    Return categories in JSON format
    """
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])

# Make JSON data available for all cocktails within a category
@app.route('/category/<int:category_id>/cocktails/JSON')
def JSONCocktails(category_id):
    """
    Return all cocktails within a category in JSON format
    """
    cocktails = session.query(Cocktails).filter_by(category_id=category_id).all()
    return jsonify(Cocktails=[i.serialize for i in cocktails])

# Make JSON data available for a single cocktail within a category
@app.route('/category/<int:category_id>/cocktails/<int:cocktail_id>/JSON')
def JSONSingleCocktail(category_id, cocktail_id):
    """
    Return details of a single cocktail in JSON format
    """
    cocktail = session.query(Cocktails).filter_by(id=cocktail_id).one()
    return jsonify(Cocktail=cocktail.serialize)

if __name__ == '__main__':
    app.secret_key = 'weoaAWJpB9i9hA'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)