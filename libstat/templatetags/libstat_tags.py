# -*- coding: UTF-8 -*-
import pytz
from datetime import datetime
from django import template
from libstat.models import targetGroups

register = template.Library()

def utc_tz(value):
    """
        Append UTC tzinfo to a datetime to get correct localization of dates and times in view.
        Datetime objects for documents are stored as UTC without timezone information.
    """
    return value.replace(tzinfo=pytz.utc) if value and isinstance(value, datetime) else value

def tg_label(value):
    """
        Get a label for a list or a single target group key.
    """
    display_names = []
    if value:
        if isinstance(value, list):
            if set(value) == set(targetGroups.keys()):
                display_names.append(u"Samtliga bibliotekstyper")
            else:
                for tg in value:
                    if tg in targetGroups:
                        display_names.append(targetGroups[tg])
        else:
            if value in targetGroups:
                display_names.append(targetGroups[value])
    return ", ".join(display_names)
            

register.filter('utc_tz', utc_tz)
register.filter('tg_label', tg_label)