from flask import Flask, Response, request, redirect, url_for
from flask_cors import CORS
import json
import logging
import re

from application_services.UsersResource.user_addr_service import UserAddrResource
from application_services.UsersResource.user_service import UserResource

# from flask_dance.contrib.google import make_google_blueprint, google
# import middleware.simple_security as simple_security
from middleware.notification import NotificationMiddlewareHandler as NotificationMiddlewareHandler

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# pagination data
OFFSET = 0
MAXLIMIT = 20

app = Flask(__name__)
CORS(app)

# oauth
# app.secret_key = "supersekrit"
# blueprint = make_google_blueprint(
#     client_id="my-key-here",
#     client_secret="my-secret-here",
#     scope=["profile", "email"]
# )
# app.register_blueprint(blueprint, url_prefix="/login")

g_bp = app.blueprints.get("google")

# help function for pagination
def handle_links(url, offset, limit):
    if "?" not in url:
        url += "?offset=" + str(offset) + "&limit=" + str(limit)
    else:
        if "offset" not in url:
            url = url + "&offset=" + str(offset)
        if "limit" not in url:
            url = url + "&limit=" + str(limit)
    links = []
    nexturl = re.sub("offset=\d+", "offset=" + str(offset + limit), url)
    prevurl = re.sub("offset=\d+", "offset=" + str(max(0, offset - limit)), url)
    links.append({"rel": "self", "href": url})
    links.append({"rel": "next", "href": nexturl})
    links.append({"rel": "prev", "href": prevurl})
    return links


@app.route('/')
def hello_world():
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
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        data = UserResource.find_by_template(None, limit, offset)
        links = handle_links(request.url, offset, limit)
        res ={"data":data,"links":links}
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
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        data = UserAddrResource.find_by_template(None, limit, offset)
        links = handle_links(request.url, offset, limit)
        res ={"data":data,"links":links}
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


@app.route('/users/<userid>/address', methods=['GET'])
def get_address_from_userid(userid):
    if request.method == 'GET':
        template = {"id": userid}
        res = UserAddrResource.find_linked_data("id", template)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp


@app.route('/address/<addressid>/users', methods=['GET'])
def get_user_from_addressid(addressid):
    if request.method == 'GET':
        template = {"id": addressid}
        res = UserResource.find_linked_data("addressID", template)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp

# @app.before_request
# def before_request_func():
#     print("before_request is running")
#     result_ok = simple_security.check_security(request, google, g_bp)
#
#     if not result_ok:
#         return redirect(url_for("google.login"))


@app.after_request
def after_request_func(response):
    NotificationMiddlewareHandler.notify(request, response)
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
