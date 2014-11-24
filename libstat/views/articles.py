# -*- coding: utf-8 -*

from django.shortcuts import render
from libstat.models import Article


def articles(request):
    # Article(title="Officiell biblioteksstatistik för verksamhetsåret 2014",
    #        content=("Idag har den insamlade datan för verksamhetsåret 2014 publicerats."
    #                 "Datan kan nås via Biblioteksstatistikens publika API eller rapportfunktion.")).save()
    # Article(title="Korrigeringar av år 2014 insamlad data",
    #        content=("På grund av mänskliga faktorer så var en del av den insamlade datan inkorrekt."
    #                 "De berörda enkäterna har ompublicerats och finns nu allmänt tillgängliga.")).save()
    articles = Article.objects.order_by("-date_published")
    context = {
        "articles": articles
    }
    return render(request, 'libstat/articles.html', context)
