# -*- coding: UTF-8 -*-
from datetime import timedelta

from libstat.tests import MongoTestCase
from libstat.models import *
from bson.objectid import ObjectId


"""
    Model class test cases
"""


class SurveyResponseTest(MongoTestCase):

    def setUp(self):
        self.current_user = User.objects.filter(username="admin")[0]

        v1 = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer",
                      is_public=True, target_groups=["public"])
        v1.save()
        v2 = Variable(key=u"folk6",
                      description=u"Är huvudbiblioteket i er kommun integrerat med ett skolbibliotek? 1=ja",
                      type="boolean", is_public=True, target_groups=["public"])
        v2.save()
        v3 = Variable(key=u"folk8", description=u"Textkommentar", type="string", is_public=False,
                      target_groups=["public"])
        v3.save()

        library = Library(bibdb_id=u"323", bibdb_sigel="Kld1", bibdb_name=u"Karlstad stadsbibliotek").save()
        sr = Survey(library_name="KARLSTAD STADSBIBLIOTEK", sample_year=2013, target_group="public",
                    observations=[], created_by=self.current_user, library=library)
        sr.observations.append(SurveyObservation(variable=v1, value=7, _source_key="folk5", _is_public=v1.is_public))
        sr.observations.append(
            SurveyObservation(variable=v2, value=None, _source_key="folk6", _is_public=v2.is_public))
        sr.observations.append(
            SurveyObservation(variable=v3, value=u"Här är en kommentar", _source_key="folk8", _is_public=v3.is_public))
        self.survey_response = sr.save()

    def test_can_not_update_status_to_invalid_value(self):
        survey = self._dummy_survey()

        try:
            survey.status = "some_invalid_status"
            self.assertTrue(False)
        except KeyError:
            pass

    def test_can_create_survey_with_valid_status(self):
        survey = self._dummy_survey(status="not_viewed")

        self.assertEquals(survey.status, "not_viewed")

    def test_can_not_create_survey_with_invalid_status(self):
        try:
            self._dummy_survey(status="some_invalid_status")
            self.assertTrue(False)
        except KeyError:
            pass

    def test_can_update_status_to_valid_value(self):
        survey = self._dummy_survey(status="not_viewed")

        survey.status = "initiated"

        self.assertEquals(survey.status, "initiated")

    def test_should_export_public_non_null_observations_to_openData(self):
        variable = self._dummy_variable(key=u"key1", is_public=True)
        observation = SurveyObservation(variable=variable, value="val1", _source_key=variable.key,
                                        _is_public=variable.is_public)
        library = self._dummy_library(name="lib1_name", sigel="lib1_sigel")
        survey = self._dummy_survey(library=library, observations=[observation])

        survey.publish(user=self.current_user)
        survey.reload()

        open_data = OpenData.objects.all().get(0)
        self.assertEquals(open_data.library_name, "lib1_name")
        self.assertEquals(open_data.variable.key, "key1")
        self.assertEquals(open_data.value, "val1")
        self.assertTrue(open_data.date_modified)
        self.assertTrue(open_data.date_created)
        self.assertEquals(open_data.date_created, open_data.date_modified)
        self.assertEquals(open_data.date_created, survey.published_at)
        self.assertEquals(survey.published_by, self.current_user)

    def test_should_overwrite_value_and_date_modified_for_existing_openData(self):
        variable = self._dummy_variable(key=u"key1", is_public=True)
        observation = SurveyObservation(variable=variable, value="old_value", _source_key=variable.key,
                                        _is_public=variable.is_public)
        library = self._dummy_library(name="lib1_name", sigel="lib1_sigel")
        survey = self._dummy_survey(library=library, observations=[observation])

        survey.publish(user=self.current_user)
        survey.reload()

        for obs in survey.observations:
            if obs.variable.key == "key1":
                obs.value = "new_value"
        survey.save()
        survey.publish(user=self.current_user)

        data = OpenData.objects.all()
        self.assertEquals(len(data), 1)

        open_data = data.get(0)
        self.assertEquals(open_data.library_name, "lib1_name")
        self.assertEquals(open_data.target_group, "public")
        self.assertEquals(open_data.value, "new_value")
        self.assertTrue(open_data.date_modified)
        self.assertTrue(open_data.date_created)
        self.assertNotEquals(open_data.date_created, open_data.date_modified)

    def test_should_get_observation_by_variable_key(self):
        self.assertEquals(self.survey_response.observation_by_key("folk8").value, u"Här är en kommentar")

    def test_should_store_version_when_updating_existing_object(self):
        library = self._dummy_library(name="lib1_old_name", city="lib1_old_city", sigel="lib1_sigel")
        survey = self._dummy_survey(website="old_website", library=library)

        library.name = "lib1_new_name"
        library.city = "lib1_new_city"
        survey.library = library.save()
        survey.website = "new_website"
        survey = survey.save()

        self.assertEquals(survey.library.name, "lib1_new_name")
        self.assertEquals(survey.library.city, "lib1_new_city")
        self.assertEquals(survey.website, "new_website")

        versions = SurveyVersion.objects.filter(survey_response_id=survey.id)
        self.assertEquals(len(versions), 1)
        self.assertEquals(versions[0].survey_response_id, survey.id)
        self.assertEquals(versions[0].library.name, "lib1_old_name")
        self.assertEquals(versions[0].library.city, "lib1_old_city")
        self.assertEquals(versions[0].website, "old_website")

    def test_should_store_one_version_for_each_change(self):
        self.survey_response.library.bibdb_id = u"321"
        self.survey_response.save()
        self.assertEquals(len(SurveyVersion.objects.filter(survey_response_id=self.survey_response.id)), 1)

        self.survey_response.library.bibdb_id = u"197"
        self.survey_response.save()
        self.assertEquals(len(SurveyVersion.objects.filter(survey_response_id=self.survey_response.id)), 2)

    def test_should_store_version_when_updating_observations_for_existing_objects(self):
        self.survey_response.observation_by_key(u"folk5").value = 5
        self.survey_response.save()

        updated_sr = Survey.objects.get(pk=self.survey_response.id)
        self.assertEquals(updated_sr.observation_by_key(u"folk5").value, 5)

        versions = SurveyVersion.objects.filter(survey_response_id=self.survey_response.id)
        self.assertEquals(len(versions), 1)
        self.assertEquals(versions[0].observation_by_key(u"folk5").value, 7)

    def test_should_not_store_version_when_creating_object(self):
        sr = Survey(library_name=u"Some name", sample_year=2014, target_group=u"research", observations=[])
        sr.save()

        versions = SurveyVersion.objects.filter(survey_response_id=self.survey_response.id)
        self.assertEquals(len(versions), 0)

    def test_should_set_modified_date_and_by_when_updating_existing_object(self):
        self.survey_response.library_name = u"Stadsbiblioteket i Karlstad"
        self.survey_response.save()

        versions = SurveyVersion.objects.filter(survey_response_id=self.survey_response.id)
        self.assertEquals(len(versions), 1)

        sr = Survey.objects.get(pk=self.survey_response.id)
        self.assertTrue(sr.date_modified > versions[0].date_modified)

    def test_should_flag_as_not_published_when_updating_existing_object(self):
        self.survey_response.library_name = u"Stadsbiblioteket i Karlstad"
        self.survey_response.save()

        sr = Survey.objects.get(pk=self.survey_response.id)
        self.assertFalse(sr.is_published)

    def test_should_set_modified_date_when_creating_object(self):
        self.assertEquals(self.survey_response.date_modified, self.survey_response.date_created)
        self.assertEquals(self.survey_response.modified_by, self.current_user)

    def test_should_flag_new_object_as_not_published(self):
        self.assertFalse(self.survey_response.is_published)

    def test_should_set_published_date_but_not_modified_date_when_publishing(self):
        survey = self._dummy_survey()
        date_modified = survey.date_modified

        survey.publish(user=self.current_user)

        self.assertNotEquals(survey.published_at, None)
        self.assertEquals(survey.published_by, self.current_user)
        self.assertEquals(survey.date_modified, date_modified)

    def test_should_flag_as_published_when_publishing(self):
        survey = self._dummy_survey()

        survey.publish()
        survey.reload()

        self.assertTrue(survey.is_published)

    def test_latest_version_published(self):
        library = self._dummy_library()
        survey = self._dummy_survey(library=library)

        survey.published_at = survey.date_modified + timedelta(hours=-1)
        self.assertFalse(survey.latest_version_published)

        survey.published_at = survey.date_modified
        self.assertTrue(survey.latest_version_published)

        survey.published_at = None
        self.assertFalse(survey.latest_version_published)

        survey.status = "submitted"
        self.assertFalse(survey.latest_version_published)

        survey.publish()
        self.assertTrue(survey.latest_version_published)

    def test_is_published(self):
        survey = self._dummy_survey()
        self.assertFalse(survey.is_published)

        survey.publish()
        self.assertTrue(survey.is_published)

        survey.status = "submitted"
        self.assertFalse(survey.is_published)


