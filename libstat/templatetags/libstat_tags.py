# -*- coding: UTF-8 -*-
import json
import textwrap
import re
import locale
from datetime import datetime

import pytz
from django import template

from bibstat import settings
from libstat.models import Dispatch, Survey
from libstat.utils import targetGroups, ALL_TARGET_GROUPS_label, variableTypes
from data.municipalities import municipalities


register = template.Library()


@register.filter
def utc_tz(value):
    return value.replace(tzinfo=pytz.utc) if value and isinstance(value, datetime) else value


@register.filter
def tg_label(value):
    display_names = []
    if value:
        if isinstance(value, list):
            if set(value) == set(targetGroups.keys()):
                display_names.append(ALL_TARGET_GROUPS_label)
            else:
                for tg in value:
                    if tg in targetGroups:
                        display_names.append(targetGroups[tg])
        else:
            if value in targetGroups:
                display_names.append(targetGroups[value])
    return ", ".join(display_names)

@register.filter
def var_type_label(var_key):
    try:
        return variableTypes[var_key]
    except KeyError:
        return None

@register.filter
def srs_label(key):
    return next((status[1] for status in Survey.STATUSES if status[0] == key))


@register.filter
def access(value, arg):
    try:
        return value[arg]
    except KeyError:
        return None

@register.filter
def get_errors(form, key):
    try:
        if len(form[key].errors) > 0:
            return form[key].errors.as_text()
    except KeyError:
        return None
    return None

@register.filter
def split_into_number_and_body(description):
    if re.compile("^[0-9]+\.").match(description):
        return description.split(" ", 1)
    else:
        return "", description


@register.filter
def municipality_name(municipality_code):
    return municipalities.get(municipality_code, municipality_code)


@register.filter
def as_json(o):
    return json.dumps(o)


@register.filter
def analytics_enabled(_):
    return settings.ANALYTICS_ENABLED


@register.filter
def debug_enabled(_):
    return settings.DEBUG


@register.filter
def format_number(number, digits=1):
    try:
        locale.setlocale(locale.LC_NUMERIC, 'sv_SE')
    except Exception:
        locale.setlocale(locale.LC_NUMERIC, 'sv_SE.UTF-8')
    return locale.format("%d" if number == int(number) else "%.{}f".format(digits), number, grouping=True)

@register.filter
def format_percentage(number):
    percentage = number * 100
    return format_number(percentage) + "%"

@register.filter
def format_email(email, limit=30):
    if len(email) <= limit:
        return email

    return email[:limit - 3] + "..."


@register.filter
def two_parts(thelist):
    middle = len(thelist) / 2

    if len(thelist) % 2 == 0:
        return [thelist[middle:], thelist[:middle]]
    else:
        return [thelist[:middle + 1], thelist[middle + 1:]]

@register.filter
def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


@register.filter
def show_in_chart(rows):
    rows = [row for row in rows if row.get("show_in_chart", False)]

    for row in rows:
        row["label"] = "<br>".join(textwrap.wrap(row["label"], 50))

    return rows


@register.simple_tag
def footer():
    infoStr = "&copy; Kungl. biblioteket 2014-" + str(datetime.now().year)
    if settings.RELEASE_VERSION:
        infoStr = infoStr + ". Version " + settings.RELEASE_VERSION
    return infoStr


@register.simple_tag()
def dispatches_count():
    return Dispatch.objects.count()
