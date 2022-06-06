import fabric
from flask import Flask, render_template, jsonify, Response
from flask import request
from flask_cors import CORS

client = fabric.Connection(
    "MyYoutube@172.16.109.128", 
    port=22, 
    connect_kwargs={'password': 'Alex0143'}
    )
name = client.run("echo SSH connection on")

from flask import Flask

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

@app.route("/ssh")
def ssh():
    result = {}
    result["Message"] = name.stdout
    return result, 200

@app.route('/mail', methods = ['POST'])
def mail():
    mailer = ""
    email = request.form.get("email")
    emailType = request.form.get("email type")
    if not email:
        result = {"Message": "No email"}
        return result, 404
    if not emailType:
        result = {"Message": "No email type"}
        return 404
    if emailType == '1':
        mailer = "mail -r 'noreply@myyoutube.com' -a 'Content-type: text/html' -s 'Changement de MdP' " + email + " < /home/brice/Documents/mailer/password.html"
        client.run(mailer, hide=False)
    if emailType == '2':
        mailer = "mail -r 'noreply@myyoutube.com' -a 'Content-type: text/html' -s 'Encodage en cours' " + email + " < /home/brice/Documents/mailer/encode.html"
        client.run(mailer, hide=False)
    

    result = {"Message": "Email send"}
    return result, 200

if __name__ == "__main__":
    app.run(debug=True, port=5002)