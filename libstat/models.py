import logging
import string
import random

from django_mongoengine import Document, EmbeddedDocument, fields, QuerySet

# from mongoengine import *
from mongoengine import signals, Q, NULLIFY, PULL
from django.conf import settings

from datetime import datetime
from mongoengine.context_managers import no_dereference
from data.municipalities import MUNICIPALITIES
from data.principals import get_library_types_with_same_principal, principal_for_library_type
from libstat.query_sets.variable import VariableQuerySet

from libstat.utils import ISO8601_utc_format
from libstat.utils import SURVEY_TARGET_GROUPS, targetGroups, VARIABLE_TYPES, rdfVariableTypes


logger = logging.getLogger(__name__)


class VariableBase(Document):
    description = fields.StringField(blank=False)
    # Comment is a private field and should never be returned as open data
    comment = fields.StringField()
    is_public = fields.BooleanField(blank=False, default=True)
    type = fields.StringField(blank=False, choices=VARIABLE_TYPES)
    target_groups = fields.ListField(fields.StringField(choices=SURVEY_TARGET_GROUPS), blank=False)
    category = fields.StringField()
    sub_category = fields.StringField()

    # TODO: Inför frågor/delfrågor i termdokument och kör om importen
    question = fields.StringField()
    question_part = fields.StringField()
    summary_of = fields.ListField()

    date_modified = fields.DateTimeField()
    is_draft = fields.BooleanField()

    # Only date-part of these fields is relevant,
    active_from = fields.DateTimeField()
    active_to = fields.DateTimeField()

    replaces = fields.ListField(fields.ReferenceField("Variable"))
    replaced_by = fields.ReferenceField("Variable")

    modified_by = fields.ReferenceField("Variable", blank=False)

    meta = {
        'abstract': True,
    }

    @property
    def is_active(self):
        if self.is_draft:
            return False
        elif self._is_no_longer_active():
            return False
        elif self._is_not_yet_active():
            return False
        else:
            return True

    @property
    def state(self):
        if self.is_draft:
            return {u"state": u"draft", u"label": u"utkast"}
        elif self.replaced_by:
            return {u"state": u"replaced", u"label": u"ersatt"}
        elif self._is_no_longer_active():
            return {u"state": u"discontinued", u"label": u"avslutad"}
        elif self._is_not_yet_active():
            return {u"state": u"pending", u"label": u"vilande"}
        else:
            # Cannot use 'active' as state/css class, it's already a class in Bootstrap...
            return {u"state": u"current", u"label": u"aktiv"}

    def _is_no_longer_active(self):
        return self.active_to and datetime.utcnow().date() > self.active_to.date()

    def _is_not_yet_active(self):
        return self.active_from and datetime.utcnow().date() < self.active_from.date()


