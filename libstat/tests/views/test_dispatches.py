# -*- coding: UTF-8 -*-
from libstat.models import Dispatch
from libstat.tests import MongoTestCase


class TestDispatches(MongoTestCase):
    def setUp(self):
        self._login()

    def test_can_not_view_dispatches_if_not_logged_in(self):
        self._logout()

        response = self._get("dispatches")

        self.assertTrue(response.status_code, 200)

    def test_can_view_dispatches(self):
        self._dummy_dispatch()
        self._dummy_dispatch()
        self._dummy_dispatch()

        response = self._get("dispatches")

        self.assertTrue(response.status_code, 200)
        self.assertTrue(len(response.context["dispatches"]), 3)

    def test_can_create_dispatches(self):
        survey1 = self._dummy_survey(library=self._dummy_library("lib1"))
        self._dummy_survey(library=self._dummy_library("lib2"))
        survey3 = self._dummy_survey(library=self._dummy_library("lib3"))

        self._post("dispatches", data={
            "title": "some_title",
            "message": "some_message",
            "description": "some_description",
            "survey-response-ids": [survey1.pk, survey3.pk]
        })

        self.assertEquals(Dispatch.objects.count(), 2)
        self.assertEquals(Dispatch.objects.get(library_name="lib3").title, "some_title")
        self.assertEquals(Dispatch.objects.get(library_name="lib3").message, "some_message")
        self.assertEquals(Dispatch.objects.get(library_name="lib3").description, "some_description")

    def test_can_delete_dispatches(self):
        dispatch1 = self._dummy_dispatch()
        self._dummy_dispatch()
        dispatch3 = self._dummy_dispatch()

        self._post("dispatches_delete", data={
            "dispatch-ids": [dispatch1.pk, dispatch3.pk]
        })

        self.assertEquals(Dispatch.objects.count(), 1)

    def test_replaces_key_words_with_survey_fields(self):
        survey = self._dummy_survey(password="some_password", library=self._dummy_library(name="some_name",
                                                                                          city="some_city"))

        self._post("dispatches", data={
            "title": "abc {bibliotek} cde {ort} fgh {lösenord}",
            "message": "ijk {lösenord} lmn{bibliotek}opq {ort}",
            "description": "some_description",
            "survey-response-ids": [survey.pk]
        })

        dispatch = Dispatch.objects.all()[0]

        self.assertEquals(dispatch.title, "abc some_name cde some_city fgh some_password")
        self.assertEquals(dispatch.message, "ijk some_password lmnsome_nameopq some_city")