from application_services.BaseApplicationResource import BaseRDBApplicationResource
import database_services.RDBService as RDBService

# data schema: UserInfo
# table_name: Users
class UserResource(BaseRDBApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_links(cls, resource_data):
        pass

    @classmethod
    def find_by_template(cls, template):
        res = RDBService.find_by_template("UserInfo", "Users", template)
        return res