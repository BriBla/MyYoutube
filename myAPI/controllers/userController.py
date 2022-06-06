import flask
from requests.api import patch
import sqlalchemy
import re
import json
import sys
import datetime
import hashlib
import jwt
import os
import requests
from flask import Flask, render_template, jsonify, Response
from flask import request as flask_request
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.datastructures import FileStorage
from models.userModels import User, Token, Video, Comment, VideoFormat
from models.pathsUtils import PathsUtils
from functools import wraps
from math import ceil, e

from __main__ import app, engine, session, ENCODER_URL

app.config['SECRET_KEY']='WeTriedSoHard'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

VALID_FORMATS = [144, 240, 360, 480, 720, 1080]

# decorator for JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        headers = flask_request.headers
        bearer = headers.get('Authorization')

        # return 401 not token
        if not bearer:
            return jsonify({'message' : 'Unauthorized'}), 401
        split_bearer = bearer.split()
        if len(split_bearer) < 2:
            return jsonify({'message' : 'Unauthorized'}), 401
        token = split_bearer[1]

        try:
            #decoding JWT
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            user_token = session.query(User).filter_by(id=data['user_id']).first()

        except:
            return jsonify({
                'message' : 'Unauthorized'
            }), 401
        if not user_token:
            #should not happen but still
            return jsonify({
                'message' : 'Unauthorized'
            }), 401
        if not user_token:
            #should not happen but still
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        #returns the current logged in users contex to the routes
        return  f(user_token, *args, **kwargs)

    return decorated

@app.route('/user', methods = ['POST'])
def create_user():
    password=flask_request.form.get("password")
    email=flask_request.form.get("email")
    username=flask_request.form.get("username")
    pseudo=flask_request.form.get("pseudo")
    if not password or not username or not email:
        return jsonify({"Message": "Invalid infos"}), 400
    passwordHashed = hashlib.sha1(password.encode('utf-8')).hexdigest()
    user = User(username=username,
        pseudo=pseudo,
        email=email,
        password=passwordHashed
    )
    errors = user.validateAttributes
    if errors:
        return jsonify({"Message": "Bad Request", "code": 10001, "data": errors}), 400
    try:
        session.add(user)
        session.commit()
    except Exception as e:
        print(e)
        return jsonify({"Message": "Bad Request", "code": 10001, "data": e.__str__()}), 400
    usernameCurrent = flask_request.form.get("username"),
    return_dict = {}
    return_dict["message"] = "OK"
    return_dict["user"] = user.serialize
    return jsonify(return_dict), 201

@app.route('/users', methods = ['GET'])
def userList():
    per_page = flask_request.form.get("perPage", 1, type=int)
    page = flask_request.form.get("page", 1, type=int)
    if page <= 0:
        page = 1
        #return jsonify({"Message": "Bad Parameters"}), 400
    if per_page <= 0:
        per_page = 1
    try:
        users = session.query(User).limit(per_page).offset((page -1) * per_page).all()
    except:
        return jsonify({"Message": "No users in Database"}), 200
    return_dict = {}
    return_dict["message"] = "OK"
    return_dict["data"] = [i.serialize for i in users]

    userCount = ceil(session.query(User).count() / per_page)
    if page > userCount:
        return {"message": "Bien tenté mon ami !"}, 404

    return_dict["pager"] = {"current": page, "total": userCount}
    return jsonify(return_dict), 200

@app.route('/auth', methods = ['POST'])
def makeToken():
    login = flask_request.form.get("login")
    password = flask_request.form.get("password")
    if password:
        passwordHashed = hashlib.sha1(password.encode('utf-8')).hexdigest()
    else:
        passwordHashed = ""
    user: User = None
    user = session.query(User).filter_by(username=login).first()
    if not user:
        user = session.query(User).filter_by(email=login).first()
    if not user:
        return jsonify({"Message": "Unauthorized"}), 401
    if (passwordHashed == user.password):
        expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        token = jwt.encode({'user_id': user.id, "exp": expiration}, app.config['SECRET_KEY'], algorithm="HS256")
        addToken = Token(code=token, expired_at=expiration, user_id=user.id)
        session.add(addToken)
        session.commit()

        return jsonify({
            "message": "OK",
            "data": {
                "token" : addToken.serialize,
            }
        }), 201
    else:
        error401 = {"Message": "Unauthorized"}
        return error401, 401

