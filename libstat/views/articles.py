# -*- coding: utf-8 -*
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from libstat.forms.article import ArticleForm
from libstat.models import Article


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
            form.save()
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