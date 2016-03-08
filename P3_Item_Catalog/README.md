# Item Catalog

This project consists of an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

#### Description

This is a cocktail menu application that is modeled of a Vancouver cocktail lounge, The Diamond, [drink list](http://di6mond.com/wp-content/uploads/2015/11/D_Drink_NOV2015.pdf). Without siging in, you will be able to view all the drink categories and the cocktails within each respective category. When signed in via Google Plus or Facebook, you will have the option of creating, editing, and deleting categories and cocktails.

The app is hosted on heroku and can be accessed by following http://cocktails-app.herokuapp.com/

#### How to run

1. Launch the vagrant virtual machine: go to the parent directory (where
   `Vagrantfile` resides) and run `vagrant up`.

2. Log into the virtual machine with `vagrant ssh`, and then go to
   `/vagrant/catalog/` directory.

3. Download the `client_secrets.json` from Google developer console, and put it
   in `catalog` subfolder.

4. Use postgres (psql) to remove `cocktailsdb` if already existed.
   Setup the database `cocktailsdb`. See `database_setup.py` for the schema.

5. Launch the web server
   `python app.py`