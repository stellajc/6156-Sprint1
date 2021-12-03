import time
from flask import Flask, Response, request, redirect, url_for, session
from flask_cors import CORS
import json
import logging
import os
from flask_dance.contrib.google import make_google_blueprint, google
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
import re

from application_services.UsersResource.user_addr_service import UserAddrResource
from application_services.UsersResource.user_service import UserResource
from application_services.AppHTTPStatus import AppHTTPStatus
# from application_services.smarty_address_service import SmartyAddressService
from database_services.RDBService import RDBService as RDBService

# from flask_dance.contrib.google import make_google_blueprint, google
# import middleware.simple_security as simple_security
from middleware.notification import NotificationMiddlewareHandler as NotificationMiddlewareHandler
from middleware.steamsignin import SteamSignIn

import middleware.security as security

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# pagination data
OFFSET = 0
MAXLIMIT = 2 #20

app = Flask(__name__)
CORS(app)
app.secret_key = "supersekrit"
os.environ['steawmpowered_key'] = 'BBC837ECFD8415A58B7575D83BCDA639'
@app.errorhandler(404)
def not_found(e):
    rsp = Response(response=json.dumps({"ERROR": "404 NOT FOUND"}, default=str, indent=4), status=404,
                   content_type="application/json")
    return rsp


@app.errorhandler(500)
def messy_error(e):
    print(e)
    rsp = Response(json.dumps({"ERROR": "500 WEIRD SERVER ERROR"}, default=str, indent=4), status=500,
                   content_type="application/json")
    return rsp

##### new line below
# app.secret_key = "some secret"
client_id = "650452278368-092i2s8rtp2n6kmcpr7m3ngt3afmb40k.apps.googleusercontent.com"
client_secret = "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"

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

blueprint = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    reprompt_consent=True,
    scope=["profile", "email"]
    # redirect_url="http://127.0.0.1:3000/"
)
app.register_blueprint(blueprint, url_prefix="/login", offline=True)
##### new line above

# @app.before_request
# def before_request_func():
#     try:
#         result_ok = security.check_security(request, google)
#         if (not result_ok) and request.endpoint != 'google.login':
#             return redirect(url_for('google.login'))
#     except TokenExpiredError:
#         del blueprint.token
#         return redirect(url_for('google.login'))

# oauth
# app.secret_key = "supersekrit"
# blueprint = make_google_blueprint(
#     client_id="my-key-here",
#     client_secret="my-secret-here",
#     scope=["profile", "email"]
# )
# app.register_blueprint(blueprint, url_prefix="/login")

# g_bp = app.blueprints.get("google")

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
@app.route('/users', methods=['GET', 'POST','OPTIONS'])
def get_users():
    if request.method == 'GET':
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        query_parms = dict()
        arg_list = [i for i in request.args.keys()]
        for i in arg_list:
            if i.lower() != "offset" and i.lower() != "limit":
                query_parms[i] = request.args.get(i)
        data, exception_res = UserResource.find_by_template(query_parms, limit, offset)
        links = handle_links(request.url, offset, limit)
        if data is not None:
            # res = {"data": data, "links": links}
            res = data
        else:
            res = data
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        # # >>>>>>>> new line below >>>>
        # data = UserResource.find_by_template(None, limit, offset)
        # links = handle_links(request.url, offset, limit)
        # res ={"data":data,"links":links}
        # rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        # # <<<<<<<< new line above <<<<
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
    else:
        res = Response()
        res.headers['Access-Control-Allow-Origin'] = '*'
        return res


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

@app.route('/user/register', methods=['POST'])
def register_new_user():
    # only json files allowed in the body
    create_data = json.loads(request.data.decode(encoding='utf-8'))
    if not create_data.get("accessToken", None):
        # TODO: prevent unauthorized users needed to be implemented on frontend
        return Response(json.dumps({"ERROR": "USER NOT AUTHORIZED"}, default=str, indent=4),
                        status=AppHTTPStatus.post_create, content_type='application/json')
    create_data = {
        'nameLast': create_data['family_name'].strip(),
        'nameFirst': create_data['given_name'].strip(),
        'email': create_data['email'].strip(),
        'googleID': create_data['sub'].strip(),
        'accessToken': create_data['accessToken'].strip()
    }
    localID, _ = UserResource.find_by_template({'email': create_data['email']}, field_list=['ID'])
    if localID:  # existing user update token
        tokenres, token_exc = UserResource.update({'ID': localID}, {'accessToken': create_data['accessToken']})
        rsp = AppHTTPStatus().format_rsp(localID, None, method='GET', path=request.path)
    else:
        res, exception_res = UserResource.create(create_data)
        localID, _ = UserResource.find_by_template({'email': create_data['email']}, field_list=['ID'])
        rsp = AppHTTPStatus().format_rsp(localID, exception_res, method='GET', path=request.path)
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
            if i.lower() != "offset" and i.lower() != "limit":
                query_parms[i] = request.args.get(i)
        data, exception_res = UserAddrResource.find_by_template(query_parms, limit, offset)
        links = handle_links(request.url, offset, limit)
        if data is not None:
            res = {"data": data, "links": links}
        else:
            res = data
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        # # <<<<<< new line below
        # data = UserAddrResource.find_by_template(None, limit, offset)
        # links = handle_links(request.url, offset, limit)
        # res ={"data":data,"links":links}
        # rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        # # >>>>> new line above >>>>
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


@app.route('/steampowered/status')
def steam_status():
    if session.get('steam_userid', None):
        print("cookie")
        print(request.cookies.get("steam_userid", None))
        return "SteamID is: {0}".format(session['steam_userid'])
        # return
    else:
        # TODO: two buttons, one for retry, one for redirect to '/'
        steamlogin = SteamSignIn()
        return steamlogin.RedirectUser(steamlogin.ConstructURL(request.url_root + url_for('steam_login')))


@app.route('/steampowered/login')
def steam_login():
    returnData = request.values
    steamlogin = SteamSignIn()
    steamID = steamlogin.ValidateResults(returnData)
    if steamID:
        session['steam_userid'] = steamID
        print('SteamID is: {0}'.format(steamID))
    # else:
    return redirect(url_for('steam_status'))


@app.route('/steampowered/logout')
def steam_logout():
    session.pop('steam_userid', None)
    return redirect(url_for('/'))

# auth to fetch game list of the specific user
@app.route('/steampowered/auth')
def steam_auth():
    user = session.get('steam_userid', None)
    if user:
        steam_key = os.getenv('steampowered_key')
        steamapi_base_url = 'https://api.steampowered.com/'




# @app.before_request
# def before_request_func():
#     print("before_request is running")
#     result_ok = simple_security.check_security(request, google, g_bp)
#
#     if not result_ok:
#         return redirect(url_for("google.login"))


# @app.after_request
# def after_request_func(response):
#     NotificationMiddlewareHandler.notify(request, response)
#     return response


if __name__ == '__main__':
    app.run()
