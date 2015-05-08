# -*- coding: utf-8 -*
from django import forms

from libstat.models import Article
from data.articletypes import ARTICLE_TYPES


class ArticleForm(forms.Form):
    title = forms.CharField(label=u"Rubrik", widget=forms.TextInput(attrs={"class": "form-control form-article-input"}))
    content = forms.CharField(label=u"Innehåll", widget=forms.Textarea(attrs={"class": "form-control form-article-input"}))
    type = forms.ChoiceField(choices=ARTICLE_TYPES, required=True, widget=forms.Select(attrs={"class": "form-control form-article-input"}))

    def __init__(self, *args, **kwargs):
        self.article = kwargs.pop('article', None)
        super(ArticleForm, self).__init__(*args, **kwargs)
        if self.article:
            self.fields["title"].initial = self.article.title
            self.fields["content"].initial = self.article.content
            self.fields["type"].initial = self.article.type


    def save(self):
        article = self.article if self.article else Article()
        article.title = self.cleaned_data["title"]
        article.content = self.cleaned_data["content"]
        article.type = self.cleaned_data["type"]
        article.save()
