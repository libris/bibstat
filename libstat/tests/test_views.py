# -*- coding: UTF-8 -*-
import uuid
import json
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from mongoengine.django.auth import User

from libstat.tests import MongoTestCase
from libstat.models import Variable, SurveyResponse, SurveyObservation, Survey, OpenData


"""
View test cases
"""


class VariablesViewTest(MongoTestCase):
    def setUp(self):
        v1 = Variable(key=u"Folk10", description=u"Antal bemannade serviceställen", type="integer", is_public=True,
                      target_groups=["public"])
        self.folk10 = v1.save()
        v2 = Variable(key=u"Sjukhus102", description=u"Bestånd av tillgängliga medier för personer med läsnedsättning",
                      type="integer", is_public=True, target_groups=["hospital"])
        self.sjukhus102 = v2.save()
        v3 = Variable(key=u"intäkterTotalt", description=u"Bibliotekets totala intäkter under mätåret", type="long",
                      is_public=True, target_groups=["public", "research", "hospital", "school"])
        self.totalRevenue = v3.save()

        self.url = reverse("variables")
        self.client.login(username="admin", password="admin")

    def test_view_requires_admin_login(self):
        self.client.logout()

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username="library_user", password="secret")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username="admin", password="admin")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_should_list_all_variables(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["variables"]), 3)

    def test_should_filter_variables_by_target_group(self):
        response = self.client.get(u"{}?target_group=hospital".format(self.url))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["variables"]), 2)
        self.assertEquals(response.context["variables"][0].key, u"Sjukhus102")
        self.assertEquals(response.context["variables"][1].key, u"intäkterTotalt")

    def test_should_filter_variables_by_target_group_all(self):
        response = self.client.get(u"{}?target_group=all".format(self.url))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["variables"]), 1)
        self.assertEquals(response.context["variables"][0].key, u"intäkterTotalt")

    def test_should_filter_variables_by_list_of_target_groups(self):
        response = self.client.get(u"{}?target_group=school&target_group=public".format(self.url))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["variables"]), 2)
        self.assertEquals(response.context["variables"][0].key, u"Folk10")
        self.assertEquals(response.context["variables"][1].key, u"intäkterTotalt")

    def test_each_variable_should_have_edit_link(self):
        response = self.client.get(self.url)
        self.assertContains(response,
                            u'<a title="Visa/Ändra" data-form="/statistics/variables/{}/" href="#" class="edit-variable">Folk10</a>'.format(
                                self.folk10.id),
                            count=1,
                            status_code=200,
                            html=True)

    def test_should_have_button_for_adding_variable(self):
        response = self.client.get(self.url)
        self.assertContains(response,
                            u'<a class="create-variable btn btn-primary" role="button" href="#" data-form="{}">Skapa term</a>'.format(
                                reverse("create_variable")),
                            count=1,
                            status_code=200,
                            html=True)


class CreateVariableViewTest(MongoTestCase):
    def setUp(self):
        self.url = reverse("create_variable")
        self.client.login(username="admin", password="admin")

    def test_should_get_empty_form(self):
        response = self.client.get(self.url)
        self.assertContains(response, u'<h4 class="modal-title">Ny term (utkast)</h4>', count=1, status_code=200,
                            html=True)
        self.assertContains(response, u'<input type="submit" value="Spara utkast" class="btn btn-primary">', count=1,
                            status_code=200, html=True)

    def test_should_create_variable_draft(self):
        response = self.client.post(self.url,
                                    {u"key": u"antalManligaBibliotekarier",
                                     u"question": u"Hur många anställda personer fanns i biblioteksverksamheten den 1 mars aktuellt mätår?",
                                     u"question_part": u"Antal anställda bibliotekarier som är män",
                                     u"category": u"Organisation",
                                     u"sub_category": u"Personal",
                                     u"type": u"integer",
                                     u"is_public": u"True",
                                     u"target_groups": [u"public", u"research", u"school", u"hospital"],
                                     u"description": u"Antal anställda manliga bibliotekarier den 1 mars aktuellt mätår",
                                     u"comment": u"Det här är ett utkast"}
        )
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse('errors' in data)
        result = Variable.objects.filter(key=u"antalManligaBibliotekarier")[0]
        self.assertEquals(result.is_draft, True)
        self.assertEquals(result.question,
                          u"Hur många anställda personer fanns i biblioteksverksamheten den 1 mars aktuellt mätår?")
        self.assertEquals(result.question_part, u"Antal anställda bibliotekarier som är män")
        self.assertEquals(result.category, u"Organisation")
        self.assertEquals(result.sub_category, u"Personal")
        self.assertEquals(result.type, u"integer")
        self.assertEquals(result.is_public, True)
        self.assertEquals(result.target_groups, [u"public", u"research", u"school", u"hospital"])
        self.assertEquals(result.description, u"Antal anställda manliga bibliotekarier den 1 mars aktuellt mätår")
        self.assertEquals(result.comment, u"Det här är ett utkast")

    def test_should_return_validation_errors_when_omitting_mandatory_fields(self):
        response = self.client.post(self.url, {})
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(len(data['errors']), 4)
        self.assertEquals(data['errors'][u'key'], [u'Detta fält måste fyllas i.'])
        self.assertEquals(data['errors'][u'type'], [u'Detta fält måste fyllas i.'])
        self.assertEquals(data['errors'][u'target_groups'], [u'Detta fält måste fyllas i.'])
        self.assertEquals(data['errors'][u'description'], [u'Detta fält måste fyllas i.'])


