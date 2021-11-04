from flask import Flask, Response, request, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_cors import CORS
import json
import logging
import os

from application_services.UsersResource.user_addr_service import UserAddrResource
from application_services.UsersResource.user_service import UserResource
from application_services.AppHTTPStatus import AppHTTPStatus
# from application_services.smarty_address_service import SmartyAddressService
from database_services.RDBService import RDBService as RDBService

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# pagination data
OFFSET = 0
MAXLIMIT = 20

app = Flask(__name__)
CORS(app)

app.secret_key = "supersekrit"
blueprint = make_google_blueprint(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    offline=True,
    scope=["profile", "email"]
)
app.register_blueprint(blueprint, url_prefix="/login")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = '1'
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = '1'

@app.before_request
def googleoauth():
    if not google.authorized:
        return redirect(url_for("google.login"))
    try:
        resp = google.get("oauth2/v2/userinfo")
        assert resp.ok, resp.text
    except Exception as e:
        return redirect(url_for("google.login"))

@app.errorhandler(404)
def not_found(e):
    rsp = Response(response=json.dumps({"ERROR": "404 NOT FOUND"}, default=str, indent=4), status=404,
                   content_type="plain/json")
    return rsp


@app.errorhandler(500)
def messy_error(e):
    print(e)
    rsp = Response(json.dumps({"ERROR": "500 WEIRD SERVER ERROR"}, default=str, indent=4), status=500,
                   content_type="plain/json")
    return rsp


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
        query_parms = dict()
        arg_list = [i for i in request.args.keys()]
        for i in arg_list:
            if i != "offset" and i != "limit":
                query_parms[i] = request.args.get(i)
        res, exception_res = UserResource.find_by_template(query_parms, limit, offset)
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp
    elif request.method == 'POST':
        # id = request.form['id']
        # name_last = request.form['name_last']
        # name_first = request.form['name_first']
        # email = request.form['email']
        # address_id = request.form['address_id']
        # create_data = {"id": id, "nameLast": name_last, "nameFirst": name_first, "email": email, "addressID": address_id}
        create_data = request.form
        if create_data:
            pass
        else:
            create_data = request.json
        res, exception_res = UserResource.create(create_data)
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp


# /users/<userid> 
"""these methods could be separated into three functions.
   for future use, we need to check form input from user (whether each var is null, selected attributes input)
"""
@app.route('/users/<userid>', methods=['GET', 'PUT', 'DELETE'])
def get_user_by_id(userid):
    if request.method == 'GET':
        template = {"id":userid}
        res, exception_res = UserResource.find_by_template(template, 1, 0)
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp
    elif request.method == 'PUT':
        name_last = request.form['name_last']
        name_first = request.form['name_first']
        email = request.form['email']
        address_id = request.form['address_id']
        select_data = {"id": userid}
        update_data = {"nameLast": name_last, "nameFirst": name_first, "email": email, "addressID": address_id}
        res, exception_res = UserResource.update(select_data, update_data)
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp
    elif request.method == 'DELETE':
        template = {"id": userid}
        res, exception_res = UserResource.delete(template)
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp


@app.route('/addresses', methods=['GET', 'POST'])
def get_addresses():
    if request.method == 'GET':
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        query_parms = dict()
        arg_list = [i for i in request.args.keys()]
        for i in arg_list:
            if i != "offset" and i != "limit":
                query_parms[i] = request.args.get(i)
        res, exception_res = UserAddrResource.find_by_template(query_parms, limit, offset)
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp
    elif request.method == 'POST':
        # id = request.form['id']
        # street_no = request.form['street_no']
        # street_name1 = request.form['street_name1']
        # street_name2 = request.form['street_name2']
        # city = request.form['city']
        # region = request.form['region']
        # country_code = request.form['country_code']
        # postal_code = request.form['postal_code']
        # create_data = {"id": id, "streetNo": street_no, "streetName1": street_name1, "streetName2": street_name2,
        #                "city": city, "region": region, "countryCode": country_code, "postalCode": postal_code}
        create_data = request.form
        if create_data:
            pass
        else:
            create_data = request.json
        res, exception_res = UserAddrResource.create(create_data)
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp

@app.route('/users/<userid>/address', methods=['GET'])
def get_address_from_userid(userid):
    if request.method == 'GET':
        template = {"id": userid}
        res, exception_res = UserAddrResource.find_linked_data("id", template, "addressID")
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp


@app.route('/address/<addressid>/users', methods=['GET'])
def get_user_from_addressid(addressid):
    if request.method == 'GET':
        template = {"id": addressid}
        res, exception_res = UserResource.find_linked_data("addressID", template, "id")
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp

# @app.route('/verify/address', methods=['GET', 'POST'])
# def verify_smarty_address():
#     if request.method == 'GET':
#         resp = google.get("oauth2/v2/userinfo")
#         user_email = resp.json()
#         print(user_email['id'])
#         smarty_verify = SmartyAddressService()
#         smarty_res = smarty_verify.look_up()
#         print(smarty_res)
#         return Response(json.dumps({}), status=200, content_type="application/json")
#     else:
#         return Response(json.dumps({}), status=200, content_type="application/json")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
