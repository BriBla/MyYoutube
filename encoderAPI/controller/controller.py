import flask
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
from models.model import Video, Format, VideoFormat
from functools import wraps
from math import ceil, e
from models.EncoderThread import EncoderThread, Scheduler
from models.Encoding_class import Encoding

import ffmpeg

from __main__ import app, engine, session


false = False
true = True

running_encodings = {}
VALID_FORMATS = [144, 240, 360, 480, 720, 1080]
dummy_thread: EncoderThread = None


def commit_encoding(source, format_id, video_id, format, encoding: Encoding):
    video_f = VideoFormat(
        source=source,
        format_id=format_id,
        video_id=video_id,
        resolution=format
    )
    try:
        session.add(video_f)
        session.commit()
        if format >= encoding.max():
            pass
            url="http://127.0.0.1:5002/mail"
            data={'email': encoding.mail, 'email type': "2"}
            requests.post(url, data)
    except Exception as e:
        print("ERROR: ", e)
        os.remove(source)

SCHEDULER = Scheduler(commit_encoding)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"Message": "OK"}), 200

@app.route('/encode/<id>', methods=['POST'])
def req_encode(id):
    global SCHEDULER, VALID_FORMATS
    session.commit()
    id = int(id)
    requested_format = flask_request.form.get("format", type=int)
    user_mail = flask_request.form.get("mail", type=str)
    if requested_format not in VALID_FORMATS or id <= 0:
        return jsonify({"Message": "Bad Request", "code": 10001, "data": {"id": "Bad parameters"}}), 401
    video: Video = session.query(Video).filter_by(id=id).first()
    format: Format = session.query(Format).filter_by(resolution=str(requested_format)).first()
    if not video or not os.path.exists(video.source) or not format:
        return jsonify({"Message": "Not Found"}), 404
    encoding = Encoding.existsOrCreate(video.source, video.id, user_mail)
    thread: EncoderThread = SCHEDULER.addTask(video.source, requested_format, video.id, format.id, encoding)
    started = False
    if thread:
        thread.start()
        started = True
    return jsonify({"Message": "OK", "video": video.serialize, "started": started}), 200

def encode(video: Video, encoding: Encoding, requested_format: int) -> bool:
    global SCHEDULER
    format = session.query(Format).filter_by(resolution=str(requested_format)).first()
    thread: EncoderThread = SCHEDULER.addTask(video.source, requested_format, video.id, format.id, encoding)
    if thread:
        thread.start()
    return not thread is None

@app.route('/encode_all/<id>', methods=['POST'])
def encode_all(id):
    session.commit()
    user_mail = flask_request.form.get("mail", type=str)
    id = int(id)
    video: Video = session.query(Video).filter_by(id=id).first()
    if not video:
        return jsonify({"Message": "Not Found"}), 404
    already_done = session.query(VideoFormat).filter_by(video_id=id).all()
    encoding: Encoding = Encoding.existsOrCreate(video.source, video.id, user_mail)
    done = [res.resolution for res in already_done]
    p_f = encoding.possibleFormats()
    to_do = [resolution for resolution in p_f if resolution not in done]
    formats = session.query(Format).all()
    print("todo", to_do)
    return_dict = {"Message": "OK", "video": video.serialize, "mail": user_mail}
    return_dict["encodings"] = {}
    for task in to_do:
        return_dict["encodings"][task] = encode(video, encoding, task)
    return jsonify(return_dict), 201


@app.route('/probe/<id>', methods=['GET'])
def probe_video(id):
    session.commit()
    global dummy_thread
    print(EncoderThread.getThreads())
    id = int(id)
    if id <= 0:
        return jsonify({"Message": "Bad Request", "code": 10001, "data": {"id": "Bad parameters"}}), 401
    video: Video = session.query(Video).filter_by(id=id).first()
    if not video:
        return jsonify({"Message": "Not Found"}), 404

    probe = ffmpeg.probe(video.source)
    video_stream = None
    for stream in probe["streams"]:
        if stream["codec_type"] == "video":
            video_stream = stream
            break
    print(video_stream)
    print(int(video_stream["width"]) / int(video_stream["height"]) * 480)
    video.source_resolution = int(video_stream["height"])
    session.commit()
    if dummy_thread:
        state = "RUNNING: " + str(dummy_thread.is_alive())
    else:
        state = "NOTHING"
    return jsonify({"Message": "OK", "thread": state}), 200

@app.route('/status/<id>', methods=['GET'])
def get_specific_status(id):
    session.commit()
    global VALID_FORMATS
    id = int(id)
    #return jsonify({"Message": "OK", "status": running_encodings}), 200
    requested_format = flask_request.form.get("format", type=int)
    started = False
    over = False
    if requested_format not in VALID_FORMATS:
        return jsonify({"Message": "Bad request"}), 400
    video = session.query(Video).filter_by(id=id).first()
    if not video:
        return jsonify({"Message": "Not found"}), 404
    encoding = Encoding.checkExists(id)
    if encoding:
        if encoding.getTarget(requested_format):
            started = True
    done = session.query(VideoFormat).filter_by(video_id=video.id).all()
    for v_f in done:
        if v_f.resolution == requested_format:
            if os.path.exists(v_f.source):
                started = True
                over = True
    return jsonify({"Message": "OK", "started": started, "over": over}), 200

@app.route('/status_all/<id>', methods=['GET'])
def get_status(id):
    global VALID_FORMATS
    session.commit()
    user_mail = flask_request.form.get("mail", type=str)
    id = int(id)
    video: Video = session.query(Video).filter_by(id=id).first()
    if not video:
        return jsonify({"Message": "Not found"}), 404
    encoding: Encoding = Encoding.existsOrCreate(video.source, video.id, user_mail)
    return_dict = {"video": video.serialize, "formats": {}}
    done = session.query(VideoFormat).filter_by(video_id=video.id).all()
    done_formats = [res.resolution for res in done if os.path.exists(res.source)]
    for format in encoding.possibleFormats():
        return_dict["formats"][format] = {}
        started = bool(False)
        over = bool(False)
        if encoding.getTarget(format):
            started = True
        if format in done_formats:
            started = True
            over = True
        return_dict["formats"][format]["started"] = started
        return_dict["formats"][format]["over"] = over
    return jsonify({"Message": "OK", "data": return_dict}), 200