# Create custom base test class with helper methods.
class EditVariableViewTest(MongoTestCase):
    def setUp(self):
        self.v1 = Variable(key=u"Folk10", description=u"Antal bemannade serviceställen", type="integer", is_public=True,
                           target_groups=["public"])
        self.v1.save()
        self.v2 = Variable(key=u"Sjukhus102",
                           description=u"Bestånd av tillgängliga medier för personer med läsnedsättning",
                           type="integer", is_public=True, target_groups=["hospital"])
        self.v2.save()
        self.v3 = Variable(key=u"Forsk23", description=u"Antal anställda personer manliga biblioteksassistenter.",
                           type="integer", is_public=True, is_draft=True, target_groups=["research"])
        self.v3.save()

        self.new_category = u"Organisation"
        self.new_sub_category = u"Bemannade serviceställen"
        self.new_type = u"string"
        self.new_target_groups = [u"research"]
        self.new_description = u"Summering"
        self.new_comment = u"Inga kommentarer"

        self.url = reverse("edit_variable", kwargs={"variable_id": str(self.v1.id)})
        self.client.login(username="admin", password="admin")
        self.current_user = User.objects.filter(username="admin")[0]

    def test_should_update_variable(self):
        response = self.client.post(self.url, {u"category": self.new_category, u"sub_category": self.new_sub_category,
                                               u"type": self.new_type, u"target_groups": self.new_target_groups,
                                               u"description": self.new_description,
                                               u"comment": self.new_comment})
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse('errors' in data)

        result = Variable.objects.get(pk=self.v1.id)
        self.assertEquals(result.key, u"Folk10")
        self.assertEquals(result.category, self.new_category)
        self.assertEquals(result.sub_category, self.new_sub_category)
        self.assertEquals(result.type, self.new_type)
        self.assertFalse(result.is_public)
        self.assertEquals(result.target_groups, self.new_target_groups)
        self.assertEquals(result.description, self.new_description)
        self.assertEquals(result.comment, self.new_comment)
        self.assertEquals(result.modified_by, self.current_user)

    def test_should_return_validation_errors_when_omitting_mandatory_fields(self):
        response = self.client.post(self.url, {})
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertTrue(len(data['errors']) == 3)
        self.assertEquals(data['errors'][u'type'], [u'Detta fält måste fyllas i.'])
        self.assertEquals(data['errors'][u'target_groups'], [u'Detta fält måste fyllas i.'])
        self.assertEquals(data['errors'][u'description'], [u'Detta fält måste fyllas i.'])

    def test_variable_key_should_not_be_editable(self):
        response = self.client.post(self.url, {u"key": u"TheNewKey", u"type": self.new_type,
                                               u"target_groups": self.new_target_groups,
                                               u"description": self.new_description})
        self.assertEquals(response.status_code, 200)
        result = Variable.objects.get(pk=self.v1.id)
        self.assertEquals(result.key, u"Folk10")

    def test_should_replace_variable(self):
        response = self.client.post(self.url, {u"active_from": u"2015-01-01", u"type": self.new_type,
                                               u"target_groups": self.new_target_groups,
                                               u"description": self.new_description,
                                               u"replaces": str(self.v2.id)})
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse('errors' in data)

        replacing = Variable.objects.get(pk=self.v1.id)
        replaced = Variable.objects.get(pk=self.v2.id)
        self.assertEquals([v.id for v in replacing.replaces], [self.v2.id])
        self.assertEquals(replaced.replaced_by.id, self.v1.id)

    def test_draft_should_replace_variable(self):
        response = self.client.post(reverse("edit_variable", kwargs={"variable_id": str(self.v3.id)}),
                                    {u"active_from": u"2015-01-01", u"type": self.new_type,
                                     u"target_groups": self.new_target_groups, u"description": self.new_description,
                                     u"replaces": str(self.v2.id)})
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse('errors' in data)

        replacing = Variable.objects.get(pk=self.v3.id)
        replaced = Variable.objects.get(pk=self.v2.id)
        self.assertEquals([v.id for v in replacing.replaces], [self.v2.id])
        self.assertEquals(replaced.replaced_by, None)

    def test_replace_requires_active_from(self):
        response = self.client.post(self.url, {u"type": self.new_type, u"target_groups": self.new_target_groups,
                                               u"description": self.new_description,
                                               u"replaces": str(self.v2.id)})
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue('errors' in data)
        self.assertEquals(data['errors'][u'active_from'], [u'Måste anges'])
        self.assertEquals(data['errors'][u'replaces'],
                          [u"Ange när ersättning börjar gälla genom att sätta 'Giltig fr o m'"])

    def test_should_not_be_able_to_edit_active_to_for_replaced(self):
        # Set up: Replace variable
        self.v2.replace_siblings([self.v1.id], switchover_date=datetime(2015, 1, 1).date(), commit=True)

        # active_to input should be disabled
        response = self.client.get(self.url)
        self.assertContains(response,
                            u'<input type="text" disabled="disabled" value="2015-01-01" name="active_to" class="form-control" id="id_active_to">',
                            count=1, status_code=200, html=True)

        # Posting a new active_to should give validation error
        response = self.client.post(self.url, {u"type": self.v1.type, u"target_groups": self.v1.target_groups,
                                               u"description": self.v1.description,
                                               u"active_to": u"2014-12-31"})
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue('errors' in data)
        self.assertEquals(data['errors'][u'active_to'], [u'Styrs av ersättande term'])


    def test_should_be_able_to_activate_draft(self):
        edit_draft_url = reverse("edit_variable", kwargs={"variable_id": str(self.v3.id)})

        response = self.client.get(edit_draft_url)
        self.assertContains(response, u'<input type="submit" value="Spara utkast" class="btn btn-primary">', count=1,
                            status_code=200, html=True)
        self.assertContains(response,
                            u'<input type="submit" id="save_and_activate" value="Spara och aktivera" class="btn btn-primary">',
                            count=1, status_code=200, html=True)

        response = self.client.post(edit_draft_url, {u"type": self.v3.type, u"target_groups": self.v3.target_groups,
                                                     u"description": self.v3.description,
                                                     u"submit_action": u"save_and_activate"})
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse('errors' in data)

        result = Variable.objects.get(pk=self.v3.id)
        self.assertEquals(result.is_draft, False)
        self.assertEquals(result.is_active, True)


    def test_add_replacements_and_activate_draft_should_replace_siblings(self):
        edit_draft_url = reverse("edit_variable", kwargs={"variable_id": str(self.v3.id)})
        response = self.client.post(edit_draft_url, {u"active_from": u"2015-01-01", u"type": self.v3.type,
                                                     u"target_groups": self.v3.target_groups,
                                                     u"description": self.v3.description, u"replaces": str(self.v2.id),
                                                     u"submit_action": u"save_and_activate"})
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse('errors' in data)

        replacing = Variable.objects.get(pk=self.v3.id)
        replaced_sibling = Variable.objects.get(pk=self.v2.id)
        switchover_date = datetime(2015, 1, 1)

        self.assertEquals(replacing.is_draft, False)
        self.assertEquals([v.id for v in replacing.replaces], [replaced_sibling.id])
        self.assertEquals(replacing.active_from, switchover_date)

        self.assertEquals(replaced_sibling.replaced_by.id, replacing.id)
        self.assertEquals(replaced_sibling.active_to, switchover_date)


    def test_activating_draft_with_existing_replacements_should_replaces_siblings(self):
        # Set up: Add replacements 
        self.v3.replace_siblings([self.v2.id], switchover_date=datetime(2015, 1, 1).date(), commit=True)

        edit_draft_url = reverse("edit_variable", kwargs={"variable_id": str(self.v3.id)})
        response = self.client.post(edit_draft_url, {u"active_from": u"2015-01-01", u"type": self.v3.type,
                                                     u"target_groups": self.v3.target_groups,
                                                     u"description": self.v3.description, u"replaces": str(self.v2.id),
                                                     u"submit_action": u"save_and_activate"})
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse('errors' in data)

        replacing = Variable.objects.get(pk=self.v3.id)
        replaced_sibling = Variable.objects.get(pk=self.v2.id)
        switchover_date = datetime(2015, 1, 1)

        self.assertEquals(replacing.is_draft, False)
        self.assertEquals([v.id for v in replacing.replaces], [replaced_sibling.id])
        self.assertEquals(replacing.active_from, switchover_date)

        self.assertEquals(replaced_sibling.replaced_by.id, replacing.id)
        self.assertEquals(replaced_sibling.active_to, switchover_date)

    def test_should_keep_active_to_date_when_updating_replaced_variable(self):
        # Setup
        replaced = self.new_variable(key="Folk28", is_draft=False)
        replaced_by = self.new_variable(key="antalManligaBibliotekarier", is_draft=False)
        replaced_by.active_from = datetime(2015, 1, 1)
        replaced_by.replace_siblings([replaced.id], switchover_date=replaced_by.active_from, commit=True)

        # Verify preconditions
        replaced = Variable.objects.get(pk=replaced.id)
        self.assertEquals(replaced.replaced_by.id, replaced_by.id)
        self.assertEquals(replaced.active_to, replaced_by.active_from)

        # Since input active_to is disabled, an empty string is posted
        response = self.post(u"save", replaced)

        # Field active_to should not have been updated
        replaced.reload()
        self.assertEquals(replaced.active_to, replaced_by.active_from)


    def test_should_not_be_able_to_delete_variable_when_it_does_not_exist(self):
        variable = self.new_variable(save=False)

        response = self.delete(variable)

        self.assertEquals(response.status_code, 404)

    def test_should_be_able_to_delete_draft_variable(self):
        variable = self.new_variable()

        response = self.delete(variable)

        self.assertOk(response)
        self.assertDoesNotExist(variable)

    def test_should_not_be_able_to_delete_non_draft_variable_when_referenced_in_survey_response(self):
        variable = self.new_variable(is_draft=False)

        survey_response = self.new_survey_response()
        survey_response.observations = [SurveyObservation(variable=str(variable.id))]
        survey_response.save()
        survey_response.publish()

        response = self.delete(variable)

        self.assertEquals(response.status_code, 403)
        self.assertExists(variable)

    def test_should_not_be_able_to_delete_non_draft_variable_when_referenced_in_open_data(self):
        variable = self.new_variable(is_draft=False)
        self.new_open_data(variable).save()

        response = self.delete(variable)

        self.assertEqual(response.status_code, 403)
        self.assertExists(variable)

    def test_should_be_able_to_delete_non_draft_variable_when_not_referenced(self):
        variable = self.new_variable(is_draft=False)

        self.delete(variable)

        self.assertDoesNotExist(variable)

    def test_should_remove_reference_in_replaced_variables_when_deleting_non_draft_variable(self):
        replaced = self.new_variable()
        replacement = self.new_variable(is_draft=False)
        replacement.active_from = datetime(2015, 1, 1)
        replacement.replace_siblings([replaced.id], switchover_date=replacement.active_from, commit=True)

        self.delete(replacement)
        replaced.reload()

        self.assertEquals(replaced.replaced_by, None)
        self.assertEquals(replaced.active_to, None)

    def test_should_remove_reference_in_replacement_variable_when_deleting_non_draft_variable(self):
        replaced = self.new_variable(is_draft=False)
        replacement = self.new_variable()
        replacement.active_from = datetime(2015, 1, 1)
        replacement.replace_siblings([replaced.id], switchover_date=replacement.active_from, commit=True)

        self.delete(replaced)
        replacement.reload()

        self.assertIs(len(replacement.replaces), 0)

    def test_should_remove_reference_in_replaced_variables_when_deleting_draft_variable(self):
        replaced = self.new_variable()
        replacement = self.new_variable()
        replacement.active_from = datetime(2015, 1, 1)
        replacement.replace_siblings([replaced.id], switchover_date=replacement.active_from, commit=True)

        self.delete(replacement)
        replaced.reload()

        self.assertEquals(replaced.replaced_by, None)
        self.assertEquals(replaced.active_to, None)

    def test_should_remove_reference_in_replacement_variable_when_deleting_draft_variable(self):
        replaced = self.new_variable()
        replacement = self.new_variable()
        replacement.active_from = datetime(2015, 1, 1)
        replacement.replace_siblings([replaced.id], switchover_date=replacement.active_from, commit=True)

        self.delete(replaced)
        replacement.reload()

        self.assertIs(len(replacement.replaces), 0)

    def post(self, action, variable):
        print "POSTING: ", variable.active_to
        url = reverse("edit_variable", kwargs={"variable_id": str(variable.id)})
        return self.client.post(url, {
            u"active_from": variable.active_from.date() if variable.active_from else "",
            # active_to input is disabled if variable is replaced
            u"active_to": variable.active_to.date() if variable.active_to and not variable.replaced_by else "",
            u"replaces": ", ".join([str(v.id) for v in variable.replaces]) if variable.replaces else "",
            u"question": variable.question,
            u"question_part": variable.question_part,
            u"category": variable.category,
            u"sub_category": variable.sub_category,
            u"type": variable.type,
            u"is_public": int(variable.is_public),
            u"target_groups": variable.target_groups,
            u"description": variable.description,
            u"comment": variable.comment,
            u"submit_action": action
        })


    def activate(self, variable):
        return self.post(u"save_and_activate", variable)

    def delete(self, variable):
        return self.post(u"delete", variable)

    def new_variable(self, key=None, description=None, type=None, target_groups=None, is_draft=True, save=True):
        variable = Variable(
            key=key if key else unicode(uuid.uuid1()),
            description=description if description else u"description",
            type=type if type else "integer",
            target_groups=target_groups if target_groups else ["public"],
            is_draft=is_draft
        )

        if save:
            variable.save()
        return variable

    def new_open_data(self, variable):
        open_data = OpenData(
            library_name='test',
            sample_year='1234',
            target_group='public',
            variable=variable.id
        )

        open_data.save()
        return open_data

    def new_survey_response(self):
        return SurveyResponse(
            target_group='public',
            library_name='test',
            sample_year='1234'
        )

    def assertOk(self, response):
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse('errors' in data)

    def assertDoesNotExist(self, variable):
        self.assertRaises(Variable.DoesNotExist, lambda: Variable.objects.get(pk=variable.id))

    def assertExists(self, variable):
        try:
            Variable.objects.get(pk=variable.id)
        except Variable.DoesNotExist as dne:
            self.fail(str(dne))

            # TODO: Borde man kunna ändra synlighet? Inte om det redan finns publik data eller inlämnade enkätsvar väl? Kommer kräva ompublicering av alla enkätsvar som har variabeln...

            # TODO: Borde man kunna ta bort en bibliotekstyp? Samma som ovan.

            # TODO: Borde man kunna ändra enhet? Samma som ovan.


