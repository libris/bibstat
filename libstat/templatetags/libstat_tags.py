# -*- coding: UTF-8 -*-
from datetime import datetime

import pytz
from django import template
from libstat.models import Dispatch

from libstat.utils import target_groups_label, survey_response_status_label


register = template.Library()


def utc_tz(value):
    return value.replace(tzinfo=pytz.utc) if value and isinstance(value, datetime) else value


def tg_label(value):
    return target_groups_label(value)


def srs_label(key):
    return survey_response_status_label(key)


def access(value, arg):
    return value[arg]


def with_status(surveys, status):
    return [survey for survey in surveys if survey.status == status]


def with_target_group(surveys, target_group):
    return [survey for survey in surveys if survey.target_group == target_group]


def dispatches_count():
    return Dispatch.objects.count()

register.filter('utc_tz', utc_tz)
register.filter('tg_label', tg_label)
register.filter('srs_label', srs_label)
register.filter('access', access)
register.filter('with_status', with_status)
register.filter('with_target_group', with_target_group)
register.simple_tag(dispatches_count)