class Variable(VariableBase):
    key = fields.StringField(blank=False, unique=True)

    meta = {
        'collection': 'libstat_variables',
        'ordering': ['key'],
        'queryset_class': VariableQuerySet,
        'indexes': [
            'key'
        ]
    }

    @classmethod
    def store_version_and_update_date_modified(cls, sender, document, **kwargs):
        if document.id and not document.is_draft:
            changed_fields = document.__dict__["_changed_fields"] if "_changed_fields" in document.__dict__ else []
            logger.debug(u"PRE_SAVE: Fields {} have changed, creating variable version from current version".format(
                changed_fields))
            query_set = Variable.objects.filter(pk=document.id)
            assert len(query_set) > 0  # Trigger lazy loading
            versions = query_set.clone_into(VariableVersion.objects)
            for v in versions:
                v.id = None
                v.variable_id = document.id
                v.save()

        document.date_modified = datetime.utcnow()

    @classmethod
    def post_delete_actions(cls, sender, document, **kwargs):
        if document.replaces:
            for replaced in document.replaces:
                if replaced.replaced_by and replaced.replaced_by.id == document.id:
                    replaced.active_to = None
                    replaced.save()
                    logger.debug(
                        u"POST_DELETE: Setting 'active_to' to None on replaced {} when deleting replacement".format(
                            replaced.id))

    @property
    def is_summary_auto_field(self):
        return len(self.summary_of) > 0 and not self.question and not self.question_part

    @property
    def label(self):
        if self.question and self.question_part:
            return [self.question, self.question_part]
        elif self.question:
            return self.question
        else:
            return self.description

    def replace_siblings(self, to_be_replaced=[], switchover_date=None, commit=False):
        """
            Important: If commit=False, make sure to use instance method
            'save_updated_self_and_modified_replaced(modified_siblings)'
            to ensure that siblings are not saved for draft variables and
            that all modifications are actually saved (no dirty transactions).
        """
        current_replacements = set(self.replaces)
        modified_siblings = set()
        siblings_to_replace = set()

        if to_be_replaced:
            # Ensure Variables to be replaced exist and are in the correct state
            for object_id in to_be_replaced:
                try:
                    variable = Variable.objects.get(pk=object_id)
                    if variable.replaced_by is not None and variable.replaced_by.id != self.id:
                        raise AttributeError(
                            u"Variable {} is already replaced by {}".format(object_id, variable.replaced_by.id))
                    siblings_to_replace.add(variable)
                except Exception as e:
                    logger.error(
                        u"Error while fetching Variable with id {} to be replaced by Variable {}: {}".format(object_id,
                                                                                                             self.id,
                                                                                                             e))
                    raise e

        siblings_to_release = current_replacements - siblings_to_replace

        # Release siblings that should no longer be replaced by this instance
        for to_release in siblings_to_release:
            if to_release.replaced_by:
                to_release.replaced_by = None
                to_release.active_to = None
                modified_siblings.add(to_release)

        # Replace sibling variables
        for to_replace in siblings_to_replace:
            """
                Nota bene: This modifies siblings for drafts as well as active variables.
                It is important to use the instance method 'save_updated_self_and_modified_replaced(modified_siblings)'
                to avoid saving siblings for draft variables.
            """
            if (not to_replace.replaced_by or to_replace.replaced_by.id != self.id
                or to_replace.active_to != switchover_date):
                to_replace.replaced_by = self
                to_replace.active_to = switchover_date if switchover_date else None
                modified_siblings.add(to_replace)

        # Update list of replaced on self
        self.replaces = list(siblings_to_replace)

        if commit:
            modified_siblings = self.save_updated_self_and_modified_replaced(modified_siblings)

        return modified_siblings

    def save_updated_self_and_modified_replaced(self, modified_siblings):
        """
            When updating both self and siblings with reference to self, we need to save self first
            and then update the reference in modified siblings before saving then. Otherwise transactions
            for siblings will be flagged as dirty (and never committed).
            If self is a draft, siblings will not be saved.
        """
        updated_siblings = []
        updated_instance = self.save()
        if not updated_instance.is_draft:
            for sibling in modified_siblings:
                if sibling.replaced_by and sibling.replaced_by.id == updated_instance.id:
                    sibling.replaced_by = updated_instance
                updated_siblings.append(sibling.save())
        return updated_siblings

    def target_groups__descriptions(self):
        display_names = []
        for target_group in SURVEY_TARGET_GROUPS:
            display_names.append(target_group[1])
        return display_names

    def to_dict(self, id_prefix=""):
        json_ld_dict = {u"@id": u"{}{}".format(id_prefix, self.key),
                        u"@type": [u"rdf:Property", u"qb:MeasureProperty"],
                        u"comment": self.description,
                        u"range": self.type_to_rdf_type(self.type)}

        if self.replaces:
            json_ld_dict[u"replaces"] = [replaced.key for replaced in self.replaces]

        if self.replaced_by:
            json_ld_dict[u"replacedBy"] = self.replaced_by.key

        if self.active_to or self.active_from:
            range_str = u"name=Giltighetstid;"
            if self.active_from:
                range_str += u" start={};".format(self.active_from.date())
            if self.active_to:
                range_str += u" end={};".format(self.active_to.date())

            json_ld_dict[u"valid"] = range_str

        return json_ld_dict

    def type_to_rdf_type(self, type):
        return rdfVariableTypes[type]

    def as_simple_dict(self):
        return {u'key': self.key, u'id': str(self.id), u'description': self.description}

    def is_deletable(self):
        if self.is_draft:
            return True

        # TODO: Check if Survey is referencing variable when Survey model has been updated.
        referenced_in_survey_response = Survey.objects.filter(observations__variable=str(self.id)).count() > 0
        referenced_in_open_data = OpenData.objects.filter(variable=str(self.id)).count() > 0

        return not referenced_in_survey_response and not referenced_in_open_data

    def __unicode__(self):
        return self.key


