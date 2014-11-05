# -*- coding: UTF-8 -*-
import uuid
import json

from django.core.urlresolvers import reverse
from mongoengine.django.auth import User

from datetime import datetime
from libstat.tests import MongoTestCase
from libstat.models import Variable, Survey, SurveyObservation, OpenData


class VariablesViewTest(MongoTestCase):

    def setUp(self):
        self.url = reverse("variables")
        self._login()

    def test_view_requires_admin_login(self):
        self._logout()

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username="library_user", password="secret")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username="admin", password="admin")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_should_list_all_variables(self):
        self._dummy_variable(key=u"key_1")
        self._dummy_variable(key=u"key_2")
        self._dummy_variable(key=u"key_3")

        response = self.client.get(self.url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["variables"]), 3)

    def test_should_filter_variables_by_target_group(self):
        self._dummy_variable(key=u"key_1", target_groups=["hospital"])
        self._dummy_variable(key=u"key_2", target_groups=["school"])
        self._dummy_variable(key=u"key_3", target_groups=["hospital"])

        response = self.client.get(u"{}?target_group=hospital".format(self.url))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["variables"]), 2)
        self.assertEquals(response.context["variables"][0].key, u"key_1")
        self.assertEquals(response.context["variables"][1].key, u"key_3")

    def test_should_filter_variables_by_target_group_all(self):
        self._dummy_variable(key=u"key_1", target_groups=["hospital"])
        self._dummy_variable(key=u"key_2", target_groups=["public", "research", "hospital", "school"])
        self._dummy_variable(key=u"key_3", target_groups=["hospital"])

        response = self.client.get(u"{}?target_group=all".format(self.url))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["variables"]), 1)
        self.assertEquals(response.context["variables"][0].key, u"key_2")

    def test_should_filter_variables_by_list_of_target_groups(self):
        self._dummy_variable(key=u"key_1")
        self._dummy_variable(key=u"key_2")

        response = self.client.get(u"{}?target_group=school&target_group=public".format(self.url))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["variables"]), 2)
        self.assertEquals(response.context["variables"][0].key, u"key_1")
        self.assertEquals(response.context["variables"][1].key, u"key_2")

    def test_each_variable_should_have_edit_link(self):
        variable = self._dummy_variable(key=u"key_1")

        response = self.client.get(self.url)

        self.assertContains(response,
                            (u'<a title="Visa/Ändra" data-form="/variables/{}"'
                             u'href="#" class="edit-variable">key_1</a>').format(variable.id),
                            count=1,
                            status_code=200,
                            html=True)

    def test_should_have_button_for_adding_variable(self):
        response = self.client.get(self.url)

        self.assertContains(response,
                            (u'<a class="create-variable btn btn-primary" role="button"'
                             'href="#" data-form="{}">Skapa term</a>').format(reverse("create_variable")),
                            count=1,
                            status_code=200,
                            html=True)