class SurveyLibraryCachingTest(MongoTestCase):

    def test_should_always_use_cached_library_and_not_actual_library(self):
        library = self._dummy_library(name="lib1_name", sigel="lib1_sigel")
        survey = self._dummy_survey(library=library)
        self.assertNotEquals(library, survey.library)

    def test_should_use_cached_library_when_actual_library_is_removed_and_survey_is_not_published(self):
        library = self._dummy_library(name="lib1_name", sigel="lib1_sigel")
        survey = self._dummy_survey(library=library)
        Library.objects.all().delete()
        self.assertEquals(survey.library.name, "lib1_name")

    def test_should_update_cached_library_to_match_actual_library_when_it_is_updated_and_survey_is_not_published(self):
        library = self._dummy_library(name="lib1_name", sigel="lib1_sigel")
        survey = self._dummy_survey(library=library)
        library.name = "new_name"
        library.save()

        self.assertEquals(survey.library.name, "new_name")

    def test_should_use_new_library_if_it_has_the_same_sigel_as_the_old_library_and_survey_is_not_published(self):
        library = self._dummy_library(name="lib1_name", sigel="lib1_sigel")
        survey = self._dummy_survey(library=library)
        Library.objects.all().delete()
        self._dummy_library(name="new_name", sigel="lib1_sigel")

        self.assertEquals(survey.library.name, "new_name")

    def test_should_use_cached_library_when_actual_library_is_removed_and_survey_is_published(self):
        library = self._dummy_library(name="lib1_name", sigel="lib1_sigel")
        survey = self._dummy_survey(library=library)
        survey.publish()
        Library.objects.all().delete()

        self.assertEquals(survey.library.name, "lib1_name")

    def test_should_use_cached_library_when_actual_library_is_updated_after_publishing_survey(self):
        library = self._dummy_library(name="lib1_name", sigel="lib1_sigel")
        survey = self._dummy_survey(library=library)
        survey.publish()
        library.name = "new_name"
        library.save()

        self.assertEquals(survey.library.name, "lib1_name")

    def test_should_use_new_library_when_published_then_library_update_then_reopen(self):
        library = self._dummy_library(name="lib1_name", sigel="lib1_sigel")
        survey = self._dummy_survey(website="abcd", library=library)
        survey.publish()
        library.name = "new_name"
        library.save()
        survey.status = "not_viewed"

        self.assertEquals(survey.library.name, "new_name")


