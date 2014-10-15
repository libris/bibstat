# -*- coding: utf-8 -*-

from django.shortcuts import render

from libstat.forms import *


logger = logging.getLogger(__name__)


def index(request):
    context = {
        "nav_start_css": "active",
        "nav_open_data_css": ""
    }
    return render(request, 'libstat/index.html', context)
