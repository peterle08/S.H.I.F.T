# configuration: database server, email, etc.
import os
# import pymysql

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret Key here'
    # SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    #     username="",
    #     password="",
    #     hostname=""
    #     databasename="",
    # )
    SQLALCHEMY_POOL_RECYCLE = 58

    SQLALCHEMY_TRACK_MODIFICATIONS = False