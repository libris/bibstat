# -*- coding: UTF-8 -*-
import uuid
import json

from django.urls import reverse
from django_mongoengine.mongo_auth.models import User

from datetime import datetime
from libstat.tests import MongoTestCase
from libstat.models import Variable, Survey, SurveyObservation, OpenData
from libstat.utils import SURVEY_TARGET_GROUPS


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
        self._dummy_variable(key=u"key_1", target_groups=["sjukbib"])
        self._dummy_variable(key=u"key_2", target_groups=["skolbib"])
        self._dummy_variable(key=u"key_3", target_groups=["sjukbib"])

        response = self.client.get(u"{}?target_group=sjukbib".format(self.url))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["variables"]), 2)
        self.assertEquals(response.context["variables"][0].key, u"key_1")
        self.assertEquals(response.context["variables"][1].key, u"key_3")

    def test_should_filter_variables_by_target_group_all(self):
        all_groups = [g[0] for g in SURVEY_TARGET_GROUPS]
        self._dummy_variable(key=u"key_1", target_groups=["sjukbib"])
        self._dummy_variable(key=u"key_2", target_groups=all_groups)
        self._dummy_variable(key=u"key_3", target_groups=["sjukbib"])

        response = self.client.get(u"{}?target_group=all".format(self.url))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["variables"]), 1)
        self.assertEquals(response.context["variables"][0].key, u"key_2")

    def test_should_filter_variables_by_list_of_target_groups(self):
        self._dummy_variable(key=u"key_1")
        self._dummy_variable(key=u"key_2")

        response = self.client.get(u"{}?target_group=skolbib&target_group=folkbib".format(self.url))

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
                                     u"target_groups": [u"folkbib", u"specbib", u"skolbib", u"sjukbib"],
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
        self.assertEquals(result.target_groups, [u"folkbib", u"specbib", u"skolbib", u"sjukbib"])
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
                           is_public=True, target_groups=["folkbib"])
        self.v1.save(validate=False)
        self.v2 = Variable(key=u"Sjukhus102",
                           description=u"Bestånd av tillgängliga medier för personer med läsnedsättning",
                           type="integer", is_public=True, target_groups=["sjukbib"])
        self.v2.save()
        self.v3 = Variable(key=u"Forsk23", description=u"Antal anställda personer manliga biblioteksassistenter.",
                           type="integer", is_public=True, is_draft=True, target_groups=["specbib"])
        self.v3.save()

        self.new_category = u"Organisation"
        self.new_sub_category = u"Bemannade serviceställen"
        self.new_type = u"string"
        self.new_target_groups = [u"specbib"]
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
        variable = self._dummy_variable(is_draft=False)

        survey = self._dummy_survey()
        survey.observations = [SurveyObservation(variable=str(variable.id))]
        survey.save()
        survey.publish()

        response = self.delete(variable)

        self.assertEquals(response.status_code, 403)
        self.assertExists(variable)

    def test_should_not_be_able_to_delete_non_draft_variable_when_referenced_in_open_data(self):
        variable = self.new_variable(is_draft=False)
        self._dummy_open_data(variable=variable)

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
        url = reverse("edit_variable", kwargs={"variable_id": str(variable.id)})
        return self.client.post(url, {
            u"active_from": variable.active_from.date() if variable.active_from else "",
            # active_to input is disabled if variable is replaced
            u"active_to": variable.active_to.date() if variable.active_to and not variable.replaced_by else "",
            u"replaces": ", ".join([str(v.id) for v in variable.replaces]) if variable.replaces else "",
            u"question": variable.question or "",
            u"question_part": variable.question_part or "",
            u"category": variable.category or "",
            u"sub_category": variable.sub_category or "",
            u"type": variable.type or "",
            u"is_public": int(variable.is_public),
            u"target_groups": variable.target_groups or "",
            u"description": variable.description or "",
            u"comment": variable.comment or "",
            u"submit_action": action
        })

    def activate(self, variable):
        return self.post(u"save_and_activate", variable)

    def delete(self, variable):
        return self.post(u"delete", variable)

    def new_variable(self, key=None, description=None, type=None, target_groups=None, is_draft=True, save=True):
        variable = Variable(
            key=key if key else str(uuid.uuid1()),
            description=description if description else u"description",
            type=type if type else "integer",
            target_groups=target_groups if target_groups else ["folkbib"],
            is_draft=is_draft
        )

        if save:
            variable.save()
        return variable

    def new_open_data(self, variable):
        open_data = OpenData(
            library_name='test',
            sample_year='1234',
            target_group='folkbib',
            variable=variable.id
        )

        open_data.save()
        return open_data

    def new_survey_response(self):
        return Survey(
            target_group='folkbib',
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


class ReplaceableVariablesApiTest(MongoTestCase):

    def setUp(self):
        self.url = reverse("replaceable_variables")
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
        var1 = self._dummy_variable(key=u"key_1")
        self._dummy_variable(key=u"key_2", is_draft=True)
        self._dummy_variable(key=u"key_3", replaced_by=var1)
        var4 = self._dummy_variable(key=u"key_4")

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [{"key": "key_1",
                                  "id": str(var1.id),
                                  "description": var1.description},
                                 {"key": "key_4",
                                  "id": str(var4.id),
                                  "description": var4.description}])

    def test_should_filter_replaceables_by_key(self):
        var = self._dummy_variable(key=u"Folk28")

        response = self.client.get("{}?q=fo".format(self.url))
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [{"key": "Folk28",
                                  "id": str(var.id),
                                  "description": var.description}])

    def test_should_filter_replaceables_by_description(self):
        var = self._dummy_variable(key=u"Skol10", description=u"Postort", type="string")
        response = self.client.get("{}?q=post".format(self.url))
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [{"key": "Skol10",
                                  "id": str(var.id),
                                  "description": var.description}])
