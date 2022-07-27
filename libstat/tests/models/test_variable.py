from datetime import timedelta

from mongoengine import DoesNotExist

from libstat.tests import MongoTestCase
from libstat.models import *
from bson.objectid import ObjectId


class VariableQuerySetTest(MongoTestCase):

    def setUp(self):
        # Discontinued (today)
        v2 = Variable(key="Folk35", description="Antal årsverken övrig personal", type="decimal", is_public=False,
                      target_groups=["folkbib"])
        v2.question = "Hur många årsverken utfördes av personal i folkbiblioteksverksamheten under 2012?"
        v2.question_part = "Antal årsverken övrig personal (ej städpersonal)"
        v2.active_to = datetime.utcnow().date()
        v2.save()
        self.v2 = Variable.objects.get(pk=v2.id)

        # Replaced
        v = Variable(key="Folk10", description="Antal bemannade servicesställen", type="integer", is_public=True,
                     target_groups=["folkbib"])
        v.replaced_by = self.v2
        v.save()
        self.v = Variable.objects.get(pk=v.id)

        # Active
        v3 = Variable(key="Folk31", description="Antal årsverken totalt", type="decimal", is_public=True,
                      target_groups=["folkbib"], is_draft=False)
        v3.summary_of = [self.v2]
        v3.save()
        self.v3 = Variable.objects.get(pk=v3.id)

        # Draft
        v4 = Variable(key="Folk69", description="Totalt nyförvärv AV-medier", type="integer", is_public=True,
                      target_groups=["folkbib"], is_draft=True)
        v4.question = "Hur många nyförvärv av AV-media gjordes under 2012?"
        v4.save()
        self.v4 = Variable.objects.get(pk=v4.id)

    def test_filter_public_terms(self):
        result_set = Variable.objects.public_terms()
        self.assertEqual([v.id for v in result_set], [self.v.id, self.v3.id])

    def test_filter_public_term_by_key(self):
        self.assertRaises(DoesNotExist, lambda: Variable.objects.public_term_by_key(None))
        self.assertRaises(DoesNotExist, lambda: Variable.objects.public_term_by_key("foo"))
        self.assertEqual(Variable.objects.public_term_by_key("Folk10").id, self.v.id)
        self.assertRaises(DoesNotExist, lambda: Variable.objects.public_term_by_key("Folk35"))
        self.assertEqual(Variable.objects.public_term_by_key("Folk31").id, self.v3.id)
        self.assertRaises(DoesNotExist, lambda: Variable.objects.public_term_by_key("Folk69"))

    def test_filter_replaceable_should_not_return_drafts_or_replaced(self):
        result_set = Variable.objects.replaceable()
        self.assertEqual([v.id for v in result_set], [self.v3.id, self.v2.id])

    def test_filter_surveyable_should_not_return_discontinued_or_replaced(self):
        result_set = Variable.objects.surveyable()
        self.assertEqual([v.id for v in result_set], [self.v3.id, self.v4.id])