class OpenDataTest(MongoTestCase):

    def setUp(self):
        v = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer",
                     is_public=True, target_groups=["public"])
        v.save()
        publishing_date = datetime(2014, 06, 03, 15, 28, 31)
        d1 = OpenData(library_name=u"KARLSTAD STADSBIBLIOTEK", library_id=u"323", sample_year=2013,
                      target_group="public", variable=v, value=6, date_created=publishing_date,
                      date_modified=publishing_date)
        d1.save()
        d2 = OpenData(library_name=u"NORRBOTTENS LÄNSBIBLIOTEK", sample_year=2013, target_group="public", variable=v,
                      value=6, date_created=publishing_date, date_modified=publishing_date)
        d2.save()

    def test_should_transform_object_with_library_id_to_dict(self):
        object = OpenData.objects.get(library_name=u"KARLSTAD STADSBIBLIOTEK")
        openDataAsDict = {
            u"@id": str(object.id),
            u"@type": u"Observation",
            u"folk5": 6,
            u"library": {u"@id": u"{}/library/323".format(settings.BIBDB_BASE_URL)},
            u"sampleYear": 2013,
            u"targetGroup": u"Folkbibliotek",
            # u"targetGroup": {u"@id": u"public"}, #TODO
            u"published": "2014-06-03T15:28:31.000000Z",
            u"modified": "2014-06-03T15:28:31.000000Z"
        }
        self.assertEquals(object.to_dict(), openDataAsDict)

    def test_should_transform_object_without_library_id_to_dict(self):
        object = OpenData.objects.get(library_name=u"NORRBOTTENS LÄNSBIBLIOTEK")
        openDataAsDict = {
            u"@id": str(object.id),
            u"@type": u"Observation",
            u"folk5": 6,
            u"library": {u"name": u"NORRBOTTENS LÄNSBIBLIOTEK"},
            u"sampleYear": 2013,
            u"targetGroup": u"Folkbibliotek",
            # u"targetGroup": {u"@id": u"public"}, #TODO
            u"published": "2014-06-03T15:28:31.000000Z",
            u"modified": "2014-06-03T15:28:31.000000Z"
        }
        self.assertEquals(object.to_dict(), openDataAsDict)


