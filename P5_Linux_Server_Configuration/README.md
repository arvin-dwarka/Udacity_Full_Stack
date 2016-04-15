# Linux Server Configuration

This project takes a baseline installation of a Linux distribution on a virtual machine and prepare it to host your web applications, to include installing updates, securing it from a number of attack vectors and installing/configuring web and database servers.

#### HTTP

A python web application, [Cocktails app](http://cocktails-app.herokuapp.com/) was developed using Flask and powered by a Postgres database. Along with the heroku platform, the app is also hosted via HTTP at [52.39.30.72](http://52.39.30.72/).

#### SSH

To access the server, SSH into it by executing the following command:

```
ssh -i ~/.ssh/[RSA_FILE] grader@52.39.30.72 -p2200
```

Make sure to include the proper RSA file to access the server.


#### List of softwares
- unattended-upgrades
- fail2ban
- sendmail
- apache2
- python-setuptools
- libapache2-mod-wsgi
- git
- python-dev
- python-pip
- Flask
- httplib2
- requests
- oauth2client
- sqlalchemy
- python-psycopg2
- postgresql
- dict2xml

#### Configurations made
- updated and upgraded modules
- change to port 2200
- added new user `grader` and gave sudo access
- configured Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123)
- configured to UTC timezone
- configured git user name and email
- created and configured `catalog.conf`
- created and configured `catalog.wsgi`
- cloned git repo to `/var/www/catalog/catalog/`
- created catalog database user
- created catalog database
- configured database access

#### References:
- [Udacity forum](https://discussions.udacity.com/c/nd004-p5-linux-based-server-configuration?_ga=1.257049165.796332827.1459399271)
- [Stueken Github Walkthrough](https://github.com/stueken/FSND-P5_Linux-Server-Configuration)