class VariableVersion(VariableBase):
    key = fields.StringField(blank=False)
    variable_id = fields.ObjectIdField(blank=False)

    meta = {
        'collection': 'libstat_variable_versions',
    }


class ExternalIdentifier(EmbeddedDocument):
    ID_TYPES = (
        (u"school_code", u"Skolenhetskod")
    )
    identifier = fields.StringField(blank=False)
    type = fields.StringField(blank=False, choices=ID_TYPES)


class Library(EmbeddedDocument):
    name = fields.StringField()
    bibdb_id = fields.StringField()
    sigel = fields.StringField()
    email = fields.StringField()
    city = fields.StringField()
    municipality_code = fields.StringField()
    address = fields.StringField()
    zip_code = fields.StringField()
    library_type = fields.StringField(choices=SURVEY_TARGET_GROUPS)
    external_identifiers = fields.ListField(fields.EmbeddedDocumentField(ExternalIdentifier), blank=True, default=None)

    meta = {
        'collection': 'libstat_libraries'
    }

    # From: http://en.wikipedia.org/wiki/Random_password_generator#Python
    @classmethod
    def _random_sigel(cls):
        alphabet = string.letters[0:52] + string.digits
        return str().join(random.SystemRandom().choice(alphabet) for _ in range(10))

    def __init__(self, *args, **kwargs):
        sigel = kwargs.pop("sigel", None)
        super(Library, self).__init__(*args, **kwargs)
        self.sigel = sigel if sigel else self._random_sigel()


class SurveyObservation(EmbeddedDocument):
    variable = fields.ReferenceField(Variable, blank=False)
    value = fields.DynamicField()
    disabled = fields.BooleanField()#TODO: remove?
    value_unknown = fields.BooleanField()
    # Public API Optimization and traceability (was this field public at the time of the survey?)
    _is_public = fields.BooleanField(blank=False, default=True)

    meta = {
        'indexes': [
            'variable'
        ]
    }

    def __unicode__(self):
        return u"{0}: {1}".format(self.variable, self.value)

    @property
    def instance_id(self):
        return self._instance.id