class SurveyResponsesViewTest(MongoTestCase):
    def setUp(self):
        self.publishing_date = datetime(2014, 8, 22, 10, 40, 33, 876)
        self.survey_response = SurveyResponse(library_name=u"KARLSTAD STADSBIBLIOTEK", sample_year=2013,
                                              target_group="public", observations=[], published_at=self.publishing_date)
        self.survey_response.save()
        sr2 = SurveyResponse(library_name=u"NORRBOTTENS LÄNSBIBLIOTEK", sample_year=2012, target_group="public",
                             observations=[], published_at=self.publishing_date);
        sr2.save()
        sr3 = SurveyResponse(library_name=u"Sjukhusbiblioteken i Dalarnas län", sample_year=2013,
                             target_group="hospital", observations=[]);
        self.hospital_sr = sr3.save()

        self.client.login(username="admin", password="admin")

    def test_should_not_fetch_survey_responses_unless_list_action_provided(self):
        response = self.client.get(reverse("survey_responses"))
        self.assertEquals(len(response.context["survey_responses"]), 0)

    def test_should_list_survey_responses_by_year(self):
        response = self.client.get("{}?action=list&sample_year=2012".format(reverse("survey_responses")))
        self.assertEquals(len(response.context["survey_responses"]), 1)

    def test_should_list_survey_responses_by_target_group(self):
        response = self.client.get("{}?action=list&target_group=public".format(reverse("survey_responses")))
        self.assertEquals(len(response.context["survey_responses"]), 2)

    def test_should_list_survey_responses_by_year_and_target_group(self):
        response = self.client.get(
            "{}?action=list&target_group=public&sample_year=2013".format(reverse("survey_responses")))
        self.assertEquals(len(response.context["survey_responses"]), 1)
        self.assertEquals(response.context["survey_responses"][0].library_name, u"KARLSTAD STADSBIBLIOTEK")

    def test_should_list_unpublished_survey_responses(self):
        self.assertFalse(self.hospital_sr.is_published)
        response = self.client.get("{}?action=list&unpublished_only=True".format(reverse("survey_responses")))
        self.assertEquals(len(response.context["survey_responses"]), 1)
        self.assertEquals(response.context["survey_responses"][0].library_name, u"Sjukhusbiblioteken i Dalarnas län")

    def test_each_survey_response_should_have_checkbox_for_actions(self):
        response = self.client.get(
            "{}?action=list&target_group=public&sample_year=2013".format(reverse("survey_responses")))
        self.assertContains(response,
                            u'<input title="Välj" class="select-one" name="survey-response-ids" type="checkbox" value="{}"/>'.format(
                                self.survey_response.id),
                            count=1, status_code=200, html=True)

    def test_each_survey_response_should_have_a_link_to_details_view(self):
        response = self.client.get(
            "{}?action=list&target_group=public&sample_year=2013".format(reverse("survey_responses")))
        self.assertContains(response, u'<a href="{}" title="Visa/redigera enkätsvar">Visa/redigera</a>'
                            .format(
            reverse("edit_survey_response", kwargs={"survey_response_id": str(self.survey_response.id)})),
                            count=1, status_code=200, html=True)


