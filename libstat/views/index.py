# -*- coding: utf-8 -*-
import logging

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from bibstat import settings
from libstat.models import Article, OpenData


logger = logging.getLogger(__name__)

def index(request):

    # Include text content from articles (edited via cms functionality on the site under /admin and publications)

    all_articles = Article.objects.all().order_by("-date_published")
    front_introtext = ""
    correction_articles = []
    statistics_introtext = ""
    reports_introtext = ""
    open_data_introtext = ""
    read_more_introtext = ""
    for article in all_articles:
        if (article.type=="front_intro"):
            front_introtext = article
        if (article.type=="correction"):
            correction_articles.append(article)
        elif (article.type=="statistics_intro"):
            statistics_introtext = article
        elif (article.type=="statistics_info"):
            statistics_infotext = article
        elif (article.type=="reports_intro"):
            reports_introtext = article
        elif (article.type=="open_data_intro"):
            open_data_introtext = article
        elif (article.type=="open_data_info"):
            open_data_infotext = article
        elif (article.type=="read_more_intro"):
            read_more_introtext = article

    context = {
        "front_introtext": front_introtext,
        "correction_articles": correction_articles,
        "statistics_introtext": statistics_introtext,
        "statistics_infotext": statistics_infotext,
        "reports_introtext": reports_introtext,
        "open_data_introtext": open_data_introtext,
        "open_data_infotext": open_data_infotext,
        "read_more_introtext": read_more_introtext,
        "open_data_years": sorted(OpenData.objects.distinct("sample_year"), reverse=True),
        "blog_url": settings.BIBSTAT_BLOG_BASE_URL,
        "api_base_url": settings.API_BASE_URL
    }

    return render(request, 'libstat/index.html', context)


def admin(request):
    if request.user.is_authenticated():
        return redirect(reverse("surveys"))

    return render(request, 'libstat/admin.html')