class SurveyQuerySet(QuerySet):
    def by(self, sample_year=None, target_group=None, status=None, municipality_code=None, free_text=None,
           is_active=None, with_email=False, without_email=False, invalid_email=False, exclude_co_reported_by_other=False, sigel=None):
        target_group_query = Q(library__library_type=target_group) if target_group else Q()
        sample_year_query = Q(sample_year=sample_year) if sample_year else Q()
        status_query = Q(_status=status) if status else Q()
        is_active_query = Q(is_active=is_active) if is_active is not None else Q()
        municipality_code_query = (Q(library__municipality_code=municipality_code)
                                   if municipality_code else Q())

        order_by_field = "library__name"

        email_query = Q()
        if with_email:
            email_query = Q(library__email__exists=True) & Q(library__email__ne="")
        if without_email:
            email_query = Q(library__email__exists=False) | Q(library__email="")
        if invalid_email:
            email_exists = Q(library__email__exists=True) & Q(library__email__ne="")
            email_invalid = Q(library__email__not__contains="@")
            email_query = email_exists & email_invalid

        free_text_query = Q()
        if free_text:
            free_text = free_text.strip().lower()
            municipality_codes = [m[1] for m in MUNICIPALITIES if free_text in m[0].lower()]

            free_text_municipality_code_query = Q(library__municipality_code__icontains=free_text)
            free_text_municipality_name_query = Q(library__municipality_code__in=municipality_codes)
            free_text_email_query = Q(library__email__icontains=free_text)
            free_text_library_name_query = Q(library__name__icontains=free_text)
            free_text_query = (free_text_municipality_code_query | free_text_email_query | free_text_library_name_query
                               | free_text_municipality_name_query)

        sigel_query = Q()
        if sigel:
            sigel_query = Q(library__sigel__iexact=sigel)
            order_by_field = "library__sigel"

        filtered_result = self.filter(target_group_query & sample_year_query & status_query &
                                      municipality_code_query & email_query & free_text_query &
                                      is_active_query & sigel_query).exclude("observations").order_by(order_by_field)

        if exclude_co_reported_by_other:
            co_reported_by_others = filtered_result.filter(selected_libraries__size=0, library__sigel__in=Survey.objects.filter(sample_year=sample_year).distinct("selected_libraries")).exclude("observations")
            filtered_result = set(filtered_result).difference(set(co_reported_by_others))

        return filtered_result


