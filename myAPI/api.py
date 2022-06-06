#! /bin/python3.7

import sqlalchemy
import re
import json
import sys
import datetime
import hashlib
import jwt
import requests
from flask import Flask, render_template, jsonify, Response
from flask import request as flask_request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

engine = sqlalchemy.create_engine("mysql+pymysql://root:Alex0143@127.0.0.1:3306/mydb")
app.config['SECRET_KEY']='WeTriedSoHard'
app.config['CORS_HEADERS'] = 'Content-Type'

Base = declarative_base()
Base.metadata.create_all(engine)

Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()

ENCODER_URL = "http://127.0.0.1:5001/"

import controllers.userController
import controllers.errorHandler
from models.pathsUtils import PathsUtils

if __name__ == "__main__":
    PathsUtils.checkArbo()
    app.run(debug=True, port=5000)
