# -*- coding: UTF-8 -*-
import pytz
from datetime import datetime
from django import template

register = template.Library()

def utc_tz(value):
    return value.replace(tzinfo=pytz.utc) if value and isinstance(value, datetime) else value

register.filter('utc_tz', utc_tz)