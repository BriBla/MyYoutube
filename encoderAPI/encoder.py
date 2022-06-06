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
CORS(app)

engine = sqlalchemy.create_engine("mysql+pymysql://root:Alex0143@127.0.0.1:3306/mydb")
app.config['SECRET_KEY']='NOinia2926az6aze646ac16a1z1a6161'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

Base = declarative_base()
Base.metadata.create_all(engine)

Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()

import controller.controller
import controller.errorHandler


if __name__ == "__main__":
    app.run(debug=True, port=5001)