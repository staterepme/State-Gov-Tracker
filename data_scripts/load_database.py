#!/usr/local/bin/python

from datetime import date, timedelta
from sqlalchemy import create_engine, Table, and_, func, not_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper

# Change Path to Database #
engine = create_engine('sqlite:////Users/christbr1985/Dropbox/CongressMonitor/StateGovTracker.db')

Base = declarative_base()

class official_tweets(Base):
    __table__ = Table('official_tweets', Base.metadata, autoload=True, autoload_with=engine)

class legis_news(Base):
	__table__ = Table('pa_legis_news', Base.metadata, autoload=True, autoload_with=engine)

class social_media_ids(Base):
	__table__ = Table('legs_socialmedia', Base.metadata, autoload=True, autoload_with=engine)	

class official_posts(Base):
	__table__ = Table('fb_data', Base.metadata, autoload=True, autoload_with=engine)

class official_info(Base):
	__table__ = Table('officials', Base.metadata, autoload=True, autoload_with=engine)

def loadSession():
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

session = loadSession()
