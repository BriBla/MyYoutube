from flask import jsonify

from __main__ import app

@app.errorhandler(404)
def invalid_url(e):
    return jsonify({"Message": "Not Found"}), 404

@app.errorhandler(405)
def invalid_method(e):
    return jsonify({"Message": "Unauthorized method for requested url"}), 405
