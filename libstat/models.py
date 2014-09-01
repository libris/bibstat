# -*- coding: UTF-8 -*-
from mongoengine import *
from mongoengine import signals
from mongoengine.queryset import Q
from mongoengine.django.auth import User
from mongoengine.errors import DoesNotExist

from pip._vendor.pkg_resources import require
from mongoengine.queryset.queryset import QuerySet
from datetime import datetime
from django.conf import settings

from libstat.utils import ISO8601_utc_format

import logging
logger = logging.getLogger(__name__)

PUBLIC_LIBRARY = ("public", "Folkbibliotek")
RESEARCH_LIBRARY = ("research", "Forskningsbibliotek")
HOSPITAL_LIBRARY = ("hospital", "Sjukhusbibliotek")
SCHOOL_LIBRARY = ("school", "Skolbibliotek")
 
SURVEY_TARGET_GROUPS = (PUBLIC_LIBRARY, RESEARCH_LIBRARY, HOSPITAL_LIBRARY, SCHOOL_LIBRARY)
targetGroups = dict(SURVEY_TARGET_GROUPS)

TYPE_STRING = (u"string", u"Text")
TYPE_BOOLEAN = (u"boolean", u"Boolesk")
TYPE_INTEGER = (u"integer", u"Integer")
TYPE_LONG = (u"long", u"Long")
TYPE_DECIMAL = (u"decimal", u"Decimal")
TYPE_PERCENT = (u"percent", u"Procent")
#TODO: TYPE_DECIMAL1 = (u"decimal1", u"1 decimals noggrannhet"), Type_DECIMAL2 = (u"decimal2", u"2 decimalers noggrannhet") isf TYPE_DECIMAL
#TODO: TYPE_TEXT = (u"text", u"Text") för kommentarer (textarea), TYPE_STRING=(u"string", u"Textsträng") för icke-numeriska värden "numerical" (input)

VARIABLE_TYPES = (TYPE_STRING, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_LONG, TYPE_DECIMAL, TYPE_PERCENT)
variable_types = dict(VARIABLE_TYPES)
rdf_variable_types = {TYPE_STRING[0]:u"xsd:string" , TYPE_BOOLEAN[0]: u"xsd:boolean", TYPE_INTEGER[0]: u"xsd:integer", 
                      TYPE_LONG[0]: u"xsd:long", TYPE_DECIMAL[0]: u"xsd:decimal", TYPE_PERCENT[0]:u"xsd:decimal" }

"""
    Useful definitions when importing data from spreadsheets
"""
DATA_IMPORT_nonMeasurementCategories = [u"Bakgrundsvariabel", u"Tid", u"Befolkning", u"Bakgrundsvariabler"]


class VariableQuerySet(QuerySet):
    """
        Custom query set for Variable.
        Contains nifty prepared filters for fetching Variables.
    """
    is_draft_not_set_query = Q(is_draft=None)
    is_not_draft_query = Q(is_draft=False)
    public_query = Q(is_public=True)
  
    def public_terms(self):
        return self.filter(self.public_query & (self.is_draft_not_set_query | self.is_not_draft_query))
    
    def public_term_by_key(self, key):
        if not key:
            raise DoesNotExist("No key value given")
        key_query = Q(key=key)
        return self.get(key_query & self.public_query & (self.is_draft_not_set_query | self.is_not_draft_query))
    
    def replaceable_siblings(self):
        is_not_replaced_query = Q(replaced_by=None)
        return self.filter(is_not_replaced_query & (self.is_draft_not_set_query | self.is_not_draft_query))
    

class VariableBase(Document):
    """
        Abstract base class for Variable and backup/logging model VariableVersion
    """
    description = StringField(required=True)
    
    # Comment is a private field and should never be returned as open data
    comment = StringField(max_length=200)
    
    is_public = BooleanField(required=True, default=True)
    type = StringField(max_length=100, required=True, choices=VARIABLE_TYPES)
    
    target_groups = ListField(StringField(max_length=20, choices=SURVEY_TARGET_GROUPS), required=True)
    
    category = StringField(max_length=100)
    sub_category = StringField(max_length=100)
    
    # TODO: Inför frågor/delfrågor i termdokument och kör om importen
    question = StringField()
    question_part = StringField()
    summary_of = ListField()
    
    date_modified = DateTimeField()
    modified_by = ReferenceField(User)
    
    is_draft = BooleanField()
    
    replaces = ListField(ReferenceField("Variable"))
    replaced_by = ReferenceField("Variable")
    # TODO: replaced_at = DateTimeField()
    
    meta = {
        'abstract': True,
    }
    
    @property
    def is_active(self):
        # TODO: Variable will have a "deactivated_at" date/flag that this method will need to handle.
        # return not self.is_draft and not self.is_deactivated  (---> or not self.deactivated_at > datetime.utcnow() )
        return False if self.is_draft else True
    
    
    
