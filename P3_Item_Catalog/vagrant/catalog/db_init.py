import os
import urlparse
from database_setup import Base, Category, Cocktails, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError



urlparse.uses_netloc.append("postgres")
# Gets DB variable from Heroku. If no DBURL is present, uses local appreview.db
dburl = urlparse.urlparse(os.getenv("DATABASE_URL", "/cocktailsdb"))
engine = create_engine('postgresql+psycopg2://%s/%s' % (dburl.netloc, dburl.path[1:]))

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = User(id=1,name='Arvin', email='arvin.dwarka@gmail.com')
session.add(user1)
session.commit()

cat1 = Category(id=1,name='Boozy', creator_id=1)
session.add(cat1)
session.commit()

ct1 = Cocktails(name='Navy Rations', description='XO Rum, Punt e Mes, House Cherry Brandy, Absinthe', price='13', category_id=1, creator_id=1)
session.add(ct1)
session.commit()

print 'done!'