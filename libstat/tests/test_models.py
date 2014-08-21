# -*- coding: UTF-8 -*-
from libstat.tests import MongoTestCase
from libstat.models import *
from mongoengine.django.auth import User

from datetime import datetime, date, timedelta
import json
from django.conf import settings


"""
    Model class test cases
"""
class SurveyResponseTest(MongoTestCase):
    def setUp(self):
        self.current_user = User.objects.filter(username="admin")[0]

        v1 = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer", is_public=True, target_groups=["public"])
        v1.save()
        v2 = Variable(key=u"folk6", description=u"Är huvudbiblioteket i er kommun integrerat med ett skolbibliotek? 1=ja", type="boolean", is_public=True, target_groups=["public"])
        v2.save()
        v3 = Variable(key=u"folk8", description=u"Textkommentar", type="string", is_public=False, target_groups=["public"])
        v3.save()
        
        sr = SurveyResponse(library_name="KARLSTAD STADSBIBLIOTEK", sample_year=2013, target_group="public", observations=[], created_by=self.current_user)
        sr.library = Library(bibdb_id=u"323", bibdb_sigel="Kld1", bibdb_name=u"Karlstad stadsbibliotek")
        sr.observations.append(SurveyObservation(variable=v1, value=7, _source_key="folk5", _is_public=v1.is_public))
        sr.observations.append(SurveyObservation(variable=v2, value=None, _source_key="folk6", _is_public=v2.is_public))
        sr.observations.append(SurveyObservation(variable=v3, value=u"Här är en kommentar", _source_key="folk8", _is_public=v3.is_public))
        self.survey_response = sr.save()
    
    
    def test_should_export_public_non_null_observations_to_openData(self):
        self.survey_response.publish(user=self.current_user)
        
        data = OpenData.objects.all()
        self.assertEquals(len(data), 1)
        
        open_data = data.get(0)
        self.assertEquals(open_data.library_name, "KARLSTAD STADSBIBLIOTEK")
        self.assertEquals(open_data.library_id, "323")
        self.assertEquals(open_data.sample_year, 2013)
        self.assertEquals(open_data.variable.key, "folk5")
        self.assertEquals(open_data.target_group, "public")
        self.assertEquals(open_data.value, 7)
        self.assertTrue(open_data.date_modified)
        self.assertTrue(open_data.date_created)
        self.assertEquals(open_data.date_created, open_data.date_modified)
        
        sr = SurveyResponse.objects.get(pk=self.survey_response.id)
        self.assertEquals(open_data.date_created, sr.published_at)
        self.assertEquals(sr.published_by, self.current_user)
        
    
    def test_should_overwrite_value_and_date_modified_for_existing_openData(self):
        self.survey_response.publish(user=self.current_user)

        for obs in self.survey_response.observations:
            if obs.variable.key == "folk5":
                obs.value = 9
        self.survey_response.save()
        self.survey_response.publish(user=self.current_user)
        
        data = OpenData.objects.all()
        self.assertEquals(len(data), 1)
        
        open_data = data.get(0)
        self.assertEquals(open_data.library_name, "KARLSTAD STADSBIBLIOTEK")
        self.assertEquals(open_data.library_id, "323")
        self.assertEquals(open_data.sample_year, 2013)
        self.assertEquals(open_data.variable.key, "folk5")
        self.assertEquals(open_data.target_group, "public")
        self.assertEquals(open_data.value, 9)
        self.assertTrue(open_data.date_modified)
        self.assertTrue(open_data.date_created)
        self.assertNotEquals(open_data.date_created, open_data.date_modified)
        
        
    def test_should_get_observation_by_variable_key(self):
        self.assertEquals(self.survey_response.observation_by_key("folk8").value, u"Här är en kommentar")
        
        
    def test_should_store_version_when_updating_existing_object(self):
        sr = self.survey_response
        sr.library_name = u"Karlstad"
        
        sr.metadata = SurveyResponseMetadata(municipality_name=u"Karlstad kommun", 
                                                               municipality_code=u"1780", 
                                                               responent_name=u"Karl Karlsson", 
                                                               respondent_email=u"karl.karlsson@karlstad.se", 
                                                               respondent_phone=u"054-540 23 72")
        sr.library.bibdb_id = u"276"
        self.survey_response = sr.save()
        
        self.assertEquals(self.survey_response.library_name, u"Karlstad")
        
        versions = SurveyResponseVersion.objects.filter(survey_response_id=self.survey_response.id)
        self.assertEquals(len(versions), 1)
        self.assertEquals(versions[0].survey_response_id, self.survey_response.id)
        # Version should contain values before update
        self.assertEquals(versions[0].library_name, u"KARLSTAD STADSBIBLIOTEK")
        self.assertEquals(versions[0].metadata, None)
        self.assertEquals(versions[0].library.bibdb_id, u"323")
        
    def test_should_store_one_version_for_each_change(self):
        self.survey_response.library.bibdb_id = u"321"
        self.survey_response.save()
        self.assertEquals(len(SurveyResponseVersion.objects.filter(survey_response_id=self.survey_response.id)), 1)
        
        self.survey_response.library.bibdb_id = u"197"
        self.survey_response.save()
        self.assertEquals(len(SurveyResponseVersion.objects.filter(survey_response_id=self.survey_response.id)), 2)
        
    def test_should_store_version_when_updating_observations_for_existing_objects(self):
        self.survey_response.observation_by_key(u"folk5").value = 5
        self.survey_response.save()
        
        updated_sr = SurveyResponse.objects.get(pk=self.survey_response.id)
        self.assertEquals(updated_sr.observation_by_key(u"folk5").value, 5)
        
        versions = SurveyResponseVersion.objects.filter(survey_response_id=self.survey_response.id)
        self.assertEquals(len(versions), 1)
        self.assertEquals(versions[0].observation_by_key(u"folk5").value, 7)
    
    def test_should_not_store_version_when_creating_object(self):
        sr = SurveyResponse(library_name=u"Some name", sample_year=2014, target_group=u"research", observations=[])
        sr.save()
        
        versions = SurveyResponseVersion.objects.filter(survey_response_id=self.survey_response.id)
        self.assertEquals(len(versions), 0)
        
    def test_should_set_modified_date_when_updating_existing_object(self):
        self.survey_response.library_name = u"Stadsbiblioteket i Karlstad"
        self.survey_response.save()

        versions = SurveyResponseVersion.objects.filter(survey_response_id=self.survey_response.id)
        self.assertEquals(len(versions), 1)
        
        sr = SurveyResponse.objects.get(pk=self.survey_response.id)
        self.assertTrue(sr.date_modified > versions[0].date_modified)
        
        
    def test_should_set_modified_date_when_creating_object(self):
        self.assertEquals(self.survey_response.date_modified, self.survey_response.date_created)
        self.assertEquals(self.survey_response.modified_by, self.current_user)
        
        
    def test_should_set_published_date_but_not_modified_date_when_publishing(self):
        self.assertTrue(self.survey_response.published_at == None)
        date_modified = self.survey_response.date_modified
        
        self.survey_response.publish(user=self.current_user)
        
        self.assertTrue(self.survey_response.published_at != None)
        self.assertTrue(self.survey_response.published_by, self.current_user)
        self.assertEquals(self.survey_response.date_modified, date_modified)
        
    def test_latest_version_published(self):
        self.survey_response.published_at = self.survey_response.date_modified + timedelta(hours=-1)
        self.assertFalse(self.survey_response.latest_version_published)
        
        self.survey_response.published_at = self.survey_response.date_modified
        self.assertTrue(self.survey_response.latest_version_published)
        
    def test_is_published(self):
        self.assertFalse(self.survey_response.is_published)
        
        self.survey_response.published_at = self.survey_response.date_modified
        self.assertTrue(self.survey_response.is_published)
        

    
