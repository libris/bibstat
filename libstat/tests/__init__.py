# -*- coding: UTF-8 -*-
from django.test.utils import setup_test_environment
from django.test.runner import DiscoverRunner
from with_asserts.case import TestCase
from django.conf import settings


class MongoEngineTestRunner(DiscoverRunner):
    def setup_databases(self):
        pass

    def teardown_databases(self, *args):
        pass


class MongoTestCase(TestCase):
    mongodb_name = 'test_%s' % settings.MONGODB_NAME

    def _fixture_setup(self):
        from mongoengine.connection import connect, disconnect

        disconnect()
        connect(self.mongodb_name)
        from mongoengine.django.mongo_auth.models import MongoUser

        MongoUser.objects.create_superuser("admin", "admin@example.com", "admin")
        MongoUser.objects.create_user("library_user", "library.user@example.com", "secret")
        setup_test_environment()

    def _post_teardown(self):
        from mongoengine.connection import get_connection, disconnect

        connection = get_connection()
        connection.drop_database(self.mongodb_name)
        disconnect()
