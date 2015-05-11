# -*- coding: utf-8 -*
import os
import logging

from django.core.files import File
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from bibstat import settings
from libstat.forms.article import ArticleForm
from libstat.models import Article
from data.articletypes import article_types_dict, article_types_to_save_as_html, single_article_types

logger = logging.getLogger(__name__)

def _html_template_path():
    if settings.ENVIRONMENT == "local":
        return "{}/libstat/templates/libstat/index/".format(os.getcwd())
    return "/data/appl/bibstat/libstat/templates/libstat/index/"

@permission_required('is_superuser', login_url='index')
def articles(request):
    context = {
        "articles": Article.objects.order_by("-date_published"),
        "nav_articles_css": "active"
    }
    return render(request, 'libstat/articles.html', context)


@permission_required('is_superuser', login_url='index')
def article(request, article_id=None):
    article = Article.objects.get(pk=article_id) if article_id else None

    if request.method == "POST":
        form = ArticleForm(request.POST, article=article)
        if form.is_valid():

            # Also check if duplicates of same type for all single article types
            type = request.POST.get("type")
            if (type in single_article_types):
                other_article_with_same_type = Article.objects.filter(type=type, pk__ne=article_id) if article_id else Article.objects.filter(type=type)
                if other_article_with_same_type.count() > 0:
                    context = {
                        "form": form,
                        "duplicate_type": article_types_dict.get(type)
                    }
                    return render(request, 'libstat/article.html', context)

            article = form.save()

            # Some article types to be saved as html template
            if article.type in article_types_to_save_as_html:
                filename = "{}.html".format(article.type)
                with open("{}{}".format(_html_template_path(), filename), "w") as f:
                    cms_comment = "\n<!-- Note! This template is edited via cms functionality. Go to adminpages/publications on the site to make changes. -->\n".encode('utf-8')
                    File(f).write(cms_comment)
                    File(f).write(article.content.encode('utf-8'))
                    File(f).write(cms_comment)
                    f.close()

        return redirect(reverse("articles"))

    if request.method == "GET":
        context = {
            "form": ArticleForm(article=article)
        }
        return render(request, 'libstat/article.html', context)


@permission_required('is_superuser', login_url='index')
def articles_delete(request, article_id=None):
    if request.method == "POST":
        article = Article.objects.get(pk=article_id) if article_id else None
        if article:
            article.delete()
        return redirect(reverse("articles"))
