# -*- coding: utf-8 -*-
import logging

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from bibstat import settings
from libstat.models import Article, OpenData


logger = logging.getLogger(__name__)

def index(request):
    context = {
        "articles" : Article.objects.all().order_by("-date_published"),
        #"correction_articles": Article.objects.filter(type=u"correction").order_by("-date_published"),
        #"statistics_introtext": Article.objects.filter(type=u"statistics_intro").order_by("-date_published").first().content,
        #"statistics_infotext": Article.objects.filter(type=u"statistics_info").order_by("-date_published").first().content,
        #"reports_introtext": Article.objects.filter(type=u"reports_intro").order_by("-date_published").first().content,
        #"reports_infotext": Article.objects.filter(type=u"reports_info").order_by("-date_published").first().content,
        #"open_data_introtext": Article.objects.filter(type=u"open_data_intro").order_by("-date_published").first().content,
        #"open_data_infotext": Article.objects.filter(type=u"open_data_info").order_by("-date_published").first().content,
        #"read_more_introtext": Article.objects.filter(type=u"read_more_intro").order_by("-date_published").first().content,
        "open_data_years": sorted(OpenData.objects.distinct("sample_year"), reverse=True),
        "blog_url": settings.BIBSTAT_BLOG_BASE_URL,
        "api_base_url": settings.API_BASE_URL
    }

    return render(request, 'libstat/index.html', context)


def admin(request):
    if request.user.is_authenticated():
        return redirect(reverse("surveys"))

    return render(request, 'libstat/admin.html')