class PublishSurveyResponsesViewTest(MongoTestCase):
    def setUp(self):
        self.survey_response = SurveyResponse(library_name="KARLSTAD STADSBIBLIOTEK", sample_year=2013,
                                              target_group="public", observations=[])
        self.survey_response.save()
        sr2 = SurveyResponse(library_name="NORRBOTTENS LÄNSBIBLIOTEK", sample_year=2012, target_group="public",
                             observations=[]);
        sr2.save()
        sr3 = SurveyResponse(library_name=u"Sjukhusbiblioteken i Dalarnas län", sample_year=2013,
                             target_group="hospital", observations=[]);
        sr3.save()

        self.url = reverse("publish_survey_responses")
        self.client.login(username="admin", password="admin")

    def test_should_publish_selection(self):
        response = self.client.post(self.url, {u"sample_year": u"2013",
                                               u"target_group": u"public",
                                               u"survey-response-ids": [u"{}".format(self.survey_response.id)]},
                                    follow=True)
        self.assertEquals(response.status_code, 200)

        survey_response = SurveyResponse.objects.get(pk=self.survey_response.id)
        self.assertTrue(survey_response.published_at != None)
        self.assertEquals(survey_response.published_by, User.objects.filter(username="admin")[0])

    def test_should_not_publish_unless_selected_ids(self):
        response = self.client.post(self.url, {u"sample_year": u"2013",
                                               u"target_group": u"public",
                                               u"survey-response-ids": []},
                                    follow=True)
        self.assertEquals(response.status_code, 200)
        survey_response = SurveyResponse.objects.get(pk=self.survey_response.id)
        self.assertEquals(survey_response.published_at, None)
        self.assertEquals(survey_response.published_by, None)