class SurveyBase(Document):
    PRINCIPALS = (
        (u"stat", "Stat"),
        (u"kommun", "Kommun"),
        (u"landsting", "Landsting"),
        (u"foretag", "Företag"),
        (u"stiftelse", "Stiftelse")
    )

    STATUSES = (
        (u"not_viewed", u"Ej öppnad"),
        (u"initiated", u"Påbörjad"),
        (u"submitted", u"Inskickad"),
        (u"controlled", u"Kontrollerad"),
        (u"published", u"Publicerad")
    )
    _status_labels = dict(STATUSES)

    published_at = fields.DateTimeField()
    date_created = fields.DateTimeField(blank=False, default=datetime.utcnow)
    date_modified = fields.DateTimeField(blank=False, default=datetime.utcnow)
    observations = fields.ListField(fields.EmbeddedDocumentField(SurveyObservation))
    _status = fields.StringField(choices=STATUSES, default="not_viewed")
    notes = fields.StringField()
    library = fields.EmbeddedDocumentField(Library)
    selected_libraries = fields.ListField(fields.StringField())
    sample_year = fields.IntField()
    password = fields.StringField()
    principal = fields.StringField(choices=PRINCIPALS)
    is_active = fields.BooleanField(blank=False, default=True)

    _municipality_code = fields.StringField()
    _library_type = fields.StringField()

    meta = {
        'abstract': True,
    }

    @classmethod
    def status_label(cls, status):
        return cls._status_labels.get(status)

    # From: http://en.wikipedia.org/wiki/Random_password_generator#Python
    @classmethod
    def _generate_password(cls):
        alphabet = string.ascii_letters[0:52] + string.digits
        return str().join(random.SystemRandom().choice(alphabet) for _ in range(10))

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if status not in [s[0] for s in Survey.STATUSES]:
            raise KeyError(u"Invalid status '{}'".format(status))
        elif status == "published":
            self.publish()
        elif status != "published":
            if self._status == "published":
                self.unpublish()
            self._status = status

    def get_observation(self, key, variable=None, variable_id=None, backtrack_replaced_variables=False):
        if variable is None:
            variables = Variable.objects.filter(id=variable_id) if variable_id else Variable.objects.filter(key=key)
            if len(variables) == 0:
                return None
            variable = variables[0]

        for observation in self.observations:
            if observation.variable == variable:
                return observation

        if backtrack_replaced_variables and len(variable.replaces) == 1:
            replaced_variable = variable.replaces[0]
            return self.get_observation(key=replaced_variable.key, variable_id=replaced_variable.id,
                                        backtrack_replaced_variables=True)

        return None

    @property
    def is_published(self):
        return self._status == "published"

    @property
    def latest_version_published(self):
        return self.published_at is not None and self.published_at >= self.date_modified

    def target_group__desc(self):
        return targetGroups[self.target_group]

    def __unicode__(self):
        return u"{} {}".format(self.library.name, self.sample_year)

    def __init__(self, *args, **kwargs):
        status = kwargs.pop("status", None)
        target_group = kwargs.pop("target_group", None)
        super(SurveyBase, self).__init__(*args, **kwargs)
        if status:
            self.status = status
        if target_group:
            self.target_group = target_group

    def selectable_libraries(self):
        if not self.library.municipality_code:
            return []

        surveys = Survey.objects.filter(
            sample_year=self.sample_year,
            library__municipality_code=self.library.municipality_code,
            library__library_type__in=get_library_types_with_same_principal(self.library),
            library__sigel__ne=self.library.sigel
        )

        selectable_libs = surveys.values_list('library')

        return selectable_libs

    #TODO: optimize by caching surveys by samle_year and municipality_code?

    def selected_sigels_in_other_surveys(self, sample_year):
        if not self.library.municipality_code:
            return set()

        surveys = Survey.objects.filter(
            sample_year=sample_year,
            library__municipality_code=self.library.municipality_code,
            library__library_type__in=get_library_types_with_same_principal(self.library),
            library__sigel__ne=self.library.sigel
        ).only("selected_libraries")

        selected_sigels = set()
        for survey in surveys:
            for sigel in survey.selected_libraries:
                selected_sigels.add(sigel)

        return selected_sigels

    def has_conflicts(self):
        for selected_sigel in self.selected_sigels_in_other_surveys(self.sample_year):
            if selected_sigel in self.selected_libraries or selected_sigel == self.library.sigel:
                return True

        return False

    #TODO: optimize by caching surveys by samle_year and municipality_code?

    def get_conflicting_surveys(self):
        if not self.library.municipality_code:
            return []

        other_surveys = Survey.objects.filter(
            sample_year=self.sample_year,
            library__municipality_code=self.library.municipality_code,
            library__library_type__in=get_library_types_with_same_principal(self.library),
            library__sigel__ne=self.library.sigel
        )

        return [
            other_survey for other_survey in other_surveys
            if any(sigel in other_survey.selected_libraries for sigel in self.selected_libraries)
            or self.library.sigel in other_survey.selected_libraries
        ]

    def get_conflicting_surveys_return_only_libs_and_selected_libs(self):
        if not self.library.municipality_code:
            return []

        other_surveys = Survey.objects.filter(
            sample_year=self.sample_year,
            library__municipality_code=self.library.municipality_code,
            library__library_type__in=get_library_types_with_same_principal(self.library),
            library__sigel__ne=self.library.sigel
        ).only("library", "selected_libraries")

        return [
            other_survey for other_survey in other_surveys
            if any(sigel in other_survey.selected_libraries for sigel in self.selected_libraries)
            or self.library.sigel in other_survey.selected_libraries
        ]

    #TODO: optimize by saving reported_by, is_reported_by_other and is_reporting_for_others to db?

    def reported_by(self):
        surveys = Survey.objects.filter(sample_year=self.sample_year, selected_libraries__contains=self.library.sigel).only("library", "selected_libraries")

        result = [survey.library.sigel for survey in surveys if self.library.sigel in survey.selected_libraries]
        return result

    def is_reported_by_other(self):
        other_surveys_selected_sigels = Survey.objects.filter(sample_year=self.sample_year, pk__ne=self.pk, selected_libraries__contains=self.library.sigel).count()
        if other_surveys_selected_sigels > 0:
            return True
        else:
            return False

    def is_reporting_for_others(self):
        return any(sigel != self.library.sigel for sigel in self.selected_libraries)


