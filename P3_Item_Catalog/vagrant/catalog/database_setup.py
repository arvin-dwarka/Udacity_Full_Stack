import os
import urlparse
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    """
    User class to capture all necessary user info.
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    """
    Category class that is related to User and Cocktails table.
    """
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    cocktails = relationship('Cocktails', cascade="all, delete-orphan")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name
        }


class Cocktails(Base):
    """
    Cocktails class that contains all the details on a drink:
    - ID
    - Name  
    - Description 
    - Price
    - Category
    - User
    """
    __tablename__ = 'cocktails'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    price = Column(String(8))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """
        Return object data in serializeable format
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price
        }

urlparse.uses_netloc.append("postgres")
# Gets DB variable from Heroku. If no DBURL is present, uses local database
dburl = urlparse.urlparse(os.getenv("DATABASE_URL", "/cocktailsdb"))
engine = create_engine('postgresql+psycopg2://%s/%s' % 
    (dburl.netloc, dburl.path[1:]))

Base.metadata.create_all(engine)