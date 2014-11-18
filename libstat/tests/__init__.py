# -*- coding: UTF-8 -*-
import random
import string
from datetime import datetime

from django.test.utils import setup_test_environment
from django.test.runner import DiscoverRunner
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse

from libstat.models import Variable, OpenData, Survey, Library


class MongoEngineTestRunner(DiscoverRunner):

    def setup_databases(self):
        pass

    def teardown_databases(self, *args):
        pass


class MongoTestCase(TestCase):
    mongodb_name = 'test_%s' % settings.MONGODB_NAME

    def _login(self):
        self.client.login(username="admin", password="admin")

    def _logout(self):
        self.client.logout()

    def _get(self, action=None, kwargs=None):
        url = reverse(action, kwargs=kwargs)
        return self.client.get(url)

    def _post(self, action=None, kwargs=None, data=None):
        url = reverse(action, kwargs=kwargs)
        return self.client.post(url, data=data)

    def _dummy_library(self, name="dummy_name", sigel=None, bibdb_id="dummy_id", city="dummy_city",
                       municipality_code="dummy_code", library_type="folkbib"):
        if not sigel:
            sigel = Library._random_sigel()
        return Library(name=name, sigel=sigel, bibdb_id=bibdb_id, city=city,
                       municipality_code=municipality_code, library_type=library_type).save()

    def _dummy_survey(self, library_name="dummy_name", sample_year=2001, password=None, target_group="folkbib",
                      status="not_viewed", publish=False, library=None,
                      observations=[], selected_libraries=[]):
        if not library:
            library = self._dummy_library()
        survey = Survey(library_name=library_name, library=library, sample_year=sample_year,
                        target_group=target_group, password=password, status=status,
                        observations=observations, selected_libraries=selected_libraries).save()
        if publish:
            survey.publish()
            survey.reload()
        return survey

    def _dummy_variable(self, key=None, description=u"dummy description", type="integer", is_public=True,
                        target_groups=["folkbib"], is_draft=False, replaced_by=None, save=True, question=None,
                        category=None, sub_category=None):
        if not key:
            key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        variable = Variable(key=key, description=description, type=type, is_public=is_public, category=category,
                            target_groups=target_groups, is_draft=is_draft, replaced_by=replaced_by, question=question,
                            sub_category=sub_category)
        if save:
            variable.save()
            variable.reload()
        return variable

    def _dummy_open_data(self, library_name=u"dummy_lib", library_id=u"123", sample_year=2013, target_group="folkbib",
                         variable=None, value=1, date_created=None, date_modified=None, save=True):
        if not variable:
            variable = self._dummy_variable()
            variable.save()
        if not date_created:
            date_created = datetime(2014, 05, 27, 8, 00, 00)
        if not date_modified:
            date_modified = datetime(2014, 06, 02, 17, 57, 16)
        open_data = OpenData(library_name=library_name, library_id=library_id, sample_year=sample_year,
                             target_group=target_group, variable=variable, value=value, date_created=date_created,
                             date_modified=date_modified)
        if save:
            open_data.save()
            open_data.reload()
        return open_data

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