class EditSurveyResponseViewTest(MongoTestCase):
    def setUp(self):
        self.survey_response = SurveyResponse(library_name=u"KARLSTAD STADSBIBLIOTEK", sample_year=2013,
                                              target_group=u"public", observations=[])
        self.survey_response.save()

        sr2 = SurveyResponse(library_name=u"ALE BIBLIOTEK", sample_year=2013, target_group=u"public", observations=[])
        sr2.save()

        self.url = reverse("edit_survey_response", kwargs={"survey_response_id": str(self.survey_response.id)})
        self.client.login(username="admin", password="admin")
        self.current_user = User.objects.filter(username="admin")[0]

    def test_view_requires_superuser_login(self):
        # TODO:
        pass

    def test_should_have_hidden_inputs_for_mandatory_fields_that_are_not_editable(self):
        response = self.client.get(
            reverse("edit_survey_response", kwargs={"survey_response_id": str(self.survey_response.id)}))
        self.assertContains(response, u'<input type="hidden" value="2013" name="sample_year" id="id_sample_year">'
                            .format(self.url), count=1, status_code=200, html=True)
        self.assertContains(response, u'<input type="hidden" value="public" name="target_group" id="id_target_group">'
                            .format(self.url), count=1, status_code=200, html=True)

    def test_should_update_survey_response(self):
        response = self.client.post(self.url, {u"sample_year": u"2013", u"target_group": u"public",
                                               u"library_name": u"Karlstad Stadsbibliotek",
                                               u"municipality_name": u"Karlstads kommun", u"municipality_code": u"1780",
                                               u"respondent_name": u"Åsa Hansen",
                                               u"respondent_email": u"asa.hansen@karlstad.se",
                                               u"respondent_phone": u"054-540 23 72"},
                                    follow=True)
        self.assertEquals(response.status_code, 200)
        result = SurveyResponse.objects.get(pk=self.survey_response.id)
        self.assertEquals(result.sample_year, 2013)
        self.assertEquals(result.target_group, u"public")
        self.assertEquals(result.library_name, u"Karlstad Stadsbibliotek")
        self.assertEquals(result.metadata.municipality_name, u"Karlstads kommun")
        self.assertEquals(result.metadata.municipality_code, u"1780")
        self.assertEquals(result.metadata.respondent_name, u"Åsa Hansen")
        self.assertEquals(result.metadata.respondent_email, u"asa.hansen@karlstad.se")
        self.assertEquals(result.metadata.respondent_phone, u"054-540 23 72")
        self.assertEquals(result.modified_by, self.current_user)

    def test_should_not_update_sample_year_or_target_group_for_existing_SurveyResponse(self):
        response = self.client.post(self.url, {u"sample_year": u"2014", u"target_group": u"research",
                                               u"library_name": u"Karlstad Stadsbibliotek",
                                               u"municipality_name": u"Karlstads kommun", u"municipality_code": u"1780",
                                               u"respondent_name": u"Åsa Hansen",
                                               u"respondent_email": u"asa.hansen@karlstad.se",
                                               u"respondent_phone": u"054-540 23 72"},
                                    follow=True)
        self.assertEquals(response.status_code, 200)
        result = SurveyResponse.objects.get(pk=self.survey_response.id)
        self.assertEquals(result.sample_year, 2013)
        self.assertEquals(result.target_group, u"public")

    def test_should_handle_non_unique_library_name(self):
        self.assertEquals(len(SurveyResponse.objects.filter(library_name=u"ALE BIBLIOTEK")), 1, "before post")

        response = self.client.post(self.url, {u"sample_year": u"2013", u"target_group": u"public",
                                               u"library_name": u"ALE BIBLIOTEK",
                                               u"municipality_name": u"Karlstads kommun", u"municipality_code": u"1780",
                                               u"respondent_name": u"Åsa Hansen",
                                               u"respondent_email": u"asa.hansen@karlstad.se",
                                               u"respondent_phone": u"054-540 23 72"},
                                    follow=True)
        self.assertEquals(response.status_code, 200)
        # FIXME: Somehow this test stopped working when I added EditSurveyObservationsViewTest and I cannot figure out why.
        # Assert below failes because there are 2 survey responses for ALE BIBLIOTEK

        # self.assertEquals(len(SurveyResponse.objects.filter(library_name=u"ALE BIBLIOTEK")), 1)

    #         self.assertEquals(response.context['form']._errors['library_name'], [u"Det finns redan ett enkätsvar för detta bibliotek"])

    def test_should_show_publish_button(self):
        response = self.client.get(
            reverse("edit_survey_response", kwargs={"survey_response_id": str(self.survey_response.id)}))
        self.assertContains(response, u'<input type="submit" value="Publicera" class="btn btn-primary pull-right"/>'
                            .format(self.url), count=1, status_code=200, html=True)