class Variable(VariableBase):
    """
        Representation of a statistical term with corresponding survey question
    """
    key = StringField(max_length=100, required=True, unique=True)
    
    meta = {
        'collection': 'libstat_variables',
        'queryset_class': VariableQuerySet
    }
    
    @classmethod
    def store_version_and_update_date_modified(cls, sender, document, **kwargs):
        if document.id and not document.is_draft: 
            changed_fields = document.__dict__["_changed_fields"] if "_changed_fields" in document.__dict__ else []
            logger.info(u"PRE SAVE: Fields {} have changed, creating variable version from current version".format(changed_fields))
            query_set = Variable.objects.filter(pk=document.id)
            assert len(query_set) > 0 # Need to do something with query_set since it is lazy loaded. Otherwise nothing will be cloned.
            versions = query_set.clone_into(VariableVersion.objects)
            for v in versions:
                v.id = None
                v.variable_id = document.id
                v.save()
        
        document.date_modified = datetime.utcnow()
        # field modified_by is set in form
    
    @property
    def is_summary_auto_field(self):
        return len(self.summary_of) > 0 and not self.question and not self.question_part
    
    """
        Return a label for this Variable.
        If the Variable has both question and question_part, an array will be returned. Otherwise a unicode string.
    """
    @property
    def label(self):
        if self.question and self.question_part:
            return [self.question, self.question_part] 
        elif self.question:
            return self.question 
        else:
            return self.description
        
        
    def replace_siblings(self, to_be_replaced=[], commit=False):
        """
            Set this Variable instance as the replacement for a list of sibling Variables 
            and return the list of modified siblings.
            All instances including self will be saved if commit=True
        """
        modified_siblings = []
        siblings_to_replace = []
        if to_be_replaced:
            # Ensure Variables to be replaced exist and are in the correct state
            for object_id in to_be_replaced:
                try:
                    variable = Variable.objects.get(pk=object_id)
                    if variable.replaced_by != None and variable.replaced_by.id != self.id:
                        raise AttributeError(u"Variable {} is already replaced by {}".format(object_id, variable.replaced_by.id))
                    siblings_to_replace.append(variable)
                except Exception as e:
                    logger.error(u"Error while fetching Variable with id {} to be replaced by Variable {}: {}".format(object_id, self.id, e))
                    raise e
                
        siblings_to_release = list(set(self.replaces) - set(siblings_to_replace))
        siblings_requiring_update = list(set(siblings_to_replace) - set(self.replaces))

        # Release siblings that should no longer be replaced by this instance
        for to_release in siblings_to_release:
            if not self.is_draft:
                to_release.replaced_by = None;
                if commit:
                    to_release.save()
                modified_siblings.append(to_release)
            self.replaces.remove(to_release)
       
        # Replace sibling variables
        for to_replace in siblings_requiring_update:
            if not self.is_draft:
                to_replace.replaced_by = self;
                if commit:
                    to_replace.save()
                modified_siblings.append(to_replace)
            self.replaces.append(to_replace)
            
        if commit:
            self.save()
        return modified_siblings
        
        
    
    def target_groups__descriptions(self):
        display_names = []
        for tg in self.target_groups:
            display_names.append(targetGroups[tg])
        return display_names
  
    def to_dict(self, id_prefix=""):
        return {
            u"@id": u"{}{}".format(id_prefix, self.key),
            u"@type": [u"rdf:Property", u"qb:MeasureProperty"],
            u"comment": self.description,
            u"range": self.type_to_rdf_type(self.type)
        };
    
    def type_to_rdf_type(self, type):
        return rdf_variable_types[type]
    
    
    def __unicode__(self):
        return self.key
 
 
class VariableVersion(VariableBase):
    """
        Backup/logging of changes in a Variable.
        
        Prior to any changes in a Variable, a new copy should be stored as a VariableVersion.
    """
    key = StringField(max_length=100, required=True)
    variable_id = ObjectIdField(required=True)
 
    meta = {
        'collection': 'libstat_variable_versions',
        #'ordering': ['-date_modified']
    }
     
 
class Survey(Document):
    target_group = StringField(max_length=20, required=True, choices=SURVEY_TARGET_GROUPS)
    sample_year = IntField(required=True)
    questions = ListField(ReferenceField(Variable), required=True)
     
    meta = {
        'collection': 'libstat_surveys'
    }
     
    def __unicode__(self):
        return u"{} {}".format(self.target_group, self.sample_year)