class VariableQuerySetTest(MongoTestCase):

    def setUp(self):
        # Discontinued (today)
        v2 = Variable(key=u"Folk35", description=u"Antal årsverken övrig personal", type="decimal", is_public=False,
                      target_groups=["public"])
        v2.question = u"Hur många årsverken utfördes av personal i folkbiblioteksverksamheten under 2012?"
        v2.question_part = u"Antal årsverken övrig personal (ej städpersonal)"
        v2.active_to = datetime.utcnow().date()
        v2.save()
        self.v2 = Variable.objects.get(pk=v2.id)

        # Replaced
        v = Variable(key=u"Folk10", description=u"Antal bemannade servicesställen", type="integer", is_public=True,
                     target_groups=["public"])
        v.replaced_by = self.v2
        v.save()
        self.v = Variable.objects.get(pk=v.id)

        # Active
        v3 = Variable(key=u"Folk31", description=u"Antal årsverken totalt", type="decimal", is_public=True,
                      target_groups=["public"], id_draft=False)
        v3.summary_of = [self.v2]
        v3.save()
        self.v3 = Variable.objects.get(pk=v3.id)

        # Draft
        v4 = Variable(key=u"Folk69", description=u"Totalt nyförvärv AV-medier", type="integer", is_public=True,
                      target_groups=["public"], is_draft=True)
        v4.question = u"Hur många nyförvärv av AV-media gjordes under 2012?"
        v4.save()
        self.v4 = Variable.objects.get(pk=v4.id)

    def test_filter_public_terms(self):
        result_set = Variable.objects.public_terms()
        self.assertEquals([v.id for v in result_set], [self.v.id, self.v3.id])

    def test_filter_public_term_by_key(self):
        self.assertRaises(DoesNotExist, lambda: Variable.objects.public_term_by_key(None))
        self.assertRaises(DoesNotExist, lambda: Variable.objects.public_term_by_key("foo"))
        self.assertEquals(Variable.objects.public_term_by_key("Folk10").id, self.v.id)
        self.assertRaises(DoesNotExist, lambda: Variable.objects.public_term_by_key("Folk35"))
        self.assertEquals(Variable.objects.public_term_by_key("Folk31").id, self.v3.id)
        self.assertRaises(DoesNotExist, lambda: Variable.objects.public_term_by_key("Folk69"))

    def test_filter_replaceable_should_not_return_drafts_or_replaced(self):
        result_set = Variable.objects.replaceable()
        self.assertEquals([v.id for v in result_set], [self.v3.id, self.v2.id])

    def test_filter_surveyable_should_not_return_discontinued_or_replaced(self):
        result_set = Variable.objects.surveyable()
        self.assertEquals([v.id for v in result_set], [self.v3.id, self.v4.id])