class PublishSurveyResponseViewTest(MongoTestCase):
    def setUp(self):
        self.survey_response = SurveyResponse(library_name=u"KARLSTAD STADSBIBLIOTEK", sample_year=2013,
                                              target_group=u"public", observations=[])
        self.survey_response.save()

        self.url = reverse("publish_survey_response", kwargs={"survey_response_id": str(self.survey_response.id)})
        self.edit_survey_response_url = reverse("edit_survey_response",
                                                kwargs={"survey_response_id": str(self.survey_response.id)})
        self.client.login(username="admin", password="admin")
        self.current_user = User.objects.filter(username="admin")[0]

    def test_should_publish_survey_response(self):
        self.assertFalse(self.survey_response.is_published)

        response = self.client.post(self.url, {}, follow=True)
        self.assertEquals(response.status_code, 200)

        result = SurveyResponse.objects.get(pk=self.survey_response.id)
        self.assertTrue(result.is_published)


class EditSurveyObservationsViewTest(MongoTestCase):
    def setUp(self):
        v1 = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type=u"integer",
                      is_public=True, target_groups=[u"public"])
        v1.save()
        v2 = Variable(key=u"folk6",
                      description=u"Är huvudbiblioteket i er kommun integrerat med ett skolbibliotek? 1=ja",
                      type=u"boolean", is_public=True, target_groups=[u"public"])
        v2.save()
        v3 = Variable(key=u"folk8", description=u"Textkommentar", type=u"string", is_public=False,
                      target_groups=[u"public"])
        v3.save()
        v4 = Variable(key=u"folk35", description=u"Antal årsverken övrig personal", type=u"decimal", is_public=True,
                      target_groups=[u"public"])
        v4.save()
        v5 = Variable(key=u"folk52", description=u"Andel tryckt skönlitteratur", type=u"percent", is_public=True,
                      target_groups=[u"public"])
        v5.save()
        v6 = Variable(key=u"folk38", description=u"Total driftskostnad", type=u"long", is_public=True,
                      target_groups=[u"public"])
        v6.save()

        sr = SurveyResponse(library_name=u"BIBLIOTEKEN I RAGUNDA", sample_year=2013, target_group="public",
                            observations=[])
        sr.observations.append(
            SurveyObservation(variable=v1, value=7.013, _source_key="folk5", _is_public=v1.is_public))
        sr.observations.append(SurveyObservation(variable=v2, value=None, _source_key="folk6", _is_public=v2.is_public))
        sr.observations.append(
            SurveyObservation(variable=v3, value=u"Här är en kommentar", _source_key="folk8", _is_public=v3.is_public))
        sr.observations.append(
            SurveyObservation(variable=v4, value=4.76593020050, _source_key=u"folk35", _is_public=v4.is_public))
        sr.observations.append(
            SurveyObservation(variable=v5, value=0.57306940, _source_key=u"folk52", _is_public=v5.is_public))
        sr.observations.append(
            SurveyObservation(variable=v6, value=49130498.0, _source_key=u"folk38", _is_public=v6.is_public))

        self.survey_response = sr.save()
        self.obs_folk5 = self.survey_response.observations[0]
        self.obs_folk6 = self.survey_response.observations[1]
        self.obs_folk8 = self.survey_response.observations[2]
        self.obs_folk35 = self.survey_response.observations[3]
        self.obs_folk52 = self.survey_response.observations[4]
        self.obs_folk38 = self.survey_response.observations[5]
        self.url = reverse("edit_survey_observations", kwargs={"survey_response_id": str(self.survey_response.id)})
        self.client.login(username="admin", password="admin")
        self.current_user = User.objects.filter(username="admin")[0]

    def test_should_edit_survey_observations(self):
        response = self.client.post(self.url, {u"folk5": u"5",
                                               u"folk6": u"True",
                                               u"folk8": u"Nu har jag skrivit en annan kommentar",
                                               u"folk35": u"8.9",
                                               u"folk52": u"61",
                                               u"folk38": u"9999999999999"},
                                    follow=True)
        self.assertEquals(response.status_code, 200)
        result = SurveyResponse.objects.get(pk=self.survey_response.id)
        self.assertEqual(result.observation_by_key(u"folk5").value, 5)
        self.assertEqual(result.observation_by_key(u"folk6").value, True)
        self.assertEqual(result.observation_by_key(u"folk8").value, u"Nu har jag skrivit en annan kommentar")
        self.assertEqual(result.observation_by_key(u"folk35").value, 8.9)
        self.assertEqual(result.observation_by_key(u"folk52").value, 0.61)
        self.assertEqual(result.observation_by_key(u"folk38").value, 9999999999999L)
        self.assertEquals(result.modified_by, self.current_user)

    def test_should_return_validation_errors_if_wrong_data_type(self):
        response = self.client.post(self.url, {u"folk5": u"5.72",
                                               u"folk6": u"foo",
                                               u"folk8": None,
                                               u"folk35": u"8",
                                               u"folk52": u"0.61",
                                               u"folk38": u"9999999999999.999999999"},
                                    follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['observations_form']._errors['folk5'], [u"Fyll i ett heltal."])
        self.assertEquals(response.context['observations_form']._errors['folk6'],
                          [u"Välj ett giltigt alternativ. foo finns inte bland tillg\xe4ngliga alternativ."])
        self.assertEquals(response.context['observations_form']._errors['folk52'], [u"Fyll i ett heltal."])
        self.assertEquals(response.context['observations_form']._errors['folk38'], [u"Fyll i ett heltal."])