class CreateVariableViewTest(MongoTestCase):

    def setUp(self):
        self.url = reverse("create_variable")
        self.client.login(username="admin", password="admin")

    def test_should_get_empty_form(self):
        response = self.client.get(self.url)

        self.assertContains(response,
                            u'<h4 class="modal-title">Ny term (utkast)</h4>',
                            count=1,
                            status_code=200,
                            html=True)
        self.assertContains(response,
                            u'<input type="submit" value="Spara utkast" class="btn btn-primary">',
                            count=1,
                            status_code=200,
                            html=True)

    def test_should_create_variable_draft(self):
        response = self.client.post(self.url,
                                    {u"key": u"antalManligaBibliotekarier",
                                     u"question": (u"Hur många anställda personer fanns i biblioteksverksamheten den "
                                                   u"1 mars aktuellt mätår?"),
                                     u"question_part": u"Antal anställda bibliotekarier som är män",
                                     u"category": u"Organisation",
                                     u"sub_category": u"Personal",
                                     u"type": u"integer",
                                     u"is_public": u"True",
                                     u"target_groups": [u"public", u"research", u"school", u"hospital"],
                                     u"description": (u"Antal anställda manliga bibliotekarier den "
                                                      u"1 mars aktuellt mätår"),
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
        self.v1 = Variable(key=u"Folk10", description=u"Antal bemannade serviceställen", type="integer",
                           is_public=True, target_groups=["public"])
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
        self.assertContains(response, (u'<input type="text" disabled="disabled" value="2015-01-01" name="active_to"'
                                       'class="form-control" id="id_active_to">'),
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
        self.assertContains(response, (u'<input type="submit" id="save_and_activate" value="Spara och aktivera"'
                                       'class="btn btn-primary">'),
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
        self.post(u"save", replaced)

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
        return Survey(
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


class SurveyViewTest(MongoTestCase):

    def setUp(self):
        self.client.login(username="admin", password="admin")

    def test_should_not_fetch_survey_responses_unless_list_action_provided(self):
        self._dummy_survey()
        self._dummy_survey()

        response = self.client.get(reverse("surveys"))

        self.assertEquals(len(response.context["survey_responses"]), 0)

    def test_should_list_survey_responses_by_year(self):
        self._dummy_survey(sample_year=2012)
        self._dummy_survey(sample_year=2013)

        response = self.client.get("{}?action=list&sample_year=2012".format(reverse("surveys")))

        self.assertEquals(len(response.context["survey_responses"]), 1)

    def test_should_list_survey_responses_by_target_group(self):
        self._dummy_survey(target_group="public")
        self._dummy_survey(target_group="school")
        self._dummy_survey(target_group="public")

        response = self.client.get("{}?action=list&target_group=public".format(reverse("surveys")))

        self.assertEquals(len(response.context["survey_responses"]), 2)

    def test_should_list_survey_responses_by_status(self):
        self._dummy_survey(status="not_viewed")
        self._dummy_survey(status="submitted")
        self._dummy_survey(status="published")

        response = self.client.get("{}?action=list&status=submitted".format(reverse("surveys")))

        self.assertEquals(len(response.context["survey_responses"]), 1)

    def test_should_list_survey_responses_by_year_and_target_group(self):
        self._dummy_survey(library=self._dummy_library(name="lib1"), target_group="public", sample_year=2012)
        self._dummy_survey(library=self._dummy_library(name="lib2"), target_group="public", sample_year=2013)
        self._dummy_survey(library=self._dummy_library(name="lib3"), target_group="school", sample_year=2013)

        response = self.client.get(
            "{}?action=list&target_group=public&sample_year=2013".format(reverse("surveys")))

        self.assertEquals(len(response.context["survey_responses"]), 1)
        self.assertEquals(response.context["survey_responses"][0].library_name, "lib2")

    def test_each_survey_response_should_have_checkbox_for_actions(self):
        survey = self._dummy_survey(sample_year=2013)

        response = self.client.get("{}?action=list&sample_year=2013".format(reverse("surveys")))

        self.assertContains(response, 'value="{}"'.format(survey.id))

    def test_each_survey_response_should_have_a_link_to_details_view(self):
        survey = self._dummy_survey(sample_year=2013)

        response = self.client.get("{}?action=list&sample_year=2013".format(reverse("surveys")))

        self.assertContains(response, u'<a href="{}" title="Visa/redigera enkätsvar">Visa/redigera</a>'
                            .format(reverse("survey", kwargs={"survey_id": str(survey.id)})),
                            count=1, status_code=200, html=True)

    def test_each_survey_response_should_have_a_link_to_bibdb(self):
        library = self._dummy_library(name="lib1", sigel="lib1_sigel")
        self._dummy_survey(sample_year=2013, library=library)

        response = self.client.get("{}?action=list&sample_year=2013".format(reverse("surveys")))

        self.assertContains(response, "<a href='http://bibdb.libris.kb.se/library/{}'>{}</a>"
                            .format(library.sigel, library.name),
                            count=1, status_code=200, html=True)


class PublishSurveyResponsesViewTest(MongoTestCase):

    def setUp(self):
        self.survey_response = Survey(library_name="KARLSTAD STADSBIBLIOTEK", sample_year=2013,
                                      target_group="public", observations=[])
        self.survey_response.save()
        sr2 = Survey(library_name="NORRBOTTENS LÄNSBIBLIOTEK", sample_year=2012, target_group="public",
                     observations=[])
        sr2.save()
        sr3 = Survey(library_name=u"Sjukhusbiblioteken i Dalarnas län", sample_year=2013,
                     target_group="hospital", observations=[])
        sr3.save()

        self.url = reverse("surveys_publish")
        self.client.login(username="admin", password="admin")

    def test_should_publish_selection(self):
        response = self.client.post(self.url, {u"sample_year": u"2013",
                                               u"target_group": u"public",
                                               u"survey-response-ids": [u"{}".format(self.survey_response.id)]},
                                    follow=True)
        self.assertEquals(response.status_code, 200)

        survey_response = Survey.objects.get(pk=self.survey_response.id)
        self.assertTrue(survey_response.published_at is not None)
        self.assertEquals(survey_response.published_by, User.objects.filter(username="admin")[0])

    def test_should_not_publish_unless_selected_ids(self):
        response = self.client.post(self.url, {u"sample_year": u"2013",
                                               u"target_group": u"public",
                                               u"survey-response-ids": []},
                                    follow=True)
        self.assertEquals(response.status_code, 200)
        survey_response = Survey.objects.get(pk=self.survey_response.id)
        self.assertEquals(survey_response.published_at, None)
        self.assertEquals(survey_response.published_by, None)