#Deleting a user
@app.route("/user/<id>", methods = ['DELETE'])
@token_required
def userDelete (user_token, id):
    if int(user_token.id) == int(id):
        user = session.query(User).filter_by(id = id).first()
        if user is not None:
            videos = session.query(Video).filter_by(user_id = id).all()
            for video in videos:
                #keep it that way to delete locally too
                os.remove(video.source)
            session.delete(user)
            session.commit()
            return '', 204
        else:
            return_dict = {}
            return_dict["message"] = "User not found"
            return jsonify(return_dict), 400 #this should never be reached
    else:
        return jsonify({"Message": "Forbidden"}), 403


#Show one user
@app.route("/user/<id>", methods = ['GET'])
@token_required
def userShow (user_token: User, id):
    user: User = session.query(User).filter_by(id = id).first()

    if not user:
        #should not be reached
        return ({"Message": "User does not exist"}), 400

    return_dict = {}
    return_dict["message"] = "OK"
    if user_token.id == int(id):
        return_dict["user"] = user.serializeAuth
    else:
        return_dict["user"] = user.serialize
    return jsonify(return_dict), 200

#Updating a user
@app.route('/user/<id>', methods=["PUT"])
@token_required
def userUpdate(user_token, id):
    if int(user_token.id) == int(id):
        user: User = session.query(User).filter_by(id = id).first()
        username = flask_request.form.get('username', '')
        pseudo = flask_request.form.get('pseudo', '')
        email = flask_request.form.get('email', '')
        password = flask_request.form.get('password', '')
        passwordHashed = hashlib.sha1(password.encode('utf-8')).hexdigest()

        if username:
            regex = re.compile("^[a-zA-Z0-9_-]+$")
            if not (re.fullmatch(regex, username)):
                return jsonify({"Message": "Invalid email format"}), 400
            user.username = username
        if pseudo:
            user.pseudo = pseudo
        if email:
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if not (re.fullmatch(regex, email)):
                return jsonify({"Message": "Invalid email format"}), 400
            user.email = email
        if password:
            user.password = passwordHashed

        return_dict = {}
        return_dict["message"] = "OK"
        return_dict["user"] = user.serialize

        session.commit()

        return jsonify(return_dict), 200
    else:
        return jsonify({"Message": "Forbidden"}), 403


#I know it shouldn't be here but whatever

def redoVidName(name: str, user_id: int):
    ext_id = name.rfind('.')
    if ext_id > 0:
        new_name = name[0:ext_id] + str(int(datetime.datetime.now().timestamp())) + "_" + str(user_id) + name[ext_id:]
    else:
        new_name = name + str(int(datetime.now().timestamp())) + "_" + str(user_id)
    return new_name