class SurveyResponseQuerySet(QuerySet):
    """
        Custom query set for SurveyResponse.
        Contains some nifty prepared queries for fetching SurveyResponses.
    """
  
    def by_year_or_group(self, sample_year=None, target_group=None):
        target_group_query = Q(target_group=target_group) if target_group else Q()
        sample_year_query = Q(sample_year=sample_year) if sample_year else Q()
        return self.filter(target_group_query & sample_year_query)
    
    def unpublished_by_year_or_group(self, sample_year=None, target_group=None):
        match_target_group = Q(target_group=target_group) if target_group else Q()
        match_sample_year = Q(sample_year=sample_year) if sample_year else Q()
        never_published = Q(published_at=None)
        changed_after_published = Q(_is_published=False)
        return self.filter(match_target_group & match_sample_year & (changed_after_published | never_published))
  
  
class SurveyObservation(EmbeddedDocument):
    variable = ReferenceField(Variable, required=True)
    
    # Need to allow None/null values to indicate invalid or missing responses in old data
    value = DynamicField() 

    # Storing variable key on observation to avoid having to fetch variables all the time.
    _source_key = StringField(max_length=100)
    
    # Public API Optimization and traceability (was this field public at the time of the survey?)
    _is_public = BooleanField(required=True, default=True)

    def __unicode__(self):
        return u"{0}: {1}".format(self.variable, self.value)
    
    @property
    def instance_id(self):
        return self._instance.id

class Library(EmbeddedDocument):
    bibdb_name = StringField()
    bibdb_id = StringField(max_length=100)
    bibdb_sigel = StringField(max_length=10)
    
    def __unicode__(self):
        return u"libdb [{}, {}, {}]".format(self.bibdb_id, self.bibdb_sigel, self.bibdb_name)

class SurveyResponseMetadata(EmbeddedDocument):
    # TODO: Migrera data från observations till denna modell!
    
    # Public
    municipality_name = StringField(max_length=100)
    municipality_code = StringField(max_length=6)
    
    #Private
    respondent_name = StringField(max_length=100)
    respondent_email = StringField(max_length=100)
    respondent_phone = StringField(max_length=20)
    
    # Private
    survey_time_hours = IntField()
    survey_time_minutes = IntField()
    
    # Private
    population_nation = LongField()
    population_0to14y = LongField()
    
    
class SurveyResponseBase(Document):
    """
        Abstract base class for SurveyResponse and backup/logging model SurveyResponseVersion.
    """
    target_group = StringField(required=True, choices=SURVEY_TARGET_GROUPS)
    
    library = EmbeddedDocumentField(Library)
    metadata = EmbeddedDocumentField(SurveyResponseMetadata)

    published_at = DateTimeField()
    published_by = ReferenceField(User)
    # True if this version is published, False otherwise. Flag needed to optimize search for unpublished SurveyResponses.
    _is_published = BooleanField() 
    
    date_created = DateTimeField(required=True, default=datetime.utcnow)
    created_by = ReferenceField(User)
    
    date_modified = DateTimeField(required=True, default=datetime.utcnow)
    modified_by = ReferenceField(User)
    
    observations = ListField(EmbeddedDocumentField(SurveyObservation))
    
    meta = {
        'abstract': True,
    }
    
    def observation_by_key(self, key):
        hits = [obs for obs in self.observations if obs._source_key == key]
        return hits[0] if len(hits) > 0 else None


class SurveyResponseDraft(SurveyResponseBase):
    """
        TODO: A draft for a survey response, where the library has not yet completed the survey.
        When the survey is completed, the draft should be copied to a SurveyResponse object. 
    """  
     # Both unique fields need to be in subclasses to enable proper indexing.
    library_name = StringField(max_length=100, required=True, unique_with='sample_year') 
    sample_year = IntField(required=True)
    
    meta = {
        'collection': 'libstat_survey_response_drafts'
    }
    
        
