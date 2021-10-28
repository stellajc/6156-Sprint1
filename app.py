from flask import Flask, Response, request
from flask_cors import CORS
import json
import logging

from application_services.UsersResource.user_addr_service import UserAddrResource
from application_services.UsersResource.user_service import UserResource

from database_services.RDBService import RDBService as RDBService

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)


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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