class Survey(SurveyBase):
    meta = {
        'collection': 'libstat_surveys',
        'queryset_class': SurveyQuerySet,
        'indexes': [
            "library.sigel",
            "library.municipality_code",
            "library.library_type",
            "library.name",
            "sample_year",
            "_status",
            "is_active"
        ]
    }

    def previous_years_survey(self):
        previous_year = self.sample_year - 1
        previous_survey = Survey.objects.filter(_status=u"published", sample_year=previous_year,
                                                     library__sigel=self.library.sigel).first()
        if not previous_survey:
            previous_survey = Survey.objects.filter(_status=u"published", sample_year=previous_year,
                                                     library__name__iexact=self.library.name).first()
        return previous_survey

    def previous_years_value(self, variable, previous_years_survey=None):
        # allow passing previous survey to reduce db lookups
        if not previous_years_survey:
            previous_years_survey = self.previous_years_survey()
            if not previous_years_survey:
                return None

        for observation in previous_years_survey.observations:
            if variable == observation.variable:
                return observation.value

        replaces = variable.replaces
        if len(replaces) > 1:
            replaces = [v for v in replaces
                        if self.library.library_type in v.target_groups
                        or previous_years_survey.library.library_type in v.target_groups]
        if len(replaces) != 1:
            return None

        previous_variable = replaces[0]
        for observation in previous_years_survey.observations:
            if previous_variable == observation.variable:
                return observation.value

        return None

    def reports_for_same_libraries(self, other_survey):
        if not self.selected_libraries or not other_survey.selected_libraries:
            return False
        if len(self.selected_libraries) != len(other_survey.selected_libraries):
            return False
        for sigel in self.selected_libraries:
            if sigel not in other_survey.selected_libraries:
                return False

        return True

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        def store_version_of(document):
            survey = Survey.objects.filter(pk=document.id)
            if survey:
                survey_version = survey.clone_into(SurveyVersion.objects)[0]
                survey_version.id = None
                survey_version.survey_response_id = document.id
                survey_version.save()

        def remove_older_versions_of(document, max_versions):
            for version in SurveyVersion.objects[max_versions:].filter(survey_response_id=document.id).only(
                    "date_modified"):
                version.delete()

        if document.id:
            if hasattr(document, "_action_publish"):
                document._status = "published"
            else:
                changed_fields = document.__dict__["_changed_fields"] if "_changed_fields" in document.__dict__ else []

                if changed_fields == ['notes']:
                    return

                store_version_of(document)

                remove_older_versions_of(document, max_versions=5)

                document.date_modified = datetime.utcnow()
        else:
            document.date_modified = document.date_created

    def can_publish(self):
        if not self.library.municipality_code:
            return False

        if not self.library.library_type in principal_for_library_type:
            return False

        if not self.selected_libraries:
            return False

        if self.has_conflicts():
            return False

        return True

    def reasons_for_not_able_to_publish(self):
        reasons = []
        if not self.library.municipality_code:
            reasons.append("Kommunkod saknas")

        if not self.library.library_type in principal_for_library_type:
            reasons.append("Huvudman saknas")

        if not self.selected_libraries:
            reasons.append("Inga bibliotek har valts")

        if self.has_conflicts():
            conflicting_surveys = ", ".join([survey.library.sigel for survey in self.get_conflicting_surveys_return_only_libs_and_selected_libs()])
            reasons.append("Konflikt i rapporteringen (med {})".format(conflicting_surveys))

        return ", ".join(reasons)

    def publish(self):
        def update_existing_open_data(self, publishing_date):
            for observation in self.observations:
                open_datas = OpenData.objects.filter(source_survey=self.pk, variable=observation.variable)
                if open_datas:
                    for open_data in open_datas:
                        if not observation._is_public or self.library.library_type not in observation.variable.target_groups:
                            if open_data.is_active:
                                open_data.date_modified = publishing_date
                                open_data.is_active = False
                        elif observation.value != open_data.value:
                            if observation.value is None or observation.value == "" or observation.value == "-":
                                open_data.delete()
                                continue
                            else:
                                open_data.value = observation.value
                                open_data.date_modified = publishing_date
                                open_data.is_active = True
                        else:
                            open_data.is_active = True
                        open_data.save()

        def create_new_open_data(self, publishing_date):
            existing_open_data_variables = [open_data.variable for open_data in
                                            OpenData.objects.filter(source_survey=self.pk)]

            observations = [observation for observation in self.observations if
                            observation._is_public and
                            self.library.library_type in observation.variable.target_groups and
                            observation.value is not None and
                            observation.value != "" and
                            observation.value != "-" and
                            not observation.variable in existing_open_data_variables]
            if observations:
                open_datas = []
                for observation in observations:
                    open_datas.append(
                        OpenData(source_survey=self,
                                 sample_year=self.sample_year,
                                 library_name=self.library.name,
                                 sigel=self.library.sigel,
                                 value=observation.value,
                                 variable=observation.variable,
                                 target_group=self.library.library_type,
                                 date_created=publishing_date,
                                 date_modified=publishing_date,
                        ))
                OpenData.objects.insert(open_datas, load_bulk=False)

        publishing_date = datetime.utcnow()

        if not self.can_publish():
            return False

        update_existing_open_data(self, publishing_date)

        create_new_open_data(self, publishing_date)

        self._status = "published"
        self.published_at = publishing_date
        self._action_publish = True
        self.save()

        return True

    def unpublish(self):
        for open_data in OpenData.objects.filter(source_survey=self.pk):
            open_data.is_active = False
            open_data.date_modified = datetime.utcnow()
            open_data.save()

    def __init__(self, *args, **kwargs):
        password = kwargs.pop("password", None)
        super(Survey, self).__init__(*args, **kwargs)
        self.password = password if password else self._generate_password()