@app.route('/user/<id>/video', methods=['POST']) 
@token_required
def videoCreate(user_token: User, id):
    if int(id) != user_token.id:
        return jsonify({"Message": "Forbidden"}), 403
    print(flask_request.files)
    request_vidname = flask_request.form.get("name")
    video: FileStorage = None
    try:
        video = flask_request.files["source"]
    except:
        return jsonify({"Message": "Bad Request", "code": 10001, "data": {"source": "No Source"}}), 401
    
    if video:
        PathsUtils.checkArbo()
        #save_path = sys.argv[0]
        #save_path = os.path.join(save_path[0:len(save_path) - len("api.py")], "public")
        dbVideo: Video = None
        #if not os.path.exists(save_path):
        #    os.mkdir(save_path)
        if not request_vidname:
            vid_name: str = video.filename
        else:
            vid_name = request_vidname
        source_vidname = video.filename
        source_vidname.replace("/", "")
        #already_exists: Video = None
        #already_exists = session.query(Video).filter_by(name=vid_name).first()
        #if this gets past exception handling = name exists
        #full_path = os.path.join(save_path, source_vidname)
        full_path = os.path.join(PathsUtils.getSourcesPath(), source_vidname)
        while os.path.exists(full_path):
            source_vidname = redoVidName(source_vidname, user_token.id)
            full_path = os.path.join(PathsUtils.getSourcesPath(), source_vidname)
        #split_path = str(full_path).split('/')
        dbVideo = Video(
            name=vid_name,
            duration=0,
            source=full_path,
            view=0,
            enabled=1,
            source_resolution=0,
            user_id=id
        )
        try:
            session.add(dbVideo)
            session.commit()
            video.save(full_path)
        except Exception as e:
            print(e)
            return jsonify({"Message": "Bad Request", "code": 10001, "data": e.__str__()}), 401
        return jsonify({"Message": "OK", "video": dbVideo.serializeAuth, "mail": user_token.email}), 201

    #if not video:
    #    return jsonify({"Message": "No video"}), 401
    pass

@app.route('/videos', methods = ['GET'])
def videoList():
    per_page = flask_request.form.get("perPage", 5, type=int)
    page = flask_request.form.get("page", 1, type=int)
    if page <= 0:
        page = 1
    if per_page <= 0:
        per_page = 1
    videoCount = ceil(session.query(Video).count())
    if not videoCount:
        return jsonify({"Message": "No videos in Database"}), 200
    total = ceil(videoCount / per_page)
    if page * per_page > videoCount + per_page:
        #return {"message": "Bien tenté mon ami !"}, 404
        page = total
    try:
        videos = session.query(Video).limit(per_page).offset((page -1) * per_page).all()
    except:
        return jsonify({"Message": "No videos in Database"}), 200
    return_dict = {}
    return_dict["message"] = "OK"
    return_dict["data"] = [i.serialize for i in videos]
    #if total % 1:
    #    total = int(total) + 1
    #else:
    #    total = int(total)
    return_dict["pager"] = {"current": page, "total": total}
    return jsonify(return_dict), 200

@app.route('/user/<id>/videos', methods=['GET'])
def videosByUser(id):
    per_page = flask_request.form.get("perPage", 1, type=int)
    page = flask_request.form.get("page", 1, type=int)
    if page <= 0:
        page = 1
    if per_page <= 0:
        per_page = 1
    videoCount = ceil(session.query(Video).filter_by(user_id=id).count())
    if not videoCount:
        return jsonify({"Message": "No corresponding videos in Database"}), 201
    total = ceil(videoCount / per_page)
    if page * per_page >= videoCount + per_page:
        #return {"message": "Bien tenté mon ami !"}, 404
        page = total
    try:
        videos = session.query(Video).filter_by(user_id=id).limit(per_page).offset((page -1) * per_page).all()
    except:
        return jsonify({"Message": "No corresponding videos in Database"}), 201
    return_dict = {}
    return_dict["message"] = "OK"
    return_dict["data"] = [i.serialize for i in videos]
    if not return_dict["data"]:
        return jsonify({"Message": "No corresponding videos in Database"}), 201
    return_dict["pager"] = {"current": page, "total": total}
    return jsonify(return_dict), 201

@app.route('/video/<id>', methods=['PUT'])
@token_required
def videoUpdate(user_token, id):
    video: Video = session.query(Video).filter_by(id=id).first()
    if not video:
        return jsonify({"Message": "Video not found"}), 401
    if video.user_id != user_token.id:
        return jsonify({"Message": "Forbidden"}), 403
    name = flask_request.form.get("name")
    new_user_id = flask_request.form.get("user", 0, type=int)
    if not name and not new_user_id:
        return jsonify({"Message": "No changes"}), 200
    if name:
        video.name = name
    if new_user_id:
        video.user_id = new_user_id
    session.commit()
    return_dict = {}
    return_dict["message"] = "OK"
    return_dict["video"] = video.serialize

    return jsonify(return_dict), 200