class VariableTest(MongoTestCase):

    def setUp(self):
        v = Variable(key=u"Folk10", description=u"Antal bemannade servicesställen", type="integer", is_public=True,
                     target_groups=["public"],
                     active_from=datetime(2010, 1, 1).date())
        v.save()
        self.v = Variable.objects.get(pk=v.id)

        v2 = Variable(key=u"Folk35", description=u"Antal årsverken övrig personal", type="decimal", is_public=True,
                      target_groups=["public"],
                      active_to=datetime(2014, 6, 1).date())
        v2.question = u"Hur många årsverken utfördes av personal i folkbiblioteksverksamheten under 2012?"
        v2.question_part = u"Antal årsverken övrig personal (ej städpersonal)"
        v2.save()
        self.v2 = Variable.objects.get(pk=v2.id)

        v3 = Variable(key=u"Folk31", description=u"Antal årsverken totalt", type="decimal", is_public=True,
                      target_groups=["public"],
                      active_from=datetime.utcnow().date(), active_to=(datetime.utcnow() + timedelta(days=1)).date())
        v3.summary_of = [self.v2]
        v3.save()
        self.v3 = Variable.objects.get(pk=v3.id)

        v4 = Variable(key=u"Folk69", description=u"Totalt nyförvärv AV-medier", type="integer", is_public=True,
                      target_groups=["public"], is_draft=True)
        v4.question = u"Hur många nyförvärv av AV-media gjordes under 2012?"
        v4.save()
        self.v4 = Variable.objects.get(pk=v4.id)

    def test_key_asc_should_be_default_sort_order(self):
        result = Variable.objects.all()
        self.assertEquals([v.key for v in result], [u"Folk10", u"Folk31", u"Folk35", u"Folk69"])

    def test_should_transform_object_to_dict(self):
        self.v.active_from = None
        self.v.save()

        folk10 = Variable.objects.get(pk=self.v.id)
        expectedVariableDict = {
            u"@id": u"Folk10",
            u"@type": [u"rdf:Property", u"qb:MeasureProperty"],
            u"comment": u"Antal bemannade servicesställen",
            u"range": u"xsd:integer"
        }
        self.assertEqual(folk10.to_dict(), expectedVariableDict)

    def test_should_transform_replacing_object_to_dict(self):
        self.v4.replace_siblings([self.v2.id], commit=True)
        folk69 = Variable.objects.get(pk=self.v4.id)
        expectedVariableDict = {
            u"@id": u"Folk69",
            u"@type": [u"rdf:Property", u"qb:MeasureProperty"],
            u"comment": u"Totalt nyförvärv AV-medier",
            u"range": u"xsd:integer",
            u"replaces": [u"Folk35"]
        }
        self.assertEqual(folk69.to_dict(), expectedVariableDict)

    def test_should_transform_replaced_object_to_dict(self):
        self.v4.is_draft = False
        self.v4.replace_siblings([self.v2.id], commit=True)

        folk35 = Variable.objects.get(pk=self.v2.id)

        expectedVariableDict = {
            u"@id": u"Folk35",
            u"@type": [u"rdf:Property", u"qb:MeasureProperty"],
            u"comment": u"Antal årsverken övrig personal",
            u"range": u"xsd:decimal",
            u"replacedBy": u"Folk69",
        }
        self.assertEqual(folk35.to_dict(), expectedVariableDict)

    def test_should_transform_discontinued_object_to_dict(self):
        self.v.active_from = None
        self.v.active_to = datetime(2014, 8, 31)
        self.v.save()

        folk10 = Variable.objects.get(pk=self.v.id)
        expectedVariableDict = {
            u"@id": u"Folk10",
            u"@type": [u"rdf:Property", u"qb:MeasureProperty"],
            u"comment": u"Antal bemannade servicesställen",
            u"range": u"xsd:integer",
            u"valid": "name=Giltighetstid; end=2014-08-31;"
        }
        self.assertEqual(folk10.to_dict(), expectedVariableDict)

    def test_should_transform_pending_object_to_dict(self):
        tomorrow = (datetime.utcnow() + timedelta(days=1)).date()
        self.v.active_from = tomorrow
        self.v.active_to = None
        self.v.save()

        folk10 = Variable.objects.get(pk=self.v.id)
        expectedVariableDict = {
            u"@id": u"Folk10",
            u"@type": [u"rdf:Property", u"qb:MeasureProperty"],
            u"comment": u"Antal bemannade servicesställen",
            u"range": u"xsd:integer",
            u"valid": u"name=Giltighetstid; start={};".format(tomorrow)
        }
        self.assertEqual(folk10.to_dict(), expectedVariableDict)

    def test_should_transform_date_ranged_object_to_dict(self):
        self.v.active_from = datetime(2010, 1, 1).date()
        self.v.active_to = datetime(2014, 12, 31)
        self.v.save()

        folk10 = Variable.objects.get(pk=self.v.id)
        expectedVariableDict = {
            u"@id": u"Folk10",
            u"@type": [u"rdf:Property", u"qb:MeasureProperty"],
            u"comment": u"Antal bemannade servicesställen",
            u"range": u"xsd:integer",
            u"valid": u"name=Giltighetstid; start=2010-01-01; end=2014-12-31;"
        }
        self.assertEqual(folk10.to_dict(), expectedVariableDict)

    def test_variable_should_have_question_and_question_part(self):
        folk35 = Variable.objects.get(pk=self.v2.id)
        self.assertTrue(hasattr(folk35,
                                "question") and folk35.question == u"Hur många årsverken utfördes av personal i folkbiblioteksverksamheten under 2012?")
        self.assertTrue(hasattr(folk35,
                                "question_part") and folk35.question_part == u"Antal årsverken övrig personal (ej städpersonal)")

    def test_summary_variable_without_question_or_question_part_is_summary_auto_field(self):
        folk31 = Variable.objects.get(pk=self.v3.id)
        self.assertTrue(folk31.is_summary_auto_field)
        # THis field is automatically summarized in survey_draft and the user cannot change the value

    def test_summary_variable_with_question_or_question_part_is_summary_field(self):
        folk69 = Variable.objects.get(pk=self.v4.id)
        self.assertFalse(folk69.is_summary_auto_field)
        # This field is automatically summarized in survey_draft, but value can be changed by user.
        # TODO: Maybe a is_summary_field helper property on model could for this state?

    def test_should_return_question_and_question_part_as_label_if_both_fields_exist(self):
        folk35 = Variable.objects.get(pk=self.v2.id)
        self.assertEquals(folk35.label, [folk35.question, folk35.question_part])

    def test_should_return_question_as_label_if_no_question_part(self):
        folk69 = Variable.objects.get(pk=self.v4.id)
        self.assertEquals(folk69.label, folk69.question)

    def test_should_return_description_as_label_if_no_question(self):
        folk31 = Variable.objects.get(pk=self.v3.id)
        self.assertEquals(folk31.label, folk31.description)

    def test_should_store_version_when_updating_existing_object(self):
        self.v.description = u"Totalt antal bemannade serviceställen, summering av antal filialer och huvudbibliotek"
        self.v.save()

        versions = VariableVersion.objects.all()
        self.assertEquals(len(versions), 1)
        self.assertEquals(versions[0].description, u"Antal bemannade servicesställen")

    def test_should_not_store_version_when_updating_draft(self):
        self.v4.description = u"En ny beskrivning"
        self.v4.save()

        versions = VariableVersion.objects.all()
        self.assertEquals(len(versions), 0)

    def test_should_set_modified_date_when_updating_existing_object(self):
        date_modified = self.v.date_modified
        self.v.description = u"Totalt antal bemannade serviceställen, summering av antal filialer och huvudbibliotek"
        self.v.save()

        updated = Variable.objects.get(pk=self.v.id)
        self.assertTrue(updated.date_modified > date_modified)

    def test_should_set_modified_date_when_updating_draft(self):
        date_modified = self.v4.date_modified
        self.v4.description = u"En ny beskrivning"
        self.v4.save()

        updated = Variable.objects.get(pk=self.v4.id)
        self.assertTrue(updated.date_modified > date_modified)

    def test_should_set_modified_date_when_creating_object(self):
        self.assertTrue(self.v.date_modified != None)

    def test_should_set_modified_date_when_creating_draft(self):
        self.assertTrue(self.v4.date_modified != None)

    def test_is_draft(self):
        self.assertFalse(self.v.is_draft)
        self.assertFalse(self.v2.is_draft)
        self.assertFalse(self.v3.is_draft)
        self.assertTrue(self.v4.is_draft)

    def test_is_active(self):
        self.assertTrue(self.v.is_active)
        self.assertFalse(self.v2.is_active)
        self.assertTrue(self.v3.is_active)
        self.assertFalse(self.v4.is_active)

    def test_active_variable_should_replace_other_variables(self):
        switchover_date = datetime(2014, 1, 1)
        self.v2.active_from = switchover_date  # TODO: Change to using self.active_from instead of switchover_date
        modified_siblings = self.v2.replace_siblings([self.v.id, self.v3.id], switchover_date=switchover_date.date(),
                                                     commit=True)
        self.assertEquals(set([v.id for v in modified_siblings]), set([self.v.id, self.v3.id]))

        replacement = Variable.objects.get(pk=self.v2.id)
        replaced_var_1 = Variable.objects.get(pk=self.v.id)
        replaced_var_2 = Variable.objects.get(pk=self.v3.id)

        # Replacement should have fields active_from and replaces set
        self.assertEquals(set([v.id for v in replacement.replaces]), set([self.v.id, self.v3.id]))
        self.assertEquals(replacement.active_from, switchover_date)

        # Replaced variables should have fields active_to and replaced_by set.
        self.assertEquals(replaced_var_1.replaced_by.id, self.v2.id)
        self.assertEquals(replaced_var_1.active_to, switchover_date)
        self.assertEquals(replaced_var_1.is_active, False)

        self.assertEquals(replaced_var_2.replaced_by.id, self.v2.id)
        self.assertEquals(replaced_var_2.active_to, switchover_date)
        self.assertEquals(replaced_var_2.is_active, False)

    def test_draft_variable_should_list_but_not_replace_other_variables(self):
        switchover_date = datetime(2014, 1, 1)
        modified_siblings = self.v4.replace_siblings([self.v2.id], switchover_date=switchover_date, commit=True)
        self.assertEquals(modified_siblings, [])

        replacement_var = Variable.objects.get(pk=self.v4.id)
        to_be_replaced = Variable.objects.get(pk=self.v2.id)
        self.assertEquals(set([v.id for v in replacement_var.replaces]), set([self.v2.id]))
        self.assertEquals(to_be_replaced.replaced_by, None)
        self.assertEquals(to_be_replaced.active_to, self.v2.active_to)
        self.assertEquals(to_be_replaced.is_active, False)

    def test_should_not_commit_replacement_unless_specified(self):
        modified_siblings = self.v2.replace_siblings([self.v.id])
        self.assertEquals(set([v.id for v in self.v2.replaces]), set([self.v.id]))
        self.assertEquals(set([v.id for v in modified_siblings]), set([self.v.id]))

        replacement_var = Variable.objects.get(pk=self.v2.id)
        replaced_var_1 = Variable.objects.get(pk=self.v.id)

        self.assertEquals(replacement_var.replaces, [])
        self.assertEquals(replaced_var_1.replaced_by, None)

    def test_should_raise_error_if_trying_to_replace_already_replaced_variable(self):
        self.v.replace_siblings([self.v2.id], commit=True)

        self.assertRaises(AttributeError, lambda: self.v3.replace_siblings([self.v2.id], commit=True))

        replacement = Variable.objects.get(pk=self.v.id)
        unsuccessful_replacement = Variable.objects.get(pk=self.v3.id)
        to_be_replaced = Variable.objects.get(pk=self.v2.id)
        self.assertEquals([v.id for v in replacement.replaces], [self.v2.id])
        self.assertEquals(unsuccessful_replacement.replaces, [])
        self.assertEquals(to_be_replaced.replaced_by.id, self.v.id)

    def test_raise_error_if_trying_to_replace_non_existing_variable(self):
        self.assertRaises(DoesNotExist,
                          lambda: self.v.replace_siblings([ObjectId("53fdec1ca9969003ec144d97")], commit=True))

    def test_should_update_replacements(self):
        self.v2.replace_siblings([self.v.id, self.v3.id], switchover_date=datetime(2014, 12, 31).date(), commit=True)
        replacement = Variable.objects.get(pk=self.v2.id)
        self.assertEquals(len(VariableVersion.objects.filter(key=self.v.key)), 1)

        # Should update v, add v4 and remove v3
        new_switchover_date = datetime(2015, 1, 1).date()
        replacement.replace_siblings([self.v.id, self.v4.id], switchover_date=new_switchover_date, commit=True)

        replacement = Variable.objects.get(pk=self.v2.id)
        modified_replaced = Variable.objects.get(pk=self.v.id)
        no_longer_replaced = Variable.objects.get(pk=self.v3.id)
        new_replaced = Variable.objects.get(pk=self.v4.id)

        # replacement should have updated list of variables (active_from is set outside of this mmethod)
        self.assertEquals(set([v.id for v in replacement.replaces]), set([modified_replaced.id, new_replaced.id]))

        # v should have updated active_to date
        self.assertEquals(modified_replaced.active_to.date(), new_switchover_date)
        self.assertEquals(modified_replaced.replaced_by.id, replacement.id)

        # v3 should no longer be replaced
        self.assertEquals(no_longer_replaced.replaced_by, None)
        self.assertEquals(no_longer_replaced.active_to, None)

        # v4 should be replaced
        self.assertEquals(new_replaced.replaced_by.id, replacement.id)
        self.assertEquals(new_replaced.active_to.date(), new_switchover_date)

    def test_should_update_replacements_for_draft(self):
        modified_siblings = self.v4.replace_siblings([self.v2.id], commit=True)
        after_setup = Variable.objects.get(pk=self.v4.id)

        after_setup.replace_siblings([self.v2.id, self.v3.id], commit=True)

        replacement_var = Variable.objects.get(pk=self.v4.id)

        self.assertEquals(set([v.id for v in replacement_var.replaces]), set([self.v2.id, self.v3.id]))
        self.assertEquals(Variable.objects.get(pk=self.v2.id).replaced_by, None)
        self.assertEquals(len(VariableVersion.objects.filter(key=self.v2.key)), 0)
        self.assertEquals(Variable.objects.get(pk=self.v3.id).replaced_by, None)
        self.assertEquals(len(VariableVersion.objects.filter(key=self.v3.key)), 0)

    def test_should_clear_all_replacements(self):
        # Setup
        replacement = self.v2
        replaced_1 = self.v
        replaced_2 = self.v3
        replacement.replace_siblings([replaced_1.id, replaced_2.id], commit=True)
        replacement.reload()
        replaced_1.reload()
        replaced_2.reload()

        # Clear replacements
        replacement.replace_siblings([], commit=True)

        self.assertEquals(replacement.reload().replaces, [])
        self.assertEquals(replaced_1.reload().replaced_by, None)
        self.assertEquals(replaced_2.reload().replaced_by, None)

    def test_should_clear_all_replacements_for_draft(self):
        # Setup
        replacement = self.v4
        replaced = self.v2
        replacement.replace_siblings([replaced.id], commit=True)
        replacement.reload()
        replaced.reload()

        # Clear replacements
        replacement.replace_siblings([], commit=True)

        self.assertEquals(replacement.reload().replaces, [])
        self.assertEquals(replaced.reload().replaced_by, None)
        self.assertEquals(len(VariableVersion.objects.filter(key=replaced.key)), 0)

    def test_should_nullify_active_to_and_references_to_replaced_by_when_deleting_replacement_instance(self):
        # Setup
        replacement = self.v2
        replaced_1 = self.v
        replaced_2 = self.v3
        replacement.replace_siblings([replaced_1.id, replaced_2.id], switchover_date=datetime(2015, 1, 1), commit=True)
        replacement.reload()

        replacement.delete()

        replaced_1.reload()
        self.assertEquals(replaced_1.replaced_by, None)
        self.assertEquals(replaced_1.active_to, None)
        replaced_2.reload()
        self.assertEquals(replaced_2.replaced_by, None)
        self.assertEquals(replaced_2.active_to, None)

    def test_should_nullify_reference_in_replaces_when_deleting_replaced_instance(self):
        # Setup
        replacement = self.v2
        replaced_1 = self.v
        replaced_2 = self.v3
        replacement.active_from = datetime(2015, 1, 1)
        replacement.replace_siblings([replaced_1.id, replaced_2.id], switchover_date=replacement.active_from,
                                     commit=True)

        replaced_2.reload().delete()

        self.assertEquals([v.id for v in replacement.reload().replaces], [replaced_1.id])
        replaced_1.reload()
        self.assertEquals(replaced_1.replaced_by.id, replacement.id)
        self.assertEquals(replaced_1.active_to, replacement.active_from)