class SurveyVersion(SurveyBase):
    survey_response_id = fields.ObjectIdField(blank=False)

    meta = {
        'collection': 'libstat_survey_versions',
        'ordering': ['-date_modified']
    }


class Article(Document):
    title = fields.StringField()
    content = fields.StringField()
    date_published = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'libstat_articles',
        'ordering': ['date_published']
    }


class Dispatch(Document):
    description = fields.StringField()
    title = fields.StringField()
    message = fields.StringField()
    library_email = fields.StringField()
    library_city = fields.StringField()
    library_name = fields.StringField()

    meta = {
        'collection': 'libstat_dispatches'
    }


class OpenData(Document):
    is_active = fields.BooleanField(blank=False, default=True) # Usage: False if source_survey has been unpublished, if source_survey.library is no longer in variable.target_group or if observation it's based on is no longer public
    source_survey = fields.ReferenceField(Survey)
    library_name = fields.StringField(blank=False)
    sigel = fields.StringField()
    sample_year = fields.IntField(blank=False)
    target_group = fields.StringField(blank=False, choices=SURVEY_TARGET_GROUPS)
    variable = fields.ReferenceField(Variable, blank=False)
    variable_key = fields.StringField()
    value = fields.DynamicField()
    date_created = fields.DateTimeField(blank=False, default=datetime.utcnow)
    date_modified = fields.DateTimeField(blank=False, default=datetime.utcnow)

    meta = {
        'collection': 'libstat_open_data',
        'ordering': ['-date_modified'],
        'indexes': [
            "is_active",
            "source_survey",
            "variable",
            "variable_key",
            "sample_year",
            "date_modified"
        ]
    }

    def date_created_str(self):
        return self.date_created.strftime(ISO8601_utc_format)

    def date_modified_str(self):
        return self.date_modified.strftime(ISO8601_utc_format)

    def to_dict(self):
        return {
            u"@id": str(self.id),
            u"@type": u"Observation",
            u"library": {
                u"@id": u"{}/library/{}".format(settings.BIBDB_BASE_URL, self.sigel) if self.sigel else "",
                u"name": self.library_name
            },
            u"sampleYear": self.sample_year,
            u"targetGroup": targetGroups[self.target_group],
            self.variable.key: self.value,
            u"published": self.date_created_str(),
            u"modified": self.date_modified_str()
        }

    def __unicode__(self):
        return u"{} {} {} {} {}".format(self.library_name, self.sample_year, self.target_group, self.variable.key,
                                        self.value)

    def __init__(self, *args, **kwargs):
        variable = kwargs.pop("variable", None)
        super(OpenData, self).__init__(*args, **kwargs)
        self.variable = variable
        if self.variable:
            self.variable_key = self.variable.key