class OpenDataTest(MongoTestCase):
    def setUp(self):
        v = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer", is_public=True, target_groups=["public"])
        v.save()
        publishing_date = datetime(2014, 06, 03, 15, 28, 31)
        d1 = OpenData(library_name=u"KARLSTAD STADSBIBLIOTEK", library_id=u"323", sample_year=2013, target_group="public", variable=v, value=6, date_created=publishing_date, date_modified=publishing_date)
        d1.save()
        d2 = OpenData(library_name=u"NORRBOTTENS LÄNSBIBLIOTEK", sample_year=2013, target_group="public", variable=v, value=6, date_created=publishing_date, date_modified=publishing_date)
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
       
       
class VariableTest(MongoTestCase):
    def setUp(self):
        self.v = Variable(key=u"Folk10", description=u"Antal bemannade servicesställen", type="integer", is_public=True, target_groups=["public"])
        self.v.save()
        
        self.v2 = Variable(key=u"Folk35", description=u"Antal årsverken övrig personal", type="decimal", is_public=True, target_groups=["public"])
        self.v2.question = u"Hur många årsverken utfördes av personal i folkbiblioteksverksamheten under 2012?"
        self.v2.question_part = u"Antal årsverken övrig personal (ej städpersonal)"
        self.v2.save()
        
        self.v3 = Variable(key=u"Folk31", description=u"Antal årsverken totalt", type="decimal", is_public=True, target_groups=["public"])
        self.v3.summary_of = [self.v2]
        self.v3.save()
        
        self.v4 = Variable(key=u"Folk69", description=u"Totalt nyförvärv AV-medier", type="integer", is_public=True, target_groups=["public"])
        self.v4.question = u"Hur många nyförvärv av AV-media gjordes under 2012?"
        self.v4.save()
        
    
    def test_should_transform_object_to_dict(self):
        folk10 = Variable.objects.get(pk=self.v.id)
        expectedVariableDict = {
            u"@id": u"Folk10",
            u"@type": [u"rdf:Property", u"qb:MeasureProperty"],
            u"comment": u"Antal bemannade servicesställen",
            u"range": u"xsd:integer"
        }
        self.assertEqual(folk10.to_dict(), expectedVariableDict)
    
    def test_variable_should_have_question_and_question_part(self):
        folk35 = Variable.objects.get(pk=self.v2.id)
        self.assertTrue(hasattr(folk35, "question") and folk35.question == u"Hur många årsverken utfördes av personal i folkbiblioteksverksamheten under 2012?")
        self.assertTrue(hasattr(folk35, "question_part") and folk35.question_part == u"Antal årsverken övrig personal (ej städpersonal)")
        
    def test_summary_variable_without_question_or_question_part_is_summary_auto_field(self):
        folk31 = Variable.objects.get(pk=self.v3.id)
        self.assertTrue(folk31.is_summary_auto_field)
        # THis field is automatically summarized in survey and the user cannot change the value
        
    def test_summary_variable_with_question_or_question_part_is_summary_field(self):
        folk69 = Variable.objects.get(pk=self.v4.id)
        self.assertFalse(folk69.is_summary_auto_field)
        # This field is automatically summarized in survey, but value can be changed by user.
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
        
    def test_should_set_modified_date_when_updating_existing_object(self):
        date_modified = self.v.date_modified
        self.v.description = u"Totalt antal bemannade serviceställen, summering av antal filialer och huvudbibliotek"
        self.v.save()
        
        updated = Variable.objects.get(pk=self.v.id)
        self.assertTrue(updated.date_modified > date_modified)
        
    def test_should_set_modified_date_when_creating_object(self):
        self.assertTrue(self.v.date_modified != None)
        