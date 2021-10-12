from flask import Flask, Response
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
@app.route('/users')
def get_users():
    res = UserResource.find_by_template(None)
    rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    return rsp

# /users/<userid> GET
@app.route('/users/<userid>')
def get_user_by_id(userid):
    template = {"id":userid}
    res = UserResource.find_by_template(template)
    rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    return rsp

@app.route('/addresses')
def get_addresses():
    res = UserAddrResource.find_by_template(None)
    rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    return rsp


# @app.route('/<db_schema>/<table_name>/<column_name>/<prefix>')
# def get_by_prefix(db_schema, table_name, column_name, prefix):
#     res = RDBService.get_by_prefix(db_schema, table_name, column_name, prefix)
#     rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
#     return rsp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