class Cell(EmbeddedDocument):
    variable_key = fields.StringField()
    required = fields.BooleanField()
    previous_value = fields.StringField()
    sum_of = fields.ListField(fields.StringField())
    part_of = fields.ListField(fields.StringField())
    has_part = fields.ListField(fields.StringField())
    types = fields.ListField(fields.StringField())
    disabled = fields.BooleanField() #TODO: remove?
    _variable = fields.ReferenceField(Variable)

    @property
    def variable(self):
        self._variable = Variable.objects.no_cache().get(key=self.variable_key)
        return self._variable

    @property
    def explanation(self):
        return self.variable.description

    @property
    def previous_value_thousands_separators(self):
        prev = self.previous_value
        if type(prev) in (int, float):
            return "{:,}".format(prev).replace(",", " ").replace(".", ",")
        return prev


class Row(EmbeddedDocument):
    cells = fields.ListField(fields.EmbeddedDocumentField(Cell))

    @property
    def description(self):
        for cell in self.cells:
            sub_category = cell.variable.sub_category
            return sub_category if sub_category else ""


class Group(EmbeddedDocument):
    rows = fields.ListField(fields.EmbeddedDocumentField(Row))

    @property
    def description(self):
        for row in self.rows:
            for cell in row.cells:
                question = cell.variable.question
                return question if question else ""

    @property
    def headers(self):
        for row in self.rows:
            headers = []
            for cell in row.cells:
                category = cell.variable.category
                headers.append(category if category else "")
            return headers

    @property
    def columns(self):
        for row in self.rows:
            return len(row.cells)


class Section(EmbeddedDocument):
    title = fields.StringField()
    groups = fields.ListField(fields.EmbeddedDocumentField(Group))


class SurveyTemplate(Document):
    intro_text_variable_key = fields.StringField()
    sections = fields.ListField(fields.EmbeddedDocumentField(Section))

    @property
    def cells(self):
        cells = []
        for section in self.sections:
            for group in section.groups:
                for row in group.rows:
                    for cell in row.cells:
                        cells.append(cell)
        return cells

    def get_cell(self, variable_key):
        for cell in self.cells:
            if cell.variable_key == variable_key:
                return cell
        return None


class CachedReport(Document):
    surveys = fields.ListField(fields.ReferenceField(Survey))
    report = fields.DictField()
    year = fields.IntField()
    date_created = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'libstat_reports',
        'ordering': ['-date_created'],
        'indexes': [
            '-date_created',
            'year',
        ],
    }

class SurveyEditingLock(Document):
    survey_id = fields.ObjectIdField(blank=False)
    date_locked = fields.DateTimeField(blank=False, default=datetime.utcnow)

    meta = {
        'collection': 'libstat_survey_locks',
        'indexes': ['survey_id']
    }

    def renew_lock(self):
        self.date_locked = datetime.utcnow()
        self.save()

    @classmethod
    def lock_survey(cls, survey_id):
        surveyEditingLock = SurveyEditingLock(survey_id = survey_id,
                                              date_locked = datetime.utcnow())
        surveyEditingLock.save()

    @classmethod
    def release_lock_on_survey(cls, survey_id):
        locked_survey = SurveyEditingLock.objects.filter(survey_id=survey_id).first()
        if locked_survey:
            locked_survey.delete()
            return True
        return False


signals.pre_save.connect(Survey.pre_save, sender=Survey)
signals.pre_save.connect(Variable.store_version_and_update_date_modified, sender=Variable)
Variable.register_delete_rule(Variable, "replaced_by", NULLIFY)
Variable.register_delete_rule(Variable, "replaces", PULL)
signals.post_delete.connect(Variable.post_delete_actions, sender=Variable)
