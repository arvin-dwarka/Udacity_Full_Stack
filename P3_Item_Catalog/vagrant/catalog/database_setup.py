
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
import os
import urlparse


Base = declarative_base()


class User(Base):
    """
    User class for all users in the database.
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    """
    Category class which identifies a name and the category's creator.
    """
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    creator_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    apps = relationship('App', cascade="all, delete-orphan")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class App(Base):
    """
    The core class for our application. Contains all of the detailed information for each app item.
    Includes:
    - Name
    - ID 
    - Publisher 
    - Description 
    - Price
    - IDs for the Apple App Store, Google Play Store, and Microsoft Store, if available
    - Category
    - Creator
    """
    __tablename__ = 'app'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    publisher = Column(String(250))
    image_url = Column(String(250)) 
    playstore_id = Column(String(250))
    appstore_id = Column(String(250))
    windows_id = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    creator_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'publisher': self.publisher,
            'image': self.image_url,
            'playstore_id': self.playstore_id,
            'appstore_id': self.appstore_id,
            'windows_id': self.windows_id,
        }

urlparse.uses_netloc.append("postgres")
# Gets DB variable from Heroku. If no DBURL is present, uses local appreview.db
dburl = urlparse.urlparse(os.getenv("DATABASE_URL", "/appreviewdb"))
engine = create_engine('postgresql+psycopg2://%s/%s' % (dburl.netloc, dburl.path[1:]))

Base.metadata.create_all(engine)