# -*- coding: UTF-8 -*-
import random
import string
from datetime import datetime

from django.core.urlresolvers import reverse

from libstat.models import Variable, OpenData, Survey, Library


def _get(instance=None, action=None, kwargs=None):
    url = reverse(action, kwargs=kwargs)
    return instance.client.get(url)


def _post(instance=None, action=None, kwargs=None, data=None):
    url = reverse(action, kwargs=kwargs)
    return instance.client.post(url, data=data)


def _login(instance=None, user=None, password=None):
    instance.client.login(username="admin", password="admin")


def _dummy_library():
    library = Library()
    library.save()
    library.reload()
    return library


def _dummy_survey(library_name="dummy_name", sample_year=2001, password=None):
    library = _dummy_library()
    survey = Survey(library_name=library_name, library=library, sample_year=sample_year,
                            target_group="public", password=password)
    survey.save()
    survey.reload()
    return survey


def _dummy_variable(key=None, description=u"dummy description", type="integer", is_public=True,
                    target_groups=["public"], is_draft=False, replaced_by=None, save=True):
    if not key:
        key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    variable = Variable(key=key, description=description, type=type, is_public=is_public, target_groups=target_groups,
                        is_draft=is_draft, replaced_by=replaced_by)
    if save:
        variable.save()
        variable.reload()
    return variable


def _dummy_open_data(library_name=u"dummy_lib", library_id=u"123", sample_year=2013, target_group="public",
                     variable=None, value=1, date_created=None, date_modified=None, save=True):
    if not variable:
        variable = _dummy_variable()
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
