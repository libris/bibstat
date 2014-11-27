# -*- coding: UTF-8 -*-
from django.core.urlresolvers import reverse
from libstat.models import Article
from libstat.tests import MongoTestCase


class TestArticleView(MongoTestCase):
    def test_can_view_articles_when_not_logged_in(self):
        self._dummy_article()
        self._dummy_article()
        self._dummy_article()

        response = self._get("articles")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["articles"]), 3)

    def test_can_view_articles_when_not_logged_in(self):
        self._dummy_article()
        article = self._dummy_article(title="some_title", content="some_content")
        self._dummy_article()

        response = self._get("articles")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["articles"][1].title, article.title)
        self.assertEqual(response.context["articles"][1].content, article.content)
        self.assertEqual(response.context["articles"][1].date_published, article.date_published)

    def test_can_not_edit_articles_when_not_logged_in(self):
        article = self._dummy_article(title="some_title", content="some_content")

        response = self._get("article", kwargs={"article_id": str(article.pk)})

        self.assertEqual(response.status_code, 302)

    def test_can_edit_articles_when_logged_in(self):
        self._login()
        article = self._dummy_article(title="some_title", content="some_content")

        response = self._get("article", kwargs={"article_id": str(article.pk)})

        self.assertEqual(response.status_code, 200)

    def test_updates_article(self):
        self._login()
        article = self._dummy_article(title="some_title", content="some_content")

        self._post("article", kwargs={"article_id": str(article.pk)}, data={"title": "new_title",
                                                                            "content": "new_content"})

        article.reload()
        self.assertEquals(article.title, "new_title")
        self.assertEquals(article.content, "new_content")

    def test_can_not_update_article_if_not_logged_in(self):
        article = self._dummy_article(title="some_title", content="some_content")

        self._post("article", kwargs={"article_id": str(article.pk)}, data={"title": "new_title",
                                                                            "content": "new_content"})

        article.reload()
        self.assertEquals(article.title, "some_title")
        self.assertEquals(article.content, "some_content")

    def test_deletes_article(self):
        self._login()
        article = self._dummy_article(title="some_title", content="some_content")

        self._post("articles_delete", kwargs={"article_id": str(article.pk)})

        self.assertEquals(Article.objects.count(), 0)

    def test_can_not_delete_article_if_not_logged_in(self):
        article = self._dummy_article(title="some_title", content="some_content")

        self._post("articles_delete", kwargs={"article_id": str(article.pk)})

        self.assertEquals(Article.objects.count(), 1)