@app.route('/video/<id>', methods=['DELETE'])
@token_required
def videoDelete(user_token, id):
    video: Video = session.query(Video).filter_by(id=id).first()
    if not video:
        return jsonify({"Message": "Video not found"}), 401
    if video.user_id != user_token.id:
        return jsonify({"Message": "Forbidden"}), 403
    session.commit() # Essential because session isolation level prevents updating video formats column (committed by another api)
    for v_f in video.formats:
        v_f: VideoFormat
        try:
            print(v_f.source)
            os.remove(v_f.source)
        except (NotImplementedError, FileNotFoundError):
            print("FAILED")
            pass
    try:
        os.remove(video.source)
    except (NotImplementedError, FileNotFoundError):
        pass
    session.delete(video)
    session.commit()
    return '', 204

@app.route('/video/<id>', methods=['PATCH'])
@token_required
def videoEncode(user_token: User, id):
    global ENCODER_URL
    video = session.query(Video).filter_by(id=id).first()
    if not video:
        return jsonify({"Message": "Not found"}), 400
    requested_format = flask_request.form.get("format")
    print(user_token.email)
    payload = {"format": requested_format, "mail": user_token.email}
    req = requests.post(f'{ENCODER_URL}encode_all/{id}', data=payload)
    return req.json(), req.status_code

@app.route('/video/<id>/comment', methods=['POST'])
@token_required
def commentCreate(user_token, id):
    video: Video = session.query(Video).filter_by(id=id).first()
    if not video:
        return jsonify({"Message": "Video not found"}), 401
    body = flask_request.form.get("body")
    if not body:
        return jsonify({"Message": "Bad Request", "code": 10001, "data": {"body": "No body"}}), 400
    comment = Comment(
        body=body,
        user_id=user_token.id,
        video_id=video.id
    )
    try:
        session.add(comment)
        session.commit()
    except Exception as e:
        return jsonify({"Message": "Bad Request", "code": 10001, "data": e.__str__()}), 400
    return ({
        "Message": "OK",
        "data": comment.serialize,
    }), 201

@app.route('/video_path/<id>', methods=['GET'])
def videoRead(id):
    session.commit()
    global VALID_FORMATS
    id = int(id)
    format = flask_request.form.get("format", type=int)
    if id <= 0 or format not in VALID_FORMATS:
        return jsonify({"Message": "Bad request"}), 400
    video_f: VideoFormat = session.query(VideoFormat).filter_by(video_id=id).filter_by(resolution=format).first()
    if not video_f:
        return jsonify({"Message": "Not found"}), 404
    return jsonify({"Message": "OK", "source": video_f.source}), 200
    

@app.route('/video/<id>/comments', methods = ['GET'])
@token_required
def commentList(user_token, id):
    per_page = flask_request.form.get("perPage", 1, type=int)
    page = flask_request.form.get("page", 1, type=int)
    if page <= 0:
        page = 1
    if per_page <= 0:
        per_page = 1
    commentCount = ceil(session.query(Comment).filter_by(video_id=id).count())
    if not commentCount:
        return jsonify({"Message": "OK", "data": []}), 201
    total = ceil(commentCount / per_page)
    if page * per_page > commentCount + per_page:
        return {"message": "Not found"}, 404
    try:
        comments = session.query(Comment).filter_by(video_id=id).limit(per_page).offset((page -1) * per_page).all()
    except:
        return jsonify({"Message": "OK", "data": []}), 201
    return_dict = {}
    return_dict["message"] = "OK"
    return_dict["data"] = []
    for comment in comments:
        if comment.user_id == user_token.id:
            return_dict["data"].append(comment.serializeAuth)
        else:
            return_dict["data"].append(comment.serialize)
    return_dict["pager"] = {"current": page, "total": total}
    return jsonify(return_dict), 201
