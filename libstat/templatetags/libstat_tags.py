# -*- coding: UTF-8 -*-
from datetime import datetime

import pytz
from django import template

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


register.filter('utc_tz', utc_tz)
register.filter('tg_label', tg_label)
register.filter('srs_label', srs_label)
register.filter('access', access)