class VariableTest(MongoTestCase):

    def setUp(self):
        v = Variable(key="Folk10", description="Antal bemannade servicesställen", type="integer", is_public=True,
                     target_groups=["folkbib"],
                     active_from=datetime(2010, 1, 1).date())
        v.save()
        self.v = Variable.objects.get(pk=v.id)

        v2 = Variable(key="Folk35", description="Antal årsverken övrig personal", type="decimal", is_public=True,
                      target_groups=["folkbib"],
                      active_to=datetime(2014, 6, 1).date())
        v2.question = "Hur många årsverken utfördes av personal i folkbiblioteksverksamheten under 2012?"
        v2.question_part = "Antal årsverken övrig personal (ej städpersonal)"
        v2.save()
        self.v2 = Variable.objects.get(pk=v2.id)

        v3 = Variable(key="Folk31", description="Antal årsverken totalt", type="decimal", is_public=True,
                      target_groups=["folkbib"],
                      active_from=datetime.utcnow().date(), active_to=(datetime.utcnow() + timedelta(days=1)).date())
        v3.summary_of = [self.v2]
        v3.save()
        self.v3 = Variable.objects.get(pk=v3.id)

        v4 = Variable(key="Folk69", description="Totalt nyförvärv AV-medier", type="integer", is_public=True,
                      target_groups=["folkbib"], is_draft=True)
        v4.question = "Hur många nyförvärv av AV-media gjordes under 2012?"
        v4.save()
        self.v4 = Variable.objects.get(pk=v4.id)

    def test_key_asc_should_be_default_sort_order(self):
        result = Variable.objects.all()
        self.assertEqual([v.key for v in result], ["Folk10", "Folk31", "Folk35", "Folk69"])

    def test_should_transform_object_to_dict(self):
        self.v.active_from = None
        self.v.save()

        folk10 = Variable.objects.get(pk=self.v.id)
        expectedVariableDict = {
            "@id": "Folk10",
            "@type": ["rdf:Property", "qb:MeasureProperty"],
            "comment": "Antal bemannade servicesställen",
            "range": "xsd:integer"
        }
        self.assertEqual(folk10.to_dict(), expectedVariableDict)

    def test_should_transform_replacing_object_to_dict(self):
        self.v4.replace_siblings([self.v2.id], commit=True)
        folk69 = Variable.objects.get(pk=self.v4.id)
        expectedVariableDict = {
            "@id": "Folk69",
            "@type": ["rdf:Property", "qb:MeasureProperty"],
            "comment": "Totalt nyförvärv AV-medier",
            "range": "xsd:integer",
            "replaces": ["Folk35"]
        }
        self.assertEqual(folk69.to_dict(), expectedVariableDict)

    def test_should_transform_replaced_object_to_dict(self):
        self.v4.is_draft = False
        self.v4.replace_siblings([self.v2.id], commit=True)

        folk35 = Variable.objects.get(pk=self.v2.id)

        expectedVariableDict = {
            "@id": "Folk35",
            "@type": ["rdf:Property", "qb:MeasureProperty"],
            "comment": "Antal årsverken övrig personal",
            "range": "xsd:decimal",
            "replacedBy": "Folk69",
        }
        self.assertEqual(folk35.to_dict(), expectedVariableDict)

    def test_should_transform_discontinued_object_to_dict(self):
        self.v.active_from = None
        self.v.active_to = datetime(2014, 8, 31)
        self.v.save()

        folk10 = Variable.objects.get(pk=self.v.id)
        expectedVariableDict = {
            "@id": "Folk10",
            "@type": ["rdf:Property", "qb:MeasureProperty"],
            "comment": "Antal bemannade servicesställen",
            "range": "xsd:integer",
            "valid": "name=Giltighetstid; end=2014-08-31;"
        }
        self.assertEqual(folk10.to_dict(), expectedVariableDict)

    def test_should_transform_pending_object_to_dict(self):
        tomorrow = (datetime.utcnow() + timedelta(days=1)).date()
        self.v.active_from = tomorrow
        self.v.active_to = None
        self.v.save()

        folk10 = Variable.objects.get(pk=self.v.id)
        expectedVariableDict = {
            "@id": "Folk10",
            "@type": ["rdf:Property", "qb:MeasureProperty"],
            "comment": "Antal bemannade servicesställen",
            "range": "xsd:integer",
            "valid": "name=Giltighetstid; start={};".format(tomorrow)
        }
        self.assertEqual(folk10.to_dict(), expectedVariableDict)

    def test_should_transform_date_ranged_object_to_dict(self):
        self.v.active_from = datetime(2010, 1, 1).date()
        self.v.active_to = datetime(2014, 12, 31)
        self.v.save()

        folk10 = Variable.objects.get(pk=self.v.id)
        expectedVariableDict = {
            "@id": "Folk10",
            "@type": ["rdf:Property", "qb:MeasureProperty"],
            "comment": "Antal bemannade servicesställen",
            "range": "xsd:integer",
            "valid": "name=Giltighetstid; start=2010-01-01; end=2014-12-31;"
        }
        self.assertEqual(folk10.to_dict(), expectedVariableDict)

    def test_variable_should_have_question_and_question_part(self):
        folk35 = Variable.objects.get(pk=self.v2.id)
        self.assertTrue(hasattr(folk35,
                                "question") and folk35.question == "Hur många årsverken utfördes av personal i folkbiblioteksverksamheten under 2012?")
        self.assertTrue(hasattr(folk35,
                                "question_part") and folk35.question_part == "Antal årsverken övrig personal (ej städpersonal)")

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
        self.assertEqual(folk35.label, [folk35.question, folk35.question_part])

    def test_should_return_question_as_label_if_no_question_part(self):
        folk69 = Variable.objects.get(pk=self.v4.id)
        self.assertEqual(folk69.label, folk69.question)

    def test_should_return_description_as_label_if_no_question(self):
        folk31 = Variable.objects.get(pk=self.v3.id)
        self.assertEqual(folk31.label, folk31.description)

    def test_should_store_version_when_updating_existing_object(self):
        self.v.description = "Totalt antal bemannade serviceställen, summering av antal filialer och huvudbibliotek"
        self.v.save()

        versions = VariableVersion.objects.all()
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0].description, "Antal bemannade servicesställen")

    def test_should_not_store_version_when_updating_draft(self):
        self.v4.description = "En ny beskrivning"
        self.v4.save()

        versions = VariableVersion.objects.all()
        self.assertEqual(len(versions), 0)

    def test_should_set_modified_date_when_updating_existing_object(self):
        date_modified = self.v.date_modified
        self.v.description = "Totalt antal bemannade serviceställen, summering av antal filialer och huvudbibliotek"
        self.v.save()

        updated = Variable.objects.get(pk=self.v.id)
        self.assertTrue(updated.date_modified > date_modified)

    def test_should_set_modified_date_when_updating_draft(self):
        date_modified = self.v4.date_modified
        self.v4.description = "En ny beskrivning"
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
        self.assertEqual(set([v.id for v in modified_siblings]), set([self.v.id, self.v3.id]))

        replacement = Variable.objects.get(pk=self.v2.id)
        replaced_var_1 = Variable.objects.get(pk=self.v.id)
        replaced_var_2 = Variable.objects.get(pk=self.v3.id)

        # Replacement should have fields active_from and replaces set
        self.assertEqual(set([v.id for v in replacement.replaces]), set([self.v.id, self.v3.id]))
        self.assertEqual(replacement.active_from, switchover_date)

        # Replaced variables should have fields active_to and replaced_by set.
        self.assertEqual(replaced_var_1.replaced_by.id, self.v2.id)
        self.assertEqual(replaced_var_1.active_to, switchover_date)
        self.assertEqual(replaced_var_1.is_active, False)

        self.assertEqual(replaced_var_2.replaced_by.id, self.v2.id)
        self.assertEqual(replaced_var_2.active_to, switchover_date)
        self.assertEqual(replaced_var_2.is_active, False)

    def test_draft_variable_should_list_but_not_replace_other_variables(self):
        switchover_date = datetime(2014, 1, 1)
        modified_siblings = self.v4.replace_siblings([self.v2.id], switchover_date=switchover_date, commit=True)
        self.assertEqual(modified_siblings, [])

        replacement_var = Variable.objects.get(pk=self.v4.id)
        to_be_replaced = Variable.objects.get(pk=self.v2.id)
        self.assertEqual(set([v.id for v in replacement_var.replaces]), set([self.v2.id]))
        self.assertEqual(to_be_replaced.replaced_by, None)
        self.assertEqual(to_be_replaced.active_to, self.v2.active_to)
        self.assertEqual(to_be_replaced.is_active, False)

    def test_should_not_commit_replacement_unless_specified(self):
        modified_siblings = self.v2.replace_siblings([self.v.id])
        self.assertEqual(set([v.id for v in self.v2.replaces]), set([self.v.id]))
        self.assertEqual(set([v.id for v in modified_siblings]), set([self.v.id]))

        replacement_var = Variable.objects.get(pk=self.v2.id)
        replaced_var_1 = Variable.objects.get(pk=self.v.id)

        self.assertEqual(replacement_var.replaces, [])
        self.assertEqual(replaced_var_1.replaced_by, None)

    def test_should_raise_error_if_trying_to_replace_already_replaced_variable(self):
        self.v.replace_siblings([self.v2.id], commit=True)

        self.assertRaises(AttributeError, lambda: self.v3.replace_siblings([self.v2.id], commit=True))

        replacement = Variable.objects.get(pk=self.v.id)
        unsuccessful_replacement = Variable.objects.get(pk=self.v3.id)
        to_be_replaced = Variable.objects.get(pk=self.v2.id)
        self.assertEqual([v.id for v in replacement.replaces], [self.v2.id])
        self.assertEqual(unsuccessful_replacement.replaces, [])
        self.assertEqual(to_be_replaced.replaced_by.id, self.v.id)

    def test_raise_error_if_trying_to_replace_non_existing_variable(self):
        self.assertRaises(DoesNotExist,
                          lambda: self.v.replace_siblings([ObjectId("53fdec1ca9969003ec144d97")], commit=True))

    def test_should_update_replacements(self):
        self.v2.replace_siblings([self.v.id, self.v3.id], switchover_date=datetime(2014, 12, 31).date(), commit=True)
        replacement = Variable.objects.get(pk=self.v2.id)
        self.assertEqual(len(VariableVersion.objects.filter(key=self.v.key)), 1)

        # Should update v, add v4 and remove v3
        new_switchover_date = datetime(2015, 1, 1).date()
        replacement.replace_siblings([self.v.id, self.v4.id], switchover_date=new_switchover_date, commit=True)

        replacement = Variable.objects.get(pk=self.v2.id)
        modified_replaced = Variable.objects.get(pk=self.v.id)
        no_longer_replaced = Variable.objects.get(pk=self.v3.id)
        new_replaced = Variable.objects.get(pk=self.v4.id)

        # replacement should have updated list of variables (active_from is set outside of this mmethod)
        self.assertEqual(set([v.id for v in replacement.replaces]), set([modified_replaced.id, new_replaced.id]))

        # v should have updated active_to date
        self.assertEqual(modified_replaced.active_to.date(), new_switchover_date)
        self.assertEqual(modified_replaced.replaced_by.id, replacement.id)

        # v3 should no longer be replaced
        self.assertEqual(no_longer_replaced.replaced_by, None)
        self.assertEqual(no_longer_replaced.active_to, None)

        # v4 should be replaced
        self.assertEqual(new_replaced.replaced_by.id, replacement.id)
        self.assertEqual(new_replaced.active_to.date(), new_switchover_date)

    def test_should_update_replacements_for_draft(self):
        modified_siblings = self.v4.replace_siblings([self.v2.id], commit=True)
        after_setup = Variable.objects.get(pk=self.v4.id)

        after_setup.replace_siblings([self.v2.id, self.v3.id], commit=True)

        replacement_var = Variable.objects.get(pk=self.v4.id)

        self.assertEqual(set([v.id for v in replacement_var.replaces]), set([self.v2.id, self.v3.id]))
        self.assertEqual(Variable.objects.get(pk=self.v2.id).replaced_by, None)
        self.assertEqual(len(VariableVersion.objects.filter(key=self.v2.key)), 0)
        self.assertEqual(Variable.objects.get(pk=self.v3.id).replaced_by, None)
        self.assertEqual(len(VariableVersion.objects.filter(key=self.v3.key)), 0)

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

        self.assertEqual(replacement.reload().replaces, [])
        self.assertEqual(replaced_1.reload().replaced_by, None)
        self.assertEqual(replaced_2.reload().replaced_by, None)

    def test_should_clear_all_replacements_for_draft(self):
        # Setup
        replacement = self.v4
        replaced = self.v2
        replacement.replace_siblings([replaced.id], commit=True)
        replacement.reload()
        replaced.reload()

        # Clear replacements
        replacement.replace_siblings([], commit=True)

        self.assertEqual(replacement.reload().replaces, [])
        self.assertEqual(replaced.reload().replaced_by, None)
        self.assertEqual(len(VariableVersion.objects.filter(key=replaced.key)), 0)

    def test_should_nullify_active_to_and_references_to_replaced_by_when_deleting_replacement_instance(self):
        # Setup
        replacement = self.v2
        replaced_1 = self.v
        replaced_2 = self.v3
        replacement.replace_siblings([replaced_1.id, replaced_2.id], switchover_date=datetime(2015, 1, 1), commit=True)
        replacement.reload()

        print((replacement.id))
        replacement.delete()

        replaced_1.reload()
        self.assertEqual(replaced_1.replaced_by, None)
        self.assertEqual(replaced_1.active_to, None)
        replaced_2.reload()
        self.assertEqual(replaced_2.replaced_by, None)
        self.assertEqual(replaced_2.active_to, None)

    def test_should_nullify_reference_in_replaces_when_deleting_replaced_instance(self):
        # Setup
        replacement = self.v2
        replaced_1 = self.v
        replaced_2 = self.v3
        replacement.active_from = datetime(2015, 1, 1)
        replacement.replace_siblings([replaced_1.id, replaced_2.id], switchover_date=replacement.active_from,
                                     commit=True)

        replaced_2.reload().delete()

        self.assertEqual([v.id for v in replacement.reload().replaces], [replaced_1.id])
        replaced_1.reload()
        self.assertEqual(replaced_1.replaced_by.id, replacement.id)
        self.assertEqual(replaced_1.active_to, replacement.active_from)
