import os
import pymysql

basedir = os.path.abspath(os.path.dirname(__file__))

# JawsDB
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret_key here'
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="iejlrzf8pfra4pxv",
        password="fzoe3kb3efmrmvdi",
        hostname="dcrhg4kh56j13bnu.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
        databasename="zrca5i7g64otwrn2",
    )
    SQLALCHEMY_POOL_RECYCLE = 58 # seconds
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # auto reload when save changes on templates
    TEMPLATES_AUTO_RELOAD = True    # remove this when deploy
    
    # Email config
    MAIL_SERVER='smtp.domain.com'
    MAIL_PORT=465
    MAIL_USE_SSL=True
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''