from flask import Flask, Response, request, redirect, url_for
from flask_cors import CORS
import json
import logging
import os
from flask_dance.contrib.google import make_google_blueprint, google
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError


from application_services.UsersResource.user_addr_service import UserAddrResource
from application_services.UsersResource.user_service import UserResource

from database_services.RDBService import RDBService as RDBService

import middleware.security as security

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

app.secret_key = "some secret"
client_id = "79382664809-0a3bcn4hokdmgr9tcapsriguql3lfnnm.apps.googleusercontent.com"
client_secret = "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"

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

blueprint = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    reprompt_consent=True,
    scope=["profile", "email"]
)
app.register_blueprint(blueprint, url_prefix="/login", offline=True)


@app.before_request
def before_request_func():
    try:
        result_ok = security.check_security(request, google)
        if (not result_ok) and request.endpoint != 'google.login':
            return redirect(url_for('google.login'))
    except TokenExpiredError:
        del blueprint.token
        return redirect(url_for('google.login'))


@app.route('/')
def hello_world():
    # if not google.authorized:
    #     return redirect(url_for("google.login"))
    # resp = google.get("/oauth2/v1/userinfo")
    # assert resp.ok, resp.text
    # print(resp.json())
    # return "You are {email} on Google".format(email=resp.json()["email"])
    return '<u>Hello World!</u>'


# @app.route('/imdb/artists/<prefix>')
# def get_artists_by_prefix(prefix):
#     res = IMDBArtistResource.get_by_name_prefix(prefix)
#     rsp = Response(json.dumps(res), status=200, content_type="application/json")
#     return rsp

# /users GET
@app.route('/users', methods=['GET', 'POST'])
def get_users():
    if request.method == 'GET':
        res = UserResource.find_by_template(None)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp
    elif request.method == 'POST':
        id = request.form['id']
        name_last = request.form['name_last']
        name_first = request.form['name_first']
        email = request.form['email']
        address_id = request.form['address_id']
        create_data = {"id": id, "nameLast": name_last, "nameFirst": name_first, "email": email, "addressID": address_id}
        res = UserResource.create(create_data)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp


# /users/<userid> 
"""these methods could be separated into three functions.
   for future use, we need to check form input from user (whether each var is null, selected attributes input)
"""
@app.route('/users/<userid>', methods=['GET', 'PUT', 'DELETE'])
def get_user_by_id(userid):
    if request.method == 'GET':
        template = {"id":userid}
        res = UserResource.find_by_template(template)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp
    elif request.method == 'PUT':
        name_last = request.form['name_last']
        name_first = request.form['name_first']
        email = request.form['email']
        address_id = request.form['address_id']
        select_data = {"id": userid}
        update_data = {"nameLast": name_last, "nameFirst": name_first, "email": email, "addressID": address_id}
        res = UserResource.update(select_data, update_data)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp
    elif request.method == 'DELETE':
        template = {"id": userid}
        res = UserResource.delete(template)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp


@app.route('/addresses', methods=['GET', 'POST'])
def get_addresses():
    if request.method == 'GET':
        res = UserAddrResource.find_by_template(None)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp
    elif request.method == 'POST':
        id = request.form['id']
        street_no = request.form['street_no']
        street_name1 = request.form['street_name1']
        street_name2 = request.form['street_name2']
        city = request.form['city']
        region = request.form['region']
        country_code = request.form['country_code']
        postal_code = request.form['postal_code']
        create_data = {"id": id, "streetNo": street_no, "streetName1": street_name1, "streetName2": street_name2,
                       "city": city, "region": region, "countryCode": country_code, "postalCode": postal_code}
        res = UserAddrResource.create(create_data)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
