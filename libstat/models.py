# -*- coding: UTF-8 -*-
from mongoengine import *
from pip._vendor.pkg_resources import require
from mongoengine.queryset.queryset import QuerySet
from datetime import datetime
from django.conf import settings

from libstat.utils import ISO8601_utc_format

PUBLIC_LIBRARY = ("public", "Folkbibliotek")
RESEARCH_LIBRARY = ("research", "Forskningsbibliotek")
HOSPITAL_LIBRARY = ("hospital", "Sjukhusbibliotek")
SCHOOL_LIBRARY = ("school", "Skolbibliotek")
 
SURVEY_TARGET_GROUPS = (PUBLIC_LIBRARY, RESEARCH_LIBRARY, HOSPITAL_LIBRARY, SCHOOL_LIBRARY)
targetGroups = dict(SURVEY_TARGET_GROUPS)

TYPE_STRING = (u"string", u"xsd:string")
TYPE_BOOLEAN = (u"boolean", u"xsd:boolean")
TYPE_INTEGER = (u"integer", u"xsd:integer")
TYPE_LONG = (u"long", u"xsd:long")
TYPE_DECIMAL = (u"decimal", u"xsd:decimal")
TYPE_PERCENT = (u"percent", u"xsd:integer")

VARIABLE_TYPES = (TYPE_STRING, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_LONG, TYPE_DECIMAL, TYPE_PERCENT)
variable_types = dict(VARIABLE_TYPES)

"""
    Useful definitions when importing data from spreadsheets
"""
DATA_IMPORT_nonMeasurementCategories = [u"Bakgrundsvariabel", u"Tid", u"Befolkning", u"Bakgrundsvariabler"]

class Variable(Document):
    key = StringField(max_length=100, required=True, unique=True)
    description = StringField(required=True)
    comment = StringField(max_length=200)
    is_public = BooleanField(required=True, default=True)
    type = StringField(max_length=100, required=True, choices=VARIABLE_TYPES)
    
    target_groups = ListField(StringField(max_length=20, choices=SURVEY_TARGET_GROUPS), required=True)
    
    category = StringField(max_length=100)
    sub_category = StringField(max_length=100)

    meta = {
        'collection': 'libstat_variables'
    }
    
    def target_groups__descriptions(self):
        display_names = []
        for tg in self.target_groups:
            display_names.append(targetGroups[tg])
        return display_names
  
    def to_dict(self, id_prefix="#"):
        return {
            u"@id": u"{}{}".format(id_prefix, self.key),
            u"@type": u"qb:MeasureProperty",
            u"comment": self.description,
            u"range": self.type_to_rdf_type(self.type)
        };
    
    def type_to_rdf_type(self, type):
        return variable_types[type]
    
    
    def __unicode__(self):
        return self.key

"""
    Question
    {
        "id": "093ur093u0983029823098",
        "parent": null, 
        "question": "Hur stort bokbestånd hade folkbiblioteket totalt den 31 december 2012?",
        "variable": null
    },
    {
        "id": "f79d87f9sd6fs7f6s7d6f9s7df",
        "parent": "093ur093u0983029823098", 
        "question": "Hur stort bokbestånd hade folkbiblioteket totalt den 31 december 2012?",
        "variable": "sd6f6s8fa9df9ad7f9a7df9"
    },
    -------- OR PERHAPS:
    {
        "id": "093ur093u0983029823098",
        "question": "Hur stort bokbestånd hade folkbiblioteket totalt den 31 december 2012?",
        "variable": null, 
        "question_parts": [
            {
                "part": "Skönlitteratur för vuxna",
                "variable": "sd6f6s8fa9df9ad7f9a7df9"
            },
            {
                "part": "Skönlitteratur för barn",
                "variable": "2309482039r8203982"
            }
        ]
    }
"""
class Question(Document):
    parent = ReferenceField('Question')
    question = StringField(required=True)
     
    # Not required if this is a parent question
    variable = ReferenceField(Variable)
     
    meta = {
        'collection': 'libstat_questions'
    }
 
class Survey(Document):
    target_group = StringField(max_length=20, required=True, choices=SURVEY_TARGET_GROUPS)
    sample_year = IntField(required=True)
    questions = ListField(ReferenceField(Question), required=True)
     
    meta = {
        'collection': 'libstat_surveys'
    }
     
    def __unicode__(self):
        return u"{} {}".format(self.target_group, self.sample_year)


class SurveyResponseQuerySet(QuerySet):
  
    def by_year_or_group(self, sample_year=None, target_group=None  ):
        filters = {}
        if target_group:
            filters["target_group"] = target_group
        if sample_year:
            filters["sample_year"] = int(sample_year)
        return self.filter(__raw__=filters)
  
  
class SurveyObservation(EmbeddedDocument):
    variable = ReferenceField(Variable, required=True)
    
    # Need to allow None/null values to indicate invalid or missing responses in old data
    value = DynamicField() 

    # Keeping the original key reference from spreadsheet for traceability
    _source_key = StringField(max_length=100)
    
    # Public API Optimization and traceability (was this field public at the time of the survey?)
    _is_public = BooleanField(required=True, default=True)

    def __unicode__(self):
        return u"{0}: {1}".format(self.variable, self.value)

class Library(EmbeddedDocument):
    bibdb_name = StringField()
    bibdb_id = StringField(max_length=100)
    bibdb_sigel = StringField(max_length=10)
    
    def __unicode__(self):
        return u"libdb [{}, {}, {}]".format(self.bibdb_id, self.bibdb_sigel, self.bibdb_name)

class SurveyResponseMetadata(EmbeddedDocument):
    # Public
    municipality_name = StringField(max_length=100)
    municipality_code = StringField(max_length=6)
    
    #Private
    respondent_name = StringField(max_length=100)
    respondent_email = StringField(max_length=100)
    respondent_phone = StringField(max_length=100)
    
    # Private
    survey_time_hours = IntField()
    survey_time_minutes = IntField()
    
    # Private
    population_nation = LongField()
    population_0to14y = LongField()
    
class SurveyResponse(Document):
    library_name = StringField(max_length=100, required=True, unique_with='sample_year')
    sample_year = IntField(required=True)
    target_group = StringField(required=True, choices=SURVEY_TARGET_GROUPS)
    
    library = EmbeddedDocumentField(Library) #TODO

    published_at = DateTimeField()

    date_created = DateTimeField(required=True, default=datetime.utcnow)
    date_modified = DateTimeField(required=True, default=datetime.utcnow)
    
    observations = ListField(EmbeddedDocumentField(SurveyObservation))
    
    metadata = EmbeddedDocumentField(SurveyResponseMetadata)

    meta = {
        'collection': 'libstat_survey_responses',
        'queryset_class': SurveyResponseQuerySet,
    }
    
    def target_group__desc(self):
        return targetGroups[self.target_group]
    
    def publish(self):
        # TODO: Publishing date as a parameter to enable setting correct date for old data?
        print(u"Publishing SurveyResponse {} {} {}".format(self.id, self.library_name, self.sample_year))
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
        self.date_modified = publishing_date
        self.save()
      
    def __unicode__(self):
        return u"{} {} {}".format(self.target_group, self.library_name, self.sample_year)


class OpenData(Document):
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
                u"targetGroup": self.target_group,
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
  