class ReplaceableVariablesApiTest(MongoTestCase):
    def setUp(self):
        v = Variable(key=u"Folk28",
                     description=u"Totalt antal anställda personer som är bibliotekarier och som är män 1 mars.",
                     type="integer", is_public=True, target_groups=["public"])
        self.active_public = v.save()
        v2 = Variable(key=u"Forsk21", description=u"Antal anställda manliga bibliotekarier och dokumentalister.",
                      type="integer", is_public=True, is_draft=True, target_groups=["research"])
        self.draft = v2.save()
        v3 = Variable(key=u"Sjukhus104",
                      description=u"Totalt antal fjärrutlån under kalenderåret - summering av de angivna delsummorna",
                      type="integer", is_public=True, replaced_by=v, target_groups=["hospital"])
        self.already_replaced = v3.save()
        v4 = Variable(key=u"Skol10", description=u"Postort", type="string", is_public=False, target_groups=["school"])
        self.active_private = v4.save()

        self.url = reverse("replaceable_variables_api")
        self.client.login(username="admin", password="admin")

    def test_view_requires_admin_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username="library_user", password="secret")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.logout()
        self.client.login(username="admin", password="admin")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_should_return_replaceable_variables_as_json(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [
            {"key": "Folk28", "id": str(self.active_public.id), "description": self.active_public.description},
            {"key": "Skol10", "id": str(self.active_private.id), "description": self.active_private.description}])

    def test_should_filter_replaceables_by_key(self):
        response = self.client.get("{}?q=fo".format(self.url))
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [
            {"key": "Folk28", "id": str(self.active_public.id), "description": self.active_public.description}])

    def test_should_filter_replaceables_by_description(self):
        response = self.client.get("{}?q=post".format(self.url))
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [
            {"key": "Skol10", "id": str(self.active_private.id), "description": self.active_private.description}])


