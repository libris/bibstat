# -*- coding: utf-8 -*-
import logging

from django.shortcuts import render
from bibstat import settings
from libstat.models import Article


logger = logging.getLogger(__name__)


def admin(request):
    context = {
        "nav_start_css": "active",
        "nav_open_data_css": ""
    }
    return render(request, 'libstat/admin.html', context)

def index(request):
    context = {
        "articles": Article.objects.all().order_by("-date_published"),
        "blog_url": settings.BIBSTAT_BLOG_BASE_URL,
        "api_base_url": settings.API_BASE_URL
    }

    return render(request, 'libstat/index.html', context)

def open_data(request):
    context = {
        "nav_start_css": "",
        "nav_open_data_css": "active",
        "api_base_url": settings.API_BASE_URL
    }
    return render(request, 'libstat/open_data.html', context)