# -*- coding: UTF-8 -*-
import random
import string
import json

from datetime import datetime

from django.test.utils import setup_test_environment
from django.test.runner import DiscoverRunner
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse

from libstat.models import Variable, OpenData, Survey, Library, SurveyObservation, Article, Dispatch


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

    def _get(self, action=None, kwargs=None, params={}):
        url = reverse(action, kwargs=kwargs)
        if params:
            url += "?"
            for key, value in params.iteritems():
                url = "{}{}={}&".format(url, key, value)
        return self.client.get(url)

    def _get_json(self, action=None, kwargs=None):
        return json.loads(self._get(action, kwargs).content)

    def _post(self, action=None, kwargs=None, data=None):
        if data:
            return self.client.post(reverse(action, kwargs=kwargs), data=data)
        else:
            return self.client.post(reverse(action, kwargs=kwargs))

    def _dummy_library(self, name="dummy_name", sigel=None, bibdb_id="dummy_id", city="dummy_city",
                       municipality_code="dummy_code", library_type="folkbib"):
        if not sigel:
            sigel = Library._random_sigel()
        return Library(name=name, sigel=sigel, bibdb_id=bibdb_id, city=city,
                       municipality_code=municipality_code, library_type=library_type)

    def _dummy_variable(self, key=None, description=u"dummy description", type="integer", is_public=True,
                        target_groups=["folkbib"], is_draft=False, replaced_by=None, save=True, question=None,
                        category=None, sub_category=None, replaces=[], question_part=None):
        if not key:
            key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        variable = Variable(key=key, description=description, type=type, is_public=is_public, category=category,
                            target_groups=target_groups, is_draft=is_draft, replaced_by=replaced_by, question=question,
                            sub_category=sub_category, replaces=replaces, question_part=question_part)
        if save:
            variable.save()
            variable.reload()
        return variable

    def _dummy_observation(self, variable=None, value="dummy_value", disabled=False, value_unknown=False,
                           _is_public=True):
        if not variable:
            variable = self._dummy_variable()
        return SurveyObservation(variable=variable, value=value, disabled=disabled, value_unknown=value_unknown,
                                 _is_public=_is_public)

    def _dummy_survey(self, sample_year=2001, password=None, target_group="folkbib",
                      status="not_viewed", publish=False, library=None, is_active=True,
                      observations=[], selected_libraries=None):
        if not library:
            library = self._dummy_library()
        if selected_libraries is None:
            selected_libraries = [library.sigel]
        survey = Survey(library=library, sample_year=sample_year,
                        target_group=target_group, password=password, status=status, is_active=is_active,
                        observations=observations, selected_libraries=selected_libraries).save()
        if publish:
            survey.publish()
            survey.reload()
        return survey

    def _dummy_open_data(self, library_name=u"dummy_lib", sigel="dummy_sigel", sample_year=2013,
                         target_group="folkbib", is_active=True,
                         variable=None, value=1, date_created=None, date_modified=None, save=True):
        if not variable:
            variable = self._dummy_variable()
            variable.save()
        if not date_created:
            date_created = datetime(2014, 05, 27, 8, 00, 00)
        if not date_modified:
            date_modified = datetime(2014, 06, 02, 17, 57, 16)
        open_data = OpenData(library_name=library_name, sigel=sigel, sample_year=sample_year, is_active=is_active,
                             target_group=target_group, variable=variable, value=value, date_created=date_created,
                             date_modified=date_modified)
        if save:
            open_data.save()
            open_data.reload()
        return open_data

    def _dummy_article(self, title=None, content=None):
        article = Article(title, content)
        article.save()
        article.reload()
        return article

    def _dummy_dispatch(self, description=None, title=None, message=None, library_email=None,
                        library_city=None, library_name=None):
        dispatch = Dispatch(description=description, title=title, message=message, library_email=library_email,
                            library_city=library_city, library_name=library_name)
        dispatch.save()
        dispatch.reload()
        return dispatch

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
