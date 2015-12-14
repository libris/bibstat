# -*- coding: utf-8 -*-
import logging

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from bibstat import settings
from libstat.models import Article, OpenData


logger = logging.getLogger(__name__)


def index(request):
    context = {
        "articles": Article.objects.all().order_by("-date_published"),
        "open_data_years": sorted(OpenData.objects.distinct("sample_year"), reverse=True),
        "blog_url": settings.BIBSTAT_BLOG_BASE_URL,
        "api_base_url": settings.API_BASE_URL,
        "environment": settings.ENVIRONMENT
    }

    return render(request, 'libstat/index.html', context)


def admin(request):
    if request.user.is_authenticated():
        return redirect(reverse("surveys"))

    return render(request, 'libstat/admin.html')