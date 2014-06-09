# -*- coding: UTF-8 -*-
import datetime


"""
    Datetime in ISO8601 format with apppending 'Z' to indicate UTC time zone
"""
ISO8601_utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"

"""
    Parse a datetime from an ISO8601 formatted date string. 
    
    Note: Timezone designator not supported ("+01:00").
"""
def parse_datetime_from_isodate_str(date_str):
    if not date_str:
        return None
    
    datetime_obj = parse_datetime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
    if not datetime_obj:
        datetime_obj = parse_datetime(date_str, "%Y-%m-%dT%H:%M:%S")
    if not datetime_obj:
        datetime_obj = parse_datetime(date_str, "%Y-%m-%dT%H:%M")
    if not datetime_obj:
        datetime_obj = parse_datetime(date_str, "%Y-%m-%dT%H")
    if not datetime_obj:
        datetime_obj = parse_datetime(date_str, "%Y-%m-%d")
    if not datetime_obj:
        datetime_obj = parse_datetime(date_str, "%Y-%m")
    if not datetime_obj:
        datetime_obj = parse_datetime(date_str, "%Y")
    return datetime_obj
    
        
def parse_datetime(date_str, date_format):
    try:
        return datetime.datetime.strptime(date_str, date_format)
    except ValueError:
        return None