class SurveyResponse(SurveyResponseBase):
    """
        A single survey response for a library, sample year (and target group).
    """
    # Both unique fields need to be in subclasses to enable proper indexing.
    library_name = StringField(max_length=100, required=True, unique_with='sample_year')
    sample_year = IntField(required=True) 
    
    meta = {
        'collection': 'libstat_survey_responses',
        'queryset_class': SurveyResponseQuerySet,
    }
    
    @classmethod
    def store_version_and_update_date_modified(cls, sender, document, **kwargs):
        if document.id: 
            if hasattr(document, "_action_publish"):
                document._is_published = True
            else:
                changed_fields = document.__dict__["_changed_fields"] if "_changed_fields" in document.__dict__ else []
                logger.info(u"PRE SAVE: Fields {} have changed, creating survey response version from current version".format(changed_fields))
                query_set = SurveyResponse.objects.filter(pk=document.id)
                assert len(query_set) > 0 # Need to do something with query_set since it is lazy loaded. Otherwise nothing will be cloned.
                versions = query_set.clone_into(SurveyResponseVersion.objects)
                for v in versions:
                    v.id = None
                    v.survey_response_id = document.id
                    v.save()
                document.date_modified = datetime.utcnow()
                document._is_published = False
                # field modified_by is set in form
        else:
            #logger.debug("PRE SAVE: Creation of new object, setting modified date to value of creation date")
            document.date_modified = document.date_created
            document.modified_by = document.created_by
            if not hasattr(document, "_is_published"):
                document._is_published = False
    
    @property
    def latest_version_published(self):
        return self._is_published if self._is_published else (self.published_at != None and self.published_at >= self.date_modified)
    
    @property
    def is_published(self):
        return self._is_published if self._is_published else self.published_at != None
    
    
    def target_group__desc(self):
        return targetGroups[self.target_group]
    
    def publish(self, user=None):
        # TODO: Publishing date as a parameter to enable setting correct date for old data?
        logger.debug(u"Publishing SurveyResponse {}".format(self.id))
        publishing_date = datetime.utcnow()
        
        for obs in self.observations:
            # Only publish public observations that have a value
            if obs._is_public and obs.value != None:
                # TODO: Warn if already is_published?
                data_item = None
                existing = OpenData.objects.filter(library_name=self.library_name, sample_year=self.sample_year, variable=obs.variable)
                if(len(existing) == 0):
                    data_item = OpenData(library_name=self.library_name, sample_year=self.sample_year, variable=obs.variable, 
                                         target_group=self.target_group, date_created=publishing_date)
                    if self.library and self.library.bibdb_id:
                        data_item.library_id = self.library.bibdb_id
                else:
                    data_item = existing.get(0)
                
                data_item.value= obs.value
                data_item.date_modified = publishing_date
                data_item.save()
            
        self.published_at = publishing_date
        self.published_by = user
        
        # Custom attribute to handle pre-save actions
        self._action_publish = True 
        
        self.save()
      
    def __unicode__(self):
        return u"{} {} {}".format(self.target_group, self.library_name, self.sample_year)


class SurveyResponseVersion(SurveyResponseBase):
    """
        Backup/logging of changes in a SurveyResponse.
        
        Prior to any changes in a SurveyResponse, a new copy should be stored as a SurveyResponseVersion.
    """
    # Not unique to enable storage of multiple versions. Both fields need to be in subclasses to enable proper indexing.
    library_name = StringField(max_length=100, required=True)
    sample_year = IntField(required=True)
    
    survey_response_id = ObjectIdField(required=True)
 
    meta = {
        'collection': 'libstat_survey_response_versions',
        'ordering': ['-date_modified']
    }



class OpenData(Document):
    """
        Open, published data based on survey observations.
        
        OpenData objects are created when publishing a SurveyResponse.
    """
    
    library_name = StringField(max_length=100, required=True, unique_with=['sample_year', 'variable'])
    library_id = StringField(max_length=100) #TODO
    sample_year = IntField(required=True)
    target_group = StringField(required=True, choices=SURVEY_TARGET_GROUPS)
    variable = ReferenceField(Variable, required=True)
    # Need to allow None/null values to indicate invalid or missing responses in old data
    value = DynamicField() 
    
    date_created = DateTimeField(required=True, default=datetime.utcnow)
    date_modified = DateTimeField(required=True, default=datetime.utcnow)
  
    meta = {
        'collection': 'libstat_open_data',
        'ordering': ['-date_modified']
    }
    
    def date_created_str(self):
        return self.date_created.strftime(ISO8601_utc_format)
    
    def date_modified_str(self):
        return self.date_modified.strftime(ISO8601_utc_format)
    
    def to_dict(self):
        _dict = {
                u"@id": str(self.id),
                u"@type": u"Observation",
                u"library": {u"@id": u"{}/library/{}".format(settings.BIBDB_BASE_URL, self.library_name)},
                u"sampleYear": self.sample_year,
                u"targetGroup": targetGroups[self.target_group],
                self.variable.key: self.value,
                u"published": self.date_created_str(),
                u"modified": self.date_modified_str()
        };
        if self.library_id:
            _dict[u"library"] = {u"@id": u"{}/library/{}".format(settings.BIBDB_BASE_URL, self.library_id)}
        else:
            _dict[u"library"] = {u"name": self.library_name}
        return _dict

    def __unicode__(self):
      return u"{} {} {} {} {}".format(self.library_name, self.sample_year, self.target_group, self.variable.key, self.value)
 
"""
    Post/pre save actions and other signals
"""
signals.pre_save.connect(SurveyResponse.store_version_and_update_date_modified, sender=SurveyResponse)
signals.pre_save.connect(Variable.store_version_and_update_date_modified, sender=Variable)