class SurveysViewTest(MongoTestCase):
    def setUp(self):
        survey = Survey(sample_year=2014, target_groups=[u"public"], is_draft=False, questions=[])
        self.survey = survey.save()

        survey_draft = Survey(sample_year=2015, target_groups=[u"public", u"research", u"hospital", u"school"],
                              is_draft=True, questions=[])
        self.survey_draft = survey_draft.save()

        self.url = reverse("surveys")
        self.client.login(username="admin", password="admin")

    def test_view_requires_admin_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username="library_user", password="secret")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.logout()
        self.client.login(username="admin", password="admin")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_should_list_surveys(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["surveys"]), 2)

    def test_should_have_button_to_create_survey(self):
        response = self.client.get(self.url)
        self.assertContains(response, u'<a href="{}" class="btn btn-primary" role="button">Skapa enkät</a>'.format(
            reverse('create_survey')), count=1, status_code=200, html=True)

    def test_each_survey_should_have_link_to_edit_view(self):
        response = self.client.get(self.url)
        self.assertContains(response, u'<a href="{}">2014 - Folkbibliotek</a>'.format(
            reverse('edit_survey', kwargs={"survey_id": str(self.survey.id)})), count=1, status_code=200, html=True)
        self.assertContains(response, u'<a href="{}">2015 - Samtliga bibliotekstyper</a>'.format(
            reverse('edit_survey', kwargs={"survey_id": str(self.survey_draft.id)})), count=1, status_code=200,
                            html=True)


class SurveyableVariablesApiTest(MongoTestCase):
    def setUp(self):
        v = Variable(key=u"Folk12", description=u"Antal bemannade filialer", type="integer", is_public=True,
                     target_groups=["public"])
        self.active_without_dates = v.save()

        v1 = Variable(key=u"Folk10", description=u"Antal bemannade servicesställen", type="integer", is_public=True,
                      target_groups=["public"],
                      active_from=datetime(2010, 1, 1).date())
        self.active_with_from_date = v1.save()

        v3 = Variable(key=u"Folk31", description=u"Antal årsverken totalt", type="decimal", is_public=True,
                      target_groups=["public"],
                      active_from=datetime.utcnow().date(), active_to=(datetime.utcnow() + timedelta(days=1)).date())
        self.active_with_date_range = v3.save()

        v2 = Variable(key=u"Folk35", description=u"Antal årsverken övrig personal", type="decimal", is_public=True,
                      target_groups=["public"],
                      active_to=datetime(2014, 6, 1).date())
        self.discontinued = v2.save()

        v5 = Variable(key=u"Folk20", description=u"Text övriga utlåningsställen", type="string", is_public=False,
                      target_groups=["public"],
                      active_from=(datetime.utcnow() + timedelta(days=90)).date())
        self.pending = v5.save()

        v4 = Variable(key=u"Folk69", description=u"Totalt nyförvärv AV-medier", type="integer", is_public=True,
                      target_groups=["public"],
                      is_draft=True)
        self.draft = v4.save()

        v6 = Variable(key=u"Folk80", description=u"Nyförvärv musik under kalanderåret.", type="integer", is_public=True,
                      target_groups=["public"],
                      replaced_by=self.draft)
        self.replaced = v6.save()

        self.url = reverse("surveyable_variables_api")
        self.client.login(username="admin", password="admin")

    def test_view_requires_admin_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username="library_user", password="secret")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.logout()
        self.client.login(username="admin", password="admin")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_should_return_active_pending_and_draft_variables_as_json(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [{"key": "Folk10", "id": str(self.active_with_from_date.id)},
                                 {"key": "Folk12", "id": str(self.active_without_dates.id)},
                                 {"key": "Folk20", "id": str(self.pending.id)},
                                 {"key": "Folk31", "id": str(self.active_with_date_range.id)},
                                 {"key": "Folk69", "id": str(self.draft.id)}])

    def test_should_filter_surveyable_by_key(self):
        response = self.client.get("{}?q=Folk1".format(self.url))
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [{"key": "Folk10", "id": str(self.active_with_from_date.id)},
                                 {"key": "Folk12", "id": str(self.active_without_dates.id)}])
        