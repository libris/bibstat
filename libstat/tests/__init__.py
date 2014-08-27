# -*- coding: UTF-8 -*-
from django.test.runner import DiscoverRunner
from django.test import TestCase
from django.conf import settings

class MongoEngineTestRunner(DiscoverRunner):
    """
        Test runner for use with MongoEngine
    """
    def setup_databases(self):
        pass
        
    def teardown_databases(self, *args):
        pass
 
class MongoTestCase(TestCase):
    """
        Test case for use with MongoEngine
    """
    mongodb_name = 'test_%s' % settings.MONGODB_NAME
    
    def _fixture_setup(self):
        from mongoengine.connection import connect, disconnect
        disconnect()
        connect(self.mongodb_name)
        from mongoengine.django.mongo_auth.models import MongoUser
        MongoUser.objects.create_superuser("admin", "admin@example.com", "admin")
        MongoUser.objects.create_user("library_user", "library.user@example.com", "secret")
        
#     def _fixture_teardown(self):
#         pass
    
    def _post_teardown(self):
        from mongoengine.connection import get_connection, disconnect
        connection = get_connection()
        connection.drop_database(self.mongodb_name)
        disconnect()
