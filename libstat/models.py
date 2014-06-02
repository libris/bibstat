# -*- coding: UTF-8 -*-
from mongoengine import *
from pip._vendor.pkg_resources import require
from mongoengine.queryset.queryset import QuerySet
from datetime import datetime

# Create your models here.

PUBLIC_LIBRARY = ("public", "Folkbibliotek")
RESEARCH_LIBRARY = ("research", "Forskningsbibliotek")
HOSPITAL_LIBRARY = ("hospital", "Sjukhusbibliotek")
SCHOOL_LIBRARY = ("school", "Skolbibliotek")
 
SURVEY_TARGET_GROUPS = (PUBLIC_LIBRARY, RESEARCH_LIBRARY, HOSPITAL_LIBRARY, SCHOOL_LIBRARY)
targetGroups = dict(SURVEY_TARGET_GROUPS)

"""
Variables
[
    {
        "id": "fpweijf+9u3+r9u3493+49u",
        "key": "noOfEmployees_Librarian_M",
        "alias": "folk18",
        "description": "Antal anställda bibliotekarier som är män",
        "is_public": True,
        "target_groups": ["PublicLibrary"]
    },
    {
        "id": "sd0f98s0d9f80s9d8f0d9f9s",
        "key": "noOfEmployees_Librarian_F",
        "alias": "folk17",
        "description": "Antal anställda bibliotekarier som är kvinnor",
        "is_public": True,
        "target_groups": ["PublicLibrary"]
    },
    {
        "id": "sd0f9s8df098sd0f9sydf86d5",
        "key": "comment_OtherLendingPlaces",
        "alias": "folk15",
        "description": "Textkommentar övriga utlåningsställen",
        "is_public": False,
        "target_groups": ["PublicLibrary"]
    },
]
"""
class Variable(Document):
    key = StringField(max_length=100, required=True, unique=True)
    alias = StringField(max_length=100, unique=True)
    
    description = StringField(max_length=300, required=True)
    comment = StringField(max_length=200)
    is_public = BooleanField(required=True, default=True)
    type = StringField(max_length=100, required=True)
    
    target_groups = ListField(StringField(max_length=20, choices=SURVEY_TARGET_GROUPS), required=True)

    meta = {
        'collection': 'libstat_variables'
    }
    
    def target_groups__descriptions(self):
      display_names = []
      for tg in self.target_groups:
        display_names.append(targetGroups[tg])
      return display_names

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

"""
SurveyResponse
{
    "id": "07sdf5df08sfg9s8g09sf9",
    "library": "Kls1",
    "refArea": "Karlstad",
    "sample_year": 2013,
    "observations": [
        <SurveyObservation> {
            "variable": "fpweijf+9u3+r9u3493+49u",
            "value": 6,
            "_variable_key": "folk18",
            "_is_public": True
        },
        <SurveyObservation> {
            "variable": "sd0f98s0d9f80s9d8f0d9f9s",
            "value": 23
            "_variable_key": "folk17",
            "_is_public": True
        },
        <SurveyObservation> {
            "variable": "sd0f9s8df098sd0f9sydf86d5",
            "value": "Boksnurror i köpcentret"
            "_variable_key": "folk15",
            "_is_public": False
        }
    ]
}
"""
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

class SurveyResponse(Document):
    library = StringField(max_length=100, required=True, unique_with='sample_year')
    sample_year = IntField(required=True)
    target_group = StringField(required=True, choices=SURVEY_TARGET_GROUPS)
    
    published_at = DateTimeField()

    date_created = DateTimeField(required=True, default=datetime.utcnow)
    date_modified = DateTimeField(required=True, default=datetime.utcnow)
    
    observations = ListField(EmbeddedDocumentField(SurveyObservation))

    meta = {
        'collection': 'libstat_survey_responses',
        'queryset_class': SurveyResponseQuerySet,
    }
    
    def target_group__desc(self):
      return targetGroups[self.target_group]
    
    def publish(self):
      # TODO: Publishing date as a parameter to enable setting correct date for old data
      print(u"Publishing SurveyResponse {} {} {}".format(self.id, self.library, self.sample_year))
      publishing_date = datetime.utcnow()
      
      for obs in self.observations:
        if obs._is_public:
          # TODO: Warn if already is_published?
          data_item = None
          existing = OpenData.objects.filter(library=self.library, sample_year=self.sample_year, variable=obs.variable)
          if(len(existing) == 0):
            data_item = OpenData(library=self.library, sample_year=self.sample_year, variable=obs.variable, target_group=self.target_group, date_created=publishing_date)
          else:
            data_item = existing.get(0)
          
          data_item.value= obs.value
          data_item.date_modified = publishing_date
          data_item.save()
          
      self.published_at = publishing_date
      self.date_modified = publishing_date
      self.save()
      
    def __unicode__(self):
        return u"{} {} {}".format(self.target_group, self.library, self.sample_year)


class OpenData(Document):
    library = StringField(max_length=100, required=True, unique_with=['sample_year', 'variable'])
    sample_year = IntField(required=True)
    target_group = StringField(required=True, choices=SURVEY_TARGET_GROUPS)
    variable = ReferenceField(Variable, required=True)
    # Need to allow None/null values to indicate invalid or missing responses in old data
    value = DynamicField() 
    
    date_created = DateTimeField(required=True, default=datetime.utcnow)
    date_modified = DateTimeField(required=True, default=datetime.utcnow)
  
    meta = {
        'collection': 'libstat_open_data'
    }
    
    def __unicode__(self):
      return u"{} {} {} {} {}".format(self.library, self.sample_year, self.target_group, self.variable.key, self.value)
  
